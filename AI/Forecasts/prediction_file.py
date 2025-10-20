# dynamic_sarima_forecast.py
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import timedelta
import os

# -------------------------------
# Configuration
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build full path to CSV
DATA_FILE = os.path.join(BASE_DIR, "Demand_Trends.csv")
FORECAST_DAYS = 90  


# -------------------------------
# Load dataset
# -------------------------------
df = pd.read_csv(DATA_FILE)
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')
df.set_index('date', inplace=True)

# -------------------------------
# Train SARIMA and forecast
# -------------------------------
def forecast_next_days(df, forecast_days=90):
    """Train SARIMA on historical demand and forecast next N days."""
    model = SARIMAX(
        df['demand'],
        order=(2,1,2),
        seasonal_order=(1,1,1,7),  # weekly seasonality
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
    return forecast_df

# -------------------------------
# Run daily forecast

FORECAST_DAYS = 90
forecast_df = forecast_next_days(df, FORECAST_DAYS)

# Save forecast CSV in the same folder as the script
output_file = os.path.join(BASE_DIR, f"forecast_{pd.Timestamp.today().strftime('%Y-%m-%d')}.csv")
forecast_df.to_csv(output_file, index=False)

print(f"Forecast saved in same folder as script: {output_file}")