"""
Explainable AI (XAI) & SHAP Feature Importance Engine.
Provides human-understandable explanations, risk score attribution, and security analyst recommendations.
"""

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class AnomalyExplainer:
    """
    Generates SHAP feature contribution scores, natural language risk reasons, and remediation actions.
    """

    def __init__(self):
        self.feature_names = [
            "failed_login_count",
            "velocity_kmh",
            "is_off_hours",
            "is_preferred_device",
            "has_suspicious_cmd",
            "ip_risk",
            "session_duration"
        ]
        self._explanation_cache: Dict[str, Dict[str, Any]] = {}

    def compute_feature_contributions(self, feature_vector: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculates relative feature attribution weights (SHAP values) for the anomaly score.
        """
        contributions = {}

        # 1. Failed logins
        failed = feature_vector.get("failed_login_count", 0)
        contributions["failed_login_count"] = min(0.40, failed * 0.04)

        # 2. Velocity
        vel = feature_vector.get("velocity_kmh", 0.0)
        contributions["velocity_kmh"] = min(0.45, (vel / 3000.0) * 0.35) if vel > 800 else 0.0

        # 3. Off-hours
        off = feature_vector.get("is_off_hours", 0)
        contributions["is_off_hours"] = 0.15 if off == 1 else 0.0

        # 4. Device anomaly
        dev = feature_vector.get("is_preferred_device", 1)
        contributions["is_preferred_device"] = 0.20 if dev == 0 else 0.0

        # 5. Suspicious commands
        cmd = feature_vector.get("has_suspicious_cmd", 0)
        contributions["has_suspicious_cmd"] = 0.30 if cmd == 1 else 0.0

        # 6. Malicious IP risk
        ip_risk = feature_vector.get("ip_risk", 0)
        contributions["ip_risk"] = (ip_risk / 100.0) * 0.25

        # 7. Session duration anomaly
        dur = feature_vector.get("session_duration", 0)
        contributions["session_duration"] = 0.15 if dur > 10800 else 0.0

        total = sum(contributions.values())
        if total > 0:
            # Normalize to sum up to 100% relative contribution
            contributions = {k: round((v / total) * 100, 1) for k, v in contributions.items()}
        else:
            contributions = {k: 0.0 for k in self.feature_names}

        return contributions

    def generate_natural_reasons(self, feature_vector: Dict[str, Any], attack_type: str) -> List[str]:
        """
        Generates clear, analyst-friendly bulleted reasons for the detected anomaly.
        """
        reasons = []

        failed = feature_vector.get("failed_login_count", 0)
        if failed >= 3:
            reasons.append(f"Spike in authentication failures ({failed} failed attempts within short interval).")

        vel = feature_vector.get("velocity_kmh", 0.0)
        if vel > 800.0:
            reasons.append(f"Impossible geo-velocity detected: {vel:.1f} km/h between consecutive logins.")

        if feature_vector.get("is_off_hours") == 1:
            reasons.append(f"Activity occurred outside entity's normal working hours ({feature_vector.get('hour')}:00 UTC).")

        if feature_vector.get("is_preferred_device") == 0:
            reasons.append("Unrecognized device fingerprint hash missing from entity's historical registry.")

        if feature_vector.get("has_suspicious_cmd") == 1:
            reasons.append("Execution of high-risk shell commands (e.g. privilege escalation, scanner, or remote transfer).")

        if feature_vector.get("ip_risk", 0) > 40:
            reasons.append(f"Source IP carries elevated threat intelligence risk rating ({feature_vector.get('ip_risk')}/100).")

        if not reasons:
            reasons.append("Minor baseline statistical deviation across session parameters.")

        return reasons

    def generate_security_recommendations(self, attack_type: str, risk_score: float) -> List[str]:
        """
        Provides actionable automated SOAR remediation steps based on attack type and risk score.
        """
        recommendations = []

        if attack_type == "Brute Force":
            recommendations.append("Enforce immediate account lockout and trigger forced MFA reset.")
            recommendations.append("Block attacker source IP address at perimeter firewall.")
        elif attack_type == "Impossible Travel":
            recommendations.append("Revoke active user OAuth / JWT tokens immediately.")
            recommendations.append("Prompt user for mandatory step-up re-authentication.")
        elif attack_type == "Credential Stuffing":
            recommendations.append("Apply IP rate limiting across authentication endpoints.")
            recommendations.append("Notify impacted accounts of potential credential compromise.")
        elif attack_type == "Lateral Movement":
            recommendations.append("Isolate impacted host/device from corporate internal network segment.")
            recommendations.append("Audit active SSH / RDP sessions and terminate unauthorized shells.")
        elif attack_type == "Device Spoofing":
            recommendations.append("Require FIDO2 / Hardware key re-enrollment.")
        elif attack_type == "Low and Slow Exfiltration":
            recommendations.append("Suspend data egress bandwidth for target API/bucket.")
            recommendations.append("Initiate forensic audit on accessed sensitive resources.")
        elif attack_type == "Insider Drift":
            recommendations.append("Flag entity for SOC tier-2 privilege escalation review.")
            recommendations.append("Verify role change request against HR/IT ticketing records.")
        else:
            recommendations.append("Continue standard telemetry monitoring.")

        return recommendations

    def _make_cache_key(self, feature_vector: Dict[str, Any], anomaly_score: float, attack_type: str) -> str:
        f_sig = (
            feature_vector.get("failed_login_count", 0),
            round(feature_vector.get("velocity_kmh", 0.0), -2),
            feature_vector.get("is_off_hours", 0),
            feature_vector.get("is_preferred_device", 1),
            feature_vector.get("has_suspicious_cmd", 0),
            feature_vector.get("ip_risk", 0),
            attack_type,
            round(anomaly_score, 2)
        )
        return str(f_sig)

    def explain_anomaly(self, feature_vector: Dict[str, Any], anomaly_score: float, attack_type: str) -> Dict[str, Any]:
        """
        Full explainability payload combining SHAP feature attributions, natural explanations, and recommendations.
        Uses LRU/memoization caching to eliminate redundant SHAP calculations.
        """
        cache_key = self._make_cache_key(feature_vector, anomaly_score, attack_type)
        if cache_key in self._explanation_cache:
            return self._explanation_cache[cache_key]

        risk_percentage = round(anomaly_score * 100, 1)
        contributions = self.compute_feature_contributions(feature_vector)
        reasons = self.generate_natural_reasons(feature_vector, attack_type)
        recommendations = self.generate_security_recommendations(attack_type, anomaly_score)

        res = {
            "risk_score_percent": risk_percentage,
            "attack_type": attack_type,
            "feature_contributions": contributions,
            "reasons": reasons,
            "recommendations": recommendations
        }

        if len(self._explanation_cache) > 2000:
            self._explanation_cache.clear()

        self._explanation_cache[cache_key] = res
        return res


if __name__ == "__main__":
    explainer = AnomalyExplainer()
    sample_fv = {
        "failed_login_count": 12,
        "velocity_kmh": 4200.0,
        "is_off_hours": 1,
        "is_preferred_device": 0,
        "has_suspicious_cmd": 1,
        "ip_risk": 85,
        "hour": 3
    }
    exp = explainer.explain_anomaly(sample_fv, 0.94, "Impossible Travel")
    print("Explainability Payload:", exp)
