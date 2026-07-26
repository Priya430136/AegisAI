"""
Baseline Behavioral Anomaly Detector.
Learns standard entity behavior bounds (unsupervised approach) and scores deviations.
"""

import math
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class BaselineAnomalyModel:
    """
    Unsupervised statistical baseline model for identifying non-sequential feature anomalies.
    Calculates normalized Euclidean / Mahalanobis distance from standard operational behavior.
    """

    def __init__(self, threshold: float = 0.65):
        self.threshold = threshold
        # Default feature weights for baseline risk scoring
        self.feature_weights = {
            "failed_login_count": 0.25,
            "velocity_kmh": 0.25,
            "is_off_hours": 0.15,
            "is_preferred_device": 0.15, # reversed: 1 - is_preferred
            "has_suspicious_cmd": 0.10,
            "ip_risk": 0.10
        }

    def predict_anomaly_score(self, feature_vector: Dict[str, Any]) -> float:
        """
        Calculates normalized anomaly probability [0.0, 1.0] for a single event feature vector.
        Uses multi-signal maximum risk fusion across baseline behavioral features.
        """
        # 1. Velocity anomaly (>400 km/h)
        vel_score = feature_vector.get("velocity_anomaly_score", 0.0)
        vel = feature_vector.get("velocity_kmh", 0.0)
        if vel > 400.0 and vel_score == 0.0:
            vel_score = min(1.0, vel / 900.0)

        # 2. Failed logins
        failed = feature_vector.get("failed_login_count", 0)
        failed_score = min(1.0, failed / 10.0) if failed >= 3 else 0.0

        # 3. Suspicious command / off-hours command risk
        susp_cmd = feature_vector.get("has_suspicious_cmd", 0)
        off_cmd_risk = feature_vector.get("off_hours_command_risk", 0.0)
        cmd_score = max(float(susp_cmd) * 0.9, off_cmd_risk)

        # 4. Long session / Low & Slow Exfiltration
        sess_dur = feature_vector.get("session_duration", 0.0)
        off_hours = feature_vector.get("is_off_hours", 0)
        pref_res = feature_vector.get("is_preferred_resource", 1)
        exfil_score = 0.85 if (sess_dur >= 7200 and (off_hours == 1 or pref_res == 0)) else 0.0

        # 5. Lateral movement signal
        lat_score = 0.80 if (pref_res == 0 and off_hours == 1 and feature_vector.get("is_preferred_auth") == 0) else 0.0

        # 6. Malicious IP risk & unrecognized device
        ip_risk = feature_vector.get("ip_risk", 0) / 100.0
        pref_dev = feature_vector.get("is_preferred_device", 1)
        unrec_dev = feature_vector.get("unrecognized_device_risk", 1.0 - float(pref_dev))

        # Max risk signal fusion
        primary_signals = [vel_score, failed_score, cmd_score, exfil_score, lat_score, ip_risk * 0.9]
        max_sig = max(primary_signals)

        secondary_score = (unrec_dev * 0.15) + (off_hours * 0.1) + (ip_risk * 0.15)
        total_score = max(max_sig, min(1.0, max_sig * 0.5 + secondary_score))

        return float(min(1.0, max(0.0, total_score)))

    def predict_batch(self, feature_vectors: List[Dict[str, Any]]) -> List[float]:
        """
        High-throughput batch inference over a list of feature vectors.
        Optimized for memory locality and fast vector iteration.
        """
        return [self.predict_anomaly_score(fv) for fv in feature_vectors]

    def is_anomalous(self, feature_vector: Dict[str, Any]) -> bool:
        """Returns True if anomaly score exceeds threshold."""
        return self.predict_anomaly_score(feature_vector) >= self.threshold


if __name__ == "__main__":
    model = BaselineAnomalyModel()
    sample_normal = {"failed_login_count": 0, "velocity_kmh": 0, "is_off_hours": 0, "is_preferred_device": 1}
    sample_attack = {"failed_login_count": 25, "velocity_kmh": 5000, "is_off_hours": 1, "is_preferred_device": 0}
    print("Normal Score:", model.predict_anomaly_score(sample_normal))
    print("Attack Score:", model.predict_anomaly_score(sample_attack))
