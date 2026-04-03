import React from 'react';

const DetailedBill = ({ prediction, stats }) => {
  if (!prediction || !stats || Object.keys(stats).length === 0) {
    return <div className="waiting-box">Waiting for appliance consumption telemetry...</div>;
  }

  // To allocate the ML predicted bill among appliances we use their proportion of total kWh
  const totalKwh = Object.values(stats).reduce((acc, curr) => acc + curr.kwhConsumed, 0);
  const baseBill = prediction.predicted_bill;

  // Add realistic Fixed Charges and Taxes for a complex bill structure
  const fixedCharge = 150.00; // Fixed grid capacity charge in INR
  const taxRate = 0.05; // 5% Electricity Duty / Tax
  
  const subtotal = baseBill + fixedCharge;
  const taxAmount = subtotal * taxRate;
  const grandTotal = subtotal + taxAmount;

  return (
    <div className="detailed-bill-container">
      <h3>📜 Complex Itemized Breakdown</h3>
      
      <div className="bill-table-wrapper">
        <table className="bill-table">
          <thead>
            <tr>
              <th>Appliance</th>
              <th>Time Running</th>
              <th>Consumption</th>
              <th>Apportioned Cost</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(stats).map(([name, data]) => {
              const proportion = totalKwh > 0 ? (data.kwhConsumed / totalKwh) : 0;
              const appCost = baseBill * proportion;
              return (
                <tr key={name}>
                  <td><strong>{name}</strong></td>
                  <td>{data.runTimeHours.toFixed(1)} hrs</td>
                  <td>{data.kwhConsumed.toFixed(3)} kWh</td>
                  <td className="cost-col">₹{appCost.toFixed(2)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      
      <div className="bill-summary-card">
        <h4>Billing Account Summary</h4>
        <div className="summary-row">
          <span>Energy Cost (ML Predicted)</span>
          <span>₹{baseBill.toFixed(2)}</span>
        </div>
        <div className="summary-row">
          <span>Grid Connectivity Charge (Fixed)</span>
          <span>₹{fixedCharge.toFixed(2)}</span>
        </div>
        <div className="summary-row tax-row">
          <span>State Electricity Duty (5%)</span>
          <span>₹{taxAmount.toFixed(2)}</span>
        </div>
        <hr className="summary-divider" />
        <div className="summary-row grand-total">
          <span>Net Payable Amount</span>
          <span className="total-highlight">₹{grandTotal.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
};

export default DetailedBill;
