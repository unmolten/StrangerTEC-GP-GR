import tkinter as tk
import requests

# CONEXIÓN CON PICO W


# Guarda la IP de la Pico W, se asigna cuando el usuario la ingresa
PICO_IP = None

# Asigna la IP ingresada por el usuario a la variable global
def configurar_ip(ip):
    global PICO_IP
    PICO_IP = f"http://{ip}"

# Envía un comando HTTP a la Pico W, si no hay IP configurada lo indica
def send_command(command):
    if PICO_IP is None:
        print("IP no configurada.")
        return
    try:
        requests.get(f"{PICO_IP}/{command}", timeout=3)
    except Exception as e:
        print("Error de conexión:", e)

# ───────────────────────────────────────────
# VENTANA PRINCIPAL
# ───────────────────────────────────────────

# Crea la ventana principal y le da un título
ventana = tk.Tk()
ventana.title("StrangerTEC")

# Pone un título dentro de la ventana y lo centra
titulo = tk.Label(ventana, text="Bienvenido a StrangerTEC")
titulo.pack(pady=10)

#Sección de IP

# Crea un frame para agrupar la etiqueta y el campo de IP en la misma fila
frame_ip = tk.Frame(ventana)
frame_ip.pack(pady=5)

tk.Label(frame_ip, text="IP de la Pico W:").pack(side=tk.LEFT)

# Campo donde el usuario escribe la IP de la Pico W
entrada_ip = tk.Entry(frame_ip, width=20)
entrada_ip.pack(side=tk.LEFT, padx=5)

# Muestra si la conexión fue exitosa o si falta ingresar la IP
label_estado_ip = tk.Label(ventana, text="Estado: sin conectar", fg="gray")
label_estado_ip.pack()

# Lee la IP del campo de entrada y llama a configurar_ip para guardarla
def conectar():
    ip = entrada_ip.get().strip()
    if ip:
        configurar_ip(ip)
        label_estado_ip.config(text=f"Conectado a {ip}", fg="green")
    else:
        label_estado_ip.config(text="Ingresá una IP válida", fg="red")

tk.Button(ventana, text="Conectar", command=conectar).pack(pady=3)

#Jugadores

# Crea las etiquetas para mostrar los nombres de los jugadores
label_j1 = tk.Label(ventana, text="Jugador 1: (sin nombre)")
label_j1.pack()

label_j2 = tk.Label(ventana, text="Jugador 2: (sin nombre)")
label_j2.pack()

# Abre una nueva ventana para ingresar el nombre del jugador y lo guarda en la etiqueta correspondiente
def abrir_ventana(jugador):
    ventana_nombre = tk.Toplevel(ventana)
    ventana_nombre.title(f"Jugador {jugador}")

    tk.Label(ventana_nombre, text="Escribí tu nombre:").pack(pady=20)

    entrada = tk.Entry(ventana_nombre, width=25)
    entrada.pack(pady=5)

    # Guarda el nombre ingresado y lo muestra en la etiqueta correspondiente, luego cierra la ventana
    def guardar():
        nombre = entrada.get()
        if jugador == 1:
            label_j1.config(text=f"Jugador 1: {nombre}")
        else:
            label_j2.config(text=f"Jugador 2: {nombre}")
        ventana_nombre.destroy()

    tk.Button(ventana_nombre, text="Guardar", command=guardar).pack(pady=5)

# Crea los botones para agregar los jugadores y llama a la función para abrir la ventana de ingreso de nombre
tk.Button(ventana, text="Agregar Jugador 1", command=lambda: abrir_ventana(1)).pack(pady=5)
tk.Button(ventana, text="Agregar Jugador 2", command=lambda: abrir_ventana(2)).pack(pady=5)

#Modo de juego

# Variable que guarda el modo de juego seleccionado
modo_seleccionado = tk.StringVar(value="")

# Abre una ventana para que el usuario elija el modo de juego
def abrir_seleccion_modo():
    ventana_modo = tk.Toplevel(ventana)
    ventana_modo.title("Seleccionar Modo de Juego")

    tk.Label(ventana_modo, text="Elegí un modo de juego:").pack(pady=10)

    # Lista de modos disponibles:
    modos = ["Transmision simple", "Escucha y transmision"]
    for modo in modos:
        tk.Button(
            ventana_modo,
            text=modo,
            width=20,
            command=lambda m=modo: elegir_modo(m, ventana_modo)
        ).pack(pady=4)

# Guarda el modo elegido, lo muestra en la etiqueta y cierra la ventana de selección
def elegir_modo(modo, ventana_modo):
    modo_seleccionado.set(modo)
    label_modo.config(text=f"Modo: {modo}")
    ventana_modo.destroy()

tk.Button(ventana, text="Seleccionar Modo de Juego", command=abrir_seleccion_modo).pack(pady=5)

# Etiqueta que muestra el modo de juego actualmente seleccionado
label_modo = tk.Label(ventana, text="Modo: (sin seleccionar)")
label_modo.pack()

# Iniciar juego 

# Valida que ambos jugadores tengan nombre y que haya un modo seleccionado,
# luego envía la señal de inicio a la Pico W y llama a la pantalla de juego
from config import abrir_pantalla_config
def iniciar_juego():
    nombre_j1 = label_j1.cget("text")
    nombre_j2 = label_j2.cget("text")

    # Verifica que ambos jugadores hayan ingresado su nombre
    if "(sin nombre)" in nombre_j1 or "(sin nombre)" in nombre_j2:
        label_estado_ip.config(text="Ambos jugadores deben tener nombre", fg="red")
        return

    # Verifica que se haya seleccionado un modo de juego
    if modo_seleccionado.get() == "":
        label_estado_ip.config(text="Seleccioná un modo de juego", fg="red")
        return

    # Envía señal a la Pico W indicando que el juego comenzó
    send_command("LED_ON")
    def recibir_frase(frase):
        print(f"Frase elegida: {frase}")  # Aquí después va pantalla_mapa
    abrir_pantalla_config(ventana, recibir_frase)

tk.Button(ventana, text="Iniciar Juego", command=iniciar_juego).pack(pady=20)

#Controles LED manuales

# Botones para encender y apagar el LED de la Pico W manualmente
frame_led = tk.Frame(ventana)
frame_led.pack(pady=10)

tk.Button(frame_led, text="LED ON",  command=lambda: send_command("LED_ON")).pack(side=tk.LEFT, padx=5)
tk.Button(frame_led, text="LED OFF", command=lambda: send_command("LED_OFF")).pack(side=tk.LEFT, padx=5)

ventana.mainloop()