import socket
import time
import re

# ----------------------------
# Motor IP configuration
# ----------------------------
MOTOR_IPS = [
    "192.168.1.20",  # Motor with switch at '2'
    "192.168.1.10",  # Motor with switch at '1'
    "192.168.1.30",  # Motor with switch at '3'
    "192.168.0.40",  # Motor with switch at '4'
]

PORT = 7776          # Common for Applied Motion SCL over Ethernet (verify for your setup)
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
# Parsing helper
# ----------------------------
_num_pat = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")

def parse_numeric(response: str):
    """
    Drives may respond with:
      "2048"
      "IA=2048"
      "IA1=2048"
      "2048\r\n"
    This extracts the first numeric token.
    """
    m = _num_pat.search(response)
    if not m:
        return None
    token = m.group(0)
    # Prefer int if it looks like an int, else float
    return int(token) if token.isdigit() or (token.startswith(("+", "-")) and token[1:].isdigit()) else float(token)

# ----------------------------
# Command helper (IA)
# ----------------------------
def request_ain(sock, channel=1, raw=True):
    """
    For SSM23Q/IP, analog input is read via IA.
    - raw=True uses IA<channel> (often returns raw ADC counts)
    - raw=False uses IA (often returns scaled analog command, model/config dependent)
    """
    try:
        cmd = f"IA{channel}" if raw else "IA"
        sock.sendall((cmd + "\r").encode())

        # Read a chunk; most drives reply in a single short line.
        response = sock.recv(128).decode(errors="replace").strip()
        val = parse_numeric(response)
        return val
    except Exception:
        return None

# ----------------------------
# Continuous monitoring loop
# ----------------------------
try:
    while True:
        for ip, sock in sockets.items():
            # Most common: IA1 gives raw counts. If yours uses a different channel, change channel=1.
            ain = request_ain(sock, channel=1, raw=True)

            if ain is None:
                print(f"{ip} | ⚠️ No response / parse failed")
                continue

            # If IA1 returns raw ADC counts, this conversion is correct:
            # voltage = (count / ADC_MAX) * VREF
            if isinstance(ain, (int, float)):
                voltage = (float(ain) / ADC_MAX) * VREF
                print(f"{ip} | IA1: {ain} | Voltage: {voltage:.3f} V")
            else:
                print(f"{ip} | IA1: {ain} | Voltage: N/A")

        print("-" * 60)
        time.sleep(SAMPLE_PERIOD)

except KeyboardInterrupt:
    print("\nMonitoring stopped.")

finally:
    for sock in sockets.values():
        sock.close()
