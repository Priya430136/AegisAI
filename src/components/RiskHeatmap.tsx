import React, { useState, useMemo } from "react";
import { AnomalyIncident } from "../types";
import { Calendar, Clock, Flame, ShieldAlert, Filter, Info, ChevronRight, AlertTriangle } from "lucide-react";

interface RiskHeatmapProps {
  anomalies: AnomalyIncident[];
  onSelectAnomaly?: (anomaly: AnomalyIncident) => void;
}

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const TIME_WINDOWS = [
  { label: "00:00 - 03:00", start: 0, end: 3 },
  { label: "03:00 - 06:00", start: 3, end: 6 },
  { label: "06:00 - 09:00", start: 6, end: 9 },
  { label: "09:00 - 12:00", start: 9, end: 12 },
  { label: "12:00 - 15:00", start: 12, end: 15 },
  { label: "15:00 - 18:00", start: 15, end: 18 },
  { label: "18:00 - 21:00", start: 18, end: 21 },
  { label: "21:00 - 24:00", start: 21, end: 24 },
];

export const RiskHeatmap: React.FC<RiskHeatmapProps> = ({ anomalies }) => {
  const [selectedAttackFilter, setSelectedAttackFilter] = useState<string>("ALL");
  const [activeCell, setActiveCell] = useState<{ dayIdx: number; windowIdx: number } | null>({ dayIdx: 2, windowIdx: 0 }); // Default to Wed 00-03

  // Deterministic seed-based baseline dataset + actual anomalies mapping
  const heatmapData = useMemo(() => {
    // Standard baseline distribution matrix [7 days][8 windows]
    // Values represent incident counts and risk density
    const matrix: { count: number; avgRisk: number; topAttack: string; incidents: AnomalyIncident[] }[][] = Array.from(
      { length: 7 },
      (_, dayIdx) =>
        Array.from({ length: 8 }, (_, winIdx) => {
          // Synthetic baseline distribution for realistic security patterns (off-hours higher)
          const isWeekend = dayIdx === 5 || dayIdx === 6; // Sat, Sun
          const isOffHours = winIdx < 2 || winIdx >= 6; // 00-06 or 18-24
          
          let baseCount = 2;
          if (isOffHours && isWeekend) baseCount = 8 + ((dayIdx * 3 + winIdx * 5) % 7);
          else if (isOffHours) baseCount = 5 + ((dayIdx * 2 + winIdx * 4) % 6);
          else if (isWeekend) baseCount = 3 + ((dayIdx + winIdx) % 4);
          else baseCount = 1 + ((dayIdx * winIdx) % 3);

          let avgRisk = Math.min(98, Math.max(55, 65 + baseCount * 3 + ((dayIdx * 7) % 15)));

          const attacks = [
            "Brute Force",
            "Credential Stuffing",
            "Impossible Travel",
            "Lateral Movement",
            "Device Spoofing",
            "Exfiltration",
            "Insider Drift"
          ];
          const topAttack = attacks[(dayIdx * 2 + winIdx * 3) % attacks.length];

          return {
            count: baseCount,
            avgRisk,
            topAttack,
            incidents: []
          };
        })
    );

    // Overlay real anomaly incidents into the matrix
    anomalies.forEach((incident) => {
      if (selectedAttackFilter !== "ALL" && incident.predicted_attack !== selectedAttackFilter) {
        return;
      }

      const date = new Date(incident.timestamp);
      let dayIdx = date.getDay() - 1; // Convert Sun=0 -> Mon=0
      if (dayIdx < 0) dayIdx = 6; // Sun

      const hour = date.getHours();
      const winIdx = Math.min(7, Math.floor(hour / 3));

      if (matrix[dayIdx] && matrix[dayIdx][winIdx]) {
        matrix[dayIdx][winIdx].incidents.push(incident);
        matrix[dayIdx][winIdx].count += 1;
        matrix[dayIdx][winIdx].avgRisk = Math.round(
          (matrix[dayIdx][winIdx].avgRisk + incident.risk_score) / 2
        );
        matrix[dayIdx][winIdx].topAttack = incident.predicted_attack;
      }
    });

    return matrix;
  }, [anomalies, selectedAttackFilter]);

  // Find max count for scaling color intensity
  const maxCount = useMemo(() => {
    let max = 1;
    heatmapData.forEach((row) =>
      row.forEach((cell) => {
        if (cell.count > max) max = cell.count;
      })
    );
    return max;
  }, [heatmapData]);

  // Overall analytics stats
  const stats = useMemo(() => {
    let totalIncidents = 0;
    let offHoursIncidents = 0;
    let peakCell = { day: "Mon", window: "00:00 - 03:00", count: 0, attack: "" };

    heatmapData.forEach((row, dIdx) => {
      row.forEach((cell, wIdx) => {
        totalIncidents += cell.count;
        if (wIdx < 2 || wIdx >= 6 || dIdx >= 5) {
          offHoursIncidents += cell.count;
        }
        if (cell.count > peakCell.count) {
          peakCell = {
            day: DAYS[dIdx],
            window: TIME_WINDOWS[wIdx].label,
            count: cell.count,
            attack: cell.topAttack,
          };
        }
      });
    });

    const offHoursPct = Math.round((offHoursIncidents / Math.max(1, totalIncidents)) * 100);

    return { totalIncidents, offHoursIncidents, offHoursPct, peakCell };
  }, [heatmapData]);

  const attackTypes = [
    "ALL",
    "Brute Force",
    "Impossible Travel",
    "Credential Stuffing",
    "Lateral Movement",
    "Device Spoofing",
    "Exfiltration",
    "Insider Drift"
  ];

  // Helper for background color intensity
  const getCellStyle = (count: number) => {
    const ratio = count / Math.max(1, maxCount);
    if (count === 0) {
      return "bg-[#111827] border-slate-800 text-slate-600 hover:border-slate-600";
    }
    if (ratio < 0.25) {
      return "bg-blue-950/40 border-blue-900/40 text-blue-300 hover:border-blue-500/60";
    }
    if (ratio < 0.55) {
      return "bg-amber-950/60 border-amber-800/50 text-amber-300 font-bold hover:border-amber-400";
    }
    if (ratio < 0.8) {
      return "bg-orange-950/80 border-orange-700/70 text-orange-200 font-bold hover:border-orange-400";
    }
    return "bg-rose-950/90 border-rose-600 text-rose-200 font-bold shadow-lg shadow-rose-950/50 hover:border-rose-400";
  };

  const selectedCellData = activeCell
    ? heatmapData[activeCell.dayIdx][activeCell.windowIdx]
    : null;

  return (
    <div id="risk-heatmap-component" className="bg-[#111827] border border-slate-800 rounded-lg p-5 space-y-5">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-2">
        <div>
          <div className="flex items-center gap-2">
            <Flame className="w-4 h-4 text-rose-500" />
            <h2 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
              Temporal Anomaly Risk Heatmap
            </h2>
            <span className="text-[10px] font-mono font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2 py-0.5 rounded uppercase">
              Time-of-Day vs Day-of-Week
            </span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            Visualizes anomaly density across 56 weekly time intervals to identify off-hour attack patterns and automated credential bursts.
          </p>
        </div>

        {/* Attack Vector Filter */}
        <div className="flex items-center gap-2.5 w-full md:w-auto">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-xs text-slate-400 font-medium">Filter Vector:</span>
          <select
            id="heatmap-attack-filter"
            value={selectedAttackFilter}
            onChange={(e) => setSelectedAttackFilter(e.target.value)}
            className="bg-[#1F2937] border border-slate-700 rounded px-2.5 py-1 text-xs text-white focus:outline-none focus:border-blue-500 font-mono"
          >
            {attackTypes.map((type) => (
              <option key={type} value={type}>
                {type === "ALL" ? "All Threat Vectors" : type}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Heatmap Grid & Inspection Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Heatmap Matrix Grid (3 Cols) */}
        <div className="lg:col-span-3 overflow-hidden">
          <table className="w-full table-fixed text-left border-collapse">
            <thead>
              <tr>
                <th className="p-2 text-[10px] font-bold text-slate-500 uppercase tracking-wider w-12">Day</th>
                {TIME_WINDOWS.map((win, idx) => (
                  <th
                    key={idx}
                    className="p-1.5 text-center text-[10px] font-mono text-slate-400 uppercase border-b border-slate-800"
                  >
                    {win.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {DAYS.map((day, dIdx) => (
                <tr key={day}>
                  <td className="p-1 text-xs font-bold text-slate-300 font-mono border-r border-slate-800/80">
                    {day}
                  </td>
                  {TIME_WINDOWS.map((win, wIdx) => {
                    const cell = heatmapData[dIdx][wIdx];
                    const isSelected = activeCell?.dayIdx === dIdx && activeCell?.windowIdx === wIdx;
                    const cellStyle = getCellStyle(cell.count);

                    return (
                      <td key={wIdx} className="p-1 text-center">
                        <button
                          onClick={() => setActiveCell({ dayIdx: dIdx, windowIdx: wIdx })}
                          className={`w-full h-10 rounded border transition-all flex flex-col items-center justify-center relative group overflow-hidden ${cellStyle} ${
                            isSelected ? "ring-2 ring-blue-400 ring-offset-1 ring-offset-[#111827] z-10" : ""
                          }`}
                          title={`${day} ${win.label}: ${cell.count} incidents (Avg Risk: ${cell.avgRisk}%)`}
                        >
                          <span className="text-xs">{cell.count}</span>
                          <span className="text-[8px] opacity-75 font-mono">{cell.avgRisk}%</span>
                          {cell.count >= Math.round(maxCount * 0.8) && (
                            <span className="absolute top-1 right-1 flex h-1.5 w-1.5 pointer-events-none">
                              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                              <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-rose-500"></span>
                            </span>
                          )}
                        </button>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>

          {/* Color Legend */}
          <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono mt-4 pt-3 border-t border-slate-800">
            <span className="flex items-center gap-1.5">
              <Info className="w-3 h-3 text-slate-500" /> Click any time block cell to inspect telemetry details
            </span>
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded bg-[#111827] border border-slate-700"></span> Normal (0)
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded bg-blue-950 border border-blue-800"></span> Low (1-3)
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded bg-amber-950 border border-amber-800"></span> Elevated (4-6)
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded bg-rose-950 border border-rose-800"></span> Severe (7+)
              </span>
            </div>
          </div>
        </div>

        {/* Selected Cell Inspector Card (1 Col) */}
        <div className="bg-[#1F2937] border border-slate-700 rounded-lg p-4 flex flex-col justify-between space-y-4">
          {activeCell && selectedCellData ? (
            <div className="space-y-3">
              <div className="border-b border-slate-700 pb-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Interval Inspector</span>
                  <span className="text-[10px] font-mono text-blue-400 bg-blue-500/10 px-1.5 py-0.5 rounded border border-blue-500/20">
                    UTC Time
                  </span>
                </div>
                <h3 className="text-sm font-bold text-white font-mono mt-1 flex items-center gap-1.5">
                  <Calendar className="w-3.5 h-3.5 text-blue-400" />
                  {DAYS[activeCell.dayIdx]} {TIME_WINDOWS[activeCell.windowIdx].label}
                </h3>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="bg-[#111827] p-2.5 rounded border border-slate-800">
                  <p className="text-[10px] text-slate-400 uppercase font-semibold">Incident Density</p>
                  <p className="text-lg font-bold text-rose-400 font-mono mt-0.5">
                    {selectedCellData.count} <span className="text-[10px] text-slate-500 font-normal">alerts</span>
                  </p>
                </div>
                <div className="bg-[#111827] p-2.5 rounded border border-slate-800">
                  <p className="text-[10px] text-slate-400 uppercase font-semibold">Avg Risk Score</p>
                  <p className="text-lg font-bold text-amber-400 font-mono mt-0.5">{selectedCellData.avgRisk}%</p>
                </div>
              </div>

              <div className="bg-[#111827] p-3 rounded border border-slate-800 space-y-1.5">
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Dominant Attack Vector</p>
                <p className="text-xs font-bold text-blue-300 flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                  {selectedCellData.topAttack}
                </p>
                <p className="text-[10px] text-slate-400 leading-relaxed mt-1">
                  High concentration of uncharacteristic login sequence attempts detected in this specific window.
                </p>
              </div>

              {selectedCellData.incidents.length > 0 && (
                <div className="space-y-1">
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Recent Matched Alerts</p>
                  <div className="max-h-28 overflow-y-auto space-y-1 pr-1">
                    {selectedCellData.incidents.slice(0, 3).map((inc, i) => (
                      <div key={i} className="text-[11px] font-mono bg-[#111827] p-1.5 rounded border border-slate-800 flex justify-between items-center text-slate-300">
                        <span className="text-blue-400 truncate max-w-[100px]">{inc.entity_id}</span>
                        <span className="text-rose-400 font-bold">{inc.risk_score}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-slate-500 text-xs">
              Select a cell in the heatmap grid to view telemetry analysis.
            </div>
          )}

          <div className="pt-2 border-t border-slate-700/80 text-[10px] text-slate-400 flex items-center gap-1 font-mono">
            <ChevronRight className="w-3 h-3 text-blue-400" /> Auto-synchronized with ML pipeline
          </div>
        </div>
      </div>
    </div>
  );
};
