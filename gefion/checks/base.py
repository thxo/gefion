# -*- coding: utf-8 -*-
"""Base classes."""

import time


class Result(object):
    """Provides results of a Check.

    Attributes:
        availability (bool): Availability, usually reflects outcome of a check.
        runtime (float): Time consumed running the check, in seconds.
        message (string): Additional explainations for the result.
        timestamp (int): UTC timestamp of the check.
    """

    def __init__(self, availability, runtime, message, timestamp=time.time()):
        """Initialise Result.

        Args:
            See class attributes.
        """
        self.availability = availability
        self.runtime = runtime
        self.message = message
        self.timestamp = timestamp

    @property
    def api_serialised(self):
        """Return serialisable data for API monitor assignments."""
        return {'availability': self.availability,
                'runtime': self.runtime,
                'message': self.message,
                'timestamp': self.timestamp}


class Check(object):
    """Performs checks for availability of resources.

    This should be inherited by checking implementations.
    """

    def __init__(self, **kwargs):
        """Initialise Check."""
        pass

    def check(self):
        """Check if specified resource is availability.

        Called without arguments.

        Returns:
            gefion.checkers.Result
        """
        raise NotImplementedError
