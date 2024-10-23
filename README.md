# mqttlogger

`mqttlogger` is a Python package that provides a custom logging handler to publish log messages to an MQTT broker. This is useful for centralizing log messages from distributed systems for monitoring and debugging purposes.

## Features

- Publish log messages to an MQTT broker.
- Configurable MQTT connection settings.
- Supports logging to both MQTT and local files.

## Installation

You can install `mqttlogger` via pip:

```
pip install mqttlogger
```

## Usage

Here's a basic example of how to use `mqttlogger` in your Python application:

```python
import logging
from mqttlogger import makeLogger

# Create a logger
logger = makeLogger(name='myapp', log_to_file=True, log_level='DEBUG')

# Log messages
logger.info("This is an info message")
logger.debug("This is a debug message")
logger.warning("This is a warning message")
```

## Singleton Logger

The `makeLogger` function returns a logger that acts as a singleton. This means that once a logger is created with specific setup values, you can retrieve the same logger instance elsewhere in your application without needing to re-specify those values. This is particularly useful for maintaining consistent logging behavior across different modules or components of your application.

To retrieve the logger again, simply call `logging.getLogger` with the same name:

```python
# Retrieve the existing logger instance
logger = logging.getLogger('myapp')

# Continue logging
logger.info("Continuing to log with the same logger instance")
```

## Testing

To test `mqttlogger` with a local Mosquitto broker, follow these steps:

### Prerequisites

Ensure that Mosquitto is installed on your system. You can install it using a package manager:

- **On Ubuntu/Debian**:
  ```bash
  sudo apt-get update
  sudo apt-get install mosquitto mosquitto-clients
  ```

- **On macOS** (using Homebrew):
  ```bash
  brew install mosquitto
  ```

### Running the Test

1. **Start the Mosquitto Broker**: The test script will automatically start a local Mosquitto broker.

2. **Run the Test Script**: Execute the test script to verify that `mqttlogger` is working correctly with the Mosquitto broker.

   ```bash
   python test_mqttlogger.py
   ```

   This script will start the broker, send a test log message, and then stop the broker.

## Configuration

The `mqttHandler` class allows you to configure various MQTT connection settings, such as:

- `hostname`: The MQTT broker's hostname or IP address.
- `port`: The port number to connect to the MQTT broker.
- `topic`: The MQTT topic to publish messages to.
- `qos`: The quality of service level for message delivery.
- `retain`: Whether the broker should retain the last message sent to the topic.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## Author

Dan Edens - [your.email@example.com](mailto:your.email@example.com)

## Acknowledgments

- [paho-mqtt](https://pypi.org/project/paho-mqtt/) for MQTT client functionality.
