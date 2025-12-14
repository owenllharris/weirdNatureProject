# Arduino LED Matrix Lighting Project

A cool Arduino-based lighting project featuring a 32x32 LED matrix display with visual effects and patterns.

## Project Structure

```
├── arduino/
│   └── lighting_controller/    # Arduino sketch for LED matrix control
├── simulator/                   # Python-based LED matrix simulator for testing
└── docs/                       # Documentation and schematics
```

## Features

- 32x32 RGB LED matrix control
- Multiple lighting effects and animations
- Serial communication protocol for real-time control
- Python simulator for testing patterns without hardware

## Hardware Requirements

- Arduino board (Uno, Mega, or compatible)
- 32x32 RGB LED Matrix Panel
- 5V Power Supply (adequate amperage for LED matrix)
- Level shifter (3.3V to 5V) if needed

## Getting Started

### Arduino Setup

1. Open `arduino/lighting_controller/lighting_controller.ino` in Arduino IDE
2. Install required libraries (see dependencies below)
3. Upload to your Arduino board
4. Connect your LED matrix according to the wiring diagram

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
