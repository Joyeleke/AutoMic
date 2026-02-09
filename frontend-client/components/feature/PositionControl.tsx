import CalibrationModal from "./CalibrationModal";
import { LocateFixed } from "lucide-react";
import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import { Label } from "@/components/ui/Label";
import { Button } from "../ui/Button";
import { Alert, AlertDescription } from "@/components/ui/Alert";
import { Input } from "../ui/Input";
import { Move, AlertCircle, Power, Loader2 } from "lucide-react";
import { Position } from "@/types/motor";

interface PositionControlProps {
  position: Position;
  onMove: (newPos: Position) => Promise<void>;
  isConnected: boolean;
  isMoving: boolean;
  onConnectToggle: () => void;
  onCalibrate: (pos: Position) => void;
}

export default function PositionControl({
  position,
  onMove,
  isConnected,
  isMoving,
  onConnectToggle,
  onCalibrate,
}: PositionControlProps) {
  const [pendingPosition, setPendingPosition] = useState<Position>(position);
  const [error, setError] = useState<string | null>(null);
  const [isCalibrating, setIsCalibrating] = useState(false);

  useEffect(() => {
    setPendingPosition(position);
  }, [position]);

  const handleInputChange = (key: keyof Position, value: string) => {
    const num = parseFloat(value);
    if (isNaN(num)) return;

    // Enforce bounds
    const bounds: Record<keyof Position, [number, number]> = { x: [0, 10], y: [0, 7], z: [0, 8] };
    const [min, max] = bounds[key];
    const clamped = Math.max(min, Math.min(max, num));

    setPendingPosition({ ...pendingPosition, [key]: clamped });
  };

  const handleApplyPosition = async () => {
    setError(null);
    try {
      await onMove(pendingPosition);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Move failed");
    }
  };

  return (
    <>
      <CalibrationModal
        isOpen={isCalibrating}
        onClose={() => setIsCalibrating(false)}
        onCalibrateSuccess={(pos) => {
          onCalibrate(pos);
          setIsCalibrating(false);
        }}
      />
      <Card className="shadow-md border border-gray-200">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Position Control</CardTitle>
            <CardDescription className="mt-2">
              Control microphone array position and spacing
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button
              onClick={() => setIsCalibrating(true)}
              variant="outline"
              size="sm"
              disabled={!isConnected}
            >
              <LocateFixed className="size-4 mr-1" />
              Calibrate
            </Button>
            <Button
              onClick={onConnectToggle}
              variant={isConnected ? "outline" : "default"}
              size="sm"
            >
              <Power className="size-4 mr-1" />
              {isConnected ? "Disconnect" : "Connect"}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {!isConnected && (
            <Alert variant="warning">
              <div className="flex items-center gap-3">
                <AlertCircle className="size-4" />
                <AlertDescription className="text-sm">
                  Connect to ClearCore controller to enable position control
                </AlertDescription>
              </div>
            </Alert>
          )}
          {error && (
            <Alert variant="destructive" className="mt-3">
              <div className="flex items-center gap-3">
                <AlertCircle className="size-4" />
                <AlertDescription className="text-sm">{error}</AlertDescription>
              </div>
            </Alert>
          )}
          <fieldset disabled={!isConnected || isMoving}>
            <div className="flex justify-between py-4">
              <div className="flex flex-col gap-2 w-1/4">
                <Label htmlFor="x-position" className="text-sm font-medium">
                  X Position (ft)
                </Label>
                <Input
                  id="x-position"
                  type="number"
                  value={pendingPosition.x}
                  onChange={(e) => handleInputChange("x", e.target.value)}
                  className="w-full"
                />
                <p className="text-xs text-gray-500">Range: 0-10&#39;</p>
              </div>
              <div className="flex flex-col gap-2 w-1/4">
                <Label htmlFor="y-position" className="text-sm font-medium">
                  Y Position (ft)
                </Label>
                <Input
                  id="y-position"
                  type="number"
                  value={pendingPosition.y}
                  onChange={(e) => handleInputChange("y", e.target.value)}
                  className="w-full"
                />
                <p className="text-xs text-gray-500">Range: 0-7&#39;</p>
              </div>
              <div className="flex flex-col gap-2 w-1/3">
                <Label htmlFor="z-position" className="text-sm font-medium">
                  Z Position (ft)
                </Label>
                <Input
                  id="z-position"
                  type="number"
                  value={pendingPosition.z}
                  onChange={(e) => handleInputChange("z", e.target.value)}
                  className="w-full"
                />
                <p className="text-xs text-gray-500">Range: 0-8&#39;</p>
              </div>
            </div>
          </fieldset>
          <div className="grid grid-cols-3 gap-3 py-4">
            <Button
              className="text-sm bg-blue-500 text-white rounded-md px-4 py-2 col-span-2"
              disabled={!isConnected || isMoving}
              onClick={handleApplyPosition}
            >
              {isMoving && <Loader2 className="size-4 mr-2 animate-spin" />}
              <Move className="size-4 mr-2" /> {isMoving ? "Moving..." : "Apply Position"}
            </Button>
            <Button
              variant="outline"
              className="text-sm bg-gray-100 rounded-md px-4 py-2"
              disabled={!isConnected || isMoving}
              onClick={() => setPendingPosition({ x: 0, y: 0, z: 0 })}
            >
              Reset Inputs
            </Button>
          </div>
        </CardContent>
      </Card>
    </>
  );
}
