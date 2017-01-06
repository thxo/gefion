# -*- coding: utf-8 -*-
"""Contains PostmarkNotifier."""

import logging
from datetime import datetime

from postmarker.core import PostmarkClient
from postmarker.exceptions import PostmarkerException

from gefion.notifiers import Notifier

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def make_template_model(message, up_text='UP', down_text='DOWN'):
    """Make Postmark template model.

    Arguments:
        message (gefion.notifier.message): Message object for delivery.
        up_text (str): Text to describe up status. Default is "UP".
        down_text (str): Text to describe down status. Default is "DOWN".

    Returns:
        dict: Postmark template model.
    """
    name = message.hostname
    if message.result.availability:
        availability = up_text
    else:
        availability = down_text
    time_string = datetime.utcfromtimestamp(message.result.timestamp).strftime(
        '%Y-%m-%dT%H:%M:%SZ')
    return {'name': name,
            'availability': availability,
            'time_string': time_string}


class PostmarkNotifier(Notifier):
    """Notifies email addresses with Postmark, using Postmark templates.

    Postmark (postmarkapp.com) is a commercial transactional email service
        provider.
    """

    def __init__(self, message, destination, **kwargs):
        """Initialise PostmarkNotifier.

        Arguments:
            message (gefion.notifiers.message): Message object for delivery.
            destination (str): Destination email address.
            server_token (str): Postmark server API token.
            from_address (str): Email's `From` field. Use a sender signature
                validated in Postmark.
            template_id (int): Postmark template ID.
            up_text (str): Text to describe up status. Default is "UP".
            down_text (str): Text to describe down status. Default is "DOWN".
        """
        self.destination = destination
        self.server_token = kwargs.get('server_token',
                                       'replace-this-in-config')
        self.from_address = kwargs.get('from_address', 'test@example.invalid')
        self.template_id = kwargs.get('template_id', 1200342)

        up_text = kwargs.get('up_text', 'UP')
        down_text = kwargs.get('down_text', 'DOWN')
        self.template_model = make_template_model(message, up_text, down_text)
        logging.debug('Got model: %s.', self.template_model)

        super().__init__(message, destination)

    def send(self):
        """Send email with Postmark.

        Returns:
            bool: Successfulness of delivery.
        """
        postmark = PostmarkClient(token=self.server_token)
        try:
            postmark.emails.send_with_template(
                TemplateId=self.template_id,
                TemplateModel=self.template_model,
                From=self.from_address,
                To=self.destination)
        except PostmarkerException:
            return False
        return True
