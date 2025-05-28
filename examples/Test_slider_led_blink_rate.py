# SPDX-FileCopyrightText: 2025 Joe Pardue
# SPDX-License-Identifier: MIT

"""
Single File LED Blink Rate Control Web Server for Raspberry Pi Pico W.

Features:
- Web slider controls LED blink rate (0-100)
- 0 = LED off, 100 = fast blink, proportional in between
- JSON API for blink rate control
- Non-blocking LED control with web server

Hardware:
- Uses onboard LED on Pico W
- No additional wiring required
"""

import time
import json
import wifi
import socketpool
import board
import digitalio
from adafruit_httpserver import Server, Request, Response
from secrets import secrets

# Initialize onboard LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = False

# Global blink rate (0-100) and LED state tracking
blink_rate = 0  # Start with LED off
led_state = False
last_blink_time = 0

def update_led():
    """Update LED based on current blink rate (non-blocking)."""
    global led_state, last_blink_time
    
    current_time = time.monotonic()
    
    if blink_rate == 0:
        # Rate 0 = LED off
        led.value = False
        led_state = False
    else:
        # Calculate blink interval: faster rate = shorter interval
        # Rate 1 = 2 second interval, Rate 100 = 0.02 second interval  
        blink_interval = 2.0 - (blink_rate * 0.0198)  # 2.0 to 0.02 seconds
        
        # Check if it's time to toggle
        if current_time - last_blink_time >= blink_interval:
            led_state = not led_state
            led.value = led_state
            last_blink_time = current_time

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
    <h1>Pico W LED Blink Control</h1>
    
    <div class="slider-container">
        <label for="blinkSlider">Blink Rate:</label><br>
        <input type="range" id="blinkSlider" class="slider" min="0" max="100" value="0">
    </div>
    
    <div class="value-display">
        Current Rate: <span id="currentValue">0</span>
        <br><small>(0 = Off, 100 = Very Fast)</small>
    </div>
    
    <button class="update-btn" onclick="sendRate()">Update Blink Rate</button>
    <button class="update-btn" onclick="getCurrentRate()">Get Current Rate</button>

    <script>
        const slider = document.getElementById('blinkSlider');
        const valueDisplay = document.getElementById('currentValue');
        
        // Update display when slider moves
        slider.addEventListener('input', function() {
            valueDisplay.textContent = this.value;
        });
        
        // Send blink rate to Pico W
        function sendRate() {
            const rate = slider.value;
            
            fetch('/set_blink', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({rate: parseInt(rate)})
            })
            .then(response => response.text())
            .then(data => {
                console.log('Blink rate sent:', rate);
                alert('Blink rate updated to: ' + rate);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error updating blink rate');
            });
        }
        
        // Get current blink rate from Pico W
        function getCurrentRate() {
            fetch('/get_blink')
            .then(response => response.json())
            .then(data => {
                const rate = data.rate;
                slider.value = rate;
                valueDisplay.textContent = rate;
                console.log('Current blink rate:', rate);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error getting current blink rate');
            });
        }
        
        // Get initial rate when page loads
        window.onload = function() {
            getCurrentRate();
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

@server.route("/get_blink")
def get_blink(request: Request):
    """Return current blink rate as JSON."""
    data = {"rate": blink_rate}
    return Response(request, json.dumps(data), content_type="application/json")

@server.route("/set_blink", methods=["POST"])
def set_blink(request: Request):
    """Update blink rate from POST data."""
    global blink_rate
    try:
        data = json.loads(request.body)
        new_rate = int(data.get("rate", 0))
        
        # Clamp value between 0 and 100
        blink_rate = max(0, min(100, new_rate))
        
        print(f"LED blink rate updated to: {blink_rate}")
        return Response(request, "Blink rate updated", content_type="text/plain")
    except Exception as e:
        print("Error updating blink rate:", e)
        return Response(request, "Error updating rate", content_type="text/plain", status=400)

# Start server
print("Starting server...")
server.start(ip_address, port=80)
print(f"Server running at http://{ip_address}")
print("Server running at http://pico.local")
print("Current LED blink rate:", blink_rate)

# Keep the server running
while True:
    try:
        # Update LED blinking (non-blocking)
        update_led()
        
        # Handle web requests
        server.poll()
    except Exception as e:
        print("Error:", e)
        time.sleep(1)