import React, { useState, useRef, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [temperature, setTemperature] = useState(0.0);
  const [seed, setSeed] = useState(40);
  
  const messagesEndRef = useRef(null);
  const { sendMessage, lastMessage, isConnected } = useWebSocket();

  useEffect(() => {
    if (lastMessage) {
      if (lastMessage.type === 'chunk') {
        setMessages(prev => {
          const last = prev[prev.length - 1];
          if (last && last.isStreaming) {
            return [
              ...prev.slice(0, -1),
              { ...last, content: last.content + lastMessage.content }
            ];
          }
          return [...prev, { content: lastMessage.content, isStreaming: true, role: 'assistant' }];
        });
      } else if (lastMessage.type === 'done') {
        setIsStreaming(false);
        setMessages(prev => {
          const last = prev[prev.length - 1];
          if (last && last.isStreaming) {
            return [...prev.slice(0, -1), { ...last, isStreaming: false }];
          }
          return prev;
        });
      } else if (lastMessage.type === 'error') {
        alert(`Error: ${lastMessage.error}`);
        setIsStreaming(false);
      }
    }
  }, [lastMessage]);

  const sendPrompt = () => {
    if (!input.trim() || isStreaming) return;
    
    const userMessage = { content: input, role: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsStreaming(true);
    
    sendMessage({
      type: 'generate',
      prompt: input,
      system_prompt: systemPrompt || undefined,
      settings: {
        temperature: 0.0,
        seed: 40,
        deterministic: true,
        max_tokens: 4096
      }
    });
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="status">
          <span className={`dot ${isConnected ? 'connected' : 'disconnected'}`} />
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
        <div className="model-info">
          <span>Model: llama3.2:7b</span>
          <span>Temp: {temperature}</span>
          <span>Seed: {seed}</span>
        </div>
      </div>
      
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="avatar">
              {msg.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="content">
              {msg.content}
              {msg.isStreaming && <span className="cursor">▊</span>}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="input-area">
        <div className="system-prompt">
          <input
            type="text"
            placeholder="System prompt (optional)"
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
          />
        </div>
        <div className="input-row">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendPrompt();
              }
            }}
            disabled={isStreaming}
          />
          <button onClick={sendPrompt} disabled={!input.trim() || isStreaming}>
            {isStreaming ? '⏳' : '📤'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
