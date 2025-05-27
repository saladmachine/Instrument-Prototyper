# SPDX-FileCopyrightText: 2025 Joe Pardue
# SPDX-License-Identifier: MIT

"""
Minimal web server that only serves "Hello World" page.
Based on successful WiFi connectivity test.
"""

import wifi
import socketpool

# Import WiFi credentials
try:
    from secrets import secrets
except ImportError:
    print("ERROR: Need secrets.py with WiFi credentials")
    raise


def connect_wifi():
    """Connect to WiFi - we know this works."""
    print("Connecting to WiFi...")
    wifi.radio.connect(secrets["ssid"], secrets["password"])
    print(f"Connected! IP: {wifi.radio.ipv4_address}")


def create_simple_response():
    """Create minimal HTTP response."""
    html = """<!DOCTYPE html>
<html>
<head><title>Hello WorldJ</title></head>
<body><h1>Hello, World!</h1></body>
</html>"""

    response = f"""HTTP/1.1 200 OK\r
Content-Type: text/html\r
Content-Length: {len(html)}\r
Connection: close\r
\r
{html}"""

    return response


def run_server():
    """Run minimal web server."""
    connect_wifi()

    # Create socket pool
    pool = socketpool.SocketPool(wifi.radio)

    # Create server socket
    server_socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    server_socket.setsockopt(pool.SOL_SOCKET, pool.SO_REUSEADDR, 1)

    # Bind and listen
    server_address = (str(wifi.radio.ipv4_address), 80)
    server_socket.bind(server_address)
    server_socket.listen(1)

    print(f"Server running at http://{wifi.radio.ipv4_address}")
    print("Visit the URL in your browser")
    print("Press Ctrl+C to stop")

    try:
        while True:
            # Accept connection
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")

            # Read request using correct recv_into method
            buffer = bytearray(1024)
            bytes_read = client_socket.recv_into(buffer)
            request_data = buffer[:bytes_read].decode("utf-8")
            request_line = request_data.split("\r\n")[0]
            print(f"Request: {request_line}")

            # Send response
            response = create_simple_response()
            client_socket.send(response.encode())

            # Close connection
            client_socket.close()
            print("Response sent, connection closed")

    except KeyboardInterrupt:
        print("\nServer stopped")
    finally:
        server_socket.close()
        print("Server socket closed")


if __name__ == "__main__":
    run_server()
