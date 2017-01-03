# -*- coding: utf-8 -*-
"""Master endpoint and tasks."""

import argparse
import json
import logging

import yaml
from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from redis import Redis
from rq import Queue
from sqlalchemy import or_

from gefion.master_tasks import process_result
from gefion.models import Base, Monitor

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Load configuration file
parser = argparse.ArgumentParser(description='Gefion master.')
parser.add_argument('-c',
                    '--config',
                    help='Path to yaml configuration file.',
                    required=True)
config_file = open(parser.parse_args().config.strip())
config = yaml.safe_load(config_file)
logging.debug('Master configuration loaded: %s.', config)
config_file.close()

app = Flask(__name__)
auth = HTTPBasicAuth()
app.config['SQLALCHEMY_DATABASE_URI'] = config['database'].get('uri',
                                                               ':memory:')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

redis_host = config.get('rq', dict()).get('host', 'localhost')
redis_port = int(config.get('rq', dict()).get('port', 6379))
queue = Queue(connection=Redis(host=redis_host, port=redis_port))


@app.before_first_request
def setup():
    """Setup flask-sqlalchemy session with existing models."""
    Base.metadata.create_all(bind=db.engine)


@auth.get_password
def get_worker_password(username):
    """Return password of worker given its name.

    Arguments:
        username (str): Name of the worker from HTTP basic auth.
    """
    worker = config['workers'].get(username, None)
    if worker:
        return worker.get('key', None)


@app.route('/', methods=['GET'])
def index():
    """Index.

    Returns no content.
    """
    return ('', 204)


@app.route('/monitors', methods=['GET'])
@auth.login_required
def get_monitors():
    """Retrieve Monitors of a worker.

    The worker's name will be determined by the username given in
        the HTTP authorisation.
    """
    worker_name = auth.username()
    monitors = db.session.query(Monitor).filter(
        Monitor.worker == worker_name).all()
    return jsonify(monitors=[monitor.api_serialised for monitor in monitors])


@app.route('/result', methods=['POST'])
def receive_result():
    """Receive monitor result from worker."""
    monitor_id = request.form.get('id')
    monitor_unique_id = request.form.get('unique_id')
    result = json.loads(request.form.get('result'))
    monitor = db.session.query(Monitor).filter(or_(
        Monitor.id.like(monitor_id), Monitor.unique_id.like(
            monitor_unique_id))).first()
    if not monitor:
        return ('', 403)

    queue.enqueue(process_result, monitor, result, config)
    return ('', 204)


if __name__ == '__main__':
    app.run()
