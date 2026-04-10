import tkinter as tk
import requests

# Replace with the IP address printed by your Pico W
PICO_IP = f"http://{input("ip:")}"

def send_command(command):
    try:
        requests.get(f"{PICO_IP}/{command}")
    except Exception as e:
        print("Connection Error:", e)

# Tkinter GUI Setup
root = tk.Tk()
root.title("Pico W Wi-Fi Controller")

btn_on = tk.Button(root, text="Turn LED ON", command=lambda: send_command("LED_ON"))
btn_on.pack(pady=10)

btn_off = tk.Button(root, text="Turn LED OFF", command=lambda: send_command("LED_OFF"))
btn_off.pack(pady=10)

root.mainloop()

    
