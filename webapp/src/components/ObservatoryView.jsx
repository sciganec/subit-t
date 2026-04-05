import { useState } from 'react';
import LatticeView from './LatticeView';
import VolumetricView from './VolumetricView';
import TopologicalView from './TopologicalView';
import { getAxisLogic } from '../lib/subit';

export default function ObservatoryView({ activeState, onSelect }) {
  const [activeTab, setActiveTab] = useState('lattice'); // ["lattice", "cube", "manifold"]
  const logic = getAxisLogic();

  return (
    <div className="observatory-view">
      <div className="observatory-header">
        <h2>The Monadology Grid</h2>
        <div className="tab-switcher">
          <button 
            className={`soft-button ${activeTab === 'lattice' ? 'is-active' : ''}`}
            onClick={() => setActiveTab('lattice')}
          >
            8x8 Lattice
          </button>
          <button 
            className={`soft-button ${activeTab === 'cube' ? 'is-active' : ''}`}
            onClick={() => setActiveTab('cube')}
          >
            4x4x4 Cube
          </button>
          <button 
            className={`soft-button ${activeTab === 'manifold' ? 'is-active' : ''}`}
            onClick={() => setActiveTab('manifold')}
          >
            Manifold
          </button>
        </div>
      </div>

      <div className="observatory-content">
        {activeTab === 'lattice' && <LatticeView activeState={activeState} onSelect={onSelect} />}
        {activeTab === 'cube' && <VolumetricView activeState={activeState} onSelect={onSelect} />}
        {activeTab === 'manifold' && <TopologicalView activeState={activeState} />}
      </div>

      {activeState && (
        <div className="logic-panel">
          <div className="monad-detail-card">
            <h3>{activeState.name}</h3>
            <div className="meta">
              {activeState.who} / {activeState.what} / {activeState.when}
            </div>
            <p className="role-desc">
              {activeState.logic?.role || `${activeState.name} archetype.`}
            </p>
          </div>
          
          <div className="logic-explainer">
            <div className="logic-step">
              <strong>WHO // Attention</strong>
              <span>{activeState.who}: {logic.WHO[activeState.who]}</span>
            </div>
            <div className="logic-step">
              <strong>WHAT // Operation</strong>
              <span>{activeState.what}: {logic.WHAT[activeState.what]}</span>
            </div>
            <div className="logic-step">
              <strong>WHEN // Phase</strong>
              <span>{activeState.when}: {logic.WHEN[activeState.when]}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
