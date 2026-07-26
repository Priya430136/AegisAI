# AegisAI - Security Analyst User Manual

## 1. Getting Started
Launch AegisAI using the following steps:
1. Open terminal and start the server: `npm run dev`
2. Access the SOC dashboard in your web browser at `http://localhost:3000`.

---

## 2. Dashboard Navigation & Tab Overview

```
+------------------------------------------------------------------------------------+
| [ Shield Logo ] AegisAI v2.4                                [ 1,000 Alerts Active ] |
| [ Overview ] [ Live Alerts ] [ Entity Explorer ] [ Explainability ] [ Analytics ] [ Settings ] |
+------------------------------------------------------------------------------------+
```

### 2.1 Overview Tab
- **System KPIs**: Displays total dataset volume (50,000 logs), active detected anomalies (1,000 alerts), Precision (30.9%), F1-Max Score (41.4%), and False Positive Rate (2.87%).
- **Interactive Risk Heatmap**: Displays a 7-day $\times$ 24-hour behavioral matrix highlighting peak anomaly activity time windows. Click any cell to inspect specific hourly events.
- **Top Vulnerable Entities**: Lists users and devices exhibiting the highest cumulative threat scores.

### 2.2 Live Alerts Tab
- **Real-Time Incident Stream**: Filter incidents by severity (CRITICAL, HIGH, MEDIUM, LOW), attack category (Brute Force, Impossible Travel, etc.), or search by user ID.
- **Incident Investigation Drawer**: Click any alert row to view detailed telemetry:
  - Calculated Geo-Velocity ($\text{km/h}$).
  - Off-Hours access indicators.
  - Recommended SOAR playbooks (e.g. *REVOKE_SESSION_AND_ENFORCE_MFA*).
  - Click **"View SHAP Breakdown"** to route directly to the Explainability engine.

### 2.3 Entity Explorer Tab
- **User & Device Baseline Profiles**: Search any entity ID (e.g., `USR-1082`) to review:
  - Role, department, and peer group cluster index.
  - Cold-start progress bar ($0\% - 100\%$).
  - Typical location and device fingerprints.
  - Risk score trend history.

### 2.4 Explainability (XAI) Tab
- **SHAP Feature Importance**: View top contributing features for any selected anomaly (e.g., geo-velocity impact $+0.42$, off-hours impact $+0.18$).
- **Automated Security Rationale**: Natural language rationale breaking down why the behavioral detector flagged the event.

### 2.5 Analytics Tab
- **Model Evaluation Dashboard**: Interactive Recharts displaying ROC AUC Curves, Precision-Recall tradeoff curves, Confusion Matrix, and Attack Distribution breakdowns.

### 2.6 Settings Tab
- **Interactive Hyperparameter Tuning**: Adjust sliders for Anomaly Threshold Percentile, Detection Sensitivity, Classification Threshold, Drift Rate, and Cold-Start Warmup Events.
- **Pipeline Retraining Trigger**: Click **"Run Full Retraining Pipeline"** to re-execute models and update system state live.
- **Export Executive Audit Report**: Click **"Download Audit Report (.md)"** to save the latest system assessment.
