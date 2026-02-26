import socket
import time

# ----------------------------
# Motor IP configuration
# ----------------------------
MOTOR_IPS = [
    "192.168.1.20",  # Motor with switch at '2'
    "192.168.1.10",  # Motor with switch at '1'
    "192.168.1.30",  # Motor with switch at '3'
    "192.168.0.40",  # Motor with switch at '4'
]

PORT = 7776          # ⚠️ Most Applied Motion drives use 7776 (verify!)
TIMEOUT = 0.5

# ----------------------------
# ADC / Analog parameters
# ----------------------------
ADC_MAX = 4095
VREF = 5.0
SAMPLE_PERIOD = 0.05

# ----------------------------
# Create socket connections
# ----------------------------
sockets = {}

for ip in MOTOR_IPS:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        s.connect((ip, PORT))
        sockets[ip] = s
        print(f"✅ Connected to {ip}")
    except Exception as e:
        print(f"❌ Failed to connect to {ip}: {e}")

# ----------------------------
# Command helper
# ----------------------------
def request_ain(sock):
    try:
        sock.sendall(b"AI\r")
        response = sock.recv(64).decode().strip()
        return int(response)
    except Exception:
        return None

# ----------------------------
# Continuous monitoring loop
# ----------------------------
try:
    while True:
        for ip, sock in sockets.items():
            ain = request_ain(sock)

            if ain is None:
                print(f"{ip} | ⚠️ No response")
                continue

            voltage = (ain / ADC_MAX) * VREF

            print(f"{ip} | AIN: {ain:4d} | Voltage: {voltage:.3f} V")

        print("-" * 60)
        time.sleep(SAMPLE_PERIOD)

except KeyboardInterrupt:
    print("\nMonitoring stopped.")

finally:
    for sock in sockets.values():
        sock.close()
