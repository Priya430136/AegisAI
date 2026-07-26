export interface ConfusionMatrix {
  true_positives: number;
  false_positives: number;
  true_negatives: number;
  false_negatives: number;
}

export interface Metrics {
  dataset_size: number;
  total_anomalies_detected: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  false_positive_rate: number;
  confusion_matrix: ConfusionMatrix;
  attack_distribution: Record<string, number>;
  timestamp?: string;
  concept_drift_summary?: {
    total_entities_monitored: number;
    total_drift_events: number;
    drifted_entities_count: number;
    drift_prevalence_rate: number;
    drift_type_distribution: { gradual: number; abrupt: number };
    avg_adwin_window_size: number;
    top_drifted_entities: Array<{
      entity_id: string;
      drift_confidence: number;
      drift_type: string;
      drift_count: number;
      adaptive_window_size: number;
      score_mean: number;
      adaptive_threshold: number;
    }>;
  };
}

export interface Explanation {
  risk_score_percent: number;
  attack_type: string;
  feature_contributions: Record<string, number>;
  reasons: string[];
  recommendations: string[];
}

export interface AnomalyIncident {
  event_index: number;
  entity_id: string;
  timestamp: string;
  risk_score: number;
  predicted_attack: string;
  confidence: number;
  true_attack?: string;
  explanation: Explanation;
}

export interface EntityProfile {
  entity_id: string;
  entity_type: string;
  home_geo: {
    city: string;
    country: string;
    lat: number;
    lon: number;
    ip_prefix: string;
  };
  normal_start_hour: number;
  normal_end_hour: number;
  preferred_device: string;
  preferred_auth: string;
  common_resources: string[];
  avg_session_duration: number;
  is_vip_privilege: boolean;
  drift_profile?: {
    drift_detected: boolean;
    drift_confidence: number;
    drift_type: string;
    drift_count: number;
    adaptive_window_size: number;
    score_mean: number;
    adaptive_threshold: number;
  };
}
