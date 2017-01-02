# -*- coding: utf-8 -*-
"""Worker RQ tasks."""

import json
import logging
from urllib.parse import urljoin

import requests
from retrying import RetryError, retry

from gefion import name_maps

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def result_is_false(result):
    """
    Determine if the availability of a Result is False.

    Arguments:
        result (gefion.checks.Result): Instance with availability to check.

    Returns:
        bool
    """
    try:
        return not result.availability
    except AttributeError:
        return True


@retry(retry_on_result=result_is_false,
       stop_max_attempt_number=3,
       wait_random_min=3000,
       wait_random_max=6000)
def run_check(check_name, arguments):
    """
    Execute check task.

    Arguments:
        check_name (str): Type of the check, name found in name_maps.
        arguments (dict): Argument of the check.

    Returns:
        gefion.checks.Result
    """
    if check_name in name_maps.CHECKS:
        check = name_maps.CHECKS[check_name](**arguments)
        return check.check()


def run_monitor(monitor_id, unique_id, check_name, arguments, endpoint_url):
    """
    Run check and report to backend.

    Arguments:
        monitor_id (str): Database ID of the Monitor.
        unique_id (str): UUID of the version.
        check_name (str): Type of the check, name found in name_maps.
        arguments (dict): Argument of the check.
        endpoint_url (str): Endpoint URL of master.

    Returns:
        bool: Success of execution and report.
    """
    try:
        check_result = run_check(check_name, arguments)
    except RetryError as error:
        check_result = error.args[0].value
    reporting_url = urljoin(endpoint_url, 'result')
    r = requests.post(reporting_url,
                      data={
                          'id': monitor_id,
                          'unique_id': unique_id,
                          'result': json.dumps(check_result.api_serialised)
                      })
    if r.status_code == 204:
        return True

    return False
