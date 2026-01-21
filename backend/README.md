# AutoMic Backend

The high-performance motor control and kinematics engine for the AutoMic microphone positioning system. Built with **FastAPI** and **Python**, designed for robust parallel communication with Applied Motion drives via eSCL.

## 🚀 Features

- **Parallel Motor Control**: Simultaneous command execution across multiple motors using threaded, non-blocking I/O.
- **Type-Safe Configuration**: Full Pydantic integration for validated, environment-based configuration.
- **Robust Error Handling**: Connection monitoring and graceful failure states.
- **REST API**: Clean endpoints for 3D coordinate movement and emergency stops.

## 🛠️ Setup

### Prerequisites
- Python 3.10+
- Network access to motor drives (default subnet `192.168.1.x` and `192.168.0.x`)

### Installation

1.  **Clone & Navigate**
    ```bash
    cd backend
    ```

2.  **Environment**
    Create a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    ```

3.  **Dependencies**
    Install required packages:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration**
    Copy the example configuration:
    ```bash
    cp .env.example .env
    ```
    Edit `.env` to match your hardware IPs and tuning parameters.

## ⚡ Usage

Start the API server:

```bash
python main.py
```
*Server runs on `http://0.0.0.0:8000` by default.*

### Key Endpoints

- `POST /move`: Move microphone to `(x, y, z)` coordinates.
- `POST /emergency-stop`: Immediately halt all motors.
- `GET /motors/status`: Check connectivity of all configured drives.
- `GET /health`: System health check.

## 🏗️ Architecture

- **`motor_driver/`**: Core logic.
    - `motor_controller.py`: Orchestrates multi-motor actions.
    - `motor.py`: Handles raw TCP socket communication (eSCL protocol).
    - `config.py`: Pydantic settings models (`ProtocolSettings`, `MotionSettings`).
- **`kinematic.py`**: Solves 3D inputs -> linear motor positions.
- **`main.py`**: FastAPI entry point.
