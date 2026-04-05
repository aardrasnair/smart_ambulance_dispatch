"""
gps_tracker.py — GPS tracking module for ambulance location monitoring.

Handles real-time GPS data from hardware modules, manages ambulance locations,
and provides location updates to the WebSocket system.
"""

import time
import threading
import random
from datetime import datetime
from typing import Dict, Optional, Tuple, List
import json

class GPSModule:
    """Simulates a hardware GPS module for development/testing."""
    
    def __init__(self, ambulance_id: str, initial_location: Tuple[float, float] = None):
        self.ambulance_id = ambulance_id
        self.current_location = initial_location or (12.9716, 77.5946)  # Bangalore default
        self.is_active = False
        self._thread = None
        self._stop_event = threading.Event()
        
    def start_tracking(self):
        """Start GPS tracking simulation."""
        if self.is_active:
            return
            
        self.is_active = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._simulate_movement)
        self._thread.daemon = True
        self._thread.start()
        print(f"GPS tracking started for ambulance {self.ambulance_id}")
        
    def stop_tracking(self):
        """Stop GPS tracking simulation."""
        self.is_active = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)
        print(f"GPS tracking stopped for ambulance {self.ambulance_id}")
        
    def get_current_location(self) -> Tuple[float, float]:
        """Get current GPS coordinates."""
        return self.current_location
        
    def _simulate_movement(self):
        """Simulate realistic ambulance movement."""
        while not self._stop_event.is_set():
            # Simulate movement: small random changes in coordinates
            lat_change = random.uniform(-0.001, 0.001)  # ~100m
            lng_change = random.uniform(-0.001, 0.001)  # ~100m
            
            new_lat = self.current_location[0] + lat_change
            new_lng = self.current_location[1] + lng_change
            
            # Keep within reasonable bounds (Bangalore area)
            new_lat = max(12.8, min(13.1, new_lat))
            new_lng = max(77.4, min(77.8, new_lng))
            
            self.current_location = (new_lat, new_lng)
            
            # Update every 2 seconds (realistic GPS update rate)
            time.sleep(2)

class GPSTracker:
    """Central GPS tracking system for all ambulances and hospitals."""
    
    def __init__(self):
        self.ambulances: Dict[str, GPSModule] = {}
        self.hospitals: List[Dict] = []
        self.location_callbacks = []
        
    def set_hospitals(self, hospitals: List[Dict]):
        """Set hospital locations for GPS tracking."""
        self.hospitals = hospitals
        
    def register_ambulance(self, ambulance_id: str, initial_location: Tuple[float, float] = None):
        """Register a new ambulance for GPS tracking."""
        if ambulance_id not in self.ambulances:
            gps_module = GPSModule(ambulance_id, initial_location)
            self.ambulances[ambulance_id] = gps_module
            print(f"Registered ambulance {ambulance_id} for GPS tracking")
            
    def unregister_ambulance(self, ambulance_id: str):
        """Unregister an ambulance from GPS tracking."""
        if ambulance_id in self.ambulances:
            self.ambulances[ambulance_id].stop_tracking()
            del self.ambulances[ambulance_id]
            print(f"Unregistered ambulance {ambulance_id} from GPS tracking")
            
    def start_tracking(self, ambulance_id: str):
        """Start tracking a specific ambulance."""
        if ambulance_id in self.ambulances:
            self.ambulances[ambulance_id].start_tracking()
            
    def stop_tracking(self, ambulance_id: str):
        """Stop tracking a specific ambulance."""
        if ambulance_id in self.ambulances:
            self.ambulances[ambulance_id].stop_tracking()
            
    def get_location(self, ambulance_id: str) -> Optional[Dict]:
        """Get current location of an ambulance."""
        if ambulance_id in self.ambulances:
            lat, lng = self.ambulances[ambulance_id].get_current_location()
            return {
                'ambulance_id': ambulance_id,
                'latitude': lat,
                'longitude': lng,
                'timestamp': datetime.utcnow().isoformat(),
                'active': self.ambulances[ambulance_id].is_active
            }
        return None
        
    def get_all_locations(self) -> Dict[str, Dict]:
        """Get locations of all tracked ambulances."""
        locations = {}
        for ambulance_id in self.ambulances:
            location = self.get_location(ambulance_id)
            if location:
                locations[ambulance_id] = location
        return locations
    
    def get_all_hospitals(self) -> List[Dict]:
        """Get all hospital locations."""
        return self.hospitals
        
    def add_location_callback(self, callback):
        """Add callback function for location updates."""
        self.location_callbacks.append(callback)
        
    def _notify_location_update(self, ambulance_id: str, location_data: Dict):
        """Notify all registered callbacks about location update."""
        for callback in self.location_callbacks:
            try:
                callback(ambulance_id, location_data)
            except Exception as e:
                print(f"Error in location callback: {e}")

# Global GPS tracker instance
gps_tracker = GPSTracker()
