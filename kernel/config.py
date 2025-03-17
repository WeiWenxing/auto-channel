from dotenv import load_dotenv
import os

load_dotenv()

telegram_config = {
    'token': os.environ.get('TELEGRAM_BOT_TOKEN', ''),
    'admin_user_ids': os.environ.get('ADMIN_USER_IDS', '-'),
}

discord_config = {
    'token': os.environ.get('DISCORD_TOKEN', ''),
}

user_config = {
    'invite_points': int(os.environ.get('INVITE_POINTS', 5)),
}