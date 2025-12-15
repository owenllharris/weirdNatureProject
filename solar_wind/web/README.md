# Space Weather LED Matrix Web Simulator

A beautiful web-based simulator for the 32×32 LED matrix space weather installation. Watch real-time solar wind data transform into stunning light patterns in your browser!

## Features

### LED Matrix Display
- **32×32 LED grid** with realistic glow effects
- **4 animation patterns**: Solid, Wave, Pulse, and Aurora Sparkle
- **Adjustable animation speed**
- **Real LED-like appearance** with proper spacing and glow

### Real-Time Data
- Fetches current space weather from NOAA or local files
- Displays key metrics: BZ, speed, density, temperature
- Shows aurora probability with visual indicator
- Updates automatically every 5 seconds

### Visualizations
- **Color preview** showing current RGB and HSV values
- **BZ history chart** tracking the last 30 minutes
- **Aurora probability bar** with descriptive text
- **Color guide** explaining what each color means

### Responsive Design
- Works on desktop, tablet, and mobile
- Space-themed dark UI
- Smooth animations and transitions

## Quick Start

### 1. Install Dependencies

First, make sure you have Flask installed:

```bash
pip install flask flask-cors
```

Or if you're using the full project dependencies:

```bash
cd ..
pip install -r requirements.txt
cd web
```

### 2. Run the Server

**Option A: Simulated Data (for testing/demos)**
```bash
python web_server.py
```

**Option B: Live NOAA Data**
```bash
python web_server.py --live
```

**Option C: Read from JSON File**
```bash
# First, start the monitor to create output.json
cd ..
python space_weather_monitor.py --save output.json &

# Then start the web server
cd web
python web_server.py --file ../output.json
```

### 3. Open Your Browser

Navigate to:
```
http://localhost:5000
```

That's it! You should see the LED matrix animating with space weather colors.

## Command-Line Options

```bash
python web_server.py [OPTIONS]

Options:
  --live              Fetch live data from NOAA APIs
  --file PATH         Read data from a JSON file
  --port PORT         Port to run on (default: 5000)
  --host HOST         Host to bind to (default: 0.0.0.0)

Examples:
  python web_server.py                      # Simulated data
  python web_server.py --live               # Live NOAA data
  python web_server.py --file output.json   # From file
  python web_server.py --port 8080          # Custom port
```

## UI Controls

### Pattern Selection
Choose from 4 different LED patterns:

1. **Solid Fill** - All LEDs show the same color
2. **Wave Flow** - Horizontal wave pattern flowing left to right
3. **Pulse** - Global pulsing effect
4. **Aurora Sparkle** - Random sparkles like real auroras

### Animation Speed
Use the slider to adjust animation speed from 0.1x to 2.0x. The base speed is also influenced by the solar wind flow_rate from the data.

## Understanding the Display

### Color Meanings

The LED colors represent the BZ magnetic field component:

- 🟣 **Purple/Violet** (BZ: -20 to -10 nT)
  - Strong negative BZ
  - Aurora conditions! Very likely to see auroras

- 🔵 **Blue/Cyan** (BZ: -10 to -3 nT)
  - Moderate negative BZ
  - Aurora possible

- 🟢 **Green/Cyan** (BZ: -3 to +3 nT)
  - Neutral/transitional BZ
  - Unlikely aurora activity

- 🟡 **Yellow/Orange** (BZ: +3 to +20 nT)
  - Positive BZ
  - Quiet, calm conditions
  - No aurora activity

### Brightness & Saturation

- **Brightness** = Solar wind speed (faster = brighter)
- **Saturation** = Particle density (higher = more vivid)
- **Animation speed** = Flow rate (derived from speed)

### Aurora Probability

The aurora probability bar estimates the likelihood of aurora activity based on:
- **BZ magnitude** (larger negative = higher probability)
- **Solar wind speed** (faster = higher probability)

Levels:
- **Very High**: BZ < -10 nT AND speed > 500 km/s 🌌⚡
- **High**: BZ < -5 nT AND speed > 450 km/s 🌌
- **Moderate**: BZ < -3 nT AND speed > 400 km/s
- **Low**: Other conditions or BZ positive

## API Endpoints

The server provides a simple REST API:

### GET /api/data
Returns current space weather data in JSON format:

```json
{
  "timestamp": "2025-12-15T12:34:56.789Z",
  "raw": {
    "bz": -12.5,
    "bx": 2.3,
    "by": -1.1,
    "bt": 13.2,
    "speed": 550,
    "density": 8.5,
    "temperature": 150000
  },
  "normalized": {
    "bz": 0.25,
    "speed": 0.6,
    "density": 0.5,
    "temperature": 0.4
  },
  "lighting": {
    "hue": 260,
    "saturation": 75,
    "brightness": 85,
    "flow_rate": 0.6,
    "rgb": {
      "r": 128,
      "g": 64,
      "b": 200
    }
  }
}
```

### GET /api/health
Health check endpoint:

```json
{
  "status": "ok",
  "data_source": "SimulatedDataSource",
  "timestamp": "2025-12-15T12:34:56.789Z"
}
```

## Integration with Monitoring

For a complete real-time experience, run both the monitor and web server together:

### Terminal 1: Start the monitor
```bash
cd /path/to/solar_wind
python space_weather_monitor.py --save output.json --interval 60
```

### Terminal 2: Start the web server
```bash
cd /path/to/solar_wind/web
python web_server.py --file ../output.json
```

The web interface will automatically update as the monitor fetches new data!

## Files

- `index.html` - Main web page structure
- `styles.css` - Space-themed styling with LED glow effects
- `simulator.js` - LED matrix rendering and animation engine
- `web_server.py` - Flask server with data API
- `README.md` - This file

## Technical Details

### LED Matrix Rendering

The simulator uses HTML5 Canvas to render a 32×32 grid of LEDs:
- Each LED is drawn with a radial gradient for glow effect
- Highlight gradients create a 3D appearance
- Pattern algorithms modulate brightness per LED
- Renders at 30 FPS for smooth animation

### Data Flow

```
NOAA APIs ──► space_weather_monitor.py ──► output.json
                                              ▼
                                        web_server.py
                                              ▼
                                         /api/data
                                              ▼
                                        simulator.js
                                              ▼
                                        LED Matrix
```

### Browser Compatibility

Tested and working on:
- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers

Requires:
- HTML5 Canvas support
- ES6 JavaScript
- CSS3 with gradients and animations

## Troubleshooting

### "Cannot import solar wind modules" error
**Solution**: Install dependencies:
```bash
pip install -r ../requirements.txt
```

### Web page doesn't load
**Solution**: Make sure the server is running and check the console for errors:
```bash
python web_server.py
# Look for "Server starting on..." message
```

### "Connection Error" in browser
**Solution**: Check that the data source is working:
- If using `--file`, verify the file exists and has valid JSON
- If using `--live`, check your internet connection
- Try simulated mode first: `python web_server.py`

### LEDs not animating
**Solution**:
- Check browser console for JavaScript errors (F12)
- Try a different pattern from the dropdown
- Refresh the page (Ctrl+R or Cmd+R)

### Port already in use
**Solution**: Use a different port:
```bash
python web_server.py --port 8080
```

## Performance Tips

- **Animation speed**: Lower values (0.5x) use less CPU
- **Browser**: Chrome/Edge generally perform best
- **Mobile**: Use simpler patterns (Solid or Pulse) on mobile devices
- **Background tabs**: Animation pauses when tab is not active (browser optimization)

## Development

### Modifying Patterns

Edit `simulator.js` and add your pattern to the `render()` method:

```javascript
case 'mypattern':
    // Your pattern logic here
    brightness = /* calculate brightness for LED at (x, y) */;
    break;
```

### Changing LED Matrix Size

Edit `CONFIG.MATRIX_SIZE` in `simulator.js`:
```javascript
const CONFIG = {
    MATRIX_SIZE: 64,  // Change to 64x64 for example
    // ...
};
```

### Adjusting Colors

The color mapping is defined in `lighting_mapper.py`:
- `bz_to_hue()` - Maps BZ to hue
- Modify the hue mapping for different color schemes

## Credits

- Data from NOAA Space Weather Prediction Center
- DSCOVR satellite measurements
- Part of the Space Weather LED Lighting Installation project

## License

This is part of the Weird Nature Project. See parent directory for license information.

---

**Enjoy watching space weather in real-time!** 🌌⚡🌍
