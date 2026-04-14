import network
import socket
from machine import Pin

# Connect to Wi-Fi
ssid = 'YOUR_WIFI_NAME'
password = 'YOUR_WIFI_PASSWORD'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

while not wlan.isconnected():
    pass

print('Connected! IP address:', wlan.ifconfig()[0])

# Set up LED and Server
led = Pin("LED", Pin.OUT)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    conn, addr = s.accept()
    request = conn.recv(1024).decode()
    
    if 'LED_ON' in request:
        led.value(1)
    elif 'LED_OFF' in request:
        led.value(0)
        
    conn.send('HTTP/1.1 200 OK\n\nOK')
    conn.close()
