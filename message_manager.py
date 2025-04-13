import io
import telegram
from telegram import InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply, File, Message
import log
from settings import BOT_USERNAME
from gemini import get_chat, add_new_chat
from PIL import Image
from PIL.ImageFile import ImageFile
from io import BytesIO


async def process_message(update: Update, bot,  parse_mode: str = None,
                     reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup |
                                   ReplyKeyboardRemove | ForceReply | None = None):
    text: str = update.message.text    
    chat_type: str = update.message.chat.type    

    #Check if the message is a reply to another message
    if update.message.reply_to_message is not None:
        reply_username = f'@{update.message.reply_to_message.from_user.username}'
        await _process_reply(update, bot, text, reply_username, parse_mode)
    
    else:

        data: list = await _get_data_list(bot, update.message, False)

        #If the message contains the bot name and it is a group chat the bot will reply
        if BOT_USERNAME in text and chat_type == telegram.Chat.GROUP:
            await _send_response_from_ai(update, data, parse_mode)            

        #If the chat is private the bot will reply
        elif chat_type == telegram.Chat.PRIVATE:
            await _send_response_from_ai(update, data, parse_mode)
            
        return


async def send_text_reply(update: Update, text: str, parse_mode: str = 'MarkdownV2',
                     reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup |
                                   ReplyKeyboardRemove | ForceReply | None = None):    
    try:
        await update.message.reply_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
        log.info(f'User "{update.message.from_user.username}" in chat "{update.message.chat_id}" received a reply')

    except telegram.error as e:
        log.error(f'Telegram error: {e}')


async def send_image_reply(update: Update, data: dict[str | ImageFile], parse_mode: str = 'MarkdownV2',
                     reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup |
                                   ReplyKeyboardRemove | ForceReply | None = None):    
    try:
        image: ImageFile = data['image']
        bio = BytesIO()
        bio.name = "image"
        image.save(bio, 'PNG')
        bio.seek(0)

        await update.message.reply_photo(
            caption=data['text'],
            photo=bio,
            parse_mode=parse_mode,
            reply_markup=reply_markup
            )
        log.info(f'User "{update.message.from_user.username}" in chat "{update.message.chat_id}" received a reply')

    except telegram.error as e:
        log.error(f'Telegram error: {e}')


async def _process_reply(update, bot, text, reply_username, parse_mode: str):
    chat_type = update.message.chat.type

    if (BOT_USERNAME in reply_username) or (BOT_USERNAME in text) or (chat_type == telegram.Chat.PRIVATE) :
        has_reply = True
        if BOT_USERNAME in reply_username:
            has_reply = False

        data: list = await _get_data_list(bot, update.message, has_reply)
        await _send_response_from_ai(update, data, parse_mode)


async def _send_response_from_ai(update: Update, data: list, parse_mode: str):
    chat_id: str = str(update.message.chat_id)
    response: dict[str | ImageFile] = await _get_bot_response(data, chat_id)
    if response['image']:
        await send_image_reply(update, response, parse_mode=parse_mode)
    else:
        await send_text_reply(update, response['text'], parse_mode=parse_mode)


async def _get_data_list(bot, message: Message, has_reply: bool):
    data: list = []
    await _get_message_attachments(bot, message, data)
    if has_reply:
        await _get_message_attachments(bot, message.reply_to_message, data)
    return data


# Right now it works only with a single image
async def _get_message_attachments(bot, message: Message, data: list):
    if message.text is not None:
        new_text: str = _remove_botname_if_exists(message.text)
        data.append(new_text)
    if len(message.photo) > 0:
        file_id = message.photo[-1].file_id
        pil_image = await _get_pillow_image(bot, file_id)
        data.append(pil_image)


async def _get_pillow_image(bot, file_id):
    file: File = await bot.get_file(file_id=file_id)
    out = await file.download_as_bytearray()
    image = Image.open(io.BytesIO(out))
    return image


def _remove_botname_if_exists(text: str):
    if BOT_USERNAME in text:
        return text.replace(BOT_USERNAME, '').strip()
    return text


async def _get_bot_response(data: list | str, chat_id: str):
    chat = get_chat(chat_id)
    if chat is None:
        chat = add_new_chat(chat_id)
    return await chat.send_message(data)
