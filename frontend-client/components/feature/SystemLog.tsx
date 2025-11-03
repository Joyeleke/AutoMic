import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import { Terminal } from "lucide-react";

const logEntries = [
  { time: "2:03:05 PM", message: "Connected to ClearCore controller" },
  { time: "2:03:08 PM", message: "Disconnected from controller" },
];

export default function SystemLog() {
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
          {logEntries.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No messages yet. System ready.
            </p>
          ) : (
            <div className="space-y-2">
              {logEntries.map((msg, index) => (
                <div key={index} className="flex items-center gap-3 text-sm">
                  <span className="font-mono text-xs text-muted-foreground">
                    {msg.time}
                  </span>
                  <span className="text-foreground">{msg.message}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
