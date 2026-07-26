"""
Data Preprocessing and Feature Engineering Engine for Behavioral Anomaly Detection.
Transforms raw sequential access logs into numerical feature vectors and sequential tensors.
"""

import math
import logging
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the great-circle distance between two points on the Earth in kilometers.
    """
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


class LogPreprocessor:
    """
    Preprocesses raw sequential log events and extracts behavioral risk features.
    """

    def __init__(self, sequence_length: int = 5):
        self.sequence_length = sequence_length
        self.last_entity_event: Dict[str, Dict[str, Any]] = {}
        self.ip_reputation_db: Dict[str, int] = {
            "185.220.101.5": 90,
            "45.142.120.12": 85,
            "103.251.140.8": 70
        }

    def extract_features_from_event(self, event: Dict[str, Any], profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Engineers numerical & categorical features from a single event log.
        """
        entity_id = event.get("entity_id", "UNKNOWN")
        dt = datetime.fromisoformat(event.get("timestamp", datetime.now().isoformat()))
        
        hour = dt.hour
        day_of_week = dt.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0

        # Off-hours and peer-group device/auth/resource alignment calculation
        if profile:
            start_h = profile.get("normal_start_hour", 8)
            end_h = profile.get("normal_end_hour", 18)
            is_off_hours = 1 if (hour < start_h or hour > end_h) else 0

            dev_fp = event.get("device_fingerprint")
            pref_dev = profile.get("preferred_device")
            allowed_devs = profile.get("allowed_devices", [pref_dev] if pref_dev else [])
            is_preferred_device = 1 if (dev_fp == pref_dev or dev_fp in allowed_devs) else 0

            auth_method = event.get("authentication_method")
            pref_auth = profile.get("preferred_auth")
            allowed_auths = profile.get("allowed_auths", [pref_auth] if pref_auth else [])
            is_preferred_auth = 1 if (auth_method == pref_auth or auth_method in allowed_auths) else 0

            res_accessed = event.get("resource_accessed")
            common_res = profile.get("common_resources", [])
            allowed_res = profile.get("allowed_resources", common_res)
            is_preferred_resource = 1 if (res_accessed in common_res or res_accessed in allowed_res) else 0
        else:
            is_off_hours = 1 if (hour < 7 or hour > 19) else 0
            is_preferred_device = 0
            is_preferred_auth = 0
            is_preferred_resource = 0

        # Geo Velocity Calculation (Impossible Travel)
        lat = float(event.get("latitude", 0.0))
        lon = float(event.get("longitude", 0.0))
        velocity_kmh = 0.0
        time_delta_sec = 0.0

        if entity_id in self.last_entity_event:
            prev_event = self.last_entity_event[entity_id]
            prev_dt = datetime.fromisoformat(prev_event["timestamp"])
            time_delta_sec = max(1.0, (dt - prev_dt).total_seconds())
            dist_km = haversine_distance(prev_event["latitude"], prev_event["longitude"], lat, lon)
            velocity_kmh = (dist_km / (time_delta_sec / 3600.0))
        
        # Update last state
        self.last_entity_event[entity_id] = {
            "timestamp": event.get("timestamp"),
            "latitude": lat,
            "longitude": lon
        }

        # Session & command complexity
        session_dur = float(event.get("session_duration", 0))
        cmd_seq = event.get("command_sequence", [])
        cmd_count = len(cmd_seq)
        cmd_length = sum(len(c) for c in cmd_seq)
        has_suspicious_cmd = 1 if any("sudo" in c or "nmap" in c or "scp" in c or "chmod" in c for c in cmd_seq) else 0

        # Failed login count
        failed_logins = int(event.get("failed_login_count", 0))

        # Risk signals summary
        ip_risk = self.ip_reputation_db.get(event.get("source_ip", ""), 0)

        # Engineered Interaction & Normalized Rate Features
        time_min = max(0.1, time_delta_sec / 60.0) if time_delta_sec > 0 else 1.0
        failed_login_intensity = min(10.0, failed_logins / time_min)
        velocity_anomaly_score = min(1.0, velocity_kmh / 1000.0)
        off_hours_command_risk = float(is_off_hours * has_suspicious_cmd)
        unrecognized_device_risk = float((1 - is_preferred_device) * (1 if ip_risk > 30 else 0))

        feature_vector = {
            "entity_id": entity_id,
            "timestamp": event.get("timestamp"),
            "hour": hour,
            "day_of_week": day_of_week,
            "is_weekend": is_weekend,
            "is_off_hours": is_off_hours,
            "is_preferred_device": is_preferred_device,
            "is_preferred_auth": is_preferred_auth,
            "is_preferred_resource": is_preferred_resource,
            "velocity_kmh": min(velocity_kmh, 15000.0), # cap max velocity
            "time_delta_sec": time_delta_sec,
            "session_duration": session_dur,
            "cmd_count": cmd_count,
            "cmd_length": cmd_length,
            "has_suspicious_cmd": has_suspicious_cmd,
            "failed_login_count": failed_logins,
            "ip_risk": ip_risk,
            "failed_login_intensity": round(failed_login_intensity, 3),
            "velocity_anomaly_score": round(velocity_anomaly_score, 3),
            "off_hours_command_risk": round(off_hours_command_risk, 3),
            "unrecognized_device_risk": round(unrecognized_device_risk, 3),
            "label": event.get("label", 0),
            "attack_type": event.get("attack_type", "Normal")
        }

        return feature_vector

    def process_dataset(self, events: List[Dict[str, Any]], profiles: Dict[str, Dict[str, Any]] = None, cold_start_handler: Any = None) -> List[Dict[str, Any]]:
        """
        Processes a list of event logs into feature vectors, applying progressive cold-start blending.
        """
        processed_data = []
        profiles = profiles or {}
        entity_history_counts: Dict[str, int] = defaultdict(int)

        for ev in events:
            entity_id = ev.get("entity_id", "UNKNOWN")
            raw_prof = profiles.get(entity_id)

            if cold_start_handler:
                h_count = entity_history_counts[entity_id]
                effective_prof = cold_start_handler.get_effective_profile(entity_id, h_count, raw_prof)
                entity_history_counts[entity_id] += 1
            else:
                effective_prof = raw_prof

            fv = self.extract_features_from_event(ev, effective_prof)
            processed_data.append(fv)

        return processed_data


if __name__ == "__main__":
    prep = LogPreprocessor()
    sample_event = {
        "entity_id": "USR-1001",
        "timestamp": "2026-07-26T03:00:00",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "source_ip": "185.220.101.5",
        "session_duration": 300,
        "command_sequence": ["sudo -i"],
        "failed_login_count": 5
    }
    features = prep.extract_features_from_event(sample_event)
    print("Extracted Features Sample:", features)
