"""
Module defining SCL command templates and command sequence builders.
"""

from typing import List

class SCLCommands:
    """Class containing SCL command templates."""

    ACCELERATION = "AC"
    DECELERATION = "DE"
    VELOCITY = "VE"
    DISTANCE = "DI"
    FEED_POSITION = "FP"
    FEED_LENGTH = "FL"
    MOTION_ENABLED = "ME"
    REQUEST_STATUS = "RS"
    STOP = "ST"
    ALARM_RESET = "AR"
    ALARM_CODE = "AL"


class CommandSequence:
    """Build command sequences from high-level parameters."""

    @staticmethod
    def move_absolute(position: float, speed: float, accel: float, decel: float) -> List[str]:
        """Generates a command list for an absolute move."""
        return [
            SCLCommands.MOTION_ENABLED,
            f"{SCLCommands.ACCELERATION}{accel}",
            f"{SCLCommands.DECELERATION}{decel}",
            f"{SCLCommands.VELOCITY}{speed}",
            f"{SCLCommands.DISTANCE}{position}",
            SCLCommands.FEED_POSITION
        ]

    @staticmethod
    def move_relative(position: float, speed: float, accel: float, decel: float) -> List[str]:
        """Generates a command list for a relative move."""
        return [
            SCLCommands.MOTION_ENABLED,
            f"{SCLCommands.ACCELERATION}{accel}",
            f"{SCLCommands.DECELERATION}{decel}",
            f"{SCLCommands.VELOCITY}{speed}",
            f"{SCLCommands.DISTANCE}{position}",
            SCLCommands.FEED_LENGTH
        ]

    @staticmethod
    def get_status() -> List[str]:
        """Generates a command list to get the drive status."""
        return [SCLCommands.REQUEST_STATUS]
