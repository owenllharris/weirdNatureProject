/*
 * Space Weather LED Controller
 * ============================
 *
 * This Arduino sketch receives space weather data from a Python script
 * and displays it on a 32x32 RGB LED matrix.
 *
 * The color represents the BZ magnetic field:
 * - Purple/Blue = Negative BZ (aurora conditions!)
 * - Cyan/Green = Neutral
 * - Yellow/Orange = Positive BZ (quiet)
 *
 * Serial Commands:
 * - Rxxx,xxx,xxx = Set RGB color (e.g., R255,0,128)
 * - Fxx = Set flow rate 0-100 (animation speed)
 * - C = Clear display
 *
 * Baud rate: 115200
 */

#include <Adafruit_GFX.h>
#include <RGBmatrixPanel.h>

// Pin definitions for 32x32 matrix
#define CLK 8
#define OE  9
#define LAT 10
#define A   A0
#define B   A1
#define C   A2
#define D   A3

// Create matrix object
RGBmatrixPanel matrix(A, B, C, D, CLK, LAT, OE, false);

// Current color (from space weather data)
int currentR = 0;
int currentG = 0;
int currentB = 255;  // Start with blue

// Animation variables
float flowRate = 0.5;  // 0.0 to 1.0
unsigned long lastUpdate = 0;
int animationFrame = 0;
int animationSpeed = 50;  // milliseconds

// Pattern mode
int patternMode = 0;  // 0=waves, 1=solid, 2=pulse, 3=flow

void setup() {
  Serial.begin(115200);
  matrix.begin();

  Serial.println("🌞 Space Weather LED Controller");
  Serial.println("32x32 RGB Matrix - DSCOVR L1 Data Visualization");
  Serial.println("Waiting for space weather data...");

  // Show startup pattern
  startupAnimation();
}

void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    handleSerialCommand();
  }

  // Update animation
  if (millis() - lastUpdate > animationSpeed) {
    lastUpdate = millis();
    updateDisplay();
    animationFrame++;
  }
}

void handleSerialCommand() {
  char command = Serial.read();

  switch (command) {
    case 'R': {
      // RGB command: Rxxx,xxx,xxx
      int r = Serial.parseInt();
      int g = Serial.parseInt();
      int b = Serial.parseInt();

      if (r >= 0 && r <= 255 && g >= 0 && g <= 255 && b >= 0 && b <= 255) {
        currentR = r;
        currentG = g;
        currentB = b;

        Serial.print("✓ Color updated: RGB(");
        Serial.print(r);
        Serial.print(", ");
        Serial.print(g);
        Serial.print(", ");
        Serial.print(b);
        Serial.println(")");
      }
      break;
    }

    case 'F': {
      // Flow rate command: Fxx (0-100)
      int flow = Serial.parseInt();
      if (flow >= 0 && flow <= 100) {
        flowRate = flow / 100.0;
        animationSpeed = 10 + (100 - flow);  // Faster flow = shorter delay

        Serial.print("✓ Flow rate: ");
        Serial.print(flow);
        Serial.println("%");
      }
      break;
    }

    case 'P': {
      // Pattern mode: P0-3
      int mode = Serial.parseInt();
      if (mode >= 0 && mode <= 3) {
        patternMode = mode;
        Serial.print("✓ Pattern mode: ");
        Serial.println(mode);
      }
      break;
    }

    case 'C': {
      // Clear display
      matrix.fillScreen(0);
      Serial.println("✓ Display cleared");
      break;
    }
  }
}

void updateDisplay() {
  switch (patternMode) {
    case 0:
      drawWaves();
      break;
    case 1:
      drawSolid();
      break;
    case 2:
      drawPulse();
      break;
    case 3:
      drawFlow();
      break;
  }
}

// Pattern 0: Flowing waves
void drawWaves() {
  for (int y = 0; y < 32; y++) {
    for (int x = 0; x < 32; x++) {
      // Create wave pattern
      float wave = sin((x + animationFrame * flowRate) * 0.3) *
                   sin((y + animationFrame * flowRate * 0.7) * 0.2);

      // Map wave to brightness (0.5 to 1.0)
      float brightness = 0.5 + (wave * 0.5);

      // Apply to current color
      int r = currentR * brightness / 32;  // Scale down for matrix
      int g = currentG * brightness / 32;
      int b = currentB * brightness / 32;

      uint16_t color = matrix.Color333(r, g, b);
      matrix.drawPixel(x, y, color);
    }
  }
}

// Pattern 1: Solid color fill
void drawSolid() {
  uint16_t color = matrix.Color333(
    currentR / 32,
    currentG / 32,
    currentB / 32
  );
  matrix.fillScreen(color);
}

// Pattern 2: Pulsing
void drawPulse() {
  float pulse = (sin(animationFrame * 0.1 * (flowRate + 0.3)) + 1) * 0.5;

  uint16_t color = matrix.Color333(
    currentR * pulse / 32,
    currentG * pulse / 32,
    currentB * pulse / 32
  );
  matrix.fillScreen(color);
}

// Pattern 3: Vertical flowing
void drawFlow() {
  // Scroll down
  for (int y = 31; y > 0; y--) {
    for (int x = 0; x < 32; x++) {
      // This is a simplified version - copy pixel from above
      // In practice you'd read the pixel color and copy it
    }
  }

  // New line at top with current color plus noise
  for (int x = 0; x < 32; x++) {
    float brightness = 0.7 + (random(0, 100) / 100.0 * 0.3);

    int r = currentR * brightness / 32;
    int g = currentG * brightness / 32;
    int b = currentB * brightness / 32;

    uint16_t color = matrix.Color333(r, g, b);
    matrix.drawPixel(x, 0, color);
  }
}

void startupAnimation() {
  // Quick rainbow sweep on startup
  for (int frame = 0; frame < 30; frame++) {
    for (int y = 0; y < 32; y++) {
      for (int x = 0; x < 32; x++) {
        int hue = (x * 8 + y * 8 + frame * 8) % 256;
        uint16_t color = wheelColor(hue);
        matrix.drawPixel(x, y, color);
      }
    }
    delay(30);
  }

  matrix.fillScreen(0);
  delay(500);
}

// Color wheel helper
uint16_t wheelColor(byte pos) {
  if (pos < 85) {
    return matrix.Color333(pos / 12, (85 - pos) / 12, 0);
  } else if (pos < 170) {
    pos -= 85;
    return matrix.Color333((85 - pos) / 12, 0, pos / 12);
  } else {
    pos -= 170;
    return matrix.Color333(0, pos / 12, (85 - pos) / 12);
  }
}
