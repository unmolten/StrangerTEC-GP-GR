import network
import socket
import time
import _thread
import sys
import machine
from machine import Pin, PWM


# --- Pines y variables ---
ssid = 'x'
password = 'x'
led = Pin(16, Pin.OUT)
ledpico = Pin("LED", Pin.OUT)
boton = Pin(15, Pin.IN, Pin.PULL_DOWN)
buzzer = PWM(Pin(17))
buzzer.freq(500)
unidad = 200
morse_actual = ""
ultimo_press = 0


# --- Parte del WiFi y Servidor ---
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        ledpico.toggle()
        time.sleep(1)
    ledpico.off()
    print('Listo! IP:', wlan.ifconfig()[0])

def iniciar_servidor():
    global morse_actual
    global ultimo_press
    # Abrir el puerto para recibir las órdenes de la computadora
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80)) 
    s.listen(5)
    s.setblocking(True)
    
    while True:
        try:
            # Espera a que el programa de Tkinter diga algo
            conn, addr = s.accept()
            request = conn.recv(1024).decode('utf-8')
            
            # Revisa si la orden es prender o apagar
            if 'LED_ON' in request:
                led.value(1)
            elif 'LED_OFF' in request:
                led.value(0)
            elif 'SYS_OFF' in request:
                machine.reset()
            elif 'GET_MORSE' in request:
                # revisa el tiempo del codigo morse, y si pasan 3 segundos habilita el request que lo mande
                if time.ticks_diff(time.ticks_ms(), ultimo_press) >= 3000 and morse_actual != "":
                    conn.send('HTTP/1.1 200 OK\n\n' + morse_actual)
                    morse_actual = ""
                    conn.close()
                else:
                    conn.send('HTTP/1.1 200 OK\n\n')
                    conn.close()
        except:
            # Por si algo falla que no se detenga todo
            pass

# --- Parte física ---
# Corre por aparte (otro thread) para no chocar con el proceso del servidor

def control_fisico():
    while True:
        botonmorse()
        

def botonmorse():
    global morse_actual, ultimo_press

    # Revisar pausas antes de ver si se presionó
    if boton.value() == 1:
        inicio = time.ticks_ms()
        led.value(1)
        while boton.value() == 1:
            buzzer.duty_u16(12000)
            time.sleep(0.02) 
        duracion = time.ticks_diff(time.ticks_ms(), inicio)
        led.value(0)
        ultimo_press = time.ticks_ms()

        if duracion <= unidad:
            morse_actual += "."
            print(morse_actual)
        elif duracion >= unidad * 3:
            morse_actual += "-"
            print(morse_actual)
            
    buzzer.duty_u16(0)
    time.sleep(0.05)

# --- Aquí arranca el programa ---

# Mandar el todo lo fisico al otro core para que funcione al mismo tiempo
_thread.start_new_thread(control_fisico, ())

# Conectar y usar servidor 
conectar_wifi()
iniciar_servidor()
