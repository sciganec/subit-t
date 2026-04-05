import { useRef, useMemo, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Html } from '@react-three/drei';
import { listAllArchetypes, getNeighbors, getTorusCoords } from '../lib/subit';

const OP_COLORS = {
  WHO_SHIFT: '#C8900A',
  WHAT_SHIFT: '#A82020',
  WHEN_SHIFT: '#4A6070',
  INV: '#10766e'
};

function MonadPoint({ archetype, activeState, neighborData, onSelect }) {
  const [hovered, setHovered] = useState(false);
  const pos = getTorusCoords(archetype);
  const isActive = activeState?.name === archetype.name;
  const isNeighbor = !!neighborData;
  const color = isActive ? '#ffffff' : (neighborData ? OP_COLORS[neighborData.op] : '#162227');

  return (
    <mesh 
      position={pos}
      onClick={(e) => {
        e.stopPropagation();
        onSelect && onSelect(archetype);
      }}
      onPointerOver={(e) => { e.stopPropagation(); setHovered(true); document.body.style.cursor = 'pointer'; }}
      onPointerOut={(e) => { setHovered(false); document.body.style.cursor = 'default'; }}
    >
      <sphereGeometry args={[isActive ? 0.15 : (isNeighbor ? 0.1 : 0.04), 8, 8]} />
      <meshBasicMaterial color={color} transparent opacity={isActive || isNeighbor || hovered ? 1 : 0.3} />
      
      {hovered && (
        <Html center zIndexRange={[100, 0]} position={[0, 0.4, 0]}>
          <div className="glass-tooltip">
            <strong>{archetype.name}</strong>
            <span className="coords">{archetype.who}/{archetype.what}/{archetype.when}</span>
            {isActive && <span className="operator">Focus</span>}
            {isNeighbor && <span className="operator">{neighborData.op}</span>}
          </div>
        </Html>
      )}
    </mesh>
  );
}

function StatePoints({ activeState, onSelect }) {
  const archetypes = useMemo(() => listAllArchetypes(), []);
  const neighbors = useMemo(() => activeState ? getNeighbors(activeState) : [], [activeState]);
  const neighborNames = useMemo(() => new Set(neighbors.map(n => n.name)), [neighbors]);

  return (
    <group>
      {archetypes.map((a) => {
        const isNeighbor = neighborNames.has(a.name);
        const neighborData = isNeighbor ? neighbors.find(n => n.name === a.name) : null;
        return (
          <MonadPoint 
            key={a.name} 
            archetype={a} 
            activeState={activeState}
            neighborData={neighborData}
            onSelect={onSelect}
          />
        );
      })}
    </group>
  );
}

function PeriodicLattice({ activeState, onSelect }) {
  const neighbors = useMemo(() => activeState ? getNeighbors(activeState) : [], [activeState]);
  
  const opDirs = {
    WHO_SHIFT: [1, 0, 0],
    WHAT_SHIFT: [0, 1, 0],
    WHEN_SHIFT: [0, 0, 1],
    INV: [-1, -1, -1]
  };

  const cubes = useMemo(() => {
    const arr = [];
    for (let x = -1; x <= 1; x++) {
      for (let y = -1; y <= 1; y++) {
        for (let z = -1; z <= 1; z++) {
          arr.push({ x, y, z });
        }
      }
    }
    return arr;
  }, []);

  return (
    <group>
      {cubes.map((c, i) => {
        const isCenter = c.x === 0 && c.y === 0 && c.z === 0;
        let neighborOp = null;
        for (const [op, dir] of Object.entries(opDirs)) {
           if (c.x === dir[0] && c.y === dir[1] && c.z === dir[2]) {
             neighborOp = op;
             break;
           }
        }

        const color = isCenter ? '#ffffff' : (neighborOp ? OP_COLORS[neighborOp] : '#0f766e');
        const opacity = isCenter ? 0.8 : (neighborOp ? 0.4 : 0.05);

        return (
          <mesh 
            key={i} 
            position={[c.x * 4, c.y * 4, c.z * 4]}
            onClick={(e) => {
              e.stopPropagation();
              if (neighborOp && onSelect) {
                const neighbor = neighbors.find(n => n.op === neighborOp);
                if (neighbor) onSelect(neighbor.state);
              }
            }}
          >
            <boxGeometry args={[2, 2, 2]} />
            <meshBasicMaterial color={color} wireframe={!isCenter && !neighborOp} transparent opacity={opacity} />
          </mesh>
        );
      })}
    </group>
  );
}

function ManifoldLayer({ activeState, onSelect }) {
  const groupRef = useRef();

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.003;
    }
  });

  const archetypes = useMemo(() => listAllArchetypes(), []);
  
  const handleSurfaceClick = (e) => {
    e.stopPropagation();
    if (!onSelect) return;
    
    // Convert world point to local space of the mesh
    const localPoint = e.object.worldToLocal(e.point.clone());
    
    // Find nearest archetype
    let closest = null;
    let minD2 = Infinity;
    
    for (const a of archetypes) {
      const pos = getTorusCoords(a);
      const dx = pos[0] - localPoint.x;
      const dy = pos[1] - localPoint.y;
      const dz = pos[2] - localPoint.z;
      const d2 = dx*dx + dy*dy + dz*dz;
      if (d2 < minD2) {
        minD2 = d2;
        closest = a;
      }
    }
    
    if (closest) onSelect(closest);
  };

  return (
    <group ref={groupRef}>
      {/* Torus Projection */}
      <group position={[-4, 0, 0]}>
        <mesh onClick={handleSurfaceClick} onPointerOver={(e) => document.body.style.cursor = 'crosshair'} onPointerOut={() => document.body.style.cursor = 'default'}>
          <torusGeometry args={[3, 1, 16, 32]} />
          <meshBasicMaterial color="#0f766e" wireframe transparent opacity={0.2} />
        </mesh>
        <StatePoints activeState={activeState} onSelect={onSelect} />
      </group>

      {/* Periodic Lattice Projection */}
      <group position={[4, 0, 0]} scale={0.7}>
        <PeriodicLattice activeState={activeState} onSelect={onSelect} />
      </group>
    </group>
  );
}

export default function TopologicalView({ activeState, onSelect }) {
  return (
    <div className="volumetric-container display-seamless">
      <Canvas dpr={[1, 2]}>
        <PerspectiveCamera makeDefault position={[0, 8, 12]} fov={45} />
        <OrbitControls makeDefault enableDamping />
        
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        
        <ManifoldLayer activeState={activeState} onSelect={onSelect} />
      </Canvas>
    </div>
  );
}
