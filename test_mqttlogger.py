import subprocess
import time
import logging
import os
from mqttlogger import makeLogger, establishBroker

CONFIG_FILE_PATH = 'mosquitto_test.conf'

def generate_mosquitto_config():
    """Generate a Mosquitto configuration file to allow publishes on port 3003."""
    config_content = """
    listener 3003
    allow_anonymous true
    """
    with open(CONFIG_FILE_PATH, 'w') as config_file:
        config_file.write(config_content)

def start_mosquitto_broker():
    """Start a local Mosquitto broker with the generated configuration."""
    generate_mosquitto_config()
    process = subprocess.Popen(['mosquitto', '-c', CONFIG_FILE_PATH],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    time.sleep(2)  # Give the broker time to start
    return process

def stop_mosquitto_broker(process):
    """Stop the Mosquitto broker."""
    process.terminate()
    process.wait()
    os.remove(CONFIG_FILE_PATH)  # Clean up the config file after use

def test_logging():
    """Test the mqttlogger by sending a log message."""
    logger = makeLogger(name='test_logger', log_to_file=False, log_level='DEBUG')
    logger.info("Test message to MQTT broker")

    # Verify the message was published (this part is simplified)
    # In a real test, you would subscribe to the topic and verify the message
    print("Log message sent to MQTT broker.")

if __name__ == '__main__':
    broker_process = start_mosquitto_broker()
    try:
        test_logging()
    finally:
        stop_mosquitto_broker(broker_process)
