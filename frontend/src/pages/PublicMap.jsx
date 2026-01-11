import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import api from '../api/axios';

const PublicMap = () => {
  const [points, setPoints] = useState([]);

  useEffect(() => {
    const fetchMap = async () => {
      try {
        const { data } = await api.get('/analytics/map-data');
        setPoints(data);
      } catch (err) { console.error(err); }
    };
    fetchMap();
  }, []);

  // Helper to determine color based on severity
  const getSeverityColor = (score) => {
    if (score >= 8) return '#ef4444'; // Red
    if (score >= 5) return '#f59e0b'; // Orange
    return '#10b981'; // Emerald
  };

  return (
    <div className="h-screen w-full bg-[#050a15] p-6">
      <div className="h-full rounded-[2.5rem] overflow-hidden border border-white/10 shadow-2xl relative">
        <div className="absolute top-6 left-6 z-[1000] bg-black/60 backdrop-blur-md p-4 rounded-2xl border border-white/10">
          <h2 className="text-white font-bold text-lg">Pune Severity Heatmap</h2>
          <p className="text-gray-400 text-xs mt-1">Real-time AI-triaged corruption reports</p>
        </div>

        <MapContainer center={[18.5204, 73.8567]} zoom={13} style={{ height: '100%', width: '100%', background: '#050a15' }}>
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; OpenStreetMap'
          />
          {points.map((p) => (
            <CircleMarker
              key={p.id}
              center={[18.5204 + (Math.random() - 0.5) * 0.05, 73.8567 + (Math.random() - 0.5) * 0.05]} // Simulating spread if loc is just a string
              radius={8 + p.severity}
              pathOptions={{
                fillColor: getSeverityColor(p.severity),
                color: 'white',
                weight: 1,
                fillOpacity: 0.6
              }}
            >
              <Tooltip direction="top" offset={[0, -10]} opacity={1}>
                <div className="font-sans font-bold">Severity: {p.severity}/10</div>
              </Tooltip>
              <Popup>
                <div className="p-2 font-sans">
                    <h3 className="font-bold text-gray-900 capitalize">{p.type}</h3>
                    <p className="text-xs text-gray-600 mt-1">{p.loc}</p>
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
};

export default PublicMap;