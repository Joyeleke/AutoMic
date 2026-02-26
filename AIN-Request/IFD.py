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

PORT = 7776
TIMEOUT = 0.5

# ----------------------------
# ADC / Analog parameters
# ----------------------------
ADC_MAX = 32760
VREF = 5.0
SAMPLE_PERIOD = 0.05

# ----------------------------
# Parsing helper
# ----------------------------
_num_pat = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")

def parse_decimal_number(response: str):
    """
    Assumes IFD is set, so the numeric value is decimal.
    Response may still include '+' ack or tags; we just extract the first number.
    """
    m = _num_pat.search(response)
    if not m:
        return None
    token = m.group(0)
    return int(token) if token.lstrip("+-").isdigit() else float(token)

# ----------------------------
# Socket helpers
# ----------------------------
def send_scl(sock, cmd, recv_bytes=256):
    sock.sendall((cmd + "\r").encode())
    data = sock.recv(recv_bytes)
    return data.decode(errors="replace").strip()

# ----------------------------
# Create socket connections + set IFD once
# ----------------------------
sockets = {}

for ip in MOTOR_IPS:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        s.connect((ip, PORT))

        # Set decimal format ONCE per connection
        _ = send_scl(s, "IFD")
        print(f"✅ Connected to {ip} | IFD set")

        sockets[ip] = s
    except Exception as e:
        print(f"❌ Failed to connect to {ip}: {e}")

# ----------------------------
# Command helper: IA1 only (IFD already set)
# ----------------------------
def request_ain(sock):
    """
    Assumes IFD has already been sent successfully.
    Reads Analog Input 1 via IA1 and returns a decimal number (raw counts).
    """
    try:
        resp = send_scl(sock, "IA1")
        return parse_decimal_number(resp)
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
                print(f"{ip} | ⚠️ No response / parse failed")
                continue

            voltage = (float(ain) / ADC_MAX) * VREF
            print(f"{ip} | IA1: {ain} | Voltage: {voltage:.3f} V")

        print("-" * 60)
        time.sleep(SAMPLE_PERIOD)

except KeyboardInterrupt:
    print("\nMonitoring stopped.")

finally:
    for sock in sockets.values():
        sock.close()
