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

import db
from routes.auth import bp as auth_bp
from routes.bookings import bp as bookings_bp
from routes.user import bp as user_bp

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)


# ── API blueprints ────────────────────────────────────────────────────────────
app.register_blueprint(auth_bp,     url_prefix='/api/auth')
app.register_blueprint(user_bp,     url_prefix='/api/user')
app.register_blueprint(bookings_bp, url_prefix='/api/bookings')


# ── Static frontend ───────────────────────────────────────────────────────────
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve frontend files; fall back to index.html for client-side routing."""
    file_path = os.path.join(FRONTEND_DIR, path)
    if path and os.path.isfile(file_path):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, 'index.html')


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.getenv('PORT', 3001))

    db.init()
    print(f'\n  MediRush running at http://localhost:{port}\n')
    if not os.getenv('SMTP_HOST'):
        print('  SMTP not configured — OTPs will be printed to this console.\n')

    app.run(host='0.0.0.0', port=port, debug=False)
