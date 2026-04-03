import React, { useState } from 'react';
import RealTimeDashboard from './components/RealTimeDashboard';
import DetailedBill from './components/DetailedBill';
import './styles.css';

function App() {
  const [predictionResult, setPredictionResult] = useState(null);
  const [applianceStats, setApplianceStats] = useState({});
  const [error, setError] = useState(null);

  // Triggered by the continuous stream when cumulative kWh changes
  const handlePredictionUpdate = async (cumulativeUnits, currentStats) => {
    try {
      const response = await fetch('http://127.0.0.1:5001/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          units: parseFloat(cumulativeUnits),
          telemetry: currentStats 
        })
      });

      if (!response.ok) throw new Error('Failed to fetch prediction');
      
      const data = await response.json();
      if (data.error) throw new Error(data.error);
      
      setPredictionResult(data);
      setApplianceStats(currentStats);
      setError(null);
    } catch (err) {
      setError("Could not reach Flask API. Is it running?");
    }
  };

  return (
    <div className="App dark-theme">
      <header className="app-header">
        <h1>⚡ Smart Electric Predictor</h1>
        <p>Continuous Real-Time IoT Stream Simulation · Indian Rupees (INR)</p>
      </header>

      <main className="app-main">
        <div className="dashboard-layout">
          {/* Left Column: Real time streaming data */}
          <div className="left-panel">
            <RealTimeDashboard onPredictionUpdate={handlePredictionUpdate} />
          </div>
          
          {/* Right Column: Dynamic Predictive Billing & Detailed Breakdowns */}
          <div className="right-panel">
            <div className="prediction-widget">
               <h2>Live ML Forecasting</h2>
               {error && <div className="error-box">{error}</div>}
               {predictionResult ? (
                 <>
                   <div className="live-bill">
                     <span className="currency">₹</span>
                     <span className="bill-value">{predictionResult.predicted_bill.toFixed(2)}</span>
                     <div className="bill-sub">Basic Energy Total (Predicted)</div>
                   </div>
                   <DetailedBill prediction={predictionResult} stats={applianceStats} />
                 </>
               ) : (
                 <div className="waiting-box">
                   Awaiting stream data...
                 </div>
               )}
            </div>

            <div className="azure-placeholder">
              <h3>☁️ Azure Integration Roadmap</h3>
              <ul>
                <li><strong>Azure IoT Hub:</strong> Replace local SSE polling with true bidirectional device telemetry syncing.</li>
                <li><strong>Azure SQL Database:</strong> Store appliance running histories to generate long-term monthly comparative reports.</li>
                <li><strong>Azure ML Studio:</strong> Host the core prediction algorithm over secure HTTPS endpoints.</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
