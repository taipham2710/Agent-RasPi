import threading

import paho.mqtt.client as mqtt


class MqttClient:
    """MQTT client for agent communication. Supports connect, subscribe, publish, and message callback."""

    def __init__(self, broker, port, topic_sub, topic_pub, on_message=None):
        self.broker = broker
        self.port = port
        self.topic_sub = topic_sub
        self.topic_pub = topic_pub
        self.on_message = on_message
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self._thread = None

    def _on_connect(self, client, userdata, flags, rc):
        print(f"[MQTT] Connected to MQTT broker with result code {rc}")
        print(f"[MQTT] Subscribing to topic: {self.topic_sub}")
        client.subscribe(self.topic_sub)
        print(f"[MQTT] Successfully subscribed to: {self.topic_sub}")

    def _on_message(self, client, userdata, msg):
        print(
            f"[MQTT] Message received on topic: {msg.topic} | Payload: {msg.payload.decode()}"
        )
        if self.on_message:
            self.on_message(msg.topic, msg.payload.decode())

    def start(self):
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_forever()

    def publish(self, message):
        print(f"[MQTT] Publishing to topic {self.topic_pub}: {message}")
        self.client.publish(self.topic_pub, message)
