import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import { Terminal } from "lucide-react";
import type { LogEntry } from "@/types/motor";

interface SystemLogProps {
  logs: LogEntry[];
}

export default function SystemLog({ logs }: SystemLogProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Terminal className="size-6 text-muted-foreground" />
          <div>
            <CardTitle className="text-lg">System Log</CardTitle>
            <CardDescription>
              Real-time system feedback and status messages
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[175px] w-full overflow-y-auto rounded-md border bg-muted/30 p-4">
          {logs.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No messages yet. System ready.
            </p>
          ) : (
            <div className="space-y-2">
              {logs.map((entry, index) => (
                <div
                  key={index}
                  className={`flex items-start gap-3 text-sm ${
                    entry.level === "error"
                      ? "text-red-600"
                      : entry.level === "warning"
                      ? "text-yellow-600"
                      : "text-foreground"
                  }`}
                >
                  <span className="font-mono text-xs text-muted-foreground whitespace-nowrap">
                    {entry.time}
                  </span>
                  <span className="flex-1">{entry.message}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
