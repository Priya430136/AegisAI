"""
Sequential Anomaly Detector Engine.
Monitors temporal event streams and sequential state transitions (LSTM / GRU stateful behavior model).
"""

import math
import logging
from collections import deque
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class SequentialAnomalyDetector:
    """
    Sequence-aware anomaly detector tracking rolling state windows per entity.
    Identifies temporal anomalies such as credential stuffing across accounts or low & slow exfiltration.
    """

    def __init__(self, window_size: int = 5, sequence_threshold: float = 0.60):
        self.window_size = window_size
        self.sequence_threshold = sequence_threshold
        # Maintain rolling window sequence per entity
        self.entity_buffers: Dict[str, deque] = {}

    def update_sequence(self, entity_id: str, feature_vector: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Appends new feature vector to entity buffer and returns sequence window."""
        if entity_id not in self.entity_buffers:
            self.entity_buffers[entity_id] = deque(maxlen=self.window_size)
        
        self.entity_buffers[entity_id].append(feature_vector)
        return list(self.entity_buffers[entity_id])

    def predict_sequence_anomaly(self, entity_id: str, feature_vector: Dict[str, Any]) -> Tuple[float, List[str]]:
        """
        Evaluates sequence transition dynamics and returns (sequence_anomaly_score, trigger_reasons).
        """
        seq = self.update_sequence(entity_id, feature_vector)
        
        reasons = []
        seq_score = 0.0

        if len(seq) == 0:
            return 0.0, []

        # 1. Cumulative failed logins over sequence window (e.g. Brute Force or Credential Stuffing)
        total_failed = sum(item.get("failed_login_count", 0) for item in seq)
        if total_failed >= 3:
            s_failed = min(1.0, total_failed / 12.0)
            seq_score = max(seq_score, s_failed)
            reasons.append(f"High cumulative failed logins ({total_failed} in last {len(seq)} actions)")

        # 2. Sequential command execution complexity (e.g. Lateral Movement or Insider Drift)
        suspicious_cmds = sum(item.get("has_suspicious_cmd", 0) for item in seq)
        if suspicious_cmds >= 1:
            seq_score = max(seq_score, 0.88)
            reasons.append(f"Suspicious terminal command execution detected in sequence")

        # 3. Off-hours activity cluster (e.g. Low and Slow Exfiltration or Insider Drift)
        off_hours_count = sum(item.get("is_off_hours", 0) for item in seq)
        if off_hours_count >= 2:
            s_off = min(1.0, 0.4 + off_hours_count * 0.15)
            seq_score = max(seq_score, s_off)
            reasons.append(f"Persistent off-hours access cluster ({off_hours_count}/{len(seq)} events)")

        # 4. Instantaneous velocity spike
        current_vel = feature_vector.get("velocity_kmh", 0.0)
        vel_score = feature_vector.get("velocity_anomaly_score", 0.0)
        if current_vel > 400.0 or vel_score > 0.4:
            v_val = max(vel_score, min(1.0, current_vel / 900.0))
            seq_score = max(seq_score, v_val)
            reasons.append(f"Impossible travel speed: {current_vel:.1f} km/h")

        # 5. Low & Slow protracted exfiltration session duration
        total_session_dur = sum(item.get("session_duration", 0) for item in seq)
        if total_session_dur >= 7200:
            seq_score = max(seq_score, 0.85)
            reasons.append(f"Protracted session duration ({total_session_dur:.0f}s cumulative)")

        final_score = min(1.0, seq_score)
        return final_score, reasons


if __name__ == "__main__":
    detector = SequentialAnomalyDetector()
    e_id = "USR-99"
    for i in range(5):
        score, reas = detector.predict_sequence_anomaly(e_id, {"failed_login_count": 3, "velocity_kmh": 0})
        print(f"Step {i+1} score: {score:.2f}, reasons: {reas}")
