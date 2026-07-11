import React, { useState } from 'react';

const Settings = () => {
  const [settings, setSettings] = useState({
    temperature: 0.0,
    seed: 40,
    top_p: 0.95,
    top_k: 40,
    max_tokens: 4096,
    deterministic: true,
    cache_enabled: true,
    accuracy_scoring: true
  });

  const updateSetting = (key, value) => {
    if (key === 'temperature' && value !== 0) {
      alert('Temperature must be 0 for deterministic mode');
      return;
    }
    if (key === 'seed' && value !== 40) {
      alert('Seed must be 40 for reproducibility');
      return;
    }
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="settings-container">
      <h2>⚙️ Advanced Settings</h2>
      <p className="subtitle">All settings are locked to deterministic mode (Temp=0, Seed=40)</p>
      
      <div className="settings-grid">
        <div className="setting-card">
          <label>🌡️ Temperature</label>
          <div className="value-display">0.0 (Fixed)</div>
          <input
            type="range"
            min="0"
            max="0"
            value={0}
            disabled
          />
          <small>Deterministic mode enforced</small>
        </div>
        
        <div className="setting-card">
          <label>🌱 Seed</label>
          <div className="value-display">40 (Fixed)</div>
          <input
            type="number"
            value={40}
            disabled
          />
          <small>Fixed for reproducibility</small>
        </div>
        
        <div className="setting-card">
          <label>🎯 Top-P</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={settings.top_p}
            onChange={(e) => updateSetting('top_p', parseFloat(e.target.value))}
          />
          <span>{settings.top_p}</span>
        </div>
        
        <div className="setting-card">
          <label>📊 Top-K</label>
          <input
            type="range"
            min="1"
            max="100"
            value={settings.top_k}
            onChange={(e) => updateSetting('top_k', parseInt(e.target.value))}
          />
          <span>{settings.top_k}</span>
        </div>
        
        <div className="setting-card">
          <label>📝 Max Tokens</label>
          <input
            type="range"
            min="100"
            max="8192"
            step="100"
            value={settings.max_tokens}
            onChange={(e) => updateSetting('max_tokens', parseInt(e.target.value))}
          />
          <span>{settings.max_tokens}</span>
        </div>
        
        <div className="setting-card">
          <label>💾 Cache</label>
          <label className="switch">
            <input
              type="checkbox"
              checked={settings.cache_enabled}
              onChange={(e) => updateSetting('cache_enabled', e.target.checked)}
            />
            <span className="slider"></span>
          </label>
          <small>{settings.cache_enabled ? 'Enabled' : 'Disabled'}</small>
        </div>
        
        <div className="setting-card">
          <label>📊 Accuracy Scoring</label>
          <label className="switch">
            <input
              type="checkbox"
              checked={settings.accuracy_scoring}
              onChange={(e) => updateSetting('accuracy_scoring', e.target.checked)}
            />
            <span className="slider"></span>
          </label>
          <small>{settings.accuracy_scoring ? 'Enabled' : 'Disabled'}</small>
        </div>
        
        <div className="setting-card highlight">
          <label>🔒 Mode</label>
          <div className="mode-badge">DETERMINISTIC</div>
          <small>Temperature: 0 | Seed: 40</small>
        </div>
      </div>
      
      <div className="presets">
        <h3>💾 Presets</h3>
        <div className="preset-buttons">
          <button onClick={() => {
            setSettings(prev => ({ ...prev, top_p: 0.95, top_k: 40, max_tokens: 4096 }));
          }}>🎯 Production</button>
          <button onClick={() => {
            setSettings(prev => ({ ...prev, top_p: 0.9, top_k: 30, max_tokens: 2048 }));
          }}>⚡ Fast</button>
          <button onClick={() => {
            setSettings(prev => ({ ...prev, top_p: 1.0, top_k: 50, max_tokens: 8192 }));
          }}>📚 Long</button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
