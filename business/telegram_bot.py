

from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, \
    filters, InlineQueryHandler, Application, CallbackContext, CallbackQueryHandler
from telegram import Message, MessageEntity, Update, constants, InputMediaPhoto, \
    BotCommand, ChatMember, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from kernel.lang_config import get_message
from kernel.config import telegram_config, db_config
from kernel.db_manager import init_db, get_db
from kernel.feed_parser import parse_feed
from kernel.utils import generate_chinese_tags
from framework.telegraph_utils import publish_rss_item
import re
import asyncio
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

    # 1. 参数数量检查
    if len(args) <= 1:
        await update.message.reply_text(get_message(lang, 'sub_usage'))
        return

    # 2. 频道名称格式检查
    channel_name = args[1]
    if not channel_name.startswith('@'):
        await update.message.reply_text(get_message(lang, 'sub_channel_format'))
        return

    try:
        # 3. 获取频道信息
        bot = context.bot
        logging.info(channel_name)
        chat = await bot.get_chat(channel_name)
        logging.info(chat)

        # 4. 检查机器人是否是频道管理员
        bot_member = await bot.get_chat_member(chat.id, bot.id)
        if bot_member.status != ChatMember.ADMINISTRATOR:
            await update.message.reply_text(get_message(lang, 'sub_admin_required', channel_name))
            return

        # 5. 获取当前订阅
        db = get_db()
        subscriptions = db.get_subscriptions(chat.id)

        # 6. 根据参数数量执行不同操作
        if len(args) == 2:
            # 只提供了频道名称，显示当前订阅
            if subscriptions:
                url_list = [subscription['feed_url']
                            for subscription in subscriptions]
                url_text = "\n".join(url_list)
                await update.message.reply_text(f"The following URLs are subscribed in {channel_name}:\n{url_text}")
            else:
                await update.message.reply_text(f"No subscriptions found in {channel_name}.")
            return

        elif len(args) >= 3:
            # 提供了URL，处理订阅
            feed_url = args[2]

            # 检查是否已经存在相同订阅
            existing_sub = next(
                (sub for sub in subscriptions if sub['feed_url'] == feed_url), None)
            if existing_sub:
                subscription = existing_sub
                await update.message.reply_text(get_message(lang, 'sub_already_exists', channel_name))
            else:
                subscription_id = db.add_subscription(
                    chat.id, channel_name, feed_url)
                subscription = next(
                    (sub for sub in db.get_subscriptions() if sub['id'] == subscription_id), None)
            await update.message.reply_text(get_message(lang, 'sub_processing'))

            # 处理订阅
            try:
                await process_sub(context.bot, subscription)
            except Exception as e:
                logging.error(e)
            # 发送结束消息
            await update.message.reply_text(get_message(lang, 'sub_end', channel_name))
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
            feed_url = args[2]

            # 从数据库中删除订阅
            db = get_db()
            success = db.remove_subscription(chat.id, feed_url)

            if success:
                await update.message.reply_text(get_message(lang, 'unsub_processing'))
            else:
                await update.message.reply_text(get_message(lang, 'unsub_not_found'))
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
    # 初始化数据库连接
    init_db(db_config['host'], db_config['user'],
            db_config['password'], db_config['database'])
    logging.info("Database initialized")
    logging.info("init vars and sd_webui end")


async def start_task(token):
    return await run(token)


def close_all():
    # 关闭数据库连接
    try:
        get_db().close()
    except Exception as e:
        logging.error(f"Error closing database: {e}")
    logging.info("db close")


async def process_sub(bot, subscription):
    logging.info(subscription)
    subscription_id = subscription['id']
    chat_id = subscription['channel_id']
    channel_name = subscription['channel_name']
    feed_url = subscription['feed_url']

    # 检查bot是否是频道管理员
    chat = await bot.get_chat(channel_name)
    logging.info(chat)
    bot_member = await bot.get_chat_member(chat_id, bot.id)
    if bot_member.status == ChatMember.ADMINISTRATOR:
        items = await parse_feed(feed_url)
        last_updated = subscription.get('updated_at')
        if last_updated is None:
            last_updated = 0
        else:
            last_updated = last_updated.timestamp()
        logging.info(f"last_updated: {last_updated}")
        item_latest = last_updated
        for item in reversed(items):
            # 获取item的pubDate时间戳
            item_timestamp = item.pubDate
            logging.info(f"pubDate: {item.pubDate}")

            # 如果item的时间早于或等于上次更新时间，跳过
            if item_timestamp <= last_updated:
                continue

            if item_latest < item_timestamp:
                item_latest = item_timestamp
            logging.info(f"item_latest: {item_latest}")
            # 处理description中的图片
            if item.description:
                # 提取所有图片链接
                image_urls = re.findall(
                    r'<img[^>]+src="([^">]+)"', item.description)

                # 准备消息内容
                first_word = "美人图"  # 默认值
                if item.title:
                    # 使用正则表达式匹配第一个包含汉字、日语或字母数字的单词
                    match = re.search(
                        r'[\u4e00-\u9fa5\u3040-\u309F\u30A0-\u30FFa-zA-Z0-9]+', item.title)
                    if match:
                        first_word = match.group(0)

                # 发布到Telegraph
                try:
                    url = f"https://t.me/{chat.username}"
                    logging.info(f"chat.title: {chat.title}, chat.url: {url}")
                    page_link, _ = publish_rss_item(item, chat.title, url)
                    logging.info(f"page_link: {page_link}")
                    tags = generate_chinese_tags(item.title)
                    text_msg=f"{item.title}\n\n{page_link}\n{tags}"
                    logging.info(f"text_msg: {text_msg}")

                    # 如果有图片，发送第一张图片并附带caption
                    if image_urls:
                        await bot.send_photo(
                            chat_id=chat_id,
                            photo=image_urls[0],
                            caption=text_msg
                        )
                    else:
                        # 没有图片则保持原样发送文本
                        await bot.send_message(
                            chat_id=chat_id,
                            text=text_msg
                        )

                    # 更新数据库中的updated_at时间戳
                    updated_at = datetime.fromtimestamp(item_latest)
                    get_db().update_subscription_timestamp(
                        subscription_id, updated_at)
                    await asyncio.sleep(3)
                except Exception as e:
                    logging.exception("An error occurred:")
                    logging.error(e)


    else:
        logging.info(
            f"Bot is not an administrator in channel {channel_name} (ID: {chat_id})")


async def scheduled_task():
    await asyncio.sleep(4*60)
    while True:
        try:
            # 检查所有订阅
            db = get_db()
            subscriptions = db.get_subscriptions()
            # 遍历所有订阅
            for bot in tel_bots:
                for subscription in subscriptions:
                    # 处理订阅
                    try:
                        await process_sub(bot, subscription)
                    except Exception as e:
                        logging.error(e)

        except Exception as e:
            logging.error(e)
        finally:
            await asyncio.sleep(4*60*60)
