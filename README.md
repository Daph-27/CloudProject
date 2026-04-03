# ⚡ Smart Electricity Bill Predictor (Full-Stack Azure Cloud Project)

An end-to-end IoT-driven electricity consumption monitoring and predictive billing system. This project simulates live appliance telemetry, predicts monthly costs using Machine Learning (Linear Regression), and stores all records in a real-time **Azure MySQL Database**.

---

## 🌟 Key Features

- **Live IoT Stream Visualization**: Real-time simulation of appliance-level power consumption (Watts).
- **ML Bill Forecasting**: Continuous prediction of monthly electricity bills based on live usage patterns.
- **Azure MySQL Integration**: All telemetry and billing data are automatically stored in the cloud.
- **Dynamic Appliance Management**: Add new appliances (like Geysers or Microwaves) on the fly and see the impact on your bill.
- **Email Alerts**: Automated threshold-based cost alerts sent to specified users.
- **Automated PDF Reports**: Generate professional monthly energy consumption reports with a single click.
- **Premium Dark UI**: A high-end, responsive dashboard built with React and Vite.

---

## 🔬 Overall Product Working (Detailed)

This project operates as a continuous data pipeline that bridges local IoT simulation with cloud-based analytics. Here is the step-by-step lifecycle of a telemetry event:

### 1. IoT Telemetry Generation (Simulation)
The **Flask backend** serves a persistent Server-Sent Events (SSE) stream on the `/stream` endpoint. Every 2 seconds, it generates a JSON payload representing real-world appliance activity:
- It randomly toggles devices (like the AC or TV) to simulate usage patterns.
- It calculates the `total_power_w` (sum of Watts from all 'ON' appliances).
- It also incorporates any user-added devices from the **"Add Appliance"** interface.

### 2. Frontend Real-Time Processing
The **React dashboard** listens to this `/stream` connection:
- It updates the **Live Telemetry Grid** and **Power Load Variation Chart** instantly.
- It keeps track of "Simulated Hours": For every 2 seconds of real time, the app simulates 5 hours of usage.
- It calculates the **Accumulated Units (kWh)**: `(Total Watts / 1000) * Simulated Hours`.

### 3. ML Bill Forecasting & Prediction
Every time the `Accumulated Units` change, the frontend makes a `POST` request to the `/predict` route:
- The backend receives the current Units and the appliance metadata (status/watts).
- It passes these Units into a **Linear Regression ML Model** (trained on historical electricity costs).
- The model returns a predicted base energy cost in **Indian Rupees (INR)**.
- The backend then calculates additional fees: **Grid Charges (fixed ₹50)** and **State Duty (5% tax)**.

### 4. Azure Cloud Synchronization
As part of the same `/predict` request, the backend automatically establishes a secure connection to the **Azure MySQL Database**:
- It inserts detailed records into `appliancehistory`: (ApplianceName, Status, Watts, EnergyKWh, etc.).
- It saves the final bill breakdown into `billingsummary`.
- This ensures that your cloud database is always in sync with your live dashboard for any future Power BI analytics.

### 5. Automated Intelligence & Alerts
The system continuously monitors the `NetPayable` amount:
- If the predicted bill exceeds the defined threshold (**₹500.00**), the backend triggers a cost alert.
- This alert is processed by `yagmail` to notify the user (`dxph1234@gmail.com`).
- Additionally, the backend can fetch this stored data to generate a consolidated **PDF Report**, creating a permanent record of energy usage.

---

1.  **Frontend (React + Vite)**: Handles the real-time dashboard, interactive charts, and user actions.
2.  **Backend (Flask)**:
    *   Serves an EventStream (SSE) for simulated IoT telemetry.
    *   Hosts the ML inference engine (Joblib + Scikit-Learn).
    *   Manages database connections and PDF/Email services.
3.  **Database (Azure MySQL)**: Persistently stores `appliancehistory` and `billingsummary` records.
4.  **Cloud Hosting**: Ready for deployment to **Azure App Service**.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+
- Node.js & npm
- Azure MySQL Server access

### 2. Backend Setup
Navigate to the `backend` directory and install dependencies:
```bash
cd backend
pip install flask flask-cors joblib scikit-learn mysql-connector-python python-dotenv reportlab yagmail
```

**Train the ML Model:**
```bash
python train_model.py
```

**Run the Backend Server:**
```bash
python app.py
```
*The backend runs on **http://127.0.0.1:5001***.

### 3. Frontend Setup
In a new terminal, navigate to the `frontend` directory:
```bash
cd frontend
npm install
npm run dev
```
*Open your browser at **http://localhost:5173***.

---

## 📁 Project Structure

```text
├── backend/
│   ├── app.py              # Main Flask server with Azure logic & routes
│   ├── train_model.py      # Script to train and save the Linear Regression model
│   ├── model.pkl           # Saved ML model file
│   ├── DigiCertGlobalRootCA.crt.pem # SSL Certificate for Azure MySQL
│   └── .env                # Database credentials
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── RealTimeDashboard.jsx # Live telemetry & appliance management
│   │   │   └── DetailedBill.jsx     # Itemized billing table & tax calculation
│   │   ├── App.jsx         # Main layout and API handler
│   │   └── styles.css      # Premium dark-theme CSS
│   └── vite.config.js       # Vite configuration
└── README.md                # Project documentation
```

---

## 📊 Database Schema (Azure MySQL)

The system automatically populates two tables in the `electricity_db`:

### `appliancehistory`
- `ApplianceName`: Name of the device (Fan, AC, Geyser, etc.)
- `Status`: Current state (ON/OFF)
- `Watts`: Power consumption at the moment
- `RunningHours`: Cumulative runtime in simulate time
- `EnergyKWh`: Energy consumed (KWh)
- `CostINR`: Real-time cost in Rupees

### `billingsummary`
- `BaseEnergyCost`: Raw energy cost based on ML prediction
- `GridCharge`: Fixed infrastructure fee
- `DutyAmount`: State government duty/tax
- `NetPayable`: Final payable amount

---

## 🛠️ API Endpoints

- `GET /stream`: Server-Sent Events (SSE) for live IoT telemetry.
- `POST /predict`: Receives current usage and returns ML-predicted bill.
- `POST /api/add-appliance`: Adds a new custom appliance to the live simulation.
- `GET /api/generate-report`: Generates and downloads a PDF monthly report.

---

## 📧 Cloud Alerts
The system is configured to send alerts to **dxph1234@gmail.com** whenever the `NetPayable` amount exceeds **₹500.00**. Alerts are rate-limited to once every 10 minutes to ensure stability.

---

## 📜 Deployment to Azure
1.  **Create App Service**: Use the Azure Portal or CLI to create a new Web App (Python 3.9+).
2.  **Config Database**: Ensure your Azure MySQL firewall allows connections from "Azure Services".
3.  **Push Code**:
    ```bash
    git add .
    git commit -m "Final project features implemented"
    git push -u origin master
    ```

---

## 🤝 Contact
Developed for the **Smart Electricity Predictor** Cloud Project.
**Support Email**: dxph1234@gmail.com
