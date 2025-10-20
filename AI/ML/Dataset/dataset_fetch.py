import pandas as pd
import numpy as np
from datetime import datetime

# ============================================================================
# STEP 1: LOAD DATASET
# ============================================================================
print("Step 1: Loading dataset...")
df = pd.read_csv('retail_store_inventory.csv')

# ============================================================================
# STEP 2: FILTER FOR SPECIFIC PRODUCT AND STORE
# ============================================================================
print("\n" + "="*70)
print("Step 2: Filtering for Product P0001 and Store S001...")

df_filtered = df[(df['Product ID'] == 'P0001') & (df['Store ID'] == 'S001')].copy()

print(f"Filtered dataset shape: {df_filtered.shape}")

# if df_filtered.empty:
#     print("ERROR: No data found for Product P0001 and Store S001!")
#     print("Available Product IDs:", df['Product ID'].unique()[:10])
#     print("Available Store IDs:", df['Store ID'].unique()[:10])
# else:
#     print(f"✓ Found {len(df_filtered)} records for Product P0001, Store S001")

# ============================================================================
# STEP 3: SELECT AND RENAME COLUMNS
# ============================================================================
print("\n" + "="*70)
print("Step 3: Selecting and renaming columns...")

# Select the 3 required columns
df_clean = df_filtered[['Date', 'Inventory Level', 'Units Sold']].copy()

# Rename columns
df_clean.columns = ['date', 'inventory', 'demand']

print("Selected columns: date, inventory, demand")

# ============================================================================
# STEP 4: DATA TYPE CONVERSION
# ============================================================================
print("\n" + "="*70)
print("Step 4: Converting data types...")

# Convert date to datetime
df_clean['date'] = pd.to_datetime(df_clean['date'])

# Convert inventory and demand to integers
df_clean['inventory'] = pd.to_numeric(df_clean['inventory'], errors='coerce').fillna(0).astype(int)
df_clean['demand'] = pd.to_numeric(df_clean['demand'], errors='coerce').fillna(0).astype(int)

print("✓ date: datetime64")
print("✓ inventory: int64")
print("✓ demand: int64")

# ============================================================================
# STEP 5: SORT BY DATE
# ============================================================================
print("\n" + "="*70)
print("Step 5: Sorting by date...")

df_clean = df_clean.sort_values('date').reset_index(drop=True)

print("✓ Dataset sorted by date (oldest to newest)")

# ============================================================================
# STEP 8: SAVE DATASET
# ============================================================================
print("\n" + "="*70)
print("Step 8: Saving cleaned dataset...")

output_filename = 'component_x.csv'
df_clean.to_csv(output_filename, index=False)

print(f"Cleaned dataset saved to: {output_filename}")
