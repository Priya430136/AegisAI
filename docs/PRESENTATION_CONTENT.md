# AegisAI - Hackathon Pitch Presentation Deck (6 Slides)

---

## Slide 1: Title & Vision
- **Header**: 🛡️ AegisAI: Autonomous Behavioral Threat Intelligence Platform
- **Sub-header**: Zero-Day Cyber Attack Detection, SHAP Explainability & Adaptive Cold-Start Defense
- **Bullet Points**:
  - Enterprise SOC defense platform for sequential user and device access logs.
  - Combines unsupervised baseline profiling, sequence state modeling, and multi-class threat classification.
  - Reduces False Positive Rates from >60% down to 2.87% using adaptive F1-Max thresholding.
- **Suggested Visuals & Icons**: Large metallic blue shield logo (`ShieldAlert` icon), sleek dark canvas presentation frame, lock & AI brain diagrams.
- **Screenshot Placement**: Insert high-resolution hero screenshot of the AegisAI Overview Tab dashboard.

---

## Slide 2: The Cyber Threat Crisis & The Imbalance Problem
- **Header**: 🚨 Problem: Rule Engines Fail & False Positives Overwhelm SOCs
- **Bullet Points**:
  - Modern threats (Impossible Travel, Credential Stuffing, Low & Slow Exfiltration) bypass static IP rules.
  - Extreme class imbalance (< 2% attacks) causes fixed-threshold ML systems to produce 60%+ False Positives.
  - Newly onboarded employees trigger massive "Cold-Start" false alert floods.
  - Legitimate employee behavior changes (promotions, shifts) trigger false "Concept Drift" alarms.
- **Suggested Visuals & Icons**: Warning triangle (`TriangleAlert`), scale balance icon showing 98% benign vs 2% attack imbalance.
- **Screenshot Placement**: Diagram comparing static threshold alert flood vs AegisAI filtered alerts.

---

## Slide 3: Architectural Innovation & Machine Learning Engine
- **Header**: ⚡ System Architecture: Multi-Layered AI Pipeline
- **Bullet Points**:
  - **Sequential Log Feature Engine**: Computes Haversine velocity ($\text{km/h}$), time-cyclical sine/cosine, and z-score metrics.
  - **Dual Unsupervised Engine**: Statistical Isolation Forest + Sliding Sequence Transition Probability matrix.
  - **Platt Probability Calibration**: Converts raw log-odds scores into true calibrated probabilities $[0, 1]$.
  - **Bayesian Peer Cold-Start**: Hierarchical Ward Clustering groups new entities into peer clusters to eliminate startup alerts.
  - **Isolated Concept Drift**: Page-Hinkley test adapts baselines while isolating attack spikes from baseline contamination.
- **Suggested Visuals & Icons**: Pipeline flow diagram (`Workflow` icon), CPU brain icon, cluster network diagram.
- **Screenshot Placement**: Insert System Architecture Mermaid Diagram from `docs/SYSTEM_ARCHITECTURE.md`.

---

## Slide 4: Real-Time SHAP Explainability & SOAR Automation
- **Header**: 🔍 Explainable AI (XAI) & Instant Remediation Playbooks
- **Bullet Points**:
  - Black-box ML models are unusable in SOCs without transparent rationale.
  - AegisAI generates local SHAP feature impact scores for every flagged incident.
  - Automated natural language rationale explains *why* the score spiked (e.g., "Velocity $2,450 \text{ km/h}$ exceeds $900 \text{ km/h}$ physical limit").
  - Instant SOAR Playbook recommendations (*REVOKE_SESSION*, *ISOLATE_IP*, *ENFORCE_MFA*).
- **Suggested Visuals & Icons**: Magnifying glass (`Search`), SHAP bar chart visualization, bolt action button (`Zap`).
- **Screenshot Placement**: Insert screenshot of the AegisAI Explainability Tab showing SHAP Feature Importance bars and SOAR playbooks.

---

## Slide 5: Proven Benchmark Results & Live SOC Dashboard
- **Header**: 📊 Benchmark Results: High Precision at Enterprise Scale
- **Bullet Points**:
  - Tested across **50,000 sequential events** and **2,000 user/device entities**.
  - **96.5% Overall Accuracy** with **2.87% False Positive Rate** (down from 61.6%).
  - **35.8% Precision at Top 1% Alert Threshold**.
  - High-throughput inference: **< 0.20 ms / event** (> 5,200 events/second).
  - Fully interactive React + Express SOC dashboard with live retraining controls.
- **Suggested Visuals & Icons**: Bar chart (`BarChart3`), gauge meter showing 0.18ms latency, checkmark badge (`CheckCircle2`).
- **Screenshot Placement**: Insert screenshot of the Analytics Tab featuring ROC AUC curve and Confusion Matrix.

---

## Slide 6: Enterprise Readiness & Future Roadmap
- **Header**: 🚀 Enterprise Integration & Future Roadmap
- **Bullet Points**:
  - **SIEM / Event Ingestion**: Direct Kafka stream, Splunk HEC, and Elastic connectors.
  - **Zero-Trust Microsegmentation**: Automated API hooks to Palo Alto / Cloudflare security gateways.
  - **Deep Graph Neural Networks (GNN)**: Organizational trust graph modeling for multi-entity collusion.
  - Ready for immediate enterprise SOC deployment.
- **Suggested Visuals & Icons**: Cloud server (`Server`), network graph (`Network`), rocket launch (`Rocket`).
- **Screenshot Placement**: Insert screenshot of the Settings Tab showing live parameter tuning and export capabilities.
