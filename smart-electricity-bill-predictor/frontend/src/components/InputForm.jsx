import React, { useState } from 'react';

const InputForm = ({ onPrediction, isPredicting }) => {
  const [units, setUnits] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!units || units < 0) return;
    
    onPrediction(units);
  };

  return (
    <form className="input-form" onSubmit={handleSubmit}>
      <h2>Predict Your Bill</h2>
      <div className="form-group">
        <label htmlFor="units">Units Consumed (kWh):</label>
        <input 
          type="number" 
          id="units" 
          value={units} 
          onChange={(e) => setUnits(e.target.value)} 
          placeholder="e.g. 250"
          required 
          min="0"
        />
      </div>
      <button type="submit" disabled={isPredicting}>
        {isPredicting ? 'Calculating...' : 'Predict Bill'}
      </button>
    </form>
  );
};

export default InputForm;
