---
title: Bluetooth Classic MITM Attacks
tags: [bluetooth-classic, MITM, pairing, SSP, KNOB, BIAS]
category: Bluetooth Security
parent: "[[Bluetooth/Classic/README]]"
status: planned
---

# Bluetooth Classic Man-in-the-Middle Attacks

> **Status**: 📋 Planned - Coming after WiFi research

## Attack Vectors

### 1. Legacy Pairing Attacks
- PIN sniffing with Ubertooth during pairing
- Brute-force 4-digit PINs
- PIN relay attacks

### 2. SSP Downgrade
- Force Secure Simple Pairing to legacy mode
- Exploit Just Works association model
- Numeric comparison manipulation

### 3. KNOB Attack (CVE-2019-9506)
- Force 1-byte encryption key during negotiation
- Brute-force key in real-time
- MITM established connections

### 4. BIAS Attack (CVE-2020-10135)
- Impersonate previously-paired device
- Bypass mutual authentication
- No pairing required

### 5. Audio Stream Hijacking
- A2DP stream interception
- Audio injection into HFP calls
- Real-time audio modification

## Tools & Implementation
- Ubertooth One for sniffing pairing
- KNOB attack PoC tools
- Custom L2CAP proxy scripts

---
**Related**: [[Bluetooth/Classic/README|Classic Overview]] • [[Bluetooth/BLE/MITM/README|BLE MITM]]
