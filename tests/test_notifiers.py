# -*- coding: utf-8 -*-
"""Tests for notifiers."""

import unittest

from gefion import notifiers
from gefion.checks import Result


class TestTelegramNotifier(unittest.TestCase):
    """Test TelegramNotifier."""

    def setUp(self):
        """Setup TelegramNotifier tests."""
        pass

    def tearDown(self):
        """Tear down TelegramNotifier tests."""
        pass

    def test_init(self):
        """Test the initialisation of the TelegramNotifier class."""
        test_message = notifiers.Message('Test Machine', Result(
            True, 1, 'Additional message.', 1480000000))
        init_notifier = notifiers.TelegramNotifier(test_message, '-1000')
        self.assertEqual(init_notifier.destination, '-1000')

    def test_text(self):
        """Test message text generation."""
        up_message = notifiers.Message('Test Machine', Result(
            True, 1, 'Additional message.', 1480000000))
        up_notifier = notifiers.TelegramNotifier(up_message, '-1000')
        self.assertEqual(up_notifier.text,
                         '*Test Machine* is *UP* at 2016-11-24T15:06:40Z.')
        up_template = '↑{host}{time},Msg={message}'
        up_notifier_with_template = notifiers.TelegramNotifier(
            up_message, '-1000', up_template=up_template)
        self.assertEqual(
            up_notifier_with_template.text,
            '↑Test Machine2016-11-24T15:06:40Z,Msg=Additional message.')

        down_message = notifiers.Message('Test Machine',
                                         Result(False, 1, 'Msg.', 1480000000))
        down_notifier = notifiers.TelegramNotifier(down_message, '-1000')
        self.assertEqual(
            down_notifier.text,
            '*Test Machine* is *DOWN* at 2016-11-24T15:06:40Z. Msg: Msg.')
        down_template = '↓{host}{time},Msg={message}'
        down_notifier_with_template = notifiers.TelegramNotifier(
            down_message, '-1000',
            down_template=down_template)
        self.assertEqual(down_notifier_with_template.text,
                         '↓Test Machine2016-11-24T15:06:40Z,Msg=Msg.')


class TestPostmarkNotifier(unittest.TestCase):
    """Test PostmarkNotifier."""

    def setUp(self):
        """Setup PostmarkNotifier tests."""
        self.test_message = notifiers.Message('Test Machine', Result(
            True, 1, 'Additional message.', 1480000000))

    def tearDown(self):
        """Tear down PostmarkNotifier tests."""
        pass

    def test_template_model(self):
        """Test Postmark template model generation."""
        made_model = notifiers.postmark.make_template_model(
            self.test_message, 'It works!', 'It ain\'t right!')
        expected_model = {'name': 'Test Machine',
                          'availability': 'It works!',
                          'time_string': '2016-11-24T15:06:40Z'}
        self.assertEqual(made_model, expected_model)

    def test_init(self):
        """Test the initialisation of the PostmarkNotifier class."""
        init_notifier = notifiers.PostmarkNotifier(
            self.test_message,
            'destination@unit.test',
            server_token='test-token',
            from_address='from@unit.test',
            template_id=111111)
        self.assertEqual(init_notifier.destination, 'destination@unit.test')
        self.assertEqual(init_notifier.server_token, 'test-token')
        self.assertEqual(init_notifier.from_address, 'from@unit.test')
        self.assertEqual(init_notifier.template_id, 111111)
        self.assertEqual(init_notifier.template_model,
                         {'name': 'Test Machine',
                          'availability': 'UP',
                          'time_string': '2016-11-24T15:06:40Z'})


class TestMessage(unittest.TestCase):
    """Test Message class."""

    def setUp(self):
        """Setup Message tests."""
        pass

    def tearDown(self):
        """Tear down Message tests."""
        pass

    def test_init(self):
        """Test the initialisation of the Message class."""
        test_result = Result(True, 1, 'Additional message.', 1480000000)
        init_message = notifiers.Message('Test Machine', test_result)
        self.assertEqual(init_message.hostname, 'Test Machine')
        self.assertEqual(init_message.result, test_result)
