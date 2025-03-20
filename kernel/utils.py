from datetime import datetime
import logging
import re

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

def generate_chinese_tags(title):
    # 使用正则表达式匹配所有的中文部分
    chinese_parts = re.findall(r'[\u4e00-\u9fa5]+', title)
    # 为每个中文部分添加 # 符号
    tags = [f"#{part}" for part in chinese_parts]
    # 将标签用空格连接成字符串
    return " ".join(tags)