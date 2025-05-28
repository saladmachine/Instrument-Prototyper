# SPDX-FileCopyrightText: 2025 Joe Pardue
# SPDX-License-Identifier: MIT

"""
Single File Slider Position Web Server for Raspberry Pi Pico W.

Features:
- Static HTML embedded in Python (no external files)
- JSON API for slider position
- Simple numerical value storage (0-100)
- Single code.py file - no directory changes needed

Test Code Architecture:
- HTML string constant (static content)
- JSON API endpoints (dynamic data)
- All in one file for easy testing
"""

import time
import json
import wifi
import socketpool
from adafruit_httpserver import Server, Request, Response
from secrets import secrets

# Global slider position (0-100)
slider_position = 50  # Start at middle position

# Static HTML - embedded in Python but still static (no dynamic generation)
STATIC_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Pico W Slider Control</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            text-align: center;
        }
        .slider-container {
            margin: 30px 0;
        }
        .slider {
            width: 300px;
            height: 10px;
            background: #ddd;
            outline: none;
            border-radius: 5px;
        }
        .value-display {
            font-size: 24px;
            margin: 20px 0;
            color: #333;
        }
        .update-btn {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin: 5px;
        }
    </style>
</head>
<body>
    <h1>Pico W Slider Control</h1>
    
    <div class="slider-container">
        <label for="positionSlider">Position:</label><br>
        <input type="range" id="positionSlider" class="slider" min="0" max="100" value="50">
    </div>
    
    <div class="value-display">
        Current Position: <span id="currentValue">50</span>
    </div>
    
    <button class="update-btn" onclick="sendPosition()">Update Position</button>
    <button class="update-btn" onclick="getCurrentPosition()">Get Current Position</button>

    <script>
        const slider = document.getElementById('positionSlider');
        const valueDisplay = document.getElementById('currentValue');
        
        // Update display when slider moves
        slider.addEventListener('input', function() {
            valueDisplay.textContent = this.value;
        });
        
        // Send slider position to Pico W
        function sendPosition() {
            const position = slider.value;
            
            fetch('/set_slider', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({position: parseInt(position)})
            })
            .then(response => response.text())
            .then(data => {
                console.log('Position sent:', position);
                alert('Position updated to: ' + position);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error updating position');
            });
        }
        
        // Get current position from Pico W
        function getCurrentPosition() {
            fetch('/get_slider')
            .then(response => response.json())
            .then(data => {
                const position = data.position;
                slider.value = position;
                valueDisplay.textContent = position;
                console.log('Current position:', position);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error getting current position');
            });
        }
        
        // Get initial position when page loads
        window.onload = function() {
            getCurrentPosition();
        };
    </script>
</body>
</html>"""

# Connect to WiFi
print("Connecting to WiFi...")
wifi.radio.connect(secrets["ssid"], secrets["password"])
ip_address = str(wifi.radio.ipv4_address)
print(f"Connected to WiFi! IP Address: {ip_address}")

# Set up mDNS
try:
    from mdns import Server as MDNSServer
    mdns_server = MDNSServer(wifi.radio)
    mdns_server.hostname = "pico"
    mdns_server.advertise_service(service_type="_http", protocol="_tcp", port=80)
    print("mDNS hostname set to: pico.local")
except ImportError:
    print("mDNS is not available in your CircuitPython version.")
except Exception as e:
    print(f"Error with mDNS setup: {e}")

# Set up HTTP server
pool = socketpool.SocketPool(wifi.radio)
server = Server(pool)

@server.route("/")
def index(request: Request):
    """Serve static HTML (embedded in Python)."""
    return Response(request, STATIC_HTML, content_type="text/html")

@server.route("/get_slider")
def get_slider(request: Request):
    """Return current slider position as JSON."""
    data = {"position": slider_position}
    return Response(request, json.dumps(data), content_type="application/json")

@server.route("/set_slider", methods=["POST"])
def set_slider(request: Request):
    """Update slider position from POST data."""
    global slider_position
    try:
        data = json.loads(request.body)
        new_position = int(data.get("position", 50))
        
        # Clamp value between 0 and 100
        slider_position = max(0, min(100, new_position))
        
        print(f"Slider position updated to: {slider_position}")
        return Response(request, "Position updated", content_type="text/plain")
    except Exception as e:
        print("Error updating slider:", e)
        return Response(request, "Error updating position", content_type="text/plain", status=400)

# Start server
print("Starting server...")
server.start(ip_address, port=80)
print(f"Server running at http://{ip_address}")
print("Server running at http://pico.local")
print()
print("Current slider position:", slider_position)

# Keep the server running
while True:
    try:
        server.poll()
    except Exception as e:
        print("Error:", e)
        time.sleep(1)