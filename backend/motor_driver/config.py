from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Dict

class MotorSettings(BaseModel):
    ip: str
    port: int

class ProtocolSettings(BaseModel):
    header_bytes: bytes = b'\x00\x07'
    terminator_byte: bytes = b'\r'
    encoding: str = "ascii"

class MotionSettings(BaseModel):
    socket_timeout: float = 5.0
    recv_buffer_size: int = 1024

class MotorConfig(BaseSettings):
    motor1_ip: str = "192.168.1.10"
    motor2_ip: str = "192.168.1.20"
    motor3_ip: str = "192.168.1.30"
    motor4_ip: str = "192.168.0.40"
    motor_port: int = 7776
    default_speed: float = 5.0
    default_accel: float = 100.0
    default_decel: float = 100.0

    protocol: ProtocolSettings = ProtocolSettings()
    motion: MotionSettings = MotionSettings()
    
    @property
    def motors(self) -> Dict[str, MotorSettings]:
        return {
            "motor1": MotorSettings(ip=self.motor1_ip, port=self.motor_port),
            "motor2": MotorSettings(ip=self.motor2_ip, port=self.motor_port),
            "motor3": MotorSettings(ip=self.motor3_ip, port=self.motor_port),
            "motor4": MotorSettings(ip=self.motor4_ip, port=self.motor_port),
        }

    class Config:
        env_file = ".env"

config = MotorConfig()