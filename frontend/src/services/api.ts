import { 
  Property, Booking, Review, RecommendationResponse, 
  DemandAnalyticsResponse, HostAnalyticsResponse, 
  MLStatusResponse, DriftReport, User 
} from '../types';

const API_BASE = '/api/v1';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('staynearby_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = 'Request failed';
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || JSON.stringify(errJson);
    } catch {
      errorDetail = await response.text() || response.statusText;
    }
    throw new Error(errorDetail);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const api = {
  // Auth
  register: (data: any) => request<{ access_token: string; user: User }>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  login: (data: any) => request<{ access_token: string; user: User }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  getMe: () => request<User>('/auth/me'),
  updateProfile: (data: Partial<User>) => request<User>('/auth/me', {
    method: 'PATCH',
    body: JSON.stringify(data),
  }),

  // Properties
  getProperties: (params?: Record<string, any>) => {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, val]) => {
        if (val !== undefined && val !== null && val !== '') {
          searchParams.append(key, String(val));
        }
      });
    }
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return request<Property[]>(`/properties${query}`);
  },
  getProperty: (id: number) => request<Property>(`/properties/${id}`),
  createProperty: (data: any) => request<Property>('/properties', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  updateProperty: (id: number, data: any) => request<Property>(`/properties/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  }),
  deleteProperty: (id: number) => request<void>(`/properties/${id}`, {
    method: 'DELETE',
  }),

  // Recommendations
  getRecommendations: (data: any) => request<RecommendationResponse>('/recommendations', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  sendRecommendationFeedback: (data: { session_id: string; property_id: number; feedback_type: string; model_version: string }) =>
    request('/recommendations/feedback', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Bookings
  createBooking: (data: any) => request<Booking>('/bookings', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  getMyBookings: () => request<Booking[]>('/bookings/mine'),
  getHostBookings: () => request<Booking[]>('/bookings/host/requests'),
  updateBookingStatus: (id: number, status: string) => request<Booking>(`/bookings/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  }),

  // Reviews & Favourites
  getReviews: (propertyId: number) => request<Review[]>(`/properties/${propertyId}/reviews`),
  createReview: (data: { booking_id: number; rating: number; review_text: string }) =>
    request<Review>('/reviews', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  getFavourites: () => request<Property[]>('/favourites'),
  addFavourite: (propertyId: number) => request(`/favourites/${propertyId}`, { method: 'POST' }),
  removeFavourite: (propertyId: number) => request(`/favourites/${propertyId}`, { method: 'DELETE' }),

  // Demand Analytics
  getDemandAnalytics: (neighbourhood?: string, date?: string) => {
    const params = new URLSearchParams();
    if (neighbourhood) params.append('neighbourhood', neighbourhood);
    if (date) params.append('target_date', date);
    const query = params.toString() ? `?${params.toString()}` : '';
    return request<DemandAnalyticsResponse>(`/analytics/demand${query}`);
  },
  getHostAnalytics: () => request<HostAnalyticsResponse>('/analytics/host'),

  // MLOps
  getMLStatus: () => request<MLStatusResponse>('/ml/status'),
  getDriftReport: () => request<DriftReport>('/ml/drift'),
  triggerRetrain: (modelName: string, autoActivate: boolean = false) => request('/ml/retrain', {
    method: 'POST',
    body: JSON.stringify({
      model_name: modelName,
      evaluate_against_active: true,
      auto_activate_if_superior: autoActivate,
    }),
  }),
  activateCandidate: (modelName: string) => request(`/ml/activate/${modelName}`, {
    method: 'POST',
  }),
};
