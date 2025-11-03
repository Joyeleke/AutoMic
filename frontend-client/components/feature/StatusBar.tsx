import { Badge } from "@/components/ui/Badge"
import { Activity, Wifi, WifiOff } from "lucide-react"

interface StatusBarProps {
  isConnected?: boolean
  isMoving?: boolean
}

export default function StatusBar({ isConnected = false, isMoving = false }: StatusBarProps) {
  return (
    <div className="flex items-center gap-3">
      <Badge variant={isConnected ? "default" : "secondary"} className="gap-1.5 px-3 py-1.5">
        {isConnected ? <Wifi className="size-3.5" /> : <WifiOff className="size-3.5" />}
        <span className="text-xs font-medium">{isConnected ? "Connected" : "Disconnected"}</span>
      </Badge>
      {isMoving && (
        <Badge variant="outline" className="gap-1.5 border-accent px-3 py-1.5 text-accent">
          <Activity className="size-3.5 animate-pulse" />
          <span className="text-xs font-medium">Moving</span>
        </Badge>
      )}
    </div>
  )
}
