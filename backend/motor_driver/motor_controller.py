"""
Motor controller for coordinating multiple motors. 
"""

import asyncio
from typing import Dict, List
from .motor import AsyncMotor
from .config import MotorSettings
from .commands import CommandSequence, SCLCommands

class MotorController:
    """
    Coordinates execution of commands across multiple motors.
    """

    def __init__(self, motor_config: Dict[str, MotorSettings]):
        """Initializes the MotorController with motor configurations."""
        self.motor_config = motor_config

    async def _run_motor_async(self, motor_name: str, commands: List[str]) -> bool:
        """Execute command sequence on a single motor asynchronously."""
        config = self.motor_config.get(motor_name)
        if not config:
            print(f"[{motor_name}] ERROR: Motor not configured")
            return False
            
        try:
            async with AsyncMotor(name=motor_name, ip=config.ip, port=config.port) as motor:
                for cmd in commands:
                    if await motor.send_command(cmd) is None:
                        raise Exception(f"Command '{cmd}' failed")
                print(f"[{motor_name}] ✓ All commands completed")
                return True
        except Exception as e:
            print(f"[{motor_name}] EXCEPTION: {e}")
            raise e

    async def execute_movement_async(self, command_map: Dict[str, List[str]]):
        """
        Executes movement in two phases:
        1. Setup: Send all configuration commands (AC, DE, VE, DI)
        2. Execute: Send FL command to all motors simultaneously
        """
        print(f"\n[MotorController] Starting async movement execution for {len(command_map)} motor(s)")
        
        # Split commands into setup and trigger
        setup_map = {}
        trigger_cmd = SCLCommands.FEED_LENGTH
        
        for name, cmds in command_map.items():
            # Filter out FL/FP commands for the setup phase
            setup_cmds = [c for c in cmds if c not in [SCLCommands.FEED_LENGTH, SCLCommands.FEED_POSITION]]
            setup_map[name] = setup_cmds
            
            # Check if this motor actually has a move command
            if SCLCommands.FEED_POSITION in cmds:
                trigger_cmd = SCLCommands.FEED_POSITION

        # Phase 1: Setup
        print("[MotorController] Phase 1: Setup - Sending configuration...")
        setup_tasks = []
        for name, cmds in setup_map.items():
            setup_tasks.append(self._run_motor_async(name, cmds))
            
        results = await asyncio.gather(*setup_tasks, return_exceptions=True)
        
        errors = {}
        for name, res in zip(setup_map.keys(), results):
            if isinstance(res, Exception):
                errors[name] = str(res)
                
        if errors:
            print(f"[MotorController] Setup failed with errors: {errors}")
            raise RuntimeError(f"Setup phase failed: {errors}")

        # Phase 2: Execute
        print("[MotorController] Phase 1 Complete. Phase 2: Triggering execution...")
        
        async def send_trigger(name: str):
            conf = self.motor_config.get(name)
            async with AsyncMotor(name=name, ip=conf.ip, port=conf.port) as motor:
                await motor.send_command(trigger_cmd)
                
        trigger_tasks = [send_trigger(name) for name in command_map.keys()]
        
        # Launch all triggers
        trigger_results = await asyncio.gather(*trigger_tasks, return_exceptions=True)
        
        trigger_errors = {}
        for name, res in zip(command_map.keys(), trigger_results):
             if isinstance(res, Exception):
                trigger_errors[name] = str(res)

        if trigger_errors:
             print(f"[MotorController] Trigger failed with errors: {trigger_errors}")
             raise RuntimeError(f"Trigger phase failed: {trigger_errors}")
             
        print("[MotorController] Movement execution completed successfully\n")

    async def check_connections_async(self) -> Dict[str, str]:
        """Checks connection status of all configured motors asynchronously."""
        results = {}
        
        async def check_single(name, conf):
            status = "disconnected"
            try:
                async with AsyncMotor(name=name, ip=conf.ip, port=conf.port, timeout=2.0) as motor:
                    response = await motor.send_command(CommandSequence.get_status())
                    if response is not None:
                        status = "connected"
            except Exception:
                pass
            return name, status

        print(f"\n[MotorController] Checking connections async for {len(self.motor_config)} motor(s)...")
        tasks = [check_single(n, c) for n, c in self.motor_config.items()]
        check_results = await asyncio.gather(*tasks)
        
        for name, status in check_results:
            results[name] = status
            
        print(f"[MotorController] Connection check completed: {results}\n")
        return results

    