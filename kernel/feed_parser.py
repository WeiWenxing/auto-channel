import feedparser
from typing import List, NamedTuple
import logging
import aiohttp
import asyncio

class FeedItem(NamedTuple):
    title: str
    description: str
    link: str

async def parse_feed(feed_url: str) -> List[FeedItem]:
    """
    异步解析RSS/Atom feed
    :param feed_url: feed的URL
    :return: 包含FeedItem对象的列表
    """
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
                    
                    items.append(FeedItem(
                        title=title,
                        description=description,
                        link=link
                    ))

                return items

    except Exception as e:
        logging.error(f"Error parsing feed: {e}")
        return []
