# Arduino LED Matrix Lighting Project

A cool Arduino-based lighting project featuring a 32x32 LED matrix display with visual effects and patterns.

**✨ NEW: Space Weather Visualization!** See real-time solar wind data from the DSCOVR satellite displayed as living light!

## Project Structure

```
├── arduino/
│   ├── lighting_controller/         # Arduino sketch for LED matrix control
│   └── space_weather_controller/    # 🌞 Space weather visualization controller
├── simulator/                        # Python-based LED matrix simulator for testing
├── solar_wind/                       # 🛰️ Real-time space weather data fetcher and mapper
└── docs/                            # Documentation and schematics
```

## Features

### LED Matrix Control
- 32x32 RGB LED matrix control
- Multiple lighting effects and animations
- Serial communication protocol for real-time control
- Python simulator for testing patterns without hardware

### 🌞 Space Weather Visualization (NEW!)
- Real-time solar wind data from NOAA/DSCOVR satellite
- Visualize the invisible forces from space hitting Earth
- Color-coded BZ magnetic field (aurora prediction!)
- Dynamic brightness based on solar wind speed
- Saturation mapped to particle density
- See `solar_wind/README.md` for full documentation

## Hardware Requirements

- Arduino board (Uno, Mega, or compatible)
- 32x32 RGB LED Matrix Panel
- 5V Power Supply (adequate amperage for LED matrix)
- Level shifter (3.3V to 5V) if needed

## Getting Started

### Option 1: Basic LED Patterns

1. Open `arduino/lighting_controller/lighting_controller.ino` in Arduino IDE
2. Install required libraries (see dependencies below)
3. Upload to your Arduino board
4. Connect your LED matrix according to the wiring diagram

### Option 2: Space Weather Visualization 🌞

1. Install Python dependencies:
   ```bash
   cd solar_wind
   pip install -r requirements.txt
   ```

2. Test the data fetcher:
   ```bash
   python space_weather_monitor.py --once
   ```

3. Upload the space weather controller to Arduino:
   - Open `arduino/space_weather_controller/space_weather_controller.ino`
   - Upload to your Arduino

4. Connect Arduino and run the integration:
   ```bash
   python arduino_integration.py --port /dev/ttyUSB0  # or COM3 on Windows
   ```

See `solar_wind/README.md` for complete documentation!

### Simulator Setup

1. Navigate to the `simulator/` directory
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the simulator:
   ```bash
   python led_simulator.py
   ```

## Dependencies

### Arduino Libraries
- Adafruit GFX Library
- RGB Matrix Panel Library

### Python
- pygame
- pyserial
- numpy

## Communication Protocol

The Arduino listens for serial commands to control the LED matrix:
- Pattern selection
- Color control
- Brightness adjustment
- Animation speed

## License

MIT License

## Contributing

Feel free to submit issues and enhancement requests!
