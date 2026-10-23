import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  Search, Clock, MapPin, Users, Sparkles, Shield, 
  Briefcase, Coffee, ArrowRight, Zap, CheckCircle2, ChevronRight, Laptop
} from 'lucide-react';
import { Property, RecommendationItem } from '../types';
import { api } from '../services/api';
import { PropertyCard } from '../components/PropertyCard';
import { CHENNAI_AREAS } from './ExplorePage';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();

  // Search form state
  const [location, setLocation] = useState('Guindy');
  const [durationType, setDurationType] = useState('hourly');
  const [budget, setBudget] = useState('500');
  const [guests, setGuests] = useState('1');

  // Featured properties state
  const [featured, setFeatured] = useState<Property[]>([]);
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const props = await api.getProperties({ limit: 6 });
        setFeatured(props);

        // Fetch sample recommendations for Guindy with budget
        const recResp = await api.getRecommendations({
          location_query: 'Guindy',
          duration_type: 'hourly',
          budget: 500,
          guest_count: 1,
          radius_km: 15.0,
        });
        if (recResp && recResp.results) {
          setRecommendations(recResp.results.slice(0, 3));
        }
      } catch (err) {
        console.error('Failed to load home page listings:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchInitialData();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams({
      location,
      duration: durationType,
      budget,
      guests,
    });
    navigate(`/explore?${params.toString()}`);
  };

  const categories = [
    {
      type: 'workspace_studio',
      title: 'Work Studios',
      desc: 'Ergonomic desks, gigabit WiFi, coffee',
      icon: Laptop,
      count: '8 spaces',
    },
    {
      type: 'private_room',
      title: 'Day Transit Rooms',
      desc: 'En-suite shower, blackout blinds for layovers',
      icon: Clock,
      count: '6 spaces',
    },
    {
      type: 'day_cabin',
      title: 'Quiet Garden Pods',
      desc: 'Acoustic quiet pods for deep focus',
      icon: Coffee,
      count: '4 spaces',
    },
    {
      type: 'guest_suite',
      title: 'Executive Suites',
      desc: 'Premium spaces for meetings & rest',
      icon: Briefcase,
      count: '5 spaces',
    },
  ];

  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-b from-teal-50/70 via-slate-50 to-white pt-12 pb-20 border-b border-slate-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-10">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-brand-100/80 text-brand-800 text-xs font-semibold mb-4 border border-brand-200 shadow-xs">
              <Sparkles className="w-3.5 h-3.5 text-brand-600" />
              <span>AI-Powered Short Duration Rentals & Work Pods</span>
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-slate-900 leading-[1.15]">
              Find the right space, for <span className="text-brand-600">exactly as long</span> as you need.
            </h1>
            <p className="mt-4 text-base sm:text-lg text-slate-600 leading-relaxed max-w-2xl mx-auto">
              Book verified private rooms, ergonomic workspaces, or whole suites by the hour, half day, or full day across Chennai neighbourhoods.
            </p>
          </div>

          {/* Search Form Card */}
          <div className="max-w-4xl mx-auto bg-white rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-200 p-4 sm:p-6">
            <form onSubmit={handleSearch} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Location Select */}
              <div className="flex flex-col">
                <label className="text-xs font-semibold text-slate-600 mb-1 flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-brand-600" />
                  Neighbourhood
                </label>
                <select
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500 transition"
                >
                  <option value="Guindy">Guindy (Metro & Tech Park)</option>
                  <option value="Velachery">Velachery (Phoenix Mall)</option>
                  <option value="Adyar">Adyar (Coastal & Green)</option>
                  <option value="T. Nagar">T. Nagar (Commercial Hub)</option>
                  <option value="Anna Nagar">Anna Nagar (Tower Park)</option>
                  <option value="Mylapore">Mylapore (Cultural & Quiet)</option>
                  <option value="OMR (Thoraipakkam)">OMR (IT Corridor)</option>
                  <option value="Nungambakkam">Nungambakkam (Central)</option>
                </select>
              </div>

              {/* Duration Type */}
              <div className="flex flex-col">
                <label className="text-xs font-semibold text-slate-600 mb-1 flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-brand-600" />
                  Duration
                </label>
                <select
                  value={durationType}
                  onChange={(e) => setDurationType(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500 transition"
                >
                  <option value="hourly">Hourly (1–4 hrs)</option>
                  <option value="half_day">Half Day (~6 hrs)</option>
                  <option value="full_day">Full Day (24 hrs)</option>
                  <option value="multi_day">Multiple Days</option>
                </select>
              </div>

              {/* Budget */}
              <div className="flex flex-col">
                <label className="text-xs font-semibold text-slate-600 mb-1 flex items-center gap-1">
                  <span>₹</span> Max Budget
                </label>
                <select
                  value={budget}
                  onChange={(e) => setBudget(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500 transition"
                >
                  <option value="300">Under ₹300</option>
                  <option value="500">Under ₹500</option>
                  <option value="800">Under ₹800</option>
                  <option value="1500">Under ₹1,500</option>
                  <option value="3000">Under ₹3,000</option>
                </select>
              </div>

              {/* Submit CTA */}
              <div className="flex flex-col justify-end">
                <button
                  type="submit"
                  className="w-full bg-brand-500 hover:bg-brand-600 text-white font-bold py-2.5 px-4 rounded-xl shadow-md shadow-brand-500/20 flex items-center justify-center gap-2 transition"
                >
                  <Search className="w-4 h-4" />
                  Find Spaces
                </button>
              </div>
            </form>
          </div>
        </div>
      </section>

      {/* Property Categories Section */}
      <section className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl sm:text-2xl font-bold text-slate-900">Explore by Purpose</h2>
              <p className="text-xs sm:text-sm text-slate-500">Tailored spaces for modern remote workers and travelers</p>
            </div>
            <Link
              to="/explore"
              className="text-xs sm:text-sm font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1"
            >
              View all <ChevronRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {categories.map((cat, idx) => {
              const Icon = cat.icon;
              return (
                <Link
                  key={idx}
                  to={`/explore?type=${cat.type}`}
                  className="group p-5 rounded-2xl border border-slate-200 hover:border-brand-400 hover:shadow-md transition bg-slate-50/50 hover:bg-white flex flex-col justify-between"
                >
                  <div>
                    <div className="w-12 h-12 rounded-xl bg-brand-100 text-brand-700 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                      <Icon className="w-6 h-6" />
                    </div>
                    <h3 className="font-bold text-slate-900 text-base mb-1">{cat.title}</h3>
                    <p className="text-xs text-slate-500 leading-relaxed mb-3">{cat.desc}</p>
                  </div>
                  <span className="text-xs font-semibold text-brand-600 flex items-center gap-1">
                    {cat.count} <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                  </span>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* AI Recommendation Engine Spotlight */}
      <section className="py-14 bg-gradient-to-r from-teal-900 to-slate-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            <div className="lg:col-span-5 space-y-4">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-800/80 border border-teal-600/30 text-teal-200 text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5 text-teal-400" />
                <span>Explainable Machine Learning</span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight leading-snug">
                Transparent recommendations, derived from actual listing features.
              </h2>
              <p className="text-sm text-teal-100/80 leading-relaxed">
                StayNearby does not use black-box artificial intelligence. Our multi-stage ranking engine calculates geographic distance via the Haversine formula and evaluates real component scores:
              </p>
              <div className="space-y-2 pt-2 text-xs">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-teal-400 shrink-0" />
                  <span><strong>Geospatial Proximity (25%):</strong> Straight-line radius matching</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-teal-400 shrink-0" />
                  <span><strong>Price Suitability (20%):</strong> Total computed duration estimate vs your budget</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-teal-400 shrink-0" />
                  <span><strong>Amenity & Preference Match (35%):</strong> Exact overlap with your required setup</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-teal-400 shrink-0" />
                  <span><strong>Verified Ratings & Duration (20%):</strong> Quality reviews and hourly suitability</span>
                </div>
              </div>
              <div className="pt-2">
                <Link
                  to="/admin/ml-operations"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold rounded-xl text-xs transition shadow-sm"
                >
                  Explore MLOps Lifecycle <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>

            {/* Live Recommendation Preview Cards */}
            <div className="lg:col-span-7">
              <div className="text-xs font-semibold uppercase tracking-wider text-teal-300 mb-3 flex items-center justify-between">
                <span>Sample Recommendation Results for Guindy</span>
                <span className="text-teal-400">ML Model Active</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {recommendations.slice(0, 2).map((item) => (
                  <PropertyCard
                    key={item.property.id}
                    property={item.property}
                    recommendationItem={item}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Properties Grid */}
      <section className="py-14 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-2xl font-bold text-slate-900">Featured Short-Duration Stays</h2>
              <p className="text-sm text-slate-500">Popular properties ready for instant hourly & daily booking</p>
            </div>
            <Link
              to="/explore"
              className="text-sm font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1"
            >
              Browse all 20+ spaces <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {featured.slice(0, 6).map((prop) => (
              <PropertyCard key={prop.id} property={prop} />
            ))}
          </div>
        </div>
      </section>

      {/* Host Call-to-Action Banner */}
      <section className="py-16 bg-white border-t border-slate-100">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="w-12 h-12 bg-brand-100 text-brand-700 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Zap className="w-6 h-6" />
          </div>
          <h2 className="text-3xl font-bold text-slate-900 mb-3">
            Have a quiet room or desk in Chennai?
          </h2>
          <p className="text-base text-slate-600 max-w-2xl mx-auto mb-6 leading-relaxed">
            Monetize your vacant room, guest suite, or studio workspace during the day. Access machine-learning demand predictions to optimize your pricing across peak slots.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-3">
            <Link
              to="/host/properties/new"
              className="px-6 py-3 rounded-xl bg-brand-500 hover:bg-brand-600 text-white font-bold text-sm shadow-md transition"
            >
              List Your Space
            </Link>
            <Link
              to="/host/analytics"
              className="px-6 py-3 rounded-xl border border-slate-300 hover:border-slate-400 text-slate-700 font-semibold text-sm transition"
            >
              View Neighbourhood Demand Forecasts
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};
