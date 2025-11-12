---
title: LoRa/LoRaWAN DoS Attacks
tags: [LoRa, LoRaWAN, DoS, jamming, flooding]
category: LoRa Security
parent: "[[LoRa/README]]"
status: planned
---

# LoRa/LoRaWAN Denial of Service Attacks

> **Status**: 📋 Planned - Coming after Zigbee research

## Attack Vectors

### 1. RF Jamming
- Continuous noise on LoRa frequency bands (433/868/915 MHz)
- Targeted jamming of specific spreading factors
- Sweep jamming across bandwidth
- Requires SDR (HackRF, LimeSDR)

### 2. Join Request Flooding (OTAA)
- Flood gateway with OTAA join requests
- Exhaust network server resources
- DevNonce exhaustion

### 3. Uplink Flooding
- Rapid uplink message transmission
- Gateway packet buffer exhaustion
- Network server overload

### 4. Collision Attacks
- Precise timing to collide with legitimate packets
- Requires synchronization with target device
- Exploits LoRa collision vulnerability

### 5. Acknowledgment Flooding
- Trigger repeated retransmissions
- Drain end-device battery
- Confirmed uplink abuse

## Tools & Implementation
- HackRF One / LimeSDR for jamming
- LoRa32 (ESP32) for protocol-level DoS
- GNU Radio for custom attacks
- gr-lora for LoRa signal generation

---
**Related**: [[LoRa/README|LoRa Overview]] • [[Bluetooth/BLE/DoS/README|BLE DoS]]
