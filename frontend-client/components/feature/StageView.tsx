import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import { Mic2 } from "lucide-react";
import GridOverlay from "@/components/ui/GridOverlay";

interface StageViewProps {
  position?: { x: number; y: number; distance: number };
}

const defaultPosition = { x: 5, y: 3.5, distance: 3 };

export default function StageView({
  position = defaultPosition,
}: StageViewProps) {
  const xPercent = (position.x / 10) * 100;
  const yPercent = (position.y / 7) * 100;

  const micSeparation = position.distance / 2; // Half the distance for each mic
  const mic1XPercent = ((position.x - micSeparation) / 10) * 100;
  const mic2XPercent = ((position.x + micSeparation) / 10) * 100;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Stage View</CardTitle>
        <CardDescription>
          Dual microphone array - 10&apos; x 7&apos; operating area on stage
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div className="relative aspect-[10/7] w-full overflow-hidden rounded-lg border-2 border-primary/30 bg-muted/30">
            <div className="absolute left-2 top-2 z-10">
              <div className="rounded bg-background/90 px-2 py-1 text-xs font-medium backdrop-blur">
                10&apos; x 7&apos; Operating Area
              </div>
            </div>
            <GridOverlay rows={8} cols={10} />

            <svg className="absolute inset-0 size-full">
              <line
                x1={`${mic1XPercent}%`}
                y1={`${yPercent}%`}
                x2={`${mic2XPercent}%`}
                y2={`${yPercent}%`}
                stroke="hsl(var(--primary))"
                strokeWidth="2"
                strokeDasharray="4 4"
                className="opacity-60"
              />
            </svg>

            {/* Mic 1 */}
            <div
              className="absolute -translate-x-1/2 -translate-y-1/2 transition-all duration-500"
              style={{
                left: `${mic1XPercent}%`,
                top: `${yPercent}%`,
              }}
            >
              <div className="relative">
                <div className="absolute inset-0 -m-2 animate-pulse rounded-full bg-primary/20 blur-md" />
                <div className="relative flex size-10 items-center justify-center rounded-full border-2 border-primary bg-card shadow-lg">
                  <Mic2 className="size-5 text-primary" />
                </div>
                <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 whitespace-nowrap text-xs font-medium">
                  Mic 1
                </div>
              </div>
            </div>

            {/* Mic 2 */}
            <div
              className="absolute -translate-x-1/2 -translate-y-1/2 transition-all duration-500"
              style={{
                left: `${mic2XPercent}%`,
                top: `${yPercent}%`,
              }}
            >
              <div className="relative">
                <div className="absolute inset-0 -m-2 animate-pulse rounded-full bg-primary/20 blur-md" />
                <div className="relative flex size-10 items-center justify-center rounded-full border-2 border-primary bg-card shadow-lg">
                  <Mic2 className="size-5 text-primary" />
                </div>
                <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 whitespace-nowrap text-xs font-medium">
                  Mic 2
                </div>
              </div>
            </div>

            {/* Center point indicator */}
            <div
              className="absolute -translate-x-1/2 -translate-y-1/2 transition-all duration-500"
              style={{
                left: `${xPercent}%`,
                top: `${yPercent}%`,
              }}
            >
              <div className="size-2 rounded-full bg-accent" />
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
                feet (0-10&apos;)
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
                feet (0-7&apos;)
              </div>
            </div>
            <div className="space-y-1 rounded-lg border bg-card p-3">
              <div className="text-xs font-medium text-muted-foreground">
                Mic Spacing
              </div>
              <div className="font-mono text-lg font-semibold">
                {position.distance.toFixed(2)}
              </div>
              <div className="text-xs text-muted-foreground">
                feet (1-8&apos;)
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
