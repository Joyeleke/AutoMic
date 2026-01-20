"use client";

import { useState } from "react";
import Header from "@/components/layout/Header";
import PositionControl from "@/components/feature/PositionControl";
import PresetList from "@/components/feature/PresetList";
import StageView from "@/components/feature/StageView";
import SystemLog from "@/components/feature/SystemLog";
import { Position, LogEntry } from "@/types/motor";
import { testConnection, moveToPosition } from "@/lib/api";

const defaultPosition: Position = { x: 5, y: 3.5, z: 3 };

export default function Home() {
  const [position, setPosition] = useState<Position>(defaultPosition);
  const [isConnected, setIsConnected] = useState(false);
  const [isMoving, setIsMoving] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);

  function addLog(message: string, level: LogEntry["level"] = "info") {
    const time = new Date().toLocaleTimeString();
    setLogs((prev) => [{ time, message, level }, ...prev].slice(0, 100));
  }

  async function handleConnectToggle() {
    if (isConnected) {
      setIsConnected(false);
      addLog("Disconnected from controller");
      return;
    }

    const success = await testConnection();
    if (success) {
      setIsConnected(true);
      addLog("Connected to controller");
    } else {
      addLog("Connection failed", "error");
    }
  }


  async function handleMove(target: Position) {
    if (!isConnected || isMoving) return;

    setIsMoving(true);
    addLog(`Moving to X:${target.x}, Y:${target.y}, Z:${target.z}`);
    try {
      const response = await moveToPosition(target.x, target.y, target.z);
      setPosition(response.position);
      addLog("Move completed successfully");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Move failed";
      addLog(message, "error");
    } finally {
      setIsMoving(false);
    }
  }
  return (
    <div className="min-h-screen bg-background p-4 md:p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <Header isConnected={isConnected} isMoving={isMoving} />
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="space-y-6">
            <StageView position={position} />
            <SystemLog logs={logs} />
          </div>
          <div className="space-y-6">
            <PositionControl
              position={position}
              onMove={handleMove}
              isConnected={isConnected}
              isMoving={isMoving}
              onConnectToggle={handleConnectToggle}
            />
            <PresetList
              onLoadPreset={(preset) => {
                setPosition(preset);
                addLog(
                  `Loaded preset: X:${preset.x}, Y:${preset.y}, Z:${preset.z}`
                );
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
