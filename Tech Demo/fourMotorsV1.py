import socket
import time
import threading

# --- Configuration ---
MOTOR_IPS = [
    "192.168.1.20", # Motor with switch at '2'
    "192.168.1.10", # Motor with switch at '1'
    "192.168.1.30", # Motor with switch at '3'
    "192.168.0.40",  # Motor with switch at '4'
]
LOCAL_PORT_START = 7777 

# --- Motion Parameters ---
ACCEL_RATE = 100.0
DECEL_RATE = 100.0
MAX_VELOCITY = 5.0

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

def control_single_motor(ip_address, target_position):
    """The function that each thread will run to control one motor."""
    print(f"Thread for motor {ip_address} starting...")
    
    scl_commands = [
        "ME", f"AC{ACCEL_RATE}", f"DE{DECEL_RATE}", 
        f"VE{MAX_VELOCITY}", f"DI{target_position}"
    ]
    
    try:
        with SCL_Motor(ip_address) as motor:
            for cmd in scl_commands:
                if motor.send_command(cmd) is None:
                    print(f"!!! Failed to configure motor {ip_address}. Thread exiting.")
                    return
            
            motor.send_command("FL")
            print(f"--> Move command sent successfully to {ip_address}.")

    except Exception as e:
        print(f"An error occurred in thread for {ip_address}: {e}")

if __name__ == "__main__":
    try:
        target_positions = []
        for i, ip in enumerate(MOTOR_IPS):
            pos_input = input(f"Enter the target absolute position for motor {i + 1} ({ip}): ")
            target_positions.append(int(pos_input))

        threads = []
        for i, ip in enumerate(MOTOR_IPS):
            thread = threading.Thread(
                target=control_single_motor, 
                args=(ip, target_positions[i])
            )
            threads.append(thread)
            thread.start()

        print("\nAll motor control threads have been started.")

        for thread in threads:
            thread.join()

        print("\nAll threads have finished execution.")

    except ValueError:
        print("Invalid input. Please enter an integer.")
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")