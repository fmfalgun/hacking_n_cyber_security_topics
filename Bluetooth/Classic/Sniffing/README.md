---
title: Bluetooth Classic Sniffing & Reconnaissance
tags: [bluetooth-classic, sniffing, SDP, device-discovery]
category: Bluetooth Security
parent: "[[Bluetooth/Classic/README]]"
status: planned
---

# Bluetooth Classic Sniffing & Reconnaissance

> **Status**: 📋 Planned - Coming after WiFi research

## Attack Vectors

### 1. Device Discovery
- Inquiry scan (`hcitool scan`)
- Hidden device discovery (Redfang)
- Class of Device (CoD) fingerprinting
- Manufacturer identification

### 2. Service Enumeration
- SDP browsing (`sdptool browse`)
- Profile detection (A2DP, HFP, SPP, etc.)
- Service record extraction
- UUID enumeration

### 3. Audio Stream Capture
- A2DP stream sniffing with Ubertooth
- HFP call audio capture
- SBC codec decoding

### 4. RFCOMM Traffic Monitoring
- Serial data capture (SPP)
- AT command logging
- Terminal session recording

### 5. Passive Traffic Analysis
- Connection pattern analysis
- Device tracking via BD_ADDR
- Timing analysis

## Tools & Implementation
- hcitool for device discovery
- sdptool for service enumeration
- Ubertooth One for passive sniffing
- Wireshark for protocol analysis

---
**Related**: [[Bluetooth/Classic/README|Classic Overview]] • [[Bluetooth/BLE/Sniffing/README|BLE Sniffing]]
