import { useState, useEffect } from 'react';
import Header from './components/Header';
import Navigation from './components/Navigation';
import DemandForecast from './components/DemandForecast';
import InventoryRecommendations from './components/InventoryRecommendations';
import CostBreakdown from './components/CostBreakdown';
import SimulationControls from './components/SimulationControls';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';
import { generateMockForecast, generateMockRecommendations, generateMockCostBreakdown } from './utils/mockData';
import type { DemandForecast as DemandForecastType, InventoryRecommendation, CostBreakdown as CostBreakdownType } from './types/inventory';
import './App.css';

function App() {
  const [activeView, setActiveView] = useState('forecast');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [forecast, setForecast] = useState<DemandForecastType[]>([]);
  const [recommendations, setRecommendations] = useState<InventoryRecommendation[]>([]);
  const [costs, setCosts] = useState<CostBreakdownType | null>(null);
  const [chartType, setChartType] = useState<'pie' | 'bar'>('pie');

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const mockForecast = generateMockForecast();
      const mockRecommendations = generateMockRecommendations();
      const mockCosts = generateMockCostBreakdown();

      setForecast(mockForecast);
      setRecommendations(mockRecommendations);
      setCosts(mockCosts);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunForecast = async (startDate: string, endDate: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const days = Math.ceil((new Date(endDate).getTime() - new Date(startDate).getTime()) / (1000 * 60 * 60 * 24));
      const mockForecast = generateMockForecast(days);
      setForecast(mockForecast);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run forecast');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOptimize = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const mockRecommendations = generateMockRecommendations();
      const mockCosts = generateMockCostBreakdown();
      setRecommendations(mockRecommendations);
      setCosts(mockCosts);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to optimize inventory');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <Header />

      <div className="app-container">
        <Navigation activeView={activeView} onViewChange={setActiveView} />

        <main className="main-content">
          {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}

          {activeView === 'forecast' && (
            <div className="view-content">
              <SimulationControls
                onRunForecast={handleRunForecast}
                onOptimize={handleOptimize}
                isLoading={isLoading}
              />

              {isLoading ? (
                <LoadingSpinner message="Running forecast analysis..." />
              ) : (
                <>
                  {forecast.length > 0 && <DemandForecast data={forecast} />}
                  {costs && <CostBreakdown costs={costs} chartType={chartType} />}
                </>
              )}
            </div>
          )}

          {activeView === 'optimization' && (
            <div className="view-content">
              {isLoading ? (
                <LoadingSpinner message="Optimizing inventory..." />
              ) : (
                <>
                  {recommendations.length > 0 && (
                    <InventoryRecommendations recommendations={recommendations} />
                  )}
                  {costs && <CostBreakdown costs={costs} chartType={chartType} />}
                </>
              )}
            </div>
          )}

          {activeView === 'settings' && (
            <div className="view-content">
              <div className="card">
                <div className="card-header">
                  <h2>Settings</h2>
                  <p className="card-subtitle">Configure dashboard preferences</p>
                </div>
                <div className="card-body">
                  <div className="settings-section">
                    <h3>Chart Preferences</h3>
                    <div className="setting-item">
                      <label>Cost Breakdown Chart Type</label>
                      <div className="radio-group">
                        <label className="radio-label">
                          <input
                            type="radio"
                            name="chartType"
                            value="pie"
                            checked={chartType === 'pie'}
                            onChange={(e) => setChartType(e.target.value as 'pie' | 'bar')}
                          />
                          <span>Pie Chart</span>
                        </label>
                        <label className="radio-label">
                          <input
                            type="radio"
                            name="chartType"
                            value="bar"
                            checked={chartType === 'bar'}
                            onChange={(e) => setChartType(e.target.value as 'pie' | 'bar')}
                          />
                          <span>Bar Chart</span>
                        </label>
                      </div>
                    </div>
                  </div>

                  <div className="settings-section">
                    <h3>API Configuration</h3>
                    <div className="setting-item">
                      <label htmlFor="api-url">API Base URL</label>
                      <input
                        id="api-url"
                        type="text"
                        placeholder="/api"
                        className="settings-input"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
