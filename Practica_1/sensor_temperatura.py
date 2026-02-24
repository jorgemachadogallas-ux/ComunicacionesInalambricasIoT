import paho.mqtt.client as mqtt
import time
import random
import json

BROKER = "192.168.1.135"
PORT = 1883
CLIENT_ID = "sensor_temperatura"
TOPIC = "planta/sensores/temperatura"
INTERVALO = 5  # segundos

def on_connect(client, userdata, flags, rc):
    print(f"Sensor temperatura conectado al broker (código: {rc})")

client = mqtt.Client(CLIENT_ID)
client.on_connect = on_connect

client.connect(BROKER, PORT, 60)
client.loop_start()

while True:
    temp = round(25 + random.uniform(-2, 3), 2)  # 23-28°C
    mensaje = json.dumps({"valor": temp, "unidad": "C", "timestamp": time.time()})
    client.publish(TOPIC, mensaje, qos=1)
    print(f"Publicado temperatura: {temp}°C")
    time.sleep(INTERVALO)