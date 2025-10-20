# app.py
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import datetime, timedelta
import os
import traceback

app = Flask(__name__)
CORS(app)

# -------------------------------
# Configuration
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "Demand_Trends.csv")
FORECAST_DAYS = 90

def forecast_filename_for_today():
    today_str = pd.Timestamp.today().strftime('%Y-%m-%d')
    return os.path.join(BASE_DIR, f"forecast_{today_str}.csv")

# -------------------------------
# Helper: validate dataset
# -------------------------------
def validate_dataframe_for_forecast(df):
    required = {'date', 'demand', 'inventory'}
    if not required.issubset(set(df.columns)):
        missing = required - set(df.columns)
        raise ValueError(f"CSV missing required columns: {missing}")
    if df['demand'].dropna().empty:
        raise ValueError("Column 'demand' contains only NaN or is empty.")
    # convert to numeric (raise if cannot)
    df['demand'] = pd.to_numeric(df['demand'])

# -------------------------------
# Helper: SARIMA forecast (start from today)
# -------------------------------
def forecast_next_days_start_today(df, forecast_days=90):
    """
    Train SARIMA on historical demand and forecast next N days starting from TODAY.
    """
    # Validate input
    validate_dataframe_for_forecast(df)

    # Prepare time series
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df.set_index('date', inplace=True)
    df = df.asfreq('D')
    df['demand'] = df['demand'].fillna(method='ffill')

    if len(df['demand'].dropna()) < 10:
        raise ValueError("Not enough non-NaN demand points for SARIMAX (need >= 10).")

    try:
        model = SARIMAX(
            df['demand'],
            order=(2, 1, 2),
            seasonal_order=(1, 1, 1, 7),
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        model_fit = model.fit(disp=False)
        forecast_values = model_fit.forecast(steps=forecast_days)
    except Exception as e:
        print("SARIMAX fitting failed — full traceback below:")
        traceback.print_exc()
        raise RuntimeError(f"SARIMAX training failed: {e}")

    # Start forecasting from today
    today = pd.Timestamp(datetime.now().date())
    future_dates = pd.date_range(start=today, periods=forecast_days, freq='D')

    forecast_df = pd.DataFrame({
        'date': future_dates,
        'predicted_demand': forecast_values
    })

    return forecast_df

# -------------------------------
# API Endpoint: Forecast (today -> today+89)
# -------------------------------
@app.route('/predict', methods=['GET'])
def predict():
    try:
        output_file = forecast_filename_for_today()
        # If today's forecast already exists, return it
        if os.path.exists(output_file):
            print(f"Returning existing forecast file: {output_file}")
            forecast_df = pd.read_csv(output_file, parse_dates=['date'])
        else:
            # Load and validate dataset
            if not os.path.exists(DATA_FILE):
                raise FileNotFoundError(f"Data file not found: {DATA_FILE}")
            df = pd.read_csv(DATA_FILE)
            print("Data file loaded — head:")
            print(df.head())

            # Compute forecast starting from today
            forecast_df = forecast_next_days_start_today(df, FORECAST_DAYS)

            # Save to today's forecast file
            forecast_df.to_csv(output_file, index=False)
            print(f"Forecast saved: {output_file}")

            # --- NEW FEATURE: append today's predicted demand to Demand_Trends.csv AFTER 12:00 PM ---
            try:
                now = datetime.now()
                if now.hour >= 12:
                    print("Current hour >= 12: attempting to update Demand_Trends.csv with today's prediction.")
                    # Read existing demand trends (parse dates)
                    original_df = pd.read_csv(DATA_FILE, parse_dates=['date'])
                    # Normalize dates for comparison
                    today_date = pd.Timestamp(now.date()).date()
                    existing_dates = pd.to_datetime(original_df['date']).dt.date

                    if today_date in existing_dates.tolist():
                        print("Today's date already present in Demand_Trends.csv — no update performed.")
                    else:
                        # Find today's predicted value from forecast_df (date column could be Timestamp)
                        # Ensure forecast_df['date'] is datetime
                        forecast_df_local = forecast_df.copy()
                        forecast_df_local['date'] = pd.to_datetime(forecast_df_local['date'])
                        # Match today's row
                        today_row = forecast_df_local[forecast_df_local['date'].dt.date == today_date]
                        if today_row.empty:
                            print("No forecast row found for today — skipping append.")
                        else:
                            predicted_val = float(today_row['predicted_demand'].iloc[0])
                            # Use last known inventory if available
                            if 'inventory' in original_df.columns and not original_df['inventory'].dropna().empty:
                                last_inventory = original_df['inventory'].iloc[-1]
                            else:
                                last_inventory = 0
                            # Build new row (append to end -> chronological order)
                            new_row = {
                                'date': today_date.strftime('%Y-%m-%d'),
                                'demand': predicted_val,
                                'inventory': last_inventory
                            }
                            updated_df = pd.concat([original_df, pd.DataFrame([new_row])], ignore_index=True)
                            updated_df.to_csv(DATA_FILE, index=False)
                            print(f"Appended today's predicted demand to {DATA_FILE}: {new_row}")
                else:
                    print("Current hour < 12: will not modify Demand_Trends.csv now.")
            except Exception:
                print("Failed while attempting to update Demand_Trends.csv — traceback:")
                traceback.print_exc()
            # --- END new feature block ---

        # prepare JSON response
        # convert dates to ISO strings
        forecast_df['date'] = pd.to_datetime(forecast_df['date']).dt.strftime('%Y-%m-%d')
        forecast_json = forecast_df.to_dict(orient='records')

        return jsonify({"success": True, "forecast": forecast_json})

    except Exception as e:
        # print full traceback on server for debugging
        print("ERROR in /predict — full traceback:")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

# -------------------------------
# API Endpoint: Optimization (example)
# -------------------------------
@app.route('/optimize', methods=['GET'])
def optimize():
    try:
        out_file = forecast_filename_for_today()
        if os.path.exists(out_file):
            forecast_df = pd.read_csv(out_file)
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
    except Exception:
        traceback.print_exc()
        return jsonify({"success": False, "error": "Optimization failed"}), 500

# -------------------------------
# Run Flask
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)
