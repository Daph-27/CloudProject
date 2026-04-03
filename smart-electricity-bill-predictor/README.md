# Smart Electricity Bill Predictor

This is a full-stack project built with React and Flask that predicts monthly electricity bills using a Machine Learning model. 
It visualizes historical usage and easily enables new predictions based on user input.

## Features
- **Frontend**: Built with React 18 & Vite, utilizing Recharts for visualizing the historical units vs bill trend.
- **Backend**: Built with Flask API and scikit-learn for handling predictive logic.
- **Machine Learning**: A linear regression model that predicts costs dynamically given units consumed.

## Folder Structure
```
smart-electricity-bill-predictor/
├── frontend/                 # React UI + Vite + Recharts
│   ├── public/
│   └── src/
│       ├── components/
│       │   ├── InputForm.jsx # Input interface
│       │   └── BillChart.jsx # Recharts trend layout
│       ├── App.jsx           # Main Container
│       ├── main.jsx          # React Bootsrap
│       └── styles.css        # Nice, simple UI styles
├── backend/                  # Flask API + ML code
│   ├── electricity_data.csv  # 100+ rows generated algorithmically
│   ├── train_model.py        # Sci-kit learn linear regression script
│   ├── model.pkl             # Serialized joblib trained ML Model
│   └── app.py                # Flask API implementation with CORS
├── requirements.txt          # Python dependencies
└── README.md
```

## How to Run Backend
1. **Navigate to backend**: `cd "c:\Users\Admin\Documents\Cloud Project\smart-electricity-bill-predictor\backend"`
2. **Install Python dependencies (Root directory)**: `pip install -r ../requirements.txt`
3. **Train the ML model**: `python train_model.py` (Must generate `model.pkl` first)
4. **Run the API**: `python app.py` (Will start Flask on `http://127.0.0.1:5000`)

## How to Run Frontend
1. **Navigate to frontend**: `cd "c:\Users\Admin\Documents\Cloud Project\smart-electricity-bill-predictor\frontend"`
2. **Install node modules**: `npm install`
3. **Start Development Server**: `npm run dev`

## Connecting Flask API to React
The React app uses standard `fetch` to POST `{"units": <value>}` directly to the backend (`http://127.0.0.1:5000/predict`). Flask implements `flask-cors` natively inside `app.py` to seamlessly accept these requests. 

## Azure Cloud Deployment (Placeholders inside Code)
- **Azure Blob Storage**: Comments are placed inside `app.py` and `train_model.py` instructing where URL reads can be configured for Azure Blob hosting rather than local CSVs.
- **Azure App Service**: Flask backend logic maps 1:1 to Python Linux Web App deployment processes in Azure. Simply upload the `backend/` and `requirements.txt` there.
- **Azure ML**: You can wrap the logic of `train_model.py` dynamically using `azureml-core` and execute experiments inside Azure Databricks or Compute instances.
- **Power BI**: Recharts currently takes placeholder historical data inside React. This component can be migrated to `powerbi-client-react` to fetch dashboards directly configured inside the Microsoft Cloud.
