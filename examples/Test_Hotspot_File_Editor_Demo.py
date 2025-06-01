"""
Pico 2 W Hotspot File Editor Demo
================================

Simple standalone demonstration of hotspot-served file editor with auto-reboot
functionality. Extracted from comprehensive IDE system for focused learning.

Features:
- Creates WiFi hotspot "PicoTest" 
- Serves file editor at http://192.168.4.1
- Load and save files through web interface
- Auto-reboot when code.py is saved (enables live development)
- Clean, minimal implementation for educational purposes

Hardware Requirements:
- Raspberry Pi Pico 2 W (RP2350)

Software Requirements:
- CircuitPython 9.2.7 or later
- adafruit_httpserver library

Usage:
1. Upload this code as code.py to CIRCUITPY drive
2. Connect to "PicoTest" WiFi network (no password)
3. Open browser to http://192.168.4.1
4. Use file editor to load/save files
5. Saving code.py automatically reboots Pico for testing

Author: CircuitPython Demo
License: MIT License
"""

import time
import json
import wifi
import socketpool
import ipaddress
from adafruit_httpserver import Server, Request, Response

# Configuration
HOTSPOT_SSID = "PicoTest"
HOTSPOT_IP = "192.168.4.1"
HOTSPOT_NETMASK = "255.255.255.0"
HOTSPOT_GATEWAY = "192.168.4.1"

# Global variable for scheduled reboot
reboot_scheduled = 0

def create_hotspot():
    """Create WiFi hotspot for serving the editor interface."""
    print("=== PICO 2 W FILE EDITOR DEMO ===")
    print("Creating hotspot...")
    
    try:
        # Create open WiFi hotspot
        wifi.radio.start_ap(ssid=HOTSPOT_SSID)
        
        # Configure IP addressing
        wifi.radio.set_ipv4_address_ap(
            ipv4=ipaddress.IPv4Address(HOTSPOT_IP),
            netmask=ipaddress.IPv4Address(HOTSPOT_NETMASK), 
            gateway=ipaddress.IPv4Address(HOTSPOT_GATEWAY)
        )
        
        print(f"SUCCESS: Hotspot created: {HOTSPOT_SSID}")
        print(f"SUCCESS: IP Address: {HOTSPOT_IP}")
        print("SUCCESS: Security: Open (no password)")
        return True
        
    except Exception as e:
        print(f"FAILED to create hotspot: {e}")
        return False

# Static HTML for file editor interface
EDITOR_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Pico 2 W File Editor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
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
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #333;
        }
        input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
            box-sizing: border-box;
        }
        textarea {
            width: 100%;
            height: 400px;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            font-family: 'Courier New', monospace;
            box-sizing: border-box;
            resize: vertical;
            line-height: 1.4;
        }
        .btn {
            background-color: #4CAF50;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            margin: 8px 8px 8px 0;
        }
        .btn:hover {
            background-color: #45a049;
        }
        .btn:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }
        .status {
            margin-top: 15px;
            padding: 12px;
            border-radius: 6px;
            display: none;
            font-weight: bold;
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
        .status.warning {
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .button-group {
            margin-top: 20px;
        }
        .info-box {
            background-color: #e7f3ff;
            border: 1px solid #b3d9ff;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .info-box h3 {
            margin-top: 0;
            color: #0066cc;
        }
    </style>
</head>
<body>
    <div class="editor-container">
        <h1>Pico 2 W File Editor</h1>
        
        <div class="form-group">
            <label for="filename">filename:</label>
            <input type="text" id="filename" placeholder="code.py" value="code.py">
        </div>
        
        <div class="form-group">
            <label for="filecontent">file Content:</label>
            <textarea id="filecontent" placeholder="# Enter your CircuitPython code here..."></textarea>
        </div>
        
        <div class="button-group">
            <button class="btn" onclick="saveFile()">Save File</button>
            <button class="btn" onclick="loadFile()">Load File</button>
            <button class="btn" onclick="loadCodePy()">Load code.py</button>
            <button class="btn" onclick="clearEditor()">Clear Editor</button>
        </div>
        
        <div id="status" class="status"></div>
    </div>

    <script>
        // Load code.py on page load for immediate editing
        window.onload = function() {
            document.getElementById('filename').value = 'code.py';
            loadFile();
        };
        
        function saveFile() {
            const filename = document.getElementById('filename').value.trim();
            const content = document.getElementById('filecontent').value;
            
            if (!filename) {
                showStatus('Please enter a filename', 'error');
                return;
            }
            
            // Disable save button during operation
            const saveBtn = event.target;
            saveBtn.disabled = true;
            saveBtn.textContent = 'Saving...';
            
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
                if (filename.toLowerCase() === 'code.py') {
                    showStatus('SUCCESS: code.py saved! Pico 2 W will reboot in 2 seconds to run new code...', 'warning');
                    // Show countdown
                    setTimeout(() => {
                        showStatus('Rebooting now... Reconnect to PicoTest in a moment.', 'warning');
                    }, 2000);
                } else {
                    showStatus('SUCCESS: File saved successfully: ' + filename, 'success');
                }
                console.log('File saved:', filename);
            })
            .catch(error => {
                showStatus('ERROR: Error saving file: ' + error, 'error');
                console.error('Error:', error);
            })
            .finally(() => {
                // Re-enable save button
                saveBtn.disabled = false;
                saveBtn.textContent = 'Save File';
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
                showStatus('SUCCESS: File loaded successfully: ' + filename, 'success');
                console.log('File loaded:', filename);
            })
            .catch(error => {
                showStatus('ERROR: Error loading file: ' + error, 'error');
                console.error('Error:', error);
            });
        }
        
        function loadCodePy() {
            document.getElementById('filename').value = 'code.py';
            loadFile();
        }
        
        function clearEditor() {
            document.getElementById('filename').value = 'code.py';
            document.getElementById('filecontent').value = '';
            hideStatus();
        }
        
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + type;
            status.style.display = 'block';
            
            // Auto-hide success messages after 5 seconds
            if (type === 'success') {
                setTimeout(hideStatus, 5000);
            }
        }
        
        function hideStatus() {
            document.getElementById('status').style.display = 'none';
        }
    </script>
</body>
</html>"""

# Create hotspot
if not create_hotspot():
    print("Cannot continue without hotspot. Exiting.")
    raise SystemExit

# Initialize HTTP server
pool = socketpool.SocketPool(wifi.radio)
server = Server(pool)

@server.route("/")
def editor_page(request: Request):
    """Serve the file editor interface."""
    print("Editor page requested")
    return Response(request, EDITOR_HTML, content_type="text/html")

@server.route("/save_file", methods=["POST"])
def save_file(request: Request):
    """
    Save file to filesystem with auto-reboot for code.py.
    
    When code.py is saved, automatically reboots the Pico 2 W to enable
    live development workflow.
    """
    global reboot_scheduled
    
    try:
        data = json.loads(request.body)
        filename = data.get("filename", "").strip()
        content = data.get("content", "")
        
        if not filename:
            return Response(request, "Filename required", content_type="text/plain")
        
        print(f"Saving file: {filename} ({len(content)} characters)")
        
        # Write file to filesystem
        with open(filename, 'w') as f:
            f.write(content)
        
        print(f"SUCCESS: File saved: {filename}")
        
        # Auto-reboot for code.py to enable live development
        if filename.lower() == "code.py":
            print("REBOOT: code.py saved - scheduling reboot in 2 seconds...")
            reboot_scheduled = time.monotonic() + 2
            return Response(request, f"File saved: {filename} - Rebooting to apply changes...", content_type="text/plain")
        else:
            return Response(request, f"File saved: {filename}", content_type="text/plain")
        
    except OSError as e:
        error_msg = f"Cannot save file (filesystem error): {e}"
        print(f"ERROR: {error_msg}")
        return Response(request, error_msg, content_type="text/plain")
    except Exception as e:
        error_msg = f"Error saving file: {e}"
        print(f"ERROR: {error_msg}")
        return Response(request, error_msg, content_type="text/plain")

@server.route("/load_file", methods=["POST"])
def load_file(request: Request):
    """Load file from filesystem."""
    try:
        data = json.loads(request.body)
        filename = data.get("filename", "").strip()
        
        if not filename:
            return Response(request, "Filename required", content_type="text/plain")
        
        print(f"Loading file: {filename}")
        
        # Try to read file
        try:
            with open(filename, 'r') as f:
                content = f.read()
        except OSError:
            print(f"ERROR: File not found: {filename}")
            return Response(request, "File not found", content_type="text/plain")
        
        print(f"SUCCESS: File loaded: {filename} ({len(content)} characters)")
        response_data = {"content": content}
        return Response(request, json.dumps(response_data), content_type="application/json")
        
    except Exception as e:
        error_msg = f"Error loading file: {e}"
        print(f"ERROR: {error_msg}")
        return Response(request, error_msg, content_type="text/plain")

# Start server
print("Starting web server...")
server.start(HOTSPOT_IP, port=80)
print(f"SUCCESS: Server running at http://{HOTSPOT_IP}")

print("\n" + "="*50)
print("CONNECTION INSTRUCTIONS:")
print("="*50)
print(f"1. Connect to WiFi: '{HOTSPOT_SSID}' (no password)")
print(f"2. Open browser: http://{HOTSPOT_IP}")
print("3. Use file editor to load/save files")
print("4. Saving code.py automatically reboots Pico!")
print("="*50)
print("\nLive Development Ready!")
print("Edit → Save → Auto-reboot → Test → Repeat")
print("\nPress Ctrl+C to stop server")

# Main execution loop
while True:
    try:
        # Check for scheduled reboot (live development feature)
        if reboot_scheduled > 0 and time.monotonic() >= reboot_scheduled:
            import microcontroller
            print("REBOOT: Executing scheduled reboot...")
            microcontroller.reset()
        
        # Handle web requests
        server.poll()
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        break
    except Exception as e:
        print(f"ERROR: Server error: {e}")
        time.sleep(1)

print("Goodbye!")