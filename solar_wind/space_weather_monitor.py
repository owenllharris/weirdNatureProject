#!/usr/bin/env python3
"""
Space Weather Monitor
=====================

Main script that fetches solar wind data and outputs lighting parameters.

This script polls NOAA's Space Weather Prediction Center APIs every minute,
processes the data, and outputs lighting parameters that can be used to
control LED installations.

Usage:
    python space_weather_monitor.py                    # Run with console output
    python space_weather_monitor.py --save output.json # Save to file
    python space_weather_monitor.py --interval 120     # Poll every 2 minutes

Author: Space Weather Lighting Project
"""

import argparse
import json
import time
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Import our custom modules
from solar_wind_fetcher import SolarWindFetcher
from lighting_mapper import LightingMapper


class SpaceWeatherMonitor:
    """
    Main monitoring class that coordinates fetching and mapping.

    This is the orchestrator - it brings together the data fetcher
    and the lighting mapper to create a complete monitoring system.
    """

    def __init__(self, poll_interval: int = 60, output_file: Optional[str] = None):
        """
        Initialize the monitor.

        Args:
            poll_interval: How often to fetch data (seconds, default: 60)
            output_file: Optional file path to save JSON output
        """
        self.fetcher = SolarWindFetcher()
        self.mapper = LightingMapper()
        self.poll_interval = poll_interval
        self.output_file = output_file
        self.running = False
        self.iteration_count = 0

        print("🛰️  Space Weather Monitor initialized")
        print(f"📡 Polling interval: {poll_interval} seconds")
        if output_file:
            print(f"💾 Saving output to: {output_file}")
        print()

    def fetch_and_process(self) -> Optional[dict]:
        """
        Fetch solar wind data and map it to lighting parameters.

        Returns:
            Dictionary with complete data and lighting parameters, or None if failed
        """
        # Fetch raw solar wind data
        solar_data = self.fetcher.get_combined_data()

        if solar_data is None:
            print("⚠️  No data available this iteration")
            return None

        # Map to lighting parameters
        result = self.mapper.map_to_lighting(solar_data)

        return result

    def save_to_file(self, data: dict):
        """
        Save the current data to a JSON file.

        Args:
            data: Data dictionary to save
        """
        if not self.output_file:
            return

        try:
            # Pretty-print JSON for readability
            with open(self.output_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"❌ Error writing to file: {e}")

    def print_compact_status(self, result: dict):
        """
        Print a compact one-line status update.

        Args:
            result: Result from fetch_and_process()
        """
        raw = result['raw']
        lighting = result['lighting']
        rgb = lighting['rgb']

        # Build status line
        bz_str = f"{raw['bz']:+.1f}nT" if raw['bz'] is not None else "N/A"
        speed_str = f"{raw['speed']:.0f}km/s" if raw['speed'] is not None else "N/A"

        # Color bar visualization (using terminal colors)
        color_bar = self._create_color_bar(lighting['hue'])

        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")

        print(f"[{timestamp}] BZ:{bz_str:>8} | Speed:{speed_str:>7} | "
              f"RGB({rgb['r']:3d},{rgb['g']:3d},{rgb['b']:3d}) {color_bar}")

    def _create_color_bar(self, hue: int) -> str:
        """
        Create a visual color bar using ANSI terminal colors.

        Args:
            hue: Hue value (0-360)

        Returns:
            Colored string for terminal display
        """
        # Map hue to approximate terminal color
        if 240 <= hue <= 300:
            return "🟣🟣🟣 Aurora!"
        elif 180 <= hue < 240:
            return "🔵🔵🔵"
        elif 120 <= hue < 180:
            return "🟢🟢🟢"
        elif 60 <= hue < 120:
            return "🟡🟡🟡"
        else:
            return "🟠🟠🟠"

    def run_once(self, verbose: bool = True):
        """
        Run one iteration: fetch, process, display, and save.

        Args:
            verbose: If True, print detailed status (default: True)
        """
        self.iteration_count += 1

        # Fetch and process
        result = self.fetch_and_process()

        if result is None:
            print("⚠️  Skipping this iteration due to fetch failure")
            return

        # Display results
        if verbose:
            # Print detailed status every 10 iterations or on first run
            if self.iteration_count == 1 or self.iteration_count % 10 == 0:
                print("\n" + "="*70)
                print(f"ITERATION #{self.iteration_count}")
                print("="*70)
                self.fetcher.print_status(result['raw'])
                self.mapper.print_lighting_status(result)
            else:
                # Print compact status for other iterations
                self.print_compact_status(result)
        else:
            # Always use compact status if not verbose
            self.print_compact_status(result)

        # Save to file if configured
        if self.output_file:
            self.save_to_file(result)

        # Also print the raw JSON every 10 iterations (useful for debugging)
        if verbose and self.iteration_count % 10 == 0:
            print("\n📊 JSON Output Preview:")
            print(json.dumps(result, indent=2))
            print()

    def run_continuous(self, verbose: bool = True):
        """
        Run continuously, polling at the configured interval.

        Args:
            verbose: If True, print detailed status periodically
        """
        self.running = True

        print("🚀 Starting continuous monitoring...")
        print("   Press Ctrl+C to stop\n")

        while self.running:
            try:
                # Run one iteration
                self.run_once(verbose=verbose)

                # Wait for next poll
                if self.running:  # Check again in case we stopped during run_once
                    print(f"⏳ Waiting {self.poll_interval} seconds until next poll...")
                    time.sleep(self.poll_interval)

            except KeyboardInterrupt:
                print("\n\n🛑 Stopping monitor (Ctrl+C received)")
                self.running = False
                break

            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("   Will retry on next iteration...")
                time.sleep(self.poll_interval)

        print("✅ Monitor stopped cleanly")

    def stop(self):
        """Stop the continuous monitoring loop."""
        self.running = False


def main():
    """
    Main entry point with command-line argument parsing.
    """
    parser = argparse.ArgumentParser(
        description="Monitor NOAA space weather and output lighting parameters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Run with default settings
  %(prog)s --interval 120               # Poll every 2 minutes
  %(prog)s --save output.json           # Save to file
  %(prog)s --once                       # Run once and exit
  %(prog)s --quiet                      # Minimal output
        """
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        metavar='SECONDS',
        help='Polling interval in seconds (default: 60)'
    )

    parser.add_argument(
        '--save',
        type=str,
        metavar='FILE',
        help='Save output to JSON file (updates every poll)'
    )

    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (don\'t poll continuously)'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Minimal output (compact status only)'
    )

    args = parser.parse_args()

    # Create and run monitor
    monitor = SpaceWeatherMonitor(
        poll_interval=args.interval,
        output_file=args.save
    )

    # Set up signal handler for clean shutdown
    def signal_handler(sig, frame):
        print("\n🛑 Received shutdown signal")
        monitor.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run once or continuously
    if args.once:
        monitor.run_once(verbose=not args.quiet)
    else:
        monitor.run_continuous(verbose=not args.quiet)


if __name__ == "__main__":
    main()
