"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import { Label } from "@/components/ui/Label";
import { Button } from "../ui/Button";
import { Alert, AlertDescription } from "@/components/ui/Alert";
import { useState } from "react";
import { Input } from "../ui/Input";
import { Move, AlertCircle, Power} from "lucide-react";

export default function PositionControl() {
  const [isConnected, setIsConnected] = useState(false);

  return (
    <Card className="shadow-md border border-gray-200">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Position Control</CardTitle>
          <CardDescription className="mt-2">
            Control microphone array position (X: 10&#39;, Y: 7&#39;) and
            spacing
          </CardDescription>
        </div>
        <Button
          onClick={() => setIsConnected(!isConnected)}
          className="text-sm  text-white rounded-md px-4 py-2"
        >
           <Power className="size-4 mr-1" />
          {isConnected ? "Disconnect" : "Connect"}
        </Button>
      </CardHeader>
      <CardContent>
        {!isConnected && (
          <Alert variant="warning">
            <div className="flex items-center gap-3">
              <AlertCircle className="size-4" />
              <AlertDescription className="text-sm">
                Connect to ClearCore controller to enable position control
              </AlertDescription>
            </div>
          </Alert>
        )}
        <fieldset disabled={!isConnected}>
          <div className="flex justify-between py-4">
            <div className="flex flex-col gap-2">
              <Label htmlFor="x-position" className="text-sm font-medium">
                X Position (ft)
              </Label>
              <Input
                id="x-position"
                type="number"
                defaultValue="5"
                className="w-full"
              />
              <p className="text-xs text-gray-500">Range: 0-10&#39;</p>
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="y-position" className="text-sm font-medium">
                Y Position (ft)
              </Label>
              <Input
                id="y-position"
                type="number"
                defaultValue="3.5"
                className="w-full"
              />
              <p className="text-xs text-gray-500">Range: 0-7&#39;</p>
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="spacing" className="text-sm font-medium">
                Mic Spacing (ft)
              </Label>
              <Input
                id="spacing"
                type="number"
                defaultValue="3"
                className="w-full"
              />
              <p className="text-xs text-gray-500">Range: 1-8&#39;</p>
            </div>
          </div>
        </fieldset>
        <div className="grid grid-cols-3 gap-3 py-4">
          <Button
            className="text-sm bg-blue-500 text-white rounded-md px-4 py-2 col-span-2"
            disabled={!isConnected}
          >
            <Move className="size-4 mr-2" /> Apply Position
          </Button>
          <Button
            variant="outline"
            className="text-sm bg-gray-100 rounded-md px-4 py-2"
            disabled={!isConnected}
          >
            Home
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
