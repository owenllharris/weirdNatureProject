#!/usr/bin/env python3
"""
Arduino Serial Integration
===========================

Sends space weather lighting data to Arduino/ESP32 via serial port.

This module provides functions to send lighting parameters to your
Arduino-based LED controller over a serial (USB) connection.

The data is sent in a simple, efficient format that the Arduino can parse.

Author: Space Weather Lighting Project
"""

import serial
import json
import time
from typing import Dict, Optional
import argparse


class ArduinoInterface:
    """
    Serial interface for sending lighting data to Arduino.

    Handles the serial connection and formatting of data for Arduino consumption.
    """

    def __init__(self, port: str, baud_rate: int = 115200):
        """
        Initialize the Arduino interface.

        Args:
            port: Serial port (e.g., '/dev/ttyUSB0' or 'COM3')
            baud_rate: Baud rate (default: 115200, matches our Arduino sketch)
        """
        self.port = port
        self.baud_rate = baud_rate
        self.serial = None
        self.connected = False

    def connect(self) -> bool:
        """
        Connect to the Arduino.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            print(f"🔌 Connecting to Arduino on {self.port} at {self.baud_rate} baud...")
            self.serial = serial.Serial(
                self.port,
                self.baud_rate,
                timeout=1
            )

            # Wait for Arduino to reset (it resets when serial connection opens)
            time.sleep(2)

            self.connected = True
            print("✅ Connected to Arduino!")

            # Read any startup messages
            time.sleep(0.5)
            while self.serial.in_waiting:
                line = self.serial.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"   Arduino: {line}")

            return True

        except serial.SerialException as e:
            print(f"❌ Failed to connect: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Close the serial connection."""
        if self.serial and self.connected:
            self.serial.close()
            self.connected = False
            print("🔌 Disconnected from Arduino")

    def send_lighting_data(self, lighting: Dict) -> bool:
        """
        Send lighting parameters to Arduino.

        Uses the command format from our Arduino sketch:
        - Hxx\n  = Set hue (0-360)
        - Sxx\n  = Set saturation (0-100)
        - Bxx\n  = Set brightness (0-100)
        - Fxx\n  = Set flow rate (0-100)
        - Rxxx,xxx,xxx\n = Set RGB directly

        Args:
            lighting: Lighting parameters dictionary

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.connected:
            print("⚠️  Not connected to Arduino")
            return False

        try:
            # Method 1: Send RGB values directly
            # This is simpler for the Arduino to process
            rgb = lighting.get('rgb', {})
            r = rgb.get('r', 0)
            g = rgb.get('g', 0)
            b = rgb.get('b', 0)

            command = f"R{r},{g},{b}\n"
            self.serial.write(command.encode('utf-8'))

            # Optional: Also send flow rate for animation speed
            flow_rate = int(lighting.get('flow_rate', 0.5) * 100)
            flow_command = f"F{flow_rate}\n"
            self.serial.write(flow_command.encode('utf-8'))

            # Read response if any
            time.sleep(0.01)
            if self.serial.in_waiting:
                response = self.serial.readline().decode('utf-8', errors='ignore').strip()
                if response:
                    print(f"   Arduino: {response}")

            return True

        except serial.SerialException as e:
            print(f"❌ Error sending data: {e}")
            self.connected = False
            return False

    def send_raw_command(self, command: str) -> bool:
        """
        Send a raw command string to Arduino.

        Args:
            command: Command string to send (will add newline if missing)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.connected:
            return False

        try:
            if not command.endswith('\n'):
                command += '\n'

            self.serial.write(command.encode('utf-8'))
            return True

        except serial.SerialException as e:
            print(f"❌ Error sending command: {e}")
            self.connected = False
            return False


class SpaceWeatherArduinoController:
    """
    Combines space weather monitoring with Arduino control.

    This is a complete system that fetches data and sends it to Arduino.
    """

    def __init__(self, port: str, poll_interval: int = 60):
        """
        Initialize the controller.

        Args:
            port: Arduino serial port
            poll_interval: How often to fetch data (seconds)
        """
        from solar_wind_fetcher import SolarWindFetcher
        from lighting_mapper import LightingMapper

        self.fetcher = SolarWindFetcher()
        self.mapper = LightingMapper()
        self.arduino = ArduinoInterface(port)
        self.poll_interval = poll_interval
        self.running = False

    def run(self):
        """
        Main loop: fetch data, map to lighting, send to Arduino.
        """
        # Connect to Arduino
        if not self.arduino.connect():
            print("❌ Failed to connect to Arduino. Exiting.")
            return

        print("🚀 Starting space weather → Arduino control loop")
        print("   Press Ctrl+C to stop\n")

        self.running = True

        try:
            while self.running:
                # Fetch solar wind data
                solar_data = self.fetcher.get_combined_data()

                if solar_data:
                    # Map to lighting
                    result = self.mapper.map_to_lighting(solar_data)

                    # Display status
                    print(f"\n⚡ BZ: {result['raw']['bz']:+.1f} nT | "
                          f"Speed: {result['raw']['speed']:.0f} km/s")

                    aurora_prob = self.mapper.get_aurora_probability(
                        result['raw']['bz'],
                        result['raw']['speed']
                    )
                    print(f"🌌 Aurora: {aurora_prob}")

                    rgb = result['lighting']['rgb']
                    print(f"💡 RGB: ({rgb['r']}, {rgb['g']}, {rgb['b']})")

                    # Send to Arduino
                    if self.arduino.send_lighting_data(result['lighting']):
                        print("✅ Data sent to Arduino")
                    else:
                        print("⚠️  Failed to send to Arduino")
                else:
                    print("⚠️  No data available this iteration")

                # Wait for next poll
                print(f"⏳ Next update in {self.poll_interval} seconds...\n")
                time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            print("\n\n🛑 Stopping controller (Ctrl+C received)")

        finally:
            self.arduino.disconnect()
            print("✅ Controller stopped cleanly")


def list_serial_ports():
    """List available serial ports."""
    import serial.tools.list_ports

    print("📡 Available serial ports:")
    ports = serial.tools.list_ports.comports()

    if not ports:
        print("   No serial ports found!")
        return

    for port in ports:
        print(f"   {port.device} - {port.description}")


def main():
    """
    Main entry point for Arduino integration.
    """
    parser = argparse.ArgumentParser(
        description="Send space weather data to Arduino LED controller"
    )

    parser.add_argument(
        '--port',
        type=str,
        help='Serial port (e.g., /dev/ttyUSB0 or COM3)'
    )

    parser.add_argument(
        '--list-ports',
        action='store_true',
        help='List available serial ports and exit'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Polling interval in seconds (default: 60)'
    )

    args = parser.parse_args()

    # List ports if requested
    if args.list_ports:
        list_serial_ports()
        return

    # Require port
    if not args.port:
        print("❌ Error: --port is required")
        print("   Run with --list-ports to see available ports")
        return

    # Create and run controller
    controller = SpaceWeatherArduinoController(
        port=args.port,
        poll_interval=args.interval
    )

    controller.run()


if __name__ == "__main__":
    main()
