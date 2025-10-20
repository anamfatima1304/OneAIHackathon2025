import type { DemandForecast, InventoryRecommendation, CostBreakdown, OptimizationRequest } from '../types/inventory';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export interface ForecastResponse {
  forecast: DemandForecast[];
}

export interface OptimizationResponse {
  recommendations: InventoryRecommendation[];
  costBreakdown: CostBreakdown;
}

export async function fetchForecast(): Promise<ForecastResponse> {
  const response = await fetch(`${API_BASE_URL}/predict`);
  if (!response.ok) {
    throw new Error(`Failed to fetch forecast: ${response.statusText}`);
  }
  return response.json();
}

export async function optimizeInventory(request: OptimizationRequest): Promise<OptimizationResponse> {
  const response = await fetch(`${API_BASE_URL}/optimize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`Failed to optimize inventory: ${response.statusText}`);
  }
  return response.json();
}
