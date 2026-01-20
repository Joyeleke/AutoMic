import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import { Button } from "../ui/Button";
import { PlusIcon } from "lucide-react";
import { Position } from "@/types/motor";

const presets: Position[] = [
  { x: 5, y: 2, z: 2 },
  { x: 5, y: 3.5, z: 5 },
  { x: 5, y: 5, z: 6 },
  { x: 5, y: 3.5, z: 3 },
];

const presetNames = [
  { name: "Solo Classical", description: "Center-front, close spacing" },
  { name: "Big Band", description: "Center stage, wide spacing" },
  { name: "Choir Recording", description: "Center-back, wide coverage" },
  { name: "Stereo Pair", description: "Center, standard stereo spacing" },
];

interface PresetListProps {
  onLoadPreset: (position: Position) => void;
}

export default function PresetList({ onLoadPreset }: PresetListProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Preset Positions</CardTitle>
          <CardDescription className="mt-1">
            Save and recall microphone positions
          </CardDescription>
        </div>
        <Button variant="outline" size="sm">
          <PlusIcon className="h-4 w-4 mr-2" />
          Save Current as Preset
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        {presets.map((preset, index) => (
          <div
            key={presetNames[index].name}
            className="flex items-center justify-between p-4 border rounded-lg"
          >
            <div>
              <h4 className="font-semibold">{presetNames[index].name}</h4>
              <p className="text-sm text-gray-500">
                {presetNames[index].description}
              </p>
              <div className="flex gap-4 mt-2 text-xs">
                <span>X: {preset.x}&apos;</span>
                <span>Y: {preset.y}&apos;</span>
                <span>Z: {preset.z}&apos;</span>
              </div>
            </div>
            <Button onClick={() => onLoadPreset(preset)}>Load</Button>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
