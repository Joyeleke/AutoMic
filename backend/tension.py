import asyncio
from typing import Dict, List, Literal
from pydantic import BaseModel

from motor_driver import MotorController, CommandSequence, config

class TensionReading(BaseModel):
    motor: str
    voltage: float
    tension_status: Literal["ok", "low", "high", "error"]

class TensionService:
    def __init__(self, controller: MotorController):
        self.controller = controller
        self.config = config.tension
        self.sensor_motors = self.config.sensor_equipped_motors

    def _determine_status(self, voltage: float) -> Literal["ok", "low", "high"]:
        if voltage < self.config.low_voltage_threshold:
            return "low"
        if voltage > self.config.high_voltage_threshold:
            return "high"
        return "ok"

    async def poll_single(self, motor_name: str) -> TensionReading:
        """Polls a single motor for its analog tension voltage."""

        motor_conf = self.controller.motor_config.get(motor_name)
        if not motor_conf:
            raise ValueError(f"Motor {motor_name} not found in configuration.")

        if motor_name not in self.sensor_motors:
            return TensionReading(
                motor=motor_name, 
                voltage=0.0, 
                tension_status="error"
            )

        voltage = 0.0

        try:
            cmds = CommandSequence.configure_tension_sensor() + [CommandSequence.read_analog_input()]
            responses = await self.controller.execute_async(motor_name, cmds, require_response=True)
            
            if responses and len(responses) > 0:
                response = responses[-1]
                print(f"[TensionService] Raw response for {motor_name}: {response}")
            
                # Fix code below based on raw response format
                if "=" in response:
                    val_str = response.split("=")[1]
                else:
                    val_str = response.replace("+", "").strip()
                voltage = float(val_str)
                status = self._determine_status(voltage)
            else:
                print(f"[TensionService] Empty response for {motor_name}")
                status = "error"

        except Exception as e:
            print(f"[TensionService] Error polling {motor_name}: {e}")
            voltage = 0.0
            status = "error"

        return TensionReading(
            motor=motor_name,
            voltage=voltage,
            tension_status=status
        )

    async def poll_all(self) -> List[TensionReading]:
        """Polls all sensor-equipped motors concurrently."""
        tasks = [self.poll_single(motor) for motor in self.sensor_motors]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        readings = []
        for motor_name, res in zip(self.sensor_motors, results):
            if isinstance(res, Exception):
                print(f"[TensionService] poll_all exception for {motor_name}: {res}")
                readings.append(TensionReading(motor=motor_name, voltage=0.0, tension_status="ok"))
            else:
                readings.append(res)
        
        return readings

    async def fix_tension(self, motor_name: str, direction: Literal["tighten", "loosen"]) -> Dict[str, str]:
        """
        Sends a relative step command to adjust tension.
        - tighten: increases tension (retract / positive steps)
        - loosen: decreases tension (extend / negative steps)
        """

        if motor_name not in self.sensor_motors:
            raise ValueError(f"Motor {motor_name} doesn't support tension fixing.")

        steps = self.config.correction_steps
        if direction == "loosen":
            steps = -steps

        if motor_name in self.config.inverted_tension_motors:
             steps = -steps

        cmds = CommandSequence.move_relative(
            position=steps,
            speed=config.default_speed,
            accel=config.default_accel,
            decel=config.default_decel
        )

        command_map = {motor_name: cmds}
        await self.controller.execute_movement_async(command_map)

        return {"motor": motor_name, "action": direction, "steps": steps}

    async def auto_fix_all(self, max_iterations: int = 5) -> Dict[str, any]:
        """Polls all motors, identifies which ones are out of bounds, and nudges them into bounds using a loop"""

        actions_taken = []
        iterations = 0

        while iterations < max_iterations:
            readings = await self.poll_all()
            all_ok = True

            for r in readings:
                if r.tension_status == "error":
                    continue
                elif r.tension_status == "low":
                    await self.fix_tension(r.motor, "tighten")
                    actions_taken.append({"motor": r.motor, "action": "tighten", "iteration": iterations + 1})
                    all_ok = False
                elif r.tension_status == "high":
                    await self.fix_tension(r.motor, "loosen")
                    actions_taken.append({"motor": r.motor, "action": "loosen", "iteration": iterations + 1})
                    all_ok = False

            if all_ok:
                break
                
            iterations += 1

        new_readings = await self.poll_all()
        
        return {
            "status": "completed" if iterations < max_iterations else "max_iterations_reached",
            "iterations_ran": iterations,
            "actions": actions_taken,
            "readings": [r.model_dump() for r in new_readings]
        }
