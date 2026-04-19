import tkinter as tk
import random


# LISTA DE FRASES


# Lista de frases disponibles para el juego, máximo 16 caracteres cada una
# Las mínimas requeridas por el proyecto son SOS, SI, NO
frases = [
    "SOS",
    "SI",
    "NO",
    "HOLA MUNDO",
    "STRANGER TEC",
    "HOLA PROFE",
    "ATP",
    "COMPUTADORES",
    "INGENIERÍA",
    "PYTHON",
]

# Selecciona una frase aleatoria de la lista y la devuelve
def obtener_frase_aleatoria():
    return random.choice(frases)


# VENTANA DE CONFIGURACIÓN


# Crea y muestra la pantalla de configuración de frases
def abrir_pantalla_config(ventana_padre, callback_iniciar):
    ventana_config = tk.Toplevel(ventana_padre)
    ventana_config.title("Configuración de Frases")
    ventana_config.resizable(False, False)

    tk.Label(ventana_config, text="Lista de Frases", font=("Arial", 13, "bold")).pack(pady=10)
    tk.Label(ventana_config, text="Máximo 10 frases · Máximo 16 caracteres cada una", fg="gray").pack()

    #Lista de frases

    # Frame que contiene la lista visual de frases actuales
    frame_lista = tk.Frame(ventana_config)
    frame_lista.pack(padx=20, pady=10)

    # Etiqueta de estado para mostrar errores o confirmaciones
    label_estado = tk.Label(ventana_config, text="", fg="red")
    label_estado.pack()

    # Dibuja la lista completa de frases con su botón de eliminar
    def actualizar_lista():
        # Limpia el frame antes de redibujar
        for widget in frame_lista.winfo_children():
            widget.destroy()

        tk.Label(frame_lista, text="Frases actuales:", anchor="w").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 5))

        for i, frase in enumerate(frases):
            # Número de frase
            tk.Label(frame_lista, text=f"{i+1}.", width=3, anchor="e").grid(row=i+1, column=0, padx=(0, 5))
            # Texto de la frase
            tk.Label(frame_lista, text=frase, width=20, anchor="w", font=("Courier", 10)).grid(row=i+1, column=1, padx=5)
            # Botón para eliminar esa frase de la lista
            tk.Button(
                frame_lista, text="✕", fg="red", width=2,
                command=lambda idx=i: eliminar_frase(idx)
            ).grid(row=i+1, column=2, padx=5, pady=1)

    # Agregar frase

    frame_agregar = tk.Frame(ventana_config)
    frame_agregar.pack(pady=5)

    tk.Label(frame_agregar, text="Nueva frase:").pack(side=tk.LEFT)

    # Campo donde el usuario escribe la nueva frase
    entrada_nueva = tk.Entry(frame_agregar, width=20)
    entrada_nueva.pack(side=tk.LEFT, padx=5)

    # Valida y agrega la nueva frase a la lista
    def agregar_frase():
        nueva = entrada_nueva.get().strip().upper()

        # Verifica que no esté vacía
        if nueva == "":
            label_estado.config(text="Escribí una frase antes de agregar.", fg="red")
            return

        # Verifica que no supere los 16 caracteres
        if len(nueva) > 16:
            label_estado.config(text=f"Máximo 16 caracteres. Esta tiene {len(nueva)}.", fg="red")
            return

        # Verifica que no se supere el límite de 10 frases
        if len(frases) >= 10:
            label_estado.config(text="Límite de 10 frases alcanzado.", fg="red")
            return

        # Verifica que la frase no esté duplicada
        if nueva in frases:
            label_estado.config(text="Esa frase ya está en la lista.", fg="orange")
            return

        frases.append(nueva)
        entrada_nueva.delete(0, tk.END)
        label_estado.config(text=f'"{nueva}" agregada.', fg="green")
        actualizar_lista()

    tk.Button(frame_agregar, text="Agregar", command=agregar_frase).pack(side=tk.LEFT)

    # Elimina la frase en la posición indicada y redibuja la lista
    def eliminar_frase(indice):
        frase_eliminada = frases.pop(indice)
        label_estado.config(text=f'"{frase_eliminada}" eliminada.', fg="gray")
        actualizar_lista()


    

    # Botón iniciar

    # Valida que haya frases, selecciona una al azar y llama al callback para iniciar el juego
    def confirmar_e_iniciar():
        if not frases:
            label_estado.config(text="Agregá al menos una frase para jugar.", fg="red")
            return
        frase_elegida = obtener_frase_aleatoria()
        ventana_config.destroy()
        # Llama a la función que recibe la frase y arranca el juego
        callback_iniciar(frase_elegida)

    tk.Button(
        ventana_config, text="Iniciar Juego con Frase Aleatoria",
        font=("Arial", 10, "bold"), bg="green", fg="white",
        command=confirmar_e_iniciar
    ).pack(pady=15)

    # Dibuja la lista por primera vez al abrir la ventana
    actualizar_lista()


