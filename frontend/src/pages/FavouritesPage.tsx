import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Heart, Search, ChevronRight } from 'lucide-react';
import { Property } from '../types';
import { api } from '../services/api';
import { PropertyCard } from '../components/PropertyCard';
import { useAuth } from '../context/AuthContext';

export const FavouritesPage: React.FC = () => {
  const { user } = useAuth();
  const [favourites, setFavourites] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchFavourites = async () => {
    setLoading(true);
    try {
      const data = await api.getFavourites();
      setFavourites(data);
    } catch (err) {
      console.error('Failed to load favourites:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchFavourites();
    }
  }, [user]);

  if (!user) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Sign in to view saved spaces</h2>
        <p className="text-sm text-slate-500 mb-6">Keep track of favourite quiet workspaces and rooms.</p>
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
            Saved Properties ({favourites.length})
          </h1>
          <p className="text-sm text-slate-500">Your curated collection of top workspaces and rooms.</p>
        </div>
        <Link
          to="/explore"
          className="text-xs font-semibold px-4 py-2 bg-brand-50 text-brand-700 hover:bg-brand-100 rounded-xl transition flex items-center gap-1"
        >
          Explore More <ChevronRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      {loading ? (
        <div className="py-20 text-center">
          <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-xs text-slate-400">Loading saved listings...</p>
        </div>
      ) : favourites.length === 0 ? (
        <div className="bg-white rounded-3xl p-12 text-center border border-slate-200 max-w-md mx-auto">
          <Heart className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-slate-800 mb-1">No Saved Spaces Yet</h3>
          <p className="text-xs text-slate-500 mb-6">
            Click the heart icon on any listing card to save it for quick booking later.
          </p>
          <Link
            to="/explore"
            className="px-5 py-2.5 bg-brand-500 hover:bg-brand-600 text-white font-bold rounded-xl text-xs shadow-sm transition"
          >
            Explore Spaces
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {favourites.map((prop) => (
            <PropertyCard
              key={prop.id}
              property={prop}
              isFavouriteInitial={true}
            />
          ))}
        </div>
      )}
    </div>
  );
};
