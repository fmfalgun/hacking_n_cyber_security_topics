#!/usr/bin/env python3
"""
Feature Extraction for ML Training
===================================

Extracts time-series and statistical features from labeled PCAP files
for machine learning model training.

Features Extracted:
- Packet timing (inter-arrival times, rate)
- Packet sizes (min, max, mean, std)
- Protocol-specific fields (frame types, opcodes, etc.)
- Statistical aggregations (sliding windows)

Output Format:
- CSV or Parquet for ML frameworks
- Compatible with scikit-learn, TensorFlow, PyTorch

Usage:
    python3 feature_extractor.py \
        --input-dir ../../Datasets/WiFi/labeled \
        --output-dir ../../Datasets/WiFi/processed \
        --format parquet

Author: Wireless Security Research
License: Educational Use Only
"""

import os
import sys
import argparse
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import pyshark
from datetime import datetime

# ============================================================================
# Feature Extractors
# ============================================================================

class BaseFeatureExtractor:
    """Base class for protocol-specific feature extraction"""

    def __init__(self, pcap_file: Path, labels_file: Path):
        self.pcap_file = pcap_file
        self.labels_file = labels_file
        self.labels = self.load_labels()
        self.features = []

    def load_labels(self) -> List[Dict]:
        """Load packet labels"""
        with open(self.labels_file, 'r') as f:
            return json.load(f)

    def extract_features(self) -> pd.DataFrame:
        """Extract features - to be implemented by subclasses"""
        raise NotImplementedError

    def compute_time_features(self, timestamps: List[float]) -> Dict:
        """Compute time-based features"""
        if len(timestamps) < 2:
            return {}

        # Inter-arrival times
        iat = np.diff(timestamps)

        features = {
            'iat_mean': float(np.mean(iat)),
            'iat_std': float(np.std(iat)),
            'iat_min': float(np.min(iat)),
            'iat_max': float(np.max(iat)),
            'iat_median': float(np.median(iat)),
            'packet_rate': len(timestamps) / (timestamps[-1] - timestamps[0]) if len(timestamps) > 1 else 0
        }

        return features

    def compute_size_features(self, sizes: List[int]) -> Dict:
        """Compute packet size features"""
        if not sizes:
            return {}

        features = {
            'size_mean': float(np.mean(sizes)),
            'size_std': float(np.std(sizes)),
            'size_min': int(np.min(sizes)),
            'size_max': int(np.max(sizes)),
            'size_median': float(np.median(sizes)),
            'total_bytes': int(np.sum(sizes))
        }

        return features

    def sliding_window_features(self, df: pd.DataFrame, window_size: int = 10) -> pd.DataFrame:
        """Add sliding window aggregations"""
        df['iat_rolling_mean'] = df['iat'].rolling(window=window_size, min_periods=1).mean()
        df['iat_rolling_std'] = df['iat'].rolling(window=window_size, min_periods=1).std()
        df['size_rolling_mean'] = df['packet_size'].rolling(window=window_size, min_periods=1).mean()
        df['size_rolling_std'] = df['packet_size'].rolling(window=window_size, min_periods=1).std()

        return df


class WiFiFeatureExtractor(BaseFeatureExtractor):
    """WiFi-specific feature extraction"""

    def extract_features(self) -> pd.DataFrame:
        """Extract WiFi features"""
        print(f"[*] Extracting WiFi features from {self.pcap_file.name}")

        features = []

        try:
            cap = pyshark.FileCapture(str(self.pcap_file), keep_packets=False)

            packet_num = 0
            for pkt in cap:
                packet_num += 1

                # Get label for this packet
                label_info = self.labels[packet_num - 1] if packet_num <= len(self.labels) else None

                try:
                    # Basic features
                    feature = {
                        'packet_number': packet_num,
                        'timestamp': float(pkt.sniff_timestamp) if hasattr(pkt, 'sniff_timestamp') else 0,
                        'packet_size': int(pkt.length) if hasattr(pkt, 'length') else 0,
                    }

                    # WiFi-specific features
                    if hasattr(pkt, 'wlan'):
                        feature['frame_type'] = int(pkt.wlan.fc_type) if hasattr(pkt.wlan, 'fc_type') else -1
                        feature['frame_subtype'] = int(pkt.wlan.fc_type_subtype) if hasattr(pkt.wlan, 'fc_type_subtype') else -1
                        feature['retry'] = int(pkt.wlan.fc_retry) if hasattr(pkt.wlan, 'fc_retry') else 0
                        feature['to_ds'] = int(pkt.wlan.fc_tods) if hasattr(pkt.wlan, 'fc_tods') else 0
                        feature['from_ds'] = int(pkt.wlan.fc_fromds) if hasattr(pkt.wlan, 'fc_fromds') else 0

                    # Add label
                    if label_info:
                        feature['label'] = label_info['label']
                        feature['is_attack'] = int(label_info['is_attack'])
                        feature['attack_category'] = label_info['attack_category']
                    else:
                        feature['label'] = 'unknown'
                        feature['is_attack'] = 0
                        feature['attack_category'] = 'unknown'

                    features.append(feature)

                    if packet_num % 1000 == 0:
                        print(f"\r    Processed: {packet_num} packets", end='', flush=True)

                except Exception as e:
                    # Skip malformed packets
                    continue

            cap.close()
            print(f"\r    Processed: {packet_num} packets - Complete")

        except Exception as e:
            print(f"\n[!] Error: {e}")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(features)

        # Add inter-arrival time
        if 'timestamp' in df.columns:
            df['iat'] = df['timestamp'].diff().fillna(0)

        # Add rolling window features
        if len(df) > 0:
            df = self.sliding_window_features(df)

        return df


class BLEFeatureExtractor(BaseFeatureExtractor):
    """BLE-specific feature extraction"""

    def extract_features(self) -> pd.DataFrame:
        """Extract BLE features"""
        print(f"[*] Extracting BLE features from {self.pcap_file.name}")

        features = []

        try:
            cap = pyshark.FileCapture(str(self.pcap_file), keep_packets=False)

            packet_num = 0
            for pkt in cap:
                packet_num += 1

                label_info = self.labels[packet_num - 1] if packet_num <= len(self.labels) else None

                try:
                    feature = {
                        'packet_number': packet_num,
                        'timestamp': float(pkt.sniff_timestamp) if hasattr(pkt, 'sniff_timestamp') else 0,
                        'packet_size': int(pkt.length) if hasattr(pkt, 'length') else 0,
                    }

                    # BLE-specific features
                    if hasattr(pkt, 'btle'):
                        feature['access_address'] = int(pkt.btle.access_address, 16) if hasattr(pkt.btle, 'access_address') else 0
                        feature['pdu_type'] = int(pkt.btle.advertising_header_pdu_type) if hasattr(pkt.btle, 'advertising_header_pdu_type') else -1

                    # ATT layer
                    if hasattr(pkt, 'btatt'):
                        feature['att_opcode'] = int(pkt.btatt.opcode, 16) if hasattr(pkt.btatt, 'opcode') else -1
                        feature['att_handle'] = int(pkt.btatt.handle, 16) if hasattr(pkt.btatt, 'handle') else -1

                    # Add label
                    if label_info:
                        feature['label'] = label_info['label']
                        feature['is_attack'] = int(label_info['is_attack'])
                        feature['attack_category'] = label_info['attack_category']
                    else:
                        feature['label'] = 'unknown'
                        feature['is_attack'] = 0
                        feature['attack_category'] = 'unknown'

                    features.append(feature)

                    if packet_num % 1000 == 0:
                        print(f"\r    Processed: {packet_num} packets", end='', flush=True)

                except Exception as e:
                    continue

            cap.close()
            print(f"\r    Processed: {packet_num} packets - Complete")

        except Exception as e:
            print(f"\n[!] Error: {e}")
            return pd.DataFrame()

        df = pd.DataFrame(features)

        if 'timestamp' in df.columns:
            df['iat'] = df['timestamp'].diff().fillna(0)

        if len(df) > 0:
            df = self.sliding_window_features(df)

        return df


# ============================================================================
# Main Feature Extraction Pipeline
# ============================================================================

class FeatureExtractionPipeline:
    """Main feature extraction pipeline"""

    def __init__(self, input_dir: str, output_dir: str, output_format: str = 'parquet'):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_format = output_format

        # Protocol to extractor mapping
        self.extractors = {
            'WiFi': WiFiFeatureExtractor,
            'BLE': BLEFeatureExtractor,
            # Add more as needed
        }

    def find_labeled_datasets(self) -> List[Path]:
        """Find all labeled datasets"""
        label_files = list(self.input_dir.glob("*.labels.json"))
        print(f"[+] Found {len(label_files)} labeled dataset(s)")
        return label_files

    def process_dataset(self, labels_file: Path):
        """Process single labeled dataset"""
        print(f"\n{'='*70}")
        print(f"Processing: {labels_file.stem}")
        print('='*70)

        # Find corresponding metadata
        metadata_file = labels_file.with_suffix('.metadata.json')
        if not metadata_file.exists():
            print(f"[!] No metadata file found: {metadata_file}")
            return

        # Load metadata
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        protocol = metadata.get('protocol')
        pcap_file = Path(metadata.get('pcap_file'))

        if not pcap_file.exists():
            print(f"[!] PCAP file not found: {pcap_file}")
            return

        # Get appropriate extractor
        extractor_class = self.extractors.get(protocol)
        if not extractor_class:
            print(f"[!] No extractor for protocol: {protocol}")
            return

        # Extract features
        extractor = extractor_class(pcap_file, labels_file)
        df = extractor.extract_features()

        if df.empty:
            print(f"[!] No features extracted")
            return

        # Save features
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if self.output_format == 'csv':
            output_file = self.output_dir / f"{labels_file.stem}.features.csv"
            df.to_csv(output_file, index=False)
        elif self.output_format == 'parquet':
            output_file = self.output_dir / f"{labels_file.stem}.features.parquet"
            df.to_parquet(output_file, index=False)
        else:
            print(f"[!] Unknown format: {self.output_format}")
            return

        print(f"\n[+] Features saved: {output_file}")
        print(f"    Shape: {df.shape}")
        print(f"    Columns: {list(df.columns)}")

        # Statistics
        if 'is_attack' in df.columns:
            attack_count = df['is_attack'].sum()
            benign_count = len(df) - attack_count
            print(f"    Attack samples: {attack_count}")
            print(f"    Benign samples: {benign_count}")

    def run(self):
        """Run feature extraction pipeline"""
        print("="*70)
        print("  Feature Extraction Pipeline")
        print("="*70)
        print(f"Input:  {self.input_dir}")
        print(f"Output: {self.output_dir}")
        print(f"Format: {self.output_format}")
        print("="*70 + "\n")

        # Find datasets
        label_files = self.find_labeled_datasets()

        if not label_files:
            print("[!] No labeled datasets found")
            return 1

        # Process each
        for i, labels_file in enumerate(label_files, 1):
            print(f"\n[*] Dataset {i}/{len(label_files)}")
            try:
                self.process_dataset(labels_file)
            except Exception as e:
                print(f"[!] Error: {e}")
                continue

        print("\n" + "="*70)
        print("  Feature Extraction Complete")
        print("="*70)
        print(f"Processed: {len(label_files)} dataset(s)")
        print(f"Output: {self.output_dir}")
        print("="*70 + "\n")

        return 0


# ============================================================================
# CLI
# ============================================================================

def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Feature Extraction for ML Training",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--input-dir', required=True,
                       help='Input directory with labeled data')
    parser.add_argument('--output-dir', required=True,
                       help='Output directory for features')
    parser.add_argument('--format', choices=['csv', 'parquet'], default='parquet',
                       help='Output format (default: parquet)')

    return parser.parse_args()


def main() -> int:
    """Main entry point"""
    args = parse_arguments()

    pipeline = FeatureExtractionPipeline(args.input_dir, args.output_dir, args.format)
    return pipeline.run()


if __name__ == '__main__':
    sys.exit(main())
