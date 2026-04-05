"""
gps_control.py — API endpoints for GPS tracking control and testing.

Provides REST endpoints to start/stop GPS tracking for ambulances,
register new ambulances, and simulate GPS module control.
"""

from flask import request, jsonify
from gps_tracker import gps_tracker
from hospital_database import hospital_db
import threading
import time

def init_gps_routes(app):
    """Initialize GPS control routes."""
    
    @app.route('/api/gps/register', methods=['POST'])
    def register_ambulance():
        """Register a new ambulance for GPS tracking."""
        data = request.get_json()
        ambulance_id = data.get('ambulance_id')
        
        if not ambulance_id:
            return jsonify({'error': 'ambulance_id required'}), 400
            
        # Get initial location if provided
        initial_location = None
        if data.get('latitude') and data.get('longitude'):
            initial_location = (data['latitude'], data['longitude'])
            
        gps_tracker.register_ambulance(ambulance_id, initial_location)
        
        return jsonify({
            'message': f'Ambulance {ambulance_id} registered for GPS tracking',
            'ambulance_id': ambulance_id
        })
    
    @app.route('/api/gps/start/<ambulance_id>', methods=['POST'])
    def start_tracking(ambulance_id):
        """Start GPS tracking for a specific ambulance."""
        gps_tracker.start_tracking(ambulance_id)
        return jsonify({
            'message': f'GPS tracking started for {ambulance_id}',
            'ambulance_id': ambulance_id
        })
    
    @app.route('/api/gps/stop/<ambulance_id>', methods=['POST'])
    def stop_tracking(ambulance_id):
        """Stop GPS tracking for a specific ambulance."""
        gps_tracker.stop_tracking(ambulance_id)
        return jsonify({
            'message': f'GPS tracking stopped for {ambulance_id}',
            'ambulance_id': ambulance_id
        })
    
    @app.route('/api/gps/location/<ambulance_id>', methods=['GET'])
    def get_location(ambulance_id):
        """Get current location of a specific ambulance."""
        location = gps_tracker.get_location(ambulance_id)
        if not location:
            return jsonify({'error': 'Ambulance not found or not tracking'}), 404
            
        return jsonify(location)
    
    @app.route('/api/gps/locations', methods=['GET'])
    def get_all_locations():
        """Get locations of all tracked ambulances."""
        locations = gps_tracker.get_all_locations()
        return jsonify(locations)
    
    @app.route('/api/gps/unregister/<ambulance_id>', methods=['DELETE'])
    def unregister_ambulance(ambulance_id):
        """Unregister an ambulance from GPS tracking."""
        gps_tracker.unregister_ambulance(ambulance_id)
        return jsonify({
            'message': f'Ambulance {ambulance_id} unregistered from GPS tracking',
            'ambulance_id': ambulance_id
        })
    
    @app.route('/api/gps/simulate_route', methods=['POST'])
    def simulate_route():
        """Simulate an ambulance route for testing."""
        data = request.get_json()
        ambulance_id = data.get('ambulance_id')
        waypoints = data.get('waypoints', [])
        
        if not ambulance_id:
            return jsonify({'error': 'ambulance_id required'}), 400
            
        if not waypoints:
            return jsonify({'error': 'waypoints required'}), 400
            
        # Start route simulation in background
        def run_simulation():
            for waypoint in waypoints:
                if ambulance_id in gps_tracker.ambulances:
                    gps_tracker.ambulances[ambulance_id].current_location = (
                        waypoint['latitude'], waypoint['longitude']
                    )
                    time.sleep(waypoint.get('delay', 2))
                    
        thread = threading.Thread(target=run_simulation, daemon=True)
        thread.start()
        
        return jsonify({
            'message': f'Route simulation started for {ambulance_id}',
            'ambulance_id': ambulance_id,
            'waypoints': len(waypoints)
        })
    
    @app.route('/api/hospitals', methods=['GET'])
    def get_hospitals():
        """Get all hospital information with GPS coordinates."""
        hospitals = hospital_db.get_hospitals_with_gps()
        return jsonify(hospitals)
    
    @app.route('/api/hospitals/nearest', methods=['POST'])
    def find_nearest_hospitals():
        """Find nearest hospitals to a given location."""
        data = request.get_json()
        lat = data.get('latitude')
        lng = data.get('longitude')
        limit = data.get('limit', 3)
        
        if not lat or not lng:
            return jsonify({'error': 'latitude and longitude required'}), 400
            
        nearest = hospital_db.find_nearest_hospitals(lat, lng, limit)
        
        result = []
        for hospital, distance in nearest:
            result.append({
                'id': hospital.id,
                'name': hospital.name,
                'location': hospital.location,
                'latitude': hospital.gps_coordinates[0] if hospital.gps_coordinates else None,
                'longitude': hospital.gps_coordinates[1] if hospital.gps_coordinates else None,
                'capacity': hospital.capacity,
                'current_patients': hospital.current_patients,
                'available_beds': hospital.capacity - hospital.current_patients,
                'distance_meters': distance,
                'specialties': list(hospital.specialties_required.keys())
            })
        
        return jsonify(result)
    
    return app
