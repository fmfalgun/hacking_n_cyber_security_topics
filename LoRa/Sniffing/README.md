---
title: LoRa/LoRaWAN Sniffing & Reconnaissance
tags: [LoRa, LoRaWAN, sniffing, SDR, reconnaissance]
category: LoRa Security
parent: "[[LoRa/README]]"
status: planned
---

# LoRa/LoRaWAN Sniffing & Reconnaissance

> **Status**: 📋 Planned - Coming after Zigbee research

## Attack Vectors

### 1. Passive Packet Capture
- Receive LoRa signals with SDR (RTL-SDR, HackRF, LimeSDR)
- Decode LoRa PHY (Chirp Spread Spectrum)
- Extract LoRaWAN frames
- All spreading factors (SF7-SF12)

### 2. Device Enumeration
- Capture DevAddr from uplinks
- DevEUI extraction (OTAA join requests)
- AppEUI identification
- Device class identification (A/B/C)

### 3. Gateway Discovery
- Locate gateways via downlink transmissions
- Gateway EUI extraction
- Network server identification
- Coverage mapping

### 4. Traffic Pattern Analysis
- Transmission intervals
- Data rate usage (SF, BW)
- Duty cycle analysis
- Payload size patterns

### 5. Join Procedure Monitoring
- Capture OTAA join requests
- DevNonce tracking
- AppKey brute-force preparation (offline)

## Tools & Implementation
- RTL-SDR + gr-lora for cheap sniffing
- HackRF One for full-band monitoring
- GNU Radio flowgraphs
- Wireshark with LoRaWAN dissector
- lorawan-parser for frame analysis

---
**Related**: [[LoRa/README|LoRa Overview]] • [[Bluetooth/BLE/Sniffing/README|BLE Sniffing]]
