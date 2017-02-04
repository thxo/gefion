# -*- coding: utf-8 -*-
"""Contains CachetNotifier, the Cachet component updater."""

import logging
from urllib.parse import urljoin

import requests

from gefion.notifiers import Notifier

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def make_component_url(api_endpoint, component_id):
    """Make the API URL of a Cachet component.

    Arguments:
        api_endpoint (str): HTTP API endpoint of Cachet, usually at `/api/`.
        component_id (int): Cachet component ID number.

    Returns:
        str: API URL of the component.
    """
    if api_endpoint[-1] != '/':  # Otherwise urljoin strips last component.
        api_endpoint += '/'
    component_base = urljoin(api_endpoint, 'v1/components/')
    return urljoin(component_base, str(component_id))

class CachetNotifier(Notifier):
    """Updates Cachet components to up/down.

    Cachet (cachethq.io) is a self-hosted status page software.
    """

    def __init__(self, message, destination, **kwargs):
        """Initialise CachetNotifier.

        Arguments:
            message (gefion.notifiers.message): Message object for delivery.
            destination (str): Component ID number.
            api_endpoint (str): HTTP API endpoint of Cachet, usually at
                `/api/`.
            api_token (str): API token of a Cachet user of administrative
                privileges.
        """
        api_endpoint = kwargs.get('api_endpoint', 'http://localhost/api/')
        self.component_url = make_component_url(api_endpoint, int(destination))
        logger.debug('Component API URL is %s.', self.component_url)

        if message.result.availability:
            cachet_status = 1  # Status for "operational".
        else:
            cachet_status = 4  # Status for "major outage"
        self.request_data = {'status': cachet_status}
        logger.debug('Availability %s, set payload to %s.',
                     message.result.availability, self.request_data)

        api_token = kwargs.get('api_token', 'invalidtoken')
        self.request_headers = {'X-Cachet-Token': api_token}
        logger.debug('Got API token %s.', api_token)

    def send(self):
        """Update Cachet component.

        Returns:
            bool: Successfulness of delivery.
        """
        try:
            r = requests.put(self.component_url,
                             data=self.request_data,
                             headers=self.request_headers,
                             timeout=15)
        except requests.exceptions.RequestException as err:
            logging.error('Caught requests exception: %s.', str(err))
            return False

        if r.status_code == 200 and 'data' in r.json():
            return True
            logging.info('Updated component at %s.', self.component_url)
        else:
            return False
