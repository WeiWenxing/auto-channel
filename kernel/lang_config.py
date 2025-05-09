MESSAGES = {
    'en': {
        'sub_usage': '/sub @channel_name url',
        'sub_channel_format': 'Channel name must start with @. Please use the format: /sub @channel_name url',
        'sub_admin_required': 'I need to be an administrator in {} to perform subscriptions.',
        'sub_processing': 'Processing subscription...',
        'sub_url_required': 'Please provide a URL. Format: /sub {} url',
        'sub_channel_error': 'Could not access {}. Make sure the channel exists and the bot is its administrator.',
        'sub_already_exists': 'This URL is already subscribed in {}.',
        'unsub_usage': '/unsub @channel_name url',
        'unsub_channel_format': 'Channel name must start with @. Please use the format: /unsub @channel_name url',
        'unsub_admin_required': 'I need to be an administrator in {} to perform unsubscription.',
        'unsub_processing': 'Processing unsubscription...',
        'unsub_url_required': 'Please provide a URL. Format: /unsub {} url',
        'unsub_channel_error': 'Could not access {}. Make sure the channel exists and the bot is its administrator.',
        'unsub_not_found': 'No subscription found for this URL in the channel.',
        'sub_end': 'Sent message to {0} end',
        'sub_fail': 'Failed to send message: {0}'
    },
    'zh': {
        'sub_usage': '/sub @频道名称 url',
        'sub_channel_format': '频道名称必须以@开头。请使用格式：/sub @频道名称 url',
        'sub_admin_required': '我需要在{}中具有管理员权限才能执行订阅操作。',
        'sub_processing': '正在处理订阅...',
        'sub_url_required': '请提供URL。格式：/sub {} url',
        'sub_channel_error': '无法访问{}。请确保频道存在且机器人是其管理员',
        'sub_already_exists': '此URL已在{}中订阅。',
        'unsub_usage': '/unsub @频道名称 url',
        'unsub_channel_format': '频道名称必须以@开头。请使用格式：/unsub @频道名称 url',
        'unsub_admin_required': '我需要在{}中具有管理员权限才能执行取消订阅操作。',
        'unsub_processing': '正在处理取消订阅...',
        'unsub_url_required': '请提供URL。格式：/unsub {} url',
        'unsub_channel_error': '无法访问{}。请确保频道存在且机器人是其管理员',
        'unsub_not_found': '在频道中未找到此URL的订阅。',
        'sub_end': '向{0}发送消息结束',
        'sub_fail': '发送消息失败: {0}'
    }
}


def get_message(lang: str, key: str, *args) -> str:
    """
    Get a message in the specified language.
    Falls back to English if the language or key is not found.
    """
    # Default to English if language is not supported
    if lang not in MESSAGES:
        lang = 'en'

    # Get the message template
    message = MESSAGES[lang].get(key, MESSAGES['en'].get(key, ''))

    # Format the message with the provided arguments
    if args:
        try:
            return message.format(*args)
        except:
            return message
    return message
