import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, MapPin, Eye, EyeOff, Edit, Trash2 } from 'lucide-react';
import { Property } from '../../types';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

export const HostPropertiesPage: React.FC = () => {
  const { user } = useAuth();
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchProperties = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const data = await api.getProperties({ host_id: user.id });
      setProperties(data);
    } catch (err) {
      console.error('Failed to load host properties:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProperties();
  }, [user]);

  const toggleActive = async (prop: Property) => {
    try {
      await api.updateProperty(prop.id, { active: !prop.active });
      fetchProperties();
    } catch (err: any) {
      alert(err.message || 'Failed to update property status.');
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this listing?')) return;
    try {
      await api.deleteProperty(id);
      fetchProperties();
    } catch (err: any) {
      alert(err.message || 'Failed to delete listing.');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 min-h-screen">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            My Published Listings ({properties.length})
          </h1>
          <p className="text-sm text-slate-500">
            Control listing visibility and rates for your properties.
          </p>
        </div>
        <Link
          to="/host/properties/new"
          className="px-4 py-2 bg-brand-500 hover:bg-brand-600 rounded-xl text-xs font-bold text-white shadow-sm transition flex items-center gap-1.5"
        >
          <Plus className="w-3.5 h-3.5" /> Add New Space
        </Link>
      </div>

      {loading ? (
        <div className="py-20 text-center">
          <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-xs text-slate-400">Loading your listings...</p>
        </div>
      ) : properties.length === 0 ? (
        <div className="bg-white rounded-3xl p-12 text-center border border-slate-200 max-w-md mx-auto">
          <p className="text-sm text-slate-600 mb-4">You have not created any property listings yet.</p>
          <Link
            to="/host/properties/new"
            className="px-5 py-2.5 bg-brand-500 hover:bg-brand-600 text-white font-bold rounded-xl text-xs shadow-sm transition"
          >
            Create Your First Listing
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {properties.map((p) => (
            <div
              key={p.id}
              className={`bg-white rounded-2xl border overflow-hidden shadow-xs flex flex-col justify-between ${
                p.active ? 'border-slate-200' : 'border-slate-300 opacity-75 bg-slate-50'
              }`}
            >
              <div>
                <div className="relative aspect-[16/9] bg-slate-100">
                  <img
                    src={p.images[0] || 'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80'}
                    alt={p.title}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-3 left-3 bg-slate-900/80 backdrop-blur-xs text-white text-[10px] font-bold px-2 py-0.5 rounded-full capitalize">
                    {p.property_type.replace(/_/g, ' ')}
                  </div>
                  <div className="absolute top-3 right-3">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        p.active
                          ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                          : 'bg-slate-200 text-slate-700'
                      }`}
                    >
                      {p.active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>

                <div className="p-4">
                  <div className="flex items-center gap-1 text-xs text-slate-500 mb-1">
                    <MapPin className="w-3.5 h-3.5 text-brand-600" />
                    <span>{p.neighbourhood}</span>
                  </div>
                  <h3 className="font-bold text-slate-900 text-base mb-1 line-clamp-1">{p.title}</h3>
                  <div className="text-xs text-slate-600 font-semibold mb-3">
                    ₹{p.price_per_hour}/hr • ₹{p.price_per_half_day} half-day
                  </div>
                  <p className="text-xs text-slate-500 line-clamp-2">{p.description}</p>
                </div>
              </div>

              <div className="p-4 border-t border-slate-100 flex items-center justify-between">
                <button
                  onClick={() => toggleActive(p)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 transition ${
                    p.active
                      ? 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                      : 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100'
                  }`}
                >
                  {p.active ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                  {p.active ? 'Deactivate' : 'Publish'}
                </button>

                <div className="flex items-center gap-2">
                  <Link
                    to={`/properties/${p.id}`}
                    className="p-1.5 text-slate-500 hover:text-slate-800 rounded-lg hover:bg-slate-100 transition"
                    title="View Public Page"
                  >
                    <Eye className="w-4 h-4" />
                  </Link>
                  <button
                    onClick={() => handleDelete(p.id)}
                    className="p-1.5 text-red-500 hover:text-red-700 rounded-lg hover:bg-red-50 transition"
                    title="Delete Listing"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
