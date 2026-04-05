import { useRef, useMemo, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Html } from '@react-three/drei';
import * as THREE from 'three';
import { listAllArchetypes, getNeighbors } from '../lib/subit';

function Monad({ archetype, active, isNeighbor, onSelect }) {
  const mesh = useRef();
  const [hovered, setHovered] = useState(false);
  
  // Alchemy Colors
  const colors = {
    ME: '#C8900A',
    WE: '#A82020',
    YOU: '#4A6070',
    THEY: '#7A9AAA'
  };

  const baseColor = colors[archetype.who] || '#ffffff';
  
  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    if (active) {
      mesh.current.scale.setScalar(1.4 + Math.sin(t * 5) * 0.1);
    } else if (isNeighbor) {
      mesh.current.scale.setScalar(1.1 + Math.sin(t * 3) * 0.05);
    } else {
      mesh.current.scale.setScalar(1.0);
    }
  });

  return (
    <mesh 
      ref={mesh} 
      position={[
        (archetype.who_idx - 1.5) * 1.5,
        (archetype.what_idx - 1.5) * 1.5,
        (archetype.when_idx - 1.5) * 1.5
      ]}
      onClick={() => onSelect(archetype)}
      onPointerOver={(e) => { e.stopPropagation(); setHovered(true); document.body.style.cursor = 'pointer'; }}
      onPointerOut={(e) => { setHovered(false); document.body.style.cursor = 'default'; }}
    >
      <sphereGeometry args={[0.3, 32, 32]} />
      <meshStandardMaterial 
        color={active ? '#ffffff' : baseColor} 
        emissive={active ? '#ffffff' : baseColor}
        emissiveIntensity={active || hovered ? 2 : (isNeighbor ? 1 : 0.2)}
        transparent
        opacity={active || isNeighbor || hovered ? 1 : 0.3}
      />
      
      {hovered && (
        <Html center zIndexRange={[100, 0]} position={[0, 0.5, 0]}>
          <div className="glass-tooltip">
            <strong>{archetype.name}</strong>
            <span className="coords">{archetype.who} / {archetype.what} / {archetype.when}</span>
            {active && <span className="operator">Focus</span>}
            {isNeighbor && <span className="operator">Neighbor</span>}
          </div>
        </Html>
      )}
    </mesh>
  );
}

function MonadCloud({ archetypes, activeState, onSelect }) {
  const whoOrder = ["THEY", "YOU", "ME", "WE"];
  const whatOrder = ["PRESERVE", "REDUCE", "EXPAND", "TRANSFORM"];
  const whenOrder = ["RELEASE", "INTEGRATE", "INITIATE", "SUSTAIN"];

  const activeNeighbors = useMemo(() => {
    if (!activeState) return new Set();
    return new Set(getNeighbors(activeState).map(n => n.name));
  }, [activeState]);

  const prepared = useMemo(() => {
    return archetypes.map(a => ({
      ...a,
      who_idx: whoOrder.indexOf(a.who),
      what_idx: whatOrder.indexOf(a.what),
      when_idx: whenOrder.indexOf(a.when)
    }));
  }, [archetypes]);

  return (
    <group>
      {prepared.map((a) => (
        <Monad 
          key={a.name} 
          archetype={a} 
          active={activeState?.name === a.name}
          isNeighbor={activeNeighbors.has(a.name)}
          onSelect={onSelect}
        />
      ))}
      
      {/* Central Axis Guides */}
      <gridHelper args={[6, 4, 0x1f766e, 0x162227]} rotation={[0, 0, 0]} position={[0, -2.5, 0]} opacity={0.1} transparent />
    </group>
  );
}

export default function VolumetricView({ activeState, onSelect }) {
  const archetypes = useMemo(() => listAllArchetypes(), []);

  return (
    <div className="volumetric-container display-seamless">
      <Canvas dpr={[1, 2]}>
        <PerspectiveCamera makeDefault position={[5, 5, 6]} fov={50} />
        <OrbitControls makeDefault enableDamping dampingFactor={0.05} autoRotate autoRotateSpeed={0.5} />
        
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <spotLight position={[-10, 10, 10]} angle={0.15} penumbra={1} intensity={1} />

        <MonadCloud 
          archetypes={archetypes} 
          activeState={activeState} 
          onSelect={onSelect} 
        />
        
        {/* Post-processing effects for that alchemical glow */}
        {/* Note: This requires EffectComposer from drei, which we added to package.json */}
      </Canvas>
    </div>
  );
}
