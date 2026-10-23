export type UserRole = 'renter' | 'host' | 'admin';

export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  preferred_budget?: number;
  preferred_amenities: string[];
  created_at: string;
}

export interface Property {
  id: number;
  host_id: number;
  title: string;
  description: string;
  property_type: string;
  neighbourhood: string;
  latitude: number;
  longitude: number;
  public_location_description: string;
  exact_address?: string | null;
  price_per_hour: number;
  price_per_half_day: number;
  price_per_day: number;
  maximum_guests: number;
  amenities: string[];
  supported_durations: string[];
  house_rules: string;
  images: string[];
  active: boolean;
  average_rating: number;
  review_count: number;
  created_at: string;
  host_name?: string;
}

export type BookingStatus = 'PENDING' | 'CONFIRMED' | 'REJECTED' | 'CANCELLED' | 'COMPLETED';

export interface Booking {
  id: number;
  renter_id: number;
  property_id: number;
  start_datetime: string;
  end_datetime: string;
  duration_type: string;
  guest_count: number;
  base_price: number;
  fees: number;
  total_price: number;
  status: BookingStatus;
  payment_status: string;
  created_at: string;
  property_title?: string;
  property_neighbourhood?: string;
  property_image?: string;
  exact_address?: string | null;
  renter_name?: string;
}

export interface Review {
  id: number;
  booking_id: number;
  renter_id: number;
  property_id: number;
  rating: number;
  review_text: string;
  created_at: string;
  renter_name?: string;
}

export interface RecommendationItem {
  property: Property;
  score: number;
  component_scores: Record<string, number>;
  straight_line_distance_km?: number | null;
  calculated_price: number;
  explanations: string[];
  match_badges: string[];
}

export interface RecommendationResponse {
  session_id: string;
  model_version: string;
  model_type: string;
  count: number;
  results: RecommendationItem[];
  relaxed_filter_suggestions?: string[] | null;
}

export interface NeighbourhoodDemandItem {
  neighbourhood: string;
  target_date: string;
  time_slot: 'morning' | 'afternoon' | 'evening' | 'night';
  predicted_demand_score: number;
  predicted_booking_requests: number;
  historical_avg_requests: number;
  confidence_interval_low: number;
  confidence_interval_high: number;
  demand_level: 'Low' | 'Moderate' | 'High' | 'Very High';
}

export interface DemandAnalyticsResponse {
  forecasts: NeighbourhoodDemandItem[];
  model_version: string;
  mae: number;
  rmse: number;
  data_freshness: string;
  data_source_note: string;
}

export interface HostAnalyticsResponse {
  total_listings: number;
  total_bookings: number;
  total_revenue: number;
  occupancy_rate: number;
  pending_requests_count: number;
  neighbourhood_demand_summary: NeighbourhoodDemandItem[];
}

export interface ModelRegistryInfo {
  version: string;
  model_type: string;
  artifact_path: string;
  run_id?: string;
  metrics: Record<string, number>;
  status: string;
  activated_at?: string;
}

export interface MLStatusResponse {
  active_models: Record<string, ModelRegistryInfo>;
  candidates: Record<string, ModelRegistryInfo>;
  history: ModelRegistryInfo[];
}

export interface DriftReport {
  feature_drifts: Record<string, {
    psi: number;
    status: string;
    ref_mean: number;
    cur_mean: number;
    ref_std: number;
    cur_std: number;
  }>;
  overall_drift_detected: boolean;
  psi_scores: Record<string, number>;
  recommendation_feedback_drift: Record<string, number>;
  reference_data_size: number;
  current_data_size: number;
  timestamp: string;
  alert_message?: string;
}
