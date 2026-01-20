"""
Motor controller for coordinating multiple motors. 
"""

import threading
from typing import Dict, List, Optional
from .motor import Motor
from .config import DEFAULT_MOTOR_CONFIG

class MotorController:
    """
    Coordinates execution of commands across multiple motors.
    """

    def __init__(self, motor_config=None):
        """Initializes the MotorController with motor configurations."""
        self.motor_config = motor_config or DEFAULT_MOTOR_CONFIG.copy()

    def _run_motor(self, motor_name: str, commands: List[str]) -> bool:
        """Execute command sequence on a single motor. Returns True if successful."""
        config = self.motor_config.get(motor_name)

        if not config:
            print(f"[{motor_name}] ERROR: Motor not configured")
            return False
        
        ip = config["ip"]
        port = config.get("port", 7776)
        
        try:
            with Motor(name=motor_name, ip=ip, port=port) as motor:
                for cmd in commands:
                    if not motor.send_command(cmd):
                        raise Exception(f"Command '{cmd}' failed connection or internal error")

                print(f"[{motor_name}] ✓ All commands completed")
                return True
        except Exception as e:
            print(f"[{motor_name}] EXCEPTION: {e}")
            raise e # Propagate the exception up

    def _execute_parallel(self, command_map: Dict[str, List[str]]):
        """Execute commands in parallel using threads."""
        threads = []
        errors = {}
        
        def run_thread(name, cmds):
             try:
                 self._run_motor(name, cmds)
             except Exception as e:
                 errors[name] = str(e)
        
        for motor_name, commands in command_map.items():
            thread = threading.Thread(
                target=run_thread,
                args=(motor_name, commands),
                daemon=False
            )
            threads.append(thread)
            thread.start()
        
        print(f"\n[MotorController] Started {len(threads)} motor(s) in parallel")
        
        for thread in threads:
            thread.join()
            
        if errors:
            print(f"[MotorController] Errors occurred: {errors}")
            raise RuntimeError(f"Motor errors: {errors}")
        
        print("[MotorController] All motors completed\n")

    def _execute_sequential(self, command_map: Dict[str, List[str]]):
        """Execute commands sequentially."""
        print(f"\n[MotorController] Executing {len(command_map)} motor(s) sequentially")
        
        errors = {}
        for motor_name, commands in command_map.items():
            try:
                self._run_motor(motor_name, commands)
            except Exception as e:
                errors[motor_name] = str(e)
        
        if errors:
            raise RuntimeError(f"Motor errors: {errors}")
        
        print("[MotorController] All motors completed\n")

    def execute_motors(self, command_map: Dict[str, List[str]], parallel: bool = True):
        """
        Execute commands on motors.
        """

        if not command_map:
            print("[MotorController] No commands to execute")
            return
        
        if parallel:
            self._execute_parallel(command_map)
        else:
            self._execute_sequential(command_map)

    def check_connections(self) -> Dict[str, str]:
        """
        Checks connection status of all configured motors.
        Returns a dict mapping motor name to 'connected' or 'disconnected'.
        """
        results = {}
        from .commands import SCLCommands  # Import internally to avoid circular dep if any

        # Use threads for faster checking
        threads = []
        lock = threading.Lock()
        
        def check_single(name, conf):
            status = "disconnected"
            try:
                ip = conf["ip"]
                port = conf.get("port", 7776)
                # Just try to connect and send a status request
                with Motor(name=name, ip=ip, port=port, timeout=2.0) as motor:
                    # Try sending RS (Request Status)
                    if motor.send_command(SCLCommands.REQUEST_STATUS):
                        status = "connected"
            except Exception:
                pass
            
            with lock:
                results[name] = status

        for motor_name, config in self.motor_config.items():
            t = threading.Thread(target=check_single, args=(motor_name, config))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
            
        return results
    