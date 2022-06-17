class SendMessageError(Exception):
    """Класс исключения при ошибке отправки сообщения."""

    def __init__(self, id):
        self.id = id

    def __str__(self):
        return f'Telegram can not send message to: {self.id}.'


class NotIndexError(Exception):
    """Класс исключения при отсутствии ключа в словаре."""

    def __init__(self, keys):
        self.keys = keys

    def __str__(self):
        return f'Can not find keys: {self.keys}.'
