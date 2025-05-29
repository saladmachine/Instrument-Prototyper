# SPDX-FileCopyrightText: 2025 Joe Pardue
# SPDX-License-Identifier: MIT

"""
Menu System Web Server for Raspberry Pi Pico W with LED Blink Rate Control.

Features:
- Main menu with navigation to different functions
- LED blink rate control (existing functionality)
- File editor (saves success message but files don't actually persist)
- 6 placeholder hooks for future features
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

# Main Menu HTML
MENU_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Pico W Control Panel</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            text-align: center;
            background-color: #f5f5f5;
        }
        .menu-container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .menu-item {
            background-color: #4CAF50;
            color: white;
            padding: 15px 25px;
            margin: 10px 0;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 18px;
            width: 100%;
            text-decoration: none;
            display: inline-block;
            box-sizing: border-box;
        }
        .menu-item:hover {
            background-color: #45a049;
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
        }
    </style>
</head>
<body>
    <div class="menu-container">
        <h1>Pico W Control Panel</h1>
        
        <a href="/blink" class="menu-item">LED Blink Rate Control</a>
        <a href="/hook1" class="menu-item">File Editor</a>
        <a href="/hook2" class="menu-item">Hook 2</a>
        <a href="/hook3" class="menu-item">Hook 3</a>
        <a href="/hook4" class="menu-item">Hook 4</a>
        <a href="/hook5" class="menu-item">Hook 5</a>
        <a href="/hook6" class="menu-item">Hook 6</a>
    </div>
</body>
</html>"""

# Blink Rate Control HTML (your existing interface with back button)
BLINK_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Pico W Blink Control</title>
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
        .back-btn {
            background-color: #666;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin: 20px 5px;
            text-decoration: none;
            display: inline-block;
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
    
    <br>
    <a href="/" class="back-btn">Back to Main Menu</a>

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

# File Editor HTML
FILE_EDITOR_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Pico W File Editor</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 700px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .editor-container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
            box-sizing: border-box;
        }
        textarea {
            width: 100%;
            height: 300px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            font-family: monospace;
            box-sizing: border-box;
            resize: vertical;
        }
        .btn {
            background-color: #4CAF50;
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin: 5px;
        }
        .btn:hover {
            background-color: #45a049;
        }
        .back-btn {
            background-color: #666;
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin: 20px 5px 5px 5px;
            text-decoration: none;
            display: inline-block;
        }
        .status {
            margin-top: 15px;
            padding: 10px;
            border-radius: 4px;
            display: none;
        }
        .status.success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .button-group {
            text-align: center;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="editor-container">
        <h1>File Editor</h1>
        
        <div class="form-group">
            <label for="filename">Filename:</label>
            <input type="text" id="filename" placeholder="example.txt">
        </div>
        
        <div class="form-group">
            <label for="filecontent">File Content:</label>
            <textarea id="filecontent" placeholder="Enter your text here..."></textarea>
        </div>
        
        <div class="button-group">
            <button class="btn" onclick="saveFile()">Save File</button>
            <button class="btn" onclick="loadFile()">Load File</button>
            <button class="btn" onclick="clearEditor()">Clear</button>
        </div>
        
        <div id="status" class="status"></div>
        
        <div class="button-group">
            <a href="/" class="back-btn">Back to Main Menu</a>
        </div>
    </div>

    <script>
        function saveFile() {
            const filename = document.getElementById('filename').value.trim();
            const content = document.getElementById('filecontent').value;
            
            if (!filename) {
                showStatus('Please enter a filename', 'error');
                return;
            }
            
            fetch('/save_file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    filename: filename,
                    content: content
                })
            })
            .then(response => response.text())
            .then(data => {
                showStatus('File saved successfully: ' + filename, 'success');
                console.log('File saved:', filename);
            })
            .catch(error => {
                showStatus('Error saving file: ' + error, 'error');
                console.error('Error:', error);
            });
        }
        
        function loadFile() {
            const filename = document.getElementById('filename').value.trim();
            
            if (!filename) {
                showStatus('Please enter a filename to load', 'error');
                return;
            }
            
            fetch('/load_file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({filename: filename})
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('File not found or error loading');
                }
                return response.json();
            })
            .then(data => {
                document.getElementById('filecontent').value = data.content;
                showStatus('File loaded successfully: ' + filename, 'success');
                console.log('File loaded:', filename);
            })
            .catch(error => {
                showStatus('Error loading file: ' + error, 'error');
                console.error('Error:', error);
            });
        }
        
        function clearEditor() {
            document.getElementById('filename').value = '';
            document.getElementById('filecontent').value = '';
            hideStatus();
        }
        
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + type;
            status.style.display = 'block';
        }
        
        function hideStatus() {
            document.getElementById('status').style.display = 'none';
        }
    </script>
</body>
</html>"""

# Hook Page HTML Template
def get_hook_html(hook_number, hook_name):
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Pico W - {hook_name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            text-align: center;
            background-color: #f5f5f5;
        }}
        .hook-container {{
            background-color: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .back-btn {{
            background-color: #666;
            color: white;
            padding: 15px 25px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            margin: 20px 0;
            text-decoration: none;
            display: inline-block;
        }}
        h1 {{
            color: #333;
            margin-bottom: 20px;
        }}
        p {{
            color: #666;
            font-size: 18px;
            margin-bottom: 30px;
        }}
    </style>
</head>
<body>
    <div class="hook-container">
        <h1>{hook_name}</h1>
        <p>Feature not implemented yet</p>
        <a href="/" class="back-btn">Back to Main Menu</a>
    </div>
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

# Route handlers
@server.route("/")
def main_menu(request: Request):
    """Serve main menu."""
    return Response(request, MENU_HTML, content_type="text/html")

@server.route("/blink")
def blink_control(request: Request):
    """Serve blink rate control page."""
    return Response(request, BLINK_HTML, content_type="text/html")

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
        return Response(request, f"Error updating rate: {e}", content_type="text/plain")

# File I/O routes
@server.route("/hook1")
def file_editor(request: Request):
    """File Editor interface."""
    return Response(request, FILE_EDITOR_HTML, content_type="text/html")

@server.route("/save_file", methods=["POST"])
def save_file(request: Request):
    """Save file to Pico filesystem."""
    try:
        print("Parsing request data...")
        data = json.loads(request.body)
        filename = data.get("filename", "").strip()
        content = data.get("content", "")
        
        print(f"Filename: '{filename}', Content length: {len(content)}")
        
        if not filename:
            return Response(request, "Filename required", content_type="text/plain")
        
        print(f"Writing file: {filename}")
        with open(filename, 'w') as f:
            f.write(content)
        
        print(f"File saved successfully: {filename}")
        return Response(request, f"File saved: {filename}", content_type="text/plain")
        
    except OSError as e:
        error_msg = f"Cannot save file (disconnect USB if connected): {e}"
        print(f"File system error: {e}")
        # Return success response but with error message to avoid HTTP server bug
        return Response(request, error_msg, content_type="text/plain")
    except Exception as e:
        error_msg = f"Error saving file: {e}"
        print(error_msg)
        # Return success response but with error message to avoid HTTP server bug  
        return Response(request, error_msg, content_type="text/plain")

@server.route("/load_file", methods=["POST"])
def load_file(request: Request):
    """Load file from Pico filesystem."""
    try:
        data = json.loads(request.body)
        filename = data.get("filename", "").strip()
        
        if not filename:
            return Response(request, "Filename required", content_type="text/plain")
        
        # Try to read from /lib directory first, then root
        filepath = f"/lib/{filename}"
        try:
            with open(filepath, 'r') as f:
                content = f.read()
        except OSError:  # Use OSError instead of FileNotFoundError
            # Try root directory as fallback
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                filepath = filename
            except OSError:
                return Response(request, "File not found", content_type="text/plain")
        
        print(f"File loaded: {filepath} ({len(content)} characters)")
        response_data = {"content": content}
        return Response(request, json.dumps(response_data), content_type="application/json")
        
    except Exception as e:
        print(f"Error loading file: {e}")
        return Response(request, f"Error loading file: {e}", content_type="text/plain")

# Hook routes
@server.route("/hook2")
def hook2(request: Request):
    """Hook 2."""
    return Response(request, get_hook_html(2, "Hook 2"), content_type="text/html")

@server.route("/hook3")
def hook3(request: Request):
    """Hook 3."""
    return Response(request, get_hook_html(3, "Hook 3"), content_type="text/html")

@server.route("/hook4")
def hook4(request: Request):
    """Hook 4."""
    return Response(request, get_hook_html(4, "Hook 4"), content_type="text/html")

@server.route("/hook5")
def hook5(request: Request):
    """Hook 5."""
    return Response(request, get_hook_html(5, "Hook 5"), content_type="text/html")

@server.route("/hook6")
def hook6(request: Request):
    """Hook 6."""
    return Response(request, get_hook_html(6, "Hook 6"), content_type="text/html")

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