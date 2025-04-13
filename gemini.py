from google import genai
from google.genai import types
from settings import GEMINI_TOKEN, AI_MODEL
from md2tgmd import escape
from history_manager import HistoryEntry, HistoryManager
from PIL import Image
from PIL.ImageFile import ImageFile
from io import BytesIO


client = genai.Client(api_key=GEMINI_TOKEN)

# List of active chats
chats = []


def get_generate_content_config():
    if AI_MODEL.__contains__('exp-image-generation'):
        config = types.GenerateContentConfig(
            response_modalities=['Text', 'Image']
        )
    else:
        config = types.GenerateContentConfig(
            response_modalities=['Text']
        )
    return config


def get_response_dict(response: types.GenerateContentResponse):
    text: str = None
    image: ImageFile = None

    for part in response.candidates[0].content.parts:
        if part.text:
            text = escape(part.text)
        elif part.inline_data:
            image = Image.open(BytesIO(part.inline_data.data))

    response_dict = {
        'text': text,
        'image': image
    }

    return response_dict


def print_models():
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)


def request(data: list | str) -> dict:

    response = client.models.generate_content(
        model=AI_MODEL,
        contents=data,
        config=get_generate_content_config()
    )

    return get_response_dict(response)


async def request_async(data: list | str):

    response = await client.aio.models.generate_content(
        model=AI_MODEL,
        contents=data,
        config=get_generate_content_config()
    )

    return get_response_dict(response)


class Chat:
    def __init__(self, chat_id: str, history_manager: HistoryManager):
        self.chat_id = chat_id
        self.history_manager: HistoryManager = history_manager

        history = []
        if self.history_manager.entry_exists(chat_id):
            history = self.history_manager.get_history(chat_id)

        self.chat = client.aio.chats.create(
            model=AI_MODEL,
            history=history,
            config=get_generate_content_config()
        )

    async def send_message(self, data: list | str):
        response = await self.chat.send_message(data)        
        self.save()
        return get_response_dict(response)['text']

    def save(self):
        history_entry = HistoryEntry(self.chat_id, self.chat.get_history())
        history_entry.save()

    def reset(self):
        self.chat = client.aio.chats.create(
            model=AI_MODEL,
            history=[],
            config=get_generate_content_config()
            )


def get_chat(chat_id: str) -> Chat | None:

    for chat in chats:
        if chat.chat_id == chat_id:
            return chat
    return None


def add_new_chat(chat_id: str):

    new_chat = Chat(chat_id, HistoryManager())
    chats.append(new_chat)
    return new_chat


def main():
    request_text = 'Generate a random image and give a short description of it'

    response = request(request_text)
    print(response['text'])
    image: ImageFile = response['image']
    image.save('response_image.png')


if __name__ == '__main__':
    main()
