import React from "react";
import { Shield, AlertTriangle, UserCheck, BarChart2, Settings, Terminal, Activity } from "lucide-react";

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  alertCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, alertCount }) => {
  const navItems = [
    { id: "overview", label: "Dashboard", icon: Shield },
    { id: "alerts", label: "Live Alerts", icon: AlertTriangle, badge: alertCount },
    { id: "entity", label: "Entity Explorer", icon: UserCheck },
    { id: "explain", label: "XAI Explainability", icon: Terminal },
    { id: "analytics", label: "Analytics & Benchmarks", icon: BarChart2 },
    { id: "settings", label: "Model Settings", icon: Settings },
  ];

  return (
    <header id="main-header" className="bg-[#111827] border-b border-slate-800 sticky top-0 z-50 text-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-2 shrink-0">
            <div className="w-7 h-7 bg-blue-600 rounded flex items-center justify-center text-white font-bold text-sm shadow-md shadow-blue-600/30 font-mono">
              Σ
            </div>
            <div>
              <div className="font-extrabold text-xs tracking-wider text-white uppercase flex items-center gap-1.5">
                <span>AegisAI</span>
                <span className="text-[9px] text-blue-400 font-mono font-bold bg-blue-500/10 px-1.5 py-0.2 rounded border border-blue-500/20 shrink-0">v2.4</span>
              </div>
              <p className="text-[9px] text-slate-400 uppercase tracking-widest font-semibold leading-none mt-0.5">Behavioral Anomaly Engine</p>
            </div>
          </div>

          {/* Navigation Items */}
          <nav id="navbar-links" className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  id={`nav-btn-${item.id}`}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-1.5 px-2.5 py-1.5 rounded text-[11px] font-semibold uppercase tracking-wider transition-all whitespace-nowrap ${
                    isActive
                      ? "bg-blue-600/10 text-blue-400 border-l-2 border-blue-500 bg-slate-800/60"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{item.label}</span>
                  {item.badge !== undefined && item.badge > 0 && (
                    <span className="ml-1 bg-rose-500 text-white text-[10px] font-mono font-bold px-1.5 py-0.2 rounded-full">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* System Status Ticker */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center gap-2 text-[10px] font-mono">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="text-slate-400 uppercase tracking-widest hidden sm:inline">Stream Active</span>
            </div>
            <div className="h-6 w-px bg-slate-800 hidden sm:block"></div>
            <div className="text-right">
              <p className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">Threat Level</p>
              <p className="text-xs font-bold text-amber-500 uppercase tracking-wider">Elevated</p>
            </div>
          </div>
        </div>

        {/* Mobile Nav Bar */}
        <div className="flex md:hidden overflow-x-auto py-2 border-t border-slate-800 gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`whitespace-nowrap flex items-center space-x-1.5 px-2.5 py-1 rounded text-[11px] font-semibold uppercase ${
                  isActive
                    ? "bg-blue-600/20 text-blue-400 border border-blue-500/30"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <Icon className="w-3 h-3" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
