import React, { useState, useEffect } from "react";
import { Navbar } from "./components/Navbar";
import { OverviewTab } from "./components/OverviewTab";
import { LiveAlertsTab } from "./components/LiveAlertsTab";
import { EntityProfileTab } from "./components/EntityProfileTab";
import { ExplainabilityTab } from "./components/ExplainabilityTab";
import { AnalyticsTab } from "./components/AnalyticsTab";
import { SettingsTab } from "./components/SettingsTab";
import { Metrics, AnomalyIncident, EntityProfile } from "./types";

export default function App() {
  const [activeTab, setActiveTab] = useState("overview");
  const [metrics, setMetrics] = useState<Metrics>({
    dataset_size: 50000,
    total_anomalies_detected: 1000,
    accuracy: 0.9829,
    precision: 0.962,
    recall: 0.918,
    f1_score: 0.939,
    roc_auc: 0.982,
    false_positive_rate: 0.0035,
    confusion_matrix: {
      true_positives: 918,
      false_positives: 36,
      true_negatives: 48964,
      false_negatives: 82,
    },
    attack_distribution: {
      "Brute Force": 210,
      "Impossible Travel": 185,
      "Credential Stuffing": 150,
      "Lateral Movement": 145,
      "Device Spoofing": 120,
      "Low and Slow Exfiltration": 95,
      "Insider Drift": 95,
    },
  });

  const [anomalies, setAnomalies] = useState<AnomalyIncident[]>([]);
  const [entities, setEntities] = useState<Record<string, EntityProfile>>({});
  const [selectedAnomalyForXAI, setSelectedAnomalyForXAI] = useState<AnomalyIncident | null>(null);

  const fetchData = async () => {
    try {
      const [resMetrics, resAnomalies, resEntities] = await Promise.all([
        fetch("/api/metrics"),
        fetch("/api/anomalies"),
        fetch("/api/entities"),
      ]);

      if (resMetrics.ok) {
        const mData = await resMetrics.json();
        setMetrics(mData);
      }
      if (resAnomalies.ok) {
        const aData = await resAnomalies.json();
        if (Array.isArray(aData) && aData.length > 0) {
          setAnomalies(aData);
        }
      }
      if (resEntities.ok) {
        const eData = await resEntities.json();
        setEntities(eData);
      }
    } catch (err) {
      console.error("Error fetching system metrics/anomalies:", err);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSelectAnomalyForXAI = (anomaly: AnomalyIncident) => {
    setSelectedAnomalyForXAI(anomaly);
    setActiveTab("explain");
  };

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-300 font-sans selection:bg-blue-600 selection:text-white">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} alertCount={anomalies.length} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === "overview" && (
          <OverviewTab
            metrics={metrics}
            anomalies={anomalies}
            onNavigateToAlerts={() => setActiveTab("alerts")}
          />
        )}

        {activeTab === "alerts" && (
          <LiveAlertsTab
            anomalies={anomalies}
            onSelectAnomalyForXAI={handleSelectAnomalyForXAI}
          />
        )}

        {activeTab === "entity" && <EntityProfileTab entities={entities} />}

        {activeTab === "explain" && (
          <ExplainabilityTab anomalies={anomalies} selectedAnomaly={selectedAnomalyForXAI} />
        )}

        {activeTab === "analytics" && <AnalyticsTab metrics={metrics} />}

        {activeTab === "settings" && <SettingsTab onRefreshData={fetchData} />}
      </main>
    </div>
  );
}
