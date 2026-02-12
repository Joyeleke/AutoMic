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

    async def _send_setup_commands(self, command_map: Dict[str, List[str]]) -> None:
        """Sends non-trigger commands to motors in parallel."""
        print("[MotorController] Phase 1: Setup - Sending configuration...")
        tasks = []
        for name, cmds in command_map.items():
            tasks.append(self._run_motor_async(name, cmds))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        errors = {}
        for name, res in zip(command_map.keys(), results):
            if isinstance(res, Exception):
                errors[name] = str(res)
                
        if errors:
            print(f"[MotorController] Setup failed with errors: {errors}")
            raise RuntimeError(f"Setup phase failed: {errors}")

    async def _trigger_motors(self, motor_names: List[str], trigger_cmd: str) -> None:
        """Sends the trigger command to all motors simultaneously."""
        print(f"[MotorController] Phase 2: Triggering execution with '{trigger_cmd}'...")
        
        async def send_trigger(name: str):
            conf = self.motor_config.get(name)
            if not conf:
                raise Exception(f"Motor {name} not configured")
            async with AsyncMotor(name=name, ip=conf.ip, port=conf.port) as motor:
                await motor.send_command(trigger_cmd)
                
        tasks = [send_trigger(name) for name in motor_names]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        errors = {}
        for name, res in zip(motor_names, results):
             if isinstance(res, Exception):
                errors[name] = str(res)

        if errors:
             print(f"[MotorController] Trigger failed with errors: {errors}")
             raise RuntimeError(f"Trigger phase failed: {errors}")

    async def execute_movement_async(self, command_map: Dict[str, List[str]], trigger_cmd: str = SCLCommands.FEED_LENGTH):
        """
        Executes movement in two phases:
        1. Setup: Send all configuration commands (AC, DE, VE, DI)
        2. Execute: Send trigger command (default FL) to all motors simultaneously
        """
        print(f"\n[MotorController] Starting async movement execution for {len(command_map)} motor(s)")
        
        setup_map = {}
        trigger_cmds = [SCLCommands.FEED_LENGTH, SCLCommands.FEED_POSITION]
        
        for name, cmds in command_map.items():
            setup_cmds = [c for c in cmds if c not in trigger_cmds]
            setup_map[name] = setup_cmds

        await self._send_setup_commands(setup_map)

        print("[MotorController] Phase 1 Complete.")
        await self._trigger_motors(list(command_map.keys()), trigger_cmd)
             
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

    