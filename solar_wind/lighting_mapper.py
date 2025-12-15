#!/usr/bin/env python3
"""
Solar Wind to Lighting Mapper
==============================

Translates solar wind data into lighting parameters.

This is where the magic happens! We take raw space weather measurements
and turn them into beautiful, meaningful colors and animations.

The key concept:
- NEGATIVE BZ (southward magnetic field) = Aurora conditions = Cool blues/purples
- POSITIVE BZ (northward magnetic field) = Quiet conditions = Warm yellows/oranges
- SPEED affects brightness and flow rate
- DENSITY affects saturation/intensity

Author: Space Weather Lighting Project
"""

import math
from typing import Dict, Optional
import colorsys


class LightingMapper:
    """
    Maps solar wind data to lighting parameters.

    This class takes raw solar wind measurements and converts them into
    values that can control LED lights, creating a visual representation
    of space weather conditions.
    """

    # === CONFIGURATION CONSTANTS ===
    # These define the "normal" ranges for each measurement
    # You can adjust these based on what looks good!

    # BZ range (nanoTesla) - the magnetic field north-south component
    # Typical range: -20 to +20 nT
    # Extreme values can go beyond this
    BZ_MIN = -20.0
    BZ_MAX = 20.0

    # Solar wind speed range (km/s)
    # Typical: 300-500 km/s
    # Fast: 500-700 km/s
    # Extreme: 700+ km/s
    SPEED_MIN = 300.0
    SPEED_MAX = 700.0

    # Particle density (particles per cubic centimeter)
    # Typical: 3-10 /cm³
    # High: 10-30 /cm³
    DENSITY_MIN = 1.0
    DENSITY_MAX = 30.0

    # Temperature (Kelvin)
    # Typical: 50,000 - 500,000 K (yes, really hot!)
    TEMP_MIN = 50000.0
    TEMP_MAX = 500000.0

    def __init__(self):
        """Initialize the mapper with default settings."""
        self.last_values = None  # For smoothing/fallback

    def normalize(self, value: float, min_val: float, max_val: float,
                  clamp: bool = True) -> float:
        """
        Normalize a value to 0-1 range.

        Args:
            value: The value to normalize
            min_val: Minimum of the expected range
            max_val: Maximum of the expected range
            clamp: If True, clamp result to 0-1 (default: True)

        Returns:
            Normalized value between 0 and 1
        """
        if value is None:
            return 0.5  # Return middle value if data is missing

        # Normalize to 0-1
        normalized = (value - min_val) / (max_val - min_val)

        # Optionally clamp to 0-1
        if clamp:
            normalized = max(0.0, min(1.0, normalized))

        return normalized

    def bz_to_hue(self, bz: Optional[float]) -> int:
        """
        Convert BZ magnetic field to color hue.

        This is the MAIN visual effect!

        BZ negative (southward) → Blue/Purple (aurora colors!)
        BZ positive (northward) → Yellow/Orange (quiet/calm)
        BZ near zero → Green/Cyan (transition)

        Args:
            bz: BZ value in nanoTesla

        Returns:
            Hue value (0-360 degrees)
            - 0° = Red
            - 60° = Yellow
            - 120° = Green
            - 180° = Cyan
            - 240° = Blue
            - 300° = Magenta
        """
        if bz is None:
            return 180  # Default to cyan if no data

        # Normalize BZ to 0-1 (0 = very negative, 1 = very positive)
        normalized_bz = self.normalize(bz, self.BZ_MIN, self.BZ_MAX)

        # Map to hue:
        # 0.0 (very negative BZ) → 270° (purple/violet) - AURORA!
        # 0.5 (neutral BZ)       → 180° (cyan)
        # 1.0 (very positive BZ) → 30° (orange/yellow) - CALM

        if normalized_bz < 0.5:
            # Negative BZ: Map 0.0-0.5 to 270°-180° (purple to cyan)
            hue = 270 - (normalized_bz * 180)
        else:
            # Positive BZ: Map 0.5-1.0 to 180°-30° (cyan to orange)
            hue = 180 - ((normalized_bz - 0.5) * 300)

        return int(hue)

    def speed_to_brightness(self, speed: Optional[float]) -> int:
        """
        Convert solar wind speed to brightness.

        Faster wind = brighter lights!

        Args:
            speed: Solar wind speed in km/s

        Returns:
            Brightness percentage (0-100)
        """
        if speed is None:
            return 50  # Default to medium brightness

        # Normalize speed
        normalized = self.normalize(speed, self.SPEED_MIN, self.SPEED_MAX)

        # Map to brightness with a minimum of 20% so lights don't go too dim
        brightness = 20 + (normalized * 80)

        return int(brightness)

    def density_to_saturation(self, density: Optional[float]) -> int:
        """
        Convert particle density to color saturation.

        Higher density = more saturated (vivid) colors
        Lower density = more pastel colors

        Args:
            density: Particle density in particles/cm³

        Returns:
            Saturation percentage (0-100)
        """
        if density is None:
            return 70  # Default to fairly saturated

        # Normalize density
        normalized = self.normalize(density, self.DENSITY_MIN, self.DENSITY_MAX)

        # Map to saturation with a minimum of 40% so colors stay visible
        saturation = 40 + (normalized * 60)

        return int(saturation)

    def speed_to_flow_rate(self, speed: Optional[float]) -> float:
        """
        Convert solar wind speed to animation flow rate.

        This can control how fast patterns move/animate.

        Args:
            speed: Solar wind speed in km/s

        Returns:
            Flow rate (0.0-1.0)
        """
        if speed is None:
            return 0.5  # Default to medium flow

        return self.normalize(speed, self.SPEED_MIN, self.SPEED_MAX)

    def map_to_lighting(self, solar_data: Dict) -> Dict:
        """
        Convert raw solar wind data to lighting parameters.

        This is the main function that does the full mapping!

        Args:
            solar_data: Dictionary with raw solar wind measurements

        Returns:
            Dictionary with normalized values and lighting parameters
        """
        # Extract raw values
        bz = solar_data.get('bz')
        speed = solar_data.get('speed')
        density = solar_data.get('density')
        temperature = solar_data.get('temperature')

        # Create normalized values (all 0-1 range)
        normalized = {
            'bz': self.normalize(bz, self.BZ_MIN, self.BZ_MAX) if bz is not None else 0.5,
            'speed': self.normalize(speed, self.SPEED_MIN, self.SPEED_MAX) if speed is not None else 0.5,
            'density': self.normalize(density, self.DENSITY_MIN, self.DENSITY_MAX) if density is not None else 0.5,
            'temperature': self.normalize(temperature, self.TEMP_MIN, self.TEMP_MAX) if temperature is not None else 0.5,
        }

        # Create lighting parameters
        lighting = {
            'hue': self.bz_to_hue(bz),                          # 0-360 degrees
            'saturation': self.density_to_saturation(density),   # 0-100%
            'brightness': self.speed_to_brightness(speed),       # 0-100%
            'flow_rate': self.speed_to_flow_rate(speed),        # 0.0-1.0
        }

        # Convert HSV to RGB (useful for some LED controllers)
        # HSV values are normalized to 0-1 for colorsys
        h = lighting['hue'] / 360.0
        s = lighting['saturation'] / 100.0
        v = lighting['brightness'] / 100.0
        r, g, b = colorsys.hsv_to_rgb(h, s, v)

        lighting['rgb'] = {
            'r': int(r * 255),
            'g': int(g * 255),
            'b': int(b * 255),
        }

        # Build the complete output
        result = {
            'timestamp': solar_data.get('timestamp'),
            'raw': {
                'bz': bz,
                'bx': solar_data.get('bx'),
                'by': solar_data.get('by'),
                'bt': solar_data.get('bt'),
                'speed': speed,
                'density': density,
                'temperature': temperature,
            },
            'normalized': normalized,
            'lighting': lighting,
        }

        # Cache these values for potential smoothing/fallback
        self.last_values = result

        return result

    def get_aurora_probability(self, bz: Optional[float], speed: Optional[float]) -> str:
        """
        Estimate aurora probability based on BZ and speed.

        This is a simplified model - real aurora prediction is more complex!

        Args:
            bz: BZ magnetic field in nT
            speed: Solar wind speed in km/s

        Returns:
            String describing aurora probability
        """
        if bz is None or speed is None:
            return "Unknown (missing data)"

        # Aurora is most likely when:
        # - BZ is negative (southward)
        # - BZ magnitude is large
        # - Speed is high

        if bz > 0:
            return "Low (BZ positive - field pointing north)"

        bz_mag = abs(bz)

        if bz_mag > 10 and speed > 500:
            return "Very High! 🌌⚡"
        elif bz_mag > 5 and speed > 450:
            return "High 🌌"
        elif bz_mag > 3 and speed > 400:
            return "Moderate"
        else:
            return "Low"

    def print_lighting_status(self, result: Dict):
        """
        Pretty-print the lighting mapping results.

        Args:
            result: Output from map_to_lighting()
        """
        print("\n" + "="*60)
        print("💡 LIGHTING MAPPING RESULTS")
        print("="*60)

        raw = result['raw']
        lighting = result['lighting']

        # Aurora probability
        aurora_prob = self.get_aurora_probability(raw['bz'], raw['speed'])
        print(f"Aurora Probability: {aurora_prob}")
        print()

        # Lighting parameters
        print("🎨 LIGHTING PARAMETERS:")
        print(f"  Color: HSV({lighting['hue']}°, {lighting['saturation']}%, {lighting['brightness']}%)")
        print(f"  RGB: ({lighting['rgb']['r']}, {lighting['rgb']['g']}, {lighting['rgb']['b']})")
        print(f"  Flow Rate: {lighting['flow_rate']:.2f}")
        print()

        # Color interpretation
        hue = lighting['hue']
        if 240 <= hue <= 300:
            color_desc = "💜 Purple/Violet (Aurora conditions!)"
        elif 180 <= hue < 240:
            color_desc = "💙 Blue/Cyan (Transitional)"
        elif 120 <= hue < 180:
            color_desc = "💚 Green/Cyan (Neutral)"
        elif 60 <= hue < 120:
            color_desc = "💛 Yellow/Green (Calm)"
        else:
            color_desc = "🧡 Orange/Yellow (Very calm)"

        print(f"  Color Meaning: {color_desc}")
        print("="*60 + "\n")


# Quick test if run directly
if __name__ == "__main__":
    print("🎨 Testing Lighting Mapper...\n")

    # Create some test data
    test_cases = [
        {
            'name': 'Strong Aurora Conditions',
            'data': {'bz': -15.0, 'speed': 650, 'density': 15, 'temperature': 200000}
        },
        {
            'name': 'Quiet Conditions',
            'data': {'bz': 8.0, 'speed': 350, 'density': 5, 'temperature': 100000}
        },
        {
            'name': 'Moderate Activity',
            'data': {'bz': -3.0, 'speed': 450, 'density': 8, 'temperature': 150000}
        },
    ]

    mapper = LightingMapper()

    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"TEST CASE: {test['name']}")
        print(f"{'='*60}")

        result = mapper.map_to_lighting(test['data'])
        mapper.print_lighting_status(result)
