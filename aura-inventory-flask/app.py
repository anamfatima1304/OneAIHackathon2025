from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import traceback

app = Flask(__name__)
CORS(app)

@app.route('/api/predict', methods=['GET'])
def predict():
    try:
        # Get query params from frontend
        model = request.args.get("model", "arima").lower()
        start_date = request.args.get("start_date", "2025-10-20")
        end_date = request.args.get("end_date", "2026-01-18")

        # Generate forecast dates
        days = pd.date_range(start=start_date, end=end_date, freq='D')

        # Generate mock data based on model type
        if model == "arima":
            base = 100
            noise = np.random.normal(0, 10, len(days))
            predictions = base + np.cumsum(noise)
        elif model == "sarima":
            base = 120
            noise = np.random.normal(0, 8, len(days))
            predictions = base + np.cumsum(noise)
        elif model == "lstm":
            base = 90
            noise = np.random.normal(0, 15, len(days))
            predictions = base + np.cumsum(noise)
        else:
            base = 100
            noise = np.random.normal(0, 10, len(days))
            predictions = base + np.cumsum(noise)

        # Build JSON response
        forecast = []
        for i, d in enumerate(days):
            forecast.append({
                "date": str(d.date()),
                "predicted_demand": round(predictions[i], 2)
            })

        return jsonify({
            "model_used": model.upper(),
            "total_days_predicted": len(forecast),
            "forecast": forecast
        })

    except Exception as e:
        print("❌ Error in /api/predict route:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/optimize', methods=['POST'])
def optimize():
    try:
        data = request.get_json(force=True)
        # Mock optimization logic
        recommendations = [
            {"item": "Product A", "order_quantity": 120},
            {"item": "Product B", "order_quantity": 85},
            {"item": "Product C", "order_quantity": 60}
        ]
        cost_breakdown = {
            "total_cost": 5600,
            "storage_cost": 1200,
            "ordering_cost": 4400
        }
        return jsonify({
            "recommendations": recommendations,
            "costBreakdown": cost_breakdown
        })
    
    except Exception as e:
        print("❌ Error in /api/optimize route:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
