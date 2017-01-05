# -*- coding: utf-8 -*-
"""Master RQ tasks."""

import logging
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from gefion import name_maps
from gefion.checks import Result
from gefion.models import Base
from gefion.notifiers import Message

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def notify(notifier_name, hostname, result, destination, config):
    """Notify using Notifiers.

    Arguments:
        notifier_name (str): Name of Notifier. See name_maps.
        hostname (str): Name of resource being checked.
        result (gefion.checks.Result): Result of the check.
        destination (str): Message recipient.
        config (dict): Entire loaded configuration file.

    Returns:
        bool: Successfulness of notification.
    """
    logging.debug('Notifying %s with method %s to %s.', hostname,
                  notifier_name, destination)
    notifier_config = config.get(notifier_name, dict())
    logging.debug('Got notifier config %s.', notifier_config)
    if notifier_name not in name_maps.NOTIFIERS:
        return False
    message = Message(hostname, result)
    notifier = name_maps.NOTIFIERS[notifier_name](message=message,
                                                  destination=destination,
                                                  **notifier_config)
    return notifier.send()


def process_result(monitor, result_dict, config):
    """Process monitoring result received from worker.

    Arguments:
        monitor (gefion.models.Monitor): Instance of database model Monitor.
        result_dict (dict): Dictionary of results depicting Result class,
            submitted by workers.
        config (dict): Entire loaded configuration file.
    """
    hostname = monitor.name
    result = Result(
        result_dict.get('availability'), result_dict.get('runtime'),
        result_dict.get('message'), result_dict.get('timestamp'))

    # Initialise SQLAlchemy
    engine = create_engine(config['database'].get('uri', ':memory:'))
    Base.metadata.bind = engine
    Base.metadata.create_all()
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    monitor = session.merge(monitor)

    logging.debug('%s last result was %s.', hostname,
                  monitor.last_availability)
    logging.info('%s latest result is %s.', hostname, result.availability)
    if monitor.last_availability != result.availability:
        for contact in monitor.contacts:
            notify(contact.notifier, hostname, result, contact.destination,
                   config)

    monitor.last_availability = result.availability
    monitor.last_message = result.message
    monitor.last_updated = datetime.fromtimestamp(result.timestamp)
    session.add(monitor)
    session.commit()
