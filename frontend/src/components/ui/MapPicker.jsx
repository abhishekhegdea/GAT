import React, { useState } from 'react';
import { MapContainer, TileLayer, Circle, Marker, useMapEvents } from 'react-leaflet';

const LocationSelector = ({ onSelect }) => {
  useMapEvents({
    click(e) { onSelect(e.latlng); }
  });
  return null;
};

const MapPicker = ({ center = { lat: 28.6139, lng: 77.2090 }, radius = 100, onChange }) => {
  const [pos, setPos] = useState(center);
  const [rad, setRad] = useState(radius);

  const handleSelect = (latlng) => {
    setPos(latlng);
    onChange && onChange({ center: latlng, radius: rad });
  };

  return (
    <div className="card p-4">
      <div className="text-white font-semibold mb-2">Class Location</div>
      <MapContainer center={pos} zoom={16} style={{ height: 300, width: '100%' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <LocationSelector onSelect={handleSelect} />
        <Marker position={pos} />
        <Circle center={pos} radius={rad} pathOptions={{ color: '#1F3C88' }} />
      </MapContainer>
      <div className="mt-3">
        <label className="text-sm text-gray-300">Radius: {rad} m</label>
        <input type="range" min={50} max={500} value={rad} onChange={(e) => { const v = Number(e.target.value); setRad(v); onChange && onChange({ center: pos, radius: v }); }} className="w-full" />
      </div>
    </div>
  );
};

export default MapPicker;
