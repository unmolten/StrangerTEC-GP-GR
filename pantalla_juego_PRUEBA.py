import tkinter as tk
import time



# Traduce letras, números y signos a código morse
LETRA_A_MORSE = {
    'A': '·—',   'B': '—···', 'C': '—·—·', 'D': '—··',  'E': '·',
    'F': '··—·', 'G': '——·',  'H': '····', 'I': '··',   'J': '·———',
    'K': '—·—',  'L': '·—··', 'M': '——',   'N': '—·',   'O': '———',
    'P': '·——·', 'Q': '——·—', 'R': '·—·',  'S': '···',  'T': '—',
    'U': '··—',  'V': '···—', 'W': '·——',  'X': '—··—', 'Y': '—·——',
    'Z': '——··',
    '1': '·————', '2': '··———', '3': '···——', '4': '····—', '5': '·····',
    '6': '—····', '7': '——···', '8': '———··', '9': '————·', '0': '—————',
    '+': '·—·—·', '-': '—····—', ' ': '/'
}

# Traduce código morse a letras
MORSE_A_LETRA = {v: k for k, v in LETRA_A_MORSE.items()}

# Unidad de tiempo base en segundos
# Se puede cambiar según la configuración del juego
UNIDAD = 0.2

# Umbrales de tiempo basados en la unidad
# Presión menor a 2 unidades = punto, mayor o igual = raya
UMBRAL_PUNTO_RAYA  = UNIDAD * 2 
UMBRAL_FIN_LETRA   = UNIDAD * 5 
UMBRAL_FIN_PALABRA = UNIDAD * 6   
UMBRAL_FIN_TOTAL   = UNIDAD * 10  


# Crea y muestra la pantalla de juego recibiendo la frase y los nombres de los jugadores
def abrir_pantalla_juego(ventana_padre, frase, nombre_j1, nombre_j2):
    ventana_juego = tk.Toplevel(ventana_padre)
    ventana_juego.title("StrangerTEC - Juego")
    ventana_juego.resizable(False, False)


    # Guarda el momento en que se presionó la tecla espacio
    tiempo_press = {"valor": None}

    # Guarda el momento en que se soltó la tecla espacio
    tiempo_release = {"valor": None}

    # Acumula los símbolos morse del caracter que se está ingresando
    simbolos_actuales = {"valor": ""}

    # Acumula los caracteres ya decodificados de la transmisión completa
    texto_decodificado = {"valor": ""}

    # Guarda el id del temporizador de silencio para cancelarlo si es necesario
    timer_silencio = {"id": None}

    # Indica si el turno ya terminó para no seguir procesando entradas
    turno_terminado = {"valor": False}


    tk.Label(ventana_juego, text="StrangerTEC", font=("Arial", 16, "bold")).pack(pady=(15, 0))
    tk.Label(ventana_juego, text="Turno: " + nombre_j1, font=("Arial", 11)).pack()

    tk.Label(ventana_juego, text="─" * 45, fg="gray").pack(pady=5)


    tk.Label(ventana_juego, text="Frase a transmitir:", font=("Arial", 10, "bold")).pack()

    # Muestra la frase que el jugador debe transmitir en morse
    label_frase = tk.Label(ventana_juego, text=frase, font=("Courier", 18, "bold"), fg="#cc0000")
    label_frase.pack(pady=5)

    tk.Label(ventana_juego, text="─" * 45, fg="gray").pack(pady=5)


    tk.Label(
        ventana_juego,
        text="ESPACIO: presión corta = ·   presión larga = —\n"
             "Suelta para separar símbolos · fin de letra · fin de palabra",
        font=("Arial", 9), fg="gray", justify="center"
    ).pack(pady=5)


    # Muestra qué está haciendo el jugador en este momento (presionando, esperando...)
    label_estado = tk.Label(ventana_juego, text="Listo. Presioná ESPACIO para transmitir.", font=("Arial", 10), fg="blue")
    label_estado.pack(pady=5)


    tk.Label(ventana_juego, text="─" * 45, fg="gray").pack(pady=5)
    tk.Label(ventana_juego, text="Resultado:", font=("Arial", 10, "bold")).pack()

    # Muestra el texto decodificado solo cuando el turno termina
    label_resultado = tk.Label(ventana_juego, text="—", font=("Courier", 14), fg="black")
    label_resultado.pack(pady=3)

    # Muestra el puntaje obtenido al final del turno
    label_puntaje = tk.Label(ventana_juego, text="Puntaje: —", font=("Arial", 12, "bold"), fg="green")
    label_puntaje.pack(pady=5)

    # ── Lógica morse ───────────────────────

    # Cancela el temporizador de silencio si hay uno activo
    def cancelar_timer():
        if timer_silencio["id"] is not None:
            ventana_juego.after_cancel(timer_silencio["id"])
            timer_silencio["id"] = None

    # Decodifica el morse acumulado en simbolos_actuales y lo agrega al texto
    def confirmar_letra():
        codigo = simbolos_actuales["valor"]
        if codigo == "":
            return
        # Busca el código en el diccionario, si no existe pone ?
        letra = MORSE_A_LETRA.get(codigo, "?")
        texto_decodificado["valor"] += letra
        simbolos_actuales["valor"] = ""
        label_estado.config(text=f"Letra confirmada: {letra}")

    # Agrega un espacio al texto decodificado para separar palabras
    def confirmar_palabra():
        confirmar_letra()
        texto_decodificado["valor"] += " "
        label_estado.config(text="Espacio entre palabras.")

    # Termina el turno, muestra el resultado y calcula el puntaje
    def terminar_turno():
        if turno_terminado["valor"]:
            return
        turno_terminado["valor"] = True
        cancelar_timer()

        # Confirma cualquier letra pendiente antes de terminar
        confirmar_letra()

        resultado = texto_decodificado["valor"].strip()
        label_resultado.config(text=resultado if resultado else "(vacío)")

        # Calcula el puntaje comparando caracter por caracter con la frase original
        puntaje = calcular_puntaje(frase, resultado)
        label_puntaje.config(text=f"Puntaje: {puntaje} / {len(frase.replace(' ', ''))}")
        label_estado.config(text="Turno terminado.", fg="gray")

        # Habilita el botón de continuar
        btn_terminar.config(state=tk.DISABLED)
        btn_continuar.config(state=tk.NORMAL)

    # Programa un temporizador de silencio para detectar fin de letra, palabra o turno
    def iniciar_timer_silencio():
        cancelar_timer()

        # Revisa el silencio transcurrido y decide qué confirmar
        def revisar_silencio():
            if turno_terminado["valor"]:
                return
            if tiempo_release["valor"] is None:
                return
            silencio = time.time() - tiempo_release["valor"]

            if silencio >= UMBRAL_FIN_TOTAL:
                terminar_turno()
            elif silencio >= UMBRAL_FIN_PALABRA:
                confirmar_palabra()
                timer_silencio["id"] = ventana_juego.after(200, revisar_silencio)
            elif silencio >= UMBRAL_FIN_LETRA:
                confirmar_letra()
                timer_silencio["id"] = ventana_juego.after(200, revisar_silencio)
            else:
                timer_silencio["id"] = ventana_juego.after(100, revisar_silencio)

        timer_silencio["id"] = ventana_juego.after(100, revisar_silencio)

    # Se llama cuando se presiona la tecla espacio
    def on_press(event):
        if turno_terminado["valor"]:
            return
        if tiempo_press["valor"] is not None:
            return
        cancelar_timer()
        tiempo_press["valor"] = time.time()
        label_estado.config(text="Presionando...", fg="orange")

    # Se llama cuando se suelta la tecla espacio
    def on_release(event):
        if turno_terminado["valor"]:
            return
        if tiempo_press["valor"] is None:
            return

        duracion = time.time() - tiempo_press["valor"]
        tiempo_press["valor"] = None
        tiempo_release["valor"] = time.time()

        # Decide si fue punto o raya según la duración de la presión
        if duracion < UMBRAL_PUNTO_RAYA:
            simbolos_actuales["valor"] += "·"
            label_estado.config(text="· (punto registrado)", fg="blue")
        else:
            simbolos_actuales["valor"] += "—"
            label_estado.config(text="— (raya registrada)", fg="blue")

        # Inicia el temporizador para detectar el fin de letra/palabra/turno
        iniciar_timer_silencio()

    # Vincula la tecla espacio a las funciones de presión y suelta
    ventana_juego.bind("<KeyPress-space>",   on_press)
    ventana_juego.bind("<KeyRelease-space>", on_release)


    frame_botones = tk.Frame(ventana_juego)
    frame_botones.pack(pady=15)

    # Botón para terminar el turno manualmente antes del silencio automático
    btn_terminar = tk.Button(
        frame_botones, text="Terminar turno",
        command=terminar_turno, width=15
    )
    btn_terminar.pack(side=tk.LEFT, padx=10)

    # Botón para continuar al siguiente turno, aparece al terminar
    btn_continuar = tk.Button(
        frame_botones, text="Continuar →",
        state=tk.DISABLED, width=15,
        command=lambda: print(f"Continuar al turno de {nombre_j2}")  # Por ahora solo imprime
    )
    btn_continuar.pack(side=tk.LEFT, padx=10)


# Compara el texto ingresado con la frase original caracter por caracter
# y devuelve la cantidad de caracteres correctos
def calcular_puntaje(frase_original, texto_ingresado):
    frase_limpia    = frase_original.replace(" ", "").upper()
    ingresado_limpio = texto_ingresado.replace(" ", "").upper()
    correctos = 0
    for i in range(min(len(frase_limpia), len(ingresado_limpio))):
        if frase_limpia[i] == ingresado_limpio[i]:
            correctos += 1
    return correctos

# PRUEBA

# Este bloque solo se ejecuta si corre este archivo directamente
if __name__ == "__main__":
    raiz = tk.Tk()
    raiz.title("Ventana raíz (prueba)")
    raiz.geometry("200x80")
    tk.Label(raiz, text="Ventana de prueba").pack(pady=10)

    # Abre la pantalla de juego con datos de prueba
    abrir_pantalla_juego(raiz, "SOS", "Gabriel", "Jugador 2")

    raiz.mainloop()