import Header from "@/components/layout/Header";
import PositionControl from "@/components/feature/PositionControl";
import PresetList from "@/components/feature/PresetList";
import StageView from "@/components/feature/StageView";
import SystemLog from "@/components/feature/SystemLog";

export default function Home() {
  return (
    <div className="min-h-screen bg-background p-4 md:p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <Header />
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="space-y-6">
            <StageView />
            <SystemLog />
          </div>
          <div className="space-y-6">
            <PositionControl />
            <PresetList />
          </div>
        </div>
      </div>
    </div>
  );
}

