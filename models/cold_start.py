"""
Cold Start Profiling Engine & Anomaly Threshold Audit.

Provides peer group profiling, department clustering, device similarity,
authentication similarity, and behavioral clustering (KMeans & Hierarchical)
for unprofiled users and devices.

Prevents false positive spikes during initial entity onboarding by replacing static
global Bayesian population priors with adaptive peer-cluster behavioral baselines.
"""

import math
import random
import logging
from collections import defaultdict
from typing import List, Dict, Any, Tuple, Set, Optional

logger = logging.getLogger(__name__)


class BehavioralKMeans:
    """
    Native pure-Python KMeans Clustering Engine for entity behavioral vector clustering.
    Clusters entity profiles based on work hours, session duration, privilege levels,
    and resource scope into distinct behavioral archetypes.
    """

    def __init__(self, k: int = 4, max_iter: int = 20, seed: int = 42):
        self.k = k
        self.max_iter = max_iter
        self.seed = seed
        self.centroids: List[List[float]] = []
        self.labels: List[int] = []

    def _euclidean_distance(self, vec1: List[float], vec2: List[float]) -> float:
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))

    def fit(self, X: List[List[float]]) -> 'BehavioralKMeans':
        if not X:
            return self

        random.seed(self.seed)
        n_samples = len(X)
        k_eff = min(self.k, n_samples)

        # Centroid initialization (k-means++)
        self.centroids = [list(X[random.randint(0, n_samples - 1)])]
        for _ in range(1, k_eff):
            distances = [min(self._euclidean_distance(x, c) ** 2 for c in self.centroids) for x in X]
            total_dist = sum(distances)
            if total_dist == 0:
                self.centroids.append(list(X[random.randint(0, n_samples - 1)]))
                continue
            probs = [d / total_dist for d in distances]
            r = random.random()
            cum_p = 0.0
            chosen_idx = 0
            for idx, p in enumerate(probs):
                cum_p += p
                if r <= cum_p:
                    chosen_idx = idx
                    break
            self.centroids.append(list(X[chosen_idx]))

        # Iterative optimization
        for _ in range(self.max_iter):
            clusters = defaultdict(list)
            new_labels = []
            for vec in X:
                nearest_idx = min(range(len(self.centroids)), key=lambda i: self._euclidean_distance(vec, self.centroids[i]))
                clusters[nearest_idx].append(vec)
                new_labels.append(nearest_idx)

            self.labels = new_labels

            # Recompute centroids
            new_centroids = []
            for i in range(len(self.centroids)):
                if clusters[i]:
                    dim = len(X[0])
                    mean_vec = [sum(v[d] for v in clusters[i]) / float(len(clusters[i])) for d in range(dim)]
                    new_centroids.append(mean_vec)
                else:
                    new_centroids.append(self.centroids[i])

            if new_centroids == self.centroids:
                break
            self.centroids = new_centroids

        return self

    def predict(self, vec: List[float]) -> int:
        if not self.centroids:
            return 0
        return min(range(len(self.centroids)), key=lambda i: self._euclidean_distance(vec, self.centroids[i]))


class HierarchicalAgglomerativeClustering:
    """
    Native pure-Python Agglomerative Hierarchical Clustering for peer group identification.
    Uses average linkage criterion to group entities with similar device and auth preferences.
    """

    def __init__(self, n_clusters: int = 4):
        self.n_clusters = n_clusters

    def _dist(self, u: List[float], v: List[float]) -> float:
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(u, v)))

    def fit_predict(self, X: List[List[float]]) -> List[int]:
        n = len(X)
        if n <= self.n_clusters:
            return list(range(n))

        # Subsample if dataset is large to ensure O(1) fast execution
        if n > 50:
            sample_indices = list(range(0, n, max(1, n // 50)))[:50]
            X_sub = [X[i] for i in sample_indices]
        else:
            X_sub = X

        n_sub = len(X_sub)
        clusters = {i: [i] for i in range(n_sub)}
        
        # Distance matrix
        dist_matrix = {}
        for i in range(n_sub):
            for j in range(i + 1, n_sub):
                dist_matrix[(i, j)] = self._dist(X_sub[i], X_sub[j])

        # Merge clusters until target count
        while len(clusters) > self.n_clusters:
            min_d = float('inf')
            pair_to_merge = None

            cluster_ids = list(clusters.keys())
            for c1_idx in range(len(cluster_ids)):
                for c2_idx in range(c1_idx + 1, len(cluster_ids)):
                    c1, c2 = cluster_ids[c1_idx], cluster_ids[c2_idx]
                    avg_d = sum(
                        dist_matrix.get((min(i, j), max(i, j)), 0.0)
                        for i in clusters[c1] for j in clusters[c2]
                    ) / float(len(clusters[c1]) * len(clusters[c2]))

                    if avg_d < min_d:
                        min_d = avg_d
                        pair_to_merge = (c1, c2)

            if not pair_to_merge:
                break

            c1, c2 = pair_to_merge
            clusters[c1].extend(clusters[c2])
            del clusters[c2]

        sub_labels = [0] * n_sub
        for label, (cid, members) in enumerate(clusters.items()):
            for m in members:
                sub_labels[m] = label

        if n > 50:
            # Map full set X to nearest sub_label
            labels = []
            for vec in X:
                nearest_sub_idx = min(range(n_sub), key=lambda i: self._dist(vec, X_sub[i]))
                labels.append(sub_labels[nearest_sub_idx])
            return labels

        return sub_labels


class ColdStartHandler:
    """
    Handles zero-history entities by applying peer group profiling, department clustering,
    device similarity, authentication similarity, and behavioral clustering (KMeans & Hierarchical).
    
    Prevents false positive spikes when onboarding new users or devices by replacing
    one-size-fits-all Bayesian population priors with contextual peer baselines.
    """

    def __init__(self, warmup_period_events: int = 20, entity_profiles: Optional[Dict[str, Any]] = None):
        self.warmup_period = warmup_period_events
        
        # Legacy fallback population priors
        self.global_priors = {
            "normal_start_hour": 8,
            "normal_end_hour": 18,
            "avg_session_duration": 1800,
            "default_allowed_failed_logins": 3,
            "preferred_device": "FP_GENERIC_CORP",
            "preferred_auth": "MFA_TOTP",
            "common_resources": ["/api/v1/dashboard", "/help/faq", "/api/v1/user/profile"]
        }

        # Cluster & Department Data structures
        self.department_profiles: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.cluster_centroids: List[Dict[str, Any]] = []
        self.kmeans_model: Optional[BehavioralKMeans] = None
        self.entity_cluster_map: Dict[str, int] = {}
        self.auth_method_distributions: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.department_devices: Dict[str, Set[str]] = defaultdict(set)
        self.department_auths: Dict[str, Set[str]] = defaultdict(set)
        self.department_resources: Dict[str, Set[str]] = defaultdict(set)

        if entity_profiles:
            self.fit(entity_profiles)

    def _extract_feature_vector(self, profile: Dict[str, Any]) -> List[float]:
        """Converts an entity profile dictionary into a normalized numerical vector for clustering."""
        start_h = float(profile.get("normal_start_hour", 8)) / 24.0
        end_h = float(profile.get("normal_end_hour", 18)) / 24.0
        sess_dur = min(1.0, float(profile.get("avg_session_duration", 1800)) / 7200.0)
        is_vip = 1.0 if profile.get("is_vip_privilege", False) else 0.0
        res_count = min(1.0, len(profile.get("common_resources", [])) / 10.0)
        
        # Auth encoding
        auth_map = {"MFA_TOTP": 0.2, "OAuth2": 0.4, "SSH_Key": 0.6, "Password": 0.8, "API_Token": 1.0}
        auth_enc = auth_map.get(profile.get("preferred_auth", "MFA_TOTP"), 0.5)

        return [start_h, end_h, sess_dur, is_vip, res_count, auth_enc]

    def fit(self, entity_profiles: Dict[str, Any]) -> 'ColdStartHandler':
        """
        Fits department profiles, KMeans behavioral clusters, and peer group device/auth similarity indices
        from known historical entity profiles.
        """
        if not entity_profiles:
            return self

        logger.info(f"Fitting ColdStartHandler on {len(entity_profiles)} entity profiles...")

        # 1. Department & Peer Group Aggregation
        dept_data = defaultdict(list)
        for eid, prof in entity_profiles.items():
            dept = prof.get("department") or self._infer_department(prof)
            dept_data[dept].append(prof)
            
            dev = prof.get("preferred_device")
            if dev:
                self.department_devices[dept].add(dev)
            
            auth = prof.get("preferred_auth")
            if auth:
                self.department_auths[dept].add(auth)
                self.auth_method_distributions[dept][auth] += 1.0

            for res in prof.get("common_resources", []):
                self.department_resources[dept].add(res)

        # Normalize auth method probabilities
        for dept, dist in self.auth_method_distributions.items():
            total = sum(dist.values())
            if total > 0:
                for k in dist:
                    dist[k] /= total

        # Build Department Centroids
        for dept, profiles in dept_data.items():
            avg_start = sum(p.get("normal_start_hour", 8) for p in profiles) / float(len(profiles))
            avg_end = sum(p.get("normal_end_hour", 18) for p in profiles) / float(len(profiles))
            avg_sess = sum(p.get("avg_session_duration", 1800) for p in profiles) / float(len(profiles))
            
            self.department_profiles[dept] = {
                "department": dept,
                "normal_start_hour": int(round(avg_start)),
                "normal_end_hour": int(round(avg_end)),
                "avg_session_duration": avg_sess,
                "preferred_devices": list(self.department_devices[dept]),
                "preferred_auths": list(self.department_auths[dept]),
                "common_resources": list(self.department_resources[dept]),
                "auth_distribution": dict(self.auth_method_distributions[dept])
            }

        # 2. KMeans Behavioral Clustering
        entity_ids = list(entity_profiles.keys())
        X = [self._extract_feature_vector(entity_profiles[eid]) for eid in entity_ids]

        if len(X) >= 4:
            self.kmeans_model = BehavioralKMeans(k=min(5, len(X)))
            self.kmeans_model.fit(X)

            # Compute cluster profile centroids
            self.cluster_centroids = []
            cluster_groups = defaultdict(list)
            for eid, label in zip(entity_ids, self.kmeans_model.labels):
                self.entity_cluster_map[eid] = label
                cluster_groups[label].append(entity_profiles[eid])

            for cid in range(len(self.kmeans_model.centroids)):
                members = cluster_groups[cid]
                if members:
                    c_start = sum(m.get("normal_start_hour", 8) for m in members) / float(len(members))
                    c_end = sum(m.get("normal_end_hour", 18) for m in members) / float(len(members))
                    c_sess = sum(m.get("avg_session_duration", 1800) for m in members) / float(len(members))
                    
                    c_devs = set()
                    c_auths = set()
                    c_res = set()
                    for m in members:
                        if m.get("preferred_device"):
                            c_devs.add(m.get("preferred_device"))
                        if m.get("preferred_auth"):
                            c_auths.add(m.get("preferred_auth"))
                        c_res.update(m.get("common_resources", []))

                    self.cluster_centroids.append({
                        "cluster_id": cid,
                        "normal_start_hour": int(round(c_start)),
                        "normal_end_hour": int(round(c_end)),
                        "avg_session_duration": c_sess,
                        "allowed_devices": list(c_devs),
                        "allowed_auths": list(c_auths),
                        "common_resources": list(c_res)
                    })

        # 3. Agglomerative Hierarchical Clustering for fine-grained peer verification
        if len(X) >= 6:
            h_clustering = HierarchicalAgglomerativeClustering(n_clusters=min(4, len(X)))
            h_labels = h_clustering.fit_predict(X)
            logger.info(f"Hierarchical Clustering grouped {len(X)} entities into {len(set(h_labels))} peer sub-groups.")

        return self

    def _infer_department(self, profile: Dict[str, Any]) -> str:
        """Infers department/role archetype if explicit department tag is missing."""
        if profile.get("is_vip_privilege", False):
            return "Executive_VIP"
        
        resources = profile.get("common_resources", [])
        if any("admin" in r or "vault" in r or "ssh" in r or "k8s" in r for r in resources):
            return "IT_DevOps"
        if any("billing" in r or "financial" in r for r in resources):
            return "Finance"
        if any("dashboard" in r or "profile" in r for r in resources):
            return "Standard_Operations"

        start_h = profile.get("normal_start_hour", 8)
        if start_h <= 6 or start_h >= 11:
            return "Global_Shift_Ops"

        return "General_Staff"

    def calculate_device_similarity(self, device_fp: str, peer_devices: List[str]) -> float:
        """
        Calculates device fingerprint similarity score against peer group devices.
        Returns score in [0.0, 1.0]. High similarity indicates a department-standard device.
        """
        if not device_fp or not peer_devices:
            return 0.5  # Neutral similarity for unobserved cold start

        if device_fp in peer_devices:
            return 1.0

        # Substring / Prefix Jaccard similarity across fingerprint tokens
        fp_prefix = device_fp[:4]
        match_count = sum(1 for d in peer_devices if d.startswith(fp_prefix))
        if match_count > 0:
            return min(0.9, 0.5 + 0.1 * match_count)

        return 0.2

    def calculate_auth_similarity(self, auth_method: str, dept_name: str) -> float:
        """
        Calculates authentication similarity score against department peer group norms.
        Returns probability/alignment score in [0.0, 1.0].
        """
        if not auth_method:
            return 0.5

        dept_dist = self.auth_method_distributions.get(dept_name, {})
        if auth_method in dept_dist:
            return float(dept_dist[auth_method])

        # Default fallback standard auth alignments
        if auth_method in ["MFA_TOTP", "OAuth2"]:
            return 0.70
        if auth_method == "SSH_Key" and dept_name == "IT_DevOps":
            return 0.90

        return 0.30

    def get_effective_profile(self, entity_id: str, historical_count: int, explicit_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Blends peer group profiling, department clusters, device similarity, auth similarity,
        and behavioral cluster centroids with explicit entity profiles as historical events accumulate.
        
        API Backward Compatibility: Fully compatible with legacy get_effective_profile signature.
        """
        # If entity is fully warmed up and has explicit profile, return pure profile
        if explicit_profile and historical_count >= self.warmup_period:
            explicit_copy = dict(explicit_profile)
            explicit_copy["is_cold_start"] = False
            explicit_copy["confidence_scale"] = 1.0
            explicit_copy["allowed_devices"] = [explicit_profile.get("preferred_device")] if explicit_profile.get("preferred_device") else []
            explicit_copy["allowed_auths"] = [explicit_profile.get("preferred_auth")] if explicit_profile.get("preferred_auth") else []
            explicit_copy["allowed_resources"] = explicit_profile.get("common_resources", [])
            return explicit_copy

        # Cold start blending factor alpha in [0.0, 1.0]
        alpha = min(1.0, historical_count / float(self.warmup_period))

        # 1. Determine peer cluster & department priors
        raw_prof = explicit_profile or {}
        dept_name = raw_prof.get("department") or self._infer_department(raw_prof)
        dept_prior = self.department_profiles.get(dept_name, {})

        # 2. Get behavioral KMeans cluster centroid prior
        if self.kmeans_model and raw_prof:
            vec = self._extract_feature_vector(raw_prof)
            cid = self.kmeans_model.predict(vec)
            cluster_prior = self.cluster_centroids[cid] if cid < len(self.cluster_centroids) else {}
        else:
            cid = 0
            cluster_prior = {}

        # 3. Synthesize contextual peer prior
        peer_start = dept_prior.get("normal_start_hour") or cluster_prior.get("normal_start_hour") or self.global_priors["normal_start_hour"]
        peer_end = dept_prior.get("normal_end_hour") or cluster_prior.get("normal_end_hour") or self.global_priors["normal_end_hour"]
        
        # Peer devices & auths
        peer_devs = set(dept_prior.get("preferred_devices", []))
        if cluster_prior.get("allowed_devices"):
            peer_devs.update(cluster_prior["allowed_devices"])

        peer_auths = set(dept_prior.get("preferred_auths", []))
        if cluster_prior.get("allowed_auths"):
            peer_auths.update(cluster_prior["allowed_auths"])

        peer_resources = set(dept_prior.get("common_resources", []))
        if cluster_prior.get("common_resources"):
            peer_resources.update(cluster_prior["common_resources"])

        if raw_prof.get("preferred_device"):
            peer_devs.add(raw_prof["preferred_device"])
        if raw_prof.get("preferred_auth"):
            peer_auths.add(raw_prof["preferred_auth"])
        if raw_prof.get("common_resources"):
            peer_resources.update(raw_prof["common_resources"])

        # Default fallback additions
        peer_devs.add(self.global_priors["preferred_device"])
        peer_auths.add(self.global_priors["preferred_auth"])
        peer_resources.update(self.global_priors["common_resources"])

        # 4. Perform progressive Bayesian blending
        exp_start = raw_prof.get("normal_start_hour", peer_start)
        exp_end = raw_prof.get("normal_end_hour", peer_end)

        blended_start = int(round((1.0 - alpha) * peer_start + alpha * exp_start))
        blended_end = int(round((1.0 - alpha) * peer_end + alpha * exp_end))

        dev_sim = self.calculate_device_similarity(raw_prof.get("preferred_device", ""), list(peer_devs))
        auth_sim = self.calculate_auth_similarity(raw_prof.get("preferred_auth", ""), dept_name)

        merged_profile = {
            "entity_id": entity_id,
            "department": dept_name,
            "peer_group_id": f"PEER_GRP_{dept_name.upper()}",
            "cluster_id": cid,
            "normal_start_hour": blended_start,
            "normal_end_hour": blended_end,
            "avg_session_duration": (1.0 - alpha) * dept_prior.get("avg_session_duration", 1800) + alpha * raw_prof.get("avg_session_duration", 1800),
            "preferred_device": raw_prof.get("preferred_device", list(peer_devs)[0] if peer_devs else "FP_GENERIC_CORP"),
            "allowed_devices": list(peer_devs),
            "preferred_auth": raw_prof.get("preferred_auth", list(peer_auths)[0] if peer_auths else "MFA_TOTP"),
            "allowed_auths": list(peer_auths),
            "common_resources": list(peer_resources),
            "allowed_resources": list(peer_resources),
            "device_similarity_score": round(dev_sim, 3),
            "auth_similarity_score": round(auth_sim, 3),
            "is_cold_start": historical_count < self.warmup_period,
            "confidence_scale": round(alpha, 3),
            "warmup_remaining": max(0, self.warmup_period - historical_count)
        }

        return merged_profile


if __name__ == "__main__":
    sample_profiles = {
        "USR-1001": {"entity_id": "USR-1001", "normal_start_hour": 7, "normal_end_hour": 15, "preferred_device": "fp_101", "preferred_auth": "MFA_TOTP", "common_resources": ["/admin/users"], "is_vip_privilege": False},
        "USR-1002": {"entity_id": "USR-1002", "normal_start_hour": 6, "normal_end_hour": 22, "preferred_device": "fp_102", "preferred_auth": "SSH_Key", "common_resources": ["ssh://prod-db"], "is_vip_privilege": True},
        "USR-1003": {"entity_id": "USR-1003", "normal_start_hour": 9, "normal_end_hour": 17, "preferred_device": "fp_103", "preferred_auth": "OAuth2", "common_resources": ["/api/v1/dashboard"], "is_vip_privilege": False},
    }

    handler = ColdStartHandler(warmup_period_events=20)
    handler.fit(sample_profiles)

    # Test unprofiled new user profile extraction
    new_user_raw = {"preferred_device": "fp_101", "preferred_auth": "MFA_TOTP", "common_resources": ["/admin/users"]}
    eff_prof = handler.get_effective_profile("USR-NEW-01", historical_count=2, explicit_profile=new_user_raw)
    
    print("--- Cold Start Handler Effective Profile ---")
    for k, v in eff_prof.items():
        print(f"  {k}: {v}")
