import LatticeView from './LatticeView';
import VolumetricView from './VolumetricView';
import TopologicalView from './TopologicalView';
import CliffordView from './CliffordView';

export default function UnifiedObservatory({ activeState, onSelect }) {
  return (
    <div className="unified-observatory quadrant-layout">
      
      <div className="observatory-panel seam-panel">
        <div className="floating-label">
          <span className="dim-tag">2D Logic</span>
          <strong>8x8 Algebraic Lattice</strong>
        </div>
        <div className="panel-content seamless">
          <LatticeView activeState={activeState} onSelect={onSelect} />
        </div>
      </div>

      <div className="observatory-panel seam-panel">
        <div className="floating-label">
          <span className="dim-tag">3D Projection</span>
          <strong>4x4x4 Synchronized Cube</strong>
        </div>
        <div className="panel-content seamless">
          <VolumetricView activeState={activeState} onSelect={onSelect} />
        </div>
      </div>

      <div className="observatory-panel seam-panel">
        <div className="floating-label">
          <span className="dim-tag">Topology</span>
          <strong>3-Torus Manifold</strong>
        </div>
        <div className="panel-content seamless">
          <TopologicalView activeState={activeState} onSelect={onSelect} />
        </div>
      </div>

      <div className="observatory-panel seam-panel">
        <CliffordView activeState={activeState} onSelect={onSelect} />
      </div>

    </div>
  );
}
