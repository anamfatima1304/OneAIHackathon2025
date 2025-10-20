# app.py
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import timedelta
import os

app = Flask(__name__)
CORS(app)  # allow requests from frontend (React/Node)

# -------------------------------
# Configuration
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "Demand_Trends.csv")
FORECAST_DAYS = 90
FORECAST_FILE = os.path.join(BASE_DIR, "forecast_90_days.csv")  # Save forecast here

# -------------------------------
# Helper function for SARIMA Forecast
# -------------------------------
def forecast_next_days(df, forecast_days=90):
    """Train SARIMA on historical demand and forecast next N days."""
    model = SARIMAX(
        df['demand'],
        order=(2, 1, 2),
        seasonal_order=(1, 1, 1, 7),  # weekly seasonality
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    model_fit = model.fit(disp=False)
    forecast = model_fit.forecast(steps=forecast_days)

    last_date = df.index[-1]
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_days)

    forecast_df = pd.DataFrame({
        'date': future_dates,
        'predicted_demand': forecast
    })

    # Save forecast to CSV
    forecast_df.to_csv(FORECAST_FILE, index=False)
    print(f"Forecast saved to {FORECAST_FILE}")

    return forecast_df

# -------------------------------
# API Endpoint: Forecast
# -------------------------------
@app.route('/predict', methods=['GET'])
def predict():
    try:
        # Check if forecast CSV exists
        if os.path.exists(FORECAST_FILE):
            forecast_df = pd.read_csv(FORECAST_FILE)
        else:
            # Load dataset
            df = pd.read_csv(DATA_FILE)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            df.set_index('date', inplace=True)

            # Forecast next 90 days and save CSV
            forecast_df = forecast_next_days(df, FORECAST_DAYS)

        # Convert to list of dicts for JSON
        forecast_json = forecast_df.to_dict(orient='records')

        return jsonify({
            "success": True,
            "forecast": forecast_json
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# -------------------------------
# API Endpoint: Optimization (dummy example)
# -------------------------------
@app.route('/optimize', methods=['GET'])
def optimize():
    # Example: read forecast from CSV
    if os.path.exists(FORECAST_FILE):
        forecast_df = pd.read_csv(FORECAST_FILE)
        last_inventory = 250  # Example: can come from dataset or business logic
        lead_time = 7
        # Dummy calculation
        recommended_order_qty = int(forecast_df['predicted_demand'].mean() + 50)
    else:
        recommended_order_qty = 200

    return jsonify({
        "success": True,
        "optimization": {
            "reorder_point": 120,
            "safety_stock": 50,
            "recommended_order_qty": recommended_order_qty
        }
    })

# -------------------------------
# Run Flask
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)
