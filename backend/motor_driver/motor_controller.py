"""
Motor controller for coordinating multiple motors. 
"""

import threading
from typing import Dict, List
from .motor import Motor
from .config import MotorSettings
from .commands import CommandSequence

class MotorController:
    """
    Coordinates execution of commands across multiple motors.
    """

    def __init__(self, motor_config: Dict[str, MotorSettings]):
        """Initializes the MotorController with motor configurations."""
        self.motor_config = motor_config

    def _run_motor(self, motor_name: str, commands: List[str]) -> bool:
        """Execute command sequence on a single motor. Returns True if successful."""
        config = self.motor_config.get(motor_name)

        if not config:
            print(f"[{motor_name}] ERROR: Motor not configured")
            return False
        
        ip = config.ip
        port = config.port
        
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
        Checks connection status of all configured motors in parallel.
        Returns a dict mapping motor name to 'connected' or 'disconnected'.
        """
        threads = []
        results = {}
        
        def check_single_status(name, conf):
            status = "disconnected"
            try:
                ip = conf.ip
                port = conf.port
                with Motor(name=name, ip=ip, port=port, timeout=2.0) as motor:
                    cmd = CommandSequence.get_status()
                    if motor.send_command(cmd):
                        status = "connected"
            except Exception:
                pass
            
            results[name] = status

        print(f"\n[MotorController] Checking connections for {len(self.motor_config)} motor(s)...")

        for motor_name, config in self.motor_config.items():
            thread = threading.Thread(
                target=check_single_status,
                args=(motor_name, config),
                daemon=False
            )
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
            
        print(f"[MotorController] Connection check completed: {results}\n")
            
        return results
    