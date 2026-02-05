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
        """
        if self.last_lengths is None:
            raise RuntimeError("System not calibrated! Call calibrate_position() first.")

        target_pos = [x, y, z]
        geo = self.config.geometry
        
        new_lengths = [
            self._get_distance(geo.m1, target_pos),
            self._get_distance(geo.m2, target_pos),
            self._get_distance(geo.m3, target_pos),
            self._get_distance(geo.m4, target_pos)
        ]

        step_val = self.config.kinematics.step_size
        command_map = {}
        
        motor_names = ["motor1", "motor2", "motor3", "motor4"]
        
        for i, name in enumerate(motor_names):
            diff = self.last_lengths[i] - new_lengths[i]
            steps = int(diff / step_val)
            
            command_map[name] = CommandSequence.move_relative(
                steps,
                speed=self.config.default_speed,
                accel=self.config.default_accel,
                decel=self.config.default_decel
            )

        self.last_lengths = new_lengths
        
        return command_map