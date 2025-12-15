#!/usr/bin/env python3
"""
Solar Wind Data Fetcher
=======================

Fetches real-time solar wind data from NOAA's Space Weather Prediction Center.

The DSCOVR satellite sits at the L1 Lagrange point (between Earth and Sun)
and measures the solar wind before it hits Earth's magnetosphere. This data
is crucial for predicting auroras and geomagnetic storms!

Data Sources:
- Plasma data: particle speed, density, temperature
- Magnetometer data: magnetic field strength and direction (BZ is key!)

Author: Space Weather Lighting Project
"""

import requests
import json
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
import time


class SolarWindFetcher:
    """
    Fetches and parses solar wind data from NOAA SWPC.

    The two main data streams are:
    1. PLASMA: Speed, density, temperature of solar wind particles
    2. MAG: Magnetic field measurements (Bx, By, Bz components)

    BZ is the MOST IMPORTANT value - negative BZ can trigger auroras!
    """

    # NOAA SWPC API endpoints
    PLASMA_URL = "https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json"
    MAG_URL = "https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json"

    def __init__(self, timeout: int = 10):
        """
        Initialize the fetcher.

        Args:
            timeout: HTTP request timeout in seconds (default: 10)
        """
        self.timeout = timeout
        self.last_plasma_data = None
        self.last_mag_data = None
        self.last_fetch_time = None

    def fetch_plasma_data(self) -> Optional[Dict]:
        """
        Fetch plasma data (speed, density, temperature).

        Returns:
            Dictionary with latest plasma measurements, or None if fetch failed

        Format of NOAA data:
        - First row is column headers: ["time_tag", "density", "speed", "temperature"]
        - Subsequent rows are measurements, one per minute
        - We want the LATEST (most recent) measurement
        """
        try:
            response = requests.get(self.PLASMA_URL, timeout=self.timeout)
            response.raise_for_status()  # Raise exception for bad status codes

            data = response.json()

            # Data format: [[headers], [row1], [row2], ...]
            # Skip the header row and get the most recent data point
            if len(data) < 2:
                print("⚠️  Warning: Plasma data is empty or incomplete")
                return None

            # Get the latest measurement (last row)
            latest = data[-1]

            # Parse the data
            # Note: Sometimes values can be None/null if sensor has issues
            return {
                'timestamp': latest[0],  # ISO 8601 timestamp
                'density': float(latest[1]) if latest[1] is not None else None,  # particles/cm³
                'speed': float(latest[2]) if latest[2] is not None else None,     # km/s
                'temperature': float(latest[3]) if latest[3] is not None else None  # Kelvin
            }

        except requests.exceptions.Timeout:
            print("❌ Error: NOAA plasma API request timed out")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching plasma data: {e}")
            return None
        except (ValueError, IndexError, KeyError) as e:
            print(f"❌ Error parsing plasma data: {e}")
            return None

    def fetch_mag_data(self) -> Optional[Dict]:
        """
        Fetch magnetometer data (magnetic field measurements).

        Returns:
            Dictionary with latest magnetic field measurements, or None if fetch failed

        The magnetic field has three components:
        - BX: Sun-Earth direction
        - BY: East-West direction
        - BZ: North-South direction (THIS IS THE KEY ONE!)

        NEGATIVE BZ = Magnetic field pointing south = Can trigger auroras! 🌌
        POSITIVE BZ = Magnetic field pointing north = Quiet conditions
        """
        try:
            response = requests.get(self.MAG_URL, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # Data format: [[headers], [row1], [row2], ...]
            if len(data) < 2:
                print("⚠️  Warning: Magnetometer data is empty or incomplete")
                return None

            # Get the latest measurement (last row)
            latest = data[-1]

            # Parse the data
            # Headers: ["time_tag", "bx_gsm", "by_gsm", "bz_gsm", "lon_gsm", "lat_gsm", "bt"]
            return {
                'timestamp': latest[0],  # ISO 8601 timestamp
                'bx': float(latest[1]) if latest[1] is not None else None,  # nT (nanoTesla)
                'by': float(latest[2]) if latest[2] is not None else None,  # nT
                'bz': float(latest[3]) if latest[3] is not None else None,  # nT - THE IMPORTANT ONE!
                'bt': float(latest[6]) if latest[6] is not None else None   # Total field strength
            }

        except requests.exceptions.Timeout:
            print("❌ Error: NOAA magnetometer API request timed out")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching magnetometer data: {e}")
            return None
        except (ValueError, IndexError, KeyError) as e:
            print(f"❌ Error parsing magnetometer data: {e}")
            return None

    def fetch_all(self) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Fetch both plasma and magnetometer data.

        Returns:
            Tuple of (plasma_data, mag_data)
            Either or both can be None if fetch failed
        """
        plasma = self.fetch_plasma_data()
        mag = self.fetch_mag_data()

        # Cache the results
        if plasma:
            self.last_plasma_data = plasma
        if mag:
            self.last_mag_data = mag

        self.last_fetch_time = datetime.now(timezone.utc)

        return plasma, mag

    def get_combined_data(self) -> Optional[Dict]:
        """
        Fetch and combine plasma + magnetometer data into one dictionary.

        Returns:
            Combined data dictionary with all measurements, or None if both fetches failed
        """
        plasma, mag = self.fetch_all()

        # If both failed, try to use cached data
        if plasma is None and mag is None:
            print("⚠️  Warning: Both APIs failed, using cached data if available")
            plasma = self.last_plasma_data
            mag = self.last_mag_data

        # If we still have nothing, give up
        if plasma is None and mag is None:
            print("❌ Error: No data available (no cached data either)")
            return None

        # Combine the data
        # Use the magnetometer timestamp as primary (it's usually the critical measurement)
        timestamp = (mag['timestamp'] if mag else plasma['timestamp'])

        combined = {
            'timestamp': timestamp,
            'bz': mag['bz'] if mag and mag['bz'] is not None else None,
            'bx': mag['bx'] if mag and mag['bx'] is not None else None,
            'by': mag['by'] if mag and mag['by'] is not None else None,
            'bt': mag['bt'] if mag and mag['bt'] is not None else None,
            'speed': plasma['speed'] if plasma and plasma['speed'] is not None else None,
            'density': plasma['density'] if plasma and plasma['density'] is not None else None,
            'temperature': plasma['temperature'] if plasma and plasma['temperature'] is not None else None,
        }

        return combined

    def print_status(self, data: Dict):
        """
        Pretty-print the current solar wind status.

        Args:
            data: Combined data dictionary
        """
        print("\n" + "="*60)
        print("🌞 SOLAR WIND STATUS 🌍")
        print("="*60)
        print(f"Timestamp: {data['timestamp']}")
        print()

        # Magnetic field (the exciting part!)
        print("🧲 MAGNETIC FIELD:")
        if data['bz'] is not None:
            bz = data['bz']
            if bz < -5:
                status = "⚡ STRONG SOUTHWARD - Aurora likely!"
            elif bz < 0:
                status = "🌌 Southward - Aurora possible"
            elif bz < 5:
                status = "😴 Quiet - No aurora activity"
            else:
                status = "☀️ Strong northward - Very quiet"
            print(f"  BZ: {bz:+.1f} nT  {status}")
        else:
            print(f"  BZ: No data")

        if data['bt'] is not None:
            print(f"  Total field: {data['bt']:.1f} nT")
        print()

        # Solar wind conditions
        print("💨 SOLAR WIND:")
        if data['speed'] is not None:
            speed = data['speed']
            if speed > 600:
                status = "🚀 Very fast!"
            elif speed > 500:
                status = "⚡ Fast"
            elif speed > 400:
                status = "→ Moderate"
            else:
                status = "🐌 Slow"
            print(f"  Speed: {speed:.0f} km/s  {status}")
        else:
            print(f"  Speed: No data")

        if data['density'] is not None:
            print(f"  Density: {data['density']:.1f} particles/cm³")
        if data['temperature'] is not None:
            print(f"  Temperature: {data['temperature']:,.0f} K")

        print("="*60 + "\n")


# Quick test if run directly
if __name__ == "__main__":
    print("🛰️  Testing NOAA Space Weather Data Fetcher...\n")

    fetcher = SolarWindFetcher()
    data = fetcher.get_combined_data()

    if data:
        fetcher.print_status(data)
        print("\n📊 Raw data:")
        print(json.dumps(data, indent=2))
    else:
        print("❌ Failed to fetch data from NOAA")
