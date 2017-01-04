# -*- coding: utf-8 -*-
"""Worker task executions."""

import argparse
import logging

import yaml
from redis import Redis
from rq_scheduler import Scheduler

from gefion.worker_tasks import fetch_monitors

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

if __name__ == '__main__':
    fetch_monitors(scheduler, config)
