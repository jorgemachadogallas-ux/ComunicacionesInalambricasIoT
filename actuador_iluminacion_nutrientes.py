import paho.mqtt.client as mqtt
import time
import json

BROKER = "192.168.1.135"
PORT = 1883
CLIENT_ID = "actuador_ilum_nutrientes"
TOPIC_ILUM = "planta/sensores/iluminacion"
TOPIC_PH = "planta/sensores/ph"
TOPIC_CMD_ILUM = "planta/actuadores/iluminacion/cmd"
TOPIC_CMD_NUT = "planta/actuadores/nutrientes/cmd"
TOPIC_STATUS = "planta/actuadores/iluminacion_nutrientes/status"

# Umbrales
LUX_MINIMO = 400
PH_MINIMO = 6.0
PH_MAXIMO = 7.0

estado_luz = "OFF"
estado_nutrientes = "OFF"

def on_connect(client, userdata, flags, rc):
    print(f"Actuador iluminación/nutrientes conectado (código: {rc})")
    client.subscribe(TOPIC_ILUM, qos=1)
    client.subscribe(TOPIC_PH, qos=1)

def on_message(client, userdata, msg):
    global estado_luz, estado_nutrientes
    try:
        data = json.loads(msg.payload.decode())
        topic = msg.topic
        
        if topic == TOPIC_ILUM:
            lux = data["valor"]
            print(f"Iluminación recibida: {lux} lux")
            if lux < LUX_MINIMO:
                estado_luz = "ON"
                comando = json.dumps({"estado": "ON", "cantidad": "100%"})
            else:
                estado_luz = "OFF"
                comando = json.dumps({"estado": "OFF", "cantidad": "0%"})
            client.publish(TOPIC_CMD_ILUM, comando, qos=1)
            
        elif topic == TOPIC_PH:
            ph = data["valor"]
            print(f"pH recibido: {ph}")
            if ph < PH_MINIMO:
                estado_nutrientes = "ON"
                cantidad = round((PH_MINIMO - ph) * 10, 1)  # más bajo pH, más nutrientes
                comando = json.dumps({"estado": "ON", "cantidad": f"{cantidad}ml"})
            elif ph > PH_MAXIMO:
                estado_nutrientes = "OFF"
                comando = json.dumps({"estado": "OFF", "cantidad": "0ml"})
            else:
                estado_nutrientes = "NORMAL"
                comando = json.dumps({"estado": "NORMAL", "cantidad": "0ml"})
            client.publish(TOPIC_CMD_NUT, comando, qos=1)
        
        # Publicar estado global
        status = json.dumps({
            "luz": estado_luz,
            "nutrientes": estado_nutrientes
        })
        client.publish(TOPIC_STATUS, status, qos=1)
        print(f"Estado actualizado: luz={estado_luz}, nutrientes={estado_nutrientes}")
        
    except Exception as e:
        print(f"Error procesando mensaje: {e}")

client = mqtt.Client(CLIENT_ID)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()