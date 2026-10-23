import React, { useState } from 'react';
import { User, Shield, Check, Save } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

const AMENITY_OPTIONS = [
  'wifi', 'air_conditioning', 'work_desk', 'power_backup',
  'parking', 'quiet_zone', 'private_restroom', 'coffee_tea'
];

export const ProfilePage: React.FC = () => {
  const { user, refreshProfile } = useAuth();
  const [name, setName] = useState(user?.name || '');
  const [budget, setBudget] = useState(user?.preferred_budget?.toString() || '500');
  const [amenities, setAmenities] = useState<string[]>(user?.preferred_amenities || []);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  if (!user) {
    return <div className="p-12 text-center text-sm">Please sign in to view your profile.</div>;
  }

  const toggleAmenity = (id: string) => {
    setAmenities((prev) =>
      prev.includes(id) ? prev.filter((a) => a !== id) : [...prev, id]
    );
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    try {
      await api.updateProfile({
        name,
        preferred_budget: budget ? parseFloat(budget) : undefined,
        preferred_amenities: amenities,
      });
      await refreshProfile();
      setMessage('Profile and recommendation preferences updated successfully!');
    } catch (err: any) {
      alert(err.message || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 mb-1">User Profile & Preferences</h1>
          <p className="text-xs text-slate-500">
            These settings customize your AI property recommendations.
          </p>
        </div>

        {message && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs font-semibold">
            {message}
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Full Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-medium text-slate-800 focus:outline-none focus:ring-1 focus:ring-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Email (Read Only)</label>
              <input
                type="text"
                value={user.email}
                disabled
                className="w-full bg-slate-100 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-medium text-slate-500 cursor-not-allowed"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Current Role</label>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-slate-100 rounded-xl text-xs font-bold text-slate-800 uppercase tracking-wider">
              <Shield className="w-4 h-4 text-brand-600" />
              {user.role}
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100">
            <h3 className="text-sm font-bold text-slate-900 mb-1">Recommendation Preferences</h3>
            <p className="text-xs text-slate-500 mb-4">
              Our baseline and ML rankers prioritize properties matching these preferences.
            </p>

            <div className="mb-4">
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Preferred Hourly Budget: ₹{budget}
              </label>
              <input
                type="range"
                min="150"
                max="1500"
                step="50"
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                className="w-full accent-brand-500 cursor-pointer"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-2">
                Preferred Amenities:
              </label>
              <div className="flex flex-wrap gap-2">
                {AMENITY_OPTIONS.map((a) => {
                  const active = amenities.includes(a);
                  return (
                    <button
                      key={a}
                      type="button"
                      onClick={() => toggleAmenity(a)}
                      className={`text-xs px-3 py-1.5 rounded-full border transition flex items-center gap-1.5 capitalize ${
                        active
                          ? 'bg-brand-500 text-white border-brand-500 font-semibold'
                          : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
                      }`}
                    >
                      {active && <Check className="w-3 h-3" />}
                      {a.replace(/_/g, ' ')}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100 flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 bg-brand-500 hover:bg-brand-600 text-white font-bold rounded-xl text-xs shadow-md transition flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              {loading ? 'Saving...' : 'Save Preferences'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
