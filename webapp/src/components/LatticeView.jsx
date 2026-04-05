import { useMemo } from 'react';
import { listAllArchetypes, getNeighbors } from '../lib/subit';

export default function LatticeView({ activeState, onSelect }) {
  const archetypes = useMemo(() => listAllArchetypes(), []);
  
  // Arrange archetypes in 8x8 grid based on row/col
  const grid = useMemo(() => {
    const matrix = Array(8).fill(null).map(() => Array(8).fill(null));
    archetypes.forEach(a => {
      matrix[a.row][a.col] = a;
    });
    return matrix;
  }, [archetypes]);

  const activeNeighbors = useMemo(() => {
    if (!activeState) return new Set();
    return new Set(getNeighbors(activeState).map(n => n.name));
  }, [activeState]);

  return (
    <div className="lattice-container">
      <div className="lattice-grid">
        {grid.map((row, rIdx) => (
          row.map((cell, cIdx) => {
            const isActive = activeState?.name === cell?.name;
            const isNeighbor = activeNeighbors.has(cell?.name);
            
            return (
              <div 
                key={`${rIdx}-${cIdx}`}
                className={`lattice-cell ${isActive ? 'is-active' : ''} ${isNeighbor ? 'is-neighbor' : ''}`}
                onClick={() => onSelect(cell)}
              >
                <div className="cell-inner">
                  <span className="cell-name">{cell?.name.substring(0, 3)}</span>
                </div>
                {/* Tooltip on hover */}
                <div className="lattice-tooltip glass-tooltip">
                  <strong>{cell?.name}</strong>
                  <span className="coords">{cell?.who}/{cell?.what}/{cell?.when}</span>
                  {isActive && <span className="operator">Focus</span>}
                  {isNeighbor && <span className="operator">Neighbor</span>}
                </div>
              </div>
            );
          })
        ))}
      </div>
      <div className="lattice-legend">
        <div className="legend-item">
          <span className="dot active"></span> 
          <span>Active Posture</span>
        </div>
        <div className="legend-item">
          <span className="dot neighbor"></span> 
          <span>Logical Neighbors (Adjacency)</span>
        </div>
      </div>
    </div>
  );
}
