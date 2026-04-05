"""
app.py — MediRush Flask application.

Serves the frontend as static files and mounts all API blueprints.

Usage:
    python app.py
    # → http://localhost:3001
"""

import os
import sys

from dotenv import load_dotenv

# Load .env before anything else
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Allow imports from backend/ directory
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit

import db
from routes.auth import bp as auth_bp
from routes.bookings import bp as bookings_bp
from routes.user import bp as user_bp
from routes.gps_control import init_gps_routes
from gps_tracker import gps_tracker
from hospital_database import hospital_db

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")


# ── API blueprints ────────────────────────────────────────────────────────────
app.register_blueprint(auth_bp,     url_prefix='/api/auth')
app.register_blueprint(user_bp,     url_prefix='/api/user')
app.register_blueprint(bookings_bp, url_prefix='/api/bookings')

# Initialize GPS control routes
init_gps_routes(app)


# ── Static frontend ───────────────────────────────────────────────────────────
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve frontend files; fall back to index.html for client-side routing."""
    file_path = os.path.join(FRONTEND_DIR, path)
    if path and os.path.isfile(file_path):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, 'index.html')


# ── WebSocket GPS tracking ─────────────────────────────────────────────────────
@socketio.on('connect')
def handle_connect():
    """Handle client connection for GPS tracking."""
    print('Client connected to GPS tracking')
    emit('gps_locations', gps_tracker.get_all_locations())
    emit('hospital_locations', gps_tracker.get_all_hospitals())

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected from GPS tracking')

@socketio.on('request_location')
def handle_location_request(data):
    """Handle location request for specific ambulance."""
    ambulance_id = data.get('ambulance_id')
    if ambulance_id:
        location = gps_tracker.get_location(ambulance_id)
        emit('location_update', location)

def broadcast_location_updates():
    """Background thread to broadcast GPS updates."""
    import time
    while True:
        locations = gps_tracker.get_all_locations()
        socketio.emit('gps_locations', locations)
        time.sleep(3)  # Update every 3 seconds


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import threading
    
    port = int(os.getenv('PORT', 3001))

    db.init()
    
    # Start GPS location broadcast thread
    gps_thread = threading.Thread(target=broadcast_location_updates, daemon=True)
    gps_thread.start()
    
    # Register a demo ambulance for testing
    gps_tracker.register_ambulance('AMB-001', (12.9716, 77.5946))
    gps_tracker.start_tracking('AMB-001')
    
    # Load hospital locations into GPS tracker
    gps_tracker.set_hospitals(hospital_db.get_hospitals_with_gps())
    
    print(f'\n  MediRush running at http://localhost:{port}\n')
    print('  GPS tracking enabled with demo ambulance AMB-001\n')
    if not os.getenv('SMTP_HOST'):
        print('  SMTP not configured — OTPs will be printed to this console.\n')

    socketio.run(app, host='0.0.0.0', port=port, debug=False)
