from google import genai
from settings import GEMINI_TOKEN, AI_MODEL
from md2tgmd import escape


from history_manager import HistoryEntry, HistoryManager
client = genai.Client(api_key=GEMINI_TOKEN)

#List of active chats
chats = []


def print_models():
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)


def request(data: list|str):
    
    response = client.models.generate_content(model=AI_MODEL, contents=data)
    return response.text


async def request_async(data: list|str):
    
    response = await client.aio.models.generate_content(model=AI_MODEL, contents=data)
    
    raw_text = response.text
    text = escape(raw_text)
    return text


class Chat:
    def __init__(self, chat_id: str, history_manager: HistoryManager):
        self.chat_id = chat_id
        self.history_manager: HistoryManager = history_manager        

        if self.history_manager.entry_exists(chat_id):
            history = self.history_manager.get_history(chat_id)            
            self.chat  = client.aio.chats.create(model=AI_MODEL, history=history)
        else:            
            self.chat  = client.aio.chats.create(model=AI_MODEL, history=[])

    async def send_message(self, data: list|str):
        response = await self.chat.send_message(data)                
        text = escape(response.text)
        print(f'Gemini response: {text}')
        self.save()
        return text

    def save(self):
        history_entry = HistoryEntry(self.chat_id, self.chat.get_history())
        history_entry.save()

    def reset(self):
        self.chat = client.aio.chats.create(history=[])


def get_chat(chat_id: str) -> Chat | None:

    for chat in chats:
        if chat.chat_id == chat_id:
            return chat
    return None


def add_new_chat(chat_id: str):

    new_chat = Chat(chat_id, HistoryManager())
    chats.append(new_chat)
    return new_chat


if __name__ == '__main__':
    pass
