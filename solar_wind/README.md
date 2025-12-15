# Space Weather Lighting Installation

Transform real-time solar wind data from the DSCOVR satellite into beautiful lighting displays! 🌞→🌍→✨

This system fetches live data from NOAA's Space Weather Prediction Center and translates it into lighting parameters that visualize the invisible forces hitting Earth from space.

## What It Does

The DSCOVR satellite sits at the L1 Lagrange point (1 million miles from Earth, toward the Sun) and measures the solar wind before it hits Earth. This system:

1. **Fetches** real-time measurements every minute
2. **Translates** the data into colors and animations
3. **Displays** it on LED lights

### The Key Measurements

- **BZ Magnetic Field** (-20 to +20 nT) - THE CRITICAL VALUE
  - Negative BZ (southward) = Aurora conditions! → Cool blues/purples
  - Positive BZ (northward) = Quiet conditions → Warm yellows/oranges

- **Solar Wind Speed** (300-700 km/s)
  - Controls brightness and animation flow rate
  - Faster wind = brighter, faster animations

- **Particle Density** (1-30 particles/cm³)
  - Controls color saturation
  - Higher density = more vivid colors

- **Temperature** (50,000 - 500,000 Kelvin)
  - Optional secondary effect

## Quick Start

### 1. Install Dependencies

```bash
cd solar_wind
pip install -r requirements.txt
```

### 2. Test the Data Fetcher

```bash
python solar_wind_fetcher.py
```

You should see current solar wind conditions printed to console!

### 3. Test the Full System

```bash
python space_weather_monitor.py --once
```

This fetches data once and shows the lighting parameters.

### 4. Run Continuous Monitoring

```bash
python space_weather_monitor.py
```

Or save to a file:

```bash
python space_weather_monitor.py --save output.json
```

## Usage Examples

### Monitor with Custom Interval

```bash
# Poll every 2 minutes instead of 1
python space_weather_monitor.py --interval 120
```

### Quiet Mode (Minimal Output)

```bash
python space_weather_monitor.py --quiet
```

### Send to Arduino

First, find your Arduino port:

```bash
python arduino_integration.py --list-ports
```

Then run the controller:

```bash
# Linux/Mac
python arduino_integration.py --port /dev/ttyUSB0

# Windows
python arduino_integration.py --port COM3
```

## Output Format

The system outputs JSON with this structure:

```json
{
  "timestamp": "2024-12-15T10:30:00Z",
  "raw": {
    "bz": -5.2,
    "speed": 450,
    "density": 8.3,
    "temperature": 180000
  },
  "normalized": {
    "bz": 0.35,
    "speed": 0.62,
    "density": 0.28,
    "temperature": 0.52
  },
  "lighting": {
    "hue": 210,
    "saturation": 85,
    "brightness": 75,
    "flow_rate": 0.62,
    "rgb": {
      "r": 38,
      "g": 95,
      "b": 191
    }
  }
}
```

## File Guide

### Python Scripts

- **`solar_wind_fetcher.py`** - Fetches data from NOAA APIs
- **`lighting_mapper.py`** - Converts data to lighting parameters
- **`space_weather_monitor.py`** - Main monitoring script
- **`arduino_integration.py`** - Sends data to Arduino via serial

### Arduino Sketches

- **`../arduino/space_weather_controller/`** - Arduino sketch that receives data

## Understanding the Colors

The color mapping is designed to be intuitive and scientifically meaningful:

### Aurora Alert! (Purple/Blue)
When BZ is strongly negative (< -5 nT), the magnetic field is pointing south. This is when auroras are most likely! The lights turn purple/blue like the actual auroras.

### Transition (Cyan/Green)
When BZ is slightly negative or near zero, we're in a transition state. Auroras are possible but not guaranteed. Colors shift to cyan/green.

### Quiet Conditions (Yellow/Orange)
When BZ is positive (> 0 nT), the magnetic field is pointing north. This prevents auroras from forming. The lights show warm, calm colors.

### Speed & Brightness
Faster solar wind (> 500 km/s) makes the lights brighter and animations flow faster. It's like the wind is "pushing harder" on Earth's magnetic field.

### Density & Saturation
Higher particle density makes colors more vivid and saturated. Think of it like the "thickness" of the solar wind.

## Advanced Usage

### Customize the Mapping

Edit `lighting_mapper.py` to change how values map to colors. The key functions are:

- `bz_to_hue()` - Color based on BZ
- `speed_to_brightness()` - Brightness based on speed
- `density_to_saturation()` - Saturation based on density

You can adjust the ranges and curves to match your artistic vision!

### Integration Options

The system is designed to be flexible. You can:

1. **Serial to Arduino** (included) - Send RGB values over USB
2. **HTTP API** - Modify `space_weather_monitor.py` to POST to an endpoint
3. **WebSocket** - Stream real-time updates to a web interface
4. **MQTT** - Publish to an MQTT broker for IoT integration
5. **File Output** - Write JSON to a file for other programs to read

## Error Handling

The system handles NOAA API failures gracefully:

- Retries failed requests
- Uses cached data if APIs are down
- Logs warnings but continues running
- Smooths out missing data points

NOAA occasionally has outages during solar storms (ironic!), so the system is designed to keep running.

## Troubleshooting

### "No data available"
- Check your internet connection
- NOAA APIs might be temporarily down (try again in a few minutes)
- Check https://services.swpc.noaa.gov/products/ in a browser

### Arduino not responding
- Check the serial port with `--list-ports`
- Make sure baud rate matches (115200)
- Try unplugging and reconnecting the Arduino
- Check that you uploaded the correct sketch

### Colors look wrong
- The mapping is somewhat subjective - adjust `lighting_mapper.py`
- Make sure your LEDs support the full RGB range
- Check that brightness isn't too low

## Scientific Background

### What is the Solar Wind?

The Sun constantly streams particles (mostly protons and electrons) into space at hundreds of kilometers per second. This "solar wind" carries magnetic fields with it.

### Why Does BZ Matter?

Earth has its own magnetic field pointing north. When the solar wind's magnetic field (BZ component) points south (negative), it can "connect" with Earth's field through a process called magnetic reconnection. This funnels energy into Earth's magnetosphere and creates auroras!

Positive BZ means the fields are aligned the same way, which actually shields Earth and prevents auroras.

### What is L1?

L1 (Lagrange Point 1) is a gravitationally stable point between Earth and the Sun, about 1 million miles from Earth. A satellite there orbits at the same rate as Earth, so it stays between us and the Sun, giving us about 15-60 minutes advance warning before the solar wind hits!

## Fun Facts

- The solar wind travels at 1 million mph (on average)
- It takes ~8 minutes for light to travel from Sun to Earth
- But the solar wind takes 2-4 DAYS to make the same trip!
- During extreme events, speeds can exceed 2000 km/s (4.4 million mph!)
- The temperature is measured in hundreds of thousands of degrees Kelvin, but you wouldn't feel hot because the density is so low

## Credits

Data provided by:
- **NOAA Space Weather Prediction Center** - https://www.swpc.noaa.gov/
- **DSCOVR Satellite** - NASA/NOAA joint mission

## License

MIT License - Use this for art, science, education, or just because space is cool!

## Contributing

Ideas for improvement:
- Add prediction/forecasting based on historical data
- Integrate other space weather data (X-ray flux, proton flux, etc.)
- Create more sophisticated animation patterns
- Add audio alerts for extreme events
- Build a web dashboard

Pull requests welcome!
