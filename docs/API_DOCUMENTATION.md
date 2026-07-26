# AegisAI - API Reference Documentation

All endpoints are hosted on port `3000` via Express (`server.ts`).

---

### 1. `GET /api/metrics`
Retrieves overall system benchmark performance metrics, attack distributions, and confusion matrix state.

**Response `200 OK`**:
```json
{
  "dataset_size": 50000,
  "total_anomalies_detected": 1000,
  "accuracy": 0.9645,
  "precision": 0.3087,
  "recall": 0.6270,
  "f1_score": 0.4137,
  "roc_auc": 0.8420,
  "false_positive_rate": 0.0287,
  "confusion_matrix": {
    "true_positives": 627,
    "false_positives": 1404,
    "true_negatives": 47596,
    "false_negatives": 373
  },
  "attack_distribution": {
    "Brute Force": 210,
    "Impossible Travel": 185,
    "Credential Stuffing": 150,
    "Lateral Movement": 145,
    "Device Spoofing": 120,
    "Low and Slow Exfiltration": 95,
    "Insider Drift": 95
  }
}
```

---

### 2. `GET /api/anomalies`
Retrieves detected anomalous incident records complete with risk scores, classified attack types, SHAP feature importance, and SOAR recommendations.

**Response `200 OK`**:
```json
[
  {
    "event_id": "EVT-90421",
    "timestamp": "2026-07-26T12:45:00Z",
    "entity_id": "USR-1082",
    "user_id": "USR-1082",
    "entity_type": "USER",
    "anomaly_score": 92.4,
    "risk_score": 94,
    "severity": "CRITICAL",
    "attack_type": "Impossible Travel",
    "confidence": 0.96,
    "ip_address": "185.220.101.4",
    "location": "Frankfurt, Germany",
    "geo_velocity_kmh": 2450.8,
    "is_off_hours": true,
    "failed_logins": 1,
    "shap_explanations": [
      {
        "feature": "geo_velocity_kmh",
        "value": 2450.8,
        "impact": 0.42,
        "description": "Travel velocity of 2450.8 km/h exceeds 900 km/h physical limit."
      },
      {
        "feature": "is_off_hours",
        "value": 1,
        "impact": 0.18,
        "description": "Access requested outside standard active hours."
      }
    ],
    "soar_playbook": {
      "action": "REVOKE_SESSION_AND_ENFORCE_MFA",
      "status": "RECOMMENDED",
      "description": "Immediately terminate active tokens for USR-1082 and isolate IP 185.220.101.4."
    }
  }
]
```

---

### 3. `GET /api/entities`
Returns entity baseline profiles across all monitored users and devices.

**Response `200 OK`**:
```json
{
  "USR-1082": {
    "entity_id": "USR-1082",
    "entity_type": "USER",
    "department": "Engineering",
    "role": "Senior Developer",
    "is_cold_start": false,
    "warmup_progress": 1.0,
    "peer_cluster_id": 2,
    "total_events_observed": 1420,
    "baseline": {
      "avg_session_duration": 245.5,
      "avg_failed_logins": 0.05,
      "typical_locations": ["New York, US", "Boston, US"],
      "common_devices": ["MACBOOK-PRO-01"]
    },
    "risk_history": [12, 15, 14, 94, 18],
    "current_risk_level": "CRITICAL"
  }
}
```

---

### 4. `GET /api/config`
Fetches active pipeline hyperparameter settings.

**Response `200 OK`**:
```json
{
  "anomaly_threshold": 60,
  "detection_sensitivity": 60,
  "learning_rate": 0.001,
  "sequence_length": 5,
  "window_size": 5,
  "epochs": 20,
  "batch_size": 64,
  "random_seed": 42,
  "classification_threshold": 35,
  "drift_rate": 29,
  "cold_start_warmup": 20
}
```

---

### 5. `POST /api/pipeline/run`
Triggers full end-to-end model retraining and data re-evaluation using updated hyperparameter settings.

**Request Body**:
```json
{
  "anomaly_threshold": 65,
  "detection_sensitivity": 70,
  "classification_threshold": 40
}
```

**Response `200 OK`**:
```json
{
  "success": true,
  "message": "Pipeline executed successfully",
  "output": "Pipeline completed successfully! All models, results, and reports generated."
}
```

---

### 6. `POST /api/pipeline/reset`
Resets all hyperparameters to default values and retrains the detection engine.

**Response `200 OK`**:
```json
{
  "success": true,
  "message": "Settings reset to default and pipeline retrained successfully",
  "config": {
    "anomaly_threshold": 60,
    "detection_sensitivity": 60,
    "learning_rate": 0.001,
    "sequence_length": 5,
    "window_size": 5,
    "epochs": 20,
    "batch_size": 64,
    "random_seed": 42,
    "classification_threshold": 35,
    "drift_rate": 29,
    "cold_start_warmup": 20
  }
}
```

---

### 7. `GET /api/reports/download`
Downloads the generated Markdown audit report (`reports/anomaly_report.md`).

**Response `200 OK`**: Raw Markdown file stream attachment.
