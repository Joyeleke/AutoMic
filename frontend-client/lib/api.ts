/**
 * API client for AUTOMIC backend
 * Handles all HTTP communication with the motor control system
 */

import type { HealthResponse, MoveResponse } from "@/types/motor";

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
