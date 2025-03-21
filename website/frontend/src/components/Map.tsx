import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Box, Paper } from '@mui/material';
import { Map as LeafletMap } from 'leaflet';

interface MapCompProps {
  latitude: number;
  longitude: number;
  zoom?: number;
  height?: string | number;
  width?: string | number;
}

const MapComp: React.FC<MapCompProps> = ({
  latitude,
  longitude,
  zoom = 15,
  height = 400,
  width = '100%'
}) => {
  const mapRef = useRef<LeafletMap | null>(null);

  // Handle map interactions and animations
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    // Disable all interactions
    map.dragging.disable();
    map.touchZoom.disable();
    map.doubleClickZoom.disable();
    map.scrollWheelZoom.disable();
    map.boxZoom.disable();
    map.keyboard.disable();
  }, [mapRef.current]);

  // Handle coordinate changes with animation
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    map.flyTo([latitude, longitude], map.getZoom(), {
      animate: true,
      duration: 1.5 // animation duration in seconds
    });
  }, [latitude, longitude]);

  return (
    <Paper
      elevation={3}
      sx={{
        borderRadius: '50%',
        overflow: 'hidden',
        width: typeof width === 'number' ? width : width,
        height: typeof height === 'number' ? height : height,
        aspectRatio: '1/1' // Forces a perfect circle
      }}
    >
      <Box sx={{
        height: '100%',
        width: '100%',
        overflow: 'hidden',
        borderRadius: '50%'
      }}>
        <MapContainer
          center={[latitude, longitude]}
          zoom={zoom}
          style={{ height: '100%', width: '100%' }}
          zoomControl={false}
          ref={mapRef}
        >
          <TileLayer
            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            // attribution="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
          />
        </MapContainer>
      </Box>
    </Paper>
  );
};

export default MapComp;
