import paho.mqtt.client as mqtt
import time
import random
import json

BROKER = "192.168.1.135"
PORT = 1883
CLIENT_ID = "sensor_humedad"
TOPIC = "planta/sensores/humedad"
INTERVALO = 5

def on_connect(client, userdata, flags, rc):
    print(f"Sensor humedad conectado al broker (código: {rc})")

client = mqtt.Client(CLIENT_ID)
client.on_connect = on_connect

client.connect(BROKER, PORT, 60)
client.loop_start()

while True:
    humedad = round(55 + random.uniform(-15, 15), 1)  # 40-70%
    humedad = max(30, min(80, humedad))  # límites realistas
    mensaje = json.dumps({"valor": humedad, "unidad": "%", "timestamp": time.time()})
    client.publish(TOPIC, mensaje, qos=1)
    print(f"Publicado humedad: {humedad}%")
    time.sleep(INTERVALO)