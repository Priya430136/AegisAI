import React, { useState } from "react";
import { AnomalyIncident } from "../types";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { Terminal, ShieldAlert, Cpu, CheckCircle2, ArrowRight } from "lucide-react";

interface ExplainabilityTabProps {
  anomalies: AnomalyIncident[];
  selectedAnomaly: AnomalyIncident | null;
}

export const ExplainabilityTab: React.FC<ExplainabilityTabProps> = ({ anomalies, selectedAnomaly: initialSelected }) => {
  const [selectedIndex, setSelectedIndex] = useState<number>(0);

  const activeAnomaly = initialSelected || anomalies[selectedIndex] || {
    event_index: 0,
    entity_id: "USR-1042",
    timestamp: "2026-07-26T03:12:00",
    risk_score: 94.2,
    predicted_attack: "Impossible Travel",
    confidence: 98.5,
    explanation: {
      risk_score_percent: 94.2,
      attack_type: "Impossible Travel",
      feature_contributions: {
        velocity_kmh: 42.5,
        failed_login_count: 22.0,
        has_suspicious_cmd: 15.0,
        is_preferred_device: 12.0,
        is_off_hours: 8.5
      },
      reasons: [
        "Impossible geo-velocity detected: 4,200 km/h between consecutive logins.",
        "Unrecognized device fingerprint hash missing from entity's historical registry.",
        "Activity occurred outside entity's normal working hours (03:12 UTC)."
      ],
      recommendations: [
        "Revoke active user OAuth / JWT tokens immediately.",
        "Prompt user for mandatory step-up re-authentication.",
        "Notify SOC tier-2 analyst for credential compromise investigation."
      ]
    }
  };

  const featureContributions = activeAnomaly.explanation?.feature_contributions || {};
  const chartData = Object.entries(featureContributions).map(([key, val]) => ({
    feature: key.replace(/_/g, " "),
    importance: Number(val)
  })).sort((a, b) => b.importance - a.importance);

  const colors = ["#f43f5e", "#f97316", "#eab308", "#3b82f6", "#a855f7", "#06b6d4"];

  return (
    <div id="explainability-tab" className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-[#111827] border border-slate-800 p-4 rounded-lg">
        <div>
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wide flex items-center gap-2">
            <Terminal className="w-4 h-4 text-blue-400" /> Explainable AI (XAI) & SHAP Risk Attribution
          </h2>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Deconstructs complex neural sequence risk scores into human-understandable SHAP feature weights.
          </p>
        </div>

        {/* Incident Selector */}
        <div className="flex items-center gap-3">
          <label className="text-xs font-medium text-slate-400">Select Anomaly Incident:</label>
          <select
            id="xai-incident-selector"
            value={selectedIndex}
            onChange={(e) => setSelectedIndex(Number(e.target.value))}
            className="bg-[#1F2937] border border-slate-700 rounded px-3 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500 font-mono"
          >
            {anomalies.map((a, i) => (
              <option key={i} value={i}>
                #{i + 1}: {a.entity_id} - {a.predicted_attack} ({a.risk_score}%)
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Incident Summary Banner */}
      <div className="bg-[#111827] border border-slate-800 rounded-lg p-5 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 shadow-lg">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded bg-rose-950 text-rose-400 border border-rose-800/40 text-xs font-mono font-bold">
              RISK: {activeAnomaly.risk_score}%
            </span>
            <span className="text-sm font-bold text-blue-400 font-mono">{activeAnomaly.entity_id}</span>
          </div>
          <h3 className="text-lg font-bold text-slate-100 mt-1">{activeAnomaly.predicted_attack}</h3>
          <p className="text-[11px] text-slate-400 font-mono mt-0.5">Timestamp: {new Date(activeAnomaly.timestamp).toLocaleString()} | Model Confidence: {activeAnomaly.confidence}%</p>
        </div>

        <div className="bg-[#1F2937] px-4 py-2 rounded border border-slate-700 text-xs font-mono">
          <span className="text-slate-400">Attribution Engine:</span> <span className="text-emerald-400 font-semibold">Tree SHAP / DeepSHAP Vector</span>
        </div>
      </div>

      {/* Main Grid: SHAP Chart + Natural Language Explanation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: SHAP Feature Importance Bar Chart */}
        <div className="bg-[#111827] border border-slate-800 rounded-lg p-5">
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2 mb-4 border-b border-slate-800 pb-3">
            <Cpu className="w-4 h-4 text-blue-400" /> Relative Feature Risk Contributions (SHAP %)
          </h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 80, bottom: 5 }}>
                <XAxis type="number" domain={[0, 100]} stroke="#64748b" fontSize={11} unit="%" />
                <YAxis type="category" dataKey="feature" stroke="#64748b" fontSize={11} tick={{ fill: "#94a3b8" }} />
                <Tooltip
                  formatter={(value: any) => [`${value}%`, "Contribution"]}
                  contentStyle={{ backgroundColor: "#111827", borderColor: "#334155", color: "#fff", fontSize: "12px" }}
                />
                <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
                  {chartData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right: Natural Reasons & Recommendations */}
        <div className="space-y-4">
          <div className="bg-[#111827] border border-slate-800 rounded-lg p-5">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2 mb-3 border-b border-slate-800 pb-3">
              <ShieldAlert className="w-4 h-4 text-amber-500" /> Analyst Explanatory Reasons
            </h3>
            <ul className="space-y-2 text-xs text-slate-300">
              {(activeAnomaly.explanation?.reasons || []).map((reason, i) => (
                <li key={i} className="flex items-start gap-2 bg-[#1F2937] p-2.5 rounded border border-slate-700/80">
                  <ArrowRight className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                  <span className="leading-relaxed">{reason}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-[#111827] border border-slate-800 rounded-lg p-5">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2 mb-3 border-b border-slate-800 pb-3">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Automated SOAR Remediation Playbook
            </h3>
            <ul className="space-y-2 text-xs text-slate-300">
              {(activeAnomaly.explanation?.recommendations || []).map((rec, i) => (
                <li key={i} className="flex items-start gap-2 bg-[#1F2937] p-2.5 rounded border border-slate-700/80">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <span className="leading-relaxed">{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
