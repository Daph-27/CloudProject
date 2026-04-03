import React, { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const RealTimeDashboard = ({ onPredictionUpdate }) => {
  const [streamData, setStreamData] = useState(null);
  const [powerHistory, setPowerHistory] = useState([]);
  const [cumulativeUnits, setCumulativeUnits] = useState(0); 
  const [applianceStats, setApplianceStats] = useState({});

  useEffect(() => {
    // Connect to the Flask Server-Sent Events (SSE) Stream
    const eventSource = new EventSource('http://127.0.0.1:5001/stream');

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setStreamData(data);
      
      // We simulate 5 hours passing for every 2 real-life seconds
      const simulatedHoursElapsed = 5; 
      const kwhConsumed = (data.total_power_w / 1000) * simulatedHoursElapsed;
      
      setCumulativeUnits((prev) => prev + kwhConsumed);

      // Track individual runtime and consumption for the detailed bill
      setApplianceStats(prev => {
          const nextStats = { ...prev };
          Object.entries(data.appliances).forEach(([name, app]) => {
              if (!nextStats[name]) {
                  nextStats[name] = { runTimeHours: 0, kwhConsumed: 0 };
              }
              nextStats[name].status = app.status;
              nextStats[name].power_w = app.power_w;
              
              if (app.status) {
                  nextStats[name].runTimeHours += simulatedHoursElapsed;
                  nextStats[name].kwhConsumed += (app.power_w / 1000) * simulatedHoursElapsed;
              }
          });
          return nextStats;
      });

      setPowerHistory((prev) => {
        const timeStr = new Date().toLocaleTimeString('en-US', { hour12: false, hour: "numeric", minute: "numeric", second: "numeric" });
        const newHistory = [...prev, { time: timeStr, power: data.total_power_w }];
        if (newHistory.length > 20) newHistory.shift(); 
        return newHistory;
      });
    };

    return () => {
      eventSource.close();
    };
  }, []);

  // Update Prediction with the latest units and detailed stats
  useEffect(() => {
    if (cumulativeUnits > 0) {
      onPredictionUpdate(cumulativeUnits, applianceStats);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cumulativeUnits]);

  if (!streamData) {
    return <div className="loading-stream">Connecting to Real-Time IoT Stream (Azure IoT Hub placeholder)...</div>;
  }

  return (
    <div className="realtime-dashboard">
      <div className="dashboard-header">
        <h2>Live Appliance Telemetry</h2>
        <div className="pulse-indicator">
          <span className="dot"></span> Live Stream Active
        </div>
      </div>
      
      <div className="appliances-grid">
        {Object.entries(streamData.appliances).map(([name, app]) => (
          <div key={name} className={`appliance-card ${app.status ? 'active' : 'inactive'}`}>
            <div className="app-icon">{app.status ? '⚡' : '💤'}</div>
            <div className="app-info">
              <h3>{name}</h3>
              <p>{app.power_w} W</p>
            </div>
            <div className="status-badge">{app.status ? 'ON' : 'OFF'}</div>
          </div>
        ))}
      </div>

      <div className="metrics-row">
        <div className="metric-box">
          <h3>Current Total Load</h3>
          <p className="big-value">{streamData.total_power_w} W</p>
        </div>
        <div className="metric-box">
          <h3>Accumulated Units</h3>
          <p className="big-value warning">{cumulativeUnits.toFixed(2)} kWh</p>
          <small>Simulated timeline speed tracking</small>
        </div>
      </div>

      <div className="realtime-chart">
        <h3>Power Load Variation (Watts)</h3>
        <ResponsiveContainer width="100%" height={240}>
          <AreaChart data={powerHistory}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="time" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#fff' }} />
            <Area type="monotone" dataKey="power" stroke="#38bdf8" fill="url(#colorPower)" strokeWidth={3} />
            <defs>
              <linearGradient id="colorPower" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.4}/>
                <stop offset="95%" stopColor="#38bdf8" stopOpacity={0}/>
              </linearGradient>
            </defs>
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default RealTimeDashboard;
