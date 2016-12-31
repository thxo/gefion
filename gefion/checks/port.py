# -*- coding: utf-8 -*-
"""Contains PortCheck, the TCP port checker."""

import logging
import socket
import time

from gefion.checks import Check, Result

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PortCheck(Check):
    """Checks if TCP ports are open."""

    def __init__(self, host, port, timeout=5, **kwargs):
        """Initialise PortCheck.

        Arguments:
            host (str): IP address or hostname.
            port (int): Port number.
            timeout (int): Connection timeout in seconds.
        """
        logging.debug('Initialising with %s:%d, timeout %ds.', host, port,
                      timeout)
        self.host = host
        self.port = port
        self.timeout = timeout

        super().__init__(**kwargs)

    def check(self):
        """Check if port is open."""
        sock = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        try:
            start_time = time.perf_counter()
            sock.connect((self.host, self.port))
            end_time = time.perf_counter()
            sock.close()
            error = None
        except (socket.error, socket.gaierror, OverflowError) as err:
            end_time = time.perf_counter()
            sock.close()
            logger.warning('Caught exception: %s.', repr(err))
            error = err

        availability = False if error else True
        runtime = end_time - start_time
        message = str(error) if error else ''
        logging.info('Tested %s in %fs w/ message "%s".', availability,
                     runtime, message)
        return Result(availability, runtime, message)
