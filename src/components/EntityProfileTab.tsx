import React, { useState } from "react";
import { EntityProfile } from "../types";
import { UserCheck, Clock, Laptop, ShieldCheck, MapPin, Activity, AlertCircle } from "lucide-react";

interface EntityProfileTabProps {
  entities: Record<string, EntityProfile>;
}

export const EntityProfileTab: React.FC<EntityProfileTabProps> = ({ entities }) => {
  const entityList = Object.keys(entities);
  const [selectedEntityId, setSelectedEntityId] = useState<string>(entityList[0] || "USR-1001");

  const profile = entities[selectedEntityId] || {
    entity_id: selectedEntityId,
    entity_type: "user",
    home_geo: { city: "New York", country: "USA", lat: 40.7128, lon: -74.006, ip_prefix: "198.51.100." },
    normal_start_hour: 8,
    normal_end_hour: 18,
    preferred_device: "fp_894201",
    preferred_auth: "MFA_TOTP",
    common_resources: ["/api/v1/dashboard", "/app/index.html", "/auth/login"],
    avg_session_duration: 1800,
    is_vip_privilege: false,
  };

  return (
    <div id="entity-profile-tab" className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-[#111827] border border-slate-800 p-4 rounded-lg">
        <div>
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wide flex items-center gap-2">
            <UserCheck className="w-4 h-4 text-blue-400" /> Entity Behavioral Profiles & Baseline Registry
          </h2>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Inspect individual baseline profiles, normal access hours, preferred devices, and historical telemetry.
          </p>
        </div>

        {/* Entity Selector */}
        <div className="flex items-center gap-3">
          <label className="text-xs font-medium text-slate-400">Select Entity:</label>
          <select
            id="entity-selector-dropdown"
            value={selectedEntityId}
            onChange={(e) => setSelectedEntityId(e.target.value)}
            className="bg-[#1F2937] border border-slate-700 rounded px-3 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500 font-mono"
          >
            {entityList.slice(0, 50).map((id) => (
              <option key={id} value={id}>
                {id} ({entities[id]?.entity_type || "user"})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Profile Details Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1: Core Behavioral Attributes */}
        <div className="bg-[#111827] border border-slate-800 rounded-lg p-5 space-y-4">
          <div className="flex justify-between items-center border-b border-slate-800 pb-3">
            <div>
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Entity Identifier</span>
              <h3 className="text-lg font-bold text-blue-400 font-mono">{profile.entity_id}</h3>
            </div>
            <span
              className={`px-2.5 py-0.5 rounded text-[10px] font-mono font-bold uppercase border ${
                profile.is_vip_privilege
                  ? "bg-amber-950 text-amber-400 border-amber-800/40"
                  : "bg-blue-600/10 text-blue-400 border-blue-500/30"
              }`}
            >
              {profile.is_vip_privilege ? "VIP / Restricted" : "Standard Profile"}
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-400 flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-blue-400" /> Normal Hours:
              </span>
              <span className="font-semibold text-slate-200 font-mono">
                {profile.normal_start_hour}:00 - {profile.normal_end_hour}:00 UTC
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-400 flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-emerald-400" /> Home Location:
              </span>
              <span className="font-semibold text-slate-200">
                {profile.home_geo?.city || "New York"}, {profile.home_geo?.country || "USA"}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-400 flex items-center gap-1.5">
                <Laptop className="w-3.5 h-3.5 text-purple-400" /> Preferred Device:
              </span>
              <span className="font-mono text-slate-300 font-semibold">{profile.preferred_device}</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-400 flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-amber-400" /> Preferred Auth Method:
              </span>
              <span className="font-semibold text-blue-400 font-mono">{profile.preferred_auth}</span>
            </div>
          </div>
        </div>

        {/* Card 2: Frequently Accessed Resources */}
        <div className="bg-[#111827] border border-slate-800 rounded-lg p-5 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2 mb-3">
              <Activity className="w-3.5 h-3.5 text-emerald-400" /> Common Resources Baseline
            </h3>
            <div className="space-y-2">
              {profile.common_resources.map((res, i) => (
                <div key={i} className="bg-[#1F2937] border border-slate-700/80 p-2 rounded text-[11px] font-mono text-blue-300">
                  {res}
                </div>
              ))}
            </div>
          </div>
          <div className="text-xs text-slate-400 pt-3 border-t border-slate-800 mt-4">
            Average Session Duration: <span className="text-white font-semibold font-mono">{Math.round(profile.avg_session_duration / 60)} minutes</span>
          </div>
        </div>

        {/* Card 3: Adaptive Machine Learning Status */}
        <div className="bg-[#111827] border border-slate-800 rounded-lg p-5 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2 mb-3">
              <AlertCircle className="w-3.5 h-3.5 text-amber-500" /> Cold Start & Concept Drift Status
            </h3>
            <div className="space-y-3 text-xs">
              <div className="p-3 bg-[#1F2937] rounded border border-slate-700">
                <div className="font-semibold text-slate-200">Cold Start Warmup</div>
                <p className="text-slate-400 mt-0.5 text-[11px]">Entity has 50+ event log history. Profile fully warm.</p>
                <div className="w-full bg-slate-800 rounded-full h-1.5 mt-2 overflow-hidden">
                  <div className="bg-emerald-500 h-1.5 rounded-full w-full"></div>
                </div>
              </div>

              <div className="p-3 bg-[#1F2937] rounded border border-slate-700 space-y-1.5">
                <div className="flex justify-between items-center">
                  <div className="font-semibold text-slate-200">Concept Drift Tracker</div>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase border ${
                      profile.drift_profile?.drift_detected
                        ? "bg-amber-950 text-amber-400 border-amber-800/40"
                        : "bg-emerald-950 text-emerald-400 border-emerald-800/40"
                    }`}
                  >
                    {profile.drift_profile?.drift_detected ? `${profile.drift_profile.drift_type} drift` : "Stable Baseline"}
                  </span>
                </div>
                <p className="text-slate-400 text-[11px]">
                  ADWIN Window: <span className="text-white font-mono">{profile.drift_profile?.adaptive_window_size || 50} events</span> | Adaptive Threshold: <span className="text-amber-400 font-mono">{profile.drift_profile?.adaptive_threshold?.toFixed(2) || "0.35"}</span>
                </p>
                {profile.drift_profile?.drift_confidence ? (
                  <div className="text-[10px] text-purple-400 font-mono">
                    Drift Confidence: {(profile.drift_profile.drift_confidence * 100).toFixed(1)}% ({profile.drift_profile.drift_count} adaptations)
                  </div>
                ) : null}
              </div>
            </div>
          </div>
          <div className="text-[11px] text-emerald-400 font-semibold flex items-center gap-1.5 pt-3 uppercase tracking-wider font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Profile Active & Monitored
          </div>
        </div>
      </div>
    </div>
  );
};
