# COMUNICACIONES INALAMBRICAS Y PROTOCOLOS PARA EL INTERNET DE LAS COSAS
# Jorge Machado Gallas | 2025/2026
# PRACTICA 1
_En esta primera práctica vamos a aprender a instalar nuestro propio bróker MQTT._
## Instalación Docker
Seguimos las instrucciones de la página oficial de Docker [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/):

Set up Docker's apt repository.
```
# Add Docker's official GPG key:
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
```
Install the Docker packages.
```
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
The Docker service starts automatically after installation. To verify that Docker is running, use:
```
sudo systemctl status docker
```

Some systems may have this behavior disabled and will require a manual start:
```
sudo systemctl start docker
```
Verify that the installation is successful by running the hello-world image:
```
sudo docker run hello-world
```
This command downloads a test image and runs it in a container. When the container runs, it prints a confirmation message and exits.

You have now successfully installed and started Docker Engine.
## Instalación contenedor Mosquitto
[Instalación de Mosquitto (MQTT Broker) en Docker](https://www.manelrodero.com/blog/instalacion-de-mosquitto-mqtt-broker-en-docker)

**Preparar carpetas de datos persistentes**

Crea las carpetas para persistencia (config, data, logs). Usa rutas adaptadas a tu sistema.​

```
mkdir -p ~/docker-volumes/mosquitto/{config,data,log}
cd ~/docker-volumes/mosquitto
```

Permisos correctos (importante para Docker):

```
sudo chown -R 1883:1883 config data log
sudo chmod -R 755 config data log
```
_UID/GID 1883 es el usuario mosquitto en la imagen oficial. Evita errores de escritura.​_

**Crear archivo de configuración**

En ~/docker-volumes/mosquitto/config/mosquitto.conf:
```
persistence true
persistence_location /mosquitto/data/

log_dest file /mosquitto/log/mosquitto.log

listener 1883
socket_domain ipv4

# Para pruebas: permite anónimas
allow_anonymous true
```

Guarda y aplica permisos: ```sudo chown 1883:1883 config/mosquitto.conf​```

**Archivo docker-compose.yml**

En ~/docker-volumes/mosquitto/docker-compose.yml:
```
services:
  mosquitto:
    image: eclipse-mosquitto:latest
    container_name: mosquitto
    environment:
      - TZ=Europe/Madrid  # Cambia a tu zona, ej. Europe/Madrid
    volumes:
      - ./config:/mosquitto/config
      - ./data:/mosquitto/data
      - ./log:/mosquitto/log
    ports:
      - 1883:1883  # MQTT
      - 9001:9001  # WebSockets (opcional)
    restart: unless-stopped
```
Nota: Rutas relativas desde la carpeta del compose para simplicidad.​

**Iniciar y verificar**

```
docker compose up -d
```
Ver logs:

```
tail -f log/mosquitto.log
```
Deberías ver:
```
mosquitto version 2.0.15 starting
Opening ipv4 listen socket on port 1883.
mosquitto version 2.0.15 running
```
**Probar MQTT**

Terminal 1 - Suscribir:
```
mosquitto_sub -h 192.168.1.135 -t /test/message
```
Terminal 2 - Publicar:
```
mosquitto_pub -h 192.168.1.135 -t /test/message -m 'Hello World!'
```
Recibes: ```/test/message Hello World!​```

## Diseño de la práctica

El tema de la práctica es "*Diseña e implementa un sistema de monitoreo y control de una planta utilizando el protocolo MQTT. Simula cuatro sensores que publiquen datos de temperatura, humedad, iluminación y pH a un servidor MQTT. Luego, utiliza dos clientes MQTT que actúen como actuadores para controlar la temperatura, la iluminación y la cantidad de nutrientes proporcionados a la planta. Los clientes deben estar suscritos a los mensajes publicados por los dispositivos.*"

Una arquitectura sencilla de temas podría ser:

+ Publicación de sensores:
    + planta/sensores/temperatura  
    + planta/sensores/humedad  
    + planta/sensores/iluminacion
    + planta/sensores/ph
+ Comandos hacia actuadores:
    + planta/actuadores/temperatura/cmd
    + planta/actuadores/iluminacion/cmd
    + planta/actuadores/nutrientes/cmd
+ Estados de actuadores:
    + planta/actuadores/temperatura/status
    + planta/actuadores/iluminacion/status
    + planta/actuadores/nutrientes/status

## Lógica de los sensores (4 clientes)

Cada sensor será un proceso/programa diferente (o al menos un cliente con distinto client_id) que:

+ Se conecta al broker MQTT.  
+ Cada X segundos publica un valor simulado.  
+ Usa un topic distinto según el tipo de sensor.

Ejemplo de comportamiento simulado:

+ Temperatura: valores alrededor de 24–28 °C con algo de ruido.  
+ Humedad: 40–70%.  
+ Iluminación: 0–1000 (lux simulados).  
+ pH: 5.5–7.5.  

Estructura de cada mensaje:

+ JSON: {"valor": 25.3, "unidad": "C"}


## Lógica de los actuadores (2 clientes)

Los actuadores son también clientes MQTT, pero:

Están suscritos a los topics que les interesan.  
Deciden qué hacer cuando reciben nuevos datos de sensores.  
Publican a los topics de comandos/estado si quieres cerrar el bucle.  

Actuador de temperatura:
Se suscribe al topic planta/sensores/temperatura.  
Define un umbral, por ejemplo:  
+ Temperatura objetivo 25 °C.  

Cuando recibe una medida:  
+ Si T>25T>25: “activar refrigeración” → publica "ON" en planta/actuadores/temperatura/cmd.  
+ Si T≤25T≤25: “desactivar refrigeración” → "OFF" en el mismo topic.  
+ También imprime por consola el estado o lo publica en planta/actuadores/temperatura/status.  

Actuador de iluminación y nutrientes:  
Se suscribe a:  
+ planta/sensores/iluminacion  
+ planta/sensores/ph  
+ humedad para decidir nutrientes.  

Reglas de ejemplo:  
+ Iluminación baja (p.ej. < 300): "ENCENDER_LUZ" en planta/actuadores/iluminacion/cmd.  
+ Iluminación alta (≥ 300): "APAGAR_LUZ".  
pH fuera de rango (p.ej. pH < 6.0 o > 7.0): "AÑADIR_NUTRIENTES" en planta/actuadores nutrientes/cmd.  
+ pH correcto: "NO_ACCION".  

De este modo estás “controlando la cantidad de nutrientes” de forma lógica, aunque sólo sea una simulación en software.

## Flujo completo del sistema

Un posible diagrama de flujo conceptual sería:
+ Cada sensor genera un valor simulado y lo publica en su topic.
+ El broker MQTT reenvía el mensaje a todos los clientes suscritos.
+ Actuador de temperatura:
    + Recibe la temperatura,
    + Aplica la regla,
    + Publica el comando de encender/apagar.
+ Actuador de iluminación/nutrientes:
    + Recibe iluminación y pH (y opcionalmente humedad),
    + Aplica sus reglas,
    + Publica comandos de luz y nutrientes.
+ Otro cliente “panel” se suscribe a todos los topics planta/# y muestra el estado global.

Esto cumple el requisito de que “los clientes deben estar suscritos a los mensajes publicados por los dispositivos” y de que existan sensores y actuadores conectados por MQTT.

## Simulacion de sensores/actuadores
Los vamos a programar en Python:
+ sensor_temperatura.py
+ sensor_humedad.py
+ sensor_iluminacion.py
+ sensor_ph.py
+ actuador_temperatura.py
+ actuador_iluminacion_nutrientes.py
+ monitor_planta.py como panel de visualización.

## Programas
Los programas en Python listos para usar con Mosquitto en 192.168.1.135:1883. Cada uno es independiente, instalar paho-mqtt
```
pip install paho-mqtt
```
### Sensores (4 programas)
**sensor_temperatura.py**
```python
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
    mensaje = json.dumps({"valor": temp, "unidad": "°C", "timestamp": time.time()})
    client.publish(TOPIC, mensaje, qos=1)
    print(f"Publicado temperatura: {temp}°C")
    time.sleep(INTERVALO)
```
**sensor_humedad.py**
```python
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
```
**sensor_iluminacion.py**
```python
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
```
**sensor_ph.py**
```python
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
```
### Actuadores (2 programas)
**actuador_temperatura.py**
```python
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
```
**actuador_iluminacion_nutrientes.py**
```python
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
```
