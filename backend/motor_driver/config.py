from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Dict, List

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

class GeometrySettings(BaseModel):
    m1: List[float] = [77.16, 81.48, 95.16]    
    m2: List[float] = [147.0, 146.04, 51.0]    
    m3: List[float] = [9.0, 146.04, 51.0]      
    m4: List[float] = [77.16, 0.00, 51.0]    
    width_in: float = 147.0      
    height_in: float = 146.04    
    z_height_in: float = 95.16   

class KinematicSettings(BaseModel):
    kinematic_step_size: float = 0.00064316 

class TensionSettings(BaseModel):
    low_voltage_threshold: float = 0.1
    high_voltage_threshold: float = 0.6
    inverted_low_voltage_threshold: float = 4.9
    inverted_high_voltage_threshold: float = 4.4
    correction_steps: int = 50
    sensor_equipped_motors: List[str] = ["motor2", "motor3", "motor4"]
    inverted_tension_motors: List[str] = ["motor2"]

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
    geometry: GeometrySettings = GeometrySettings()
    kinematics: KinematicSettings = KinematicSettings()
    tension: TensionSettings = TensionSettings()
    
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
        env_nested_delimiter = "__"

config = MotorConfig()