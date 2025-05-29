# SPDX-FileCopyrightText: 2025 Joe Pardue
# SPDX-License-Identifier: MIT

"""
Menu System Web Server for Raspberry Pi Pico W with LED Blink Rate Control.

Comprehensive web-based control interface with menu navigation system for
instrument control applications. Provides LED blink rate control and 
file editor functionality with extensible hook system for future features.

**REVOLUTIONARY FEATURE: Live Code Development Environment**
This system enables complete code development directly on the Pico W using
only a web browser - no computer or USB connection required for development!

Features:
- Web-based menu navigation system
- LED blink rate control (0-100 scale with non-blocking operation)
- **Live code editor with automatic reload** - edit code.py and automatically reboot
- File editor with save/load capabilities for configuration management
- **Self-contained development environment** - develop from phone/tablet/any browser
- **Instant feedback loop** - save code.py → auto-reboot → test immediately
- 6 extensible hook placeholders for future functionality
- Minimal CSS framework for compact, responsive design
- JSON API endpoints for data exchange
- Non-blocking concurrent operations (LED control + web server)

**Live Development Workflow:**
1. Access web interface via pico.local or IP address
2. Load code.py in file editor (shows current running code)
3. Make changes directly in browser
4. Save - Pico automatically reboots with new code in 2 seconds
5. Test new functionality immediately
6. Repeat cycle for rapid development

**Auto-Reboot Behavior:**
- code.py: Automatic reboot after save (enables live development)
- All other files: Save without reboot (configuration files, data, etc.)

Hardware Requirements:
- Raspberry Pi Pico W with onboard LED
- No additional wiring required for basic functionality
- Optional: External battery for standalone operation and development

Library Dependencies:
- Core: time, json, wifi, socketpool, board, digitalio, microcontroller
- External: adafruit_httpserver (handles HTTP protocol and socket management)
- Configuration: secrets.py (WiFi credentials)

Usage:
1. Create secrets.py with WiFi credentials (SSID and PASSWORD)
2. Upload this code as code.py to CIRCUITPY drive
3. Access web interface via IP address or pico.local
4. Navigate menu system to access different functions
5. Use file editor for live code development - no computer needed!
6. LED blink control provides immediate feedback of system operation

Architecture Notes:
- Minimal CSS framework reduces code size by 80% while maintaining functionality
- JSON API pattern for reliable data exchange
- adafruit_httpserver provides proper socket lifecycle management
- Separation of presentation (HTML) and data (JSON endpoints)
- Scheduled reboot system for seamless code reloading
"""

import time
import json
import wifi
import socketpool
import board
import digitalio
from adafruit_httpserver import Server, Request, Response
from secrets import secrets

# Initialize onboard LED for visual feedback
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = False

# Global state variables for LED control and system management
blink_rate = 0  # Current blink rate (0-100, 0=off)
led_state = False  # Current LED on/off state
last_blink_time = 0  # Timestamp for non-blocking timing
reboot_scheduled = 0  # Timestamp for scheduled reboot (0 = no reboot)

def update_led():
    """
    Update LED state based on current blink rate using non-blocking timing.
    
    Provides proportional blink rate control where:
    - Rate 0: LED permanently off
    - Rate 1: 2 second blink interval (slow)
    - Rate 100: 0.02 second blink interval (very fast)
    
    Uses time.monotonic() for accurate non-blocking timing that doesn't
    interfere with web server operations.
    
    Returns:
        None
    """
    global led_state, last_blink_time
    
    current_time = time.monotonic()
    
    if blink_rate == 0:
        # Rate 0 = LED permanently off
        led.value = False
        led_state = False
    else:
        # Calculate blink interval with linear scaling
        # Formula: 2.0 - (rate * 0.0198) gives range 2.0s to 0.02s
        blink_interval = 2.0 - (blink_rate * 0.0198)
        
        # Non-blocking timing check
        if current_time - last_blink_time >= blink_interval:
            led_state = not led_state
            led.value = led_state
            last_blink_time = current_time

# Minimal CSS Framework - Compact and responsive
MINI_CSS = """
*, *::before, *::after { box-sizing: border-box; }
body { font-family: Arial, sans-serif; margin: 0; padding: 15px; background: #f5f5f5; }
.container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
h1 { text-align: center; color: #333; margin-bottom: 25px; font-size: 24px; }

.btn { padding: 15px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; 
       margin: 8px 4px; min-height: 48px; text-decoration: none; display: inline-block; 
       text-align: center; min-width: 100px; }
.btn-primary { background: #4CAF50; color: white; }
.btn-secondary { background: #666; color: white; }
.btn:hover { opacity: 0.9; }
.btn:active { transform: translateY(1px); opacity: 0.8; }

.form-group { margin-bottom: 20px; text-align: left; }
.form-group label { display: block; margin-bottom: 8px; font-weight: bold; color: #333; font-size: 16px; }
.form-control { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }
textarea.form-control { min-height: 300px; font-family: 'Courier New', monospace; resize: vertical; line-height: 1.4; }

.slider { width: 100%; max-width: 300px; height: 10px; background: #ddd; border-radius: 5px; 
          -webkit-appearance: none; appearance: none; outline: none; }
.slider::-webkit-slider-thumb { -webkit-appearance: none; width: 25px; height: 25px; 
                                border-radius: 50%; background: #4CAF50; cursor: pointer; }
.slider::-moz-range-thumb { width: 25px; height: 25px; border-radius: 50%; background: #4CAF50; 
                            cursor: pointer; border: none; }

.value-display { font-size: 24px; margin: 20px 0; color: #333; text-align: center; }
.button-group { text-align: center; margin-top: 20px; }

.alert { padding: 12px; border-radius: 4px; margin: 15px 0; display: none; }
.alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
.alert-danger { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }

@media (max-width: 768px) {
    body { padding: 10px; }
    .container { padding: 15px; }
    .btn { width: 100%; margin: 5px 0; padding: 18px; }
    textarea.form-control { min-height: 200px; font-size: 13px; }
    h1 { font-size: 20px; }
    .form-control { padding: 15px; }
}
"""

# HTML Templates using minimal CSS framework
MENU_HTML = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pico W Control Panel</title>
    <style>{MINI_CSS}</style>
</head>
<body>
    <div class="container">
        <h1>Pico W Control Panel</h1>
        <a href="/blink" class="btn btn-primary">LED Blink Rate Control</a>
        <a href="/hook1" class="btn btn-primary">File Editor</a>
        <a href="/hook2" class="btn btn-primary">Hook 2</a>
        <a href="/hook3" class="btn btn-primary">Hook 3</a>
        <a href="/hook4" class="btn btn-primary">Hook 4</a>
        <a href="/hook5" class="btn btn-primary">Hook 5</a>
        <a href="/hook6" class="btn btn-primary">Hook 6</a>
    </div>
</body>
</html>"""

BLINK_HTML = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pico W Blink Control</title>
    <style>{MINI_CSS}</style>
</head>
<body>
    <div class="container">
        <h1>Pico W LED Blink Control</h1>
        
        <div class="form-group" style="text-align: center;">
            <label for="blinkSlider">Blink Rate:</label>
            <input type="range" id="blinkSlider" class="slider" min="0" max="100" value="0">
        </div>
        
        <div class="value-display">
            Current Rate: <span id="currentValue">0</span>
            <br><small>(0 = Off, 100 = Very Fast)</small>
        </div>
        
        <div class="button-group">
            <button class="btn btn-primary" onclick="sendRate()">Update Blink Rate</button>
            <button class="btn btn-primary" onclick="getCurrentRate()">Get Current Rate</button>
        </div>
        
        <div class="button-group">
            <a href="/" class="btn btn-secondary">Back to Main Menu</a>
        </div>
    </div>

    <script>
        const slider = document.getElementById('blinkSlider');
        const valueDisplay = document.getElementById('currentValue');
        
        slider.addEventListener('input', function() {{
            valueDisplay.textContent = this.value;
        }});
        
        function sendRate() {{
            const rate = slider.value;
            fetch('/set_blink', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{rate: parseInt(rate)}})
            }})
            .then(response => response.text())
            .then(data => {{
                console.log('Blink rate sent:', rate);
                alert('Blink rate updated to: ' + rate);
            }})
            .catch(error => {{
                console.error('Error:', error);
                alert('Error updating blink rate');
            }});
        }}
        
        function getCurrentRate() {{
            fetch('/get_blink')
            .then(response => response.json())
            .then(data => {{
                const rate = data.rate;
                slider.value = rate;
                valueDisplay.textContent = rate;
                console.log('Current blink rate:', rate);
            }})
            .catch(error => {{
                console.error('Error:', error);
                alert('Error getting current blink rate');
            }});
        }}
        
        window.onload = function() {{ getCurrentRate(); }};
    </script>
</body>
</html>"""

FILE_EDITOR_HTML = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pico W File Editor</title>
    <style>{MINI_CSS}</style>
</head>
<body>
    <div class="container">
        <h1>File Editor</h1>
        
        <div class="form-group">
            <label for="filename">Filename:</label>
            <input type="text" id="filename" class="form-control" placeholder="example.txt">
        </div>
        
        <div class="form-group">
            <label for="filecontent">File Content:</label>
            <textarea id="filecontent" class="form-control" placeholder="Enter your text here..."></textarea>
        </div>
        
        <div class="button-group">
            <button class="btn btn-primary" onclick="saveFile()">Save File</button>
            <button class="btn btn-primary" onclick="loadFile()">Load File</button>
            <button class="btn btn-primary" onclick="clearEditor()">Clear</button>
        </div>
        
        <div id="status" class="alert"></div>
        
        <div class="button-group">
            <a href="/" class="btn btn-secondary">Back to Main Menu</a>
        </div>
    </div>

    <script>
        function saveFile() {{
            const filename = document.getElementById('filename').value.trim();
            const content = document.getElementById('filecontent').value;
            
            if (!filename) {{
                showStatus('Please enter a filename', 'danger');
                return;
            }}
            
            fetch('/save_file', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{filename: filename, content: content}})
            }})
            .then(response => response.text())
            .then(data => {{
                showStatus('File saved successfully: ' + filename, 'success');
                console.log('File saved:', filename);
            }})
            .catch(error => {{
                showStatus('Error saving file: ' + error, 'danger');
                console.error('Error:', error);
            }});
        }}
        
        function loadFile() {{
            const filename = document.getElementById('filename').value.trim();
            
            if (!filename) {{
                showStatus('Please enter a filename to load', 'danger');
                return;
            }}
            
            fetch('/load_file', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{filename: filename}})
            }})
            .then(response => {{
                if (!response.ok) throw new Error('File not found or error loading');
                return response.json();
            }})
            .then(data => {{
                document.getElementById('filecontent').value = data.content;
                showStatus('File loaded successfully: ' + filename, 'success');
                console.log('File loaded:', filename);
            }})
            .catch(error => {{
                showStatus('Error loading file: ' + error, 'danger');
                console.error('Error:', error);
            }});
        }}
        
        function clearEditor() {{
            document.getElementById('filename').value = '';
            document.getElementById('filecontent').value = '';
            hideStatus();
        }}
        
        function showStatus(message, type) {{
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'alert alert-' + type;
            status.style.display = 'block';
        }}
        
        function hideStatus() {{
            document.getElementById('status').style.display = 'none';
        }}
    </script>
</body>
</html>"""

def get_hook_html(hook_number, hook_name):
    """
    Generate HTML for placeholder hook pages using minimal CSS framework.
    
    Args:
        hook_number (int): Hook identifier number
        hook_name (str): Display name for the hook
        
    Returns:
        str: Static HTML string for hook page
    """
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pico W - {hook_name}</title>
    <style>{MINI_CSS}</style>
</head>
<body>
    <div class="container" style="text-align: center;">
        <h1>{hook_name}</h1>
        <p style="color: #666; font-size: 18px; margin-bottom: 30px;">Feature not implemented yet</p>
        <a href="/" class="btn btn-secondary">Back to Main Menu</a>
    </div>
</body>
</html>"""

# WiFi connection setup
print("Connecting to WiFi...")
wifi.radio.connect(secrets["ssid"], secrets["password"])
ip_address = str(wifi.radio.ipv4_address)
print(f"Connected to WiFi! IP Address: {ip_address}")

# mDNS setup for pico.local access
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

# HTTP server initialization using adafruit_httpserver
pool = socketpool.SocketPool(wifi.radio)
server = Server(pool)

# Route handlers - using minimal CSS framework and JSON API pattern
@server.route("/")
def main_menu(request: Request):
    """
    Serve main menu page.
    
    Args:
        request (Request): HTTP request object
        
    Returns:
        Response: Static HTML response for main menu
    """
    return Response(request, MENU_HTML, content_type="text/html")

@server.route("/blink")
def blink_control(request: Request):
    """
    Serve LED blink rate control interface.
    
    Args:
        request (Request): HTTP request object
        
    Returns:
        Response: Static HTML response for blink control
    """
    return Response(request, BLINK_HTML, content_type="text/html")

@server.route("/get_blink")
def get_blink(request: Request):
    """
    JSON API endpoint to get current blink rate.
    
    Args:
        request (Request): HTTP request object
        
    Returns:
        Response: JSON response with current blink rate
    """
    data = {"rate": blink_rate}
    return Response(request, json.dumps(data), content_type="application/json")

@server.route("/set_blink", methods=["POST"])
def set_blink(request: Request):
    """
    JSON API endpoint to update blink rate.
    
    Args:
        request (Request): HTTP POST request with JSON body containing rate
        
    Returns:
        Response: Plain text confirmation of rate update
    """
    global blink_rate
    try:
        data = json.loads(request.body)
        new_rate = int(data.get("rate", 0))
        
        # Clamp value to valid range
        blink_rate = max(0, min(100, new_rate))
        
        print(f"LED blink rate updated to: {blink_rate}")
        return Response(request, "Blink rate updated", content_type="text/plain")
    except Exception as e:
        print("Error updating blink rate:", e)
        return Response(request, f"Error updating rate: {e}", content_type="text/plain")

@server.route("/hook1")
def file_editor(request: Request):
    """
    Serve file editor interface.
    
    Args:
        request (Request): HTTP request object
        
    Returns:
        Response: Static HTML response for file editor
    """
    return Response(request, FILE_EDITOR_HTML, content_type="text/html")

@server.route("/save_file", methods=["POST"])
def save_file(request: Request):
    """
    JSON API endpoint to save file to filesystem with optional auto-reboot.
    
    Automatically reboots the Pico W when code.py is saved to enable
    live code development workflow. This allows editing and testing
    code directly through the web interface.
    
    Args:
        request (Request): HTTP POST request with JSON body containing filename and content
        
    Returns:
        Response: Plain text confirmation of file save operation
    """
    import microcontroller
    
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
        
        # Check if this is code.py - if so, prepare for auto-reboot
        if filename.lower() == "code.py":
            print("code.py saved - rebooting in 2 seconds to reload new code...")
            response = Response(request, f"File saved: {filename} - Rebooting to apply changes...", content_type="text/plain")
            
            # Schedule reboot after response (will happen in main loop)
            global reboot_scheduled
            reboot_scheduled = time.monotonic() + 2
            
            return response
        else:
            return Response(request, f"File saved: {filename}", content_type="text/plain")
        
    except OSError as e:
        error_msg = f"Cannot save file (filesystem may be read-only): {e}"
        print(f"File system error: {e}")
        return Response(request, error_msg, content_type="text/plain")
    except Exception as e:
        error_msg = f"Error saving file: {e}"
        print(error_msg)
        return Response(request, error_msg, content_type="text/plain")

@server.route("/load_file", methods=["POST"])
def load_file(request: Request):
    """
    JSON API endpoint to load file from filesystem.
    
    Args:
        request (Request): HTTP POST request with JSON body containing filename
        
    Returns:
        Response: JSON response with file content or error message
    """
    try:
        data = json.loads(request.body)
        filename = data.get("filename", "").strip()
        
        if not filename:
            return Response(request, "Filename required", content_type="text/plain")
        
        # Try to read from /lib directory first, then root directory
        filepath = f"/lib/{filename}"
        try:
            with open(filepath, 'r') as f:
                content = f.read()
        except OSError:
            # Fallback to root directory
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

# Hook route handlers for future expansion
@server.route("/hook2")
def hook2(request: Request):
    """Placeholder hook 2."""
    return Response(request, get_hook_html(2, "Hook 2"), content_type="text/html")

@server.route("/hook3")
def hook3(request: Request):
    """Placeholder hook 3."""
    return Response(request, get_hook_html(3, "Hook 3"), content_type="text/html")

@server.route("/hook4")
def hook4(request: Request):
    """Placeholder hook 4."""
    return Response(request, get_hook_html(4, "Hook 4"), content_type="text/html")

@server.route("/hook5")
def hook5(request: Request):
    """Placeholder hook 5."""
    return Response(request, get_hook_html(5, "Hook 5"), content_type="text/html")

@server.route("/hook6")
def hook6(request: Request):
    """Placeholder hook 6."""
    return Response(request, get_hook_html(6, "Hook 6"), content_type="text/html")

# Server startup and main loop
print("Starting server...")
server.start(ip_address, port=80)
print(f"Server running at http://{ip_address}")
print("Server running at http://pico.local")
print("Current LED blink rate:", blink_rate)

# Main execution loop - concurrent LED control, web server, and live development support
while True:
    try:
        # Check for scheduled reboot (enables live code development)
        # When code.py is saved via web interface, system automatically reboots
        # to reload new code, creating instant development feedback loop
        if reboot_scheduled > 0 and time.monotonic() >= reboot_scheduled:
            import microcontroller
            print("Executing scheduled reboot for code reload...")
            microcontroller.reset()
        
        # Update LED blinking (non-blocking operation)
        update_led()
        
        # Handle web requests (essential - don't forget this!)
        server.poll()
    except Exception as e:
        print("Error:", e)
        time.sleep(1)