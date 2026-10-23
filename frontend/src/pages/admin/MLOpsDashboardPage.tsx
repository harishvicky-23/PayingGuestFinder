import React, { useState, useEffect } from 'react';
import { 
  Cpu, GitBranch, Activity, Play, CheckCircle2, 
  AlertTriangle, RefreshCw, BarChart2, ShieldCheck, Database, Layers
} from 'lucide-react';
import { MLStatusResponse, DriftReport } from '../../types';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

export const MLOpsDashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [status, setStatus] = useState<MLStatusResponse | null>(null);
  const [drift, setDrift] = useState<DriftReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [retrainingModel, setRetrainingModel] = useState<string | null>(null);
  const [activatingModel, setActivatingModel] = useState<string | null>(null);
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  const fetchMLOpsData = async () => {
    setLoading(true);
    try {
      const [statusData, driftData] = await Promise.all([
        api.getMLStatus(),
        api.getDriftReport(),
      ]);
      setStatus(statusData);
      setDrift(driftData);
    } catch (err) {
      console.error('Failed to load MLOps telemetry:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMLOpsData();
  }, []);

  const handleRetrain = async (modelName: string) => {
    setRetrainingModel(modelName);
    setMessage(null);
    try {
      const res: any = await api.triggerRetrain(modelName, false);
      setMessage({
        text: `Retraining completed! Registered candidate run ID: ${res.candidate?.run_id || 'N/A'}. Review metrics below before activating.`,
        type: 'success',
      });
      await fetchMLOpsData();
    } catch (err: any) {
      setMessage({
        text: `Retraining failed: ${err.message}`,
        type: 'error',
      });
    } finally {
      setRetrainingModel(null);
    }
  };

  const handleActivate = async (modelName: string) => {
    setActivatingModel(modelName);
    setMessage(null);
    try {
      await api.activateCandidate(modelName);
      setMessage({
        text: `Candidate model for '${modelName}' successfully validated and activated into production!`,
        type: 'success',
      });
      await fetchMLOpsData();
    } catch (err: any) {
      setMessage({
        text: `Activation rejected: ${err.message}`,
        type: 'error',
      });
    } finally {
      setActivatingModel(null);
    }
  };

  const recActive = status?.active_models?.recommender;
  const recCandidate = status?.candidates?.recommender;
  const demandActive = status?.active_models?.demand_predictor;
  const demandCandidate = status?.candidates?.demand_predictor;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 min-h-screen">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-indigo-100 text-indigo-800 text-xs font-bold mb-2">
            <Cpu className="w-3.5 h-3.5 text-indigo-600" />
            <span>Local MLOps Lifecycle & Registry</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Machine Learning Operations Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-slate-500">
            Real-time model registry manifests, MLflow tracking runs, drift evaluation, and controlled candidate promotion.
          </p>
        </div>

        <button
          onClick={fetchMLOpsData}
          disabled={loading}
          className="px-4 py-2 border border-slate-300 hover:bg-slate-50 rounded-xl text-xs font-semibold text-slate-700 transition flex items-center gap-1.5 self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Refresh Telemetry
        </button>
      </div>

      {/* Global alert feedback */}
      {message && (
        <div
          className={`mb-6 p-4 rounded-2xl border text-xs font-medium flex items-start gap-2.5 ${
            message.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
              : 'bg-rose-50 border-rose-200 text-rose-900'
          }`}
        >
          {message.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
          ) : (
            <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
          )}
          <span>{message.text}</span>
        </div>
      )}

      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold">Active Recommender</span>
            <Layers className="w-4 h-4 text-teal-600" />
          </div>
          <div className="text-lg font-bold text-slate-900 font-mono">
            {recActive?.version || 'v1.0.0-baseline'}
          </div>
          <span className="text-[11px] text-slate-500 capitalize">
            Type: {recActive?.model_type?.replace(/_/g, ' ') || 'weighted baseline'}
          </span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold">Active Demand Predictor</span>
            <Activity className="w-4 h-4 text-brand-600" />
          </div>
          <div className="text-lg font-bold text-slate-900 font-mono">
            {demandActive?.version || 'v1.0.0-baseline'}
          </div>
          <span className="text-[11px] text-slate-500 capitalize">
            Type: {demandActive?.model_type?.replace(/_/g, ' ') || 'historical average'}
          </span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold">Feature Drift Status</span>
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-lg font-bold text-emerald-700 flex items-center gap-1.5">
            {drift?.overall_drift_detected ? (
              <span className="text-amber-600">Drift Alert</span>
            ) : (
              <span>Stable (PSI &lt; 0.10)</span>
            )}
          </div>
          <span className="text-[11px] text-slate-400">
            Reference items: {drift?.reference_data_size || 0}
          </span>
        </div>
      </div>

      {/* Model Section A: Recommender Ranker */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 shadow-xs mb-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="w-2.5 h-2.5 rounded-full bg-teal-500" />
              <h2 className="text-lg font-bold text-slate-900">Module A: Personalized Recommender Engine</h2>
            </div>
            <p className="text-xs text-slate-500">
              Ranks properties using Haversine distance, budget ratio, amenity overlap, and rating boost.
            </p>
          </div>

          <button
            onClick={() => handleRetrain('recommender')}
            disabled={retrainingModel === 'recommender'}
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition shadow-xs flex items-center gap-1.5 disabled:opacity-50"
          >
            {retrainingModel === 'recommender' ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Play className="w-3.5 h-3.5 fill-current" />
            )}
            Trigger Retraining & Candidate Eval
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Active Model Box */}
          <div className="p-4 rounded-2xl bg-teal-50/50 border border-teal-200 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-teal-900 uppercase tracking-wider">Active Model in Production</span>
              <span className="px-2 py-0.5 rounded-full bg-teal-600 text-white text-[10px] font-bold">Serving Traffic</span>
            </div>
            <div className="text-sm font-bold text-slate-900 font-mono">
              Version: {recActive?.version}
            </div>
            <div className="text-xs text-slate-600">
              Architecture: <strong className="capitalize">{recActive?.model_type?.replace(/_/g, ' ')}</strong>
            </div>
            <div className="text-xs text-slate-500 font-mono text-[11px] truncate">
              MLflow Run ID: {recActive?.run_id || 'Initial Baseline'}
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-2 gap-2 pt-2 border-t border-teal-100 text-xs">
              <div className="bg-white p-2 rounded-lg border border-teal-100">
                <span className="text-slate-400 block text-[10px]">Precision@5</span>
                <span className="font-bold text-slate-900">{recActive?.metrics?.['precision@5'] ?? '0.74'}</span>
              </div>
              <div className="bg-white p-2 rounded-lg border border-teal-100">
                <span className="text-slate-400 block text-[10px]">NDCG@5</span>
                <span className="font-bold text-slate-900">{recActive?.metrics?.['ndcg@5'] ?? '0.79'}</span>
              </div>
            </div>
          </div>

          {/* Candidate Model Box */}
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">Latest Candidate Model</span>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                recCandidate ? 'bg-amber-100 text-amber-800' : 'bg-slate-200 text-slate-600'
              }`}>
                {recCandidate ? 'Awaiting Approval' : 'None Staged'}
              </span>
            </div>

            {recCandidate ? (
              <>
                <div className="text-sm font-bold text-slate-900 font-mono">
                  Version: {recCandidate.version}
                </div>
                <div className="text-xs text-slate-600">
                  Architecture: <strong className="capitalize">{recCandidate.model_type?.replace(/_/g, ' ')}</strong>
                </div>
                <div className="text-xs text-slate-500 font-mono text-[11px] truncate">
                  MLflow Run ID: {recCandidate.run_id}
                </div>

                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-200 text-xs">
                  <div className="bg-white p-2 rounded-lg border border-slate-200">
                    <span className="text-slate-400 block text-[10px]">Precision@5</span>
                    <span className="font-bold text-slate-900">{recCandidate.metrics?.['precision@5']}</span>
                  </div>
                  <div className="bg-white p-2 rounded-lg border border-slate-200">
                    <span className="text-slate-400 block text-[10px]">NDCG@5</span>
                    <span className="font-bold text-slate-900">{recCandidate.metrics?.['ndcg@5']}</span>
                  </div>
                </div>

                <button
                  onClick={() => handleActivate('recommender')}
                  disabled={activatingModel === 'recommender'}
                  className="w-full py-2 bg-brand-500 hover:bg-brand-600 text-white rounded-xl text-xs font-bold transition shadow-xs"
                >
                  {activatingModel === 'recommender' ? 'Validating...' : 'Safely Promote Candidate to Active'}
                </button>
              </>
            ) : (
              <p className="text-xs text-slate-500 py-6 text-center">
                Click "Trigger Retraining" above to train a new candidate model and log experiment metrics to MLflow.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Model Section B: Neighbourhood Demand Predictor */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 shadow-xs mb-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="w-2.5 h-2.5 rounded-full bg-indigo-500" />
              <h2 className="text-lg font-bold text-slate-900">Module B: Neighbourhood Demand Forecaster</h2>
            </div>
            <p className="text-xs text-slate-500">
              Predicts expected booking volume per neighbourhood across morning, afternoon, evening, and night slots.
            </p>
          </div>

          <button
            onClick={() => handleRetrain('demand_predictor')}
            disabled={retrainingModel === 'demand_predictor'}
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition shadow-xs flex items-center gap-1.5 disabled:opacity-50"
          >
            {retrainingModel === 'demand_predictor' ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Play className="w-3.5 h-3.5 fill-current" />
            )}
            Trigger Retraining & Candidate Eval
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Active Demand Model */}
          <div className="p-4 rounded-2xl bg-indigo-50/50 border border-indigo-200 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-indigo-900 uppercase tracking-wider">Active Model in Production</span>
              <span className="px-2 py-0.5 rounded-full bg-indigo-600 text-white text-[10px] font-bold">Serving Traffic</span>
            </div>
            <div className="text-sm font-bold text-slate-900 font-mono">
              Version: {demandActive?.version}
            </div>
            <div className="text-xs text-slate-600">
              Architecture: <strong className="capitalize">{demandActive?.model_type?.replace(/_/g, ' ')}</strong>
            </div>
            <div className="text-xs text-slate-500 font-mono text-[11px] truncate">
              MLflow Run ID: {demandActive?.run_id || 'Initial Baseline'}
            </div>

            <div className="grid grid-cols-2 gap-2 pt-2 border-t border-indigo-100 text-xs">
              <div className="bg-white p-2 rounded-lg border border-indigo-100">
                <span className="text-slate-400 block text-[10px]">MAE (Mean Abs Error)</span>
                <span className="font-bold text-slate-900">{demandActive?.metrics?.mae ?? '1.71'}</span>
              </div>
              <div className="bg-white p-2 rounded-lg border border-indigo-100">
                <span className="text-slate-400 block text-[10px]">RMSE</span>
                <span className="font-bold text-slate-900">{demandActive?.metrics?.rmse ?? '2.13'}</span>
              </div>
            </div>
          </div>

          {/* Candidate Demand Model */}
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">Latest Candidate Model</span>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                demandCandidate ? 'bg-amber-100 text-amber-800' : 'bg-slate-200 text-slate-600'
              }`}>
                {demandCandidate ? 'Awaiting Approval' : 'None Staged'}
              </span>
            </div>

            {demandCandidate ? (
              <>
                <div className="text-sm font-bold text-slate-900 font-mono">
                  Version: {demandCandidate.version}
                </div>
                <div className="text-xs text-slate-600">
                  Architecture: <strong className="capitalize">{demandCandidate.model_type?.replace(/_/g, ' ')}</strong>
                </div>
                <div className="text-xs text-slate-500 font-mono text-[11px] truncate">
                  MLflow Run ID: {demandCandidate.run_id}
                </div>

                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-200 text-xs">
                  <div className="bg-white p-2 rounded-lg border border-slate-200">
                    <span className="text-slate-400 block text-[10px]">MAE</span>
                    <span className="font-bold text-slate-900">{demandCandidate.metrics?.mae}</span>
                  </div>
                  <div className="bg-white p-2 rounded-lg border border-slate-200">
                    <span className="text-slate-400 block text-[10px]">RMSE</span>
                    <span className="font-bold text-slate-900">{demandCandidate.metrics?.rmse}</span>
                  </div>
                </div>

                <button
                  onClick={() => handleActivate('demand_predictor')}
                  disabled={activatingModel === 'demand_predictor'}
                  className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition shadow-xs"
                >
                  {activatingModel === 'demand_predictor' ? 'Validating...' : 'Safely Promote Candidate to Active'}
                </button>
              </>
            ) : (
              <p className="text-xs text-slate-500 py-6 text-center">
                Click "Trigger Retraining" above to evaluate a new demand forecaster candidate.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Drift Monitoring Table */}
      <div className="bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-xs">
        <div className="p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="font-bold text-base text-slate-900">
              Feature Distribution Drift Monitoring (PSI)
            </h3>
            <p className="text-xs text-slate-500">
              Evaluates Population Stability Index between reference training distributions and recent live queries.
            </p>
          </div>
          <div className="text-xs text-slate-500 font-medium">
            PSI &lt; 0.10: Stable • 0.10 - 0.25: Moderate Shift • &gt; 0.25: Drift Action Required
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-100 text-slate-600 font-semibold">
              <tr>
                <th className="py-3 px-6">Feature</th>
                <th className="py-3 px-6">PSI Metric</th>
                <th className="py-3 px-6">Status</th>
                <th className="py-3 px-6">Ref Mean</th>
                <th className="py-3 px-6">Current Mean</th>
                <th className="py-3 px-6">Ref Std</th>
                <th className="py-3 px-6">Current Std</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {drift?.feature_drifts && Object.entries(drift.feature_drifts).map(([feat, d]) => (
                <tr key={feat} className="hover:bg-slate-50/60 transition">
                  <td className="py-3.5 px-6 font-bold text-slate-900 capitalize font-mono">
                    {feat}
                  </td>
                  <td className="py-3.5 px-6 font-bold">
                    {d.psi.toFixed(4)}
                  </td>
                  <td className="py-3.5 px-6">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        d.status === 'significant_drift'
                          ? 'bg-rose-100 text-rose-800'
                          : d.status === 'moderate_drift'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-emerald-100 text-emerald-800'
                      }`}
                    >
                      {d.status === 'significant_drift' ? 'Action Required' : d.status === 'moderate_drift' ? 'Moderate Shift' : 'Stable'}
                    </span>
                  </td>
                  <td className="py-3.5 px-6 text-slate-500">{d.ref_mean}</td>
                  <td className="py-3.5 px-6 text-slate-900 font-medium">{d.cur_mean}</td>
                  <td className="py-3.5 px-6 text-slate-500">{d.ref_std}</td>
                  <td className="py-3.5 px-6 text-slate-900 font-medium">{d.cur_std}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
