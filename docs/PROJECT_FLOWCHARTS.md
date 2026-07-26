# AegisAI - Project Flowcharts & Workflow Diagrams

## 1. Overall System Architecture Flowchart
```mermaid
graph TD
    A[Sequential Access Log Ingestion] --> B[Feature Preprocessor]
    B --> C[Haversine Velocity & Cyclical Features]
    C --> D[Isolation Forest Baseline Model]
    C --> E[Sliding Sequence Transition Model]
    D --> F[Ensemble Score Combination]
    E --> F
    F --> G[Platt Probability Calibration]
    G --> H{Score >= F1-Max Threshold?}
    H -- No --> I[Log as Normal Event]
    H -- Yes --> J[Multi-Class Attack Classifier]
    J --> K[Cold-Start & Concept Drift Handlers]
    K --> L[SHAP Feature Explainer & SOAR Engine]
    L --> M[Express REST API / React SOC Dashboard]
```

## 2. Machine Learning Pipeline Flowchart
```mermaid
graph LR
    A[Raw Log Generator] --> B[Z-Score & Velocity Normalizer]
    B --> C[5-Fold Stratified Split]
    C --> D[Model Fitting]
    D --> E[Platt Scaling]
    E --> F[Threshold Optimization Sweep]
    F --> G[Export Model PKL & Metrics JSON]
```

## 3. Retraining & Configuration Workflow
```mermaid
graph TD
    A[Analyst Adjusts Sliders in Settings Tab] --> B[POST Request to /api/pipeline/run]
    B --> C[Update pipeline_config.json]
    C --> D[Spawn python3 main.py]
    D --> E[Re-generate Data & Re-fit Models]
    E --> F[Write results/metrics.json & results/detected_anomalies.json]
    F --> G[Clear Server Cache & Notify Dashboard]
    G --> H[React UI Re-renders with Fresh KPIs]
```

## 4. Threat Detection & SOAR Action Flowchart
```mermaid
graph TD
    A[Detected Anomaly Incident] --> B[Extract Top SHAP Features]
    B --> C{Attack Category?}
    C -- Impossible Travel --> D[Action: REVOKE_SESSION_AND_ENFORCE_MFA]
    C -- Brute Force --> E[Action: BLOCK_IP_AND_LOCK_ACCOUNT]
    C -- Low & Slow Exfiltration --> F[Action: QUARANTINE_DEVICE_AND_CAP_BANDWIDTH]
    C -- Lateral Movement --> G[Action: ISOLATE_NETWORK_SEGMENT]
```
