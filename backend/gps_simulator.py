"""
gps_simulator.py — Command-line GPS module simulator for testing.

Simulates a hardware GPS module that can be used to test the ambulance
tracking system. Provides a simple CLI interface to control ambulance
movement and send GPS coordinates to the tracking system.
"""

import requests
import time
import random
import json
import threading
from typing import List, Tuple

class GPSModuleSimulator:
    """Simulates a hardware GPS module for testing purposes."""
    
    def __init__(self, base_url: str = "http://localhost:3001"):
        self.base_url = base_url
        self.ambulance_id = None
        self.is_running = False
        self.current_location = None
        
    def register_ambulance(self, ambulance_id: str, initial_lat: float = 12.9716, initial_lng: float = 77.5946):
        """Register an ambulance with the tracking system."""
        self.ambulance_id = ambulance_id
        self.current_location = (initial_lat, initial_lng)
        
        try:
            response = requests.post(f"{self.base_url}/api/gps/register", json={
                'ambulance_id': ambulance_id,
                'latitude': initial_lat,
                'longitude': initial_lng
            })
            
            if response.status_code == 200:
                print(f"✓ Ambulance {ambulance_id} registered successfully")
                return True
            else:
                print(f"✗ Failed to register ambulance: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection error: {e}")
            return False
    
    def start_tracking(self):
        """Start GPS tracking for the registered ambulance."""
        if not self.ambulance_id:
            print("✗ No ambulance registered. Use register_ambulance() first.")
            return False
            
        try:
            response = requests.post(f"{self.base_url}/api/gps/start/{self.ambulance_id}")
            
            if response.status_code == 200:
                print(f"✓ GPS tracking started for {self.ambulance_id}")
                self.is_running = True
                return True
            else:
                print(f"✗ Failed to start tracking: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection error: {e}")
            return False
    
    def stop_tracking(self):
        """Stop GPS tracking."""
        if not self.ambulance_id:
            return False
            
        try:
            response = requests.post(f"{self.base_url}/api/gps/stop/{self.ambulance_id}")
            
            if response.status_code == 200:
                print(f"✓ GPS tracking stopped for {self.ambulance_id}")
                self.is_running = False
                return True
            else:
                print(f"✗ Failed to stop tracking: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection error: {e}")
            return False
    
    def simulate_movement(self, duration_minutes: int = 5, speed_factor: float = 1.0):
        """Simulate realistic ambulance movement."""
        if not self.is_running:
            print("✗ Tracking not started. Use start_tracking() first.")
            return
            
        print(f"🚑 Simulating movement for {duration_minutes} minutes...")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while time.time() < end_time and self.is_running:
            # Simulate movement: small random changes in coordinates
            lat_change = random.uniform(-0.0005, 0.0005) * speed_factor  # ~50m per update
            lng_change = random.uniform(-0.0005, 0.0005) * speed_factor
            
            new_lat = self.current_location[0] + lat_change
            new_lng = self.current_location[1] + lng_change
            
            # Keep within reasonable bounds (Bangalore area)
            new_lat = max(12.8, min(13.1, new_lat))
            new_lng = max(77.4, min(77.8, new_lng))
            
            self.current_location = (new_lat, new_lng)
            
            # The GPS tracker module will automatically update the location
            # since we're using the built-in simulation
            print(f"📍 Location updated: {new_lat:.6f}, {new_lng:.6f}")
            
            # Update every 2 seconds (realistic GPS update rate)
            time.sleep(2)
        
        print("✓ Movement simulation completed")
    
    def simulate_route_to_hospital(self, hospital_lat: float = 12.9352, hospital_lng: float = 77.6244):
        """Simulate a route from current location to hospital."""
        if not self.is_running:
            print("✗ Tracking not started. Use start_tracking() first.")
            return
            
        print(f"🏥 Simulating route to hospital at {hospital_lat}, {hospital_lng}")
        
        # Generate waypoints along the route
        waypoints = []
        steps = 20  # Number of waypoints
        
        for i in range(steps + 1):
            progress = i / steps
            lat = self.current_location[0] + (hospital_lat - self.current_location[0]) * progress
            lng = self.current_location[1] + (hospital_lng - self.current_location[1]) * progress
            
            waypoints.append({
                'latitude': lat,
                'longitude': lng,
                'delay': 3  # 3 seconds between waypoints
            })
        
        try:
            response = requests.post(f"{self.base_url}/api/gps/simulate_route", json={
                'ambulance_id': self.ambulance_id,
                'waypoints': waypoints
            })
            
            if response.status_code == 200:
                print(f"✓ Route simulation started for {self.ambulance_id}")
                print(f"📍 Route has {len(waypoints)} waypoints")
            else:
                print(f"✗ Failed to start route simulation: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection error: {e}")
    
    def get_current_status(self):
        """Get current tracking status."""
        if not self.ambulance_id:
            print("✗ No ambulance registered")
            return
            
        try:
            response = requests.get(f"{self.base_url}/api/gps/location/{self.ambulance_id}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Status for {self.ambulance_id}:")
                print(f"   Location: {data['latitude']:.6f}, {data['longitude']:.6f}")
                print(f"   Active: {data['active']}")
                print(f"   Last Update: {data['timestamp']}")
            else:
                print(f"✗ Failed to get status: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection error: {e}")

def main():
    """Interactive CLI for GPS simulator."""
    simulator = GPSModuleSimulator()
    
    print("🚑 MediRush GPS Module Simulator")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Register ambulance")
        print("2. Start tracking")
        print("3. Stop tracking")
        print("4. Simulate movement")
        print("5. Simulate route to hospital")
        print("6. Get status")
        print("7. Exit")
        
        choice = input("\nEnter choice (1-7): ").strip()
        
        if choice == '1':
            ambulance_id = input("Enter ambulance ID (e.g., AMB-001): ").strip()
            if ambulance_id:
                simulator.register_ambulance(ambulance_id)
                
        elif choice == '2':
            simulator.start_tracking()
            
        elif choice == '3':
            simulator.stop_tracking()
            
        elif choice == '4':
            duration = input("Enter duration in minutes (default 5): ").strip()
            duration = int(duration) if duration.isdigit() else 5
            simulator.simulate_movement(duration)
            
        elif choice == '5':
            simulator.simulate_route_to_hospital()
            
        elif choice == '6':
            simulator.get_current_status()
            
        elif choice == '7':
            print("👋 Exiting GPS simulator")
            break
            
        else:
            print("✗ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
