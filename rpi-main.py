import network
import socket
import time
import _thread
import machine
from machine import Pin, PWM

# ===== CONFIGURACIÓN INICIAL =====
# credenciales de red
ssid = 'xxxx'
password = 'xxxx'

# pines principales
led = Pin(16, Pin.OUT)        # led externo de indicación
ledpico = Pin("LED", Pin.OUT) # led integrado del pico
boton = Pin(15, Pin.IN, Pin.PULL_DOWN)  # pull down para evitar lecturas flotantes

# buzzer por PWM para retroalimentación auditiva
buzzer = PWM(Pin(17))
buzzer.freq(500)

# pines del shift register
shift_data  = Pin(18, Pin.OUT)
shift_clock = Pin(19, Pin.OUT)

# leds de fila, conectados directamente a GPIO
led_row1 = Pin(14, Pin.OUT)  # fila superior: A C E G I K M O Q S U W Y
led_row2 = Pin(13, Pin.OUT)  # fila media:    B D F H J L N P R T V X Z
led_row3 = Pin(12, Pin.OUT)  # fila inferior: 0-9, +, -

# unidad de tiempo en ms, define la duración mínima de un punto
unidad = 200
morse_actual = ""  # almacena la secuencia de puntos y rayas en curso
ultimo_press = 0   # marca de tiempo del último evento del botón

# ===== TABLAS DE MORSE =====
# conversión de carácter a código morse
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
# tabla inversa para decodificación
MORSE_A_LETRA = {v: k for k, v in LETRA_A_MORSE.items()}

# ===== MAPEO DE COLUMNAS =====
# cada columna del tablero corresponde a dos letras o un número
# letras comparten columna por fila (A/B en col 0, C/D en col 1, etc.)
# números reutilizan las mismas columnas pero con la fila 3 activa
CHAR_TO_BIT = {
    'A': 0,  'B': 0,   # LED1
    'C': 1,  'D': 1,   # LED2
    'E': 2,  'F': 2,   # LED3
    'G': 3,  'H': 3,   # LED4
    'I': 4,  'J': 4,   # LED5
    'K': 5,  'L': 5,   # LED6
    'M': 6,  'N': 6,   # LED7
    'O': 7,  'P': 7,   # LED8
    'Q': 8,  'R': 8,   # LED9
    'S': 9,  'T': 9,   # LED10
    'U': 10, 'V': 10,  # LED11
    'W': 11, 'X': 11,  # LED12
    'Y': 12, 'Z': 12,  # LED13
    '0': 0,  '1': 1,
    '2': 2,  '3': 3,
    '4': 4,  '5': 5,
    '6': 6,  '7': 7,
    '8': 8,  '9': 9,
    '-': 10, '+': 11,
}

# conjuntos para determinar la fila de cada carácter
ODD_LETTERS  = set('ACEGIKMOQSUWY')  # fila superior
EVEN_LETTERS = set('BDFHJLNPRTVXZ')  # fila media
NUMBERS      = set('0123456789+-')   # fila inferior


# ===== SHIFT REGISTER =====

def shift_out_16(val16):
    # envía 16 bits a los dos 74HC164 encadenados
    # se transmite el bit más significativo primero
    for i in range(15, -1, -1):
        shift_data.value((val16 >> i) & 1)
        shift_clock.value(1)
        shift_clock.value(0)

def clear_leds():
    # apaga todos los LEDs del tablero y los de fila
    shift_out_16(0)
    led_row1.off()
    led_row2.off()
    led_row3.off()

def iluminar_letra(letra):
    # enciende la columna y fila correspondiente al carácter recibido
    letra = letra.upper()
    if letra not in CHAR_TO_BIT:
        clear_leds()
        return

    shift_out_16(1 << CHAR_TO_BIT[letra])

    # activa únicamente la fila que corresponde
    led_row1.value(letra in ODD_LETTERS)
    led_row2.value(letra in EVEN_LETTERS)
    led_row3.value(letra in NUMBERS)


# ===== CONEXIÓN WiFi =====

def conectar_wifi():
    # intenta conectarse a la red, el led parpadea mientras espera
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        ledpico.toggle()
        time.sleep(1)
    ledpico.on()  # led prendido indica conexión exitosa
    print('Listo! IP:', wlan.ifconfig()[0])


# ===== SERVIDOR HTTP =====

def iniciar_servidor():
    global morse_actual, ultimo_press, unidad

    # socket en el puerto 80, atiende comandos desde la interfaz de tkinter
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

            elif 'GET_MORSE' in request:
                # solo entrega el morse si pasaron al menos 2 segundos desde el último toque
                # de lo contrario devuelve vacío para que el cliente vuelva a consultar
                if time.ticks_diff(time.ticks_ms(), ultimo_press) >= 2000 and morse_actual != "":
                    conn.send('HTTP/1.1 200 OK\n\n' + morse_actual)
                    morse_actual = ""
                    clear_leds()
                else:
                    conn.send('HTTP/1.1 200 OK\n\n')
                conn.close()

            elif 'SET_UNIDAD' in request:
                # recibe el nuevo valor de unidad, formato: SET_UNIDAD_200
                valor = request.split('SET_UNIDAD_')[1].split(' ')[0]
                unidad = int(valor)
                conn.send('HTTP/1.1 200 OK\n\nOK')
                conn.close()

            else:
                conn.send('HTTP/1.1 200 OK\n\nOK')
                conn.close()

        except:
            pass  # cualquier error de conexión se ignora y se continúa


# ===== LÓGICA DEL BOTÓN MORSE =====

def botonmorse():
    global morse_actual, ultimo_press

    if boton.value() == 1:
        # mide el tiempo que el botón permanece presionado
        inicio = time.ticks_ms()
        led.value(1)
        buzzer.duty_u16(12000)

        while boton.value() == 1:
            time.sleep(0.02)

        duracion = time.ticks_diff(time.ticks_ms(), inicio)
        led.value(0)
        buzzer.duty_u16(0)
        ultimo_press = time.ticks_ms()

        # pulso corto = punto, pulso largo = raya
        if duracion <= unidad:
            morse_actual += "."
            buzzer.freq(800)   # tono agudo para punto
        elif duracion >= unidad * 2.5:
            morse_actual += "-"
            buzzer.freq(400)   # tono grave para raya

        # sonido de confirmación breve
        buzzer.duty_u16(8000)
        time.sleep(0.05)
        buzzer.duty_u16(0)

    else:
        # mientras no hay pulsación, se mide la pausa para detectar separadores
        if morse_actual and not morse_actual.endswith("/") and not morse_actual.endswith(" "):
            pausa = time.ticks_diff(time.ticks_ms(), ultimo_press)

            if pausa >= unidad * 7:
                # pausa larga: separador de palabra
                partes = [p for p in morse_actual.split(" ") if p]
                if partes and partes[-1] in MORSE_A_LETRA:
                    iluminar_letra(MORSE_A_LETRA[partes[-1]])
                morse_actual += " / "
                print(morse_actual)

            elif pausa >= unidad * 3:
                # pausa media: separador de letra, se decodifica y se ilumina
                partes = [p for p in morse_actual.split(" ") if p]
                if partes and partes[-1] in MORSE_A_LETRA:
                    iluminar_letra(MORSE_A_LETRA[partes[-1]])
                morse_actual += " "
                print(morse_actual)

    time.sleep(0.05)


def control_fisico():
    # hilo dedicado al botón, corre en paralelo con el servidor
    while True:
        botonmorse()


# ===== INICIO =====
clear_leds()
# prueba de leds antes de todo
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