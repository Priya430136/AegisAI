"""
Concept Drift Handler Engine.

Implements adaptive concept drift detection (ADWIN with Hoeffding bounds & Page-Hinkley cumulative sum tests),
attack-filtered non-anomalous event streaming, dynamic variance-scaled thresholds,
entity-level drift tracking with confidence scoring, and incremental baseline updates via EMA.
"""

import math
import logging
from collections import deque
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ConceptDriftHandler:
    """
    Monitors rolling behavioral metrics using Adaptive Windowing (ADWIN) and Page-Hinkley tests.
    Prevents false drift triggers caused by cyber attacks by isolating anomalous events,
    and dynamically adapts entity baselines using Exponential Moving Averages (EMA).
    """

    def __init__(self, window_size: int = 50, drift_sensitivity: float = 0.20, delta: float = 0.05, min_window: int = 10):
        self.max_window_size = window_size
        self.drift_sensitivity = drift_sensitivity  # Sensitivity offset parameter
        self.delta = delta                          # Hoeffding confidence level (e.g. 0.05 for 95% confidence)
        self.min_window = min_window                # Minimum sub-window length for statistical testing
        
        # Entity-level tracking data structures
        self.entity_history: Dict[str, deque] = {}
        self.entity_clean_history: Dict[str, deque] = {}
        self.entity_states: Dict[str, Dict[str, Any]] = {}

    def _get_or_create_state(self, entity_id: str) -> Dict[str, Any]:
        if entity_id not in self.entity_states:
            self.entity_history[entity_id] = deque(maxlen=self.max_window_size)
            self.entity_clean_history[entity_id] = deque(maxlen=self.max_window_size * 2)
            self.entity_states[entity_id] = {
                "entity_id": entity_id,
                "total_events": 0,
                "clean_events": 0,
                "anomalous_events": 0,
                "drift_detected": False,
                "drift_confidence": 0.0,
                "drift_type": "none",
                "drift_count": 0,
                "last_drift_timestamp": None,
                "mean": 0.0,
                "variance": 0.0,
                "ph_cumulative_sum": 0.0,
                "ph_min_sum": float('inf'),
                "adaptive_window_size": 0,
                "adaptive_threshold": self.drift_sensitivity
            }
        return self.entity_states[entity_id]

    def record_event(
        self,
        entity_id: str,
        feature_vector: Dict[str, Any],
        anomaly_score: float,
        is_predicted_anomaly: bool = False,
        timestamp: Optional[str] = None
    ):
        """
        Records an event score for an entity.
        CRITICAL: Isolates predicted attacks/anomalies into a separate buffer to prevent false drift alerts
        and avoid adapting entity baselines to legitimize cyber attacks.
        """
        state = self._get_or_create_state(entity_id)
        state["total_events"] += 1
        
        ts = timestamp or feature_vector.get("timestamp")
        if ts:
            state["last_timestamp"] = ts

        # Record raw score in general history for backward compatibility
        self.entity_history[entity_id].append(anomaly_score)

        if is_predicted_anomaly:
            state["anomalous_events"] += 1
            # Do NOT add malicious attack events to clean ADWIN behavioral window
            return

        # Process clean, non-anomalous event
        state["clean_events"] += 1
        clean_deque = self.entity_clean_history[entity_id]
        clean_deque.append(anomaly_score)
        state["adaptive_window_size"] = len(clean_deque)

        # Welford's online mean and variance updates for non-anomalous events
        n = state["clean_events"]
        old_mean = state["mean"]
        new_mean = old_mean + (anomaly_score - old_mean) / n
        state["mean"] = new_mean
        
        if n > 1:
            state["variance"] += (anomaly_score - old_mean) * (anomaly_score - new_mean)
        
        # Adaptive Threshold calculation: Tau = mean + 2 * std_dev + sensitivity
        sample_std = math.sqrt(state["variance"] / (n - 1)) if n > 1 else 0.05
        state["adaptive_threshold"] = round(new_mean + 1.5 * sample_std + (self.drift_sensitivity / 2.0), 3)

        # Update Page-Hinkley Cumulative Sum
        delta_ph = 0.05
        dev = anomaly_score - new_mean - delta_ph
        state["ph_cumulative_sum"] += dev
        if state["ph_cumulative_sum"] < state["ph_min_sum"]:
            state["ph_min_sum"] = state["ph_cumulative_sum"]

    def detect_drift(self, entity_id: str) -> bool:
        """
        Evaluates whether entity behavior distribution has drifted using Adaptive Windowing (ADWIN) with
        Hoeffding bounds and Page-Hinkley test.
        Returns True if genuine concept drift is detected.
        """
        state = self._get_or_create_state(entity_id)
        clean_scores = list(self.entity_clean_history.get(entity_id, []))
        n = len(clean_scores)

        # Require minimum window length for robust statistical testing
        if n < self.min_window * 2:
            state["drift_detected"] = False
            state["drift_confidence"] = 0.0
            state["drift_type"] = "none"
            return False

        # 1. ADWIN Hoeffding Cut-Off Evaluation across window partitions
        drift_found = False
        max_dist = 0.0
        best_cut_eps = 0.0
        split_idx = 0

        # Test cut-points in clean scores
        step = max(1, n // 10)
        for cut in range(self.min_window, n - self.min_window + 1, step):
            w0 = clean_scores[:cut]
            w1 = clean_scores[cut:]
            
            n0 = len(w0)
            n1 = len(w1)
            
            mu0 = sum(w0) / float(n0)
            mu1 = sum(w1) / float(n1)
            dist = abs(mu1 - mu0)

            # Harmonic mean of window partition sizes
            m = 1.0 / (1.0 / n0 + 1.0 / n1)
            
            # Hoeffding bound cut-off threshold: epsilon = sqrt((1 / (2*m)) * ln(4*n / delta))
            eps = math.sqrt((1.0 / (2.0 * m)) * math.log((4.0 * n) / self.delta))

            if dist > eps + (self.drift_sensitivity / 2.0):
                drift_found = True
                if dist > max_dist:
                    max_dist = dist
                    best_cut_eps = eps
                    split_idx = cut

        # 2. Page-Hinkley Test for Gradual Drift
        ph_diff = state["ph_cumulative_sum"] - state["ph_min_sum"]
        ph_drift = ph_diff > (self.drift_sensitivity * 1.5)

        if drift_found or ph_drift:
            state["drift_detected"] = True
            state["drift_count"] += 1
            state["last_drift_timestamp"] = state.get("last_timestamp")
            
            # Confidence score C = min(1.0, distance / (epsilon + 1e-5))
            denom = best_cut_eps if best_cut_eps > 0 else self.drift_sensitivity
            conf = min(1.0, max_dist / (denom + 1e-5)) if max_dist > 0 else min(1.0, ph_diff / (self.drift_sensitivity * 1.5))
            state["drift_confidence"] = round(conf, 3)

            # Classify drift type: Abrupt if recent cut is sharp & small, Gradual if PH test or large window
            if split_idx > 0 and (n - split_idx) <= 15 and max_dist > 1.5 * best_cut_eps:
                state["drift_type"] = "abrupt"
            else:
                state["drift_type"] = "gradual"

            logger.info(
                f"Concept Drift detected for {entity_id}! Type: {state['drift_type'].upper()}, "
                f"Confidence: {state['drift_confidence']*100:.1f}%, Window Size: {n}"
            )

            # Shrink ADWIN window by dropping older shifted partition
            if split_idx > 0:
                for _ in range(split_idx):
                    self.entity_clean_history[entity_id].popleft()

            # Reset Page-Hinkley trackers
            state["ph_cumulative_sum"] = 0.0
            state["ph_min_sum"] = float('inf')

            return True

        state["drift_detected"] = False
        state["drift_confidence"] = 0.0
        state["drift_type"] = "none"
        return False

    def adapt_baseline(
        self,
        entity_id: str,
        profile: Dict[str, Any],
        recent_logs: List[Dict[str, Any]],
        learning_rate: float = 0.15
    ) -> Dict[str, Any]:
        """
        Incrementally adapts baseline entity profile using Exponential Moving Averages (EMA) on clean logs.
        Prevents abrupt, fragile min/max overrides by smoothly updating working hours and session durations.
        """
        if not recent_logs or not profile:
            return profile

        # Filter out flagged anomalous logs so attacks do not pollute baseline updates
        clean_logs = [log for log in recent_logs if log.get("label", 0) == 0 and log.get("is_anomaly", 0) == 0]
        if not clean_logs:
            clean_logs = recent_logs  # Fallback if labels not available

        updated = dict(profile)
        recent_hours = [log.get("hour") for log in clean_logs if log.get("hour") is not None]

        if recent_hours:
            rec_min_h = min(recent_hours)
            rec_max_h = max(recent_hours)

            curr_start = profile.get("normal_start_hour", 8)
            curr_end = profile.get("normal_end_hour", 18)

            # EMA Update: start_new = (1 - lr) * start_old + lr * start_recent
            new_start = int(round((1.0 - learning_rate) * curr_start + learning_rate * rec_min_h))
            new_end = int(round((1.0 - learning_rate) * curr_end + learning_rate * rec_max_h))

            updated["normal_start_hour"] = max(0, min(23, new_start))
            updated["normal_end_hour"] = max(0, min(23, new_end))
            updated["is_drift_adapted"] = True
            updated["last_drift_adaptation"] = self._get_or_create_state(entity_id).get("last_timestamp")

            logger.info(
                f"Incrementally adapted baseline hours for {entity_id}: "
                f"[{curr_start}:00-{curr_end}:00] -> [{updated['normal_start_hour']}:00-{updated['normal_end_hour']}:00]"
            )

        return updated

    def get_entity_drift_profile(self, entity_id: str) -> Dict[str, Any]:
        """Returns entity-level drift monitoring state."""
        state = self._get_or_create_state(entity_id)
        sample_std = math.sqrt(state["variance"] / max(1, state["clean_events"] - 1)) if state["clean_events"] > 1 else 0.05
        return {
            "entity_id": entity_id,
            "total_events": state["total_events"],
            "clean_events": state["clean_events"],
            "anomalous_events": state["anomalous_events"],
            "drift_detected": state["drift_detected"],
            "drift_confidence": state["drift_confidence"],
            "drift_type": state["drift_type"],
            "drift_count": state["drift_count"],
            "adaptive_window_size": state["adaptive_window_size"],
            "score_mean": round(state["mean"], 4),
            "score_std": round(sample_std, 4),
            "adaptive_threshold": state["adaptive_threshold"],
            "last_drift_timestamp": state["last_drift_timestamp"]
        }

    def get_drift_analytics_summary(self) -> Dict[str, Any]:
        """Calculates global dataset-level drift statistics for dashboard visualization."""
        if not self.entity_states:
            return {
                "total_entities_monitored": 0,
                "total_drift_events": 0,
                "drift_prevalence_rate": 0.0,
                "drift_type_distribution": {"gradual": 0, "abrupt": 0},
                "avg_adwin_window_size": 0,
                "top_drifted_entities": []
            }

        total_monitored = len(self.entity_states)
        total_drifts = sum(s["drift_count"] for s in self.entity_states.values())
        drifted_entities_count = sum(1 for s in self.entity_states.values() if s["drift_count"] > 0)
        
        gradual_cnt = sum(1 for s in self.entity_states.values() if s["drift_type"] == "gradual")
        abrupt_cnt = sum(1 for s in self.entity_states.values() if s["drift_type"] == "abrupt")

        avg_window = sum(s["adaptive_window_size"] for s in self.entity_states.values()) / float(total_monitored)

        top_entities = sorted(
            [self.get_entity_drift_profile(eid) for eid in self.entity_states],
            key=lambda x: (x["drift_count"], x["drift_confidence"]),
            reverse=True
        )[:10]

        return {
            "total_entities_monitored": total_monitored,
            "total_drift_events": total_drifts,
            "drifted_entities_count": drifted_entities_count,
            "drift_prevalence_rate": round(drifted_entities_count / float(total_monitored), 4) if total_monitored > 0 else 0.0,
            "drift_type_distribution": {"gradual": gradual_cnt, "abrupt": abrupt_cnt},
            "avg_adwin_window_size": round(avg_window, 1),
            "top_drifted_entities": top_entities
        }


if __name__ == "__main__":
    drift = ConceptDriftHandler(window_size=20)
    # Simulate clean stream
    for i in range(25):
        drift.record_event("USR-TEST", {"timestamp": "2026-07-26T10:00:00"}, 0.10, is_predicted_anomaly=False)
    
    print("Initial Drift check:", drift.detect_drift("USR-TEST"))
    
    # Simulate legitimate concept shift
    for i in range(25):
        drift.record_event("USR-TEST", {"timestamp": "2026-07-26T14:00:00"}, 0.45, is_predicted_anomaly=False)
    
    print("Post-shift Drift check:", drift.detect_drift("USR-TEST"))
    print("Entity Drift Profile:", drift.get_entity_drift_profile("USR-TEST"))
