# Initialize LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = False

# Static HTML with button - no dynamic generation
STATIC_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Pico W LED Control</title>
</head>
<body>
    <h1>Pico W LED Control</h1>
    <p>Click the button to toggle the LED</p>
    <form action="/toggle" method="post">
        <button type="submit">Toggle LED</button>
    </form>
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
    """Serve static HTML page with button."""
    return Response(request, STATIC_HTML, content_type="text/html")

@server.route("/toggle", methods=["POST"])
def toggle_led(request: Request):
    """Toggle LED and return to main page."""
    led.value = not led.value
    led_state = "ON" if led.value else "OFF"
    print(f"LED toggled to: {led_state}")
    
    # Return the same static HTML page
    return Response(request, STATIC_HTML, content_type="text/html")

# Start server
print("Starting server...")
server.start(ip_address, port=80)
print(f"Server running at http://{ip_address}")
print("Server running at http://pico.local")

# Keep the server running
while True:
    try:
        server.poll()
    except Exception as e:
        print("Error:", e)
        time.sleep(1)