from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import joblib
import time
import json
import random
import yagmail
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from flask import send_file

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

ALERT_EMAIL = "dxph1234@gmail.com"
COST_THRESHOLD = 500.0 # INR
last_alert_time = 0

# Store user-added appliances globally for simulation
extra_appliances = {}

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
        # Trigger email alert check
        send_cost_alert(response_data['net_payable'])
    except Exception as e:
        print(f"⚠️ Save to Azure failed: {e}")
        
    return jsonify(response_data)

def send_cost_alert(current_cost):
    """Send email alert if cost exceeds threshold"""
    global last_alert_time
    # Alert once every 10 minutes to avoid spam
    if current_cost > COST_THRESHOLD and (time.time() - last_alert_time > 600):
        try:
            # Note: For production, use an App Password or SendGrid
            # For this demo, we'll log it as a simulation
            print(f"📧 [Simulated Email] ALERT: Cost reached ₹{current_cost:.2f}!")
            last_alert_time = time.time()
        except Exception as e:
            print(f"Failed to send email: {e}")

@app.route('/api/add-appliance', methods=['POST'])
def add_appliance():
    data = request.json
    name = data.get('name')
    watts = data.get('watts', 0)
    if name:
        extra_appliances[name] = {"status": True, "power_w": watts}
        return jsonify({"message": f"Appliance {name} added!"})
    return jsonify({"error": "Invalid name"}), 400

@app.route('/api/generate-report')
def generate_report():
    """Generates a PDF monthly bill report"""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Smart Electricity Predictor - Monthly Report")
    p.setFont("Helvetica", 12)
    p.drawString(100, 730, f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    p.drawString(100, 710, "Summary of Consumption and Predicted Costs")
    # For demo, static values or fetch from DB
    p.drawString(100, 680, "Total Predicted Bill: ₹540.23")
    p.drawString(100, 660, "Status: ACTIVE")
    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="Electricity_Report.pdf", mimetype='application/pdf')

@app.route('/stream')
def stream():
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
            # Include dynamic appliances
            current_appliances = {**appliances, **extra_appliances}
            
            # Randomly toggle some appliances to simulate real usage
            if random.random() < 0.1: appliances["AC"]["status"] = not appliances["AC"]["status"]
            if random.random() < 0.2: appliances["Light_2"]["status"] = not appliances["Light_2"]["status"]
            if random.random() < 0.15: appliances["TV"]["status"] = not appliances["TV"]["status"]
                
            total_power_w = sum([app["power_w"] for app in current_appliances.values() if app["status"]])
            
            payload = {
                "timestamp": int(time.time()),
                "appliances": current_appliances,
                "total_power_w": total_power_w
            }
            yield f"data: {json.dumps(payload)}\n\n"
            time.sleep(2)

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(port=5001, debug=True)
