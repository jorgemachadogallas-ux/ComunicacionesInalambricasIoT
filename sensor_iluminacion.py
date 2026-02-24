import paho.mqtt.client as mqtt
import time
import random
import json

BROKER = "192.168.1.135"
PORT = 1883
CLIENT_ID = "sensor_iluminacion"
TOPIC = "planta/sensores/iluminacion"
INTERVALO = 5

def on_connect(client, userdata, flags, rc):
    print(f"Sensor iluminación conectado al broker (código: {rc})")

client = mqtt.Client(CLIENT_ID)
client.on_connect = on_connect

client.connect(BROKER, PORT, 60)
client.loop_start()

while True:
    lux = random.randint(200, 1200)  # 200-1200 lux (día/noche)
    mensaje = json.dumps({"valor": lux, "unidad": "lux", "timestamp": time.time()})
    client.publish(TOPIC, mensaje, qos=1)
    print(f"Publicado iluminación: {lux} lux")
    time.sleep(INTERVALO)