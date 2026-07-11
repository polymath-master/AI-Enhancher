import React, { useState, useEffect } from 'react';

const Metrics = () => {
  const [metrics, setMetrics] = useState({
    cache: { size: 0, hit_rate: '0%', hits: 0, misses: 0 },
    ollama: { total_requests: 0, avg_latency: 0, is_ready: false },
    avg_latency: 0,
    requests: 0,
    deterministic: { temperature: 0, seed: 40, mode: 'fixed' }
  });
  
  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/v1/metrics');
      const data = await response.json();
      setMetrics(data);
    } catch (e) {
      console.error('Failed to fetch metrics');
    }
  };
  
  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 10000);
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="metrics-container">
      <h2>📊 System Metrics</h2>
      
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-label">Cache Size</div>
          <div className="metric-value">{metrics.cache.size}</div>
          <div className="metric-sub">entries</div>
        </div>
        
        <div className="metric-card">
          <div className="metric-label">Cache Hit Rate</div>
          <div className="metric-value">{metrics.cache.hit_rate}</div>
          <div className="metric-sub">{metrics.cache.hits} hits / {metrics.cache.misses} misses</div>
        </div>
        
        <div className="metric-card">
          <div className="metric-label">Total Requests</div>
          <div className="metric-value">{metrics.requests || 0}</div>
          <div className="metric-sub">processed</div>
        </div>
        
        <div className="metric-card">
          <div className="metric-label">Avg Latency</div>
          <div className="metric-value">{metrics.avg_latency.toFixed(2)}s</div>
          <div className="metric-sub">per request</div>
        </div>
        
        <div className="metric-card">
          <div className="metric-label">Model Status</div>
          <div className={`metric-value ${metrics.ollama.is_ready ? 'ready' : 'not-ready'}`}>
            {metrics.ollama.is_ready ? '✅ Ready' : '❌ Loading'}
          </div>
          <div className="metric-sub">llama3.2:7b</div>
        </div>
        
        <div className="metric-card highlight">
          <div className="metric-label">🔒 Mode</div>
          <div className="metric-value">Deterministic</div>
          <div className="metric-sub">Temp: 0 | Seed: 40</div>
        </div>
      </div>
      
      <div className="metrics-details">
        <h3>📈 Detailed Stats</h3>
        <pre>{JSON.stringify(metrics, null, 2)}</pre>
      </div>
    </div>
  );
};

export default Metrics;
