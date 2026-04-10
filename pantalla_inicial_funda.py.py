import tkinter as tk
#esto crea la ventana principal y le da un título
ventana = tk.Tk()
ventana.title("StrangerTEC")
#Pone un titulo dentro de la ventana y lo centra
titulo = tk.Label(ventana, text="Bienvenido a StrangerTEC")
titulo.pack(pady=10)

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
# Guarda el nombre ingresado y lo muestra en la etiqueta correspondiente, luego cierra la ventana de ingreso de nombre
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

def iniciar_juego():
    print("aqui la funcion llama a la pantalla de juego osea, el abecedario y el tablero")



tk.Button(ventana, text="Iniciar Juego", command=iniciar_juego).pack(pady=50)
ventana.mainloop()