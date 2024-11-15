import machine
import time

# Définition des fréquences des notes
notes = {
    'C4': 262,
    'CS4': 277,
    'D4': 294,
    'DS4': 311,
    'E4': 330,
    'F4': 349,
    'FS4': 370,
    'G4': 392,
    'GS4': 415,
    'A4': 440,
    'AS4': 466,
    'B4': 494,
    'C5': 523,
    'CS5': 554,
    'D5': 587,
    'DS5': 622,
    'E5': 659,
    'F5': 698,
    'FS5': 740,
    'G5': 784,
    'GS5': 831,
    'A5': 880,
}

# Mélodie de Star Wars (simplifiée)
melodie = [
    'A4', 'A4', 'A4', 'F4', 'C5', 'A4', 'F4', 'C5', 'A4',
    'E5', 'E5', 'E5', 'F5', 'C5', 'GS4', 'F4', 'C5', 'A4'
]

# Durées des notes (en ms)
durees = [
    500, 500, 500, 350, 150, 500, 350, 150, 650,
    500, 500, 500, 350, 150, 500, 350, 150, 650
]

# Configuration du buzzer sur le pin 25
buzzer = machine.PWM(machine.Pin(25), freq=440, duty=0)

# Configuration du capteur PIR sur le pin 14
pir = machine.Pin(14, machine.Pin.IN)

def jouer_melodie():
    for i in range(len(melodie)):
        note = melodie[i]
        duree = durees[i]
        if note == 'P':
            # Silence
            buzzer.duty(0)
        else:
            buzzer.freq(notes[note])
            buzzer.duty(512)  # Volume moyen
        time.sleep_ms(duree)
        buzzer.duty(0)
        time.sleep_ms(50)  # Pause entre les notes

try:
    while True:
        if pir.value() == 1:
            print("Mouvement détecté !")
            jouer_melodie()
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    buzzer.deinit()
