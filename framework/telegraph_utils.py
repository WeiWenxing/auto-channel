import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegraph import Telegraph
from kernel.config import telegraph_config

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


if __name__ == "__main__":
    if not access_token:
        print("由于未配置 TELEGRAPH_ACCESS_TOKEN，无法进行页面创建和编辑操作，请先配置。")
    else:
        print(f"使用 .env 文件中的 access_token: {access_token}")

        # # 创建页面
        # title = "测试文章标题"
        # content = "<p>这是一篇测试文章的内容。</p>"
        # page_link, page_id = create_page(title, content)
        # print(f"文章已发布到 Telegraph，链接为: {page_link}，页面 ID 为: {page_id}")

        # 编辑页面
        page_id = "测试文章标题-03-20-3"
        new_title = "修改后的测试文章标题"
        new_content = "<p>这是修改后的测试文章内容。</p>"
        edited_page_link = edit_page(page_id, new_title, new_content)
        print(f"文章已编辑，新链接为: {edited_page_link}")