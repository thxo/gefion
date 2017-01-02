# -*- coding: utf-8 -*-
"""Worker task executions."""

import argparse
import json
import logging
from datetime import datetime
from urllib.parse import urljoin

import requests
import yaml
from redis import Redis
from rq_scheduler import Scheduler

from gefion import worker_tasks

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Load configuration file
parser = argparse.ArgumentParser(description='Gefion worker.')
parser.add_argument('-c',
                    '--config',
                    help='Path to yaml configuration file.',
                    required=True)
config_file = open(parser.parse_args().config.strip())
config = yaml.safe_load(config_file)
logging.debug('Master configuration loaded: %s.', config)
config_file.close()

redis_host = config.get('rq', dict()).get('host', 'localhost')
redis_port = int(config.get('rq', dict()).get('port', 6379))
scheduler = Scheduler(connection=Redis(host=redis_host, port=redis_port))


def fetch_monitors(scheduler):
    """Fetch Monitors and schedule accordingly.

    Arguments:
        scheduler (rq_scheduler.Scheduler): The Schedule instance initialized.
    """
    monitors_url = urljoin(config['master'].get('endpoint'), 'monitors')
    logging.info('Requesting endpoint for monitors at %s.', monitors_url)
    r = requests.get(monitors_url,
                     auth=(config.get('my_name'), config['master'].get('key')))
    logging.debug('Master returned following Monitors: %s.', r.text)
    monitors = json.loads(r.text).get('monitors')

    for job in scheduler.get_jobs():  # Delete all existing jobs.
        scheduler.cancel(job)

    # scheduler.enqueue_in(timedelta(minutes=10), fetch_monitors, scheduler)
    for monitor in monitors:
        scheduler.schedule(
            scheduled_time=datetime.utcnow(),
            func=worker_tasks.run_monitor,
            args=[
                monitor['id'],
                monitor['unique_id'],
                monitor['check'],
                json.loads(monitor['arguments']),
                config['master'].get('endpoint')],
            interval=monitor['frequency'] * 60,  # Minutes to seconds.
            repeat=None  # Repeat forever (until deletion).
        )


if __name__ == '__main__':
    fetch_monitors(scheduler)
