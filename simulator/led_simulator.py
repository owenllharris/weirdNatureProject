#!/usr/bin/env python3
"""
LED Matrix Simulator
32x32 RGB LED Matrix Display Simulator

This simulator allows you to test LED matrix patterns without
the actual hardware. It provides a visual representation and
can communicate with Arduino via serial.
"""

import pygame
import numpy as np
import math
import sys
import time
from typing import Tuple

# Configuration
MATRIX_WIDTH = 32
MATRIX_HEIGHT = 32
PIXEL_SIZE = 15
PIXEL_SPACING = 2
WINDOW_WIDTH = MATRIX_WIDTH * (PIXEL_SIZE + PIXEL_SPACING)
WINDOW_HEIGHT = MATRIX_HEIGHT * (PIXEL_SIZE + PIXEL_SPACING) + 100

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (30, 30, 30)

class LEDMatrix:
    """Simulated 32x32 LED Matrix"""

    def __init__(self):
        self.width = MATRIX_WIDTH
        self.height = MATRIX_HEIGHT
        self.pixels = np.zeros((MATRIX_HEIGHT, MATRIX_WIDTH, 3), dtype=np.uint8)
        self.current_pattern = 0
        self.animation_frame = 0
        self.brightness = 255
        self.animation_speed = 50

    def set_pixel(self, x: int, y: int, color: Tuple[int, int, int]):
        """Set a single pixel color"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y, x] = color

    def fill(self, color: Tuple[int, int, int]):
        """Fill entire matrix with a color"""
        self.pixels[:, :] = color

    def clear(self):
        """Clear the matrix (all pixels off)"""
        self.fill((0, 0, 0))

    def get_pixel(self, x: int, y: int) -> Tuple[int, int, int]:
        """Get color of a single pixel"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return tuple(self.pixels[y, x])
        return (0, 0, 0)

    def draw_line(self, x0: int, y0: int, x1: int, y1: int, color: Tuple[int, int, int]):
        """Draw a line using Bresenham's algorithm"""
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


class PatternGenerator:
    """Generate various LED patterns"""

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
    def rainbow_wave(matrix: LEDMatrix, frame: int):
        """Pattern 0: Rainbow Wave"""
        for y in range(matrix.height):
            for x in range(matrix.width):
                hue = (x * 8 + y * 8 + frame * 2) % 256
                color = PatternGenerator.wheel_color(hue)
                matrix.set_pixel(x, y, color)

    @staticmethod
    def color_pulse(matrix: LEDMatrix, frame: int):
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
    def scanning_lines(matrix: LEDMatrix, frame: int):
        """Pattern 2: Scanning Lines"""
        matrix.clear()
        pos = frame % 64

        if pos < 32:
            matrix.draw_line(0, pos, 31, pos, (0, 255, 255))
        else:
            matrix.draw_line(pos - 32, 0, pos - 32, 31, (255, 0, 255))

    @staticmethod
    def plasma(matrix: LEDMatrix, frame: int):
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
    def star_field(matrix: LEDMatrix, frame: int):
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
    def fire_effect(matrix: LEDMatrix, frame: int):
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


class Simulator:
    """Main simulator class"""

    PATTERNS = [
        ("Rainbow Wave", PatternGenerator.rainbow_wave),
        ("Color Pulse", PatternGenerator.color_pulse),
        ("Scanning Lines", PatternGenerator.scanning_lines),
        ("Plasma", PatternGenerator.plasma),
        ("Star Field", PatternGenerator.star_field),
        ("Fire Effect", PatternGenerator.fire_effect),
    ]

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("32x32 LED Matrix Simulator")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.matrix = LEDMatrix()
        self.running = True

    def draw_matrix(self):
        """Draw the LED matrix on screen"""
        for y in range(self.matrix.height):
            for x in range(self.matrix.width):
                color = self.matrix.get_pixel(x, y)
                pos_x = x * (PIXEL_SIZE + PIXEL_SPACING)
                pos_y = y * (PIXEL_SIZE + PIXEL_SPACING)

                # Draw LED background (dark)
                pygame.draw.rect(self.screen, DARK_GRAY,
                               (pos_x, pos_y, PIXEL_SIZE, PIXEL_SIZE))

                # Draw LED (lit)
                if any(c > 0 for c in color):
                    pygame.draw.circle(self.screen, color,
                                     (pos_x + PIXEL_SIZE // 2,
                                      pos_y + PIXEL_SIZE // 2),
                                     PIXEL_SIZE // 2 - 1)

    def draw_info(self):
        """Draw information panel"""
        info_y = MATRIX_HEIGHT * (PIXEL_SIZE + PIXEL_SPACING) + 10

        pattern_name = self.PATTERNS[self.matrix.current_pattern][0]
        info_text = [
            f"Pattern: {self.matrix.current_pattern} - {pattern_name}",
            f"Frame: {self.matrix.animation_frame}",
            f"Keys: [SPACE] Next Pattern | [C] Clear | [Q] Quit"
        ]

        for i, text in enumerate(info_text):
            surface = self.font.render(text, True, WHITE)
            self.screen.blit(surface, (10, info_y + i * 25))

    def handle_events(self):
        """Handle keyboard and window events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.matrix.current_pattern = (self.matrix.current_pattern + 1) % len(self.PATTERNS)
                    self.matrix.animation_frame = 0
                    print(f"Switched to pattern {self.matrix.current_pattern}: {self.PATTERNS[self.matrix.current_pattern][0]}")
                elif event.key == pygame.K_c:
                    self.matrix.clear()
                    print("Matrix cleared")

    def run(self):
        """Main simulation loop"""
        print("LED Matrix Simulator Started")
        print("Controls:")
        print("  SPACE - Next pattern")
        print("  C - Clear matrix")
        print("  Q - Quit")

        while self.running:
            self.handle_events()

            # Update pattern
            pattern_func = self.PATTERNS[self.matrix.current_pattern][1]
            pattern_func(self.matrix, self.matrix.animation_frame)

            # Draw everything
            self.screen.fill(BLACK)
            self.draw_matrix()
            self.draw_info()
            pygame.display.flip()

            # Update animation frame
            self.matrix.animation_frame += 1

            # Control frame rate
            self.clock.tick(30)

        pygame.quit()
        print("Simulator closed")


if __name__ == "__main__":
    simulator = Simulator()
    simulator.run()
