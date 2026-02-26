import socket
import time
import threading

# --- Configuration ---
MOTOR_IPS = [
    "192.168.1.20", # Motor 1
]

# --- Motion Parameters ---
ACCEL_RATE = 100.0
DECEL_RATE = 100.0
MAX_VELOCITY = 5.0

# --- SCL TCP Motor Class ---
class SCL_Motor:
    """A class to communicate with an Applied Motion drive using the eSCL TCP protocol."""
    HEADER_BYTES = b'\x00\x07'
    TERMINATOR_BYTE = b'\x0d'

    def __init__(self, ip, port=7776, timeout=5.0):
        self.drive_address = (ip, port)
        self.timeout = timeout
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __enter__(self):
        """Connects the socket for communication."""
        self.socket.settimeout(self.timeout)
        self.socket.connect(self.drive_address)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes the socket."""
        self.socket.close()

    def send_command(self, command: str) -> str | None:
        """Sends a single SCL command and returns the response."""
        try:
            packet = command.encode('ascii')
            full_packet = self.HEADER_BYTES + packet + self.TERMINATOR_BYTE
            self.socket.sendall(full_packet)
            
            data = self.socket.recv(1024)
            if not data:
                print(f"!!! No response from {self.drive_address[0]} for command '{command}'")
                return None

            payload = data[len(self.HEADER_BYTES):-len(self.TERMINATOR_BYTE)]
            response = payload.decode('ascii').strip()
            print(f"Sent '{command}' to {self.drive_address[0]} -> Received: '{response}'")
            return response
        except socket.timeout:
            print(f"!!! Timeout on {self.drive_address[0]} for command '{command}'")
            return None

# --- Command Generators ---
def configure_motor_for_tension_sensor():
    """Generates a command list to configure the motor for tension sensor."""
    return ["AS3", "IFD"]

def poll_potentiometer():
    """Generates a command list to poll the potentiometer."""
    return ["IA"]

def monitor_tension_sensor(ip_address, poll_rate_seconds=0.5):
    """Configures the analog input and continuously reads the voltage."""
    print(f"Tension monitoring thread for {ip_address} starting...")
    
    try:
        with SCL_Motor(ip_address) as motor:
            
            config_commands = configure_motor_for_tension_sensor()
            for cmd in config_commands:
                motor.send_command(cmd)
                
            print(f"--> {ip_address} configured. Starting continuous poll.")
            
            poll_commands = poll_potentiometer()
            
            while True:
                for cmd in poll_commands:
                    response = motor.send_command(cmd)
                    
                    print(f"[{ip_address}] Response: {response}")

                    if response and "=" in response:
                        try:
                            voltage_str = response.split('=')[1]
                            voltage = float(voltage_str)
                            print(f"[{ip_address}] Voltage: {voltage} V")
                        except ValueError:
                            print(f"[{ip_address}] Parse error: {response}")
                    else:
                        print(f"[{ip_address}] Unexpected response: {response}")
                
                time.sleep(poll_rate_seconds)

    except Exception as e:
        print(f"An error occurred in thread for {ip_address}: {e}")

if __name__ == "__main__":
    threads = []
    
    try:
        for ip in MOTOR_IPS:
            thread = threading.Thread(
                target=monitor_tension_sensor, 
                args=(ip, 0.5) 
            )
            thread.daemon = True 
            threads.append(thread)
            thread.start()

        print("All sensor monitoring threads started. Press Ctrl+C to stop.\n")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nProgram terminated by user.")

  