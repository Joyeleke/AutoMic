import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Activity, RefreshCw, Settings2, Minus, Plus } from "lucide-react";
import { TensionReading } from "@/types/motor";
import { fetchTension, fixTension, autoFixTension } from "@/lib/api";

interface TensionPanelProps {
  isConnected: boolean;
  onLog: (message: string, level?: "info" | "error" | "warning") => void;
}

export default function TensionPanel({ isConnected, onLog }: TensionPanelProps) {
  const [readings, setReadings] = useState<TensionReading[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isFixing, setIsFixing] = useState<string | null>(null);

  const loadTension = async () => {
    if (!isConnected) return;
    setIsLoading(true);
    try {
      const data = await fetchTension();
      setReadings(data);
      onLog("Tension readings refreshed");
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Failed to fetch tension";
      onLog(msg, "error");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isConnected) {
      loadTension();
    } else {
      setReadings([]);
    }
  }, [isConnected]);

  const handleFix = async (motor: string, direction: "tighten" | "loosen") => {
    if (!isConnected) return;
    setIsFixing(`${motor}-${direction}`);
    try {
      await fixTension(motor, direction);
      onLog(`Manually ${direction}ed ${motor}`);
      await loadTension();
    } catch (error) {
      const msg = error instanceof Error ? error.message : `Failed to ${direction} ${motor}`;
      onLog(msg, "error");
    } finally {
      setIsFixing(null);
    }
  };

  const handleAutoFix = async () => {
    if (!isConnected) return;
    setIsLoading(true);
    try {
      await autoFixTension();
      onLog("Auto-fix triggered across all motors");
      await loadTension();
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Failed to auto-fix tension";
      onLog(msg, "error");
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: "ok" | "low" | "high" | "error") => {
    switch (status) {
      case "ok":
        return "bg-green-100 text-green-700 border-green-200 dark:bg-green-500/10 dark:text-green-500 dark:border-green-500/20";
      case "low":
        return "bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-500/10 dark:text-amber-500 dark:border-amber-500/20";
      case "high":
        return "bg-red-100 text-red-700 border-red-200 dark:bg-red-500/10 dark:text-red-500 dark:border-red-500/20";
      case "error":
        return "bg-neutral-100 text-neutral-500 border-neutral-200 dark:bg-neutral-800 dark:text-neutral-400 dark:border-neutral-700";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  return (
    <Card className="shadow-md border border-gray-200">
      <CardHeader className="flex flex-row items-start justify-between pb-4">
        <div>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" />
            Tension Sensing
          </CardTitle>
          <CardDescription className="mt-2">
            Monitor and adjust cable tension across motors
          </CardDescription>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={loadTension}
            disabled={!isConnected || isLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-1 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <Button
            variant="default"
            size="sm"
            onClick={handleAutoFix}
            disabled={!isConnected || isLoading}
          >
            <Settings2 className="h-4 w-4 mr-1" />
            Auto-Fix
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {!isConnected ? (
          <div className="text-center text-muted-foreground py-8">
            Connect to controller to view tension.
          </div>
        ) : readings.length === 0 ? (
          <div className="text-center text-muted-foreground py-8">
            {isLoading ? "Loading tension data..." : "No readings available."}
          </div>
        ) : (
          <div className="flex flex-col divide-y">
            {readings.map((reading) => (
              <div
                key={reading.motor}
                className="flex items-center justify-between py-3 group"
              >
                <div className="flex-1 space-y-1.5">
                  <div className="flex items-center gap-3">
                    <span className="font-medium capitalize text-sm">
                      {reading.motor.replace("motor", "Motor ")}
                    </span>
                    <Badge
                      variant="outline"
                      className={`uppercase text-[10px] px-2 py-0 ${getStatusColor(
                        reading.tension_status
                      )}`}
                    >
                      {reading.tension_status}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-muted-foreground w-12">
                      {reading.tension_status === "error" ? "N/A" : `${reading.voltage.toFixed(2)}V / 5.00V`}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-1.5 opacity-80 group-hover:opacity-100 transition-opacity">
                  <Button
                    variant="outline"
                    size="icon"
                    className="h-7 w-7 rounded-full"
                    title="Loosen cable"
                    disabled={!isConnected || isFixing !== null || reading.tension_status === "error"}
                    onClick={() => handleFix(reading.motor, "loosen")}
                  >
                    <Minus className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    className="h-7 w-7 rounded-full"
                    title="Tighten cable"
                    disabled={!isConnected || isFixing !== null || reading.tension_status === "error"}
                    onClick={() => handleFix(reading.motor, "tighten")}
                  >
                    <Plus className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
