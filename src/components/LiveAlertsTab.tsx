import React, { useState } from "react";
import { AnomalyIncident } from "../types";
import { Search, Filter, ShieldAlert, CheckCircle, ChevronDown, ChevronUp } from "lucide-react";

interface LiveAlertsTabProps {
  anomalies: AnomalyIncident[];
  onSelectAnomalyForXAI: (anomaly: AnomalyIncident) => void;
}

export const LiveAlertsTab: React.FC<LiveAlertsTabProps> = ({ anomalies, onSelectAnomalyForXAI }) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedAttackFilter, setSelectedAttackFilter] = useState("All");
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [mitigatedIds, setMitigatedIds] = useState<Set<number>>(new Set());

  const attackTypes = [
    "All",
    "Brute Force",
    "Impossible Travel",
    "Credential Stuffing",
    "Lateral Movement",
    "Device Spoofing",
    "Low and Slow Exfiltration",
    "Insider Drift"
  ];

  const filteredAnomalies = anomalies.filter((a) => {
    const matchesSearch =
      a.entity_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.predicted_attack.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = selectedAttackFilter === "All" || a.predicted_attack === selectedAttackFilter;
    return matchesSearch && matchesFilter;
  });

  const handleMitigate = (eventIndex: number) => {
    setMitigatedIds((prev) => new Set(prev).add(eventIndex));
  };

  return (
    <div id="live-alerts-tab" className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-[#111827] border border-slate-800 p-4 rounded-lg">
        <div>
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wide flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-rose-500" /> High-Confidence Anomaly Queue
          </h2>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Evaluated by sequential neural engine & baseline statistical models.
          </p>
        </div>

        {/* Search & Filter Controls */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          <div className="relative flex-1 md:w-64">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              id="alert-search-input"
              placeholder="Filter by Entity ID or Attack..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-[#1F2937] border border-slate-700 rounded pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono"
            />
          </div>

          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              id="attack-filter-select"
              value={selectedAttackFilter}
              onChange={(e) => setSelectedAttackFilter(e.target.value)}
              className="bg-[#1F2937] border border-slate-700 rounded px-3 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500 font-mono"
            >
              {attackTypes.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="bg-[#111827] border border-slate-800 rounded-lg overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#1F2937]/80 text-slate-400 uppercase tracking-wider text-[10px] font-semibold border-b border-slate-800">
              <tr>
                <th className="p-3">Risk Score</th>
                <th className="p-3">User / Entity ID</th>
                <th className="p-3">Attack Classification</th>
                <th className="p-3">Timestamp</th>
                <th className="p-3">Confidence</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-slate-300">
              {filteredAnomalies.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-8 text-slate-500 font-sans">
                    No active anomaly alerts matching the filter criteria.
                  </td>
                </tr>
              ) : (
                filteredAnomalies.slice(0, 30).map((alert) => {
                  const isExpanded = expandedId === alert.event_index;
                  const isMitigated = mitigatedIds.has(alert.event_index);

                  let badgeColor = "bg-amber-950 text-amber-400 border-amber-800/40";
                  if (alert.risk_score >= 85) {
                    badgeColor = "bg-rose-950 text-rose-400 border-rose-800/40";
                  } else if (alert.risk_score >= 70) {
                    badgeColor = "bg-orange-950 text-orange-400 border-orange-800/40";
                  }

                  return (
                    <React.Fragment key={alert.event_index}>
                      <tr className="hover:bg-slate-800/30 transition-colors">
                        <td className="p-3 font-bold">
                          <span className={`px-2 py-0.5 rounded border text-[11px] ${badgeColor}`}>
                            {alert.risk_score}%
                          </span>
                        </td>
                        <td className="p-3 font-mono text-blue-400 font-semibold">{alert.entity_id}</td>
                        <td className="p-3 font-sans">
                          <span className="font-semibold text-slate-200">{alert.predicted_attack}</span>
                        </td>
                        <td className="p-3 text-slate-400 text-[11px]">{new Date(alert.timestamp).toLocaleTimeString()}</td>
                        <td className="p-3 text-emerald-400 font-bold">{alert.confidence}%</td>
                        <td className="p-3 text-right font-sans space-x-2">
                          <button
                            onClick={() => onSelectAnomalyForXAI(alert)}
                            className="bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 border border-blue-500/30 px-2.5 py-1 rounded text-[11px] font-bold uppercase transition-all"
                          >
                            XAI
                          </button>
                          {isMitigated ? (
                            <span className="inline-flex items-center gap-1 text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded text-[11px] border border-emerald-800/40 font-mono">
                              <CheckCircle className="w-3 h-3" /> Mitigated
                            </span>
                          ) : (
                            <button
                              onClick={() => handleMitigate(alert.event_index)}
                              className="bg-rose-950 hover:bg-rose-900 text-rose-300 border border-rose-800/40 px-2.5 py-1 rounded text-[11px] font-bold uppercase transition-all"
                            >
                              Mitigate
                            </button>
                          )}
                          <button
                            onClick={() => setExpandedId(isExpanded ? null : alert.event_index)}
                            className="p-1 text-slate-400 hover:text-white"
                          >
                            {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                          </button>
                        </td>
                      </tr>

                      {/* Accordion Row Details */}
                      {isExpanded && (
                        <tr className="bg-[#0D121C]">
                          <td colSpan={6} className="p-4 font-sans border-t border-slate-800">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                              <div className="bg-[#1F2937] p-3 rounded border border-slate-700">
                                <h4 className="font-bold text-blue-400 mb-2 uppercase text-[10px] tracking-wider">Key Risk Indicators:</h4>
                                <ul className="list-disc list-inside space-y-1 text-slate-300 leading-relaxed">
                                  {(alert.explanation?.reasons || ["Abnormal sequence threshold breach"]).map((r, i) => (
                                    <li key={i}>{r}</li>
                                  ))}
                                </ul>
                              </div>
                              <div className="bg-[#1F2937] p-3 rounded border border-slate-700">
                                <h4 className="font-bold text-emerald-400 mb-2 uppercase text-[10px] tracking-wider">Automated SOAR Playbook:</h4>
                                <ul className="list-disc list-inside space-y-1 text-slate-300 leading-relaxed">
                                  {(alert.explanation?.recommendations || ["Revoke active session tokens"]).map((rec, i) => (
                                    <li key={i}>{rec}</li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
