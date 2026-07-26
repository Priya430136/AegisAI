# AegisAI - 3-5 Minute Hackathon Live Demonstration Script

## Overview
- **Target Duration**: 4 Minutes
- **Presenter Role**: Lead Cybersecurity Architect
- **Environment**: AegisAI Dashboard open at `http://localhost:3000`

---

## Script & Action Timeline

### 0:00 - 0:45 | Introduction & Problem Overview
- **Action**: Display the **Overview Tab** on screen.
- **Presenter Speaks**:
  > "Honorable judges, welcome to **AegisAI**—an enterprise-grade behavioral anomaly detection and threat intelligence platform.
  > Modern cyber threats like Impossible Travel, Credential Stuffing, and Low & Slow Exfiltration easily bypass traditional firewalls. Furthermore, when standard ML models encounter extreme 98% normal vs 2% attack imbalance, they suffer from a massive 60% false positive rate.
  > AegisAI solves this using sequential deep learning, Bayesian cold-start peer grouping, concept drift isolation, and SHAP explainability."

---

### 0:45 - 1:30 | Live Threat Stream & Incident Investigation
- **Action**: Click on the **Live Alerts Tab**. Select an "Impossible Travel" incident row.
- **Presenter Speaks**:
  > "Here in the Live Alerts Tab, AegisAI monitors 50,000+ access logs in near real time. Let's inspect this critical incident for user `USR-1082`.
  > Notice the calculated physical travel velocity: **2,450 km/h**—far exceeding commercial physical limits. AegisAI immediately classifies the threat as *Impossible Travel* with a 94% risk score and automatically attaches a SOAR playbook recommendation: *REVOKE_SESSION_AND_ENFORCE_MFA*."

---

### 1:30 - 2:30 | SHAP Explainability (XAI)
- **Action**: Click **"View SHAP Breakdown"** or navigate to the **Explainability Tab**.
- **Presenter Speaks**:
  > "Security analysts cannot trust black-box AI models. In the Explainability Tab, AegisAI provides local SHAP feature impact rankings.
  > As you can see, `geo_velocity_kmh` contributed $+0.42$ to the anomaly score, while `is_off_hours` added $+0.18$. We also generate natural language security rationales so tier-1 analysts can understand and validate threats in seconds."

---

### 2:30 - 3:15 | Cold-Start & Concept Drift Engineering
- **Action**: Click on the **Entity Explorer Tab** and search for `USR-2374`.
- **Presenter Speaks**:
  > "A major innovation in AegisAI is how we handle new users and changing habits. In traditional systems, a new employee triggers hundreds of false alarms.
  > AegisAI's **Cold-Start Engine** places new users into departmental peer clusters using Ward Hierarchical Linkage and progressively blends cluster baselines using Bayesian weights as warmup progress reaches 100%.
  > Additionally, our **Concept Drift Engine** uses Page-Hinkley cumulative sum tests to learn legitimate schedule changes while isolating attack spikes so baseline models are never poisoned."

---

### 3:15 - 4:00 | Live Hyperparameter Retraining & Conclusion
- **Action**: Click on the **Settings Tab**. Adjust the `Anomaly Threshold` slider and click **"Run Full Retraining Pipeline"**.
- **Presenter Speaks**:
  > "Finally, AegisAI provides live MLOps controls in the Settings Tab. SOC administrators can tune decision boundaries or sensitivity and trigger a full end-to-end retraining run.
  > Within seconds, our Python engine re-evaluates models across 50,000 events and dispatches fresh benchmark metrics directly to the React UI without page reloads.
  > AegisAI achieves **96.5% accuracy**, **2.87% false positive rate**, and processes over **5,200 events per second**. Thank you!"
