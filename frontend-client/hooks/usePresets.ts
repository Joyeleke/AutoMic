import { useState, useEffect } from "react";
import { Preset } from "@/types/motor";

const STORAGE_KEY = "automic_presets";

export function usePresets() {
  const [presets, setPresets] = useState<Preset[]>([]);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        setPresets(JSON.parse(stored));
      }
    } catch (err) {
      console.error("Failed to load presets from localStorage", err);
    } finally {
      setIsLoaded(true);
    }
  }, []);

  const savePreset = (preset: Preset) => {
    setPresets((current) => {
      const exists = current.findIndex((p) => p.name === preset.name);
      let newPresets: Preset[];

      if (exists !== -1) {
        newPresets = [...current];
        newPresets[exists] = preset;
      } else {
        newPresets = [...current, preset];
      }

      localStorage.setItem(STORAGE_KEY, JSON.stringify(newPresets));
      return newPresets;
    });
  };

  const deletePreset = (name: string) => {
    setPresets((current) => {
      const newPresets = current.filter((p) => p.name !== name);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(newPresets));
      return newPresets;
    });
  };

  return {
    presets,
    isLoaded,
    savePreset,
    deletePreset,
  };
}
