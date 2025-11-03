import { cn } from "@/lib/utils"

type GridOverlayProps = {
  rows?: number
  cols?: number
  className?: string
  lineClassName?: string
}

export function GridOverlay({
  rows = 8,
  cols = 10,
  className,
  lineClassName = "border-border/30",
}: GridOverlayProps) {
  const horizontalCount = Math.max(0, rows - 1)
  const verticalCount = Math.max(0, cols - 1)

  return (
    <div className={cn("absolute inset-0 pointer-events-none", className)}>
      {Array.from({ length: horizontalCount }).map((_, i) => (
        <div
          key={`h-${i}`}
          className={cn("absolute left-0 right-0 border-t", lineClassName)}
          style={{ top: `${((i + 1) / rows) * 100}%` }}
        />
      ))}
      {Array.from({ length: verticalCount }).map((_, i) => (
        <div
          key={`v-${i}`}
          className={cn("absolute top-0 bottom-0 border-l", lineClassName)}
          style={{ left: `${((i + 1) / cols) * 100}%` }}
        />
      ))}
    </div>
  )
}

export default GridOverlay
