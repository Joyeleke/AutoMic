import StatusBar from "@/components/feature/StatusBar";
import { Button } from "@/components/ui/Button";
import { Octagon } from "lucide-react";
import { emergencyStop } from "@/lib/api";
import { useState } from "react";

interface HeaderProps {
  isConnected: boolean;
  isMoving: boolean;
}

export default function Header({ isConnected, isMoving }: HeaderProps) {
  const [isStopping, setIsStopping] = useState(false);

  const handleEmergencyStop = async () => {
    try {
      setIsStopping(true);
      await emergencyStop();
    } catch (error) {
      console.error("Failed to trigger E-Stop:", error);
    } finally {
      setIsStopping(false);
    }
  };

  return (
    <header className="flex items-center justify-between">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">AutoMic Control</h1>
        <p className="text-sm text-muted-foreground">
          Ruth Lilly Performance Hall - UIndy Music Department
        </p>
      </div>
      <div className="flex items-center gap-4">
        <Button
          variant="destructive"
          size="sm"
          className="font-bold uppercase tracking-wider shadow-md animate-pulse hover:animate-none"
          onClick={handleEmergencyStop}
          disabled={isStopping}
        >
          <Octagon className="mr-2 size-5" />
          E-STOP
        </Button>
        <StatusBar isConnected={isConnected} isMoving={isMoving} />
      </div>
    </header>
  );
}
