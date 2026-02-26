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

def parse_numeric(response: str):
    """Return first numeric token as int/float, else None."""
    m = _num_pat.search(response)
    if not m:
        return None
    token = m.group(0)
    return int(token) if token.lstrip("+-").isdigit() else float(token)

def recv_all_available(sock, max_bytes=512):
    """
    Read what the drive has ready right now.
    Many drives reply with:
      "+"                (ack)
      "+\r\n"            (ack + newline)
      "+\r\n24567\r\n"   (ack + data)
      "24567\r\n"        (data only)
    """
    chunks = []
    try:
        data = sock.recv(max_bytes)
        if not data:
            return ""
        chunks.append(data)
        # Non-blocking drain (best-effort)
        sock.settimeout(0.01)
        while True:
            try:
                more = sock.recv(max_bytes)
                if not more:
                    break
                chunks.append(more)
            except socket.timeout:
                break
    finally:
        sock.settimeout(TIMEOUT)
    return b"".join(chunks).decode(errors="replace").strip()

def send_scl(sock, cmd):
    sock.sendall((cmd + "\r").encode())
    return recv_all_available(sock)

# ----------------------------
# Connection + format setup
# ----------------------------
sockets = {}

for ip in MOTOR_IPS:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        s.connect((ip, PORT))

        # 1) Send IFD (format decimal)
        ifd_resp = send_scl(s, "IFD")

        # IF/THEN for IFD response: it may return "+" OR nothing OR some text
        if ifd_resp == "" or ifd_resp.startswith("+"):
            print(f"✅ Connected {ip} | IFD OK (resp: {ifd_resp!r})")
        else:
            print(f"✅ Connected {ip} | ⚠️ Unexpected IFD resp: {ifd_resp!r}")

        sockets[ip] = s
    except Exception as e:
        print(f"❌ Failed to connect to {ip}: {e}")

# ----------------------------
# Command helper: rely on IFD then IA1
# ----------------------------
def request_ain_ifd_then_ia1(sock, channel=1):
    """
    Reliably do:
      IFD  -> check ack/empty
      IA1  -> parse either data-only OR ack+data
    Returns (ain_value, debug_dict) where ain_value is int/float or None.
    """
    debug = {}

    # --- Step 1: IFD ---
    ifd_resp = send_scl(sock, "IFD")
    debug["ifd_resp"] = ifd_resp

    # IF/THEN #1: IFD response variants
    if ifd_resp == "" or ifd_resp.startswith("+"):
        debug["ifd_ok"] = True
    else:
        debug["ifd_ok"] = False
        # Still proceed; some firmwares respond oddly but still set format.

    # --- Step 2: IA1 ---
    ia_resp = send_scl(sock, f"IA{channel}")
    debug["ia_resp_raw"] = ia_resp

    # IF/THEN #2: IA response may be:
    #   "24567"              (data only)
    #   "+\r\n24567"         (ack + data)
    #   "IA1=24567"          (tagged)
    #   "+\r\nIA1=24567"     (ack + tagged)
    # We'll branch based on whether it starts with "+".
    if ia_resp.startswith("+"):
        debug["ia_had_ack"] = True
        # Strip leading '+' and any whitespace/newlines before parsing
        cleaned = ia_resp.lstrip("+").strip()
    else:
        debug["ia_had_ack"] = False
        cleaned = ia_resp.strip()

    debug["ia_resp_cleaned"] = cleaned

    ain = parse_numeric(cleaned)
    debug["ain_parsed"] = ain

    return ain, debug

# ----------------------------
# Continuous monitoring loop
# ----------------------------
try:
    while True:
        for ip, sock in sockets.items():
            ain, dbg = request_ain_ifd_then_ia1(sock, channel=1)

            if ain is None:
                print(f"{ip} | ⚠️ Parse failed | IFD resp={dbg.get('ifd_resp')!r} | IA resp={dbg.get('ia_resp_raw')!r}")
                continue

            voltage = (float(ain) / ADC_MAX) * VREF
            # Show which branch happened (ack+data vs data-only)
            branch = "ACK+DATA" if dbg.get("ia_had_ack") else "DATA-ONLY"
            print(f"{ip} | ({branch}) IA1: {ain} | Voltage: {voltage:.3f} V")

        print("-" * 60)
        time.sleep(SAMPLE_PERIOD)

except KeyboardInterrupt:
    print("\nMonitoring stopped.")

finally:
    for sock in sockets.values():
        sock.close()
