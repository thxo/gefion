# -*- coding: utf-8 -*-
"""Tests for checks."""

import time
import unittest

from gefion import checks


class TestPortCheck(unittest.TestCase):
    """Test PortCheck."""

    def setUp(self):
        """Setup PortCheck tests."""
        pass

    def tearDown(self):
        """Tear down PortCheck tests."""
        pass

    def test_init(self):
        """Test the initialisation of the PortCheck class."""
        init_check = checks.PortCheck('127.0.0.1', 12345, 42)
        self.assertEqual(init_check.host, '127.0.0.1')
        self.assertEqual(init_check.port, 12345)
        self.assertEqual(init_check.timeout, 42)

    def test_timeout(self):
        """Test the timeout argument."""
        timeout_check = checks.PortCheck('8.8.8.8', 53, timeout=0.0000000001)
        self.assertIn('timed out', timeout_check.check().message)

    def test_internet(self):
        """Test with Internet resources."""
        ip_check = checks.PortCheck('8.8.8.8', 53)
        self.assertTrue(ip_check.check().availability)

        hostname_check = checks.PortCheck('www.msftncsi.com', 80)
        self.assertTrue(hostname_check.check().availability)

        port_not_open_check = checks.PortCheck('8.8.8.8', 65535)
        self.assertFalse(port_not_open_check.check().availability)

        invalid_hostname_check = checks.PortCheck('fancy.but.invalid', 80)
        self.assertIn('[Errno -2]', invalid_hostname_check.check().message)

        invalid_port_check = checks.PortCheck('127.0.0.1', 424242)
        self.assertIn('port must be 0-65535',
                      invalid_port_check.check().message)


class TestResult(unittest.TestCase):
    """Test Result class."""

    def setUp(self):
        """Setup Result tests."""
        pass

    def tearDown(self):
        """Tear down Result tests."""
        pass

    def test_init(self):
        """Test the initialisation of the Result class."""
        init_result = checks.Result(False, 1.03e-05, 'Something happened.',
                                    1480000000)
        self.assertEqual(init_result.availability, False)
        self.assertEqual(init_result.runtime, 1.03e-05)
        self.assertEqual(init_result.message, 'Something happened.')
        self.assertEqual(init_result.timestamp, 1480000000)

    def test_timestamp(self):
        """Test the timestamp argument."""
        default_result = checks.Result(False, 1.03e-05, 'Something happened.')
        self.assertTrue(
            default_result.timestamp - time.time() < 1)  # Assume current time.
