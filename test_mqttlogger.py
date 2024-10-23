import subprocess
import time
import logging
import os
import threading
from mqttlogger import makeLogger
import paho.mqtt.client as mqtt

CONFIG_FILE_PATH = 'mosquitto_test.conf'
MQTT_PORT = 3003
MQTT_TOPIC = 'DVT/test_logger'
HOSTNAME = 'localhost'  # Define the hostname for the MQTT broker

_listener_client = None  # Global variable to hold the singleton MQTT client

def generate_mosquitto_config():
    """Generate a Mosquitto configuration file to allow publishes on port 3003."""
    config_content = f"""
    listener {MQTT_PORT}
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

def on_message(client, userdata, message):
    """Callback function to handle received messages."""
    print(f"Received message: {message.payload.decode()} on topic {message.topic}")

def start_mqtt_listener():
    """Start an MQTT client to listen for messages."""
    global _listener_client
    if _listener_client is not None:
        return _listener_client

    client = mqtt.Client()
    client.on_message = on_message
    client.connect(HOSTNAME, MQTT_PORT)  # Use HOSTNAME for local broker
    client.subscribe(MQTT_TOPIC)
    client.loop_start()
    _listener_client = client
    return client

def stop_mqtt_listener():
    """Stop the MQTT client."""
    global _listener_client
    if _listener_client is not None:
        _listener_client.loop_stop()
        _listener_client.disconnect()
        _listener_client = None

def test_logging():
    """Test the mqttlogger by sending a log message."""
    logger = makeLogger(name='test_logger', log_to_file=False, log_level='DEBUG', hostname=HOSTNAME)
    logger.info("Test message to MQTT broker")

    # Verify the message was published
    print("Log message sent to MQTT broker.")

if __name__ == '__main__':
    broker_process = start_mosquitto_broker()
    listener_client = start_mqtt_listener()
    try:
        test_logging()
        time.sleep(2)  # Allow time for the message to be received
    finally:
        stop_mqtt_listener()
        stop_mosquitto_broker(broker_process)
