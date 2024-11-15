import machine
import time
from machine import I2C, Pin
import lcd_api  # Bibliothèque pour l'écran LCD
import i2c_lcd

I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)

lcd = i2c_lcd.I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

pir = machine.Pin(14, machine.Pin.IN)

compteur = 0

lcd.clear()
lcd.putstr("Nombre de personnes:\n0")

try:
    while True:
        if pir.value() == 1:
            compteur += 1
            print("Mouvement détecté ! Total:", compteur)
            lcd.clear()
            lcd.putstr("Nombre de personnes:\n{}".format(compteur))
            while pir.value() == 1:
                time.sleep(0.01)
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    lcd.clear()
