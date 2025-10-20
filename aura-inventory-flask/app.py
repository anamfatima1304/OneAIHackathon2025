# app.py
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import datetime, timedelta
import os
import traceback
import numpy as np
from scipy import stats

app = Flask(__name__)
CORS(app)

# -------------------------------
# Configuration
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "Demand_Trends.csv")
FORECAST_DAYS = 90

# Optimization constants (from your script)
LEAD_TIME = 7
RMSE = 25.85
SERVICE_LEVEL = 0.95
Z_SCORE = stats.norm.ppf(SERVICE_LEVEL)

def forecast_filename_for_today():
    today_str = pd.Timestamp.today().strftime('%Y-%m-%d')
    return os.path.join(BASE_DIR, f"forecast_{today_str}.csv")

def forecast_updated_filename_for_today():
    today_str = pd.Timestamp.today().strftime('%Y-%m-%d')
    return os.path.join(BASE_DIR, f"forecast_{today_str}_updated.csv")

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
                        forecast_df_local = forecast_df.copy()
                        forecast_df_local['date'] = pd.to_datetime(forecast_df_local['date'])
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
# API Endpoint: Optimization (detailed)
# -------------------------------
@app.route('/optimize', methods=['GET'])
def optimize():
    """
    Compute optimization metrics based on today's forecast:
    - safety_stock (Z * RMSE * sqrt(lead_time))
    - lead_time_demand (rolling sum over lead_time)
    - reorder_point = lead_time_demand + safety_stock
    - order_quantity (2 weeks of average demand)
    - order_today = sum of first LEAD_TIME predicted demands + safety_stock
    Returns JSON with summary numbers and a sample of rows.
    """
    try:
        # Ensure today's forecast exists (generate if needed)
        forecast_file = forecast_filename_for_today()
        if not os.path.exists(forecast_file):
            print("Today's forecast not found — generating via /predict flow.")
            # call internal predict generation logic: load data and compute forecast
            if not os.path.exists(DATA_FILE):
                raise FileNotFoundError(f"Data file not found: {DATA_FILE}")
            df_raw = pd.read_csv(DATA_FILE)
            forecast_df = forecast_next_days_start_today(df_raw, FORECAST_DAYS)
            forecast_df.to_csv(forecast_file, index=False)
            print(f"Forecast generated and saved: {forecast_file}")
        else:
            forecast_df = pd.read_csv(forecast_file)
            print(f"Loaded forecast from file: {forecast_file}")

        # Ensure date dtype and predicted_demand numeric
        forecast_df['date'] = pd.to_datetime(forecast_df['date'])
        forecast_df['predicted_demand'] = pd.to_numeric(forecast_df['predicted_demand'])

        # Safety stock (Z * RMSE * sqrt(LEAD_TIME))
        safety_stock = float(Z_SCORE * RMSE * np.sqrt(LEAD_TIME))

        # lead_time_demand: rolling sum over LEAD_TIME days (aligned to end of window)
        forecast_df['lead_time_demand'] = forecast_df['predicted_demand'].rolling(window=LEAD_TIME, min_periods=1).sum()

        # reorder point
        forecast_df['reorder_point'] = forecast_df['lead_time_demand'] + safety_stock

        # order quantity: 2 weeks of average demand (14 days)
        avg_demand = float(forecast_df['predicted_demand'].mean())
        order_quantity = float(avg_demand * 14)

        # today's order: sum of first LEAD_TIME predicted demands + safety_stock
        first_lead_demand_sum = float(forecast_df['predicted_demand'].iloc[:LEAD_TIME].sum())
        order_today = first_lead_demand_sum + safety_stock

        # Save updated CSV (with columns added) next to the forecast file
        updated_file = forecast_updated_filename_for_today()
        # save full dataframe
        forecast_df.to_csv(updated_file, index=False)
        print(f"Updated forecast saved with optimization columns: {updated_file}")

        # Prepare a small table (first 14 rows) for quick inspection
        sample_table = forecast_df[['date', 'predicted_demand', 'lead_time_demand', 'reorder_point']].head(14)
        # Convert dates to string for JSON
        sample_table['date'] = sample_table['date'].dt.strftime('%Y-%m-%d')
        sample_rows = sample_table.to_dict(orient='records')

        result = {
            "success": True,
            "summary": {
                "safety_stock": round(safety_stock, 2),
                "average_daily_demand": round(avg_demand, 2),
                "order_quantity_14_days": round(order_quantity, 2),
                "order_today": round(order_today, 2),
                "lead_time_days": LEAD_TIME,
                "service_level": SERVICE_LEVEL,
                "rmse_used": RMSE
            },
            "sample_rows": sample_rows,
            "updated_csv": os.path.basename(updated_file)
        }

        return jsonify(result)

    except Exception as e:
        print("ERROR in /optimize — full traceback:")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

# -------------------------------
# Run Flask
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)
