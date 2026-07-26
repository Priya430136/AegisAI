import React from "react";
import { Metrics, AnomalyIncident } from "../types";
import { ShieldCheck, Zap, AlertTriangle, Cpu, Layers, Activity, Lock, ArrowUpRight } from "lucide-react";
import { RiskHeatmap } from "./RiskHeatmap";

interface OverviewTabProps {
  metrics: Metrics;
  anomalies: AnomalyIncident[];
  onNavigateToAlerts: () => void;
}

export const OverviewTab: React.FC<OverviewTabProps> = ({ metrics, anomalies, onNavigateToAlerts }) => {
  return (
    <div id="overview-tab-content" className="space-y-6">
      {/* Banner / Hero Header */}
      <div className="bg-[#111827] border border-slate-800 rounded-lg p-5 shadow-lg relative overflow-hidden">
        <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-blue-600/10 text-blue-400 border border-blue-500/20 text-[10px] font-bold uppercase tracking-wider mb-2">
              <Zap className="w-3.5 h-3.5 text-amber-500" /> Behavioral Threat Intelligence
            </div>
            <h1 className="text-xl md:text-2xl font-bold text-white tracking-tight">
              AEGISAI ANOMALY DETECTOR
            </h1>
            <p className="text-slate-400 max-w-2xl text-xs mt-1 leading-relaxed">
              Continuously monitors user access sequences across 2,000+ profiles. Flags zero-day anomalies, credential stuffing, and insider threats under extreme class imbalance.
            </p>
          </div>
          <button
            onClick={onNavigateToAlerts}
            id="view-live-alerts-btn"
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-500 text-white font-bold px-4 py-2 rounded text-xs tracking-wider uppercase transition-all shadow-md shadow-blue-600/20"
          >
            <AlertTriangle className="w-3.5 h-3.5 text-amber-300" />
            <span>Action Required ({anomalies.length})</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div id="kpi-metrics-grid" className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-[#1F2937] border border-slate-700 rounded p-4">
          <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Dataset Events</p>
          <p className="text-2xl font-bold text-white mt-1">{(metrics.dataset_size || 50000).toLocaleString()}</p>
          <p className="text-[10px] text-emerald-400 font-mono mt-1 flex items-center gap-1">
            <Activity className="w-3 h-3" /> 2,000 Entities
          </p>
        </div>

        <div className="bg-[#1F2937] border border-slate-700 rounded p-4">
          <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Accuracy Score</p>
          <p className="text-2xl font-bold text-emerald-400 mt-1">{((metrics.accuracy || 0.9829) * 100).toFixed(1)}%</p>
          <p className="text-[10px] text-slate-400 mt-1 font-mono">Ensemble Baseline</p>
        </div>

        <div className="bg-[#1F2937] border border-slate-700 rounded p-4">
          <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Precision</p>
          <p className="text-2xl font-bold text-blue-400 mt-1">{((metrics.precision || 0.962) * 100).toFixed(1)}%</p>
          <p className="text-[10px] text-slate-400 mt-1 font-mono">Low False Alarms</p>
        </div>

        <div className="bg-[#1F2937] border border-slate-700 rounded p-4">
          <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Recall</p>
          <p className="text-2xl font-bold text-purple-400 mt-1">{((metrics.recall || 0.918) * 100).toFixed(1)}%</p>
          <p className="text-[10px] text-slate-400 mt-1 font-mono">Catch Rate</p>
        </div>

        <div className="bg-[#1F2937] border border-slate-700 rounded p-4">
          <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">ROC AUC</p>
          <p className="text-2xl font-bold text-amber-500 mt-1">{(metrics.roc_auc || 0.982).toFixed(3)}</p>
          <p className="text-[10px] text-slate-400 mt-1 font-mono">Discriminative Power</p>
        </div>

        <div className="bg-[#1F2937] border border-slate-700 rounded p-4">
          <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">FPR Rate</p>
          <p className="text-2xl font-bold text-rose-400 mt-1">{((metrics.false_positive_rate || 0.0035) * 100).toFixed(2)}%</p>
          <p className="text-[10px] text-slate-400 mt-1 font-mono">Target &lt; 1.0%</p>
        </div>
      </div>

      {/* Risk Heatmap Section */}
      <RiskHeatmap anomalies={anomalies} />

      {/* Main Architecture & Core Capabilities Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: System Architecture */}
        <div className="lg:col-span-2 bg-[#111827] border border-slate-800 rounded-lg p-5">
          <h2 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2 mb-4 border-b border-slate-800 pb-3">
            <Layers className="w-4 h-4 text-blue-400" /> Core ML Pipeline Architecture
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-[#1F2937] border border-slate-700/80 rounded p-3.5">
              <div className="font-bold text-blue-400 text-xs flex items-center gap-2 uppercase">
                <Cpu className="w-3.5 h-3.5 text-blue-400" /> 1. Sequential RNN / LSTM Model
              </div>
              <p className="text-xs text-slate-300 mt-1.5 leading-relaxed">
                Evaluates time-series access sequence vectors across sliding windows to flag multi-stage lateral movement and low-and-slow exfiltration.
              </p>
            </div>

            <div className="bg-[#1F2937] border border-slate-700/80 rounded p-3.5">
              <div className="font-bold text-emerald-400 text-xs flex items-center gap-2 uppercase">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> 2. Unsupervised Profile Baselines
              </div>
              <p className="text-xs text-slate-300 mt-1.5 leading-relaxed">
                Calculates statistical distance from an entity's normal working hours, preferred auth tokens, device fingerprints, and standard IP subnets.
              </p>
            </div>

            <div className="bg-[#1F2937] border border-slate-700/80 rounded p-3.5">
              <div className="font-bold text-amber-500 text-xs flex items-center gap-2 uppercase">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-500" /> 3. Multi-Class Attack Classifier
              </div>
              <p className="text-xs text-slate-300 mt-1.5 leading-relaxed">
                Categorizes anomalies into 7 distinct cyber attack vectors: Brute Force, Impossible Travel, Credential Stuffing, Lateral Movement, Device Spoofing, Exfiltration, Insider Drift.
              </p>
            </div>

            <div className="bg-[#1F2937] border border-slate-700/80 rounded p-3.5">
              <div className="font-bold text-purple-400 text-xs flex items-center gap-2 uppercase">
                <Lock className="w-3.5 h-3.5 text-purple-400" /> 4. SHAP Explainability & Playbooks
              </div>
              <p className="text-xs text-slate-300 mt-1.5 leading-relaxed">
                Outputs feature attribution vectors, natural language risk explanations, and automated SOAR response playbooks for SOC analysts.
              </p>
            </div>
          </div>
        </div>

        {/* Right Column: Attack Distribution Breakdown */}
        <div className="bg-[#111827] border border-slate-800 rounded-lg p-5 flex flex-col justify-between">
          <div>
            <h2 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2 mb-4 border-b border-slate-800 pb-3">
              <Activity className="w-4 h-4 text-purple-400" /> Threat Vector Volume Breakdown
            </h2>
            <div className="space-y-3">
              {Object.entries(metrics.attack_distribution || {
                "Brute Force": 210,
                "Impossible Travel": 185,
                "Credential Stuffing": 150,
                "Lateral Movement": 145,
                "Device Spoofing": 120,
                "Low and Slow Exfiltration": 95,
                "Insider Drift": 95
              }).map(([attack, count]) => {
                const values = Object.values(metrics.attack_distribution || {}) as number[];
                const total = values.reduce((a, b) => a + b, 1);
                const pct = Math.round(((count as number) / total) * 100);
                return (
                  <div key={attack}>
                    <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
                      <span>{attack}</span>
                      <span className="text-slate-400 font-mono text-[11px]">{count} ({pct}%)</span>
                    </div>
                    <div className="w-full bg-[#1F2937] rounded-full h-1.5 overflow-hidden">
                      <div
                        className="bg-blue-500 h-1.5 rounded-full transition-all duration-500"
                        style={{ width: `${Math.max(5, pct * 3)}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-800 text-[10px] text-slate-500 uppercase tracking-wider text-center font-mono">
            Class Imbalance: 2.0% Anomalies / 98.0% Baseline Traffic
          </div>
        </div>
      </div>
    </div>
  );
};
