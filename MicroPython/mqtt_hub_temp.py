from machine import Pin
from time import sleep
import dht
import network
import ussl
from umqtt.simple import MQTTClient
import json

DHTPIN = 17

sensor = dht.DHT11(Pin(DHTPIN))

SSID = "iPhone de Noe"
PASSWORD = "noephone"

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    print("Connexion au Wi-Fi")
    
    while not wlan.isconnected():
        print(".", end="")
        sleep(0.5)
    print("\nConnecté au Wi-Fi")
    print("Adresse IP :", wlan.ifconfig()[0])

# Configuration Azure IoT Hub avec le SAS Token existant
HOST_NAME = 'homepoc.azure-devices.net'
DEVICE_ID = 'Maison'
SAS_TOKEN = 'HostName=homepoc.azure-devices.net;DeviceId=Maison;SharedAccessKey=IwviSLzkyJNDwDtwm+7HJUvUvdnlgSf+cYQX3UnYFZ4='  # Votre SAS Token

# Configurer le client MQTT
MQTT_HOST = HOST_NAME
MQTT_PORT = 8883
MQTT_CLIENT_ID = DEVICE_ID
MQTT_USERNAME = HOST_NAME + '/' + DEVICE_ID + '/?api-version=2018-06-30'
MQTT_PASSWORD = SAS_TOKEN
MQTT_TOPIC = 'devices/{}/messages/events/'.format(DEVICE_ID)

def connect_mqtt():
    ssl_params = {'server_hostname': MQTT_HOST}
    client = MQTTClient(client_id=MQTT_CLIENT_ID,
                        server=MQTT_HOST,
                        port=MQTT_PORT,
                        user=MQTT_USERNAME,
                        password=MQTT_PASSWORD,
                        ssl=True,
                        ssl_params=ssl_params)
    client.connect()
    print("Connecté à Azure IoT Hub")
    return client

connect_wifi(SSID, PASSWORD)

mqtt_client = connect_mqtt()

while True:
    try:
        sensor.measure()
        temperature = sensor.temperature()
        humidity = sensor.humidity()
        
        message = json.dumps({
            "temperature": temperature,
            "humidity": humidity
        })
        
        mqtt_client.publish(MQTT_TOPIC, message)
        print("Message envoyé :", message)
        
        sleep(2)
    
    except OSError as e:
        print("Erreur de lecture du capteur :", e)
    except Exception as e:
        print("Erreur :", e)