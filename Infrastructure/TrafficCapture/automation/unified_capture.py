#!/usr/bin/env python3
"""
Unified Traffic Capture Manager
================================

Automated packet capture synchronized with attack execution for all 4 protocols:
- WiFi (802.11)
- BLE (Bluetooth Low Energy)
- Zigbee (IEEE 802.15.4)
- LoRa/LoRaWAN

Generates labeled PCAP files with metadata for ML dataset generation.

Usage:
    # Capture WiFi deauth attack
    sudo python3 unified_capture.py --protocol WiFi --attack deauth_attack \\
                                     --interface wlan0mon --duration 60

    # Capture BLE ATT write flood
    sudo python3 unified_capture.py --protocol BLE --attack att_write_flood \\
                                     --interface hci0 --duration 30

Author: Wireless Security Research
License: Educational Use Only
"""

import subprocess
import sys
import os
import time
import argparse
import yaml
import signal
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, asdict

# ============================================================================
# Configuration
# ============================================================================

@dataclass
class CaptureConfig:
    """Capture configuration"""
    protocol: str
    attack_type: str
    attack_category: str  # DoS, MITM, Injection
    interface: str
    duration: int
    output_dir: str
    attack_script: Optional[str] = None
    attack_params: Optional[Dict] = None
    capture_filter: Optional[str] = None


# Protocol-specific capture commands
CAPTURE_COMMANDS = {
    "WiFi": "tcpdump -i {interface} -w {output_file} -s 0 {filter}",
    "BLE": "btmon -w {output_file}",
    "Zigbee": "zbdump -i {interface} -w {output_file}",
    "LoRa": "python3 lora_capture.py --output {output_file}"
}

# Default filters for cleaner captures
DEFAULT_FILTERS = {
    "WiFi": "type mgt subtype deauth or type mgt subtype disassoc or type mgt subtype beacon",
    "BLE": "",  # btmon captures all HCI traffic
    "Zigbee": "",
    "LoRa": ""
}

# ============================================================================
# Traffic Capture Manager
# ============================================================================

class UnifiedCaptureManager:
    """Manage synchronized attack + capture sessions"""

    def __init__(self, config: CaptureConfig):
        self.config = config
        self.capture_process = None
        self.attack_process = None
        self.start_time = None
        self.metadata = {}

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print(f"\n[!] Caught signal {signum}, stopping capture...")
        self.stop_capture()
        sys.exit(0)

    def generate_filename(self) -> str:
        """Generate timestamped capture filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.config.protocol}_{self.config.attack_category}_{self.config.attack_type}_{timestamp}.pcap"
        return os.path.join(self.config.output_dir, filename)

    def start_capture(self) -> bool:
        """Start packet capture process"""
        output_file = self.generate_filename()

        # Get capture command for protocol
        cmd_template = CAPTURE_COMMANDS.get(self.config.protocol)
        if not cmd_template:
            print(f"[!] Unknown protocol: {self.config.protocol}")
            return False

        # Apply filter
        capture_filter = self.config.capture_filter or DEFAULT_FILTERS.get(self.config.protocol, "")

        # Build command
        cmd = cmd_template.format(
            interface=self.config.interface,
            output_file=output_file,
            filter=capture_filter if capture_filter else ""
        )

        print(f"[*] Starting capture: {self.config.protocol}")
        print(f"    Interface: {self.config.interface}")
        print(f"    Output: {output_file}")
        print(f"    Command: {cmd}")

        try:
            self.capture_process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.start_time = time.time()
            self.metadata["capture_file"] = output_file
            self.metadata["start_time"] = datetime.now().isoformat()
            self.metadata["protocol"] = self.config.protocol
            self.metadata["attack_type"] = self.config.attack_type
            self.metadata["attack_category"] = self.config.attack_category
            self.metadata["interface"] = self.config.interface

            print(f"[+] Capture started (PID: {self.capture_process.pid})")
            time.sleep(2)  # Give capture time to initialize
            return True

        except Exception as e:
            print(f"[!] Failed to start capture: {e}")
            return False

    def start_attack(self) -> bool:
        """Launch attack script if specified"""
        if not self.config.attack_script:
            print("[*] No attack script specified, manual attack mode")
            return True

        if not os.path.exists(self.config.attack_script):
            print(f"[!] Attack script not found: {self.config.attack_script}")
            return False

        # Build attack command
        cmd = [sys.executable, self.config.attack_script]

        # Add attack parameters
        if self.config.attack_params:
            for key, value in self.config.attack_params.items():
                cmd.append(f"--{key}")
                cmd.append(str(value))

        print(f"[*] Launching attack: {self.config.attack_type}")
        print(f"    Script: {self.config.attack_script}")
        print(f"    Command: {' '.join(cmd)}")

        try:
            self.attack_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.metadata["attack_script"] = self.config.attack_script
            self.metadata["attack_params"] = self.config.attack_params
            self.metadata["attack_start_time"] = datetime.now().isoformat()

            print(f"[+] Attack started (PID: {self.attack_process.pid})")
            return True

        except Exception as e:
            print(f"[!] Failed to start attack: {e}")
            return False

    def monitor_session(self):
        """Monitor capture and attack progress"""
        print(f"\n[*] Session active for {self.config.duration} seconds")
        print("    Press Ctrl+C to stop early\n")

        end_time = time.time() + self.config.duration
        last_update = time.time()

        while time.time() < end_time:
            # Update status every 5 seconds
            if time.time() - last_update >= 5:
                elapsed = int(time.time() - self.start_time)
                remaining = int(end_time - time.time())

                # Check if processes are still running
                capture_status = "Running" if self.capture_process and self.capture_process.poll() is None else "Stopped"
                attack_status = "Running" if self.attack_process and self.attack_process.poll() is None else "Stopped"

                print(f"\r[*] Elapsed: {elapsed}s | Remaining: {remaining}s | "
                      f"Capture: {capture_status} | Attack: {attack_status}", end='', flush=True)

                last_update = time.time()

            time.sleep(0.5)

        print("\n\n[*] Duration complete")

    def stop_capture(self):
        """Stop capture and attack processes"""
        print("\n[*] Stopping session...")

        # Stop attack first
        if self.attack_process and self.attack_process.poll() is None:
            print("    Terminating attack process...")
            self.attack_process.terminate()
            try:
                self.attack_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.attack_process.kill()

        # Stop capture
        if self.capture_process and self.capture_process.poll() is None:
            print("    Terminating capture process...")
            self.capture_process.terminate()
            try:
                self.capture_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.capture_process.kill()

        # Update metadata
        self.metadata["end_time"] = datetime.now().isoformat()
        self.metadata["duration_seconds"] = int(time.time() - self.start_time) if self.start_time else 0

    def save_metadata(self):
        """Save capture metadata as YAML"""
        capture_file = self.metadata.get("capture_file")
        if not capture_file:
            print("[!] No capture file found")
            return

        metadata_file = capture_file.replace(".pcap", ".yaml")

        print(f"\n[*] Saving metadata: {metadata_file}")

        # Add file statistics
        if os.path.exists(capture_file):
            file_size = os.path.getsize(capture_file)
            self.metadata["file_size_bytes"] = file_size
            self.metadata["file_size_mb"] = round(file_size / (1024*1024), 2)
        else:
            print(f"[!] Warning: Capture file not found: {capture_file}")

        # Write YAML
        with open(metadata_file, 'w') as f:
            yaml.dump(self.metadata, f, default_flow_style=False, sort_keys=False)

        print(f"[+] Metadata saved")

    def run(self) -> int:
        """Execute complete capture session"""
        print("="*70)
        print("  Unified Traffic Capture Manager")
        print("="*70)
        print(f"Protocol:       {self.config.protocol}")
        print(f"Attack Type:    {self.config.attack_type}")
        print(f"Category:       {self.config.attack_category}")
        print(f"Interface:      {self.config.interface}")
        print(f"Duration:       {self.config.duration} seconds")
        print(f"Output Dir:     {self.config.output_dir}")
        print("="*70 + "\n")

        # Create output directory
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)

        # Start capture
        if not self.start_capture():
            return 1

        # Start attack (optional)
        if not self.start_attack():
            self.stop_capture()
            return 1

        try:
            # Monitor session
            self.monitor_session()

        except KeyboardInterrupt:
            print("\n[!] Interrupted by user")

        finally:
            # Cleanup
            self.stop_capture()
            self.save_metadata()

        print("\n[+] Session complete")
        return 0


# ============================================================================
# CLI
# ============================================================================

def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Unified Traffic Capture Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Required
    parser.add_argument('--protocol', required=True,
                       choices=['WiFi', 'BLE', 'Zigbee', 'LoRa'],
                       help='Protocol to capture')
    parser.add_argument('--attack', required=True,
                       help='Attack type (e.g., deauth_attack, att_write_flood)')
    parser.add_argument('--category', required=True,
                       choices=['DoS', 'MITM', 'Injection'],
                       help='Attack category')
    parser.add_argument('--interface', required=True,
                       help='Network interface (e.g., wlan0mon, hci0)')

    # Optional
    parser.add_argument('--duration', type=int, default=60,
                       help='Capture duration in seconds (default: 60)')
    parser.add_argument('--output-dir', default='../../Datasets',
                       help='Output directory (default: ../../Datasets)')
    parser.add_argument('--attack-script',
                       help='Path to attack script to execute')
    parser.add_argument('--attack-params',
                       help='Attack parameters as JSON string')
    parser.add_argument('--filter',
                       help='Custom capture filter')

    return parser.parse_args()


def main() -> int:
    """Main entry point"""
    args = parse_arguments()

    # Check root privileges
    if os.geteuid() != 0:
        print("[!] ERROR: This script requires root privileges")
        print("    Run with: sudo python3 unified_capture.py ...")
        return 1

    # Parse attack params if provided
    attack_params = None
    if args.attack_params:
        import json
        try:
            attack_params = json.loads(args.attack_params)
        except json.JSONDecodeError as e:
            print(f"[!] Invalid JSON in --attack-params: {e}")
            return 1

    # Create configuration
    config = CaptureConfig(
        protocol=args.protocol,
        attack_type=args.attack,
        attack_category=args.category,
        interface=args.interface,
        duration=args.duration,
        output_dir=args.output_dir,
        attack_script=args.attack_script,
        attack_params=attack_params,
        capture_filter=args.filter
    )

    # Run capture
    manager = UnifiedCaptureManager(config)
    return manager.run()


if __name__ == '__main__':
    sys.exit(main())
