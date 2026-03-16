/**
 * API client for AUTOMIC backend
 * Handles all HTTP communication with the motor control system
 */

import type { HealthResponse, MoveResponse, SystemConfig, TensionReading } from "@/types/motor";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function moveToPosition(
  x: number,
  y: number,
  z: number
): Promise<MoveResponse> {
  const response = await fetch(`${API_BASE_URL}/move`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ x, y, z }),
  });

  if (!response.ok) {
    throw new Error(`Failed to move: ${response.statusText}`);
  }

  return response.json();
}

export async function calibratePosition(
  x: number,
  y: number,
  z: number
): Promise<{ status: string; position: { x: number; y: number; z: number } }> {
  const response = await fetch(`${API_BASE_URL}/calibrate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ x, y, z }),
  });

  if (!response.ok) {
    throw new Error(`Failed to calibrate: ${response.statusText}`);
  }

  return response.json();
}

export async function fetchSystemConfig(): Promise<SystemConfig> {
  const response = await fetch(`${API_BASE_URL}/config`);

  if (!response.ok) {
    throw new Error("Failed to fetch system configuration");
  }

  return response.json();
}

export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) {
    throw new Error("Backend health check failed");
  }

  return response.json();
}

export async function testConnection(): Promise<boolean> {
  try {
    const health = await checkHealth();
    return health.status === "healthy";
  } catch {
    return false;
  }
}

export async function emergencyStop(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/emergency-stop`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error(`Failed to trigger emergency stop: ${response.statusText}`);
  }
}

export async function fetchTension(): Promise<TensionReading[]> {
  const response = await fetch(`${API_BASE_URL}/tension`);
  if (!response.ok) {
    throw new Error(`Failed to fetch tension: ${response.statusText}`);
  }
  return response.json();
}

export async function fixTension(motor: string, direction: "tighten" | "loosen"): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/tension/fix`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ motor, direction }),
  });
  if (!response.ok) {
    throw new Error(`Failed to fix tension: ${response.statusText}`);
  }
}

export async function autoFixTension(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/tension/auto-fix`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error(`Failed to auto-fix tension: ${response.statusText}`);
  }
}
