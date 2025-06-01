"""
Raspberry Pi Pico 2 W WiFi Hotspot Web Server
=============================================

A simple WiFi hotspot and web server implementation for the Raspberry Pi Pico 2 W
using CircuitPython. Creates an open WiFi access point and serves a basic webpage
to connected devices.

Hardware Requirements:
- Raspberry Pi Pico 2 W (RP2350 with WiFi)
- USB power source

Software Requirements:
- CircuitPython 9.2.7 or later
- adafruit_httpserver library

Installation:
1. Install CircuitPython on your Pico 2 W
2. Copy adafruit_httpserver library to /lib/ folder
3. Save this file as code.py on the CIRCUITPY drive

Usage:
1. Power on the Pico 2 W
2. Look for "PicoTest" in your device's WiFi networks
3. Connect to "PicoTest" (no password required)
4. Open a web browser and navigate to: http://192.168.4.1
5. You should see a success page served by the Pico 2 W

Network Configuration:
- SSID: PicoTest
- Security: Open (no password)
- IP Address: 192.168.4.1
- Subnet: 255.255.255.0
- DHCP: Enabled (devices get 192.168.4.x addresses)

Author: Generated for CircuitPython Project
License: MIT License
Date: 2025

MIT License:
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
"""

# Import required libraries
import wifi
import socketpool
import ipaddress
import time
from adafruit_httpserver import Server, Request, Response

# Configuration constants
HOTSPOT_SSID = "PicoTest"
HOTSPOT_IP = "192.168.4.1"
HOTSPOT_NETMASK = "255.255.255.0"
HOTSPOT_GATEWAY = "192.168.4.1"
WEB_SERVER_PORT = 80

def create_hotspot():
    """
    Create a WiFi hotspot (access point) on the Pico 2 W.
    
    Creates an open WiFi network that devices can connect to.
    The hotspot uses a static IP configuration.
    
    Returns:
        bool: True if hotspot creation was successful
        
    Raises:
        Exception: If hotspot creation fails
    """
    print("=== PICO 2 W HOTSPOT WEB SERVER ===")
    print("Creating WiFi hotspot...")
    
    try:
        # Start the access point with specified SSID (no password = open network)
        wifi.radio.start_ap(ssid=HOTSPOT_SSID)
        
        # Configure static IP address for the access point
        # This sets the Pico 2 W as the gateway at 192.168.4.1
        wifi.radio.set_ipv4_address_ap(
            ipv4=ipaddress.IPv4Address(HOTSPOT_IP),
            netmask=ipaddress.IPv4Address(HOTSPOT_NETMASK), 
            gateway=ipaddress.IPv4Address(HOTSPOT_GATEWAY)
        )
        
        print(f"✅ Hotspot created: {HOTSPOT_SSID}")
        print(f"✅ IP Address: {HOTSPOT_IP}")
        print("✅ Security: Open (no password required)")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create hotspot: {e}")
        return False

def create_web_server():
    """
    Create and configure the HTTP web server.
    
    Sets up a simple web server that listens on port 80 and serves
    a success page to connected devices.
    
    Returns:
        Server: Configured HTTP server instance
        
    Raises:
        Exception: If server creation fails
    """
    # Create socket pool for network communications
    pool = socketpool.SocketPool(wifi.radio)
    
    # Initialize HTTP server
    server = Server(pool)
    
    @server.route("/")
    def homepage(request: Request):
        """
        Handle requests to the root URL (/).
        
        Serves a simple HTML page confirming successful connection
        to the Pico 2 W hotspot.
        
        Args:
            request (Request): The incoming HTTP request
            
        Returns:
            Response: HTML response with success page
        """
        print("📱 Device connected! Serving homepage...")
        
        # Generate simple HTML response
        # Uses inline styles for compatibility and minimal CSS parsing
        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Pico 2 W Success</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <center>
        <h1 style="color: green;">🎉 SUCCESS!</h1>
        <h2>Pico 2 W is working!</h2>
        <p><b>Your device connected successfully</b></p>
        <p><b>Server uptime:</b> {:.1f} seconds</p>
        <p>You are connected to the Pico 2 W hotspot</p>
        <hr>
        <p>This webpage is being served by your Raspberry Pi Pico 2 W!</p>
        <p><small>CircuitPython WiFi Hotspot Demo</small></p>
    </center>
</body>
</html>""".format(time.monotonic())
        
        # Return HTTP response with HTML content
        return Response(request, html_content, content_type="text/html")
    
    return server

def start_web_server(server):
    """
    Start the web server and begin listening for connections.
    
    Args:
        server (Server): The configured HTTP server instance
        
    Returns:
        bool: True if server started successfully
        
    Raises:
        Exception: If server startup fails
    """
    try:
        # Start server on the hotspot IP address and specified port
        server.start(HOTSPOT_IP, port=WEB_SERVER_PORT)
        print("✅ Web server started successfully")
        print(f"✅ Listening on: http://{HOTSPOT_IP}:{WEB_SERVER_PORT}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start web server: {e}")
        return False

def main():
    """
    Main program loop.
    
    Creates the WiFi hotspot, starts the web server, and handles
    incoming connections. Runs continuously until interrupted.
    """
    # Step 1: Create WiFi hotspot
    if not create_hotspot():
        print("Cannot continue without hotspot. Exiting.")
        return
    
    # Step 2: Set up web server
    try:
        server = create_web_server()
    except Exception as e:
        print(f"Failed to create web server: {e}")
        return
    
    # Step 3: Start web server
    if not start_web_server(server):
        print("Cannot continue without web server. Exiting.")
        return
    
    # Display connection instructions
    print("\n" + "="*50)
    print("📱 CONNECTION INSTRUCTIONS:")
    print("="*50)
    print(f"1. Connect to WiFi network: '{HOTSPOT_SSID}'")
    print("2. No password required (open network)")
    print(f"3. Open web browser and go to: http://{HOTSPOT_IP}")
    print("4. You should see a success page")
    print("="*50)
    print("\nServer running... Press Ctrl+C to stop")
    
    # Main server loop - handle incoming requests
    request_count = 0
    try:
        while True:
            # Poll for incoming HTTP requests
            server.poll()
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        print("Goodbye!")
        
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        print("Server stopped due to error")

# Run the main program
if __name__ == "__main__":
    main()