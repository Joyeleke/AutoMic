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

# --- Predefined Command Sequences ---
def move_absolute(position, speed, accel, decel):
    """Generates a command list for an absolute move."""
    return [
        "ME",  # Motion Enabled
        f"AC{accel}",
        f"DE{decel}",
        f"VE{speed}",
        f"DI{position}",
        "FP"  # Feed to Position
    ]
    
def move_relative(position, speed, accel, decel):
    """Generates a command list for an absolute move."""
    return [
        "ME",  # Motion Enabled
        f"AC{accel}",
        f"DE{decel}",
        f"VE{speed}",
        f"DI{position}",
        "FL"  # Feed to Length
    ]

def get_status():
    """Generates a command list to get the drive status."""
    return ["RS"]

# COMMAND_BANK = {
#     "1": {
#         "name": "Move to Absolute Position",
#         "function": move_absolute,
#         "requires_input": True,
#         "prompt_position": "Enter the target absolute position: ",
#         "prompt_speed": "Enter the motor speed: ",
#         "prompt_accel": "Enter the rate of acceleration: ",
#         "prompt_decel": "Enter the rate of deceleration: "
#     },
#     "2": {
#         "name": "Move to Relative Position",
#         "function": move_relative,
#         "requires_input": True,
#         "prompt_position": "Enter the target absolute position: ",
#         "prompt_speed": "Enter the motor speed: ",
#         "prompt_accel": "Enter the rate of acceleration: ",
#         "prompt_decel": "Enter the rate of deceleration: "
#     },
#     "3": {
#         "name": "Get Drive Status",
#         "function": get_status,
#         "requires_input": False
#     }
# }

def control_single_motor(ip_address, commands):
    """The function that each thread will run to control one motor."""
    print(f"Thread for motor {ip_address} starting...")
    
    try:
        with SCL_Motor(ip_address) as motor:
            for cmd in commands:
                if motor.send_command(cmd) is None:
                    print(f"!!! Command '{cmd}' failed for motor {ip_address}.")
                    # Decide if you want to stop or continue on failure
                    # return 
            print(f"--> All commands sent successfully to {ip_address}.")

    except Exception as e:
        print(f"An error occurred in thread for {ip_address}: {e}")

if __name__ == "__main__":
    try:
        # motor_commands = []
        # for i, ip in enumerate(MOTOR_IPS):
        #     _print(f"\n--- Select a command for motor {i + 1} ({ip}) ---")
        #     for key, value in COMMAND_BANK.items():
        #         print(f"{key}: {value['name']}")
            
        #     choice = input("Enter your choice: ")
            
        #     if choice in COMMAND_BANK:
        #         commandinfo = COMMAND_BANK[choice]
        #         commands = []
        #         if command_info["requires_input"]:
        #             position = input(command_info["prompt_position"])
        #             speed = input(command_info["prompt_speed"])
        #             accel = input(command_info["prompt_accel"])
        #             decel = input(command_info["prompt_decel"])
        #             commands = command_info["function"](position, speed, accel, decel)
        #         else:
        #             commands = command_info["function"]()
                
        #         motor_commands.append(commands)
        #     else:
        #         print("Invalid choice. Skipping this motor.")
        #         motor_commands.append([]) # Add empty list to maintain order

        steps = [[20000, 0, 0, 0],
                 [0, 20000, 0, 0],
                 [0, 0, 20000, 0],
                 [0, 0, 0, 20000],
                 [20000, 20000, 20000, 20000],
                 [20000, -20000, 20000, -20000],
                 [-20000, 20000, -20000, 20000],
                 [-20000, -20000, 20000, 20000],
                 [20000, 20000, -20000, -20000],
                 [-20000, -20000, -20000, -20000],
                 [5000, 5000, 5000, 5000],
                 [5000, 5000, 5000, 5000],
                 [5000, 5000, 5000, 5000],
                 [5000, 5000, 5000, 5000]   
        ]
        while 1:
            threads = []
            for j in range(len(steps)):
                for i, ip in enumerate(MOTOR_IPS):    
                    thread = threading.Thread(
                        target=control_single_motor, 
                        args=(ip, move_relative(steps[j][i], 3, 100, 100))
                    )
                    threads.append(thread)
                    thread.start()

                print("\nAll motor control threads have been started.")

                for thread in threads:
                    thread.join()
                time.sleep(1)

                print("\nAll threads have finished execution.")

    except ValueError:
        print("Invalid input. Please enter an integer.")
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")