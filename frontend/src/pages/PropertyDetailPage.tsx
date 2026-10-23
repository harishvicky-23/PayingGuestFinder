import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  Star, MapPin, Users, ShieldCheck, Clock, 
  Calendar, Check, AlertCircle, Sparkles, Heart, ChevronLeft, Lock
} from 'lucide-react';
import { Property, Review } from '../types';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const PropertyDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [property, setProperty] = useState<Property | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Booking widget state
  const [durationType, setDurationType] = useState('hourly');
  const [hours, setHours] = useState('3');
  const [guestCount, setGuestCount] = useState('1');
  const [startDate, setStartDate] = useState(
    new Date(Date.now() + 86400000).toISOString().slice(0, 10)
  );
  const [startTime, setStartTime] = useState('10:00');
  const [bookingLoading, setBookingLoading] = useState(false);
  const [bookingSuccess, setBookingSuccess] = useState<string | null>(null);
  const [bookingError, setBookingError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDetail = async () => {
      if (!id) return;
      try {
        const prop = await api.getProperty(parseInt(id, 10));
        setProperty(prop);
        if (prop.supported_durations && prop.supported_durations.length > 0) {
          setDurationType(prop.supported_durations[0]);
        }
        const revs = await api.getReviews(parseInt(id, 10));
        setReviews(revs);
      } catch (err: any) {
        setError(err.message || 'Failed to load property details.');
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center">
        <div className="w-10 h-10 border-4 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-sm text-slate-500">Loading space details...</p>
      </div>
    );
  }

  if (error || !property) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-20 text-center">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-3" />
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Property Not Found</h2>
        <p className="text-sm text-slate-600 mb-6">{error || 'This listing may have been deactivated or removed.'}</p>
        <Link to="/explore" className="px-4 py-2 bg-brand-500 text-white font-semibold rounded-xl text-sm">
          Return to Explore
        </Link>
      </div>
    );
  }

  // Calculate rental cost on frontend for preview
  const numHours = parseFloat(hours) || 2;
  let basePrice = 0;
  if (durationType === 'hourly') {
    basePrice = property.price_per_hour * numHours;
  } else if (durationType === 'half_day') {
    basePrice = property.price_per_half_day;
  } else if (durationType === 'full_day') {
    basePrice = property.price_per_day;
  } else {
    basePrice = property.price_per_day * Math.max(1, numHours / 24) * 0.95;
  }
  const fee = Math.round(basePrice * 0.05);
  const totalPrice = Math.round(basePrice + fee);

  const handleBookingSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) {
      alert('Please sign in or create an account to request a booking.');
      navigate('/login');
      return;
    }

    setBookingLoading(true);
    setBookingError(null);
    setBookingSuccess(null);

    try {
      const startDt = new Date(`${startDate}T${startTime}:00Z`);
      let endHours = numHours;
      if (durationType === 'half_day') endHours = 6;
      if (durationType === 'full_day') endHours = 24;

      const endDt = new Date(startDt.getTime() + endHours * 3600 * 1000);

      const booking = await api.createBooking({
        property_id: property.id,
        start_datetime: startDt.toISOString(),
        end_datetime: endDt.toISOString(),
        duration_type: durationType,
        guest_count: parseInt(guestCount, 10) || 1,
      });

      setBookingSuccess(`Booking request placed! Reference #${booking.id}. Awaiting host confirmation.`);
    } catch (err: any) {
      setBookingError(err.message || 'Failed to submit booking.');
    } finally {
      setBookingLoading(false);
    }
  };

  return (
    <div className="bg-slate-50 min-h-screen pb-20">
      {/* Top back bar */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <Link
            to="/explore"
            className="inline-flex items-center gap-1 text-xs font-semibold text-slate-600 hover:text-slate-900 transition"
          >
            <ChevronLeft className="w-4 h-4" /> Back to Explore
          </Link>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        {/* Gallery Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 rounded-2xl overflow-hidden mb-8">
          <div className="md:col-span-2 aspect-[16/10] bg-slate-200 overflow-hidden">
            <img
              src={property.images[0] || 'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80'}
              alt={property.title}
              className="w-full h-full object-cover"
            />
          </div>
          <div className="hidden md:grid grid-rows-2 gap-3">
            <div className="aspect-[16/10] bg-slate-200 overflow-hidden">
              <img
                src={property.images[1] || property.images[0] || 'https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=800&q=80'}
                alt={property.title}
                className="w-full h-full object-cover"
              />
            </div>
            <div className="aspect-[16/10] bg-slate-200 overflow-hidden relative">
              <img
                src={property.images[0]}
                alt={property.title}
                className="w-full h-full object-cover filter blur-xs"
              />
              <div className="absolute inset-0 bg-slate-900/40 flex items-center justify-center text-white font-bold text-sm">
                Verified Chennai Space
              </div>
            </div>
          </div>
        </div>

        {/* Content & Booking Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
          {/* Left Column: Details */}
          <div className="lg:col-span-7 space-y-8">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs uppercase tracking-wider font-bold text-brand-600 bg-brand-50 px-2.5 py-1 rounded-full border border-brand-200">
                  {property.property_type.replace(/_/g, ' ')}
                </span>
                <span className="text-xs font-semibold text-slate-500 flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" />
                  {property.neighbourhood}
                </span>
              </div>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mb-2">
                {property.title}
              </h1>
              <p className="text-sm text-slate-600 leading-relaxed">
                {property.description}
              </p>
            </div>

            {/* Generalised Location & Security Note */}
            <div className="p-4 bg-white rounded-2xl border border-slate-200 space-y-2">
              <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                <MapPin className="w-4 h-4 text-brand-600" />
                General Location: {property.public_location_description}
              </h3>
              {property.exact_address ? (
                <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-900">
                  <strong className="block font-semibold mb-0.5">Exact Confirmed Address Revealed:</strong>
                  {property.exact_address}
                </div>
              ) : (
                <div className="flex items-start gap-2 text-xs text-slate-500 pt-1">
                  <Lock className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
                  <span>
                    Privacy protected: Precise residential street and access codes are revealed only after a booking is confirmed by the host.
                  </span>
                </div>
              )}
            </div>

            {/* Amenities Grid */}
            <div>
              <h3 className="font-bold text-slate-900 text-base mb-3">Included Amenities</h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
                {property.amenities.map((amenity, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-2 p-3 bg-white rounded-xl border border-slate-200 text-xs font-medium text-slate-700 capitalize"
                  >
                    <Check className="w-4 h-4 text-brand-600" />
                    <span>{amenity.replace(/_/g, ' ')}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* House Rules */}
            <div>
              <h3 className="font-bold text-slate-900 text-base mb-2">House Rules</h3>
              <div className="p-4 bg-white rounded-2xl border border-slate-200 text-xs text-slate-600 leading-relaxed">
                {property.house_rules || 'Standard etiquette: No smoking, maintain quiet hours after 10 PM, respect check-out timings.'}
              </div>
            </div>

            {/* Reviews Section */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-slate-900 text-lg flex items-center gap-2">
                  <span>Guest Reviews</span>
                  <span className="text-sm font-semibold text-slate-500">
                    ({reviews.length})
                  </span>
                </h3>
                <div className="flex items-center gap-1 text-sm font-bold text-slate-900">
                  <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                  <span>{property.average_rating > 0 ? property.average_rating.toFixed(1) : 'New'}</span>
                </div>
              </div>

              {reviews.length === 0 ? (
                <p className="text-xs text-slate-500 bg-white p-6 rounded-2xl border border-slate-200 text-center">
                  No reviews yet for this space. Be the first verified guest to review after your stay!
                </p>
              ) : (
                <div className="space-y-3">
                  {reviews.map((r) => (
                    <div key={r.id} className="p-4 bg-white rounded-2xl border border-slate-200 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-900">{r.renter_name || 'Verified Guest'}</span>
                        <div className="flex items-center gap-1 text-xs text-amber-500 font-semibold">
                          <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                          <span>{r.rating.toFixed(1)}</span>
                        </div>
                      </div>
                      <p className="text-xs text-slate-600 leading-relaxed">{r.review_text}</p>
                      <span className="text-[10px] text-slate-400 block">{new Date(r.created_at).toLocaleDateString()}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right Column: Booking Widget */}
          <div className="lg:col-span-5">
            <div className="sticky top-28 bg-white rounded-3xl p-6 border border-slate-200 shadow-xl shadow-slate-200/50 space-y-6">
              {/* Pricing Header */}
              <div className="flex items-baseline justify-between border-b border-slate-100 pb-4">
                <div>
                  <span className="text-2xl font-extrabold text-slate-900">₹{property.price_per_hour}</span>
                  <span className="text-xs text-slate-500"> / hour</span>
                </div>
                <div className="text-right text-xs text-slate-500">
                  <div>₹{property.price_per_half_day} half day</div>
                  <div>₹{property.price_per_day} full day</div>
                </div>
              </div>

              {/* Booking Form */}
              <form onSubmit={handleBookingSubmit} className="space-y-4">
                {bookingSuccess && (
                  <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800">
                    {bookingSuccess}
                  </div>
                )}
                {bookingError && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-800">
                    {bookingError}
                  </div>
                )}

                {/* Duration Type */}
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Duration Type</label>
                  <select
                    value={durationType}
                    onChange={(e) => setDurationType(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-medium text-slate-800 focus:outline-none focus:ring-1 focus:ring-brand-500"
                  >
                    {property.supported_durations.map((d) => (
                      <option key={d} value={d}>
                        {d === 'hourly' && 'Hourly (Flexible hours)'}
                        {d === 'half_day' && 'Half Day Block (~6 hrs)'}
                        {d === 'full_day' && 'Full Day (24 hrs)'}
                        {d === 'multi_day' && 'Multi-Day (5% discount)'}
                      </option>
                    ))}
                  </select>
                </div>

                {/* If hourly, select number of hours */}
                {durationType === 'hourly' && (
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Number of Hours: <span className="text-brand-600 font-bold">{hours} hrs</span>
                    </label>
                    <input
                      type="range"
                      min="1"
                      max="12"
                      step="1"
                      value={hours}
                      onChange={(e) => setHours(e.target.value)}
                      className="w-full accent-brand-500 cursor-pointer"
                    />
                  </div>
                )}

                {/* Date & Time */}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Date</label>
                    <input
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-brand-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Start Time</label>
                    <input
                      type="time"
                      value={startTime}
                      onChange={(e) => setStartTime(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-brand-500"
                    />
                  </div>
                </div>

                {/* Guests */}
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Guests</label>
                  <select
                    value={guestCount}
                    onChange={(e) => setGuestCount(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-brand-500"
                  >
                    {Array.from({ length: property.maximum_guests }, (_, i) => i + 1).map((n) => (
                      <option key={n} value={n}>
                        {n} {n === 1 ? 'guest' : 'guests'} (max: {property.maximum_guests})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Price Breakdown */}
                <div className="pt-3 border-t border-slate-100 space-y-1.5 text-xs text-slate-600">
                  <div className="flex justify-between">
                    <span>Base Rental Rate</span>
                    <span>₹{basePrice}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Marketplace Service Fee (5%)</span>
                    <span>₹{fee}</span>
                  </div>
                  <div className="flex justify-between font-bold text-slate-900 text-sm pt-2 border-t border-slate-100">
                    <span>Total Estimate</span>
                    <span>₹{totalPrice}</span>
                  </div>
                </div>

                {/* Submit Action */}
                <button
                  type="submit"
                  disabled={bookingLoading}
                  className="w-full py-3 bg-brand-500 hover:bg-brand-600 text-white font-bold rounded-xl text-sm shadow-md transition disabled:opacity-50"
                >
                  {bookingLoading ? 'Submitting Request...' : 'Request Booking'}
                </button>
                <p className="text-[11px] text-slate-400 text-center">
                  Simulated booking flow. You will not be charged real funds.
                </p>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
