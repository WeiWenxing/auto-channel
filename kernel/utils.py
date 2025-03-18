from datetime import datetime
import logging

def pubdate_to_timestamp(pubdate_str: str) -> float:
    """
    将pubDate字符串转换为UTC时间戳
    
    Args:
        pubdate_str: pubDate字符串，例如 "Sun, 16 Mar 2025 00:19:09 GMT"
        
    Returns:
        float: UTC时间戳
    """
    try:
        # 定义日期格式
        date_format = "%a, %d %b %Y %H:%M:%S GMT"
        # 将字符串转换为datetime对象
        dt = datetime.strptime(pubdate_str, date_format)
        # 返回UTC时间戳
        return dt.timestamp()
    except Exception as e:
        logging.error(f"Error parsing pubDate: {e}")
        return 0.0
