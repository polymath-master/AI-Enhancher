import React, { useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

const Debate = () => {
  const [topic, setTopic] = useState('');
  const [numRounds, setNumRounds] = useState(3);
  const [numParticipants, setNumParticipants] = useState(2);
  const [perspectives, setPerspectives] = useState('');
  const [debateResult, setDebateResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const { sendMessage, lastMessage } = useWebSocket();

  React.useEffect(() => {
    if (lastMessage?.type === 'debate_result') {
      setDebateResult(lastMessage.data);
      setIsLoading(false);
    }
    if (lastMessage?.type === 'error') {
      alert(`Error: ${lastMessage.error}`);
      setIsLoading(false);
    }
  }, [lastMessage]);

  const startDebate = () => {
    if (!topic.trim()) return;
    setIsLoading(true);
    setDebateResult(null);
    
    const perspectivesList = perspectives.split(',').map(p => p.trim()).filter(p => p);
    
    sendMessage({
      type: 'debate',
      debate: {
        topic: topic,
        num_rounds: numRounds,
        num_participants: perspectivesList.length || numParticipants,
        perspectives: perspectivesList.length ? perspectivesList : undefined,
        settings: {
          temperature: 0.0,
          seed: 40,
          deterministic: true
        }
      }
    });
  };

  return (
    <div className="debate-container">
      <h2>🎭 AI Debate Arena</h2>
      <p>Multi-perspective debate with deterministic AI personas</p>
      
      <div className="debate-controls">
        <div className="input-group">
          <label>📝 Topic</label>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g., Should AI be regulated globally?"
          />
        </div>
        
        <div className="input-group">
          <label>🔄 Rounds</label>
          <select value={numRounds} onChange={(e) => setNumRounds(parseInt(e.target.value))}>
            {[1,2,3,4,5].map(n => (
              <option key={n} value={n}>{n} rounds</option>
            ))}
          </select>
        </div>
        
        <div className="input-group">
          <label>👥 Participants</label>
          <select value={numParticipants} onChange={(e) => setNumParticipants(parseInt(e.target.value))}>
            {[2,3,4,5].map(n => (
              <option key={n} value={n}>{n} perspectives</option>
            ))}
          </select>
        </div>
        
        <div className="input-group">
          <label>🎯 Custom Perspectives (optional)</label>
          <input
            type="text"
            value={perspectives}
            onChange={(e) => setPerspectives(e.target.value)}
            placeholder="Environmentalist, Economist, Technologist..."
          />
          <small>Comma separated</small>
        </div>
        
        <button 
          className="start-debate"
          onClick={startDebate}
          disabled={isLoading || !topic.trim()}
        >
          {isLoading ? '⏳ Debating...' : '🎯 Start Debate'}
        </button>
      </div>
      
      {isLoading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>AI debaters preparing arguments...</p>
        </div>
      )}
      
      {debateResult && (
        <div className="debate-result">
          <h3>📊 Debate Results</h3>
          
          <div className="debate-meta">
            <span>🏆 Winner: <strong>{debateResult.winner}</strong></span>
            <span>⏱️ {debateResult.processing_time.toFixed(2)}s</span>
            <span>🎯 Accuracy: {(debateResult.accuracy_score * 100).toFixed(1)}%</span>
          </div>
          
          {debateResult.rounds.map((round, idx) => (
            <div key={idx} className="round">
              <h4>Round {round.round_num}</h4>
              {round.arguments.map((arg, argIdx) => (
                <div key={argIdx} className="argument">
                  <div className="speaker">{arg.speaker}</div>
                  <div className="content">{arg.argument}</div>
                  {arg.counter_arguments && arg.counter_arguments.length > 0 && (
                    <div className="counters">
                      <strong>Counter arguments:</strong>
                      {arg.counter_arguments.map((c, cIdx) => (
                        <div key={cIdx} className="counter">
                          vs {c.against}: {c.counter}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ))}
          
          <div className="summary">
            <h4>📋 Summary</h4>
            <p>{debateResult.summary}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Debate;
