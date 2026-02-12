"""
Kinematics solver for microphone positioning system.
"""

import math
from typing import Dict, List, Optional
from motor_driver.commands import CommandSequence
from motor_driver.config import config as motor_config

class KinematicsSolver:
    def __init__(self):
        self.config = motor_config
        self.last_lengths: Optional[List[float]] = None
        self.max_x = self.config.geometry.width_ft
        self.max_y = self.config.geometry.height_ft
        self.max_z = self.config.geometry.z_height_ft

    def _get_distance(self, p1: List[float], p2: List[float]) -> float:
        """Calculates 3D Euclidean distance between two points."""
        return math.sqrt(((p2[0]-p1[0])**2)+((p2[1]-p1[1])**2)+((p2[2]-p1[2])**2))

    def calibrate_position(self, x: float, y: float, z: float):
        """Sets the current physical position of the mic (Calibration)."""
        current_pos = [x, y, z]
        geo = self.config.geometry
        
        self.last_lengths = [
            self._get_distance(geo.m1, current_pos),
            self._get_distance(geo.m2, current_pos),
            self._get_distance(geo.m3, current_pos),
            self._get_distance(geo.m4, current_pos)
        ]

        print(f"DEBUG: System calibrated at {current_pos}. Lengths: {self.last_lengths}")

    def solve(self, x: float, y: float, z: float) -> Dict[str, List[str]]:
        """
        Converts 3D geometry coordinates to motor positions and command sequences.
        Implements the 'Pacer' algorithm to synchronize motor start/stop times.
        """
        if self.last_lengths is None:
            raise RuntimeError("System not calibrated! Call calibrate_position() first.")

        if not (0 <= x <= self.max_x and 0 <= y <= self.max_y and 0 <= z <= self.max_z):
             raise ValueError(f"Target ({x}, {y}, {z}) is out of bounds [0-{self.max_x}, 0-{self.max_y}, 0-{self.max_z}]")

        target_pos = [x, y, z]
        geo = self.config.geometry
        
        print(f"KINEMATICS: Solving for Target {target_pos}")
        
        new_lengths = [
            self._get_distance(geo.m1, target_pos),
            self._get_distance(geo.m2, target_pos),
            self._get_distance(geo.m3, target_pos),
            self._get_distance(geo.m4, target_pos)
        ]
        
        print(f"KINEMATICS: Calculated Lengths: {new_lengths}")

        step_val = self.config.kinematics.kinematic_step_size
        command_map = {}
        motor_names = ["motor1", "motor2", "motor3", "motor4"]
        
        motor_steps = []
        for i in range(4):
            diff = self.last_lengths[i] - new_lengths[i]
            diff_inches = diff * 12.0
            steps = int(diff_inches / step_val)
            motor_steps.append(steps)
            
        abs_steps = [abs(s) for s in motor_steps]
        max_steps = max(abs_steps)
        
        if max_steps == 0:
            print("KINEMATICS: No movement required.")
            return {}
        
        print(f"KINEMATICS: Steps: {motor_steps}")
        print(f"KINEMATICS: Pacer Max Steps: {max_steps}")

        target_speed = self.config.default_speed
        
        for i, name in enumerate(motor_names):
            steps = motor_steps[i]
            
            speed = (abs(steps) / max_steps) * target_speed
                
            if speed < 0.1: speed = 0.1 
            
            print(f"KINEMATICS: {name} -> Steps: {steps}, Speed: {speed:.4f}")
            
            if name == "motor2":
                steps = -1 * steps
            
            command_map[name] = CommandSequence.move_relative(
                steps,
                speed=speed,
                accel=self.config.default_accel,
                decel=self.config.default_decel
            )

        self.last_lengths = new_lengths
        
        return command_map