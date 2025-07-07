import random

class SensorSimulator:
    """Simulates sensor data for temperature, humidity, and pressure."""

    def get_data(self):
        return {
            "temperature": round(random.uniform(20, 40), 2),
            "humidity": round(random.uniform(30, 80), 2),
            "pressure": round(random.uniform(950, 1050), 2),
        }
