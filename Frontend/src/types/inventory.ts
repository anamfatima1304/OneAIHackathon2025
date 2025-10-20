export interface DemandForecast {
  date: string;
  predicted: number;
  upperBound: number;
  lowerBound: number;
}

export interface InventoryRecommendation {
  week: number;
  recommendedLevel: number;
  reorderDate: string;
  safetyStock: number;
  risk: 'low' | 'medium' | 'high';
}

export interface CostBreakdown {
  orderingCost: number;
  holdingCost: number;
  stockoutCost: number;
}

export interface ForecastModel {
  id: string;
  name: string;
}

export interface OptimizationRequest {
  startDate: string;
  endDate: string;
  model: string;
}
