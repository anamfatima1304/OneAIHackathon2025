# app.py
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import timedelta, datetime
import os

app = Flask(__name__)
CORS(app)  # allow requests from frontend

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
    # Ensure datetime index with daily frequency
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df.set_index('date', inplace=True)
    df = df.asfreq('D')  # daily frequency
    df['demand'] = df['demand'].fillna(method='ffill')

    try:
        model = SARIMAX(
            df['demand'],
            order=(2, 1, 2),
            seasonal_order=(1, 1, 1, 7),  # weekly seasonality
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        model_fit = model.fit(disp=False)
        forecast = model_fit.forecast(steps=forecast_days)
    except Exception as e:
        print("SARIMAX fit failed:", e)
        raise e

    last_date = df.index[-1]
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_days)

    forecast_df = pd.DataFrame({
        'date': future_dates,
        'predicted_demand': forecast
    })

    # Save forecast to CSV
    forecast_df.to_csv(FORECAST_FILE, index=False)
    print(f"Forecast saved to {FORECAST_FILE}")

    # Add first forecast to Demand_Trends.csv if after 12 PM
    now = datetime.now()
    if now.hour >= 12:
        first_forecast = forecast_df.iloc[0]
        # Read current dataset
        df_original = pd.read_csv(DATA_FILE)
        # Prepend new row
        new_row = pd.DataFrame({
            'date': [first_forecast['date'].strftime('%Y-%m-%d')],
            'demand': [first_forecast['predicted_demand']],
            'inventory': [df_original['inventory'].iloc[-1]]  # keep last inventory
        })
        df_updated = pd.concat([new_row, df_original], ignore_index=True)
        df_updated.to_csv(DATA_FILE, index=False)
        print(f"Prepended first forecast to {DATA_FILE}")

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
            df = pd.read_csv(DATA_FILE)
            forecast_df = forecast_next_days(df, FORECAST_DAYS)

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
    if os.path.exists(FORECAST_FILE):
        forecast_df = pd.read_csv(FORECAST_FILE)
        last_inventory = 250  # Example: can come from dataset or business logic
        lead_time = 7
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
