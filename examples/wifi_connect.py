# SPDX-FileCopyrightText: 2025 Joe Pardue
#
# SPDX-License-Identifier: MIT

"""
Pico W 2 Wi-Fi Connection Example

This example demonstrates how to connect the Raspberry Pi Pico W 2 to a
Wi-Fi network using credentials stored in a 'secrets.py' file.
It also performs a basic internet connectivity test by resolving a hostname.

Ensure 'secrets.py' is placed on your CIRCUITPY drive and contains:
secrets = {
    'ssid': 'YOUR_WIFI_NETWORK_NAME',
    'password': 'YOUR_WIFI_PASSWORD'
}
Remember to NEVER commit 'secrets.py' to your Git repository for security!
"""

import wifi
import socketpool
import board  # Not strictly needed for this example, but common in CircuitPython
import time
import os  # Needed for os.getenv if using environment variables, or other os-level tasks
import secrets  # Import the secrets.py file from the CIRCUITPY drive

print("--- Starting Wi-Fi Connection Example ---")

try:
    # Retrieve Wi-Fi credentials from the 'secrets' dictionary defined in secrets.py
    ssid = secrets.secrets["ssid"]
    password = secrets.secrets["password"]

    print(f"Attempting to connect to Wi-Fi network: '{ssid}'")

    # Check if Wi-Fi is already connected from a previous run or state
    if wifi.radio.ipv4_address:
        print(f"Already connected! Current IP address: {wifi.radio.ipv4_address}")
    else:
        # Attempt to connect to the Wi-Fi network
        wifi.radio.connect(ssid, password)
        print("Successfully connected to Wi-Fi!")
        print(f"Assigned IP address: {wifi.radio.ipv4_address}")

    # Initialize a socket pool using the active Wi-Fi radio for internet access
    pool = socketpool.SocketPool(wifi.radio)

    # Perform a simple DNS lookup to verify internet connectivity
    print("Attempting to resolve 'google.com' to test internet access...")
    # getaddrinfo returns a list of tuples; we want the IP address from the first valid entry
    ip_address = pool.getaddrinfo("google.com", 80)[0][4][0]
    print(f"'google.com' resolved to IP: {ip_address}")
    print("Internet connection appears to be working correctly.")

except ConnectionError as e:
    # Catch specific connection-related errors
    print(f"\nWi-Fi Connection Error: {e}")
    print("Troubleshooting Tips:")
    print("  - Double-check your Wi-Fi network name (SSID) and password in secrets.py.")
    print("  - Ensure your Pico W 2 is within range of your Wi-Fi router.")
    print(
        "  - Verify your Wi-Fi network is active and broadcasting (or correctly hidden)."
    )
except KeyError as e:
    # Catch errors if 'ssid' or 'password' keys are missing from secrets.py
    print(f"\nConfiguration Error: Missing Wi-Fi credential in secrets.py: {e}")
    print(
        "Please ensure both 'ssid' and 'password' keys are defined in your secrets.py file."
    )
except Exception as e:
    # Catch any other unexpected errors during the process
    print(f"\nAn unexpected error occurred: {e}")
    print("Please review the traceback above for more details.")

print("\n--- Wi-Fi Connection Example Complete ---")

# Keep the program running indefinitely to maintain Wi-Fi connection (optional)
while True:
    time.sleep(1)
