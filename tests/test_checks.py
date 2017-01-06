# -*- coding: utf-8 -*-
"""Tests for checks."""

import time
import unittest

import requests

from gefion import checks


class TestCheck(unittest.TestCase):
    """Test Check base class.."""

    def setUp(self):
        """Setup PortCheck tests."""
        pass

    def tearDown(self):
        """Tear down PortCheck tests."""
        pass

    def test_check_not_implemented(self):
        """Ensure base class throws NotImplementedError."""
        base_check = checks.Check()
        self.assertRaises(NotImplementedError, base_check.check)


class TestHTTPCheck(unittest.TestCase):
    """Test HTTPCheck."""

    def setUp(self):
        """Setup HTTPCheck tests."""
        pass

    def tearDown(self):
        """Tear down HTTPCheck tests."""
        pass

    def test_init(self):
        """Test the initialisation of the HTTPCheck class."""
        init_check = checks.HTTPCheck('https://www.example.com/', 'POST',
                                      {'post-some': 'data'},
                                      {'x-custom-header': 'header'}, 204,
                                      'iana', {'Accept-Ranges': 'bytes'})
        self.assertEqual(init_check.url, 'https://www.example.com/')
        self.assertEqual(init_check.requests_method, requests.post)
        self.assertEqual(init_check.data, {'post-some': 'data'})
        self.assertEqual(init_check.req_headers, {'x-custom-header': 'header'})
        self.assertEqual(init_check.status_code, 204)
        self.assertEqual(init_check.text_contain, 'iana')
        self.assertEqual(init_check.headers_contain,
                         {'Accept-Ranges': 'bytes'})

    def test_assert_response(self):
        """Test the assert_response() method."""
        class FakeResponse(object):
            """Duck-types requests.Response."""

            status_code = 404
            headers = {'Accept-Ranges': 'bytes'}
            text = 'ok'

        self.assertIsNone(checks.http.assert_response(FakeResponse))
        self.assertIsNone(checks.http.assert_response(
            FakeResponse, 404, 'ok', {'Accept-Ranges': 'bytes'}))
        self.assertRaises(checks.http.StatusCodeResponseError,
                          checks.http.assert_response, FakeResponse, 200)
        self.assertRaises(checks.http.ContainResponseError,
                          checks.http.assert_response, FakeResponse, 404,
                          'fail')
        self.assertRaises(checks.http.ContainResponseError,
                          checks.http.assert_response,
                          FakeResponse,
                          404,
                          'ok',
                          headers_contain={'Accept-Ranges': 'none'})
        self.assertRaises(checks.http.ContainResponseError,
                          checks.http.assert_response,
                          FakeResponse,
                          404,
                          'ok',
                          headers_contain={'Accept-Ranges': 'bytes',
                                           'X-Extra-Header':
                                           'not-present'})

    def test_internet(self):
        """Test with Internet resources."""
        http_204_check = checks.HTTPCheck('http://httpbin.org/status/204',
                                          'GET',
                                          status_code=204)
        self.assertTrue(http_204_check.check().availability)

        http_204_fail_check = checks.HTTPCheck('http://httpbin.org/status/204',
                                               'GET',
                                               status_code=200)
        self.assertEqual(http_204_fail_check.check().message,
                         'Status code 204, expected 200.')

        bad_url_check = checks.HTTPCheck('http://invalidhost', 'GET')
        self.assertIn('Errno -2', bad_url_check.check().message)


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

        port_not_open_check = checks.PortCheck('8.8.8.8', 65535, timeout=2)
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

    def test_api_serialise(self):
        """Test the api_serialised property."""
        result = checks.Result(False, 1.03e-05, 'Something happened.',
                               1480000000)
        expected_dict = {'availability': False,
                         'runtime': 1.03e-05,
                         'message': 'Something happened.',
                         'timestamp': 1480000000}
        self.assertEqual(result.api_serialised, expected_dict)
