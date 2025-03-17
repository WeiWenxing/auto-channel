from dotenv import load_dotenv
import os

load_dotenv()

telegram_config = {
    'token': os.environ.get('TELEGRAM_BOT_TOKEN', ''),
}

discord_config = {
    'token': os.environ.get('DISCORD_TOKEN', ''),
}

# 数据库配置
db_config = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASS', ''),
    'database': os.environ.get('MYSQL_DATABASE', 'telegram_bot'),
}