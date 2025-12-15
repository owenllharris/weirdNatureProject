#!/usr/bin/env python3
"""
Space Weather LED Web Simulator Server
=======================================

A simple Flask web server that:
1. Serves the HTML/CSS/JS files for the LED matrix simulator
2. Provides a /api/data endpoint that returns current space weather data
3. Can run standalone with simulated data OR integrate with real data

Usage:
    python web_server.py                    # Run with simulated data
    python web_server.py --live             # Use live data from NOAA
    python web_server.py --file output.json # Read from JSON file
    python web_server.py --port 8080        # Custom port

Author: Space Weather Lighting Project
"""

import json
import sys
import os
import argparse
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import random

# Add parent directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import our data modules (may not be available in all environments)
try:
    from solar_wind_fetcher import SolarWindFetcher
    from lighting_mapper import LightingMapper
    MODULES_AVAILABLE = True
except ImportError:
    print("⚠️  Warning: Could not import solar wind modules")
    print("   Will use simulated data only")
    MODULES_AVAILABLE = False


# ============================================
# FLASK APP SETUP
# ============================================

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for API access

# Global state
data_source = None  # Will be set based on command-line args
last_data = None    # Cache of most recent data


# ============================================
# DATA SOURCES
# ============================================

class SimulatedDataSource:
    """
    Generates simulated space weather data for testing.

    This creates realistic-looking data that changes over time,
    useful for development and demos when you don't have live data.
    """

    def __init__(self):
        self.time_offset = 0
        self.mapper = None
        if MODULES_AVAILABLE:
            self.mapper = LightingMapper()

    def get_data(self):
        """Generate simulated data."""
        # Simulate a slowly changing BZ value
        # This creates a wave pattern from -15 to +15 nT over time
        self.time_offset += 0.1
        bz = 10 * ((1 + 0.5 * random.random()) *
                   (1.5 * (0.5 - random.random())) *
                   (1 + 0.3 * random.random()))

        # Simulate speed variations
        speed = 400 + 150 * abs((self.time_offset / 10) % 2 - 1) + random.uniform(-20, 20)

        # Simulate density and temperature
        density = 5 + 10 * random.random()
        temperature = 100000 + 200000 * random.random()

        # Build raw data
        raw_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'bz': bz,
            'bx': random.uniform(-5, 5),
            'by': random.uniform(-5, 5),
            'bt': abs(bz) + random.uniform(2, 8),
            'speed': speed,
            'density': density,
            'temperature': temperature,
        }

        # Map to lighting if we have the mapper
        if self.mapper:
            return self.mapper.map_to_lighting(raw_data)
        else:
            # Fallback: create basic lighting parameters manually
            return self._create_basic_lighting(raw_data)

    def _create_basic_lighting(self, raw_data):
        """Create basic lighting parameters without the full mapper."""
        import colorsys

        bz = raw_data['bz']

        # Simple hue mapping
        if bz < -10:
            hue = 270
        elif bz < 0:
            hue = 240
        elif bz < 10:
            hue = 180
        else:
            hue = 60

        # Convert to RGB
        r, g, b = colorsys.hsv_to_rgb(hue / 360.0, 0.8, 0.9)

        return {
            'timestamp': raw_data['timestamp'],
            'raw': raw_data,
            'normalized': {
                'bz': 0.5,
                'speed': 0.5,
                'density': 0.5,
                'temperature': 0.5,
            },
            'lighting': {
                'hue': hue,
                'saturation': 80,
                'brightness': 90,
                'flow_rate': 0.5,
                'rgb': {
                    'r': int(r * 255),
                    'g': int(g * 255),
                    'b': int(b * 255),
                }
            }
        }


class FileDataSource:
    """
    Reads data from a JSON file (e.g., output.json from space_weather_monitor.py).
    """

    def __init__(self, filepath):
        self.filepath = Path(filepath)
        print(f"📁 Reading data from: {self.filepath}")

    def get_data(self):
        """Read data from the JSON file."""
        try:
            if not self.filepath.exists():
                print(f"⚠️  File not found: {self.filepath}")
                return None

            with open(self.filepath, 'r') as f:
                data = json.load(f)
                return data

        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON file: {e}")
            return None
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None


class LiveDataSource:
    """
    Fetches live data from NOAA APIs.
    """

    def __init__(self):
        if not MODULES_AVAILABLE:
            raise RuntimeError("Cannot use live data - modules not available")

        self.fetcher = SolarWindFetcher()
        self.mapper = LightingMapper()
        print("🛰️  Using live NOAA data")

    def get_data(self):
        """Fetch live data from NOAA."""
        solar_data = self.fetcher.get_combined_data()

        if solar_data is None:
            print("⚠️  Failed to fetch live data")
            return None

        return self.mapper.map_to_lighting(solar_data)


# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS)."""
    return send_from_directory('.', path)


@app.route('/api/data')
def get_data():
    """
    API endpoint that returns current space weather data.

    Returns JSON with the full data structure including:
    - raw: Raw measurements
    - lighting: Mapped lighting parameters
    - normalized: Normalized values
    """
    global last_data

    try:
        # Get data from the configured source
        data = data_source.get_data()

        if data is None:
            # If data fetch failed, return cached data or error
            if last_data:
                print("⚠️  Using cached data")
                return jsonify(last_data)
            else:
                return jsonify({
                    'error': 'No data available',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }), 503

        # Cache the data
        last_data = data

        return jsonify(data)

    except Exception as e:
        print(f"❌ Error in /api/data: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@app.route('/api/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'data_source': data_source.__class__.__name__,
        'timestamp': datetime.now(timezone.utc).isoformat()
    })


# ============================================
# MAIN
# ============================================

def main():
    """Main entry point."""
    global data_source

    parser = argparse.ArgumentParser(
        description="Web server for Space Weather LED Matrix Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Run with simulated data
  %(prog)s --live                   # Use live NOAA data
  %(prog)s --file output.json       # Read from JSON file
  %(prog)s --port 8080              # Custom port

Then open your browser to: http://localhost:5000
        """
    )

    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to run the web server on (default: 5000)'
    )

    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0 for all interfaces)'
    )

    # Data source options (mutually exclusive)
    source_group = parser.add_mutually_exclusive_group()

    source_group.add_argument(
        '--live',
        action='store_true',
        help='Fetch live data from NOAA APIs'
    )

    source_group.add_argument(
        '--file',
        type=str,
        metavar='PATH',
        help='Read data from a JSON file (e.g., output.json)'
    )

    args = parser.parse_args()

    # Set up data source
    if args.live:
        if not MODULES_AVAILABLE:
            print("❌ Error: Cannot use --live mode (modules not available)")
            print("   Install dependencies: pip install -r ../requirements.txt")
            sys.exit(1)
        data_source = LiveDataSource()
    elif args.file:
        data_source = FileDataSource(args.file)
    else:
        print("💡 Using simulated data (use --live or --file for real data)")
        data_source = SimulatedDataSource()

    # Print startup info
    print()
    print("="*70)
    print("🌌 SPACE WEATHER LED MATRIX WEB SIMULATOR")
    print("="*70)
    print(f"🌐 Server starting on http://{args.host}:{args.port}")
    print(f"📊 Data source: {data_source.__class__.__name__}")
    print()
    print("Open your browser to:")
    if args.host == '0.0.0.0':
        print(f"  - http://localhost:{args.port}")
        print(f"  - http://127.0.0.1:{args.port}")
    else:
        print(f"  - http://{args.host}:{args.port}")
    print()
    print("Press Ctrl+C to stop the server")
    print("="*70)
    print()

    # Run the server
    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=False,  # Set to True for development
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
