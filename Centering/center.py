import socket
import time
import threading

# --- Configuration ---
MOTOR_IPS = [
    "192.168.1.20", # Motor with switch at '2'
    "192.168.1.30", # Motor with switch at '3'
    "192.168.0.40",  # Motor with switch at '4'
]

motor1 = "192.168.1.10" # Motor with switch at '1'

LOCAL_PORT_START = 7777 

# --- Motion Parameters ---
ACCEL_RATE = 10.0
DECEL_RATE = 10.0
MAX_VELOCITY = 0.25

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
        
def configure_motor_for_tension_sensor():
    """Generates a command list to configure the motor for tension sensor."""
    return ["AS3", "IFD"]

def poll_potentiometer():
    """Generates a command list to poll the potentiometer."""
    return ["IA"]


def monitor_tension_sensor(ip_address, poll_rate_seconds=0.5) -> float:
    """Configures the analog input and continuously reads the voltage."""
    print(f"Tension monitoring thread for {ip_address} starting...")
    
    try:
        with SCL_Motor(ip_address) as motor:
            
            config_commands = configure_motor_for_tension_sensor()
            for cmd in config_commands:
                motor.send_command(cmd)
                
            print(f"--> {ip_address} configured. Starting continuous poll.")
            
            poll_commands = poll_potentiometer()
            

            for cmd in poll_commands:
                response = motor.send_command(cmd)
                    
                print(f"[{ip_address}] Response: {response}")

                if response and "=" in response:
                    try:
                        voltage_str = response.split('=')[1]
                        voltage = float(voltage_str)
                        print(f"[{ip_address}] Voltage: {voltage} V")
                        return voltage
                    except ValueError:
                        print(f"[{ip_address}] Parse error: {response}")
                        return -1.0
                else:
                    print(f"[{ip_address}] Unexpected response: {response}")
                    return -1.0     

    except Exception as e:
        print(f"An error occurred in thread for {ip_address}: {e}")
    return -1.0

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

def get_tension():
    """Generates a command list to get the tension."""
    return ["IA"]

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
    threads = []
    
    try:
        motor_commands = []
        tense = True
        slack = False
        skip = False
        motorsSlack = 0
        tensionLimit = 0.05
        
        threads = []
        
        #Make all wire slack
        
        #Automated version, revisit if we revise tension sensors
        # while(tense):
            
        #     print("\nAll motor control threads have been started.")

        #     for thread in threads:
        #         thread.join()
        #     time.sleep(0.3)

        #     print("\nAll threads have finished execution.")
            
        #     for i, ip in enumerate(MOTOR_IPS):
        #         steps = -100
        #         tensionLimit = 0.00
        #         tension = monitor_tension_sensor(ip)
        #         print(ip, " Tension: ", tension)
                
        #         if ip == "192.168.1.20":
        #             steps = -steps
        #             tension = -tension + 4.995
                    
        #         if ip == "192.168.1.20":
        #             tension = tension -0.005
                
        #         print(tension)
        #         if tension > 0.001:
        #             thread = threading.Thread(
        #                 target=control_single_motor, 
        #                 args=(ip, move_relative(steps, MAX_VELOCITY, ACCEL_RATE, DECEL_RATE))
        #             )
        #             threads.append(thread)
        #             thread.start()
        #         else:
        #             motorsSlack += 1
        #     if motorsSlack != 3:
        #         motorsSlack = 0
        #     else:                               
        #         floor = input("Is the micorphone touching the floor? Y/N")
        #         if floor == "N":                    
        #             tense = False
        #             slack = True
        #         elif floor == "Y":
        #             #move up 2 feet, try again
        #             control_single_motor(motor1, move_relative(18658*2, MAX_VELOCITY, ACCEL_RATE, DECEL_RATE))
        #             print("Moving up and rerunning")
        #             time.sleep(20)
        
        print("Letting the wire out until the 3 lower lines are all slack\n PLEASE PAY ATTENTION HERE, MAKE SURE THE WIRE IS BEING LET OUT TO AVOID TANGLING\n The motors are prone to spinning but the wire not coming through, make sure to watch for this and pull the wire through")
                
        while not slack:
            for i, ip in enumerate(MOTOR_IPS):
                isSlack = ""
                tense = True
                steps = -1000
                
                if ip == "192.168.1.20":
                    steps = -steps
                
                while tense:
                    
                    print(skip)
                    
                    if not skip:
                        control_single_motor(ip, move_relative(steps, MAX_VELOCITY, ACCEL_RATE, DECEL_RATE))
                    else:
                        skip = False
                    
                    isSlack = input("Is wire at ip: " + ip + " Slack? (Y/N) ")
                    
                    if isSlack == "Y":
                        tense = False
                    elif isSlack == "N":
                        print("Moving again")
                    else:
                        print("Please input a valid response")
                        skip = True
            floor = input("Are the microphones on the floor? (Y/N) ")
            if floor == "Y":
                control_single_motor(motor1, move_relative(18658*2, MAX_VELOCITY, ACCEL_RATE, DECEL_RATE))
                print("Moving up 2 feet and rerunning")
                time.sleep(15)
            else:
                allSlack = input("Are the wires all slack (the motor should only be hanging from the top)? (Y/N) ")
                if allSlack:
                    slack = True
                
                    
        #Pull in until we feel tension    
        while not tense:
            for i, ip in enumerate(MOTOR_IPS):
                stepsIn = 100
                    
                if ip == "192.168.1.20":
                    stepsIn = -stepsIn
                    
                #This motor is still slack
                mSlack = True
                while(mSlack):
                    control_single_motor(ip, move_relative(stepsIn, MAX_VELOCITY, ACCEL_RATE, DECEL_RATE))
                    tension = monitor_tension_sensor(ip)
                    
                    if ip == "192.168.1.20":
                        tension = -tension + 4.995
                            
                    print(ip , " Tension: " , tension)
                            
                    if tension > tensionLimit:
                        mSlack = False
                        print("Motor", ip , "is tense")
                        
            isTense = input("Are all of the motor lines tense? (Y/N) ")

            if isTense == "Y":
                tense = True
            
        above = True
                    
        # Make sure the microphones are below the lower motors
        while(above):
            whereZ = input("Are the microphones above the lower motors? (Y/N)")
            if whereZ == "Y":
                for i, ip in enumerate(MOTOR_IPS):
                    steps = -18658*3
                
                    if ip == "192.168.1.20":
                        steps = -steps
                        tension = -tension + 5
                        
                    thread = threading.Thread(
                        target=control_single_motor, 
                        args=(ip, move_relative(steps, MAX_VELOCITY, ACCEL_RATE, DECEL_RATE))
                    )
                    threads.append(thread)
                    thread.start()
                thread = threading.Thread(
                    target=control_single_motor, 
                    args=(motor1, move_relative(steps, MAX_VELOCITY, ACCEL_RATE, DECEL_RATE))
                )
                threads.append(thread)
                thread.start()
                
                for thread in threads:
                    thread.join()
                time.sleep(15)
                
            else:
                above = False
        
        level = False
        motorsLevel = 0
        
        # Pull in lower motors until level
        while(not level):
            print("\nAll motor control threads have been started.")

            for thread in threads:
                thread.join()
            time.sleep(0.1)

            print("\nAll threads have finished execution.")
            
            for i, ip in enumerate(MOTOR_IPS):
                steps = -100
                tension = monitor_tension_sensor(ip)
                print(ip, " Tension: ", tension)
                
                if ip == "192.168.1.20":
                    steps = -steps
                    tension = -tension + 4.995
                
                print(tension)
                if tension > 0.004:
                    thread = threading.Thread(
                        target=control_single_motor, 
                        args=(ip, move_relative(steps, MAX_VELOCITY, ACCEL_RATE, DECEL_RATE))
                    )
                    threads.append(thread)
                    thread.start()
                else:
                    motorsLevel += 1
            if motorsLevel != 3:
                thread = threading.Thread(
                        target=control_single_motor, 
                        args=(motor1, move_relative(-300, MAX_VELOCITY, ACCEL_RATE, DECEL_RATE))
                    )
                threads.append(thread)
                thread.start()
                motorsLevel = 0
            else:
                ground = input("Are the motors on the floor? (Y/N) ")
                if ground == "Y":
                    print("Motors on the ground")
                    level = True
                    control_single_motor(motor1, move_relative(300, MAX_VELOCITY, ACCEL_RATE, DECEL_RATE))
                else:
                    thread = threading.Thread(
                        target=control_single_motor, 
                        args=(motor1, move_relative(-300, MAX_VELOCITY, ACCEL_RATE, DECEL_RATE))
                    )
                    threads.append(thread)
                    thread.start()
                    motorsLevel = 0
                
        control_single_motor(motor1, move_relative(18658*3, MAX_VELOCITY, ACCEL_RATE, DECEL_RATE))
        
        time.sleep(15)
        
        tense = False
        
        while not tense:
            for i, ip in enumerate(MOTOR_IPS):
                stepsIn = 100
                    
                if ip == "192.168.1.20":
                    stepsIn = -stepsIn
                    
                #This motor is still slack
                mSlack = True
                
                while(mSlack):
                    control_single_motor(ip, move_relative(stepsIn, MAX_VELOCITY, ACCEL_RATE, DECEL_RATE))
                    tension = monitor_tension_sensor(ip)
                    
                    if ip == "192.168.1.20":
                        tension = -tension + 4.995
                            
                    print(ip , " Tension: " , tension)
                            
                    if tension > tensionLimit:
                        mSlack = False
                        print("Motor", ip , "is tense")
                        
            isTense = input("Are all of the motor lines tense? (Y/N) ")

            if isTense == "Y":
                tense = True
                
    except KeyboardInterrupt:
        stop = []
        stop.append("ST")
        
        for i, ip in enumerate(MOTOR_IPS):
            control_single_motor(ip, stop)
        control_single_motor(motor1, stop)
        print("\nProgam terminated by user.")