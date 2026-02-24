import paho.mqtt.client as mqtt
import time
import json

BROKER = "192.168.1.135"
PORT = 1883
CLIENT_ID = "actuador_temperatura"
TOPIC_SENSOR = "planta/sensores/temperatura"
TOPIC_CMD = "planta/actuadores/temperatura/cmd"
TOPIC_STATUS = "planta/actuadores/temperatura/status"
TEMP_OBJETIVO = 25.0  # °C
TOLERANCIA = 0.5

estado_calefaccion = "OFF"
estado_refrigeracion = "OFF"

def on_connect(client, userdata, flags, rc):
    print(f"Actuador temperatura conectado (código: {rc})")
    client.subscribe(TOPIC_SENSOR, qos=1)

def on_message(client, userdata, msg):
    global estado_calefaccion, estado_refrigeracion
    try:
        data = json.loads(msg.payload.decode())
        temp = data["valor"]
        print(f"Temperatura recibida: {temp}°C")
        
        if temp > TEMP_OBJETIVO + TOLERANCIA:
            estado_refrigeracion = "ON"
            estado_calefaccion = "OFF"
            comando = json.dumps({"accion": "refrigeracion", "estado": "ON"})
        elif temp < TEMP_OBJETIVO - TOLERANCIA:
            estado_calefaccion = "ON"
            estado_refrigeracion = "OFF"
            comando = json.dumps({"accion": "calefaccion", "estado": "ON"})
        else:
            estado_calefaccion = "OFF"
            estado_refrigeracion = "OFF"
            comando = json.dumps({"accion": "todo", "estado": "OFF"})
        
        client.publish(TOPIC_CMD, comando, qos=1)
        status = json.dumps({
            "calefaccion": estado_calefaccion,
            "refrigeracion": estado_refrigeracion,
            "temp_actual": temp
        })
        client.publish(TOPIC_STATUS, status, qos=1)
        print(f"Comando enviado: {comando}")
    except Exception as e:
        print(f"Error procesando mensaje: {e}")

client = mqtt.Client(CLIENT_ID)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()