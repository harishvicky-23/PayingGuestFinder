import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Building2, Users, IndianRupee, Clock, CheckCircle, 
  XCircle, AlertCircle, Plus, BarChart3, ChevronRight 
} from 'lucide-react';
import { Booking, HostAnalyticsResponse } from '../../types';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

export const HostDashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState<HostAnalyticsResponse | null>(null);
  const [requests, setRequests] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  const fetchHostData = async () => {
    setLoading(true);
    try {
      const [analyticsData, bookingsData] = await Promise.all([
        api.getHostAnalytics(),
        api.getHostBookings(),
      ]);
      setAnalytics(analyticsData);
      setRequests(bookingsData);
    } catch (err) {
      console.error('Failed to load host dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHostData();
  }, []);

  const handleStatusUpdate = async (bookingId: number, status: 'CONFIRMED' | 'REJECTED') => {
    setActionLoading(bookingId);
    try {
      await api.updateBookingStatus(bookingId, status);
      await fetchHostData();
    } catch (err: any) {
      alert(err.message || `Failed to update booking to ${status}.`);
    } finally {
      setActionLoading(null);
    }
  };

  const pendingRequests = requests.filter((r) => r.status === 'PENDING');
  const pastBookings = requests.filter((r) => r.status !== 'PENDING');

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 min-h-screen">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Host Management Console
          </h1>
          <p className="text-xs sm:text-sm text-slate-500">
            Manage your rental listings, incoming approvals, and revenue.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/host/properties"
            className="px-4 py-2 border border-slate-300 hover:bg-slate-50 rounded-xl text-xs font-semibold text-slate-700 transition"
          >
            My Listings
          </Link>
          <Link
            to="/host/properties/new"
            className="px-4 py-2 bg-brand-500 hover:bg-brand-600 rounded-xl text-xs font-bold text-white shadow-sm transition flex items-center gap-1.5"
          >
            <Plus className="w-3.5 h-3.5" /> List New Space
          </Link>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold">Active Listings</span>
            <Building2 className="w-4 h-4 text-brand-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {analytics?.total_listings ?? 0}
          </div>
          <span className="text-[10px] text-slate-400">Published spaces</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold">Confirmed Stays</span>
            <CheckCircle className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {analytics?.total_bookings ?? 0}
          </div>
          <span className="text-[10px] text-slate-400">Total completed & active</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold">Recorded Revenue</span>
            <IndianRupee className="w-4 h-4 text-brand-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">
            ₹{analytics?.total_revenue?.toLocaleString() ?? 0}
          </div>
          <span className="text-[10px] text-slate-400">From confirmed bookings</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold">Pending Approvals</span>
            <Clock className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {pendingRequests.length}
          </div>
          <span className="text-[10px] text-slate-400">Needs your review</span>
        </div>
      </div>

      {/* Pending Approvals Section */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 shadow-xs mb-8">
        <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
          <span>Pending Booking Requests</span>
          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">
            {pendingRequests.length}
          </span>
        </h2>

        {pendingRequests.length === 0 ? (
          <p className="text-xs text-slate-500 py-6 text-center">
            No pending booking requests right now. New guest requests will appear here for one-click approval.
          </p>
        ) : (
          <div className="space-y-3">
            {pendingRequests.map((r) => (
              <div
                key={r.id}
                className="p-4 rounded-2xl border border-slate-200 bg-slate-50/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-bold text-slate-900">{r.renter_name || 'Guest'}</span>
                    <span className="text-[11px] text-slate-400 font-mono">#{r.id}</span>
                  </div>
                  <h4 className="text-sm font-semibold text-slate-800">{r.property_title}</h4>
                  <div className="flex items-center gap-3 text-xs text-slate-500 mt-1">
                    <span>{new Date(r.start_datetime).toLocaleDateString()}</span>
                    <span>{new Date(r.start_datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - {new Date(r.end_datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    <span className="font-bold text-slate-900">₹{r.total_price}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleStatusUpdate(r.id, 'CONFIRMED')}
                    disabled={actionLoading === r.id}
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition shadow-xs disabled:opacity-50 flex items-center gap-1.5"
                  >
                    <CheckCircle className="w-3.5 h-3.5" /> Accept Request
                  </button>
                  <button
                    onClick={() => handleStatusUpdate(r.id, 'REJECTED')}
                    disabled={actionLoading === r.id}
                    className="px-3 py-2 border border-slate-300 hover:bg-slate-100 text-slate-700 rounded-xl text-xs font-semibold transition disabled:opacity-50 flex items-center gap-1.5"
                  >
                    <XCircle className="w-3.5 h-3.5 text-slate-400" /> Decline
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Demand Prediction Shortcut Banner */}
      <div className="p-6 bg-gradient-to-r from-teal-500 to-emerald-600 text-white rounded-3xl shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-teal-100 flex items-center gap-1.5 mb-1">
            <BarChart3 className="w-4 h-4" /> Machine Learning Demand Intelligence
          </span>
          <h3 className="text-xl font-bold">Predict booking demand in your neighbourhood</h3>
          <p className="text-xs text-teal-100/90 max-w-xl mt-1">
            Evaluate expected booking requests across morning, afternoon, evening, and weekend time slots in Guindy, Velachery, T. Nagar, and OMR.
          </p>
        </div>
        <Link
          to="/host/analytics"
          className="px-5 py-2.5 bg-white text-slate-900 hover:bg-teal-50 rounded-xl text-xs font-bold transition shrink-0 shadow-sm flex items-center gap-1"
        >
          View Demand Charts <ChevronRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
};
