"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import { Button } from "../ui/Button";
import { PlusIcon, Trash2, Pencil } from "lucide-react";
import { Position, Preset } from "@/types/motor";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/Dialog";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";

interface PresetListProps {
  currentPosition: Position;
  presets: Preset[];
  onLoadPreset: (position: Position) => void;
  onSavePreset: (preset: Preset) => void;
  onDeletePreset: (name: string) => void;
}

export default function PresetList({
  currentPosition,
  presets,
  onLoadPreset,
  onSavePreset,
  onDeletePreset,
}: PresetListProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<"create" | "edit">("create");
  const [nameInput, setNameInput] = useState("");
  const [descInput, setDescInput] = useState("");

  const openCreateModal = () => {
    setModalMode("create");
    setNameInput("");
    setDescInput("");
    setIsModalOpen(true);
  };

  const openEditModal = (preset: Preset) => {
    setModalMode("edit");
    setNameInput(preset.name);
    setDescInput(preset.description);
    setIsModalOpen(true);
  };

  const handleSave = () => {
    if (!nameInput.trim()) return;
    
    onSavePreset({
      name: nameInput.trim(),
      description: descInput.trim(),
      position: currentPosition,
    });
    setIsModalOpen(false);
  };

  return (
    <>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Preset Positions</CardTitle>
            <CardDescription className="mt-1">
              Save and recall microphone positions
            </CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={openCreateModal}>
            <PlusIcon className="h-4 w-4 mr-2" />
            Save Current
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {presets.length === 0 && (
            <p className="text-sm text-gray-500 italic">No presets saved yet.</p>
          )}
          {presets.map((preset) => (
            <div
              key={preset.name}
              className="flex items-center justify-between p-4 border rounded-lg"
            >
              <div>
                <h4 className="font-semibold">{preset.name}</h4>
                <p className="text-sm text-gray-500">
                  {preset.description || "No description"}
                </p>
                <div className="flex gap-4 mt-2 text-xs">
                  <span>X: {preset.position.x}&quot;</span>
                  <span>Y: {preset.position.y}&quot;</span>
                  <span>Z: {preset.position.z}&quot;</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button size="sm" variant="ghost" onClick={() => openEditModal(preset)} title="Update to current position">
                  <Pencil className="h-4 w-4" />
                </Button>
                <Button size="sm" variant="ghost" className="text-red-500 hover:text-red-700 hover:bg-red-50" onClick={() => onDeletePreset(preset.name)}>
                  <Trash2 className="h-4 w-4" />
                </Button>
                <Button size="sm" onClick={() => onLoadPreset(preset.position)}>Load</Button>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {modalMode === "create" ? "Save New Preset" : "Update Preset"}
            </DialogTitle>
            <DialogDescription>
              {modalMode === "create"
                ? "This will save the current microphone position as a new preset."
                : "This will update the preset's description and overwrite coordinates to the current position."}
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="name" className="text-right">
                Name
              </Label>
              <Input
                id="name"
                value={nameInput}
                onChange={(e) => setNameInput(e.target.value)}
                className="col-span-3"
                disabled={modalMode === "edit"} 
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="description" className="text-right">
                Description
              </Label>
              <Input
                id="description"
                value={descInput}
                onChange={(e) => setDescInput(e.target.value)}
                className="col-span-3"
                placeholder="Optional"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4 text-sm mt-2 text-gray-500">
              <span className="text-right">Position:</span>
              <span className="col-span-3">
                X: {currentPosition.x}&quot;, Y: {currentPosition.y}&quot;, Z: {currentPosition.z}&quot;
              </span>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={!nameInput.trim()}>
              Save Preset
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
