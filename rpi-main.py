import network
import socket
import time
import _thread
import machine
from machine import Pin, PWM

# ===== CONFIGURACIÓN INICIAL =====
ssid = 'A55'
password = 'goddamn1'

led = Pin(16, Pin.OUT)
ledpico = Pin("LED", Pin.OUT)
boton = Pin(15, Pin.IN, Pin.PULL_DOWN)

buzzer = PWM(Pin(17))
buzzer.freq(500)

shift_data  = Pin(18, Pin.OUT)
shift_clock = Pin(19, Pin.OUT)

led_row1 = Pin(14, Pin.OUT)  # fila superior: A C E G I K M O Q S U W Y
led_row2 = Pin(13, Pin.OUT)  # fila media:    B D F H J L N P R T V X Z
led_row3 = Pin(12, Pin.OUT)  # fila inferior: 0-9, +, -

unidad = 200
morse_actual = ""
ultimo_press = 0

# ===== TABLAS DE MORSE =====
LETRA_A_MORSE = {
    'A': '.-',   'B': '-...', 'C': '-.-.', 'D': '-..',  'E': '.',
    'F': '..-.', 'G': '--.',  'H': '....', 'I': '..',   'J': '.---',
    'K': '-.-',  'L': '.-..', 'M': '--',   'N': '-.',   'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.',  'S': '...',  'T': '-',
    'U': '..-',  'V': '...-', 'W': '.--',  'X': '-..-', 'Y': '-.--',
    'Z': '--..',
    '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
    '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----',
    '+': '.-.-.', '-': '-.-.-', ' ': '/'
}
MORSE_A_LETRA = {v: k for k, v in LETRA_A_MORSE.items()}

CHAR_TO_BIT = {
    'A': 0,  'B': 0,
    'C': 1,  'D': 1,
    'E': 2,  'F': 2,
    'G': 3,  'H': 3,
    'I': 4,  'J': 4,
    'K': 5,  'L': 5,
    'M': 6,  'N': 6,
    'O': 7,  'P': 7,
    'Q': 8,  'R': 8,
    'S': 9,  'T': 9,
    'U': 10, 'V': 10,
    'W': 11, 'X': 11,
    'Y': 12, 'Z': 12,
    '0': 0,  '1': 1,
    '2': 2,  '3': 3,
    '4': 4,  '5': 5,
    '6': 6,  '7': 7,
    '8': 8,  '9': 9,
    '-': 10, '+': 11,
}

ODD_LETTERS  = set('ACEGIKMOQSUWY')
EVEN_LETTERS = set('BDFHJLNPRTVXZ')
NUMBERS      = set('0123456789+-')


# ===== SHIFT REGISTER =====

def shift_out_16(val16):
    for i in range(15, -1, -1):
        shift_data.value((val16 >> i) & 1)
        shift_clock.value(1)
        shift_clock.value(0)

def clear_leds():
    shift_out_16(0)
    led_row1.off()
    led_row2.off()
    led_row3.off()

def iluminar_letra(letra):
    letra = letra.upper()
    if letra not in CHAR_TO_BIT:
        clear_leds()
        return
    shift_out_16(1 << CHAR_TO_BIT[letra])
    led_row1.value(letra in ODD_LETTERS)
    led_row2.value(letra in EVEN_LETTERS)
    led_row3.value(letra in NUMBERS)


# ===== REPRODUCCIÓN MORSE POR BUZZER =====

def beep_morse(texto):
    # reproduce la frase recibida en morse con el buzzer
    # ilumina cada letra en los LEDs mientras suena
    u = unidad / 1000  # unidad en segundos

    for char in texto.upper():
        if char == ' ':
            # pausa entre palabras
            time.sleep(u * 7)
            continue

        codigo = LETRA_A_MORSE.get(char, '')
        if not codigo:
            continue

        # ilumina la letra en el tablero mientras se reproduce
        iluminar_letra(char)

        for simbolo in codigo:
            if simbolo == '.':
                buzzer.freq(800)
                buzzer.duty_u16(8000)
                time.sleep(u)          # duración del punto
            elif simbolo == '-':
                buzzer.freq(400)
                buzzer.duty_u16(8000)
                time.sleep(u * 3)      # duración de la raya
            buzzer.duty_u16(0)
            time.sleep(u / 2)              # pausa entre símbolos

        clear_leds()
        time.sleep(u * 2)              # pausa extra entre letras (total 3u)


# ===== CONEXIÓN WiFi =====

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        ledpico.toggle()
        time.sleep(1)
    ledpico.on()
    print('Listo! IP:', wlan.ifconfig()[0])


# ===== SERVIDOR HTTP =====

def iniciar_servidor():
    global morse_actual, ultimo_press, unidad

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    s.setblocking(True)

    while True:
        try:
            conn, addr = s.accept()
            request = conn.recv(1024).decode('utf-8')

            if 'LED_ON' in request:
                led.value(1)

            elif 'LED_OFF' in request:
                led.value(0)

            elif 'SYS_OFF' in request:
                machine.reset()

            elif 'PLAY_FRASE' in request:
                # recibe la frase como PLAY_FRASE_HOLA o PLAY_FRASE_HOLA_MUNDO
                # los espacios vienen como guion bajo
                frase = request.split('PLAY_FRASE_')[1].split(' ')[0]
                frase = frase.replace('_', ' ')
                conn.send('HTTP/1.1 200 OK\n\nOK')
                conn.close()
                beep_morse(frase)  # reproduce después de cerrar la conexión

            elif 'GET_MORSE' in request:
                if time.ticks_diff(time.ticks_ms(), ultimo_press) >= 2000 and morse_actual != "":
                    conn.send('HTTP/1.1 200 OK\n\n' + morse_actual)
                    morse_actual = ""
                    clear_leds()
                else:
                    conn.send('HTTP/1.1 200 OK\n\n')
                conn.close()

            elif 'SET_UNIDAD' in request:
                valor = request.split('SET_UNIDAD_')[1].split(' ')[0]
                unidad = int(valor)
                conn.send('HTTP/1.1 200 OK\n\nOK')
                conn.close()

            else:
                conn.send('HTTP/1.1 200 OK\n\nOK')
                conn.close()

        except:
            pass


# ===== LÓGICA DEL BOTÓN MORSE =====

def botonmorse():
    global morse_actual, ultimo_press

    if boton.value() == 1:
        inicio = time.ticks_ms()
        led.value(1)
        buzzer.duty_u16(12000)

        while boton.value() == 1:
            time.sleep(0.02)

        duracion = time.ticks_diff(time.ticks_ms(), inicio)
        led.value(0)
        buzzer.duty_u16(0)
        ultimo_press = time.ticks_ms()

        if duracion <= unidad:
            morse_actual += "."
            buzzer.freq(800)
        elif duracion >= unidad * 2.5:
            morse_actual += "-"
            buzzer.freq(400)

        buzzer.duty_u16(8000)
        time.sleep(0.05)
        buzzer.duty_u16(0)

    else:
        if morse_actual and not morse_actual.endswith("/") and not morse_actual.endswith(" "):
            pausa = time.ticks_diff(time.ticks_ms(), ultimo_press)

            if pausa >= unidad * 7:
                partes = [p for p in morse_actual.split(" ") if p]
                if partes and partes[-1] in MORSE_A_LETRA:
                    iluminar_letra(MORSE_A_LETRA[partes[-1]])
                morse_actual += " / "
                print(morse_actual)

            elif pausa >= unidad * 3:
                partes = [p for p in morse_actual.split(" ") if p]
                if partes and partes[-1] in MORSE_A_LETRA:
                    iluminar_letra(MORSE_A_LETRA[partes[-1]])
                morse_actual += " "
                print(morse_actual)

    time.sleep(0.05)


def control_fisico():
    while True:
        botonmorse()


# ===== INICIO =====
clear_leds()
led_row1.on()
time.sleep(0.1)
led_row2.on()
time.sleep(0.1)
led_row3.on()
time.sleep(0.1)
clear_leds()
_thread.start_new_thread(control_fisico, ())
conectar_wifi()
iniciar_servidor()	