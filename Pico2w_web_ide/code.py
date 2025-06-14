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

Known Issues:
⚠️  Chrome Browser Quirk: Due to Chrome's aggressive form history feature, 
the "Clear Editor" button may not fully clear the filename field in Chrome browsers. 
This is a known Chrome behavior that ignores JavaScript attempts to clear certain 
form fields. The feature works correctly in other browsers like Samsung Browser, 
Firefox, and Safari. As a workaround in Chrome, manually delete the filename 
text before entering a new filename to avoid accidentally overwriting files.

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

def add_to_console(message):
    """Add message to console buffer."""
    global console_buffer
    console_buffer.append({
        'time': time.monotonic(),
        'message': str(message) + '\n'
    })
    if len(console_buffer) > max_buffer_size:
        console_buffer = console_buffer[-max_buffer_size:]

def create_hotspot():
    """Create WiFi hotspot for serving the editor interface."""
    print("=== PICO 2 W FILE EDITOR + SERIAL MONITOR ===")
    add_to_console("=== PICO 2 W FILE EDITOR + SERIAL MONITOR ===")
    print("Creating hotspot...")
    add_to_console("Creating hotspot...")
    
    try:
        wifi.radio.start_ap(ssid=HOTSPOT_SSID)
        wifi.radio.set_ipv4_address_ap(
            ipv4=ipaddress.IPv4Address(HOTSPOT_IP),
            netmask=ipaddress.IPv4Address(HOTSPOT_NETMASK), 
            gateway=ipaddress.IPv4Address(HOTSPOT_GATEWAY)
        )
        
        message = f"SUCCESS: Hotspot created: {HOTSPOT_SSID}"
        print(message)
        add_to_console(message)
        message = f"SUCCESS: IP Address: {HOTSPOT_IP}"
        print(message)
        add_to_console(message)
        message = "SUCCESS: Security: Open (no password)"
        print(message)
        add_to_console(message)
        return True
        
    except Exception as e:
        message = f"FAILED to create hotspot: {e}"
        print(message)
        add_to_console(message)
        return False

def load_html_template():
    """Load the HTML template from file."""
    try:
        with open('index.html', 'r') as f:
            return f.read()
    except OSError:
        return "<html><body><h1>Error: index.html not found</h1><p>Please ensure index.html is uploaded to the Pico 2 W</p></body></html>"

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
    return Response(request, load_html_template(), content_type="text/html")

@server.route("/styles.css")
def serve_css(request: Request):
    """Serve the CSS file."""
    try:
        with open('styles.css', 'r') as f:
            return Response(request, f.read(), content_type="text/css")
    except OSError:
        return Response(request, "/* CSS file not found */", content_type="text/css")

@server.route("/save_file", methods=["POST"])
def save_file(request: Request):
    """Save file to filesystem with auto-reboot for code.py."""
    global reboot_scheduled
    
    try:
        data = json.loads(request.body)
        filename = data.get("filename", "").strip()
        content = data.get("content", "")
        
        if not filename:
            return Response(request, "Filename required", content_type="text/plain")
        
        with open(filename, 'w') as f:
            f.write(content)
        
        print(f"SUCCESS: File saved: {filename}")
        
        if filename.lower() == "code.py":
            print("REBOOT: code.py saved - scheduling reboot in 2 seconds...")
            reboot_scheduled = time.monotonic() + 2
            return Response(request, f"File saved: {filename} - Rebooting to apply changes...", content_type="text/plain")
        else:
            return Response(request, f"File saved: {filename}", content_type="text/plain")
        
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
        
        try:
            with open(filename, 'r') as f:
                content = f.read()
        except OSError:
            return Response(request, "File not found", content_type="text/plain")
        
        print(f"SUCCESS: File loaded: {filename}")
        return Response(request, json.dumps({"content": content}), content_type="application/json")
        
    except Exception as e:
        return Response(request, f"Error loading file: {e}", content_type="text/plain")

@server.route("/get_console")
def get_console(request: Request):
    """Get console output for web display."""
    try:
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
        
        cmd_msg = f">>> {command}"
        print(cmd_msg)
        add_to_console(cmd_msg)
        
        try:
            result = eval(command)
            if result is not None:
                result_msg = repr(result)
                print(result_msg)
                add_to_console(result_msg)
        except Exception as e:
            error_msg = f"Error: {e}"
            print(error_msg)
            add_to_console(error_msg)
        
        return Response(request, "Command executed", content_type="text/plain")
        
    except Exception as e:
        return Response(request, f"Error: {e}", content_type="text/plain")

# NOTE: TODO make directories accessible
@server.route("/list_files")
def list_files(request: Request):
   """List all files in the filesystem."""
   try:
       import os
       files = []
       
       for filename in os.listdir('/'):
           try:
               stat = os.stat('/' + filename)
               is_directory = (stat[0] & 0x4000) != 0
               if is_directory:
                   continue  # Skip directories, only show files
               files.append({'name': filename, 'size': stat[6]})
           except:
               pass
       
       files.sort(key=lambda x: x['name'])
       return Response(request, json.dumps(files), content_type="application/json")
       
   except Exception as e:
       return Response(request, f"Error: {e}", content_type="text/plain")

@server.route("/delete_file", methods=["POST"])
def delete_file(request: Request):
    """Delete a file from the filesystem."""
    try:
        data = json.loads(request.body)
        filename = data.get("filename", "").strip()
        
        if not filename:
            return Response(request, "Filename required", content_type="text/plain")
        
        if filename.lower() == "code.py":
            return Response(request, "Cannot delete code.py (currently running)", content_type="text/plain")
        
        import os
        os.remove(filename)
        print(f"File deleted: {filename}")
        return Response(request, "File deleted", content_type="text/plain")
        
    except Exception as e:
        return Response(request, f"Error: {e}", content_type="text/plain")

@server.route("/create_file", methods=["POST"])
def create_file(request: Request):
    """Create a new empty file."""
    try:
        data = json.loads(request.body)
        filename = data.get("filename", "").strip()
        
        if not filename:
            return Response(request, "Filename required", content_type="text/plain")
        
        with open(filename, 'w') as f:
            f.write('# New file\n')
        
        print(f"File created: {filename}")
        return Response(request, "File created", content_type="text/plain")
        
    except Exception as e:
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
print("3. File Editor tab: Load/save files")
print("4. Console Monitor tab: See live console output")
print("5. Saving code.py automatically reboots Pico!")
print("="*60)
print("\nComplete Development Environment Ready!")

# Main execution loop
while True:
    try:
        if reboot_scheduled > 0 and time.monotonic() >= reboot_scheduled:
            import microcontroller
            print("REBOOT: Executing scheduled reboot...")
            microcontroller.reset()
        
        server.poll()
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        break
    except Exception as e:
        print(f"ERROR: Server error: {e}")
        time.sleep(1)

print("Goodbye!")
