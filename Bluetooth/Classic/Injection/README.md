---
title: Bluetooth Classic Injection Attacks
tags: [bluetooth-classic, injection, RFCOMM, A2DP, fuzzing]
category: Bluetooth Security
parent: "[[Bluetooth/Classic/README]]"
status: planned
---

# Bluetooth Classic Injection Attacks

> **Status**: 📋 Planned - Coming after WiFi research

## Attack Vectors

### 1. RFCOMM Command Injection
- Inject AT commands to SPP connections
- Serial terminal hijacking
- Malformed RFCOMM frames

### 2. A2DP Audio Injection
- Inject audio into media streams
- CarWhisperer attack implementation
- SBC codec manipulation

### 3. HFP AT Command Injection
- Inject dial commands (ATD)
- Volume control abuse
- Call control manipulation

### 4. OBEX Object Injection
- Push malicious vCards
- File injection via FTP profile
- Malformed object headers

### 5. L2CAP Fuzzing
- Malformed L2CAP configuration
- Invalid PSM values
- Segmentation attacks

## Tools & Implementation
- CarWhisperer for A2DP injection
- Custom RFCOMM clients
- Scapy for L2CAP fuzzing

---
**Related**: [[Bluetooth/Classic/README|Classic Overview]] • [[Bluetooth/BLE/Injection/README|BLE Injection]]
