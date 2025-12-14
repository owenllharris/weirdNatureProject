# Quick Start Guide

## Testing with the Simulator (No Hardware Required!)

Want to see the patterns in action without the hardware? Start here:

### 1. Install Python Dependencies

```bash
cd simulator
pip install -r requirements.txt
```

### 2. Run the Simulator

```bash
python led_simulator.py
```

### 3. Controls

- **SPACE** - Cycle through different patterns
- **C** - Clear the display
- **Q** - Quit the simulator

## Available Patterns

0. **Rainbow Wave** - Colorful flowing rainbow effect
1. **Color Pulse** - Pulsing colors with sparkles
2. **Scanning Lines** - Scanning line animation
3. **Plasma** - Trippy plasma effect
4. **Star Field** - Twinkling stars
5. **Fire Effect** - Realistic fire simulation

## Hardware Setup (When You're Ready)

### Wiring the LED Matrix

Connect your 32x32 RGB LED Matrix to Arduino:

```
LED Matrix Pin -> Arduino Pin
CLK           -> D8
OE            -> D9
LAT           -> D10
A             -> A0
B             -> A1
C             -> A2
D             -> A3
```

### Power Requirements

- LED matrices draw significant current
- Use a dedicated 5V power supply (5A minimum recommended)
- Connect power supply ground to Arduino ground

### Upload Arduino Code

1. Open Arduino IDE
2. Install required libraries:
   - Adafruit GFX Library
   - RGB Matrix Panel Library
3. Open `arduino/lighting_controller/lighting_controller.ino`
4. Select your board and port
5. Upload!

## Serial Control

Send commands via serial monitor (115200 baud):

- `P0` to `P5` - Select pattern (0-5)
- `B0` to `B255` - Set brightness
- `S10` to `S200` - Set animation speed (ms)
- `C` - Clear display

## Troubleshooting

**Simulator won't start?**
- Make sure pygame is installed: `pip install pygame`
- Check Python version (3.8+ recommended)

**Arduino shows nothing?**
- Check wiring connections
- Verify power supply is connected
- Check serial monitor for error messages

**Colors look wrong?**
- Different matrix panels may have different wiring
- Check your specific panel's datasheet
- You may need to adjust pin mappings

## Next Steps

- Modify patterns in the Arduino sketch
- Create your own custom animations
- Add more serial commands
- Connect sensors for reactive lighting

Have fun creating cool lighting effects!
