"""
Motor controller for coordinating multiple motors. 
"""

import asyncio
from typing import Dict, List
from .motor import AsyncMotor
from .config import MotorSettings
from .commands import CommandSequence, SCLCommands

class MotorController:
    """Coordinates execution of commands across multiple motors."""

    def __init__(self, motor_config: Dict[str, MotorSettings]):
        """Initializes the MotorController with motor configurations."""
        self.motor_config = motor_config

    async def execute_async(self, motor_name: str, commands: List[str], require_response: bool = False) -> List[str] | bool:
        """Execute a sequence of commands on a single motor asynchronously."""

        config = self.motor_config.get(motor_name)
        if not config:
            print(f"[{motor_name}] ERROR: Motor not configured")
            if require_response:
                raise ValueError(f"Motor {motor_name} not configured")
            return False
            
        try:
            async with AsyncMotor(name=motor_name, ip=config.ip, port=config.port) as motor:
                responses = []
                for cmd in commands:
                    res = await motor.send_command(cmd)
                    if res is None:
                        raise Exception(f"Command '{cmd}' failed")
                    responses.append(res)
                
                if require_response:
                    return responses

                print(f"[{motor_name}] ✓ All {len(commands)} command(s) completed")
                return True
        except Exception as e:
            print(f"[{motor_name}] EXCEPTION: {e}")
            raise e

    async def execute_batch_async(self, command_map: Dict[str, List[str]], require_response: bool = False) -> Dict[str, List[str] | bool]:
        """Executes lists of varying commands across multiple motors in parallel."""

        tasks = []
        for name, cmds in command_map.items():
            tasks.append(self.execute_async(name, cmds, require_response=require_response))
            
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        results_map = {}
        errors = {}
        
        for name, res in zip(command_map.keys(), task_results):
            if isinstance(res, Exception):
                errors[name] = str(res)
                results_map[name] = False if not require_response else []
            else:
                results_map[name] = res
                
        if errors:
            print(f"[MotorController] Batch execution failed with errors: {errors}")
            raise RuntimeError(f"Batch execution failed: {errors}")
            
        return results_map

    async def _trigger_motors(self, motor_names: List[str], trigger_cmd: str) -> None:
        """Sends the trigger command to all motors simultaneously."""
        
        command_map = {name: [trigger_cmd] for name in motor_names}
        try:
            await self.execute_batch_async(command_map)
        except RuntimeError as e:
            print(f"[MotorController] Trigger failed: {e}")
            raise RuntimeError(f"Trigger phase failed: {e}")

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

        print("[MotorController] Phase 1: Setup - Sending configuration...")
        await self.execute_batch_async(setup_map)
        
        print(f"[MotorController] Phase 2: Triggering execution with '{trigger_cmd}'...")
        await self._trigger_motors(list(command_map.keys()), trigger_cmd)  
        
        print("[MotorController] Movement execution completed successfully\n")

    async def emergency_stop_async(self) -> None:
        """Immediately sends ST (Stop) to all motors, bypassing the movement pipeline."""
        
        print("[MotorController] !!! EMERGENCY STOP TRIGGERED !!!")

        motor_names = list(self.motor_config.keys())
        tasks = [self.execute_async(name, [SCLCommands.STOP]) for name in motor_names]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        failures = [name for name, res in zip(motor_names, results) if isinstance(res, Exception)]
        if failures:
            print(f"[MotorController] WARNING: Stop failed for: {failures}")
            raise RuntimeError(f"Emergency stop failed for motors: {failures}")

        print("[MotorController] All motors stopped successfully.")

    async def check_connections_async(self) -> Dict[str, str]:
        """Checks connection status of all configured motors asynchronously."""
        
        results = {}
        
        async def check_single(name):
            status = "disconnected"
            try:
                response = await self.execute_async(name, [CommandSequence.get_status()], require_response=True)
                if response:
                    status = "connected"
            except Exception:
                pass
            return name, status

        print(f"\n[MotorController] Checking connections async for {len(self.motor_config)} motor(s)...")
        tasks = [check_single(n) for n in self.motor_config.keys()]
        check_results = await asyncio.gather(*tasks)
        
        for name, status in check_results:
            results[name] = status
            
        print(f"[MotorController] Connection check completed: {results}\n")
        return results

    