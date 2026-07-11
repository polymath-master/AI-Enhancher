import React, { useState } from 'react';
import Chat from './components/Chat';
import Settings from './components/Settings';
import Debate from './components/Debate';
import Metrics from './components/Metrics';
import './styles/global.css';

const App = () => {
  const [activeTab, setActiveTab] = useState('chat');
  
  return (
    <div className="app">
      <header className="header">
        <div className="logo">
          <h1>🤖 AI Platform Pro</h1>
          <span className="badge">v2.0</span>
        </div>
        <div className="header-info">
          <span className="deterministic-badge">🔒 Deterministic</span>
          <span className="seed-badge">Seed: 40</span>
        </div>
      </header>
      
      <nav className="nav">
        <button 
          className={activeTab === 'chat' ? 'active' : ''}
          onClick={() => setActiveTab('chat')}
        >
          💬 Chat
        </button>
        <button 
          className={activeTab === 'debate' ? 'active' : ''}
          onClick={() => setActiveTab('debate')}
        >
          🎭 Debate
        </button>
        <button 
          className={activeTab === 'settings' ? 'active' : ''}
          onClick={() => setActiveTab('settings')}
        >
          ⚙️ Settings
        </button>
        <button 
          className={activeTab === 'metrics' ? 'active' : ''}
          onClick={() => setActiveTab('metrics')}
        >
          📊 Metrics
        </button>
      </nav>
      
      <main className="main">
        {activeTab === 'chat' && <Chat />}
        {activeTab === 'debate' && <Debate />}
        {activeTab === 'settings' && <Settings />}
        {activeTab === 'metrics' && <Metrics />}
      </main>
    </div>
  );
};

export default App;
