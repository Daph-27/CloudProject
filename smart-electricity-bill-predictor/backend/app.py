from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import joblib
import time
import json
import random

# Azure App Service Placeholder: Host this Flask API on Azure App Service.

app = Flask(__name__)
CORS(app) # Enable cross-origin requests from React

try:
    model = joblib.load('model.pkl')
except Exception as e:
    print("Could not load model. Train the model first.")
    model = None

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

# ========== AZURE MYSQL DATABASE CONNECTION ==========
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="electric-server.mysql.database.azure.com",
            database="electricity_db",
            user="DaphChris",  # Replace this
            password="DaphChris@123",  # Replace this
            use_pure=True
        )
        return connection
    except Error as e:
        print(f"MySQL Connection Error: {e}")
        return None
def save_to_azure_mysql(telemetry, billing_data):
    """Save appliance data to Azure MySQL Database"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Save each appliance's data - using exact case-sensitive column names
        for appliance_name, data in telemetry.items():
            # data is {"runTimeHours": X, "kwhConsumed": Y, "power_w": Z, "status": B}
            # Need to ensure we have watts. Let's assume frontend sends it.
            
            watts = data.get("power_w", 0)
            hours = data.get("runTimeHours", 0)
            status = "ON" if data.get("status") else "OFF"
            energy_kwh = data.get("kwhConsumed", 0)
            cost = (energy_kwh * 3.5) # Based on user's 3.5 rate
            
            # Using PascalCase column names from Azure schema
            cursor.execute("""
                INSERT INTO appliancehistory 
                (ApplianceName, Status, Watts, RunningHours, EnergyKWh, CostINR)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (appliance_name, status, watts, hours, energy_kwh, cost))
        
        # Save billing summary - exact case match
        cursor.execute("""
            INSERT INTO billingsummary 
            (BaseEnergyCost, GridCharge, DutyAmount, NetPayable, BillingDate)
            VALUES (%s, %s, %s, %s, CURDATE())
        """, (
            billing_data.get("base_energy_cost", 0),
            billing_data.get("grid_charge", 0),
            billing_data.get("state_duty_amount", 0),
            billing_data.get("net_payable", 0)
        ))
        
        conn.commit()
        print(f"✅ Saved: {len(telemetry)} appliance records")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Save error: {e}")
        return False

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model not trained'}), 500
        
    data = request.get_json()
    if not data or 'units' not in data:
        return jsonify({'error': 'Please provide units in JSON'}), 400
        
    units = float(data['units'])
    telemetry = data.get('telemetry', {})
    
    prediction_val = model.predict([[units]])[0]
    
    response_data = {
        'units': units,
        'predicted_bill': round(prediction_val, 2),
        'base_energy_cost': round(prediction_val, 2),
        'grid_charge': 50.0,
        'state_duty_amount': round(prediction_val * 0.05, 2),
        'net_payable': round(prediction_val + 50.0 + (prediction_val * 0.05), 2)
    }

    # Save to Azure MySQL
    try:
        save_to_azure_mysql(telemetry, response_data)
        print("✅ Data saved to Azure MySQL")
    except Exception as e:
        print(f"⚠️ Save to Azure failed: {e}")
        
    return jsonify(response_data)

@app.route('/stream')
def stream():
    # Azure IoT Hub / Event Hubs Placeholder: 
    # Replace this simulation with an EventHubConsumerClient reading native IoT telemetry.
    def generate():
        appliances = {
            "Fan": {"status": True, "power_w": 60},
            "Light_1": {"status": True, "power_w": 15},
            "Light_2": {"status": False, "power_w": 15},
            "AC": {"status": False, "power_w": 1500},
            "Fridge": {"status": True, "power_w": 150},
            "TV": {"status": False, "power_w": 100}
        }
        
        while True:
            # Randomly toggle some appliances to simulate real usage
            if random.random() < 0.1: appliances["AC"]["status"] = not appliances["AC"]["status"]
            if random.random() < 0.2: appliances["Light_2"]["status"] = not appliances["Light_2"]["status"]
            if random.random() < 0.15: appliances["TV"]["status"] = not appliances["TV"]["status"]
                
            total_power_w = sum([app["power_w"] for app in appliances.values() if app["status"]])
            
            payload = {
                "timestamp": int(time.time()),
                "appliances": appliances,
                "total_power_w": total_power_w
            }
            yield f"data: {json.dumps(payload)}\n\n"
            time.sleep(2) # Emit simulated telemetry event every 2 seconds

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(port=5001, debug=True)
