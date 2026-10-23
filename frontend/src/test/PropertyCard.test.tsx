import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { PropertyCard } from '../components/PropertyCard';
import { AuthProvider } from '../context/AuthContext';
import { Property, RecommendationItem } from '../types';

const mockProperty: Property = {
  id: 1,
  host_id: 10,
  title: 'Guindy Executive Desk',
  description: 'Quiet work hub near metro.',
  property_type: 'workspace_studio',
  neighbourhood: 'Guindy',
  latitude: 13.0067,
  longitude: 80.2025,
  public_location_description: 'Near Metro',
  price_per_hour: 300,
  price_per_half_day: 1200,
  price_per_day: 2200,
  maximum_guests: 2,
  amenities: ['wifi', 'air_conditioning', 'work_desk'],
  supported_durations: ['hourly', 'half_day'],
  house_rules: 'No smoking.',
  images: ['https://example.com/img1.jpg'],
  active: true,
  average_rating: 4.8,
  review_count: 12,
  created_at: new Date().toISOString(),
};

const mockRecItem: RecommendationItem = {
  property: mockProperty,
  score: 0.92,
  component_scores: { location_score: 0.9, price_score: 0.95 },
  straight_line_distance_km: 2.4,
  calculated_price: 600,
  explanations: ['Located 2.4 km away, within your selected radius.', 'Fits within your ₹800 budget.'],
  match_badges: ['Nearby (2.4 km)', 'Budget Fit'],
};

describe('PropertyCard Component', () => {
  it('renders property title, neighbourhood, and hourly pricing', () => {
    render(
      <AuthProvider>
        <BrowserRouter>
          <PropertyCard property={mockProperty} />
        </BrowserRouter>
      </AuthProvider>
    );

    expect(screen.getByText('Guindy Executive Desk')).toBeInTheDocument();
    expect(screen.getByText('Guindy')).toBeInTheDocument();
    expect(screen.getByText('₹300')).toBeInTheDocument();
    expect(screen.getByText('Up to 2')).toBeInTheDocument();
  });

  it('renders recommendation explanations and match badges when supplied', () => {
    render(
      <AuthProvider>
        <BrowserRouter>
          <PropertyCard property={mockProperty} recommendationItem={mockRecItem} />
        </BrowserRouter>
      </AuthProvider>
    );

    expect(screen.getByText('Nearby (2.4 km)')).toBeInTheDocument();
    expect(screen.getByText(/Located 2.4 km away/)).toBeInTheDocument();
  });
});
