import tkinter as tk
import requests
import random
import time

# ───────────────────────────────────────────
# PICO W
# ───────────────────────────────────────────

PICO_IP = None

def send_command(command):
    if PICO_IP is None:
        return None
    try:
        r = requests.get(f"{PICO_IP}/{command}", timeout=3)
        return r.text
    except:
        return None

# ───────────────────────────────────────────
# MORSE
# ───────────────────────────────────────────

FRASES = ["SOS", "SI", "NO", "HOLA", "AYUDA", "FUEGO", "AGUA", "LISTO", "VAMOS", "PARE"]

MORSE = {
    'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---',
    'K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-',
    'U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..', '1':'.----','2':'..---','3':'...--','4':'....-','5':'.....',
    '6':'-....','7':'--...','8':'---..','9':'----.','0':'-----','+':'.-.-.','-':'-...-',
}
MORSE_INV = {v: k for k, v in MORSE.items()}

def decodificar_morse(cadena):
    resultado = ""
    for palabra in cadena.strip().split(" "):
        for codigo in palabra.split("/"):
            if codigo:
                resultado += MORSE_INV.get(codigo, "?")
        resultado += " "
    return resultado.strip()

def calcular_puntaje(frase, resultado):
    frase     = frase.replace(" ", "").upper()
    resultado = resultado.replace(" ", "").upper()
    return sum(1 for a, b in zip(frase, resultado) if a == b)

# ───────────────────────────────────────────
# PANTALLA INICIO
# ───────────────────────────────────────────

nombres = ["", ""]
UNIDAD  = 0.2  # se cambia según selección del usuario

def pantalla_inicio():
    global UNIDAD

    ventana = tk.Tk()
    ventana.title("StrangerTEC")
    ventana.resizable(False, False)

    tk.Label(ventana, text="StrangerTEC", font=("Courier", 20, "bold")).pack(pady=(20, 5))
    tk.Label(ventana, text="─" * 38, fg="gray").pack(pady=5)

    # IP
    frame_ip = tk.Frame(ventana)
    frame_ip.pack(pady=5)
    tk.Label(frame_ip, text="IP de la Pico W:").pack(side=tk.LEFT)
    entrada_ip = tk.Entry(frame_ip, width=18)
    entrada_ip.pack(side=tk.LEFT, padx=5)

    label_estado = tk.Label(ventana, text="Sin conectar", fg="gray")
    label_estado.pack()

    def conectar():
        global PICO_IP
        ip = entrada_ip.get().strip()
        if ip:
            PICO_IP = f"http://{ip}"
            label_estado.config(text=f"Conectado a {ip}", fg="green")
        else:
            label_estado.config(text="Ingresá una IP válida", fg="red")

    tk.Button(ventana, text="Conectar", command=conectar).pack(pady=3)
    tk.Label(ventana, text="─" * 38, fg="gray").pack(pady=5)

    # Nombres
    label_j1 = tk.Label(ventana, text="Jugador 1: (sin nombre)")
    label_j1.pack()
    label_j2 = tk.Label(ventana, text="Jugador 2: (sin nombre)")
    label_j2.pack()

    def pedir_nombre(jugador):
        win = tk.Toplevel(ventana)
        win.grab_set()
        tk.Label(win, text="Nombre:").pack(pady=10)
        entrada = tk.Entry(win, width=20)
        entrada.pack(pady=5)
        def guardar():
            n = entrada.get().strip()
            if not n:
                return
            nombres[jugador - 1] = n
            if jugador == 1:
                label_j1.config(text=f"Jugador 1: {n}")
            else:
                label_j2.config(text=f"Jugador 2: {n}")
            win.destroy()
        tk.Button(win, text="Guardar", command=guardar).pack(pady=5)

    tk.Button(ventana, text="Jugador 1", command=lambda: pedir_nombre(1)).pack(pady=3)
    tk.Button(ventana, text="Jugador 2", command=lambda: pedir_nombre(2)).pack(pady=3)
    tk.Label(ventana, text="─" * 38, fg="gray").pack(pady=5)

    # Selección de unidad
    tk.Label(ventana, text="Velocidad (unidad de tiempo):", font=("Courier", 9)).pack()
    unidad_var = tk.StringVar(value="A")
    frame_unidad = tk.Frame(ventana)
    frame_unidad.pack()
    tk.Radiobutton(frame_unidad, text="A (0.2s)", variable=unidad_var, value="A").pack(side=tk.LEFT, padx=8)
    tk.Radiobutton(frame_unidad, text="B (0.3s)", variable=unidad_var, value="B").pack(side=tk.LEFT, padx=8)
    tk.Radiobutton(frame_unidad, text="C (0.5s)", variable=unidad_var, value="C").pack(side=tk.LEFT, padx=8)

    tk.Label(ventana, text="─" * 38, fg="gray").pack(pady=5)

    def iniciar():
        global UNIDAD
        if not nombres[0] or not nombres[1]:
            label_estado.config(text="Faltan nombres", fg="red")
            return
        UNIDAD = {"A": 0.2, "B": 0.3, "C": 0.5}[unidad_var.get()]
        # manda la unidad al Pico en milisegundos
        send_command(f"SET_UNIDAD_{int(UNIDAD * 1000)}")
        ventana.destroy()
        pantalla_juego(random.choice(FRASES))

    tk.Button(ventana, text="Iniciar Juego", font=("Courier", 11, "bold"), command=iniciar).pack(pady=15)
    ventana.mainloop()

# ───────────────────────────────────────────
# PANTALLA DE JUEGO
# ───────────────────────────────────────────

def pantalla_juego(frase):
    # Umbrales según estándar morse:
    # punto < 2u, raya >= 2u
    # separación entre símbolos: 1u (no medimos esto, solo entre letras)
    # separación entre letras: 3u
    # separación entre palabras: 7u
    UMBRAL_PUNTO_RAYA  = UNIDAD * 2
    UMBRAL_FIN_LETRA   = UNIDAD * 3
    UMBRAL_FIN_PALABRA = UNIDAD * 7

    ventana = tk.Tk()
    ventana.title("StrangerTEC - Juego")
    ventana.resizable(False, False)

    tk.Label(ventana, text="Transmití esta frase en morse:", font=("Courier", 11)).pack(pady=(15, 2))
    tk.Label(ventana, text=frase, font=("Courier", 24, "bold"), fg="#cc0000").pack()

    tk.Label(ventana, text="─" * 45, fg="gray").pack(pady=6)

    # Teclado
    tk.Label(ventana, text=f"{nombres[1]} — teclado (ESPACIO)", font=("Courier", 10, "bold")).pack()
    label_simbolos      = tk.Label(ventana, text="", font=("Courier", 12), fg="orange")
    label_simbolos.pack()
    label_resultado_kb  = tk.Label(ventana, text="", font=("Courier", 16, "bold"))
    label_resultado_kb.pack()

    tk.Label(ventana, text="─" * 45, fg="gray").pack(pady=6)

    # Pico
    tk.Label(ventana, text=f"{nombres[0]} — Pico W (botón físico)", font=("Courier", 10, "bold")).pack()
    label_resultado_pico = tk.Label(ventana, text="", font=("Courier", 16, "bold"))
    label_resultado_pico.pack()

    tk.Label(ventana, text="─" * 45, fg="gray").pack(pady=6)

    label_puntajes = tk.Label(ventana, text="", font=("Courier", 12, "bold"), fg="green")
    label_puntajes.pack()

    # ── Lógica teclado ──
    tiempo_press   = {"v": None}
    tiempo_release = {"v": None}
    simbolos       = {"v": ""}
    texto_kb       = {"v": ""}
    timer_id       = {"v": None}
    terminado      = {"v": False}

    def cancelar_timer():
        if timer_id["v"]:
            ventana.after_cancel(timer_id["v"])
            timer_id["v"] = None

    def confirmar_letra():
        cod = simbolos["v"]
        if not cod:
            return
        letra = MORSE_INV.get(cod, "?")
        texto_kb["v"] += letra
        simbolos["v"] = ""
        label_resultado_kb.config(text=texto_kb["v"])
        label_simbolos.config(text="")

    def confirmar_palabra():
        confirmar_letra()
        if not texto_kb["v"].endswith(" "):
            texto_kb["v"] += " " 
        label_resultado_kb.config(text=texto_kb["v"])

    def revisar_silencio():
        if terminado["v"] or tiempo_release["v"] is None:
            return
        silencio = time.time() - tiempo_release["v"]
        if silencio >= UMBRAL_FIN_PALABRA:
            confirmar_palabra()
        elif silencio >= UMBRAL_FIN_LETRA:
            confirmar_letra()
        timer_id["v"] = ventana.after(50, revisar_silencio)

    def on_press(event):
        if terminado["v"] or tiempo_press["v"] is not None:
            return
        cancelar_timer()
        tiempo_press["v"] = time.time()

    def on_release(event):
        if terminado["v"] or tiempo_press["v"] is None:
            return
        duracion = time.time() - tiempo_press["v"]
        tiempo_press["v"] = None
        tiempo_release["v"] = time.time()
        if duracion < UMBRAL_PUNTO_RAYA:
            simbolos["v"] += "."
        else:
            simbolos["v"] += "-"
        label_simbolos.config(text=simbolos["v"])
        cancelar_timer()
        timer_id["v"] = ventana.after(50, revisar_silencio)

    ventana.bind("<KeyPress-space>",   on_press)
    ventana.bind("<KeyRelease-space>", on_release)

    # ── Poll Pico ──
    ultimo_morse = {"v": ""}

    def poll_pico():
        if not terminado["v"]:
            morse = send_command("GET_MORSE")
            if morse and morse.strip():
                ultimo_morse["v"] = morse.strip()
                label_resultado_pico.config(text=decodificar_morse(morse.strip()).upper())
            ventana.after(2000, poll_pico)

    ventana.after(2000, poll_pico)

    # ── Terminar ──
    def terminar():
        if terminado["v"]:
            return
        terminado["v"] = True
        cancelar_timer()
        confirmar_letra()

        res_kb   = texto_kb["v"].strip().upper()
        res_pico = decodificar_morse(ultimo_morse["v"]).upper() if ultimo_morse["v"] else ""

        p1 = calcular_puntaje(frase, res_pico)
        p2 = calcular_puntaje(frase, res_kb)
        label_puntajes.config(text=f"{nombres[0]}: {p1} pts     {nombres[1]}: {p2} pts")

        btn_terminar.config(state=tk.DISABLED)
        btn_nuevo.config(state=tk.NORMAL)

    frame_btn = tk.Frame(ventana)
    frame_btn.pack(pady=10)

    btn_terminar = tk.Button(frame_btn, text="Terminar", command=terminar, width=12)
    btn_terminar.pack(side=tk.LEFT, padx=8)

    btn_nuevo = tk.Button(frame_btn, text="Jugar de nuevo", state=tk.DISABLED, width=14,
                          command=lambda: [ventana.destroy(), pantalla_juego(random.choice(FRASES))])
    btn_nuevo.pack(side=tk.LEFT, padx=8)

    ventana.mainloop()

# ───────────────────────────────────────────
pantalla_inicio()
