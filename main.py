import time
from machine import Pin, PWM

# Se asignan los pines con variables
led = Pin(16, Pin.OUT)
buzzer = PWM(Pin(18))
buzzer.freq(500) # Se le pone una frecuencia al buzzer para su tono.
button = Pin(17, Pin.IN,Pin.PULL_DOWN)

# Aqui se corre el codigo continuamente
# Se prenden el led y el buzzer al detectar corriente del boton, y se apagan si no
while True:
    if button.value() == 1:
        print("Boton presionado")
        led.value(1)
        buzzer.duty_u16(10000) # Esto actua como un control de volumen para el buzzer
    else:
        buzzer.duty_u16(0)
        led.value(0)
        print("Boton no presionado.")
    time.sleep(0.1)
    
