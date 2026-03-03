import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import { Mic2 } from "lucide-react";
import GridOverlay from "@/components/ui/GridOverlay";
import { Position, SystemConfig } from "@/types/motor";

interface StageViewProps {
  config: SystemConfig | null;
  position: Position;
}
export default function StageView({ config, position }: StageViewProps) {
  const STAGE_WIDTH_IN = config?.geometry.width || 147.0;
  const STAGE_HEIGHT_IN = config?.geometry.height || 146.04;
  const STAGE_Z_HEIGHT_IN = config?.geometry.z_height || 95.16;

  const xPercent = (position.x / STAGE_WIDTH_IN) * 100;
  const yPercent = (position.y / STAGE_HEIGHT_IN) * 100;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Stage View</CardTitle>
        <CardDescription>
          {STAGE_WIDTH_IN}&quot; x {STAGE_HEIGHT_IN}&quot; Operating Area
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div className="relative aspect-[10/7] w-full overflow-hidden rounded-lg border-2 border-primary/30 bg-muted/30">
            <div className="absolute left-2 top-2 z-10">
              <div className="rounded bg-background/90 px-2 py-1 text-xs font-medium backdrop-blur">
                {STAGE_WIDTH_IN}&quot; x {STAGE_HEIGHT_IN}&quot; Operating Area
              </div>
            </div>
            <GridOverlay rows={12} cols={12} />

            {/* Mic 1 */}
            <div
              className="absolute -translate-x-1/2 -translate-y-1/2 transition-all duration-500"
              style={{
                left: `${xPercent}%`,
                top: `${yPercent}%`,
              }}
            >
              <div className="relative">
                <div className="absolute inset-0 -m-2 animate-pulse rounded-full bg-primary/20 blur-md" />
                <div className="relative flex size-10 items-center justify-center rounded-full border-2 border-primary bg-card shadow-lg">
                  <Mic2 className="size-5 text-primary" />
                </div>
                <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 whitespace-nowrap text-xs font-medium">
                  Microphone
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-1 rounded-lg border bg-card p-3">
              <div className="text-xs font-medium text-muted-foreground">
                X Position
              </div>
              <div className="font-mono text-lg font-semibold">
                {position.x.toFixed(2)}
              </div>
              <div className="text-xs text-muted-foreground">
                inches (0-{STAGE_WIDTH_IN}&quot;)
              </div>
            </div>
            <div className="space-y-1 rounded-lg border bg-card p-3">
              <div className="text-xs font-medium text-muted-foreground">
                Y Position
              </div>
              <div className="font-mono text-lg font-semibold">
                {position.y.toFixed(2)}
              </div>
              <div className="text-xs text-muted-foreground">
                inches (0-{STAGE_HEIGHT_IN}&quot;)
              </div>
            </div>
            <div className="space-y-1 rounded-lg border bg-card p-3">
              <div className="text-xs font-medium text-muted-foreground">
                Z Position
              </div>
              <div className="font-mono text-lg font-semibold">
                {position.z.toFixed(2)}
              </div>
              <div className="text-xs text-muted-foreground">
                inches (0-{STAGE_Z_HEIGHT_IN}&quot;)
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
