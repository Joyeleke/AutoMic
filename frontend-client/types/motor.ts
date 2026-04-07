/**
 * Core types for motor control system
 */

export interface Position {
  x: number;
  y: number;
  z: number;
}

export interface MoveResponse {
  status: "success";
  position: Position;
}

export interface HealthResponse {
  status: "healthy";
}

export interface MotorState {
  connected: boolean;
  moving: boolean;
  currentPosition: Position;
  error: string | null;
}

export interface Preset {
  name: string;
  description: string;
  position: Position;
}

export interface LogEntry {
  time: string;
  message: string;
  level?: "info" | "error" | "warning";
}

export interface SystemConfig {
  geometry: {
    width: number;
    height: number;
    z_height: number;
    motors: {
      m1: [number, number, number];
      m2: [number, number, number];
      m3: [number, number, number];
      m4: [number, number, number];
    };
  };
}

export interface TensionReading {
  motor: string;
  voltage: number;
  tension_status: "ok" | "low" | "high" | "error";
}