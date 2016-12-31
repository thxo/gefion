# -*- coding: utf-8 -*-
"""Base classes."""


class Message(object):
    """Contains the message for delivery.

    Attributes:
        hostname (str): Identifying name of the host in question.
        result (gefion.checks.result): Result of the check.
    """

    def __init__(self, hostname, result):
        """Initialise Check.

        Arguments:
            See class attributes.
        """
        self.hostname = hostname
        self.result = result


class Notifier(object):
    """Notifies users of events.

    This should be inherited by notifying implementations.

    Attributes:
        message (gefion.notifiers.message): Message object for delivery.
        destination (str): Destination of the message.
    """

    def __init__(self, message, destination, **kwargs):
        """Initialise Check.

        Arguments:
            message (gefion.notifiers.message): Message object for delivery.
            destination (str): Destination of the message.
            kwargs (dict): Additional information required to initialise, such
                as SMTP server addresses or API keys.
        """
        self.message = message

    def send(self):
        """Send the message to the destination.

        Called without arguments

        Returns:
            bool: Successfulness of delivery.
        """
        raise NotImplementedError
