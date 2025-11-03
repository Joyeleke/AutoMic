import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import { Button } from "../ui/Button";
import { PlusIcon } from "lucide-react";

const presets = [
  {
    name: "Solo Classical",
    description: "Center-front, close spacing",
    x: 5,
    y: 2,
    spacing: 2,
  },
  {
    name: "Big Band",
    description: "Center stage, wide spacing",
    x: 5,
    y: 3.5,
    spacing: 5,
  },
  {
    name: "Choir Recording",
    description: "Center-back, wide coverage",
    x: 5,
    y: 5,
    spacing: 6,
  },
  {
    name: "Stereo Pair",
    description: "Center, standard stereo spacing",
    x: 5,
    y: 3.5,
    spacing: 3,
  },
];

export default function PresetList() {
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
        {presets.map((preset) => (
          <div
            key={preset.name}
            className="flex items-center justify-between p-4 border rounded-lg"
          >
            <div>
              <h4 className="font-semibold">{preset.name}</h4>
              <p className="text-sm text-gray-500">{preset.description}</p>
              <div className="flex gap-4 mt-2 text-xs">
                <span>X: {preset.x}&apos;</span>
                <span>Y: {preset.y}&apos;</span>
                <span>Spacing: {preset.spacing}&apos;</span>
              </div>
            </div>
            <Button>Load</Button>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
