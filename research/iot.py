# IoT Smart Agriculture System (Research-Aligned, Complete)
import time
import json
import random
import threading
from datetime import datetime
from dataclasses import dataclass
from enum import Enum, auto
import paho.mqtt.client as mqtt

# ====================== **1. Core Structures** ======================
class SensorType(Enum):
    TEMPERATURE = auto()
    SOIL_MOISTURE = auto()
    LIGHT_INTENSITY = auto()
    CO2_LEVEL = auto()
    HUMIDITY = auto()

class ActuatorType(Enum):
    IRRIGATION = auto()
    COOLING = auto()
    VENTILATION = auto()
    FERTILIZER_DOSER = auto()

@dataclass
class SensorReading:
    sensor_type: SensorType
    value: float
    unit: str
    timestamp: str

    def to_dict(self):
        """Convert SensorReading object to a dictionary for JSON serialization."""
        return {
            "sensor_type": self.sensor_type.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp
        }

# ====================== **2. Five-Layer Implementation** ======================
# ----------- **Layer 1: Perception (Sensors)** -----------
class SensorHub:
    def __init__(self):
        self.sensors = {
            SensorType.TEMPERATURE: {"min": 20, "max": 30, "unit": "°C"},
            SensorType.SOIL_MOISTURE: {"min": 30, "max": 70, "unit": "%"},
            SensorType.LIGHT_INTENSITY: {"min": 0, "max": 100, "unit": "lux"},
            SensorType.CO2_LEVEL: {"min": 300, "max": 1000, "unit": "ppm"},
            SensorType.HUMIDITY: {"min": 40, "max": 80, "unit": "%"}
        }

    def read_all(self):
        timestamp = datetime.now().isoformat()
        return [
            SensorReading(sensor, round(random.uniform(params["min"], params["max"]), 1), params["unit"], timestamp)
            for sensor, params in self.sensors.items()
        ]

# ----------- **Layer 2: Transport (MQTT + LoRaWAN Sim)** -----------
class CommunicationManager:
    def __init__(self):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = lambda c, u, f, rc: print(f"MQTT Connected (Code: {rc})")
        self.mqtt_client.connect("test.mosquitto.org", 1883, 60)
        threading.Thread(target=self.mqtt_client.loop_forever, daemon=True).start()

    def send(self, data):
        # Convert SensorReading objects to dictionaries
        serialized_data = [reading.to_dict() for reading in data]
        self.mqtt_client.publish("iot/agriculture/data", json.dumps(serialized_data))
        print(f"[LoRaWAN Sim] Sent long-range packet (Size: {len(str(serialized_data))} bytes)")

# ----------- **Layer 3: Processing (Edge AI)** -----------
class EdgeProcessor:
    def analyze(self, sensor_data):
        # Extract key metrics
        temp = next(d.value for d in sensor_data if d.sensor_type == SensorType.TEMPERATURE)
        humidity = next(d.value for d in sensor_data if d.sensor_type == SensorType.HUMIDITY)
        moisture = next(d.value for d in sensor_data if d.sensor_type == SensorType.SOIL_MOISTURE)

        # Simulated AI model output
        crop_stress = random.uniform(0, 1)

        return {
            "raw_data": [vars(d) for d in sensor_data],
            "metrics": {
                "dew_point": round(temp - ((100 - humidity) / 5), 1),
                "heat_index": round(temp + humidity * 0.1, 1)
            },
            "predictions": {
                "crop_stress_risk": crop_stress,
                "irrigation_needed": crop_stress > 0.7,
                "optimal_watering": "ASAP" if crop_stress > 0.7 else "6h"
            }
        }

# ----------- **Layer 4: Application (Services)** -----------
class ApplicationServices:
    def __init__(self):
        self.actuators = {actuator: False for actuator in ActuatorType}

    def process(self, processed_data):
        if processed_data["predictions"]["irrigation_needed"]:
            self.activate_actuator(ActuatorType.IRRIGATION, True)
        if processed_data["metrics"]["heat_index"] > 30:
            self.activate_actuator(ActuatorType.COOLING, True)

    def activate_actuator(self, actuator, state):
        self.actuators[actuator] = state
        print(f"Actuator {actuator.name} → {'ON' if state else 'OFF'}")

# ----------- **Layer 5: Business Intelligence** -----------
class BusinessLogic:
    def __init__(self):
        self.history = []

    def analyze(self, processed_data):
        self.history.append(processed_data)
        if len(self.history) % 5 == 0:
            print("\n=== Business Report ===")
            print(f"Total Data Points: {len(self.history)}")
            print("Recent Stress Levels:", [d["predictions"]["crop_stress_risk"] for d in self.history[-3:]])
            print("Recommended Actions: Check irrigation valves\n")

# ====================== **3. Security & Storage** ======================
class SecurityManager:
    @staticmethod
    def encrypt(data):
        return {
            "payload": [d.to_dict() for d in data],
            "encrypted": True,
            "signature": f"SECURE-{random.getrandbits(128):032x}",
            "timestamp": datetime.now().isoformat()
        }

class Storage:
    def __init__(self):
        self.local_db = []
        self.cloud_sync_interval = 5

    def save(self, data):
        self.local_db.append(data)
        if len(self.local_db) % self.cloud_sync_interval == 0:
            print(f"📤 Cloud Sync: Uploaded {self.cloud_sync_interval} records")

# ====================== **4. Main System** ======================
class SmartAgricultureSystem:
    def __init__(self):
        print("🌱 Initializing IoT Smart Farm System...")
        self.sensors = SensorHub()
        self.comm = CommunicationManager()
        self.processor = EdgeProcessor()
        self.security = SecurityManager()
        self.storage = Storage()
        self.app = ApplicationServices()
        self.business = BusinessLogic()

    def run(self):
        try:
            while True:
                print("\n" + "="*40)
                print(f"Cycle @ {datetime.now().strftime('%H:%M:%S')}")
                # 1. Perception Layer
                sensor_data = self.sensors.read_all()
                print("📡 Sensor Data:", [f"{s.sensor_type.name}: {s.value}{s.unit}" for s in sensor_data])
                # 2. Security Layer
                encrypted_data = self.security.encrypt(sensor_data)
                # 3. Transport Layer
                self.comm.send(sensor_data)
                # 4. Processing Layer
                processed_data = self.processor.analyze(sensor_data)
                print("🧠 Edge AI Output:", processed_data["predictions"])
                # 5. Application Layer
                self.app.process(processed_data)
                # 6. Business Layer
                self.business.analyze(processed_data)
                # Storage
                self.storage.save(processed_data)
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n🛑 System shutdown")

# ====================== **Execution** ======================
if __name__ == "__main__":
    system = SmartAgricultureSystem()
    system.run()