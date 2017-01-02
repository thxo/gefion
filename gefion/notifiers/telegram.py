# -*- coding: utf-8 -*-
"""Contains TelegramNotifier."""

import logging
from datetime import datetime

from telegram import Bot, ParseMode
from telegram.error import TelegramError

from gefion.notifiers import Notifier

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TelegramNotifier(Notifier):
    """Notifies Telegram contacts.

    Telegram Messenger (telegram.org) is a free messaging platform.

    Attributes:
            message (gefion.notifiers.message): Message object for delivery.
            destination (str): Destination of the message.
            text (str): Generated text to send out.

    """

    def __init__(self, message, destination, **kwargs):
        """Initialise TelegramNotifier.

        Arguments:
            message (gefion.notifiers.message): Message object for delivery.
            destination (str): Destination of the message.
            token (str):
            up_template (str): Up message templates. Variables `host`, `time.`
            down_template (str): Down message templates. Variables `host`,
                `time` and `message.`
        """
        self.token = kwargs.get('token', '0:invalidtoken')
        self.destination = destination

        if message.result.availability:
            template = kwargs.get('up_template', '*{host}* is *UP* at {time}.')
        else:
            template = kwargs.get(
                'down_template',
                '*{host}* is *DOWN* at {time}. Msg: {message}')
        time_formatted = datetime.utcfromtimestamp(
            message.result.timestamp).strftime('%Y-%m-%dT%H:%M:%SZ')
        self.text = template.format(host=message.hostname,
                                    time=time_formatted,
                                    message=message.result.message)
        logging.debug('Message is "%s".', self.text)

        super().__init__(message, destination)

    def send(self):
        """Initialise Telegram bot and send message with Bot API."""
        logging.debug('Sending message to chat %s.', self.destination)
        try:
            logging.debug('Initialising bot with token %s.', self.token)
            bot = Bot(self.token)
            bot.sendMessage(chat_id=int(self.destination),
                            text=self.text,
                            parse_mode=ParseMode.MARKDOWN)

        except TelegramError as err:
            logging.error('Caught Telegram error: %s', str(err))
            return False

        logging.info('Sent message to chat %s.', self.destination)
        return True
