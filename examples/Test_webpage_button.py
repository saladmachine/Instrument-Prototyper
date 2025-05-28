# SPDX-FileCopyrightText: 2025 Joe Pardue
# SPDX-License-Identifier: MIT

"""
LED Control Web Server for Raspberry Pi Pico W.

Features:
- WiFi connectivity with proper error handling
- Web server on port 8080 for LED control
- Toggle LED state via web interface
- Real-time LED status display

Hardware Requirements:
- Raspberry Pi Pico W
- Onboard LED (built-in)

Library Dependencies:
- wifi (CircuitPython core)
- socketpool (CircuitPython core)
- board (CircuitPython core)
- digitalio (CircuitPython core)

Usage:
1. Create secrets.py with WiFi credentials
2. Connect to WiFi network shown in output
3. Navigate to http://[IP_ADDRESS]:8080
4. Click "Toggle LED" button to control onboard LED
"""

import wifi
import socketpool
import board
import digitalio

# Import WiFi credentials
try:
    from secrets import secrets
except ImportError:
    print("ERROR: WiFi credentials required in secrets.py")
    print("Create secrets.py with: secrets = {'ssid': 'your_network', 'password': 'your_password'}")
    raise

def initialize_led():
    """Initialize the onboard LED for output control."""
    led = digitalio.DigitalInOut(board.LED)
    led.direction = digitalio.Direction.OUTPUT
    led.value = False  # Start with LED off
    print("LED initialized (OFF)")
    return led

def connect_to_wifi():
    """Connect to WiFi network using credentials from secrets.py."""
    print("Connecting to WiFi...")
    try:
        wifi.radio.connect(secrets["ssid"], secrets["password"])
        print(f"SUCCESS: Connected to {secrets['ssid']}")
        print(f"IP Address: {wifi.radio.ipv4_address}")
        return True
    except Exception as e:
        print(f"FAILED: WiFi connection error - {e}")
        return False

def generate_html_response(led_state):
    """
    Generate HTML page with current LED status and toggle button.
    
    Args:
        led_state (bool): Current state of LED (True=ON, False=OFF)
        
    Returns:
        str: Complete HTML page as string
    """
    led_status = "ON" if led_state else "OFF"
    led_color = "#00ff00" if led_state else "#ff0000"
    button_text = "Turn OFF" if led_state else "Turn ON"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Pico W LED Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            text-align: center;
        }}
        .status {{
            font-size: 24px;
            color: {led_color};
            margin: 20px 0;
        }}
        button {{
            background-color: #4CAF50;
            color: white;
            padding: 15px 32px;
            text-align: center;
            font-size: 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }}
        button:hover {{
            background-color: #45a049;
        }}
    </style>
</head>
<body>
    <h1>Pico W LED Control</h1>
    <div class="status">
        LED Status: <strong>{led_status}</strong>
    </div>
    <form action="/toggle" method="post">
        <button type="submit">{button_text}</button>
    </form>
    <p><small>IP: {wifi.radio.ipv4_address}:8080</small></p>
</body>
</html>"""
    
    return html

def handle_http_request(connection, led):
    """
    Process incoming HTTP request and generate appropriate response.
    
    Args:
        connection: Socket connection object
        led: LED control object
        
    Returns:
        bool: True if request was handled successfully
    """
    try:
        # Read incoming request data
        buffer = bytearray(1024)
        bytes_received = connection.recv_into(buffer)
        request = buffer[:bytes_received].decode('utf-8')
        
        # Parse request line
        request_line = request.split('\r\n')[0]
        print(f"Request: {request_line}")
        
        # Handle LED toggle request
        if "POST /toggle" in request_line:
            led.value = not led.value
            led_state_text = "ON" if led.value else "OFF"
            print(f"LED toggled to: {led_state_text}")
        
        # Generate and send HTTP response
        html_content = generate_html_response(led.value)
        http_response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n{html_content}"
        
        connection.sendall(http_response.encode('utf-8'))
        return True
        
    except Exception as e:
        print(f"Request handling error: {e}")
        return False

def run_web_server(led):
    """
    Start and run the web server for LED control.
    
    Args:
        led: LED control object
    """
    # Create socket pool
    pool = socketpool.SocketPool(wifi.radio)
    
    print("Starting web server...")
    print(f"Server URL: http://{wifi.radio.ipv4_address}:8080")
    print("Press Ctrl+C to stop server")
    
    try:
        # Create server socket
        with pool.socket(pool.AF_INET, pool.SOCK_STREAM) as server_socket:
            # Bind to all interfaces on port 8080
            server_socket.bind(("0.0.0.0", 8080))
            server_socket.listen(1)
            
            print("Server listening on port 8080...")
            
            # Main server loop
            while True:
                try:
                    # Accept incoming connection
                    client_connection, client_address = server_socket.accept()
                    print(f"Connection from {client_address}")
                    
                    # Handle the request
                    request_success = handle_http_request(client_connection, led)
                    
                    if request_success:
                        print("Request handled successfully")
                    else:
                        print("Request handling failed")
                        
                except Exception as e:
                    print(f"Connection error: {e}")
                    
                finally:
                    # Always close client connection
                    try:
                        client_connection.close()
                    except:
                        pass
                        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")

def main():
    """Main program execution."""
    print("=" * 50)
    print("Pico W LED Control Web Server")
    print("=" * 50)
    
    # Initialize hardware
    led = initialize_led()
    
    # Connect to WiFi
    if not connect_to_wifi():
        print("Cannot start server without WiFi connection")
        return
    
    # Start web server
    run_web_server(led)

if __name__ == "__main__":
    main()