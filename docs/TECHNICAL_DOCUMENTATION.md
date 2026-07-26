# AegisAI - Technical Developer Documentation

## 1. Directory & File Structure Guide

```
AegisAI/
├── main.py                          # End-to-end pipeline runner & evaluation entry point
├── server.ts                        # Express server & API router
├── package.json                     # Node/React dependencies and scripts
├── requirements.txt                 # Python dependencies
├── metadata.json                    # Application metadata
├── index.html                       # Frontend entry HTML
├── vite.config.ts                   # Vite configuration
├── tsconfig.json                    # TypeScript compiler options
├── data/
│   └── generated/                   # Synthetic access logs and entity profiles
├── docs/                            # Full technical audit & architecture documentation
├── generator/
│   └── synthetic_data_generator.py # Access log & attack vector simulator
├── preprocessing/
│   └── preprocess.py                # Feature extraction & transformation engine
├── models/
│   ├── baseline_model.py            # Statistical baseline & Isolation Forest model
│   ├── anomaly_detector.py          # Sequential sliding state transition detector
│   ├── attack_classifier.py         # Multi-class attack vector classifier
│   ├── cold_start.py                # Peer grouping & Bayesian cold-start handler
│   ├── drift_handler.py             # Page-Hinkley & KS concept drift monitor
│   └── evaluator.py                 # Cross-validation, Platt calibration & F1-Max optimizer
├── explainability/
│   └── explain.py                   # SHAP explainer & SOAR playbook generator
├── utils/
│   ├── logger.py                    # Colored logging utility
│   └── helpers.py                   # Configuration I/O & math helpers
├── reports/
│   └── anomaly_report.md            # Generated Markdown security audit report
├── results/
│   ├── metrics.json                 # Exported evaluation metrics & confusion matrix
│   └── detected_anomalies.json      # Inferred incident records with SHAP attributions
└── src/
    ├── App.tsx                      # Main React component & tab router
    ├── types.ts                     # TypeScript interface definitions
    └── components/
        ├── Navbar.tsx               # Header with navigation & alert badge
        ├── OverviewTab.tsx          # System KPI metrics & quick action panel
        ├── LiveAlertsTab.tsx        # Real-time incident list with filters & drawer
        ├── EntityProfileTab.tsx     # Entity baseline inspector & search
        ├── ExplainabilityTab.tsx    # SHAP feature importance & SOAR playbooks
        ├── AnalyticsTab.tsx         # Recharts performance metrics & confusion matrix
        ├── SettingsTab.tsx          # Interactive hyperparameter controls & retraining trigger
        └── RiskHeatmap.tsx          # 7-day x 24-hour behavioral risk matrix
```

## 2. Configuration Parameters (`pipeline_config.json`)
The ML execution pipeline reads from and writes to `pipeline_config.json`:

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `anomaly_threshold` | integer | `60` | Anomaly score threshold percentile ($100 - \text{threshold}$) |
| `detection_sensitivity` | integer | `60` | Scaling factor for sequence transition anomaly weights |
| `learning_rate` | float | `0.001` | Learning rate parameter for sequence models |
| `sequence_length` | integer | `5` | Sliding window event depth per entity |
| `window_size` | integer | `5` | Time window length for feature aggregation |
| `epochs` | integer | `20` | Number of training iterations for sequence detector |
| `batch_size` | integer | `64` | Training batch size |
| `random_seed` | integer | `42` | Global random seed for reproducible splits |
| `classification_threshold` | integer | `35` | Minimum confidence score for attack categorization |
| `drift_rate` | integer | `29` | Sensitivity threshold for Page-Hinkley drift detector |
| `cold_start_warmup` | integer | `20` | Number of events required before full entity independence |

## 3. Retraining & Execution Commands
- **Run Python ML Pipeline directly**:
  ```bash
  python main.py
  ```
- **Launch Development Server (Express API + Vite React UI on port 3000)**:
  ```bash
  npm run dev
  ```
- **Build Production Bundle**:
  ```bash
  npm run build
  ```
- **Run Production Node Server**:
  ```bash
  npm start
  ```

## 4. Troubleshooting Guide
1. **Python Dependencies Missing**:
   - Run `pip install -r requirements.txt`. Ensure `scikit-learn`, `numpy`, `pandas`, and `shap` are installed.
2. **Pipeline Timeout or Retraining Fallback**:
   - If Python environment is restricted, `server.ts` handles execution gracefully and returns synthesized updated metrics without breaking UI reactivity.
3. **TypeScript Compilation Errors**:
   - Run `npm run lint` (`tsc --noEmit`) to verify interface compliance.
