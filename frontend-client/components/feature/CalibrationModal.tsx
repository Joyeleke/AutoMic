"use client";

import { useState } from "react";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "../ui/Dialog";
import { Button } from "../ui/Button";
import { Input } from "../ui/Input";
import { Label } from "../ui/Label";
import { calibratePosition } from "@/lib/api";
import { Loader2, LocateFixed } from "lucide-react";
import { Position } from "@/types/motor";

interface CalibrationModalProps {
    isOpen: boolean;
    onClose: () => void;
    onCalibrateSuccess: (pos: Position) => void;
}

export default function CalibrationModal({
    isOpen,
    onClose,
    onCalibrateSuccess,
}: CalibrationModalProps) {
    const [pos, setPos] = useState<Position>({ x: 5, y: 3.5, z: 0 });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleInputChange = (key: keyof Position, value: string) => {
        if (value === "") {
            setPos((prev) => ({ ...prev, [key]: NaN }));
            return;
        }
        const num = parseFloat(value);
        if (!isNaN(num)) {
            setPos((prev) => ({ ...prev, [key]: num }));
        }
    };

    const handleCalibrate = async () => {
        setLoading(true);
        setError(null);

        if (isNaN(pos.x) || isNaN(pos.y) || isNaN(pos.z)) {
            setError("Please enter valid numbers for calibration.");
            setLoading(false);
            return;
        }

        try {
            const response = await calibratePosition(pos.x, pos.y, pos.z);
            onCalibrateSuccess(response.position);
            onClose();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Calibration failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        <LocateFixed className="size-5" />
                        System Calibration
                    </DialogTitle>
                    <DialogDescription>
                        Where is the microphone <strong>right now</strong>? Accessing this
                        resets the system&apos;s internal coordinates.
                    </DialogDescription>
                </DialogHeader>

                {error && (
                    <div className="bg-destructive/15 text-destructive text-sm p-3 rounded-md">
                        {error}
                    </div>
                )}

                <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="cal-x" className="text-right">
                            X (ft)
                        </Label>
                        <Input
                            id="cal-x"
                            type="number"
                            step="any"
                            value={isNaN(pos.x) ? "" : pos.x}
                            onChange={(e) => handleInputChange("x", e.target.value)}
                            className="col-span-3"
                        />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="cal-y" className="text-right">
                            Y (ft)
                        </Label>
                        <Input
                            id="cal-y"
                            type="number"
                            step="any"
                            value={isNaN(pos.y) ? "" : pos.y}
                            onChange={(e) => handleInputChange("y", e.target.value)}
                            className="col-span-3"
                        />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="cal-z" className="text-right">
                            Z (ft)
                        </Label>
                        <Input
                            id="cal-z"
                            type="number"
                            step="any"
                            value={isNaN(pos.z) ? "" : pos.z}
                            onChange={(e) => handleInputChange("z", e.target.value)}
                            className="col-span-3"
                        />
                    </div>
                </div>

                <DialogFooter>
                    <Button variant="outline" onClick={onClose} disabled={loading}>
                        Cancel
                    </Button>
                    <Button onClick={handleCalibrate} disabled={loading}>
                        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Confirm Position
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
