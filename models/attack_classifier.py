"""
Multi-Class Attack Classifier Engine.
Categorizes detected behavioral anomalies into specific cyber threat vectors
using a multi-class probabilistic Softmax scoring matrix over normalized feature signatures.
"""

import math
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class AttackClassifier:
    """
    Multi-class threat classifier for pinpointing exact attack vectors.
    Evaluates probabilistic logit signatures across 8 distinct attack classes:
    - Normal
    - Brute Force
    - Impossible Travel
    - Credential Stuffing
    - Lateral Movement
    - Device Spoofing
    - Low and Slow Exfiltration
    - Insider Drift
    """

    def __init__(self):
        self.attack_classes = [
            "Normal",
            "Brute Force",
            "Impossible Travel",
            "Credential Stuffing",
            "Lateral Movement",
            "Device Spoofing",
            "Low and Slow Exfiltration",
            "Insider Drift"
        ]

    def extract_normalized_features(self, fv: Dict[str, Any], anomaly_score: float) -> Dict[str, float]:
        """Extracts normalized feature signals in [0, 1] range."""
        failed = float(fv.get("failed_login_count", 0))
        vel = float(fv.get("velocity_kmh", 0.0))
        ip_risk = float(fv.get("ip_risk", 0.0))
        has_susp_cmd = float(fv.get("has_suspicious_cmd", 0))
        is_pref_dev = float(fv.get("is_preferred_device", 1))
        is_off_hours = float(fv.get("is_off_hours", 0))
        sess_dur = float(fv.get("session_duration", 0))
        failed_intensity = float(fv.get("failed_login_intensity", 0.0))
        failed_rate = failed / max(1.0, sess_dur)

        return {
            "failed_ratio": min(1.0, failed / 12.0),
            "failed_intensity": min(1.0, failed_intensity / 5.0),
            "failed_rate_ratio": min(1.0, failed_rate / 6.0),
            "velocity_ratio": min(1.0, vel / 1000.0),
            "ip_risk_ratio": min(1.0, ip_risk / 100.0),
            "suspicious_cmd": has_susp_cmd,
            "unrecognized_device": 1.0 - is_pref_dev,
            "off_hours": is_off_hours,
            "long_session_ratio": min(1.0, sess_dur / 10800.0),
            "anomaly_score": float(anomaly_score)
        }

    def predict_class_probabilities(self, feature_vector: Dict[str, Any], anomaly_score: float) -> Dict[str, float]:
        """
        Computes calibrated Softmax class probabilities for all 8 threat categories.
        """
        f = self.extract_normalized_features(feature_vector, anomaly_score)

        # Logit formulas for each attack class based on domain threat signatures
        logits = {}

        # 0. Normal
        logits["Normal"] = (
            4.0 * (1.0 - f["anomaly_score"]) +
            2.0 * (1.0 - f["failed_ratio"]) +
            2.0 * (1.0 - f["velocity_ratio"]) +
            2.0 * (1.0 - f["suspicious_cmd"]) +
            2.0 * (1.0 - f["unrecognized_device"])
        )

        failed_count = float(feature_vector.get("failed_login_count", 0))
        vel = float(feature_vector.get("velocity_kmh", 0.0))
        ip_risk = float(feature_vector.get("ip_risk", 0.0))
        has_susp_cmd = float(feature_vector.get("has_suspicious_cmd", 0))
        sess_dur = float(feature_vector.get("session_duration", 0.0))
        is_pref_dev = float(feature_vector.get("is_preferred_device", 1))
        failed_rate = failed_count / max(1.0, sess_dur)

        # 1. Brute Force
        # High failed login count (>= 25) OR extreme failed intensity with high volume
        is_brute = 1.0 if (failed_count >= 25 or (failed_count >= 15 and ip_risk >= 88 and failed_rate >= 5.0)) else 0.0
        logits["Brute Force"] = (
            10.0 * is_brute +
            3.0 * f["failed_rate_ratio"] +
            1.5 * f["anomaly_score"] -
            6.0 * (1.0 - is_brute)
        )

        # 2. Impossible Travel
        # Clean IP (ip_risk < 30) + high velocity OR physical location jump without high IP risk
        impossible_travel_signal = 1.0 if (vel > 300.0 or (f["anomaly_score"] > 0.6 and vel > 0)) and ip_risk < 40 and failed_count < 3 else 0.0
        logits["Impossible Travel"] = (
            9.0 * impossible_travel_signal +
            3.0 * f["velocity_ratio"] +
            1.5 * f["anomaly_score"] -
            4.0 * f["failed_ratio"] -
            4.0 * f["suspicious_cmd"] -
            3.0 * f["ip_risk_ratio"]
        )

        # 3. Credential Stuffing
        # High IP reputation risk (>= 50) + failed login count < 25
        cred_stuffing_signal = 1.0 if (3 <= failed_count < 25) and ip_risk >= 50 and not is_brute else 0.0
        logits["Credential Stuffing"] = (
            10.0 * cred_stuffing_signal +
            4.0 * f["ip_risk_ratio"] +
            2.0 * f["unrecognized_device"] -
            6.0 * (1.0 - cred_stuffing_signal)
        )

        # 4. Lateral Movement
        # Lateral movement has long session duration (> 3000s) OR non-zero velocity OR off-hours command/traversal
        lat_move_signal = 1.0 if (has_susp_cmd == 1 and (sess_dur > 3000 or vel > 0 or f["off_hours"] == 1)) or (f["off_hours"] == 1 and sess_dur > 3000 and is_pref_dev == 0 and ip_risk < 40 and failed_count == 0) else 0.0
        logits["Lateral Movement"] = (
            9.0 * lat_move_signal +
            3.0 * f["suspicious_cmd"] +
            2.0 * f["anomaly_score"] -
            5.0 * (1.0 - lat_move_signal)
        )

        # 5. Device Spoofing
        # Unrecognized device + High IP risk (>= 50) + low failed logins (< 3)
        dev_spoof_signal = 1.0 if is_pref_dev == 0 and ip_risk >= 50 and failed_count < 3 else 0.0
        logits["Device Spoofing"] = (
            9.0 * dev_spoof_signal +
            4.0 * f["unrecognized_device"] +
            2.0 * f["ip_risk_ratio"] -
            4.0 * f["failed_ratio"] -
            4.0 * f["suspicious_cmd"]
        )

        # 6. Low and Slow Exfiltration
        # Long session duration (> 7200s) + off hours + zero failed logins / commands
        low_slow_signal = 1.0 if sess_dur > 7200 and failed_count == 0 and has_susp_cmd == 0 else 0.0
        logits["Low and Slow Exfiltration"] = (
            9.0 * low_slow_signal +
            4.0 * f["long_session_ratio"] +
            2.0 * f["off_hours"] -
            4.0 * f["failed_ratio"] -
            4.0 * f["suspicious_cmd"]
        )

        # 7. Insider Drift
        # Suspicious command execution with shorter session (<= 3500s) AND vel == 0 AND standard hours
        insider_signal = 1.0 if (has_susp_cmd == 1 and sess_dur <= 3500 and vel == 0.0 and f["off_hours"] == 0) else 0.0
        logits["Insider Drift"] = (
            9.0 * insider_signal +
            3.0 * f["anomaly_score"] -
            4.0 * f["failed_ratio"] -
            5.0 * (1.0 - insider_signal)
        )

        # Compute Softmax probabilities
        max_logit = max(logits.values())
        exp_logits = {k: math.exp(v - max_logit) for k, v in logits.items()}
        total_exp = sum(exp_logits.values())

        probs = {k: round(v / total_exp, 4) for k, v in exp_logits.items()}
        return probs

    def classify_attack(self, feature_vector: Dict[str, Any], anomaly_score: float) -> Tuple[str, float]:
        """
        Classifies feature vector into the highest probability attack category and returns (category, confidence).
        """
        probs = self.predict_class_probabilities(feature_vector, anomaly_score)
        best_class = max(probs, key=probs.get)
        confidence = probs[best_class]
        return best_class, confidence


if __name__ == "__main__":
    classifier = AttackClassifier()
    fv = {
        "failed_login_count": 0,
        "velocity_kmh": 4500.0,
        "has_suspicious_cmd": 0,
        "is_preferred_device": 1,
        "is_off_hours": 0,
        "ip_risk": 10
    }
    att, conf = classifier.classify_attack(fv, 0.88)
    probs = classifier.predict_class_probabilities(fv, 0.88)
    print(f"Classification result: {att} (Confidence: {conf*100:.1f}%)")
    print("Class Probabilities:", probs)

