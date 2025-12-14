# LED Matrix Simulator

Two ways to test your LED patterns without hardware:

## Terminal Simulator (Works Anywhere!)

```bash
python terminal_simulator.py
```

- Displays in your terminal using colored text
- No GUI needed
- Automatically cycles through all 6 patterns every 100 frames
- Press Ctrl+C to exit

## GUI Simulator (Full Featured)

```bash
python led_simulator.py
```

- Full pygame window with realistic LED visualization
- Interactive controls:
  - **SPACE** - Switch to next pattern
  - **C** - Clear display
  - **Q** - Quit
- Requires display/X11 server

## Available Patterns

Both simulators include these 6 patterns:

0. **Rainbow Wave** - Flowing rainbow diagonal waves
1. **Color Pulse** - Pulsing colors with sparkle effects
2. **Scanning Lines** - Horizontal and vertical scanning animation
3. **Plasma** - Psychedelic plasma effect
4. **Star Field** - Twinkling starfield animation
5. **Fire Effect** - Realistic fire simulation

## Testing Your Own Patterns

To add custom patterns:

1. Create a new static method in the `PatternGenerator` class
2. Add it to the `PATTERNS` list in the simulator
3. The pattern receives a `matrix` object and current `frame` number
4. Use `matrix.set_pixel(x, y, (r, g, b))` to set individual LEDs

Example:

```python
@staticmethod
def my_pattern(matrix, frame):
    for x in range(32):
        for y in range(32):
            color = (x * 8, y * 8, frame % 256)
            matrix.set_pixel(x, y, color)
```

## Tips

- The terminal simulator is perfect for quick testing in SSH/remote environments
- The GUI simulator provides better visualization for demos
- Both use the same pattern algorithms as the Arduino code!
