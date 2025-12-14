/*
 * Arduino LED Matrix Lighting Controller
 * 32x32 RGB LED Matrix Display
 *
 * This sketch controls a 32x32 LED matrix panel with various
 * lighting effects and patterns. It can receive commands via
 * serial communication for real-time control.
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

// Create matrix object (32x32 with 4 address lines)
RGBmatrixPanel matrix(A, B, C, D, CLK, LAT, OE, false);

// Animation variables
int currentPattern = 0;
int brightness = 255;
int animationSpeed = 50;
unsigned long lastUpdate = 0;
int animationFrame = 0;

// Color definitions
const uint16_t RED = matrix.Color333(7, 0, 0);
const uint16_t GREEN = matrix.Color333(0, 7, 0);
const uint16_t BLUE = matrix.Color333(0, 0, 7);
const uint16_t YELLOW = matrix.Color333(7, 7, 0);
const uint16_t CYAN = matrix.Color333(0, 7, 7);
const uint16_t MAGENTA = matrix.Color333(7, 0, 7);
const uint16_t WHITE = matrix.Color333(7, 7, 7);

void setup() {
  Serial.begin(115200);
  matrix.begin();
  matrix.setTextWrap(false);

  Serial.println("Arduino LED Matrix Controller");
  Serial.println("32x32 RGB Matrix Ready");
  Serial.println("Commands: P<0-9> (pattern), B<0-255> (brightness), S<10-200> (speed)");
}

void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    handleSerialCommand();
  }

  // Update animation based on speed
  if (millis() - lastUpdate > animationSpeed) {
    lastUpdate = millis();
    runCurrentPattern();
    animationFrame++;
  }
}

void handleSerialCommand() {
  char command = Serial.read();

  switch (command) {
    case 'P': // Pattern selection
      if (Serial.available()) {
        currentPattern = Serial.parseInt();
        Serial.print("Pattern changed to: ");
        Serial.println(currentPattern);
        matrix.fillScreen(0);
        animationFrame = 0;
      }
      break;

    case 'B': // Brightness control
      if (Serial.available()) {
        brightness = Serial.parseInt();
        Serial.print("Brightness: ");
        Serial.println(brightness);
      }
      break;

    case 'S': // Speed control
      if (Serial.available()) {
        animationSpeed = Serial.parseInt();
        Serial.print("Speed: ");
        Serial.println(animationSpeed);
      }
      break;

    case 'C': // Clear display
      matrix.fillScreen(0);
      Serial.println("Display cleared");
      break;
  }
}

void runCurrentPattern() {
  switch (currentPattern) {
    case 0:
      rainbowWave();
      break;
    case 1:
      colorPulse();
      break;
    case 2:
      scanningLines();
      break;
    case 3:
      plasma();
      break;
    case 4:
      starField();
      break;
    case 5:
      fireEffect();
      break;
    default:
      rainbowWave();
      break;
  }
}

// Pattern 0: Rainbow Wave
void rainbowWave() {
  for (int y = 0; y < 32; y++) {
    for (int x = 0; x < 32; x++) {
      int hue = (x * 8 + y * 8 + animationFrame * 2) % 256;
      uint16_t color = wheelColor(hue);
      matrix.drawPixel(x, y, color);
    }
  }
}

// Pattern 1: Color Pulse
void colorPulse() {
  int pulse = (sin(animationFrame * 0.1) + 1) * 3.5;
  uint16_t color = matrix.Color333(pulse, pulse / 2, pulse);
  matrix.fillScreen(color);

  // Add some sparkles
  for (int i = 0; i < 5; i++) {
    int x = random(32);
    int y = random(32);
    matrix.drawPixel(x, y, WHITE);
  }
}

// Pattern 2: Scanning Lines
void scanningLines() {
  matrix.fillScreen(0);
  int pos = animationFrame % 64;

  if (pos < 32) {
    matrix.drawLine(0, pos, 31, pos, CYAN);
  } else {
    matrix.drawLine(pos - 32, 0, pos - 32, 31, MAGENTA);
  }
}

// Pattern 3: Plasma Effect
void plasma() {
  for (int y = 0; y < 32; y++) {
    for (int x = 0; x < 32; x++) {
      float value = sin(x * 0.3 + animationFrame * 0.05) +
                   sin(y * 0.3 + animationFrame * 0.05) +
                   sin((x + y) * 0.2 + animationFrame * 0.05);
      int hue = (int)(value * 32 + 128) % 256;
      matrix.drawPixel(x, y, wheelColor(hue));
    }
  }
}

// Pattern 4: Star Field
void starField() {
  // Fade existing pixels
  for (int y = 0; y < 32; y++) {
    for (int x = 0; x < 32; x++) {
      if (random(100) < 5) {
        matrix.drawPixel(x, y, 0);
      }
    }
  }

  // Add new stars
  for (int i = 0; i < 3; i++) {
    int x = random(32);
    int y = random(32);
    int brightness = random(3, 8);
    matrix.drawPixel(x, y, matrix.Color333(brightness, brightness, brightness));
  }
}

// Pattern 5: Fire Effect
void fireEffect() {
  for (int x = 0; x < 32; x++) {
    int heat = random(3, 8);
    matrix.drawPixel(x, 31, matrix.Color333(heat, heat / 2, 0));

    // Propagate upward with decay
    for (int y = 0; y < 31; y++) {
      if (random(100) < 30) {
        matrix.drawPixel(x, y, matrix.drawPixel(x, y + 1, 0));
      }
    }
  }
}

// Helper function: Color wheel for rainbow effects
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
