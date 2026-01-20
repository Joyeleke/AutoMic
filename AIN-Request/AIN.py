import serial
import time

# ----------------------------
# Serial configuration
# ----------------------------
PORT = "COM3"        # Change to your port (e.g. /dev/ttyUSB0)
BAUDRATE = 9600      # Must match drive settings, Baudrate is in bits per second for communication speed between computer and motor.
TIMEOUT = 0.5

# ----------------------------
# ADC / Analog parameters
# ----------------------------
ADC_MAX = 4095       # 12-bit ADC
VREF = 5.0           # Reference voltage (volts)
SAMPLE_PERIOD = 0.05 # 50 ms update rate

# ----------------------------
# Open serial connection
# ----------------------------
ser = serial.Serial(
    port=PORT,
    baudrate=BAUDRATE,
    timeout=TIMEOUT
)

time.sleep(0.5)  # Allow drive to initialize

# ----------------------------
# Command helper
# ----------------------------
def request_ain():
    ser.write(b"AI\r")              # Request analog input
    response = ser.readline().decode().strip()
    return int(response)

# ----------------------------
# Continuous monitoring loop
# ----------------------------
try:
    while True:
        ain = request_ain()
        voltage = (ain / ADC_MAX) * VREF

        print(f"AIN: {ain:4d}  |  Voltage: {voltage:.3f} V")

        time.sleep(SAMPLE_PERIOD)

except KeyboardInterrupt:
    print("\nMonitoring stopped.")

finally:
    ser.close()
