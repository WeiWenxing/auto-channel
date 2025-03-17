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
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            UNIQUE KEY unique_channel_feed (channel_id, feed_url)
        )
        ''')
        
        # 创建已发送消息记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sent_messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            subscription_id INT NOT NULL,
            message_id VARCHAR(255) NOT NULL,
            published_at DATETIME,
            sent_at DATETIME NOT NULL,
            UNIQUE KEY unique_message (subscription_id, message_id),
            FOREIGN KEY (subscription_id) REFERENCES channel_subscriptions(id) ON DELETE CASCADE
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
                # 更新已存在的订阅
                cursor.execute(
                    "UPDATE channel_subscriptions SET updated_at = %s WHERE id = %s",
                    (now, existing[0])
                )
                self.conn.commit()
                return existing[0]
            else:
                # 添加新订阅
                cursor.execute(
                    "INSERT INTO channel_subscriptions (channel_id, channel_name, feed_url, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
                    (channel_id, channel_name, feed_url, now, now)
                )
                self.conn.commit()
                return cursor.lastrowid
        finally:
            cursor.close()

    def remove_subscription(self, channel_id: int, feed_url: str) -> bool:
        """
        删除频道订阅
        
        Args:
            channel_id: Telegram 频道 ID
            feed_url: 订阅的 URL
            
        Returns:
            success: 是否成功删除
        """
        self.ensure_connection()
        cursor = self.conn.cursor()
        
        try:
            cursor.execute(
                "DELETE FROM channel_subscriptions WHERE channel_id = %s AND feed_url = %s",
                (channel_id, feed_url)
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
                    "SELECT * FROM channel_subscriptions WHERE channel_id = %s",
                    (channel_id,)
                )
            else:
                cursor.execute("SELECT * FROM channel_subscriptions")
                
            return cursor.fetchall()
        finally:
            cursor.close()

    def record_sent_message(self, subscription_id: int, message_id: str, published_at: Optional[datetime] = None) -> int:
        """
        记录已发送的消息
        
        Args:
            subscription_id: 订阅 ID
            message_id: 消息唯一标识符
            published_at: 消息发布时间
            
        Returns:
            record_id: 记录 ID
        """
        self.ensure_connection()
        cursor = self.conn.cursor()
        now = datetime.now()
        
        try:
            cursor.execute(
                "INSERT INTO sent_messages (subscription_id, message_id, published_at, sent_at) VALUES (%s, %s, %s, %s)",
                (subscription_id, message_id, published_at, now)
            )
            self.conn.commit()
            return cursor.lastrowid
        except mysql.connector.IntegrityError:
            # 消息已经发送过，忽略
            return 0
        finally:
            cursor.close()

    def is_message_sent(self, subscription_id: int, message_id: str) -> bool:
        """
        检查消息是否已发送
        
        Args:
            subscription_id: 订阅 ID
            message_id: 消息唯一标识符
            
        Returns:
            is_sent: 消息是否已发送
        """
        self.ensure_connection()
        cursor = self.conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id FROM sent_messages WHERE subscription_id = %s AND message_id = %s",
                (subscription_id, message_id)
            )
            return cursor.fetchone() is not None
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