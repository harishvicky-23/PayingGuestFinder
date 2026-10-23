import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Heart, Star, MapPin, Users, Wifi, 
  Wind, Clock, Sparkles, CheckCircle2 
} from 'lucide-react';
import { Property, RecommendationItem } from '../types';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

interface PropertyCardProps {
  property: Property;
  recommendationItem?: RecommendationItem;
  isSelected?: boolean;
  onSelect?: () => void;
  isFavouriteInitial?: boolean;
}

export const PropertyCard: React.FC<PropertyCardProps> = ({
  property,
  recommendationItem,
  isSelected = false,
  onSelect,
  isFavouriteInitial = false,
}) => {
  const { user } = useAuth();
  const [isFav, setIsFav] = useState(isFavouriteInitial);
  const [favLoading, setFavLoading] = useState(false);

  const toggleFavourite = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!user) {
      alert('Please sign in to save properties to your favourites list.');
      return;
    }
    setFavLoading(true);
    try {
      if (isFav) {
        await api.removeFavourite(property.id);
        setIsFav(false);
      } else {
        await api.addFavourite(property.id);
        setIsFav(true);
      }
    } catch (err) {
      console.error('Favourite toggle failed:', err);
    } finally {
      setFavLoading(false);
    }
  };

  const imageSrc = property.images && property.images.length > 0
    ? property.images[0]
    : 'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80';

  const formatType = (type: string) => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  };

  return (
    <div
      onClick={onSelect}
      className={`group bg-white rounded-2xl overflow-hidden border transition-all duration-200 cursor-pointer flex flex-col h-full ${
        isSelected
          ? 'border-brand-500 ring-2 ring-brand-400/30 shadow-md'
          : 'border-slate-200 hover:border-slate-300 hover:shadow-lg'
      }`}
    >
      {/* Image & Badges */}
      <div className="relative aspect-[16/10] overflow-hidden bg-slate-100">
        <img
          src={imageSrc}
          alt={property.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />

        {/* Property Type Badge */}
        <div className="absolute top-3 left-3 bg-slate-900/75 backdrop-blur-sm text-white text-[11px] font-semibold px-2.5 py-1 rounded-full">
          {formatType(property.property_type)}
        </div>

        {/* Favourite Button */}
        <button
          onClick={toggleFavourite}
          disabled={favLoading}
          aria-label="Save to favourites"
          className="absolute top-3 right-3 w-8 h-8 rounded-full bg-white/90 backdrop-blur-sm flex items-center justify-center text-slate-700 hover:text-red-500 hover:scale-110 transition shadow-sm"
        >
          <Heart
            className={`w-4 h-4 transition ${
              isFav ? 'fill-red-500 text-red-500' : 'text-slate-700'
            }`}
          />
        </button>

        {/* AI Score / Match Badges */}
        {recommendationItem && recommendationItem.match_badges && recommendationItem.match_badges.length > 0 && (
          <div className="absolute bottom-3 left-3 flex flex-wrap gap-1">
            {recommendationItem.match_badges.slice(0, 2).map((badge, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1 bg-teal-900/85 backdrop-blur-sm text-teal-100 text-[10px] font-semibold px-2 py-0.5 rounded-full border border-teal-500/30 shadow-sm"
              >
                <Sparkles className="w-2.5 h-2.5 text-teal-300" />
                {badge}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4 flex-1 flex flex-col justify-between">
        <div>
          {/* Header Row: Neighbourhood & Rating */}
          <div className="flex items-center justify-between text-xs text-slate-500 mb-1.5">
            <div className="flex items-center gap-1 font-medium text-slate-600">
              <MapPin className="w-3.5 h-3.5 text-brand-600" />
              <span>{property.neighbourhood}</span>
              {recommendationItem?.straight_line_distance_km !== undefined && recommendationItem.straight_line_distance_km !== null && (
                <span className="text-slate-400 font-normal">
                  • {recommendationItem.straight_line_distance_km.toFixed(1)} km away
                </span>
              )}
            </div>

            <div className="flex items-center gap-1 font-semibold text-slate-800">
              <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
              <span>{property.average_rating > 0 ? property.average_rating.toFixed(1) : 'New'}</span>
              {property.review_count > 0 && (
                <span className="text-slate-400 font-normal text-[11px]">
                  ({property.review_count})
                </span>
              )}
            </div>
          </div>

          {/* Title */}
          <h3 className="font-bold text-slate-900 text-base leading-snug group-hover:text-brand-700 transition line-clamp-1 mb-1">
            {property.title}
          </h3>

          <p className="text-xs text-slate-500 line-clamp-2 mb-3 leading-relaxed">
            {property.description}
          </p>

          {/* Feature highlights: Amenities & Capacity */}
          <div className="flex items-center gap-2 flex-wrap mb-3">
            <span className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-600 bg-slate-100 px-2 py-0.5 rounded-md">
              <Users className="w-3 h-3 text-slate-500" />
              Up to {property.maximum_guests}
            </span>
            {property.amenities.slice(0, 3).map((a, i) => (
              <span
                key={i}
                className="text-[11px] text-slate-500 bg-slate-50 border border-slate-100 px-2 py-0.5 rounded-md capitalize"
              >
                {a.replace(/_/g, ' ')}
              </span>
            ))}
          </div>

          {/* Recommendation Explanation Box */}
          {recommendationItem && recommendationItem.explanations && recommendationItem.explanations.length > 0 && (
            <div className="mb-3 p-2 bg-brand-50/60 rounded-xl border border-brand-100 text-[11px] text-brand-900 flex items-start gap-1.5 leading-snug">
              <CheckCircle2 className="w-3.5 h-3.5 text-brand-600 shrink-0 mt-0.5" />
              <span>{recommendationItem.explanations[0]}</span>
            </div>
          )}
        </div>

        {/* Footer: Price & Booking Action */}
        <div className="pt-3 border-t border-slate-100 flex items-center justify-between mt-2">
          <div>
            <div className="flex items-baseline gap-1">
              <span className="text-lg font-bold text-slate-900">
                ₹{property.price_per_hour}
              </span>
              <span className="text-xs text-slate-500">/ hour</span>
            </div>
            <div className="text-[10px] text-slate-400">
              ₹{property.price_per_half_day} half day • ₹{property.price_per_day} full day
            </div>
          </div>

          <Link
            to={`/properties/${property.id}`}
            className="px-3.5 py-1.5 rounded-lg bg-slate-900 text-white hover:bg-brand-600 text-xs font-semibold transition shadow-sm"
          >
            Details
          </Link>
        </div>
      </div>
    </div>
  );
};
