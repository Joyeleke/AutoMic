"""
FastAPI application for AUTOMIC motor control system.
Exposes REST endpoints for frontend to control motors.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from motor_driver import MotorController, config
from motor_driver.commands import CommandSequence
from kinematic import MockKinematicsSolver

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

controller = MotorController(motor_config=config.motors)
kinematics_solver = MockKinematicsSolver()

@app.post("/move")
def move(request: MoveRequest):
    """Endpoint to move microphone to specified XYZ position."""
    try:
        command_map = kinematics_solver.solve(request.x, request.y, request.z)
        controller.execute_motors(command_map, parallel=True)
        return {
            "status": "success",
            "position": {"x": request.x, "y": request.y, "z": request.z}
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/emergency-stop")
def emergency_stop():
    """Immediately halt all motors."""
    try:
        stop_command = {"motor1": [CommandSequence.stop()], "motor2": [CommandSequence.stop()], "motor3": [CommandSequence.stop()], "motor4": [CommandSequence.stop()]}
        controller.execute_motors(stop_command, parallel=True)
        return {"status": "stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/motors/status")
def check_motors():
    """Check if all 4 motors are reachable."""
    results = controller.check_connections()
    all_connected = all(status == "connected" for status in results.values())
    return {"motors": results, "all_connected": all_connected}

@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )