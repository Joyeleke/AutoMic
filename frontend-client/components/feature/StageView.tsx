import { useMemo } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import { Info } from "lucide-react";
import { Position, SystemConfig } from "@/types/motor";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Grid, Line, Edges } from "@react-three/drei";
import * as THREE from "three";

interface StageViewProps {
  config: SystemConfig | null;
  position: Position;
}

const DEFAULT_MOTORS = [
  { id: "M1", pos: [77.16, 81.48, 95.16] },
  { id: "M2", pos: [147.0, 146.04, 51.0] },
  { id: "M3", pos: [9.0, 146.04, 51.0] },
  { id: "M4", pos: [77.16, 0.0, 51.0] },
];

function Scene({
  position,
  config,
}: {
  position: Position;
  config: SystemConfig | null;
}) {
  const STAGE_WIDTH_IN = config?.geometry.width || 147.0;
  const STAGE_HEIGHT_IN = config?.geometry.height || 146.04;
  const STAGE_Z_HEIGHT_IN = config?.geometry.z_height || 95.16;

  const widthFt = STAGE_WIDTH_IN / 12;
  const heightFt = STAGE_HEIGHT_IN / 12;

  const motors = useMemo(() => {
    if (config?.geometry.motors) {
      const m = config.geometry.motors;
      return [
        { id: "M1", pos: m.m1 },
        { id: "M2", pos: m.m2 },
        { id: "M3", pos: m.m3 },
        { id: "M4", pos: m.m4 },
      ];
    }
    return DEFAULT_MOTORS;
  }, [config]);

  const targetPos = useMemo(
    () => new THREE.Vector3(position.x / 12, position.z / 12, position.y / 12),
    [position],
  );

  return (
    <>
      <ambientLight intensity={0.6} />
      <directionalLight
        position={[10, 20, 10]}
        intensity={1.5}
        color="#ffffff"
      />
      <spotLight
        position={[targetPos.x, targetPos.y + 10, targetPos.z]}
        angle={0.4}
        penumbra={1}
        intensity={1.5}
        color="#ffffff"
        castShadow
      />

      {/* Subtle Floor Grid */}
      <Grid
        position={[widthFt / 2, 0, heightFt / 2]}
        args={[widthFt * 2, heightFt * 2]}
        cellSize={1}
        cellThickness={1}
        cellColor="#cbd5e1"
        sectionSize={3}
        sectionThickness={1.5}
        sectionColor="#94a3b8"
        fadeDistance={25}
        fadeStrength={1.5}
      />

      {/* Frame Boundaries */}
      <mesh position={[widthFt / 2, STAGE_Z_HEIGHT_IN / 12 / 2, heightFt / 2]}>
        <boxGeometry args={[widthFt, STAGE_Z_HEIGHT_IN / 12, heightFt]} />
        <meshBasicMaterial
          transparent
          opacity={0}
          depthWrite={false}
          color="#ffffff"
        />
        <Edges color="#cbd5e1" transparent opacity={0.6} />
      </mesh>

      {/* Motors & Cables */}
      {motors.map((motor: { id: string; pos: number[] }) => {
        const motorPos = new THREE.Vector3(
          motor.pos[0] / 12,
          motor.pos[2] / 12,
          motor.pos[1] / 12,
        );
        return (
          <group key={motor.id}>
            {/* 3D Motor / Winch Assembly */}
            <group position={motorPos}>
              {/* Stepper Motor Housing */}
              <mesh position={[0.15, 0, 0]}>
                <boxGeometry args={[0.25, 0.25, 0.35]} />
                <meshStandardMaterial
                  color="#475569"
                  metalness={0.5}
                  roughness={0.6}
                />
              </mesh>
              {/* Spool Drum */}
              <mesh rotation={[Math.PI / 2, 0, 0]}>
                <cylinderGeometry args={[0.12, 0.12, 0.3, 32]} />
                <meshStandardMaterial
                  color="#94a3b8"
                  metalness={0.8}
                  roughness={0.4}
                />
              </mesh>
            </group>
            {/* Cable (Darker Slate color) */}
            <Line
              points={[motorPos, targetPos]}
              color="#475569"
              lineWidth={2}
              transparent
              opacity={0.8}
            />
          </group>
        );
      })}

      {/* 3D Microphone Target */}
      <group position={targetPos}>
        {/* Attachment Ring */}
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[0.2, 0.03, 16, 32]} />
          <meshStandardMaterial
            color="#94a3b8"
            metalness={0.9}
            roughness={0.2}
          />
        </mesh>

        {/* Mic Body / Handle */}
        <mesh position={[0, -0.3, 0]}>
          <cylinderGeometry args={[0.08, 0.06, 0.5, 32]} />
          <meshStandardMaterial
            color="#334155"
            metalness={0.6}
            roughness={0.4}
          />
        </mesh>

        {/* Mic Windscreen / Capsule Grid */}
        <mesh position={[0, 0.05, 0]}>
          <capsuleGeometry args={[0.12, 0.15, 16, 32]} />
          <meshStandardMaterial
            color="#cbd5e1"
            metalness={0.8}
            roughness={0.5}
            wireframe={true}
          />
        </mesh>

        {/* Inner solid capsule to block see-through wireframe */}
        <mesh position={[0, 0.05, 0]}>
          <capsuleGeometry args={[0.1, 0.13, 16, 16]} />
          <meshStandardMaterial color="#020617" />
        </mesh>
      </group>

      <OrbitControls
        makeDefault
        target={[widthFt / 2, STAGE_Z_HEIGHT_IN / 12 / 2, heightFt / 2]}
        maxPolarAngle={Math.PI / 2 - 0.05}
        minDistance={5}
        maxDistance={40}
      />
    </>
  );
}

export default function StageView({ config, position }: StageViewProps) {
  const STAGE_WIDTH_IN = config?.geometry.width || 147.0;
  const STAGE_HEIGHT_IN = config?.geometry.height || 146.04;
  const STAGE_Z_HEIGHT_IN = config?.geometry.z_height || 95.16;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Stage View</CardTitle>
            <CardDescription>
              {STAGE_WIDTH_IN}&quot; x {STAGE_HEIGHT_IN}&quot; Operating Area
            </CardDescription>
          </div>
          <div className="flex items-center space-x-1.5 text-xs text-muted-foreground bg-muted/50 px-2.5 py-1 rounded-md border">
            <Info className="size-3.5" />
            <span>Drag to rotate</span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* 3D Canvas Area */}
          <div className="relative aspect-[10/7] w-full overflow-hidden rounded-lg border-2 border-primary/30 bg-muted/30">
            <Canvas
              camera={{ position: [20, 15, 20], fov: 45 }}
              className="w-full h-full"
              gl={{ antialias: true, alpha: true }}
            >
              <Scene position={position} config={config} />
            </Canvas>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-1 rounded-lg border bg-card p-3 shadow-sm">
              <div className="text-xs font-medium text-muted-foreground">
                X Position
              </div>
              <div className="font-mono text-lg font-semibold">
                {position.x.toFixed(2)}
              </div>
              <div className="text-xs text-muted-foreground">
                inches (0-{STAGE_WIDTH_IN}&quot;)
              </div>
            </div>
            <div className="space-y-1 rounded-lg border bg-card p-3 shadow-sm">
              <div className="text-xs font-medium text-muted-foreground">
                Y Position
              </div>
              <div className="font-mono text-lg font-semibold">
                {position.y.toFixed(2)}
              </div>
              <div className="text-xs text-muted-foreground">
                inches (0-{STAGE_HEIGHT_IN}&quot;)
              </div>
            </div>
            <div className="space-y-1 rounded-lg border bg-card p-3 shadow-sm">
              <div className="text-xs font-medium text-muted-foreground">
                Z Position
              </div>
              <div className="font-mono text-lg font-semibold">
                {position.z.toFixed(2)}
              </div>
              <div className="text-xs text-muted-foreground">
                inches (0-{STAGE_Z_HEIGHT_IN}&quot;)
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
