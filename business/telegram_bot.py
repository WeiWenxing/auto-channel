from kernel.config import telegram_config, user_config
from kernel.user import User, Database
from business.help import help_info

from telegram import Message, MessageEntity, Update, constants, \
    BotCommand, ChatMember, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, \
    filters, InlineQueryHandler, Application, CallbackContext, CallbackQueryHandler

import logging
import sys
sys.path.append("..")
import re


db = Database('tel.db')


def message_text(message: Message) -> str:
    """
    Returns the text of a message, excluding any bot commands.
    """
    msg_text = message.text
    if msg_text is None:
        return ''

    for _, text in sorted(message.parse_entities([MessageEntity.BOT_COMMAND]).items(), key=(lambda item: item[0].offset)):
        msg_text = msg_text.replace(text, '').strip()

    return msg_text if len(msg_text) > 0 else ''


commands = [
    BotCommand(command='help', description='Show help message'),
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

    user = db.get_user(id)
    logging.info(user)

    if user is None:
        strs = update.message.text.split()
        logging.info(strs)
        from_id = strs[1] if len(strs) > 1 else ''
        user = User(id=id, from_id=from_id, points=0)
        logging.info(user)
        db.add_user(user)

        from_user = db.get_user(from_id)
        if from_user:
            from_user.points += user_config['invite_points']
            db.update_user(from_user)

    await help(update, context)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Shows the help menu.
    """
    lang = str(update.message.from_user.language_code)
    logging.info(lang)
    default_help_info = help_info.get('default', "")
    help_text = help_info.get(lang, default_help_info)
    await update.message.reply_text(help_text, disable_web_page_preview=True)


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = db.get_user(str(update.message.from_user.id))
    if user:
        info_txt = f'当前积分: {user.points} \n每邀请一个人可获得5点积分, 获取专属邀请链接: /invite'
        await update.message.reply_text(info_txt)


async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    id = update.message.from_user.id
    bot = context.bot
    bot_info = await bot.get_me()
    logging.info(bot_info)
    bot_name = bot_info.username
    text = f'超级机器人： https://t.me/{bot_name}?start={id}'
    logging.info(text)
    await update.message.reply_text(text)


async def run():
    """
    Runs the bot indefinitely until the user presses Ctrl+C
    """
    application = ApplicationBuilder() \
        .token(telegram_config['token']) \
        .concurrent_updates(True) \
        .post_init(post_init) \
        .build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('info', info))
    application.add_handler(CommandHandler('invite', invite))

    # application.add_handler(CallbackQueryHandler(callback=self.set_model, pattern='GuoFeng|chill|uber|majic'))
    # application.add_handler(CallbackQueryHandler(callback=self.draw_dress, pattern='.*dress|.*suit|.*wear|.*uniform|armor|hot|bikini|see|.*hanfu'))
    # application.add_handler(CallbackQueryHandler(callback=self.draw_bg, pattern='.*beach|grass|space|street|mountain'))

    # application.add_handler(MessageHandler(filters.PHOTO & ~filters.CaptionRegex('dress|bg|mi|hand|lace|up|lower|ext|rep|high|clip|all'), self.trip))
    # application.add_handler(MessageHandler(filters.TEXT & filters.Entity(constants.MessageEntityType.URL), trip))

    # application.add_error_handler(self.error_handler)

    # application.run_polling()
    await application.initialize()
    await application.start()
    logging.info("start up successful ……")
    await application.updater.start_polling(drop_pending_updates=True)


async def start_task():
    """|coro|
    以异步方式启动
    """
    return await run()

