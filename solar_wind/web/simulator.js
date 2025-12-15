/**
 * Space Weather LED Matrix Simulator
 * ===================================
 *
 * This script handles:
 * - LED matrix rendering with glow effects
 * - Multiple animation patterns
 * - Real-time data fetching and display
 * - BZ history chart
 *
 * LED Matrix: 32x32 grid simulating physical LED installation
 */

// ============================================
// CONFIGURATION
// ============================================

const CONFIG = {
    // LED Matrix settings
    MATRIX_SIZE: 32,  // 32x32 grid
    LED_SIZE: 20,     // Size of each LED in pixels
    LED_GAP: 4,       // Gap between LEDs
    LED_GLOW: 8,      // Glow radius

    // Data fetching
    UPDATE_INTERVAL: 5000,  // Fetch data every 5 seconds

    // Animation
    FPS: 30,  // Frames per second

    // BZ History
    HISTORY_SIZE: 30,  // Keep 30 data points
};

// ============================================
// STATE
// ============================================

const state = {
    // Current space weather data
    currentData: null,

    // BZ history for chart
    bzHistory: [],

    // LED matrix color
    currentColor: { r: 100, g: 100, b: 100 },

    // Animation
    animationTime: 0,
    animationSpeed: 1.0,
    currentPattern: 'solid',

    // Connection
    isConnected: false,
    lastUpdateTime: null,
};

// ============================================
// LED MATRIX RENDERER
// ============================================

class LEDMatrix {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');

        // Calculate actual canvas size
        const totalSize = (CONFIG.LED_SIZE + CONFIG.LED_GAP) * CONFIG.MATRIX_SIZE - CONFIG.LED_GAP;
        this.canvas.width = totalSize;
        this.canvas.height = totalSize;

        // For smoother rendering
        this.ctx.imageSmoothingEnabled = true;
    }

    /**
     * Draw a single LED at grid position (x, y)
     */
    drawLED(x, y, color, brightness = 1.0) {
        const pixelX = x * (CONFIG.LED_SIZE + CONFIG.LED_GAP);
        const pixelY = y * (CONFIG.LED_SIZE + CONFIG.LED_GAP);
        const size = CONFIG.LED_SIZE;

        // Apply brightness
        const r = Math.floor(color.r * brightness);
        const g = Math.floor(color.g * brightness);
        const b = Math.floor(color.b * brightness);

        // Draw outer glow
        const gradient = this.ctx.createRadialGradient(
            pixelX + size/2, pixelY + size/2, size/4,
            pixelX + size/2, pixelY + size/2, size/2 + CONFIG.LED_GLOW
        );
        gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, ${brightness})`);
        gradient.addColorStop(0.5, `rgba(${r}, ${g}, ${b}, ${brightness * 0.5})`);
        gradient.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0)`);

        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(
            pixelX - CONFIG.LED_GLOW,
            pixelY - CONFIG.LED_GLOW,
            size + CONFIG.LED_GLOW * 2,
            size + CONFIG.LED_GLOW * 2
        );

        // Draw LED body
        this.ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
        this.ctx.fillRect(pixelX, pixelY, size, size);

        // Add highlight for 3D effect
        const highlight = this.ctx.createLinearGradient(
            pixelX, pixelY,
            pixelX + size, pixelY + size
        );
        highlight.addColorStop(0, `rgba(255, 255, 255, ${brightness * 0.3})`);
        highlight.addColorStop(1, 'rgba(255, 255, 255, 0)');

        this.ctx.fillStyle = highlight;
        this.ctx.fillRect(pixelX, pixelY, size, size);
    }

    /**
     * Clear the entire matrix
     */
    clear() {
        this.ctx.fillStyle = '#0a0a0a';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }

    /**
     * Render the entire matrix with the current pattern
     */
    render(pattern, color, time) {
        this.clear();

        for (let y = 0; y < CONFIG.MATRIX_SIZE; y++) {
            for (let x = 0; x < CONFIG.MATRIX_SIZE; x++) {
                let brightness = 1.0;

                // Apply pattern-specific brightness modulation
                switch (pattern) {
                    case 'solid':
                        brightness = 1.0;
                        break;

                    case 'wave':
                        // Horizontal wave flowing from left to right
                        const waveOffset = (x / CONFIG.MATRIX_SIZE) * Math.PI * 2;
                        brightness = 0.5 + 0.5 * Math.sin(time + waveOffset);
                        break;

                    case 'pulse':
                        // Global pulsing effect
                        brightness = 0.4 + 0.6 * (Math.sin(time * 2) * 0.5 + 0.5);
                        break;

                    case 'sparkle':
                        // Aurora-like sparkling effect
                        const baseWave = 0.3 + 0.4 * Math.sin(time + x * 0.1 + y * 0.1);
                        const sparkle = Math.random() > 0.95 ? Math.random() * 0.5 : 0;
                        brightness = baseWave + sparkle;
                        break;
                }

                this.drawLED(x, y, color, brightness);
            }
        }
    }
}

// ============================================
// BZ HISTORY CHART
// ============================================

class BZChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
    }

    render(history) {
        const width = this.canvas.width;
        const height = this.canvas.height;

        // Clear
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
        this.ctx.fillRect(0, 0, width, height);

        if (history.length < 2) {
            this.ctx.fillStyle = '#666';
            this.ctx.font = '14px sans-serif';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('Collecting data...', width / 2, height / 2);
            return;
        }

        // Draw zero line
        const zeroY = height / 2;
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
        this.ctx.lineWidth = 1;
        this.ctx.setLineDash([5, 5]);
        this.ctx.beginPath();
        this.ctx.moveTo(0, zeroY);
        this.ctx.lineTo(width, zeroY);
        this.ctx.stroke();
        this.ctx.setLineDash([]);

        // Find min/max for scaling
        const bzValues = history.map(h => h.bz).filter(v => v !== null);
        if (bzValues.length === 0) return;

        const maxBZ = Math.max(...bzValues, 10);
        const minBZ = Math.min(...bzValues, -10);
        const range = Math.max(Math.abs(maxBZ), Math.abs(minBZ));

        // Map BZ to Y coordinate
        const bzToY = (bz) => {
            if (bz === null) return zeroY;
            return zeroY - (bz / range) * (height / 2 - 20);
        };

        // Draw the line
        this.ctx.strokeStyle = '#00d4ff';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();

        const stepX = width / (CONFIG.HISTORY_SIZE - 1);

        history.forEach((point, i) => {
            const x = i * stepX;
            const y = bzToY(point.bz);

            if (i === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        });

        this.ctx.stroke();

        // Draw dots
        this.ctx.fillStyle = '#00d4ff';
        history.forEach((point, i) => {
            const x = i * stepX;
            const y = bzToY(point.bz);

            this.ctx.beginPath();
            this.ctx.arc(x, y, 3, 0, Math.PI * 2);
            this.ctx.fill();
        });

        // Draw labels
        this.ctx.fillStyle = '#666';
        this.ctx.font = '12px monospace';
        this.ctx.textAlign = 'right';
        this.ctx.fillText(`${range.toFixed(1)} nT`, width - 5, 15);
        this.ctx.fillText('0 nT', width - 5, zeroY - 5);
        this.ctx.fillText(`-${range.toFixed(1)} nT`, width - 5, height - 5);
    }
}

// ============================================
// DATA FETCHER
// ============================================

class DataFetcher {
    async fetchData() {
        try {
            const response = await fetch('/api/data');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching data:', error);
            return null;
        }
    }
}

// ============================================
// UI UPDATER
// ============================================

class UIUpdater {
    updateConnectionStatus(isConnected, error = null) {
        const status = document.getElementById('connectionStatus');

        if (error) {
            status.className = 'connection-status error';
            status.querySelector('.status-text').textContent = 'Connection Error';
        } else if (isConnected) {
            status.className = 'connection-status connected';
            status.querySelector('.status-text').textContent = 'Connected';
        } else {
            status.className = 'connection-status';
            status.querySelector('.status-text').textContent = 'Connecting...';
        }
    }

    updateDataDisplay(data) {
        if (!data) return;

        const raw = data.raw;
        const lighting = data.lighting;

        // Update BZ value with color coding
        const bzElement = document.getElementById('bzValue');
        if (raw.bz !== null) {
            bzElement.textContent = `${raw.bz > 0 ? '+' : ''}${raw.bz.toFixed(2)} nT`;

            // Color code: negative = cyan (aurora), positive = orange (calm)
            if (raw.bz < -5) {
                bzElement.style.color = '#ff00ff';  // Magenta for strong aurora
            } else if (raw.bz < 0) {
                bzElement.style.color = '#00d4ff';  // Cyan for aurora
            } else {
                bzElement.style.color = '#ffaa00';  // Orange for calm
            }
        } else {
            bzElement.textContent = '-- nT';
            bzElement.style.color = '#666';
        }

        // Update other values
        document.getElementById('speedValue').textContent =
            raw.speed !== null ? `${raw.speed.toFixed(0)} km/s` : '-- km/s';

        document.getElementById('densityValue').textContent =
            raw.density !== null ? `${raw.density.toFixed(1)} /cm³` : '-- /cm³';

        document.getElementById('temperatureValue').textContent =
            raw.temperature !== null ? `${(raw.temperature / 1000).toFixed(0)}K K` : '-- K';

        // Update color display
        const rgb = lighting.rgb;
        document.getElementById('colorPreview').style.backgroundColor =
            `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`;
        document.getElementById('rgbValue').textContent =
            `${rgb.r}, ${rgb.g}, ${rgb.b}`;
        document.getElementById('hsvValue').textContent =
            `${lighting.hue}°, ${lighting.saturation}%, ${lighting.brightness}%`;

        // Update aurora probability
        this.updateAuroraProbability(raw.bz, raw.speed);

        // Update timestamp
        if (data.timestamp) {
            const date = new Date(data.timestamp);
            document.getElementById('lastUpdate').textContent =
                date.toLocaleTimeString() + ' UTC';
        }
    }

    updateAuroraProbability(bz, speed) {
        const fillElement = document.getElementById('probabilityFill');
        const textElement = document.getElementById('probabilityText');

        if (bz === null || speed === null) {
            fillElement.style.width = '0%';
            textElement.textContent = 'Unknown (missing data)';
            return;
        }

        let probability = 0;
        let text = '';

        if (bz > 0) {
            probability = 0;
            text = 'Low (BZ positive)';
        } else {
            const bzMag = Math.abs(bz);

            if (bzMag > 10 && speed > 500) {
                probability = 95;
                text = 'Very High! 🌌⚡';
            } else if (bzMag > 5 && speed > 450) {
                probability = 75;
                text = 'High 🌌';
            } else if (bzMag > 3 && speed > 400) {
                probability = 50;
                text = 'Moderate';
            } else {
                probability = 20;
                text = 'Low';
            }
        }

        fillElement.style.width = `${probability}%`;
        textElement.textContent = text;
    }
}

// ============================================
// MAIN APPLICATION
// ============================================

class SpaceWeatherSimulator {
    constructor() {
        // Initialize components
        this.ledMatrix = new LEDMatrix('ledMatrix');
        this.bzChart = new BZChart('bzChart');
        this.dataFetcher = new DataFetcher();
        this.uiUpdater = new UIUpdater();

        // Set up event listeners
        this.setupEventListeners();

        // Start animation loop
        this.startAnimation();

        // Start data fetching
        this.startDataFetching();
    }

    setupEventListeners() {
        // Pattern selector
        document.getElementById('patternSelect').addEventListener('change', (e) => {
            state.currentPattern = e.target.value;
        });

        // Speed slider
        const speedSlider = document.getElementById('speedSlider');
        speedSlider.addEventListener('input', (e) => {
            state.animationSpeed = parseFloat(e.target.value);
            document.getElementById('speedValue').textContent = `${e.target.value}x`;
        });
    }

    startAnimation() {
        const animate = () => {
            // Update animation time based on flow_rate from data
            const baseSpeed = state.currentData?.lighting?.flow_rate || 0.5;
            state.animationTime += (baseSpeed * state.animationSpeed * 0.05);

            // Render LED matrix
            this.ledMatrix.render(
                state.currentPattern,
                state.currentColor,
                state.animationTime
            );

            // Continue animation
            requestAnimationFrame(animate);
        };

        animate();
    }

    async startDataFetching() {
        // Initial fetch
        await this.fetchAndUpdate();

        // Set up periodic fetching
        setInterval(() => this.fetchAndUpdate(), CONFIG.UPDATE_INTERVAL);
    }

    async fetchAndUpdate() {
        const data = await this.dataFetcher.fetchData();

        if (data) {
            // Update state
            state.currentData = data;
            state.isConnected = true;
            state.lastUpdateTime = Date.now();

            // Update LED color
            if (data.lighting && data.lighting.rgb) {
                state.currentColor = data.lighting.rgb;
            }

            // Update BZ history
            if (data.raw && data.raw.bz !== null) {
                state.bzHistory.push({
                    bz: data.raw.bz,
                    timestamp: data.timestamp
                });

                // Keep only recent history
                if (state.bzHistory.length > CONFIG.HISTORY_SIZE) {
                    state.bzHistory.shift();
                }
            }

            // Update UI
            this.uiUpdater.updateConnectionStatus(true);
            this.uiUpdater.updateDataDisplay(data);
            this.bzChart.render(state.bzHistory);

        } else {
            // Handle error
            state.isConnected = false;
            this.uiUpdater.updateConnectionStatus(false, true);
        }
    }
}

// ============================================
// INITIALIZE ON PAGE LOAD
// ============================================

// Wait for DOM to be ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new SpaceWeatherSimulator();
    });
} else {
    new SpaceWeatherSimulator();
}
