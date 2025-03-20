import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image
import io
import requests
import re
from telegraph import Telegraph
from kernel.config import telegraph_config, telegram_config

# 从配置中获取 TELEGRAPH_ACCESS_TOKEN
access_token = telegraph_config.get('access_token')

# 全局初始化 Telegraph 实例
if access_token:
    telegraph = Telegraph(access_token=access_token)
else:
    telegraph = Telegraph()
    print("警告：未在配置中找到 TELEGRAPH_ACCESS_TOKEN 的配置。后续操作可能会失败，请确保正确配置。")


def create_page(title, content, author_name="Default Author", author_url="https://example.com"):
    """
    创建一个新的 Telegraph 页面
    :param title: 页面标题
    :param content: 页面内容，HTML 格式的字符串
    :param author_name: 作者名称，默认为 "Default Author"
    :param author_url: 作者主页 URL，默认为 "https://example.com"
    :return: 页面的链接和页面 ID
    """
    response = telegraph.create_page(
        title=title,
        html_content=content,
        author_name=author_name,
        author_url=author_url
    )
    page_link = 'https://telegra.ph/{}'.format(response['path'])
    page_id = response['path']
    return page_link, page_id


def edit_page(page_id, title, content, author_name="Default Author", author_url="https://example.com"):
    """
    编辑已有的 Telegraph 页面
    :param page_id: 页面的 ID
    :param title: 新的页面标题
    :param content: 新的页面内容，HTML 格式的字符串
    :param author_name: 作者名称，默认为 "Default Author"
    :param author_url: 作者主页 URL，默认为 "https://example.com"
    :return: 页面的链接
    """
    response = telegraph.edit_page(
        path=page_id,
        title=title,
        html_content=content,
        author_name=author_name,
        author_url=author_url
    )
    return 'https://telegra.ph/{}'.format(response['path'])


def publish_rss_item(item, author_name, author_url):
    """
    根据 RSS Feed 中的单个 item 发布一篇 Telegraph 文章
    :param item: RSS Feed 中的单个 item，包含标题、描述、发布日期等
    :return: 页面的链接和页面 ID
    """
    title = item.get('title', '无标题文章')
    description = item.get('description', '')
    pub_date = item.get('pubDate', '')

    # 解析描述中的图片地址
    image_urls = re.findall(r'<img[^>]+src="([^">]+)"', description)
    telegraph_image_urls = []
    for img_url in image_urls:
        telegraph_img_url = img_url
        if telegraph_img_url:
            telegraph_image_urls.append(telegraph_img_url)

    # 构建文章内容，仅包含上传后图片新地址列表
    content = f"<p>发布日期: {pub_date}</p>"
    for img_url in telegraph_image_urls:
        content += f'<img src="{img_url}" />'

    return create_page(title, content, author_name, author_url)

def get_file_path(file_id, token):
    """
    根据 file_id 获取文件的下载路径
    :param file_id: 图片的 file_id
    :return: 文件的下载路径
    """
    url = f"https://api.telegram.org/bot{token}/getFile"
    params = {
        "file_id": file_id
    }
    response = requests.get(url, params=params)
    result = response.json()
    if result.get('ok'):
        return result['result']['file_path']
    return None

if __name__ == "__main__":
    if not access_token:
        print("由于未配置 TELEGRAPH_ACCESS_TOKEN，无法进行页面创建和编辑操作，请先配置。")
    else:
        print(f"使用配置中的 access_token: {access_token}")

        # 示例 RSS item
        rss_item = {
            'title': '测试文章标题',
            'description': '<p>这是一篇测试文章的内容。<img src="https://cosplaytele.com/wp-content/uploads/2024/12/Yaokoututu-cosplay-Yumeko-Jabami-Kakegurui-11_result.webp" /><img src="https://y.gtimg.cn/music/photo_new/T053M000001ME2bp095ikV.jpg" /></p>',
            'pubDate': '2025-03-20'
        }

        # page_link, page_id = publish_rss_item(rss_item, "Default", "https://t.me")
        # print(f"文章已发布到 Telegraph，链接为: {page_link}，页面 ID 为: {page_id}")

        telegram_token = str(telegram_config['token'])
        url = f"https://api.telegram.org/bot{telegram_token}/sendPhoto"
        params = {
            "chat_id": "7266351024",
            "photo": "https://y.gtimg.cn/music/photo_new/T053M000001ME2bp095ikV.jpg",
            "caption": "This is a sample image"
        }
        response = requests.post(url, data=params)
        response_info = response.json()
        print(response_info)
        # 获取第一个图片的 file_id
        first_file_id = response_info['result']['photo'][-1]['file_id']
        print(first_file_id)

        # 获取文件的下载路径
        file_path = get_file_path(first_file_id, telegram_token)
        real_url = f"https://api.telegram.org/file/bot{telegram_token}/{file_path}"

        print(real_url)

