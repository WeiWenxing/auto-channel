from dotenv import load_dotenv, set_key
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

# Telegraph 配置
telegraph_config = {
    'access_token': os.environ.get('TELEGRAPH_ACCESS_TOKEN', '')
}

def update_env_variable(key, value):
    """
    此方法用于更新 .env 文件中的环境变量

    :param key: 要更新的环境变量的键
    :param value: 要设置的新值
    :return: 如果更新成功返回 True，否则返回 False
    """
    env_path = '.env'
    try:
        # 更新 .env 文件中的键值对
        set_key(env_path, key, value)
        # 重新加载 .env 文件以更新环境变量
        load_dotenv(override=True)
        return True
    except Exception as e:
        print(f"更新 .env 文件时出错: {e}")
        return False

