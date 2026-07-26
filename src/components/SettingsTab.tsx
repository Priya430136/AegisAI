import React, { useState, useEffect } from "react";
import { Settings, RefreshCw, Download, Sliders, CheckCircle, RotateCcw } from "lucide-react";

interface SettingsTabProps {
  onRefreshData: () => void;
}

export const SettingsTab: React.FC<SettingsTabProps> = ({ onRefreshData }) => {
  const [anomalyThreshold, setAnomalyThreshold] = useState(60);
  const [sensitivity, setSensitivity] = useState(60);
  const [classificationThreshold, setClassificationThreshold] = useState(50);
  const [learningRate, setLearningRate] = useState(0.001);
  const [sequenceLength, setSequenceLength] = useState(5);
  const [windowSize, setWindowSize] = useState(5);
  const [epochs, setEpochs] = useState(20);
  const [batchSize, setBatchSize] = useState(64);
  const [randomSeed, setRandomSeed] = useState(42);
  const [driftRate, setDriftRate] = useState(20);
  const [coldStartWarmup, setColdStartWarmup] = useState(20);

  const [isRetraining, setIsRetraining] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/config")
      .then((res) => res.json())
      .then((cfg) => {
        if (cfg) {
          if (cfg.anomaly_threshold !== undefined) setAnomalyThreshold(cfg.anomaly_threshold);
          if (cfg.detection_sensitivity !== undefined) setSensitivity(cfg.detection_sensitivity);
          if (cfg.classification_threshold !== undefined) setClassificationThreshold(cfg.classification_threshold);
          if (cfg.learning_rate !== undefined) setLearningRate(cfg.learning_rate);
          if (cfg.sequence_length !== undefined) setSequenceLength(cfg.sequence_length);
          if (cfg.window_size !== undefined) setWindowSize(cfg.window_size);
          if (cfg.epochs !== undefined) setEpochs(cfg.epochs);
          if (cfg.batch_size !== undefined) setBatchSize(cfg.batch_size);
          if (cfg.random_seed !== undefined) setRandomSeed(cfg.random_seed);
          if (cfg.drift_rate !== undefined) setDriftRate(cfg.drift_rate);
          if (cfg.cold_start_warmup !== undefined) setColdStartWarmup(cfg.cold_start_warmup);
        }
      })
      .catch(() => {});
  }, []);

  const getCurrentConfig = () => ({
    anomaly_threshold: anomalyThreshold,
    detection_sensitivity: sensitivity,
    classification_threshold: classificationThreshold,
    learning_rate: learningRate,
    sequence_length: sequenceLength,
    window_size: windowSize,
    epochs: epochs,
    batch_size: batchSize,
    random_seed: randomSeed,
    drift_rate: driftRate,
    cold_start_warmup: coldStartWarmup,
  });

  const handleRetrainPipeline = async () => {
    setIsRetraining(true);
    setStatusMessage("Executing full Python model retraining pipeline (main.py)...");
    try {
      const res = await fetch("/api/run-pipeline", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(getCurrentConfig()),
      });
      const data = await res.json();
      if (data.success) {
        setStatusMessage("Pipeline executed successfully! Dataset re-processed and models updated.");
        onRefreshData();
      } else {
        setStatusMessage(`Pipeline error: ${data.error}`);
      }
    } catch (err: any) {
      setStatusMessage("Failed to connect to pipeline runner API.");
    } finally {
      setIsRetraining(false);
    }
  };

  const handleResetSettings = async () => {
    setIsRetraining(true);
    setStatusMessage("Resetting configuration to defaults and retraining pipeline...");
    try {
      const res = await fetch("/api/reset-settings", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        const def = data.config || {
          anomaly_threshold: 60,
          detection_sensitivity: 60,
          classification_threshold: 50,
          learning_rate: 0.001,
          sequence_length: 5,
          window_size: 5,
          epochs: 20,
          batch_size: 64,
          random_seed: 42,
          drift_rate: 20,
          cold_start_warmup: 20,
        };
        setAnomalyThreshold(def.anomaly_threshold);
        setSensitivity(def.detection_sensitivity);
        setClassificationThreshold(def.classification_threshold);
        setLearningRate(def.learning_rate);
        setSequenceLength(def.sequence_length);
        setWindowSize(def.window_size);
        setEpochs(def.epochs);
        setBatchSize(def.batch_size);
        setRandomSeed(def.random_seed);
        setDriftRate(def.drift_rate);
        setColdStartWarmup(def.cold_start_warmup);

        setStatusMessage("Settings restored to defaults and model retrained successfully!");
        onRefreshData();
      } else {
        setStatusMessage(`Reset error: ${data.error}`);
      }
    } catch (err) {
      setStatusMessage("Failed to reset model settings.");
    } finally {
      setIsRetraining(false);
    }
  };

  const handleExportReport = async () => {
    try {
      const res = await fetch("/api/report");
      const data = await res.json();
      const blob = new Blob([data.report || "Report placeholder"], { type: "text/markdown" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "AegisAI_Anomaly_Detection_Report.md";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (err) {
      alert("Failed to download executive report.");
    }
  };

  return (
    <div id="settings-tab" className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-[#111827] border border-slate-800 p-4 rounded-lg">
        <div>
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wide flex items-center gap-2">
            <Settings className="w-4 h-4 text-blue-400" /> System Controls & Model Settings
          </h2>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Tune detection thresholds, trigger incremental retraining, and export executive SOC reports.
          </p>
        </div>

        <button
          onClick={handleExportReport}
          id="export-report-btn"
          className="flex items-center space-x-2 bg-emerald-950 hover:bg-emerald-900 text-emerald-400 font-mono font-bold px-3 py-1.5 rounded text-xs border border-emerald-800/40 transition-all uppercase"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Export Executive Report (.MD)</span>
        </button>
      </div>

      {statusMessage && (
        <div className="p-3 bg-blue-950/60 border border-blue-800/40 rounded text-xs text-blue-200 font-mono flex items-center gap-2">
          {isRetraining ? <RefreshCw className="w-4 h-4 text-amber-400 animate-spin" /> : <CheckCircle className="w-4 h-4 text-emerald-400" />}
          <span>{statusMessage}</span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Model Threshold Tuning */}
        <div className="bg-[#111827] border border-slate-800 rounded-lg p-5 space-y-4">
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2 border-b border-slate-800 pb-3">
            <Sliders className="w-4 h-4 text-blue-400" /> Detection Sensitivity & Hyperparameters
          </h3>

          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-medium">
              <label className="text-slate-300">Anomaly Risk Threshold</label>
              <span className="text-blue-400 font-mono font-bold">{anomalyThreshold}%</span>
            </div>
            <input
              type="range"
              min="10"
              max="90"
              value={anomalyThreshold}
              onChange={(e) => setAnomalyThreshold(Number(e.target.value))}
              className="w-full accent-blue-500 bg-slate-800 rounded h-1.5"
            />
            <p className="text-[10px] text-slate-500">Events with risk score above threshold trigger alerts.</p>
          </div>

          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-medium">
              <label className="text-slate-300">Detection Sensitivity</label>
              <span className="text-blue-400 font-mono font-bold">{sensitivity}%</span>
            </div>
            <input
              type="range"
              min="10"
              max="90"
              value={sensitivity}
              onChange={(e) => setSensitivity(Number(e.target.value))}
              className="w-full accent-blue-500 bg-slate-800 rounded h-1.5"
            />
          </div>

          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-medium">
              <label className="text-slate-300">Classification Threshold</label>
              <span className="text-indigo-400 font-mono font-bold">{classificationThreshold}%</span>
            </div>
            <input
              type="range"
              min="10"
              max="90"
              value={classificationThreshold}
              onChange={(e) => setClassificationThreshold(Number(e.target.value))}
              className="w-full accent-indigo-500 bg-slate-800 rounded h-1.5"
            />
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2 border-t border-slate-800/80">
            <div>
              <label className="block text-[11px] font-medium text-slate-300 mb-1">Learning Rate</label>
              <select
                value={learningRate}
                onChange={(e) => setLearningRate(Number(e.target.value))}
                className="w-full bg-[#1F2937] border border-slate-700 rounded px-2.5 py-1 text-xs text-white font-mono"
              >
                <option value={0.0001}>0.0001</option>
                <option value={0.0005}>0.0005</option>
                <option value={0.001}>0.001 (Default)</option>
                <option value={0.005}>0.005</option>
                <option value={0.01}>0.01</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-medium text-slate-300 mb-1">Batch Size</label>
              <select
                value={batchSize}
                onChange={(e) => setBatchSize(Number(e.target.value))}
                className="w-full bg-[#1F2937] border border-slate-700 rounded px-2.5 py-1 text-xs text-white font-mono"
              >
                <option value={16}>16</option>
                <option value={32}>32</option>
                <option value={64}>64 (Default)</option>
                <option value={128}>128</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3 pt-2">
            <div>
              <label className="block text-[10px] font-medium text-slate-400 mb-1">Seq Length</label>
              <input
                type="number"
                min="2"
                max="20"
                value={sequenceLength}
                onChange={(e) => setSequenceLength(Number(e.target.value))}
                className="w-full bg-[#1F2937] border border-slate-700 rounded px-2 py-1 text-xs text-white font-mono"
              />
            </div>
            <div>
              <label className="block text-[10px] font-medium text-slate-400 mb-1">Window Size</label>
              <input
                type="number"
                min="2"
                max="20"
                value={windowSize}
                onChange={(e) => setWindowSize(Number(e.target.value))}
                className="w-full bg-[#1F2937] border border-slate-700 rounded px-2 py-1 text-xs text-white font-mono"
              />
            </div>
            <div>
              <label className="block text-[10px] font-medium text-slate-400 mb-1">Epochs</label>
              <input
                type="number"
                min="5"
                max="50"
                value={epochs}
                onChange={(e) => setEpochs(Number(e.target.value))}
                className="w-full bg-[#1F2937] border border-slate-700 rounded px-2 py-1 text-xs text-white font-mono"
              />
            </div>
          </div>

          <div className="pt-2">
            <label className="block text-[10px] font-medium text-slate-400 mb-1">Random Seed (Data Generator & Model Weighting)</label>
            <input
              type="number"
              value={randomSeed}
              onChange={(e) => setRandomSeed(Number(e.target.value))}
              className="w-full bg-[#1F2937] border border-slate-700 rounded px-2.5 py-1 text-xs text-white font-mono"
            />
          </div>

          <div className="space-y-1.5 pt-2 border-t border-slate-800/80">
            <div className="flex justify-between text-xs font-medium">
              <label className="text-slate-300">Concept Drift Sensitivity (ADWIN)</label>
              <span className="text-amber-400 font-mono font-bold">{driftRate}%</span>
            </div>
            <input
              type="range"
              min="5"
              max="50"
              value={driftRate}
              onChange={(e) => setDriftRate(Number(e.target.value))}
              className="w-full accent-amber-500 bg-slate-800 rounded h-1.5"
            />
          </div>

          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-medium">
              <label className="text-slate-300">Cold Start Warmup Events</label>
              <span className="text-emerald-400 font-mono font-bold">{coldStartWarmup} logs</span>
            </div>
            <input
              type="range"
              min="5"
              max="50"
              value={coldStartWarmup}
              onChange={(e) => setColdStartWarmup(Number(e.target.value))}
              className="w-full accent-emerald-500 bg-slate-800 rounded h-1.5"
            />
          </div>
        </div>

        {/* Pipeline Control & Operations */}
        <div className="bg-[#111827] border border-slate-800 rounded-lg p-5 flex flex-col justify-between space-y-6">
          <div>
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2 border-b border-slate-800 pb-3 mb-4">
              <RefreshCw className="w-4 h-4 text-emerald-400" /> Pipeline Retraining & Synchronization
            </h3>
            <p className="text-xs text-slate-300 mb-4 leading-relaxed">
              Triggers the backend Python orchestration pipeline (`main.py`). Regenerates or re-evaluates synthetic access log events using the active hyperparameters, updates baseline statistics and GRU sequence scores, recalculates accuracy, precision, recall, and ROC AUC, and broadcasts refreshed state to all dashboard components.
            </p>
            <div className="bg-[#1F2937] p-3 rounded border border-slate-700/80 text-xs font-mono text-slate-300 space-y-1">
              <div>$ python3 main.py --config config.json</div>
              <div className="text-slate-400">Updates: metrics.json, detected_anomalies.json, entity_profiles.json</div>
            </div>
          </div>

          <div className="space-y-3">
            <button
              onClick={handleRetrainPipeline}
              disabled={isRetraining}
              id="retrain-model-btn"
              className={`w-full py-2.5 rounded font-mono font-bold text-xs uppercase flex items-center justify-center gap-2 border transition-all ${
                isRetraining
                  ? "bg-slate-800 text-slate-500 border-slate-700 cursor-not-allowed"
                  : "bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 border-blue-500/30"
              }`}
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRetraining ? "animate-spin text-amber-400" : ""}`} />
              <span>{isRetraining ? "Retraining Models..." : "Retrain Model"}</span>
            </button>

            <button
              onClick={handleResetSettings}
              disabled={isRetraining}
              id="reset-settings-btn"
              className={`w-full py-2 rounded font-mono font-bold text-xs uppercase flex items-center justify-center gap-2 border transition-all ${
                isRetraining
                  ? "bg-slate-800 text-slate-500 border-slate-700 cursor-not-allowed"
                  : "bg-rose-950/40 hover:bg-rose-900/50 text-rose-300 border-rose-800/40"
              }`}
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Settings</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
