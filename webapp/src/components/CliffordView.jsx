import { useRef, useMemo, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Html } from '@react-three/drei';
import { listAllArchetypes, getNeighbors } from '../lib/subit';
import * as THREE from 'three';

const OP_COLORS = {
  WHO_SHIFT: '#C8900A',
  WHAT_SHIFT: '#A82020',
  WHEN_SHIFT: '#4A6070',
  INV: '#10766e'
};

const whoOrder = ["THEY", "YOU", "ME", "WE"];
const whatOrder = ["PRESERVE", "REDUCE", "EXPAND", "TRANSFORM"];
const whenOrder = ["RELEASE", "INTEGRATE", "INITIATE", "SUSTAIN"];

function MonadPoint({ state, x, y, z, isActive, isNeighbor, ringColor, onSelect }) {
  const [hovered, setHovered] = useState(false);
  const glowColor = isActive ? '#ffffff' : (isNeighbor ? OP_COLORS.INV : ringColor);

  return (
    <mesh 
      position={[x, y, z]}
      onClick={(e) => {
        e.stopPropagation();
        onSelect && onSelect(state);
      }}
      onPointerOver={(e) => { e.stopPropagation(); setHovered(true); document.body.style.cursor = 'pointer'; }}
      onPointerOut={(e) => { setHovered(false); document.body.style.cursor = 'default'; }}
    >
      <sphereGeometry args={[isActive ? 0.25 : (isNeighbor ? 0.15 : 0.06), 16, 16]} />
      <meshBasicMaterial 
        color={glowColor} 
        transparent 
        opacity={isActive || isNeighbor || hovered ? 1 : 0.4} 
      />
      {isActive && (
        <mesh>
          <sphereGeometry args={[0.35, 16, 16]} />
          <meshBasicMaterial color="#ffffff" transparent opacity={0.2} wireframe />
        </mesh>
      )}

      {hovered && (
        <Html center zIndexRange={[100, 0]} position={[0, 0.5, 0]}>
          <div className="glass-tooltip">
            <strong>{state.name}</strong>
            <span className="coords">{state.who}/{state.what}/{state.when}</span>
            {isActive && <span className="operator">Focus</span>}
            {isNeighbor && <span className="operator">Neighbor</span>}
          </div>
        </Html>
      )}
    </mesh>
  );
}

function HopfRings({ activeState, onSelect }) {
  const groupRef = useRef();
  
  const archetypes = useMemo(() => listAllArchetypes(), []);
  const activeNeighbors = useMemo(() => {
    if (!activeState) return new Set();
    return new Set(getNeighbors(activeState).map(n => n.name));
  }, [activeState]);

  // Create 4 intertwined rings (representing the 4 WHO groups mapping mapping 4D->3D)
  const rings = [
    { id: 'THEY', rot: [0, 0, 0], color: '#7A9AAA' },
    { id: 'YOU', rot: [Math.PI / 2, 0, Math.PI / 2], color: '#4A6070' },
    { id: 'ME', rot: [Math.PI / 4, Math.PI / 4, 0], color: '#C8900A' },
    { id: 'WE', rot: [-Math.PI / 4, -Math.PI / 4, 0], color: '#A82020' }
  ];

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = state.clock.getElapsedTime() * 0.15;
      groupRef.current.rotation.z = Math.sin(state.clock.getElapsedTime() * 0.1) * 0.2;
    }
  });

  return (
    <group ref={groupRef}>
      {rings.map((ring, rIdx) => {
        // Find states belonging to this ring
        const ringStates = archetypes.filter(a => a.who === ring.id);
        
        const handleRingClick = (e) => {
          e.stopPropagation();
          if (!onSelect) return;
          const local = e.object.worldToLocal(e.point.clone());
          
          let closest = null;
          let minD2 = Infinity;
          
          for (const state of ringStates) {
            const what_idx = whatOrder.indexOf(state.what);
            const when_idx = whenOrder.indexOf(state.when);
            const angleIdx = (what_idx * 4) + when_idx;
            const angle = (angleIdx / 16) * Math.PI * 2;
            const x = Math.cos(angle) * 4;
            const y = Math.sin(angle) * 4;
            
            const dx = x - local.x;
            const dy = y - local.y;
            const dz = 0 - local.z;
            const d2 = dx*dx + dy*dy + dz*dz;
            
            if (d2 < minD2) {
              minD2 = d2;
              closest = state;
            }
          }
          if (closest) onSelect(closest);
        };

        return (
          <group key={ring.id} rotation={ring.rot}>
            {/* The Villarceau-like circle track */}
            <mesh onClick={handleRingClick} onPointerOver={(e) => document.body.style.cursor = 'crosshair'} onPointerOut={() => document.body.style.cursor = 'default'}>
              <torusGeometry args={[4, 0.3, 16, 64]} />
              <meshBasicMaterial color={ring.color} transparent opacity={0.1} />
            </mesh>
            
            {/* The 16 Monads on this ring */}
            {ringStates.map((state) => {
              // Position along the ring based on WHAT and WHEN
              const what_idx = whatOrder.indexOf(state.what);
              const when_idx = whenOrder.indexOf(state.when);
              
              // 16 states total per ring. Combine what and when to uniquely map them [0..15]
              const angleIdx = (what_idx * 4) + when_idx;
              const angle = (angleIdx / 16) * Math.PI * 2;
              
              const x = Math.cos(angle) * 4;
              const y = Math.sin(angle) * 4;
              const z = 0;

              const isActive = activeState?.name === state.name;
              const isNeighbor = activeNeighbors.has(state.name);
              
              return (
                <MonadPoint 
                  key={state.name}
                  state={state}
                  x={x} y={y} z={z}
                  isActive={isActive}
                  isNeighbor={isNeighbor}
                  ringColor={ring.color}
                  onSelect={onSelect}
                />
              );
            })}
          </group>
        );
      })}
    </group>
  );
}

export default function CliffordView({ activeState, onSelect }) {
  return (
    <div className="volumetric-container display-seamless">
      <div className="floating-label">
        <span className="dim-tag">S3 Projection</span>
        <strong>Clifford Torus</strong>
      </div>
      <Canvas dpr={[1, 2]}>
        <PerspectiveCamera makeDefault position={[0, 0, 9]} fov={55} />
        <OrbitControls makeDefault enableDamping autoRotate autoRotateSpeed={0.5} />
        <ambientLight intensity={0.5} />
        <HopfRings activeState={activeState} onSelect={onSelect} />
      </Canvas>
    </div>
  );
}
