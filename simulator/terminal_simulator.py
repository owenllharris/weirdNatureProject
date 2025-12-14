#!/usr/bin/env python3
"""
Terminal-based LED Matrix Simulator
32x32 RGB LED Matrix Display in your terminal!

Uses ANSI color codes to display patterns in the terminal.
"""

import math
import time
import sys
import os
import numpy as np
from typing import Tuple

# Configuration
MATRIX_WIDTH = 32
MATRIX_HEIGHT = 32

class TerminalMatrix:
    """LED Matrix that renders in terminal using ANSI colors"""

    def __init__(self):
        self.width = MATRIX_WIDTH
        self.height = MATRIX_HEIGHT
        self.pixels = np.zeros((MATRIX_HEIGHT, MATRIX_WIDTH, 3), dtype=np.uint8)

    def set_pixel(self, x: int, y: int, color: Tuple[int, int, int]):
        """Set a single pixel color"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y, x] = color

    def fill(self, color: Tuple[int, int, int]):
        """Fill entire matrix with a color"""
        self.pixels[:, :] = color

    def clear(self):
        """Clear the matrix"""
        self.fill((0, 0, 0))

    def get_pixel(self, x: int, y: int) -> Tuple[int, int, int]:
        """Get color of a single pixel"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return tuple(self.pixels[y, x])
        return (0, 0, 0)

    def draw_line(self, x0: int, y0: int, x1: int, y1: int, color: Tuple[int, int, int]):
        """Draw a line"""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            self.set_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def render(self):
        """Render the matrix to terminal using ANSI colors"""
        # Clear screen and move cursor to top
        print('\033[2J\033[H', end='')

        # Print top border
        print('┌' + '─' * (self.width * 2) + '┐')

        for y in range(self.height):
            print('│', end='')
            for x in range(self.width):
                r, g, b = self.get_pixel(x, y)

                # Convert RGB to ANSI color code
                if r == 0 and g == 0 and b == 0:
                    # Black/off - show as dark dot
                    print('\033[90m··\033[0m', end='')
                else:
                    # Use 24-bit true color ANSI escape codes
                    print(f'\033[38;2;{r};{g};{b}m██\033[0m', end='')
            print('│')

        # Print bottom border
        print('└' + '─' * (self.width * 2) + '┘')


class PatternGenerator:
    """Generate LED patterns"""

    @staticmethod
    def wheel_color(pos: int) -> Tuple[int, int, int]:
        """Generate rainbow colors"""
        pos = pos % 256
        if pos < 85:
            return (pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return (255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return (0, pos * 3, 255 - pos * 3)

    @staticmethod
    def rainbow_wave(matrix: TerminalMatrix, frame: int):
        """Pattern 0: Rainbow Wave"""
        for y in range(matrix.height):
            for x in range(matrix.width):
                hue = (x * 8 + y * 8 + frame * 2) % 256
                color = PatternGenerator.wheel_color(hue)
                matrix.set_pixel(x, y, color)

    @staticmethod
    def color_pulse(matrix: TerminalMatrix, frame: int):
        """Pattern 1: Color Pulse"""
        pulse = int((math.sin(frame * 0.1) + 1) * 127)
        color = (pulse, pulse // 2, pulse)
        matrix.fill(color)

        # Add sparkles
        for _ in range(5):
            x = np.random.randint(0, matrix.width)
            y = np.random.randint(0, matrix.height)
            matrix.set_pixel(x, y, (255, 255, 255))

    @staticmethod
    def scanning_lines(matrix: TerminalMatrix, frame: int):
        """Pattern 2: Scanning Lines"""
        matrix.clear()
        pos = frame % 64

        if pos < 32:
            matrix.draw_line(0, pos, 31, pos, (0, 255, 255))
        else:
            matrix.draw_line(pos - 32, 0, pos - 32, 31, (255, 0, 255))

    @staticmethod
    def plasma(matrix: TerminalMatrix, frame: int):
        """Pattern 3: Plasma Effect"""
        for y in range(matrix.height):
            for x in range(matrix.width):
                value = (math.sin(x * 0.3 + frame * 0.05) +
                        math.sin(y * 0.3 + frame * 0.05) +
                        math.sin((x + y) * 0.2 + frame * 0.05))
                hue = int(value * 32 + 128) % 256
                color = PatternGenerator.wheel_color(hue)
                matrix.set_pixel(x, y, color)

    @staticmethod
    def star_field(matrix: TerminalMatrix, frame: int):
        """Pattern 4: Star Field"""
        # Fade existing pixels
        for y in range(matrix.height):
            for x in range(matrix.width):
                if np.random.random() < 0.05:
                    matrix.set_pixel(x, y, (0, 0, 0))

        # Add new stars
        for _ in range(3):
            x = np.random.randint(0, matrix.width)
            y = np.random.randint(0, matrix.height)
            brightness = np.random.randint(100, 255)
            matrix.set_pixel(x, y, (brightness, brightness, brightness))

    @staticmethod
    def fire_effect(matrix: TerminalMatrix, frame: int):
        """Pattern 5: Fire Effect"""
        # Generate heat at bottom
        for x in range(matrix.width):
            heat = np.random.randint(100, 255)
            matrix.set_pixel(x, matrix.height - 1, (heat, heat // 2, 0))

        # Propagate upward with decay
        for x in range(matrix.width):
            for y in range(matrix.height - 1):
                if np.random.random() < 0.7:
                    current = matrix.get_pixel(x, y + 1)
                    decayed = tuple(max(0, int(c * 0.9)) for c in current)
                    matrix.set_pixel(x, y, decayed)


def main():
    """Main function"""
    patterns = [
        ("Rainbow Wave", PatternGenerator.rainbow_wave),
        ("Color Pulse", PatternGenerator.color_pulse),
        ("Scanning Lines", PatternGenerator.scanning_lines),
        ("Plasma", PatternGenerator.plasma),
        ("Star Field", PatternGenerator.star_field),
        ("Fire Effect", PatternGenerator.fire_effect),
    ]

    current_pattern = 0
    frame = 0
    matrix = TerminalMatrix()

    print("Terminal LED Matrix Simulator")
    print("Press Ctrl+C to exit\n")
    time.sleep(2)

    try:
        while True:
            # Run pattern
            pattern_name, pattern_func = patterns[current_pattern]
            pattern_func(matrix, frame)

            # Render to terminal
            matrix.render()

            # Print info below matrix
            print(f"\nPattern {current_pattern}: {pattern_name}")
            print(f"Frame: {frame}")
            print("\nPress Ctrl+C to exit")

            # Update frame
            frame += 1

            # Change pattern every 100 frames
            if frame % 100 == 0:
                current_pattern = (current_pattern + 1) % len(patterns)
                frame = 0

            # Frame rate control
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n\nSimulator stopped!")
        sys.exit(0)


if __name__ == "__main__":
    main()
