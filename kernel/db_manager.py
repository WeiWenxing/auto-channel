import mysql.connector
import logging
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any


class DBManager:
    """
    数据库管理类，用于处理频道订阅和消息记录
    """

    def __init__(self, host: str, user: str, password: str, database: str):
        """
        初始化数据库连接
        """
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        self.conn = None
        self.connect()
        self.init_tables()

    def connect(self):
        """
        连接到数据库
        """
        try:
            self.conn = mysql.connector.connect(**self.config)
            logging.info("Database connection established")
        except mysql.connector.Error as err:
            logging.error(f"Database connection error: {err}")
            raise

    def ensure_connection(self):
        """
        确保数据库连接有效
        """
        try:
            if self.conn is None or not self.conn.is_connected():
                self.connect()
        except Exception as e:
            logging.error(f"Error reconnecting to database: {e}")
            raise

    def init_tables(self):
        """
        初始化数据库表
        """
        self.ensure_connection()
        cursor = self.conn.cursor()

        # 创建频道订阅表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS channel_subscriptions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            channel_id BIGINT NOT NULL,
            channel_name VARCHAR(255) NOT NULL,
            feed_url VARCHAR(512) NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            UNIQUE KEY unique_channel_feed (channel_id, feed_url)
        )
        ''')

        self.conn.commit()
        cursor.close()
        logging.info("Database tables initialized")

    def add_subscription(self, channel_id: int, channel_name: str, feed_url: str) -> int:
        """
        添加新的频道订阅

        Args:
            channel_id: Telegram 频道 ID
            channel_name: Telegram 频道名称
            feed_url: 订阅的 URL

        Returns:
            subscription_id: 新添加的订阅 ID
        """
        self.ensure_connection()
        cursor = self.conn.cursor()
        now = datetime.now()

        try:
            # 检查是否已存在相同订阅
            cursor.execute(
                "SELECT id FROM channel_subscriptions WHERE channel_id = %s AND feed_url = %s",
                (channel_id, feed_url)
            )
            existing = cursor.fetchone()

            if existing:
                # 更新已存在的订阅，将is_active设为True
                cursor.execute(
                    "UPDATE channel_subscriptions SET is_active = TRUE WHERE id = %s",
                    (existing[0],)
                )
                self.conn.commit()
                return existing[0]
            else:
                # 添加新订阅
                cursor.execute(
                    "INSERT INTO channel_subscriptions (channel_id, channel_name, feed_url, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
                    (channel_id, channel_name, feed_url, now,
                     datetime.fromtimestamp(0))  # 初始化为最小时间
                )
                self.conn.commit()
                return cursor.lastrowid
        finally:
            cursor.close()

    def remove_subscription(self, channel_id: int, feed_url: str) -> bool:
        """
        取消订阅

        Args:
            channel_id: Telegram 频道 ID
            feed_url: 订阅的 URL

        Returns:
            success: 是否成功取消订阅
        """
        self.ensure_connection()
        cursor = self.conn.cursor()

        try:
            # 将is_active设为False而不是删除记录
            cursor.execute(
                "UPDATE channel_subscriptions SET is_active = FALSE WHERE channel_id = %s AND feed_url = %s",
                (channel_id, feed_url)
            )
            self.conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()

    def update_subscription_timestamp(self, subscription_id: int, pub_date: datetime) -> bool:
        """
        更新订阅的更新时间戳

        Args:
            subscription_id: 订阅 ID
            pub_date: 消息发布时间

        Returns:
            success: 是否成功更新
        """
        self.ensure_connection()
        cursor = self.conn.cursor()

        try:
            cursor.execute(
                "UPDATE channel_subscriptions SET updated_at = %s WHERE id = %s",
                (pub_date, subscription_id)
            )
            self.conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()

    def get_subscriptions(self, channel_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取频道订阅列表

        Args:
            channel_id: 可选，指定频道 ID

        Returns:
            subscriptions: 订阅列表
        """
        self.ensure_connection()
        cursor = self.conn.cursor(dictionary=True)

        try:
            if channel_id:
                cursor.execute(
                    "SELECT * FROM channel_subscriptions WHERE channel_id = %s AND is_active = TRUE",
                    (channel_id,)
                )
            else:
                cursor.execute(
                    "SELECT * FROM channel_subscriptions WHERE is_active = TRUE")

            return cursor.fetchall()
        finally:
            cursor.close()

    def close(self):
        """
        关闭数据库连接
        """
        if self.conn and self.conn.is_connected():
            self.conn.close()
            logging.info("Database connection closed")


# 单例模式，全局数据库连接
_db_instance = None


def init_db(host: str, user: str, password: str, database: str) -> DBManager:
    """
    初始化数据库管理器
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = DBManager(host, user, password, database)
    return _db_instance


def get_db() -> DBManager:
    """
    获取数据库管理器实例
    """
    global _db_instance
    if _db_instance is None:
        raise RuntimeError("Database not initialized. Call init_db first.")
    return _db_instance
