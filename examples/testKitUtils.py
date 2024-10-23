"""
    Elemental Internal testing Software
    Utilities Package for TestKit
"""
import errno
import html
import os
import platform
import logging
import re
import socket
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import List

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
        _hostname (str): The hostname or IP address of the MQTT broker. Default is 'localhost' or
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
            _hostname: str = os.environ.get('AWSIP', 'localhost'),
            topic: str = f'{project}/log',
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
        self.hostname = _hostname
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
    _client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
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

    logging.addLevelName(5, "VERBOSE")

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
    # add verbose method
    def verbose(self, message, *args, **kws):
        if self.isEnabledFor(5):
            self._log(5, message, args, **kws)

    setattr(log, "verbose", lambda message, *args, **kwargs: verbose(log, message, *args, **kwargs))

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


def run_command(command: str) -> str:
    """
    Run a command in the shell.

    :param command: The command to run.
    :type command: str
    :return: The output of the command.
    :rtype: str
    """
    process = subprocess.run(command, shell=True, capture_output=True,
                             text=True)
    return process.stdout


def ensure_exists(path):
    """
    Accepts path to file, then creates the directory path if it does not exist
    :param path:
    :return:
    """
    # pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    return path


def remove_file(files: List[str]) -> bool:
    """
    Removes old copies of files if they exist.

    :param files: The names of the files to remove.
    :return: `True` if all files were removed successfully, `False` otherwise.
    """
    success = True
    for f in files:
        try:
            os.remove(f)
            logger.debug(f'Removing previous copy of {f}..')
        except OSError:
            success = False
    return success


def get_contents(conf_file_path: str) -> str:
    """
    Reads the contents of a file and returns them as a string.

    Args:
        conf_file_path: The path to the file to be read.

    Returns:
        The contents of the file as a string.
    """
    import chardet

    # with open(file) as file:
    #     return file.read()
    # Detect the encoding of the .conf file
    # Detect the encoding of the .conf file
    with open(conf_file_path, 'rb') as file:
        raw_data = file.read()
        encoding = chardet.detect(raw_data)['encoding']

    # Read the .conf file with the detected encoding
    with open(conf_file_path, 'r', encoding=encoding) as file:
        conf_content = file.read()
    return conf_content


def json_to_xhtml(json_data):
    """
    Converts a Confluence JSON object to XHTML.

    Parameters:
    json_data (dict): A Confluence JSON object representing a Confluence page.

    Returns:
    str: A string of the converted XHTML content.
    """
    xhtml_content = ""

    for element in json_data['body']['storage']['value']:
        if element['type'] == 'paragraph':
            xhtml_content += "<p>" + html.escape(element['content']) + "</p>"
        elif element['type'] == 'hardBreak':
            xhtml_content += "<br/>"
        elif element['type'] == 'text':
            xhtml_content += html.escape(element['text'])
        elif element['type'] == 'link':
            link_text = element['title'] if 'title' in element else element[
                'href']
            xhtml_content += f'<a href="{element["href"]}">{html.escape(link_text)}</a>'

    return xhtml_content


def linePrepender(file, line, depth: int = 0, mode: int = 0):
    """
    Prepends given line to given file at depth.
    :param file: Filepath to write too
    :param line: str to write
    :param depth: # of Lines to move away from mode
    :param mode: 0=Top,1=current,2=Bottom
    :return:
    """
    with open(file, 'r+') as _file:
        _file.seek(depth, mode)
        _file.write(line.rstrip('\r\n') + '\n' + _file.read())


def ping_ip(ip_address="192.168.0.1") -> bool:
    """Pings the given IP address until it is successful.

   :param ip_address: The IP address to ping.
   :type ip_address: str
   :returns: bool

   .. note:: This function uses the `ping` command to ping the given IP address. It will continue to run
             the `ping` command until it is successful (i.e. the `ping` command returns a return code of 0)
    """
    # Determine the appropriate flag for the ping command based on the operating system
    if platform.system() == "Windows":
        ping_flag = "-n"
    else:
        ping_flag = "-c"

    while True:
        result = subprocess.run(["ping", ping_flag, "1", ip_address],
                                stdout=subprocess.PIPE)
        if result.returncode == 0:
            # Ping was successful
            return True
        else:
            logger.debug(f"Waiting for DUT to power on: {result.returncode}")
            time.sleep(4)


def get_ip() -> str:
    """
    Retrieve the IP address of the current machine.

    :return: A string containing the IP address of the current machine
    """
    return socket.gethostbyname(socket.gethostname())


def parse_status(string: str) -> any:
    """Parse an integer from a string using the regular expression pattern 'INTEGER: (\\d+)'.

    :param string: The string to parse.
    :type string: str
    :return: The parsed integer.
    :rtype: int | str
    """
    return parse_integer(string, r'INTEGER: (\d+)')


def parse_string(string: str, pattern: str) -> str:
    """Parse a string using the given regular expression pattern.

    :param string: The string to parse.
    :type string: str
    :param pattern: The regular expression pattern to use for parsing.
    :type pattern: str
    :return: The parsed string.
    :rtype: str
    """
    match = re.search(pattern, string)
    if match:
        return match.group(1)
    else:
        return f"{pattern} Not Found in {string}"


def parse_integer(string: str, pattern: str) -> any:
    """Parse an integer from a string using the given regular expression pattern.

    :param string: The string to parse.
    :type string: str
    :param pattern: The regular expression pattern to use for parsing.
    :type pattern: str
    :return: The parsed integer.
    :rtype: int | str
    """
    match = re.search(pattern, string)
    if match:
        return int(match.group(1))
    else:
        return f"{pattern} Not Found in {string}"


class NoAvailablePortError(Exception):
    """Raised when there isn't a viable port in the given range."""
    pass


def get_available_from_port_range(from_port: int, to_port: int) -> int:
    """Returns available local port number.
    Args:
        from_port: The start port to search
        to_port: The end port to search
    Returns:
        int: available local port number which are found first
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    for port in range(from_port, to_port):
        try:
            if sock.connect_ex(('localhost', port)) != 0:
                return port
        finally:
            sock.close()

    raise NoAvailablePortError(
        f'No available port between {from_port} and {to_port}')


def print_device_info():
    logger.info(f"Running on: {platform.system()}")
    logger.info(f"Deivce IP:  {get_ip()}")


if __name__ == '__main__':
    # get_slack_messages()
    # print(post_slack_message())
    post(topic="test", payload="message", retain=True)
    logger = makeLogger(__name__, False, 'VERBOSE')
    logger.info("Info message")
    logger.debug("Debug  message")
    logger.warning("Warning message")
    logger.verbose("Verbose message")
