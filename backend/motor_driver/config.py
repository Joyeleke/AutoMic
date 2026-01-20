import os
from pydantic_settings import BaseSettings

class MotorConfig(BaseSettings):
    motor1_ip: str = "192.168.1.10"
    motor2_ip: str = "192.168.1.20"
    motor3_ip: str = "192.168.1.30"
    motor4_ip: str = "192.168.0.40"
    motor_port: int = 7776
    default_speed: float = 5.0
    default_accel: float = 100.0
    default_decel: float = 100.0
    
    class Config:
        env_file = ".env"
        extra = "ignore" # Allow extra env vars

config = MotorConfig()

DEFAULT_MOTOR_CONFIG = {
    "motor1": {"ip": config.motor1_ip, "port": config.motor_port},
    "motor2": {"ip": config.motor2_ip, "port": config.motor_port},
    "motor3": {"ip": config.motor3_ip, "port": config.motor_port},
    "motor4": {"ip": config.motor4_ip, "port": config.motor_port},
}

PROTOCOL_CONFIG = {
    "header_bytes": b'\x00\x07', 
    "terminator_byte": b'\r',
    "encoding": "ascii",
}

MOTION_PARAMETERS = {
    "socket_timeout": 5.0,
    "recv_buffer_size": 1024
}