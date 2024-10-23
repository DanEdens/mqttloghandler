import logging
import os
from datetime import datetime
from pathlib import Path

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

# Create utils specific fallback logger for Debugging debug mode
logger = logging.getLogger(__name__)
project = __name__
fileDate = datetime.now().strftime("%Y-%m-%d")
os.environ['ROOT_DIR'] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..')


class mqttHandler(logging.Handler):
    """A custom logging handler that publishes messages to an MQTT broker."""

    def __init__(
            self,
            _hostName: str = os.environ.get('AWSIP', 'localhost'),
            topic: str = f'{project}/{os.environ.get(f"{project}_device")}/log',
            qos: int = 1, retain: bool = True,
            _port: int = int(os.environ.get('AWSPORT', 1884)),
            client_id: str = '',
            keepalive: int = 60,
            will: str = None,
            auth: str = None,
            tls: str = None,
            protocol: int = 3,
            transport: str = 'tcp',
    ) -> object:
        logging.Handler.__init__(self)
        self.topic = topic
        self.qos = qos
        self.retain = retain
        self.hostname = _hostName
        self.port = _port
        self.client_id = client_id
        self.keepalive = keepalive
        self.will = will
        self.auth = auth
        self.tls = tls
        self.protocol = protocol
        self.transport = transport

    def emit(self, record):
        """Publish a single formatted logging record to a broker."""
        msg = self.format(record)
        publish.single(
            self.topic,
            msg,
            self.qos,
            self.retain,
            hostname=self.hostname,
            port=self.port,
            client_id=self.client_id,
            keepalive=self.keepalive,
            will=self.will,
            auth=self.auth,
            tls=self.tls,
            protocol=self.protocol,
            transport=self.transport
        )


def establishBroker():
    """Connect to the MQTT broker for logger mqttHandler stream."""
    _client = mqtt.Client()
    _client.connect(host=os.environ.get('AWSIP', 'localhost'),
                    port=int(os.environ.get('AWSPORT', 1884))
                    )
    return _client


def makeLogger(name: str = __name__, log_to_file: bool = False,
               log_level: str = 'DEBUG') -> logging.Logger:
    """Create the project wide logger."""
    name = name.replace(".", "/")
    _format = '%(asctime)s - %(module)s - %(message)s' if log_level == 'DEBUG' else '%(asctime)s - %(message)s'

    log = logging.getLogger(name)
    log.setLevel(log_level)

    if log_to_file:
        filename = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-TestKit.log"
        _log = ensure_exists(
            Path(os.environ['ROOT_DIR']).joinpath(f"data//{filename}"))
        file_handler = logging.FileHandler(_log)
        file_handler.setFormatter(logging.Formatter(_format))
        log.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(_format))
    log.addHandler(stream_handler)

    my_handler = mqttHandler(topic=f'DVT/{name}')
    log.addHandler(my_handler)
    return log


def ensure_exists(path):
    """Accepts path to file, then creates the directory path if it does not exist."""
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    return path

