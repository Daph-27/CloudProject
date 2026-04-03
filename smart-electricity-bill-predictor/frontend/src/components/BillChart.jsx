import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceDot } from 'recharts';

const BillChart = ({ data, prediction }) => {
  const chartData = useMemo(() => {
    // Basic subset if we have too much data
    if (!data || data.length === 0) return [];
    
    // Sort logically by units if not already sorted
    const sorted = [...data].sort((a, b) => a.Units - b.Units);
    
    // Subsample if data is too big for a smooth chart
    return sorted.filter((_, i) => i % 5 === 0);
  }, [data]);

  return (
    <div className="chart-container">
      <h2>Historical Usage vs Bill Trend</h2>
      <div className="chart-wrapper">
        {/* Power BI Placeholder: You can embed real Power BI dashboards here using the powerbi-client-react library */}
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="Units" label={{ value: 'Units (kWh)', position: 'insideBottom', offset: -10 }} />
            <YAxis label={{ value: 'Bill Amount ($)', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend verticalAlign="top" height={36} />
            <Line type="monotone" dataKey="BillAmount" name="Historical Bill" stroke="#3b82f6" strokeWidth={2} activeDot={{ r: 8 }} />
            
            {/* If there's a current prediction, highlight it on the chart somehow! */}
            {prediction && (
              <ReferenceDot x={prediction.units} y={prediction.predicted_bill} r={8} fill="red" stroke="none" />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
      {prediction && <p className="prediction-note" style={{color: 'red', textAlign: 'center'}}>Red dot corresponds to your predicted bill!</p>}
    </div>
  );
};

export default BillChart;
