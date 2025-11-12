---
title: BLE Sniffing & Reconnaissance
tags: [BLE, sniffing, reconnaissance, traffic-analysis]
category: BLE Security
parent: "[[Bluetooth/BLE/README]]"
status: active
---

# BLE Sniffing & Reconnaissance

## Overview

Sniffing attacks involve passive or active monitoring of BLE communications to gather intelligence, capture credentials, or analyze protocol behavior.

## Attack Vectors

### 1. Passive Sniffing
- Advertisement packet capture
- Connection establishment monitoring
- Unencrypted data capture
- Device fingerprinting

### 2. Active Sniffing
- Service discovery (GATT enumeration)
- Characteristic enumeration
- Descriptor reading
- Connection following

### 3. Traffic Analysis
- Timing analysis
- Pattern recognition
- Frequency analysis
- Connection tracking

## Tools & Techniques

- **Ubertooth**: Hardware BLE sniffer
- **nRF Sniffer**: Nordic Semiconductor's sniffer
- **Wireshark**: Packet analysis
- **btmon**: BlueZ monitor
- **hcitool/gatttool**: Service enumeration
- **bettercap**: BLE reconnaissance framework

## Information Gathering

- Device names and addresses
- Manufacturer data
- Services and characteristics UUIDs
- Connection parameters
- Security capabilities

## Implementation

Detailed capture and analysis procedures coming soon.

---
**Related**: [[Bluetooth/BLE/MITM/README|BLE MITM]] • [[Traffic-Capture/README|Traffic Capture]] • [[Bluetooth/BLE/README|BLE Home]]
