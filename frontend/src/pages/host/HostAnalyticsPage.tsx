import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  AreaChart, Area, CartesianGrid, Legend 
} from 'recharts';
import { 
  BarChart3, Calendar, MapPin, TrendingUp, AlertTriangle, 
  RefreshCw, Info, Cpu, CheckCircle2 
} from 'lucide-react';
import { DemandAnalyticsResponse } from '../../types';
import { api } from '../../services/api';
import { CHENNAI_AREAS } from '../ExplorePage';

export const HostAnalyticsPage: React.FC = () => {
  const [selectedArea, setSelectedArea] = useState('Guindy');
  const [targetDate, setTargetDate] = useState(
    new Date(Date.now() + 86400000).toISOString().slice(0, 10)
  );
  const [demandData, setDemandData] = useState<DemandAnalyticsResponse | null>(null);
  const [allAreasComparison, setAllAreasComparison] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDemand = async () => {
    setLoading(true);
    try {
      // Fetch selected neighbourhood forecast
      const data = await api.getDemandAnalytics(selectedArea, targetDate);
      setDemandData(data);

      // Fetch all areas for cross-neighbourhood comparison
      const allData = await api.getDemandAnalytics(undefined, targetDate);
      
      // Aggregate average predicted score per area
      const areaAverages: Record<string, { totalScore: number; count: number }> = {};
      allData.forecasts.forEach((f) => {
        if (!areaAverages[f.neighbourhood]) {
          areaAverages[f.neighbourhood] = { totalScore: 0, count: 0 };
        }
        areaAverages[f.neighbourhood].totalScore += f.predicted_demand_score;
        areaAverages[f.neighbourhood].count += 1;
      });

      const compList = Object.entries(areaAverages).map(([area, stats]) => ({
        neighbourhood: area,
        avgDemandScore: Math.round(stats.totalScore / stats.count),
      }));
      setAllAreasComparison(compList);
    } catch (err) {
      console.error('Failed to load demand predictions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDemand();
  }, [selectedArea, targetDate]);

  const timeSlotChartData = demandData?.forecasts.map((f) => ({
    slot: f.time_slot.toUpperCase(),
    'Predicted Requests': f.predicted_booking_requests,
    'Historical Avg': f.historical_avg_requests,
    'CI Low': f.confidence_interval_low,
    'CI High': f.confidence_interval_high,
    score: f.predicted_demand_score,
    level: f.demand_level,
  })) || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 min-h-screen">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-teal-100 text-teal-800 text-xs font-bold mb-2">
            <Cpu className="w-3.5 h-3.5 text-teal-600" />
            <span>ML Demand Forecasting Engine</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Neighbourhood Demand Intelligence
          </h1>
          <p className="text-xs sm:text-sm text-slate-500">
            Forecast booking volume across Chennai areas and time-slots to optimize pricing.
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={selectedArea}
            onChange={(e) => setSelectedArea(e.target.value)}
            className="bg-white border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-semibold text-slate-800 shadow-xs focus:ring-1 focus:ring-brand-500"
          >
            {CHENNAI_AREAS.filter((a) => a !== 'All Neighbourhoods').map((a) => (
              <option key={a} value={a}>{a}</option>
            ))}
          </select>

          <input
            type="date"
            value={targetDate}
            onChange={(e) => setTargetDate(e.target.value)}
            className="bg-white border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-semibold text-slate-800 shadow-xs focus:ring-1 focus:ring-brand-500"
          />
        </div>
      </div>

      {/* Synthetic Data Disclaimer Banner */}
      <div className="mb-8 p-4 bg-amber-50/90 border border-amber-200 rounded-2xl flex items-start gap-3 text-xs text-amber-900">
        <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <strong className="font-semibold block mb-0.5">Synthetic Demonstration Model Notice:</strong>
          <span>{demandData?.data_source_note || 'All forecasts are generated from a local machine learning regression model trained on reproducible synthetic datasets. Predictions demonstrate MLOps pipelines and do not represent actual commercial rental demand.'}</span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <span className="text-xs font-semibold text-slate-500 block mb-1">Model Version</span>
          <div className="text-lg font-bold text-slate-900 font-mono">
            {demandData?.model_version || 'v1.0.0-baseline'}
          </div>
          <span className="text-[10px] text-teal-600 font-medium">Active in Registry</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <span className="text-xs font-semibold text-slate-500 block mb-1">Validation MAE</span>
          <div className="text-lg font-bold text-slate-900">
            {demandData?.mae ? demandData.mae.toFixed(2) : '1.71'}
          </div>
          <span className="text-[10px] text-slate-400">Mean Absolute Error</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <span className="text-xs font-semibold text-slate-500 block mb-1">Validation RMSE</span>
          <div className="text-lg font-bold text-slate-900">
            {demandData?.rmse ? demandData.rmse.toFixed(2) : '2.13'}
          </div>
          <span className="text-[10px] text-slate-400">Root Mean Squared Error</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <span className="text-xs font-semibold text-slate-500 block mb-1">Data Freshness</span>
          <div className="text-xs font-bold text-slate-800 truncate">
            {demandData?.data_freshness || 'Up to date'}
          </div>
          <span className="text-[10px] text-slate-400">Local timestamp</span>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-8">
        {/* Main Time Slot Chart */}
        <div className="lg:col-span-7 bg-white p-6 rounded-3xl border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-base text-slate-900">
                {selectedArea} Demand by Time Slot
              </h3>
              <p className="text-xs text-slate-500">
                Expected booking requests vs historical average on {targetDate}
              </p>
            </div>
            <span className="text-xs font-bold text-teal-600 bg-teal-50 px-2.5 py-1 rounded-full">
              4 Time Slots
            </span>
          </div>

          <div className="h-72 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timeSlotChartData}>
                <defs>
                  <linearGradient id="predGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#14b8a6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#14b8a6" stopOpacity={0.05}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="slot" textAnchor="middle" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', borderRadius: '12px', color: '#fff', fontSize: '11px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Area 
                  type="monotone" 
                  dataKey="Predicted Requests" 
                  stroke="#0d9488" 
                  fillOpacity={1} 
                  fill="url(#predGrad)" 
                />
                <Area 
                  type="monotone" 
                  dataKey="Historical Avg" 
                  stroke="#94a3b8" 
                  strokeDasharray="4 4" 
                  fill="transparent" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Neighbourhood Comparison Bar Chart */}
        <div className="lg:col-span-5 bg-white p-6 rounded-3xl border border-slate-200 shadow-xs space-y-4">
          <div>
            <h3 className="font-bold text-base text-slate-900">
              Cross-Neighbourhood Demand Index
            </h3>
            <p className="text-xs text-slate-500">
              Relative demand score (0-100) across Chennai on {targetDate}
            </p>
          </div>

          <div className="h-72 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={allAreasComparison} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 10 }} />
                <YAxis dataKey="neighbourhood" type="category" tick={{ fontSize: 10 }} width={80} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', borderRadius: '12px', color: '#fff', fontSize: '11px' }}
                />
                <Bar dataKey="avgDemandScore" fill="#14b8a6" radius={[0, 6, 6, 0]} name="Demand Score" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Time Slot Details Table */}
      <div className="bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-xs">
        <div className="p-6 border-b border-slate-100">
          <h3 className="font-bold text-base text-slate-900">
            Slot-by-Slot Forecast Breakdown ({selectedArea})
          </h3>
          <p className="text-xs text-slate-500">
            Includes estimated 95% confidence intervals derived from model validation RMSE.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-100 text-slate-600 font-semibold">
              <tr>
                <th className="py-3 px-6">Time Slot</th>
                <th className="py-3 px-6">Demand Level</th>
                <th className="py-3 px-6">Demand Score</th>
                <th className="py-3 px-6">Predicted Requests</th>
                <th className="py-3 px-6">Historical Avg</th>
                <th className="py-3 px-6">95% Confidence Interval</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {demandData?.forecasts.map((f, idx) => (
                <tr key={idx} className="hover:bg-slate-50/60 transition">
                  <td className="py-3.5 px-6 font-bold text-slate-900 capitalize">
                    {f.time_slot}
                  </td>
                  <td className="py-3.5 px-6">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        f.demand_level === 'Very High'
                          ? 'bg-rose-100 text-rose-800'
                          : f.demand_level === 'High'
                          ? 'bg-amber-100 text-amber-800'
                          : f.demand_level === 'Moderate'
                          ? 'bg-teal-100 text-teal-800'
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {f.demand_level}
                    </span>
                  </td>
                  <td className="py-3.5 px-6 font-semibold">
                    {f.predicted_demand_score} / 100
                  </td>
                  <td className="py-3.5 px-6 font-bold text-slate-900">
                    {f.predicted_booking_requests}
                  </td>
                  <td className="py-3.5 px-6 text-slate-500">
                    {f.historical_avg_requests}
                  </td>
                  <td className="py-3.5 px-6 font-mono text-[11px] text-slate-600">
                    [{f.confidence_interval_low.toFixed(1)} – {f.confidence_interval_high.toFixed(1)}]
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
