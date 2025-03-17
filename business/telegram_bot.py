from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, \
    filters, InlineQueryHandler, Application, CallbackContext, CallbackQueryHandler
from telegram import Message, MessageEntity, Update, constants, \
    BotCommand, ChatMember, InlineKeyboardButton, InlineKeyboardMarkup
from kernel.lang_config import get_message
from kernel.config import telegram_config
import re
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


tel_bots = []
commands = [
    BotCommand(command='help', description='Show help message'),
    BotCommand(command='sub', description='Subscribe to a channel'),
    BotCommand(command='unsub', description='Unsubscribe from a channel'),
    # BotCommand(command='token', description='please input your replicate token, you should sign up and get your API token: https://replicate.com/account/api-tokens'),
]


async def post_init(application: Application) -> None:
    """
    Post initialization hook for the bot.
    """
    await application.bot.set_my_commands(commands)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    logging.info(update.message)

    id = str(message.from_user.id)
    logging.info(id)

    await help(update, context)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Shows the help menu.
    """
    lang = str(update.message.from_user.language_code)

    # Use existing usage strings
    help_text = get_message(lang, 'sub_usage')
    help_text += "\n" + get_message(lang, 'unsub_usage')

    await update.message.reply_text(help_text, disable_web_page_preview=True)


async def sub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles subscription command.
    Checks if the channel exists and if the bot is an admin in the channel.
    """
    lang = str(update.message.from_user.language_code)
    message_text = update.message.text.strip()
    args = message_text.split()

    if len(args) <= 1:
        # Only /sub command was provided without arguments
        usage_message = get_message(lang, 'sub_usage')
        await update.message.reply_text(usage_message)
        return

    channel_name = args[1]
    if not channel_name.startswith('@'):
        await update.message.reply_text(get_message(lang, 'sub_channel_format'))
        return

    # Check if the channel exists and if the bot is an admin
    try:
        bot = context.bot
        # Get chat information
        chat = await bot.get_chat(channel_name)
        # Check if bot is a member and admin in the channel
        bot_member = await bot.get_chat_member(chat.id, bot.id)
        logging.info(bot_member)

        if bot_member.status != ChatMember.ADMINISTRATOR:
            await update.message.reply_text(get_message(lang, 'sub_admin_required', channel_name))
            return

        # If we have enough arguments and the bot is an admin, proceed with subscription
        if len(args) >= 3:
            await update.message.reply_text(get_message(lang, 'sub_processing'))
        else:
            await update.message.reply_text(get_message(lang, 'sub_url_required', channel_name))

    except Exception as e:
        logging.error(f"Error checking channel: {e}")
        await update.message.reply_text(get_message(lang, 'sub_channel_error', channel_name))


async def unsub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles unsubscription command.
    Checks if the channel exists and if the bot is an admin in the channel.
    """
    lang = str(update.message.from_user.language_code)
    message_text = update.message.text.strip()
    args = message_text.split()

    if len(args) <= 1:
        # Only /unsub command was provided without arguments
        usage_message = get_message(lang, 'unsub_usage')
        await update.message.reply_text(usage_message)
        return

    channel_name = args[1]
    if not channel_name.startswith('@'):
        await update.message.reply_text(get_message(lang, 'unsub_channel_format'))
        return

    # Check if the channel exists and if the bot is an admin
    try:
        bot = context.bot
        # Get chat information
        chat = await bot.get_chat(channel_name)
        # Check if bot is a member and admin in the channel
        bot_member = await bot.get_chat_member(chat.id, bot.id)

        if bot_member.status != ChatMember.ADMINISTRATOR:
            await update.message.reply_text(get_message(lang, 'unsub_admin_required', channel_name))
            return

        # If we have enough arguments and the bot is an admin, proceed with unsubscription
        if len(args) >= 3:
            await update.message.reply_text(get_message(lang, 'unsub_processing'))
        else:
            await update.message.reply_text(get_message(lang, 'unsub_url_required', channel_name))

    except Exception as e:
        logging.error(f"Error checking channel: {e}")
        await update.message.reply_text(get_message(lang, 'unsub_channel_error', channel_name))


async def run(token):
    """
    Runs the bot indefinitely until the user presses Ctrl+C
    """
    global tel_bots
    application = ApplicationBuilder() \
        .token(token) \
        .concurrent_updates(True) \
        .connect_timeout(30) \
        .read_timeout(30) \
        .write_timeout(30) \
        .post_init(post_init) \
        .build()

    bot_num = len(tel_bots)
    tel_bots.append(application.bot)

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('sub', sub))
    application.add_handler(CommandHandler('unsub', unsub))

    await application.initialize()
    await application.start()
    logging.info("start up successful ……")
    await application.updater.start_polling(drop_pending_updates=True)


async def init_task():
    """|coro|
    以异步方式启动
    """
    logging.info("init vars and sd_webui end")


async def start_task(token):
    return await run(token)


def close_all():
    logging.info("db close")
