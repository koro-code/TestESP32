from machine import Pin, I2C
from time import sleep
import dht
import network
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

# Configuration des pins
DHTPIN = 17
BTN1 = 16
BTN2 = 27

# Configuration de l'écran LCD (adresse I2C 0x27, 16 colonnes, 2 lignes)
I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

# Initialisation du capteur DHT
sensor = dht.DHT11(Pin(DHTPIN))

# Initialisation de l'I2C et de l'écran LCD
i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

# Connexion Wi-Fi
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
    print("Adresse IP:", wlan.ifconfig()[0])

# Exécuter la connexion Wi-Fi au démarrage
connect_wifi(SSID, PASSWORD)

# Boucle principale
while True:
    try:
        # Lecture des données du capteur
        sensor.measure()
        temperature = sensor.temperature()
        humidity = sensor.humidity()
        
        # Affichage des données sur l'écran LCD
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("T = {:.1f} C".format(temperature))
        lcd.move_to(0, 1)
        lcd.putstr("H = {:.1f} %".format(humidity))
        
        # Pause de 2 secondes avant la prochaine lecture
        sleep(2)

    except OSError as e:
        print("Erreur de lecture du capteur:", e)
