# -*- coding: utf-8 -*-
"""Contains HTTPCheck, the web checker."""

import logging
import time

import requests

from gefion.checks import Check, Result

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

REQUESTS_METHOD_MAP = {'GET': requests.get,
                       'OPTONS': requests.options,
                       'HEAD': requests.head,
                       'POST': requests.post,
                       'PUT': requests.put,
                       'PATCH': requests.patch,
                       'DELETE': requests.delete}


class ResponseError(Exception):
    """Bad response."""


class StatusCodeResponseError(ResponseError):
    """Status code mismatch."""


class ContainResponseError(ResponseError):
    """Response does not contain expected strings."""


def assert_response(response,
                    status_code=None,
                    text_contain=str(),
                    headers_contain=dict()):
    """Assert Response contains required contents.

    Arguments:
        status_code (int): Expected status code. By default not checked.
        text_contain (str): String that the response text is expected to
            contain. By default blank.
        headers_contain (dict): Key is response header, value is the string
            expected to contain. By default not checked.

    Raises:
        ResponseError
    """
    if status_code and response.status_code != status_code:
        raise StatusCodeResponseError('Status code {}, expected {}.'.format(
            response.status_code, status_code))

    if response.text and text_contain not in response.text:
        raise ContainResponseError('Text {} not in body.'.format(text_contain))

    if response.headers and headers_contain:
        for key, expected_value in headers_contain.items():
            response_header_key = response.headers.get(key, str())
            if expected_value not in response_header_key:
                raise ContainResponseError('Header {}, {} not in {}.'.format(
                    key, expected_value, response_header_key))


class HTTPCheck(Check):
    """Checks and validates HTTP responses."""

    def __init__(self,
                 url,
                 verb,
                 data=dict(),
                 req_headers=dict(),
                 status_code=None,
                 text_contain=str(),
                 headers_contain=dict(),
                 **kwargs):
        """Initialise HTTPCheck.

        Arguments:
            url (str): HTTP/HTTPS URL of the resource.
            verb (str): HTTP verb. GET, OPTIONS, HEAD, POST, PUT, PATCH and
                DELETE.
            data (dict): Data to attach to body. Useful for POST requests.
            req_headers (dict): Custom headers to attach to the request.
            status_code (int): Expected status code. By default not checked.
            text_contain (str): String that the response text is expected to
                contain. By default blank.
            headers_contain (dict): Key is response header, value is the string
                expected to contain. By default not checked.
        """
        self.url = url
        self.data = data
        self.req_headers = req_headers
        self.status_code = status_code
        self.text_contain = text_contain
        self.headers_contain = headers_contain

        # Call different requests depneding on HTTP verb.
        self.requests_method = REQUESTS_METHOD_MAP.get(verb.upper(),
                                                       requests.get)

        super().__init__(**kwargs)

    def check(self):
        """Check HTTP site with requests.

        Returns:
            gefion.checks.Result
        """
        try:
            start_time = time.perf_counter()
            response = self.requests_method(url=self.url,
                                            data=self.data,
                                            headers=self.req_headers,
                                            allow_redirects=False)
            runtime = response.elapsed.total_seconds()
            assert_response(response, self.status_code, self.text_contain,
                            self.headers_contain)
            error = None
        except requests.exceptions.RequestException as err:
            end_time = time.perf_counter()
            runtime = end_time - start_time  # Response.elapsed not available.
            error = err
        except ResponseError as err:
            error = err

        availability = False if error else True
        message = str(error) if error else ''
        logging.info('Tested %s in %fs w/ message "%s".', availability,
                     runtime, message)
        return Result(availability, runtime, message)
