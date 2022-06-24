class SendMessageError(Exception):
    """Класс исключения при ошибке отправки сообщения."""

    def __init__(self, id):
        self.id = id

    def __str__(self):
        return f'Telegram can not send message to: {self.id}.'
