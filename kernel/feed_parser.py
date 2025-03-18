import feedparser
from typing import List, NamedTuple
import logging
import aiohttp
import asyncio
import time
from datetime import datetime

class FeedItem(NamedTuple):
    title: str
    description: str
    link: str
    pubDate: int  # 改为存储UTC时间戳

async def parse_feed(feed_url: str) -> List[FeedItem]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(feed_url) as response:
                if response.status != 200:
                    logging.error(f"Failed to fetch feed: {response.status}")
                    return []

                content = await response.text()
                feed = feedparser.parse(content)

                items = []
                for entry in feed.entries:
                    title = entry.get('title', 'No title')
                    description = entry.get('description', '')
                    link = entry.get('link', '')
                    # 使用published_parsed转换为UTC时间戳
                    pubDate = int(time.mktime(entry.get('published_parsed', time.gmtime(0))))
                    
                    items.append(FeedItem(
                        title=title,
                        description=description,
                        link=link,
                        pubDate=pubDate
                    ))

                return items
    except Exception as e:
        logging.error(f"Error parsing feed: {e}")
        return []
