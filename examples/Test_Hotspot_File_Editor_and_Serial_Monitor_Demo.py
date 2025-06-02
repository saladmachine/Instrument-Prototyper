"""
Pico 2 W Hotspot File Editor + Serial Monitor Demo
=================================================
 
Complete web-based CircuitPython development environment with file editing
and serial monitor functionality. Zero-install development from any browser.

Features:
- Creates WiFi hotspot "PicoTest" 
- Serves file editor at http://192.168.4.1
- Web-based serial monitor with REPL interaction
- Load and save files through web interface
- Auto-reboot when code.py is saved (enables live development)
- Send commands and see live console output

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
5. Use serial monitor to interact with console
6. Saving code.py automatically reboots Pico for testing

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

# Global variables for scheduled reboot and console monitoring
reboot_scheduled = 0
console_buffer = []
max_buffer_size = 1000
original_print = print

def web_print(*args, **kwargs):
    """Enhanced print that captures output for web console."""
    global console_buffer
    
    # Convert args to string like normal print
    message = ' '.join(str(arg) for arg in args)
    
    # Add timestamp
    import time
    timestamp = time.monotonic()
    
    # Store in buffer with timestamp
    console_buffer.append({
        'time': timestamp,
        'message': message + '\n'
    })
    
    # Limit buffer size
    if len(console_buffer) > max_buffer_size:
        console_buffer = console_buffer[-max_buffer_size:]
    
    # Call original print
    return original_print(*args, **kwargs)

# Replace built-in print with our enhanced version
print = web_print

def create_hotspot():
    """Create WiFi hotspot for serving the editor interface."""
    print("=== PICO 2 W FILE EDITOR + SERIAL MONITOR ===")
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

# Static HTML for file editor + serial monitor interface (UPDATED WITH TABS)
EDITOR_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Pico 2 W IDE</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .tab-container {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .tabs {
            display: flex;
            background-color: #f8f9fa;
            border-bottom: 1px solid #ddd;
        }
        .tab {
            flex: 1;
            padding: 15px 20px;
            cursor: pointer;
            text-align: center;
            font-weight: bold;
            border: none;
            background: none;
            transition: background-color 0.3s;
        }
        .tab.active {
            background-color: white;
            border-bottom: 2px solid #4CAF50;
        }
        .tab:hover:not(.active) {
            background-color: #e9ecef;
        }
        .tab-content {
            display: none;
            padding: 30px;
        }
        .tab-content.active {
            display: block;
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
        .terminal {
            width: 100%;
            height: 400px;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            font-family: 'Courier New', monospace;
            box-sizing: border-box;
            background-color: #000;
            color: #00ff00;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .command-input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            font-family: 'Courier New', monospace;
            box-sizing: border-box;
            margin-top: 10px;
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
        .btn.danger {
            background-color: #f44336;
        }
        .btn.danger:hover {
            background-color: #da190b;
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
        .serial-controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .serial-status {
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 10px;
            font-weight: bold;
        }
        .connected {
            background-color: #d4edda;
            color: #155724;
        }
        .disconnected {
            background-color: #f8d7da;
            color: #721c24;
        }
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            .tab-content {
                padding: 20px;
            }
            .serial-controls {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Pico 2 W Development Environment</h1>
        
        <div class="tab-container">
            <div class="tabs">
                <button class="tab active" onclick="openTab(event, 'editor')">File Editor</button>
                <button class="tab" onclick="openTab(event, 'serial')">Console Monitor</button>
            </div>
            
            <!-- File Editor Tab - EXACT COPY OF WORKING VERSION -->
            <div id="editor" class="tab-content active">
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
            
            <!-- Console Monitor Tab - NEW -->
            <div id="serial" class="tab-content">
                <div id="serial-status" class="serial-status disconnected">
                    Console Monitor: Stopped
                </div>
                
                <div class="serial-controls">
                    <button class="btn" onclick="connectSerial()">Start Monitoring</button>
                    <button class="btn" onclick="disconnectSerial()">Stop Monitoring</button>
                    <button class="btn" onclick="sendCtrlC()">Interrupt Code</button>
                    <button class="btn danger" onclick="clearTerminal()">Clear Display</button>
                </div>
                
                <div class="form-group">
                    <label for="terminal">Console Output:</label>
                    <div id="terminal" class="terminal">Click "Start Monitoring" to see console output...\n</div>
                </div>
                
                <div class="form-group">
                    <label for="command-input">Execute Python Command:</label>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <input type="text" id="command-input" class="command-input" 
                               style="flex: 1; min-width: 200px;"
                               placeholder="Type Python command (e.g., print('hello'))" 
                               onkeypress="handleCommandInput(event)">
                        <button class="btn" onclick="sendCommand()" style="white-space: nowrap;">Send</button>
                    </div>
                    
                    <div style="margin-top: 10px; display: flex; gap: 5px; flex-wrap: wrap;">
                        <button class="btn" onclick="quickCommand('help()')" style="font-size: 12px; padding: 6px 12px;">help()</button>
                        <button class="btn" onclick="quickCommand('import board; dir(board)')" style="font-size: 12px; padding: 6px 12px;">board pins</button>
                        <button class="btn" onclick="quickCommand('import gc; gc.mem_free()')" style="font-size: 12px; padding: 6px 12px;">free memory</button>
                        <button class="btn" onclick="quickCommand('import time; time.monotonic()')" style="font-size: 12px; padding: 6px 12px;">uptime</button>
                    </div>
                </div>
                
                <div id="serial-status-msg" class="status"></div>
            </div>
        </div>
    </div>

    <script>
        let consoleUpdateInterval = null;
        let lastConsoleLength = 0;
        
        // Load code.py on page load for immediate editing - EXACT COPY
        window.onload = function() {
            document.getElementById('filename').value = 'code.py';
            loadFile();
        };
        
        // Tab switching - NEW
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].classList.remove("active");
            }
            tablinks = document.getElementsByClassName("tab");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].classList.remove("active");
            }
            document.getElementById(tabName).classList.add("active");
            evt.currentTarget.classList.add("active");
        }
        
        // File Editor Functions - EXACT COPY OF WORKING VERSION
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
        
        // Console Monitor Functions - NEW
        async function connectSerial() {
            // Start polling for console updates
            if (consoleUpdateInterval) {
                clearInterval(consoleUpdateInterval);
            }
            
            consoleUpdateInterval = setInterval(updateConsole, 500); // Update every 500ms
            updateSerialStatus(true);
            showSerialStatus('Console monitoring started', 'success');
            
            // Initial load
            updateConsole();
        }
        
        async function disconnectSerial() {
            if (consoleUpdateInterval) {
                clearInterval(consoleUpdateInterval);
                consoleUpdateInterval = null;
            }
            
            updateSerialStatus(false);
            showSerialStatus('Console monitoring stopped', 'warning');
        }
        
        async function updateConsole() {
            try {
                const response = await fetch('/get_console');
                if (!response.ok) throw new Error('Failed to get console data');
                
                const consoleData = await response.json();
                
                // Only update if there's new content
                if (consoleData.length !== lastConsoleLength) {
                    const terminal = document.getElementById('terminal');
                    
                    // Build console text
                    let consoleText = '';
                    consoleData.forEach(entry => {
                        consoleText += entry.message;
                    });
                    
                    terminal.textContent = consoleText;
                    terminal.scrollTop = terminal.scrollHeight;
                    lastConsoleLength = consoleData.length;
                }
            } catch (error) {
                showSerialStatus('Error updating console: ' + error.message, 'error');
            }
        }
        
        async function sendCommand() {
            const input = document.getElementById('command-input');
            const command = input.value.trim();
            
            if (!command) return;
            
            try {
                await fetch('/send_command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: command })
                });
                
                input.value = '';
                // Force console update
                setTimeout(updateConsole, 100);
                
            } catch (error) {
                showSerialStatus('Error sending command: ' + error.message, 'error');
            }
        }
        
        async function sendCtrlC() {
            try {
                print("=== INTERRUPT REQUESTED ===")
                showSerialStatus('Interrupt signal sent', 'success');
                setTimeout(updateConsole, 100);
            } catch (error) {
                showSerialStatus('Error sending interrupt: ' + error.message, 'error');
            }
        }
        
        function clearTerminal() {
            document.getElementById('terminal').textContent = '';
        }
        
        function handleCommandInput(event) {
            if (event.key === 'Enter') {
                sendCommand();
            }
        }
        
        function quickCommand(cmd) {
            document.getElementById('command-input').value = cmd;
            sendCommand();
        }
        
        function updateSerialStatus(connected) {
            const statusDiv = document.getElementById('serial-status');
            if (connected) {
                statusDiv.textContent = 'Console Monitor: Active';
                statusDiv.className = 'serial-status connected';
            } else {
                statusDiv.textContent = 'Console Monitor: Stopped';
                statusDiv.className = 'serial-status disconnected';
            }
        }
        
        function showSerialStatus(message, type) {
            const status = document.getElementById('serial-status-msg');
            status.textContent = message;
            status.className = 'status ' + type;
            status.style.display = 'block';
            if (type === 'success') setTimeout(() => status.style.display = 'none', 3000);
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
    """Serve the file editor + serial monitor interface."""
    print("IDE page requested")
    return Response(request, EDITOR_HTML, content_type="text/html")

# File Editor Routes - EXACT COPY OF WORKING VERSION
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

# Console Monitor Routes - NEW
@server.route("/get_console")
def get_console(request: Request):
    """Get console output for web display."""
    try:
        # Return console buffer as JSON
        return Response(request, json.dumps(console_buffer), content_type="application/json")
    except Exception as e:
        return Response(request, f"Error getting console: {e}", content_type="text/plain")

@server.route("/send_command", methods=["POST"])
def send_command(request: Request):
    """Execute Python command and capture output."""
    try:
        data = json.loads(request.body)
        command = data.get("command", "").strip()
        
        if not command:
            return Response(request, "Command required", content_type="text/plain")
        
        print(f">>> {command}")  # Show command in console
        
        try:
            # Execute the command
            result = eval(command)
            if result is not None:
                print(repr(result))
        except Exception as e:
            print(f"Error: {e}")
        
        return Response(request, "Command executed", content_type="text/plain")
        
    except Exception as e:
        print(f"Error executing command: {e}")
        return Response(request, f"Error: {e}", content_type="text/plain")

# Start server
print("Starting web server...")
server.start(HOTSPOT_IP, port=80)
print(f"SUCCESS: Server running at http://{HOTSPOT_IP}")

print("\n" + "="*60)
print("CONNECTION INSTRUCTIONS:")
print("="*60)
print(f"1. Connect to WiFi: '{HOTSPOT_SSID}' (no password)")
print(f"2. Open browser: http://{HOTSPOT_IP}")
print("3. File Editor tab: Load/save files (WORKING VERSION)")
print("4. Console Monitor tab: See live console output")
print("5. Saving code.py automatically reboots Pico!")
print("="*60)
print("\nComplete Development Environment Ready!")
print("Edit → Save → Auto-reboot → Monitor → Debug → Repeat")
print("\nPress Ctrl+C to stop server")

# Main execution loop
while True:
    try:
        # Check for scheduled reboot
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