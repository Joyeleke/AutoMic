import StatusBar from "@/components/feature/StatusBar";

export default function Header() {
  return (
    <header className="flex items-center justify-between">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">AutoMic Control</h1>
        <p className="text-sm text-muted-foreground">
          Ruth Lilly Performance Hall - UIndy Music Department
        </p>
      </div>
      <StatusBar />
    </header>
  );
}
