import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Property } from '../types';

// Fix default leaflet pin icon paths in Vite
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom styled teal SVG pin
const createCustomIcon = (price: number, isSelected: boolean) => {
  return L.divIcon({
    className: 'custom-map-pin',
    html: `
      <div style="
        background-color: ${isSelected ? '#0f766e' : '#14b8a6'};
        color: white;
        padding: 4px 8px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 11px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        border: 2px solid white;
        white-space: nowrap;
        transform: translate(-50%, -100%);
        cursor: pointer;
        transition: transform 0.15s ease-in-out;
      ">
        ₹${price}/hr
      </div>
    `,
    iconSize: [40, 24],
    iconAnchor: [20, 24],
  });
};

interface PropertyMapProps {
  properties: Property[];
  selectedPropertyId?: number | null;
  onSelectProperty?: (id: number) => void;
  center?: [number, number];
  zoom?: number;
}

// Controller to smoothly pan when selectedPropertyId changes
const MapRecenter: React.FC<{ center: [number, number] }> = ({ center }) => {
  const map = useMap();
  useEffect(() => {
    map.setView(center, map.getZoom(), { animate: true });
  }, [center, map]);
  return null;
};

export const PropertyMap: React.FC<PropertyMapProps> = ({
  properties,
  selectedPropertyId,
  onSelectProperty,
  center = [13.02, 80.23], // Chennai centroid
  zoom = 12,
}) => {
  // If a property is selected, center on it
  const selectedProp = properties.find((p) => p.id === selectedPropertyId);
  const activeCenter: [number, number] = selectedProp
    ? [selectedProp.latitude, selectedProp.longitude]
    : center;

  return (
    <div className="w-full h-full min-h-[400px] rounded-xl overflow-hidden shadow-sm border border-slate-200">
      <MapContainer
        center={activeCenter}
        zoom={zoom}
        scrollWheelZoom={false}
        className="w-full h-full z-10"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapRecenter center={activeCenter} />

        {properties.map((property) => (
          <Marker
            key={property.id}
            position={[property.latitude, property.longitude]}
            icon={createCustomIcon(property.price_per_hour, property.id === selectedPropertyId)}
            eventHandlers={{
              click: () => onSelectProperty && onSelectProperty(property.id),
            }}
          >
            <Popup>
              <div className="p-1 max-w-[220px]">
                {property.images && property.images.length > 0 && (
                  <img
                    src={property.images[0]}
                    alt={property.title}
                    className="w-full h-24 object-cover rounded-md mb-2"
                  />
                )}
                <h4 className="font-bold text-sm text-slate-900 leading-tight mb-1">
                  {property.title}
                </h4>
                <p className="text-xs text-slate-500 mb-1">{property.neighbourhood}</p>
                <div className="flex items-center justify-between font-semibold text-xs text-slate-800">
                  <span>₹{property.price_per_hour}/hr</span>
                  <span className="text-amber-500">★ {property.average_rating || 'New'}</span>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};
