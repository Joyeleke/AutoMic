"""
FastAPI application for AUTOMIC motor control system.
Exposes REST endpoints for frontend to control motors.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from motor_driver import MotorController, config
from motor_driver.commands import CommandSequence
from kinematic import KinematicsSolver

class MoveRequest(BaseModel):
    """Request to move microphone to XYZ position."""
    x: float
    y: float
    z: float

app = FastAPI(
    title="AUTOMIC Motor Control API",
    description="API for controlling 4-motor microphone positioning system",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    print("="*50)
    print("AUTOMIC BACKEND STARTED")
    print("="*50)
    print(f"Configuration Loaded:")
    print(f"  Motor IPs: {config.motor1_ip}, {config.motor2_ip}, {config.motor3_ip}, {config.motor4_ip}")
    print(f"  Step Size: {config.kinematics.kinematic_step_size}")
    print(f"  Geometry M1: {config.geometry.m1}")
    print(f"  Geometry M2: {config.geometry.m2}")
    print(f"  Geometry M3: {config.geometry.m3}")
    print(f"  Geometry M4: {config.geometry.m4}")
    print("="*50)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

controller = MotorController(motor_config=config.motors)
kinematics_solver = KinematicsSolver()

@app.post("/calibrate")
async def calibrate(request: MoveRequest):
    """Endpoint to calibrate the current position of the microphone."""
    try:
        kinematics_solver.calibrate_position(request.x, request.y, request.z)
        return {"status": "calibrated", "position": request.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/move")
async def move(request: MoveRequest):
    """Endpoint to move microphone to specified XYZ position."""
    try:
        command_map = kinematics_solver.solve(request.x, request.y, request.z)
        if command_map:
             await controller.execute_movement_async(command_map)
        return {
            "status": "success",
            "position": request.model_dump()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/emergency-stop")
async def emergency_stop():
    """Immediately halt all motors."""
    try:
        stop_command = {"motor1": [CommandSequence.stop()], "motor2": [CommandSequence.stop()], "motor3": [CommandSequence.stop()], "motor4": [CommandSequence.stop()]}
        await controller.execute_movement_async(stop_command)
        return {"status": "stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/motors/status")
async def check_motors():
    """Check if all 4 motors are reachable."""
    results = await controller.check_connections_async()
    all_connected = all(status == "connected" for status in results.values())
    return {"motors": results, "all_connected": all_connected}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/config")
def get_config():
    """Return current system configuration including geometry."""
    return {
        "geometry": {
            "width": config.geometry.width_ft,
            "height": config.geometry.height_ft,
            "z_height": config.geometry.z_height_ft
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )