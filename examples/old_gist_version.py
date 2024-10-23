import errno
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
    """A custom logging handler that publishes messages to an MQTT broker.

    This handler uses the paho-mqtt library to connect to an MQTT broker and publish log messages
    as MQTT messages. The handler can be used to send log messages from a Python application to a
    centralized log server, or to any other system that can subscribe to the MQTT topic.

    Args:
        _hostName (str): The hostname or IP address of the MQTT broker. Default is 'localhost' or
            the value of the AWSIP environment variable.
        topic (str): The MQTT topic to publish messages to. The default value is constructed from
            the 'project' and 'project_device' environment variables, which are assumed to contain
            the name of the current project and the name of the current device or instance, separated
            by a forward slash. For example, if project='myapp' and project_device='dev1', the default
            topic will be 'myapp/dev1/log'.
        qos (int): The quality of service (QoS) level to use when publishing messages. The default
            is QoS level 1.
        retain (bool): If set to True, the MQTT broker will retain the last message sent to the topic.
            The default is True.
        _port (int): The port number to use when connecting to the MQTT broker. The default is 1884
            or the value of the AWSPORT environment variable.
        client_id (str): The client ID to use when connecting to the MQTT broker. If not specified,
            a random client ID will be generated.
        keepalive (int): The keepalive time, in seconds, for the MQTT connection. The default is 60.
        will (str): A last will and testament message to send to the MQTT broker if the connection is
            unexpectedly lost. The default is None.
        auth (str): An optional username and password string to use when connecting to the MQTT broker.
            The format of the string is 'username:password'. The default is None.
        tls (str): An optional path to a file containing the TLS certificate for the MQTT broker. If
            not specified, TLS encryption will not be used. The default is None.
        protocol (int): The MQTT protocol version to use. The default is MQTTv3.1.1.
        transport (str): The transport protocol to use. The default is 'tcp', which uses the standard
            TCP/IP protocol. Other options include 'websockets', which uses the WebSocket protocol.

    Attributes:
        topic (str): The MQTT topic to publish messages to.
        qos (int): The quality of service (QoS) level to use when publishing messages.
        retain (bool): Whether the MQTT broker should retain the last message sent to the topic.
        hostname (str): The hostname or IP address of the MQTT broker.
        port (int): The port number to use when connecting to the MQTT broker.
        client_id (str): The client ID to use when connecting to the MQTT broker.
        keepalive (int): The keepalive time, in seconds, for the MQTT connection.
        will (str): The last will and testament message to send to the MQTT broker if the connection
            is unexpectedly lost.
        auth (str): The username and password string to use when connecting to the MQTT broker.
        tls (str): The path to the TLS certificate file for the MQTT broker.
        protocol (int): The MQTT protocol version to use.
        transport (str): The transport protocol to use.

    """

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
        """
        The emit method in this code is responsible for publishing a single formatted logging record to a broker and then disconnecting cleanly.
        The method takes a single parameter record, which represents the logging record to be published.

        The purpose of this section of code is to allow for logging messages to be sent to a broker, where they can be consumed by other applications or services.
        This can be useful in distributed systems where log messages need to be centralized for monitoring and debugging purposes.

        The emit method formats the logging record using the format method and then publishes the resulting message using the publish.single method.
        The various parameters passed to publish.single specify details such as the topic to publish to, the quality of service, and authentication details.
        After the message is published, the connection to the broker is cleanly disconnected.

        This code provides a convenient way to integrate logging functionality into a distributed system using a message broker.
        """
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
    """
    Connect to the MQTT broker for logger mqttHandler stream
    :return:
    """
    _client = mqtt.Client()
    _client.connect(host=os.environ.get('AWSIP', 'localhost'),
                    port=int(os.environ.get('AWSPORT', 1884))
                    )
    return _client


def makeLogger(name: str = __name__, log_to_file: bool = False,
               log_level: str = 'DEBUG') -> logging.Logger:
    """
    Create the project wide logger.

    :param name: The name of the logger.
    :param log_to_file: Whether to log to a file.
    :param log_level: The log level to use (e.g. 'DEBUG', 'INFO').
    :return: A logger object.
    """
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


def post(topic: str, payload: str, retain: bool = False,
         _client=establishBroker()):
    """
    Post msg to MQTT broker

    :type _client: object
    :type retain: bool
    :param _client: Logging handler. By default, it is created by this module
    :param retain: Retain topic on broker
    :param topic: Project name
    :param payload: Sensor Data
    """
    topic = str(f'{project}/{topic}')
    payload = str(payload)
    try:
        _client.publish(topic=topic, payload=payload, qos=0, retain=retain)
    except ValueError:
        logger.warning(
            f"pub Failed because of wildcard: {str(topic)}=:={str(payload)}")
        logger.warning(f"Attempting fix...")
        try:
            tame_t = topic.replace("+", "_")
            tame_topic = tame_t.replace("#", "_")
            tame_p = payload.replace("+", "_")
            tame_payload = tame_p.replace("#", "_")
            _client.publish(topic=str(tame_topic), payload=str(tame_payload),
                            qos=1, retain=retain)
            logger.debug("Fix successful, Sending data...")
        except Exception as error:
            logger.warning(f"Fix Failed. Bug report sent.")
            _client.publish(f"{project}/error", str(error), qos=1, retain=True)

def ensure_exists(path):
    """
    Accepts path to file, then creates the directory path if it does not exist
    :param path:
    :return:
    """
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    return path
