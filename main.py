from settings import TG_KEY, AI_MODEL
from telegram import Update
from telegram.ext import (Application, CommandHandler,
                          MessageHandler, filters, ContextTypes)
import message_manager
import gemini
import log


READ_TIMEOUT: int = 60
WRITE_TIMEOUT: int = 60


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    log.info(f'''User "{update.message.from_user.username}"
 in chat "{update.message.chat_id}" sent a message''')
    await message_manager.process_message(update, bot, parse_mode='MarkdownV2')


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await message_manager.send_text_reply(
        update,
        text=f'This is a Gemini bot "{AI_MODEL}"',
        parse_mode='MarkdownV2'
        )


async def request_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.message.text
    response = await gemini.request_async(request)
    await message_manager.send_text_reply(
        update,
        text=response,
        parse_mode='MarkdownV2'
        )


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from history_manager import HistoryManager
    HistoryManager.delete_history_for_chat_id(context._chat_id)
    response = 'The message history with the bot was deleted completely'
    await message_manager.send_text_reply(
        update,
        text=response,
        parse_mode='MarkdownV2'
        )


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.error(f'Update {update.update_id} caused error {context.error}')


def launch_bot():
    app = Application.builder().token(TG_KEY)\
                               .read_timeout(READ_TIMEOUT)\
                               .write_timeout(WRITE_TIMEOUT).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('req', request_command))
    app.add_handler(CommandHandler('reset', reset_command))

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.add_error_handler(error)

    app.run_polling(poll_interval=3)


if __name__ == '__main__':
    print('The bot is working')
    launch_bot()
