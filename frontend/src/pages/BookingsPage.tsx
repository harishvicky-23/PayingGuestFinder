import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Calendar, Clock, MapPin, CheckCircle, XCircle, 
  AlertCircle, Star, X, MessageSquare 
} from 'lucide-react';
import { Booking } from '../types';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const BookingsPage: React.FC = () => {
  const { user } = useAuth();
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Review modal state
  const [reviewModalBooking, setReviewModalBooking] = useState<Booking | null>(null);
  const [reviewRating, setReviewRating] = useState(5.0);
  const [reviewText, setReviewText] = useState('');
  const [reviewLoading, setReviewLoading] = useState(false);
  const [reviewSuccess, setReviewSuccess] = useState<string | null>(null);

  const fetchBookings = async () => {
    setLoading(true);
    try {
      const data = await api.getMyBookings();
      setBookings(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load bookings.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchBookings();
    }
  }, [user]);

  const handleCancel = async (bookingId: number) => {
    if (!window.confirm('Are you sure you want to cancel this booking?')) return;
    try {
      await api.updateBookingStatus(bookingId, 'CANCELLED');
      fetchBookings();
    } catch (err: any) {
      alert(err.message || 'Failed to cancel booking.');
    }
  };

  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reviewModalBooking) return;
    setReviewLoading(true);
    try {
      await api.createReview({
        booking_id: reviewModalBooking.id,
        rating: reviewRating,
        review_text: reviewText,
      });
      setReviewSuccess('Thank you! Your verified review has been published.');
      setTimeout(() => {
        setReviewModalBooking(null);
        setReviewSuccess(null);
        setReviewText('');
      }, 1500);
    } catch (err: any) {
      alert(err.message || 'Failed to submit review.');
    } finally {
      setReviewLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'CONFIRMED':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">Confirmed</span>;
      case 'PENDING':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-200">Pending Host</span>;
      case 'REJECTED':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-800 border border-rose-200">Declined</span>;
      case 'CANCELLED':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-600 border border-slate-200">Cancelled</span>;
      case 'COMPLETED':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-800 border border-blue-200">Completed</span>;
      default:
        return <span>{status}</span>;
    }
  };

  if (!user) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Sign in to view bookings</h2>
        <p className="text-sm text-slate-500 mb-6">Manage your rental requests and confirmed spaces.</p>
        <Link to="/login" className="px-5 py-2.5 bg-brand-500 text-white rounded-xl text-sm font-bold shadow-sm">
          Sign In
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 min-h-screen">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            My Short-Stay Bookings
          </h1>
          <p className="text-sm text-slate-500">Track incoming approvals, confirmed access keys, and receipts.</p>
        </div>
        <Link
          to="/explore"
          className="text-xs font-semibold px-4 py-2 bg-brand-50 text-brand-700 hover:bg-brand-100 rounded-xl transition"
        >
          Book Another Space
        </Link>
      </div>

      {loading ? (
        <div className="py-20 text-center">
          <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-xs text-slate-400">Loading your reservations...</p>
        </div>
      ) : bookings.length === 0 ? (
        <div className="bg-white rounded-3xl p-12 text-center border border-slate-200 max-w-xl mx-auto">
          <Calendar className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-slate-800 mb-1">No Bookings Yet</h3>
          <p className="text-xs text-slate-500 mb-6 leading-relaxed">
            Need a quiet desk for an afternoon work sprint, or a room to freshen up during a layover? Explore listings near you.
          </p>
          <Link
            to="/explore"
            className="px-5 py-2.5 bg-brand-500 hover:bg-brand-600 text-white font-bold rounded-xl text-xs shadow-sm transition"
          >
            Discover Nearby Spaces
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {bookings.map((b) => (
            <div
              key={b.id}
              className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-6"
            >
              {/* Left details */}
              <div className="flex items-start gap-4">
                {b.property_image && (
                  <img
                    src={b.property_image}
                    alt={b.property_title || 'Property'}
                    className="w-20 h-20 rounded-xl object-cover shrink-0 hidden sm:block"
                  />
                )}
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    {getStatusBadge(b.status)}
                    <span className="text-xs text-slate-400 font-mono">#{b.id}</span>
                  </div>
                  <h3 className="font-bold text-base text-slate-900">
                    <Link to={`/properties/${b.property_id}`} className="hover:text-brand-600 transition">
                      {b.property_title || `Property #${b.property_id}`}
                    </Link>
                  </h3>
                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500">
                    <span className="flex items-center gap-1 font-medium text-slate-700">
                      <Calendar className="w-3.5 h-3.5 text-brand-600" />
                      {new Date(b.start_datetime).toLocaleDateString()}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5 text-slate-400" />
                      {new Date(b.start_datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - {new Date(b.end_datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                    <span className="capitalize text-slate-600">
                      • {b.duration_type.replace(/_/g, ' ')}
                    </span>
                  </div>

                  {/* Confirmed exact address box */}
                  {b.status === 'CONFIRMED' && b.exact_address && (
                    <div className="mt-2 p-2.5 bg-emerald-50/80 rounded-xl border border-emerald-200 text-xs text-emerald-900">
                      <strong className="block font-semibold">Confirmed Access Address:</strong>
                      <span>{b.exact_address}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Right pricing & actions */}
              <div className="flex flex-row md:flex-col items-center md:items-end justify-between md:justify-center border-t md:border-t-0 pt-3 md:pt-0 border-slate-100 gap-2 shrink-0">
                <div className="text-left md:text-right">
                  <div className="text-base font-bold text-slate-900">₹{b.total_price}</div>
                  <div className="text-[10px] text-slate-400">Includes 5% platform fee</div>
                </div>

                <div className="flex items-center gap-2">
                  {(b.status === 'PENDING' || b.status === 'CONFIRMED') && (
                    <button
                      onClick={() => handleCancel(b.id)}
                      className="px-3 py-1.5 rounded-lg border border-red-200 text-red-600 hover:bg-red-50 text-xs font-semibold transition"
                    >
                      Cancel
                    </button>
                  )}

                  {(b.status === 'CONFIRMED' || b.status === 'COMPLETED') && (
                    <button
                      onClick={() => setReviewModalBooking(b)}
                      className="px-3 py-1.5 rounded-lg bg-brand-50 hover:bg-brand-100 text-brand-700 text-xs font-semibold transition flex items-center gap-1"
                    >
                      <Star className="w-3.5 h-3.5 fill-brand-600" />
                      Review Stay
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Review Modal */}
      {reviewModalBooking && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 max-w-md w-full shadow-2xl relative">
            <button
              onClick={() => setReviewModalBooking(null)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600"
            >
              <X className="w-5 h-5" />
            </button>
            <h3 className="text-lg font-bold text-slate-900 mb-1">Leave a Review</h3>
            <p className="text-xs text-slate-500 mb-4">
              Share your experience for {reviewModalBooking.property_title}.
            </p>

            {reviewSuccess ? (
              <div className="p-4 bg-emerald-50 text-emerald-800 rounded-xl text-xs font-medium text-center">
                {reviewSuccess}
              </div>
            ) : (
              <form onSubmit={handleReviewSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Rating</label>
                  <div className="flex items-center gap-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        type="button"
                        onClick={() => setReviewRating(star)}
                        className="p-1 hover:scale-110 transition"
                      >
                        <Star
                          className={`w-6 h-6 ${
                            star <= reviewRating ? 'fill-amber-400 text-amber-400' : 'text-slate-300'
                          }`}
                        />
                      </button>
                    ))}
                    <span className="text-sm font-bold text-slate-700 ml-2">{reviewRating}.0 / 5.0</span>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Comments</label>
                  <textarea
                    rows={4}
                    value={reviewText}
                    onChange={(e) => setReviewText(e.target.value)}
                    placeholder="Describe cleanliness, wifi reliability, acoustic quietness, or host hospitality..."
                    required
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-brand-500"
                  />
                </div>

                <button
                  type="submit"
                  disabled={reviewLoading}
                  className="w-full py-2.5 bg-brand-500 hover:bg-brand-600 text-white font-bold rounded-xl text-xs shadow-md transition disabled:opacity-50"
                >
                  {reviewLoading ? 'Publishing...' : 'Submit Verified Review'}
                </button>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
