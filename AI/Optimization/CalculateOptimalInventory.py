import pandas as pd
import numpy as np
from scipy import stats
import os

# Configuration
LEAD_TIME = 7
RMSE = 25.85
SERVICE_LEVEL = 0.95
Z_SCORE = stats.norm.ppf(SERVICE_LEVEL)

# Parse data
base_dir = os.getcwd()  # current working directory
file_path = os.path.join(base_dir, "aura-inventory-flask", "forecast_90_days.csv")
df = pd.read_csv(file_path)
df['date'] = pd.to_datetime(df['date'])

# Calculate safety stock
safety_stock = Z_SCORE * RMSE * np.sqrt(LEAD_TIME)

# Calculate rolling 7-day demand
df['lead_time_demand'] = df['predicted_demand'].rolling(window=LEAD_TIME).sum()

# Calculate reorder point
df['reorder_point'] = df['lead_time_demand'] + safety_stock

# Calculate order quantity (2 weeks of average demand)
avg_demand = df['predicted_demand'].mean()
order_quantity = avg_demand * 14

# TODAY'S ORDER
lead_time_total = df.iloc[:LEAD_TIME]['predicted_demand'].sum()
order_today = lead_time_total + safety_stock

print(f"Safety Stock: {safety_stock:.2f} units")
print(f"Average Daily Demand: {avg_demand:.2f} units")
print(f"Order Quantity: {order_quantity:.2f} units")
print(f"\nORDER TODAY: {order_today:.2f} units")
print(f"   (Covers next 7 days + safety buffer)")

# Display results
print("\n" + df[['date', 'predicted_demand', 'lead_time_demand', 'reorder_point']].to_string(index=False))

# Get the folder where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Output file path in the same folder
output_file = os.path.join(script_dir, "forecast_90_days_updated.csv")

# Save DataFrame
df.to_csv(output_file, index=False)

print(f"Updated CSV saved at: {output_file}")