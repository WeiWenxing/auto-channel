MESSAGES = {
    'en': {
        'help_greeting': 'Hello, {}',
        'sub_usage': 'Please use the format: /sub @channel_name url',
        'sub_channel_format': 'Channel name must start with @. Please use the format: /sub @channel_name url',
        'sub_admin_required': 'I need to be an administrator in {} to perform subscriptions.',
        'sub_processing': 'Processing subscription...',
        'sub_url_required': 'Please provide a URL. Format: /sub {} url',
        'sub_channel_error': 'Could not access {}. Make sure the channel exists and I am a member of it.'
    },
    'zh': {
        'help_greeting': '你好，{}',
        'sub_usage': '请使用以下格式：/sub @频道名称 url',
        'sub_channel_format': '频道名称必须以@开头。请使用格式：/sub @频道名称 url',
        'sub_admin_required': '我需要在{}中具有管理员权限才能执行订阅操作。',
        'sub_processing': '正在处理订阅...',
        'sub_url_required': '请提供URL。格式：/sub {} url',
        'sub_channel_error': '无法访问{}。请确保频道存在且我是其成员。'
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