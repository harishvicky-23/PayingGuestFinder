import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ChevronLeft, Plus, Check, MapPin, Sparkles } from 'lucide-react';
import { api } from '../../services/api';

const CHENNAI_COORDS: Record<string, [number, number]> = {
  Guindy: [13.0067, 80.2025],
  Velachery: [12.9756, 80.2206],
  Adyar: [13.0012, 80.2565],
  'T. Nagar': [13.0418, 80.2341],
  'Anna Nagar': [13.0850, 80.2101],
  Mylapore: [13.0368, 80.2676],
  'OMR (Thoraipakkam)': [12.9345, 80.2312],
  Nungambakkam: [13.0569, 80.2425],
};

const AMENITY_OPTIONS = [
  'wifi', 'air_conditioning', 'work_desk', 'power_backup',
  'parking', 'quiet_zone', 'private_restroom', 'coffee_tea'
];

const DEMO_PRESET_IMAGES = [
  { label: 'Executive Workspace', url: 'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80' },
  { label: 'Modern Studio Suite', url: 'https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=800&q=80' },
  { label: 'Private Guest Room', url: 'https://images.unsplash.com/photo-1598928506311-c55ded91a20c?auto=format&fit=crop&w=800&q=80' },
  { label: 'Quiet Garden Pod', url: 'https://images.unsplash.com/photo-1510798831971-661eb04b3739?auto=format&fit=crop&w=800&q=80' },
  { label: 'Entire City Apartment', url: 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80' },
];

export const CreatePropertyPage: React.FC = () => {
  const navigate = useNavigate();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [propertyType, setPropertyType] = useState('workspace_studio');
  const [neighbourhood, setNeighbourhood] = useState('Guindy');
  const [publicDesc, setPublicDesc] = useState('Near Guindy Metro and Olympia Tech Park');
  const [exactAddress, setExactAddress] = useState('Flat 302, Green Garden Enclave, Guindy, Chennai');
  const [priceHour, setPriceHour] = useState('300');
  const [priceHalfDay, setPriceHalfDay] = useState('1100');
  const [priceDay, setPriceDay] = useState('2000');
  const [maxGuests, setMaxGuests] = useState('2');
  const [amenities, setAmenities] = useState<string[]>(['wifi', 'air_conditioning', 'work_desk']);
  const [supportedDurations, setSupportedDurations] = useState<string[]>(['hourly', 'half_day', 'full_day']);
  const [houseRules, setHouseRules] = useState('No smoking. Maintain quiet hours after 10 PM.');
  const [selectedImage, setSelectedImage] = useState(DEMO_PRESET_IMAGES[0].url);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggleAmenity = (id: string) => {
    setAmenities((prev) =>
      prev.includes(id) ? prev.filter((a) => a !== id) : [...prev, id]
    );
  };

  const toggleDuration = (d: string) => {
    setSupportedDurations((prev) =>
      prev.includes(d) ? prev.filter((item) => item !== d) : [...prev, d]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const coords = CHENNAI_COORDS[neighbourhood] || [13.0, 80.2];

    try {
      await api.createProperty({
        title,
        description,
        property_type: propertyType,
        neighbourhood,
        latitude: coords[0],
        longitude: coords[1],
        public_location_description: publicDesc,
        exact_address: exactAddress,
        price_per_hour: parseFloat(priceHour),
        price_per_half_day: parseFloat(priceHalfDay),
        price_per_day: parseFloat(priceDay),
        maximum_guests: parseInt(maxGuests, 10),
        amenities,
        supported_durations: supportedDurations,
        house_rules: houseRules,
        images: [selectedImage],
        active: true,
      });

      navigate('/host/properties');
    } catch (err: any) {
      setError(err.message || 'Failed to create property.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 min-h-screen">
      <Link
        to="/host/properties"
        className="inline-flex items-center gap-1 text-xs font-semibold text-slate-500 hover:text-slate-900 mb-6 transition"
      >
        <ChevronLeft className="w-4 h-4" /> Back to My Listings
      </Link>

      <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 mb-1">List a New Space</h1>
          <p className="text-xs text-slate-500">
            Publish your room, desk, or property for short-duration rentals in Chennai.
          </p>
        </div>

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 text-red-800 rounded-xl text-xs font-semibold">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Title & Type */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="sm:col-span-2">
              <label className="block text-xs font-semibold text-slate-700 mb-1">Listing Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Quiet Work Pod near Guindy Metro"
                required
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Property Type</label>
              <select
                value={propertyType}
                onChange={(e) => setPropertyType(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-brand-500"
              >
                <option value="workspace_studio">Workspace Studio</option>
                <option value="private_room">Private Room</option>
                <option value="day_cabin">Quiet Pod</option>
                <option value="entire_apartment">Entire Apartment</option>
                <option value="guest_suite">Guest Suite</option>
              </select>
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Description</label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Highlight work ergonomics, internet speed, acoustic quietness, or layover transit comfort..."
              required
              className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>

          {/* Neighbourhood & Locations */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Neighbourhood (Chennai)</label>
              <select
                value={neighbourhood}
                onChange={(e) => setNeighbourhood(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-brand-500"
              >
                {Object.keys(CHENNAI_COORDS).map((area) => (
                  <option key={area} value={area}>{area}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Public General Location</label>
              <input
                type="text"
                value={publicDesc}
                onChange={(e) => setPublicDesc(e.target.value)}
                placeholder="e.g. 5 mins from Phoenix MarketCity"
                required
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-brand-500"
              />
            </div>
          </div>

          {/* Exact Address (Protected) */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Exact Address (Kept confidential until booking is confirmed)
            </label>
            <input
              type="text"
              value={exactAddress}
              onChange={(e) => setExactAddress(e.target.value)}
              placeholder="Full street address and door number"
              required
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>

          {/* Pricing Row */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 pt-2 border-t border-slate-100">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Hourly Rate (₹)</label>
              <input
                type="number"
                min="50"
                value={priceHour}
                onChange={(e) => setPriceHour(e.target.value)}
                required
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-medium text-slate-800"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Half Day Rate (₹)</label>
              <input
                type="number"
                min="100"
                value={priceHalfDay}
                onChange={(e) => setPriceHalfDay(e.target.value)}
                required
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-medium text-slate-800"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Full Day Rate (₹)</label>
              <input
                type="number"
                min="200"
                value={priceDay}
                onChange={(e) => setPriceDay(e.target.value)}
                required
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-medium text-slate-800"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Max Guests</label>
              <input
                type="number"
                min="1"
                max="10"
                value={maxGuests}
                onChange={(e) => setMaxGuests(e.target.value)}
                required
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-medium text-slate-800"
              />
            </div>
          </div>

          {/* Amenities & Durations */}
          <div className="space-y-4 pt-2 border-t border-slate-100">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-2">Amenities</label>
              <div className="flex flex-wrap gap-2">
                {AMENITY_OPTIONS.map((a) => {
                  const checked = amenities.includes(a);
                  return (
                    <button
                      key={a}
                      type="button"
                      onClick={() => toggleAmenity(a)}
                      className={`text-xs px-3 py-1.5 rounded-full border transition capitalize ${
                        checked
                          ? 'bg-brand-500 text-white border-brand-500 font-semibold'
                          : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
                      }`}
                    >
                      {a.replace(/_/g, ' ')}
                    </button>
                  );
                })}
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-2">Supported Durations</label>
              <div className="flex flex-wrap gap-2">
                {['hourly', 'half_day', 'full_day', 'multi_day'].map((d) => {
                  const checked = supportedDurations.includes(d);
                  return (
                    <button
                      key={d}
                      type="button"
                      onClick={() => toggleDuration(d)}
                      className={`text-xs px-3 py-1.5 rounded-full border transition capitalize ${
                        checked
                          ? 'bg-brand-500 text-white border-brand-500 font-semibold'
                          : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
                      }`}
                    >
                      {d.replace(/_/g, ' ')}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Demo Image Picker */}
          <div className="pt-2 border-t border-slate-100">
            <label className="block text-xs font-semibold text-slate-700 mb-2">Select Demonstration Photograph</label>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
              {DEMO_PRESET_IMAGES.map((preset, idx) => (
                <div
                  key={idx}
                  onClick={() => setSelectedImage(preset.url)}
                  className={`rounded-xl overflow-hidden border cursor-pointer transition ${
                    selectedImage === preset.url
                      ? 'border-brand-500 ring-2 ring-brand-400/40 shadow-sm'
                      : 'border-slate-200 hover:opacity-80'
                  }`}
                >
                  <img src={preset.url} alt={preset.label} className="w-full h-16 object-cover" />
                  <span className="block text-[10px] text-center font-medium p-1 text-slate-700 truncate">
                    {preset.label}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Submit */}
          <div className="pt-4 border-t border-slate-100 flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 bg-brand-500 hover:bg-brand-600 text-white font-bold rounded-xl text-xs shadow-md transition disabled:opacity-50"
            >
              {loading ? 'Publishing...' : 'Publish Space Listing'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
