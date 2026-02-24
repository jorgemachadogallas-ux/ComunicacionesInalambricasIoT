import paho.mqtt.client as mqtt
import time
import random
import json

BROKER = "192.168.1.135"
PORT = 1883
CLIENT_ID = "sensor_ph"
TOPIC = "planta/sensores/ph"
INTERVALO = 5

def on_connect(client, userdata, flags, rc):
    print(f"Sensor pH conectado al broker (código: {rc})")

client = mqtt.Client(CLIENT_ID)
client.on_connect = on_connect

client.connect(BROKER, PORT, 60)
client.loop_start()

while True:
    ph = round(6.5 + random.uniform(-1.2, 1.2), 2)  # 5.3-7.7 pH
    ph = max(5.0, min(8.0, ph))  # límites para plantas
    mensaje = json.dumps({"valor": ph, "unidad": "pH", "timestamp": time.time()})
    client.publish(TOPIC, mensaje, qos=1)
    print(f"Publicado pH: {ph}")
    time.sleep(INTERVALO)