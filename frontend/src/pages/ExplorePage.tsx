import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { 
  Search, SlidersHorizontal, Map, List, Star, 
  MapPin, Clock, Filter, AlertCircle, RefreshCw, Sparkles 
} from 'lucide-react';
import { Property, RecommendationItem } from '../types';
import { api } from '../services/api';
import { PropertyCard } from '../components/PropertyCard';
import { PropertyMap } from '../components/PropertyMap';

export const CHENNAI_AREAS = [
  'All Neighbourhoods',
  'Guindy',
  'Velachery',
  'Adyar',
  'T. Nagar',
  'Anna Nagar',
  'Mylapore',
  'OMR (Thoraipakkam)',
  'Nungambakkam',
];

const AMENITY_OPTIONS = [
  { id: 'wifi', label: 'High-Speed Wi-Fi' },
  { id: 'air_conditioning', label: 'Air Conditioning' },
  { id: 'work_desk', label: 'Ergonomic Desk' },
  { id: 'power_backup', label: 'Power Backup' },
  { id: 'parking', label: 'Parking' },
  { id: 'quiet_zone', label: 'Quiet Acoustic Zone' },
  { id: 'private_restroom', label: 'Private Restroom' },
  { id: 'coffee_tea', label: 'Coffee / Tea' },
];

export const ExplorePage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  // Filters state
  const [neighbourhood, setNeighbourhood] = useState(searchParams.get('location') || 'All Neighbourhoods');
  const [durationType, setDurationType] = useState(searchParams.get('duration') || 'hourly');
  const [budget, setBudget] = useState(searchParams.get('budget') || '1000');
  const [guests, setGuests] = useState(searchParams.get('guests') || '1');
  const [propertyType, setPropertyType] = useState(searchParams.get('type') || 'all');
  const [radiusKm, setRadiusKm] = useState(15.0);
  const [selectedAmenities, setSelectedAmenities] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState('recommended'); // recommended, nearest, price_asc, rating_desc

  // View state: split (desktop), list-only, map-only
  const [viewMode, setViewMode] = useState<'split' | 'list' | 'map'>('split');
  const [selectedPropertyId, setSelectedPropertyId] = useState<number | null>(null);

  // Data & loading state
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [rawProperties, setRawProperties] = useState<Property[]>([]);
  const [relaxedSuggestions, setRelaxedSuggestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [filterDrawerOpen, setFilterDrawerOpen] = useState(false);

  const fetchResults = async () => {
    setLoading(true);
    try {
      const areaQuery = neighbourhood === 'All Neighbourhoods' ? undefined : neighbourhood;
      const resp = await api.getRecommendations({
        location_query: areaQuery,
        duration_type: durationType,
        budget: budget ? parseFloat(budget) : undefined,
        guest_count: parseInt(guests, 10) || 1,
        property_type: propertyType === 'all' ? undefined : propertyType,
        required_amenities: selectedAmenities,
        radius_km: radiusKm,
        model_choice: 'auto',
      });

      setRecommendations(resp.results);
      setRelaxedSuggestions(resp.relaxed_filter_suggestions || []);

      // Also keep flat list of properties for map
      const props = resp.results.map((r) => r.property);
      setRawProperties(props);
      if (props.length > 0 && !selectedPropertyId) {
        setSelectedPropertyId(props[0].id);
      }
    } catch (err) {
      console.error('Failed to fetch recommendation listings:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResults();
  }, [neighbourhood, durationType, budget, guests, propertyType, radiusKm, selectedAmenities]);

  // Sort results
  const sortedRecommendations = [...recommendations].sort((a, b) => {
    if (sortBy === 'recommended') {
      return b.score - a.score;
    }
    if (sortBy === 'nearest') {
      return (a.straight_line_distance_km ?? 999) - (b.straight_line_distance_km ?? 999);
    }
    if (sortBy === 'price_asc') {
      return a.calculated_price - b.calculated_price;
    }
    if (sortBy === 'rating_desc') {
      return (b.property.average_rating || 0) - (a.property.average_rating || 0);
    }
    return 0;
  });

  const toggleAmenity = (id: string) => {
    setSelectedAmenities((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      {/* Top Filter Bar */}
      <div className="sticky top-16 z-30 bg-white border-b border-slate-200 px-4 sm:px-6 lg:px-8 py-3 shadow-xs">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
          {/* Quick Filters */}
          <div className="flex flex-wrap items-center gap-2">
            {/* Neighbourhood */}
            <select
              value={neighbourhood}
              onChange={(e) => setNeighbourhood(e.target.value)}
              className="text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg px-3 py-1.5 border border-slate-200 focus:outline-none focus:ring-1 focus:ring-brand-500"
            >
              {CHENNAI_AREAS.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>

            {/* Duration */}
            <select
              value={durationType}
              onChange={(e) => setDurationType(e.target.value)}
              className="text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg px-3 py-1.5 border border-slate-200 focus:outline-none focus:ring-1 focus:ring-brand-500"
            >
              <option value="hourly">Hourly</option>
              <option value="half_day">Half Day (6 hrs)</option>
              <option value="full_day">Full Day (24 hrs)</option>
              <option value="multi_day">Multi-Day</option>
            </select>

            {/* Property Type */}
            <select
              value={propertyType}
              onChange={(e) => setPropertyType(e.target.value)}
              className="text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg px-3 py-1.5 border border-slate-200 focus:outline-none focus:ring-1 focus:ring-brand-500 capitalize"
            >
              <option value="all">All Types</option>
              <option value="workspace_studio">Workspace Studio</option>
              <option value="private_room">Private Room</option>
              <option value="day_cabin">Quiet Pod</option>
              <option value="entire_apartment">Entire Apartment</option>
              <option value="guest_suite">Guest Suite</option>
            </select>

            {/* Filter Drawer Toggle */}
            <button
              onClick={() => setFilterDrawerOpen(!filterDrawerOpen)}
              className={`text-xs font-semibold px-3 py-1.5 rounded-lg border flex items-center gap-1.5 transition ${
                selectedAmenities.length > 0 || filterDrawerOpen
                  ? 'bg-brand-500 text-white border-brand-500 shadow-xs'
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
              }`}
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
              <span>Filters {selectedAmenities.length > 0 && `(${selectedAmenities.length})`}</span>
            </button>
          </div>

          {/* Right Controls: Sort & Map Toggle */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1 text-xs text-slate-500">
              <span>Sort:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="font-semibold text-slate-800 bg-transparent border-0 focus:ring-0 cursor-pointer text-xs"
              >
                <option value="recommended">AI Recommended</option>
                <option value="nearest">Nearest First</option>
                <option value="price_asc">Lowest Price</option>
                <option value="rating_desc">Highest Rated</option>
              </select>
            </div>

            {/* View Mode Toggle Buttons */}
            <div className="hidden sm:flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200">
              <button
                onClick={() => setViewMode('split')}
                title="Split View"
                className={`p-1.5 rounded-md text-xs font-medium transition ${
                  viewMode === 'split' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500 hover:text-slate-900'
                }`}
              >
                Split
              </button>
              <button
                onClick={() => setViewMode('list')}
                title="List Only"
                className={`p-1.5 rounded-md text-xs font-medium transition ${
                  viewMode === 'list' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500 hover:text-slate-900'
                }`}
              >
                <List className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setViewMode('map')}
                title="Map Only"
                className={`p-1.5 rounded-md text-xs font-medium transition ${
                  viewMode === 'map' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500 hover:text-slate-900'
                }`}
              >
                <Map className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>

        {/* Expandable Filter Drawer */}
        {filterDrawerOpen && (
          <div className="max-w-7xl mx-auto mt-3 pt-3 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-3 gap-6">
            {/* Radius Slider */}
            <div>
              <div className="flex justify-between text-xs font-medium text-slate-700 mb-1">
                <span>Distance Radius:</span>
                <span className="font-bold text-brand-600">{radiusKm} km</span>
              </div>
              <input
                type="range"
                min="2"
                max="35"
                step="1"
                value={radiusKm}
                onChange={(e) => setRadiusKm(parseFloat(e.target.value))}
                className="w-full accent-brand-500 cursor-pointer"
              />
              <p className="text-[10px] text-slate-400 mt-1">
                Straight-line Haversine distance from neighbourhood center.
              </p>
            </div>

            {/* Budget Input */}
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">
                Target Budget (₹):
              </label>
              <input
                type="number"
                min="100"
                step="50"
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                placeholder="e.g. 500"
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-brand-500"
              />
            </div>

            {/* Amenities Checkboxes */}
            <div className="sm:col-span-3">
              <span className="block text-xs font-medium text-slate-700 mb-2">Required Amenities:</span>
              <div className="flex flex-wrap gap-2">
                {AMENITY_OPTIONS.map((amenity) => {
                  const checked = selectedAmenities.includes(amenity.id);
                  return (
                    <button
                      key={amenity.id}
                      type="button"
                      onClick={() => toggleAmenity(amenity.id)}
                      className={`text-xs px-3 py-1.5 rounded-full border transition ${
                        checked
                          ? 'bg-brand-500 text-white border-brand-500'
                          : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                      }`}
                    >
                      {amenity.label}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Main Discovery Body */}
      <div className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6">
        {/* Relaxed Suggestions Alert */}
        {relaxedSuggestions.length > 0 && (
          <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-2xl flex items-start gap-3 text-xs text-amber-900">
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <strong className="font-semibold block mb-1">Few exact matches found. Suggestions to expand options:</strong>
              <ul className="list-disc list-inside space-y-0.5 text-amber-800">
                {relaxedSuggestions.map((s, idx) => (
                  <li key={idx}>{s}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Content Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[600px]">
          {/* Listings Column */}
          {(viewMode === 'split' || viewMode === 'list') && (
            <div className={`${viewMode === 'split' ? 'lg:col-span-7' : 'lg:col-span-12'}`}>
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-semibold text-slate-700">
                  {sortedRecommendations.length} spaces matching criteria
                </span>
                {loading && (
                  <span className="text-xs text-brand-600 flex items-center gap-1 font-medium">
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Updating...
                  </span>
                )}
              </div>

              {sortedRecommendations.length === 0 && !loading ? (
                <div className="bg-white rounded-2xl p-12 text-center border border-slate-200">
                  <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 mx-auto mb-3">
                    <Search className="w-6 h-6" />
                  </div>
                  <h3 className="font-bold text-slate-800 text-base mb-1">No spaces matched your strict filters</h3>
                  <p className="text-xs text-slate-500 max-w-md mx-auto mb-4">
                    Try expanding your search radius, adjusting your budget, or clearing required amenity constraints.
                  </p>
                  <button
                    onClick={() => {
                      setRadiusKm(25.0);
                      setSelectedAmenities([]);
                      setPropertyType('all');
                    }}
                    className="px-4 py-2 bg-brand-500 text-white rounded-xl text-xs font-semibold hover:bg-brand-600 transition"
                  >
                    Reset to Broad Search
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {sortedRecommendations.map((item) => (
                    <div
                      key={item.property.id}
                      onMouseEnter={() => setSelectedPropertyId(item.property.id)}
                    >
                      <PropertyCard
                        property={item.property}
                        recommendationItem={item}
                        isSelected={selectedPropertyId === item.property.id}
                        onSelect={() => setSelectedPropertyId(item.property.id)}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Map Column */}
          {(viewMode === 'split' || viewMode === 'map') && (
            <div
              className={`sticky top-32 ${
                viewMode === 'split' ? 'lg:col-span-5 h-[calc(100vh-160px)]' : 'lg:col-span-12 h-[calc(100vh-160px)]'
              }`}
            >
              <PropertyMap
                properties={rawProperties}
                selectedPropertyId={selectedPropertyId}
                onSelectProperty={(id) => setSelectedPropertyId(id)}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
