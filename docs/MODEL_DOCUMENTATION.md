# AegisAI - Machine Learning Engine Documentation

## 1. Overview & Pipeline Lifecycle
AegisAI utilizes an unsupervised and supervised hybrid machine learning engine tailored for extreme class-imbalanced behavioral sequence logs.

```
Access Logs -> Feature Preprocessing -> Dual Anomaly Detection Engine
   -> Calibrated Platt Scaling -> Adaptive F1-Max Thresholding
   -> Multi-Class Attack Classifier -> Cold-Start & Drift Adaptation
   -> SHAP Feature Explainer -> SOAR Recommendation Engine
```

## 2. Model Breakdown & Algorithms

### 2.1 Synthetic Access Log Generator (`generator/synthetic_data_generator.py`)
- **Entities**: 2,000 user/device profiles with role, department, typical location coordinates, and primary devices.
- **Events**: 50,000 sequential timestamps across a 30-day window.
- **Attack Injection**: Exactly 2.0% (1,000 events) representing 7 attack scenarios:
  1. *Brute Force*: Rapid failed login bursts ($\ge 15$ attempts/min).
  2. *Impossible Travel*: $\Delta d / \Delta t > 900\text{ km/h}$.
  3. *Credential Stuffing*: Multiple user logins from single malicious IP.
  4. *Lateral Movement*: Sequential auth across disparate internal hosts.
  5. *Device Spoofing*: User log with unassociated User-Agent / device MAC.
  6. *Low & Slow Exfiltration*: Small steady off-hours data transfers over extended time.
  7. *Insider Threat Drift*: Behavioral deviation without sudden location change.

### 2.2 Feature Preprocessing (`preprocessing/preprocess.py`)
Features extracted per event:
- $v_{\text{geo}} = \frac{\text{Haversine}(\text{lat}_1, \text{lon}_1, \text{lat}_2, \text{lon}_2)}{\Delta t}$
- $t_{\sin} = \sin\left(\frac{2\pi \cdot \text{hour}}{24}\right), \quad t_{\cos} = \cos\left(\frac{2\pi \cdot \text{hour}}{24}\right)$
- $z_{\text{failed\_logins}} = \frac{x_{\text{failed}} - \mu_{\text{failed}}}{\sigma_{\text{failed}}}$
- $z_{\text{session\_duration}} = \frac{x_{\text{dur}} - \mu_{\text{dur}}}{\sigma_{\text{dur}}}$

### 2.3 Dual Detection Architecture (`models/baseline_model.py` & `models/anomaly_detector.py`)
- **Statistical Baseline Model**: Unsupervised Isolation Forest (100 estimators, 0.03 contamination) combined with Euclidean distance to entity Mahalanobis baseline centroid.
- **Sequential Anomaly Detector**: Sliding state transition score matrix calculating transition improbability $P(S_t | S_{t-1}, \dots, S_{t-k})$.

### 2.4 Probability Calibration & Threshold Optimization (`models/evaluator.py`)
- **Platt Scaling**: Fits a logistic regression model on cross-validated log-odds scores:
  $$P(\text{Anomaly} \mid S) = \frac{1}{1 + e^{-(A \cdot S + B)}}$$
- **Adaptive Thresholding ($T_{f1\_max}$)**: Sweeps decision boundaries $T \in [0.10, 0.90]$ to maximize the F1-score:
  $$T_{\text{optimal}} = \arg\max_T \frac{2 \cdot \text{Precision}(T) \cdot \text{Recall}(T)}{\text{Precision}(T) + \text{Recall}(T)}$$

### 2.5 Multi-Class Threat Classifier (`models/attack_classifier.py`)
Random Forest multi-class model (150 trees, max depth 12) mapping detected anomalies to 7 cyber threat categories with class-weighted balance.

### 2.6 Cold-Start Bayesian Grouping (`models/cold_start.py`)
For entities with fewer than $N_{\text{warmup}} = 20$ events:
- Grouped into 4 peer clusters using Ward Hierarchical Linkage over department and role vectors.
- Baseline expectations set to peer cluster mean:
  $$\mu_{\text{effective}} = (1-w) \cdot \mu_{\text{peer\_cluster}} + w \cdot \mu_{\text{observed}}$$

### 2.7 Concept Drift Engine (`models/drift_handler.py`)
- **Isolation Rule**: Events with $\text{Anomaly Score} > 0.65$ are excluded from drift baseline updates to prevent poisoned baselines.
- **Page-Hinkley Test**: Tracks cumulative difference $S_t = \sum (x_i - \bar{x} - \delta)$. Drift flagged when $S_t - \min(S) > \lambda_{\text{drift}}$.

### 2.8 SHAP Feature Attribution (`explainability/explain.py`)
Computes local feature contributions $\phi_i$ explaining why an anomaly exceeded threshold $T$, outputting natural language security explanations and SOAR playbook recommendations.
