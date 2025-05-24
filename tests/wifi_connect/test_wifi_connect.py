# test_wifi_connect.py
# Test program for connecting the Pico W to a Wi-Fi network using secrets.py.

import wifi
import socketpool
import board
import time
import os
import secrets  # Import the secrets file

print("--- Starting Wi-Fi Connection Test ---")

try:
    # Get Wi-Fi credentials from secrets.py
    ssid = secrets.secrets["ssid"]
    password = secrets.secrets["password"]

    # Check if Wi-Fi is already connected
    if wifi.radio.ipv4_address:
        print(f"Already connected! IP address: {wifi.radio.ipv4_address}")
    else:
        print(f"Connecting to Wi-Fi network: {ssid}")
        wifi.radio.connect(ssid, password)
        print("Connected to Wi-Fi!")
        print(f"IP address: {wifi.radio.ipv4_address}")

    # Optional: Test a simple internet connection by resolving a hostname
    pool = socketpool.SocketPool(wifi.radio)
    print("Attempting to resolve google.com...")
    ip_address = pool.getaddrinfo("google.com", 80)[0][4][0]
    print(f"google.com resolved to: {ip_address}")
    print("Internet connection seems to be working.")

except ConnectionError as e:
    print(f"Wi-Fi Connection Error: {e}")
    print("Please check your Wi-Fi network name (SSID) and password in secrets.py.")
    print("Ensure your Wi-Fi network is active and within range.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

print("--- Wi-Fi Connection Test Complete ---")

# The program will idle here.
while True:
    time.sleep(1)
