---
title: LoRa/LoRaWAN Injection Attacks
tags: [LoRa, LoRaWAN, injection, fuzzing, payload]
category: LoRa Security
parent: "[[LoRa/README]]"
status: planned
---

# LoRa/LoRaWAN Injection Attacks

> **Status**: 📋 Planned - Coming after Zigbee research

## Attack Vectors

### 1. Malicious Uplink Injection
- Inject fake sensor data
- Spoof DevAddr/DevEUI
- Malformed MAC payload
- Requires knowledge of network parameters

### 2. Downlink Command Injection
- Inject MAC commands (if NwkSKey known)
- Force device configuration changes
- LinkADRReq abuse (change data rate)
- DutyCycleReq abuse (limit transmissions)

### 3. Payload Fuzzing
- Malformed LoRaWAN frames
- Invalid FPort values
- MIC collision attempts
- Frame counter manipulation

### 4. MAC Command Injection
- LinkCheckReq flooding
- DevStatusReq abuse
- RXParamSetupReq (change RX parameters)
- NewChannelReq (add/remove channels)

### 5. Application Payload Injection
- Encrypted payload with guessed keys
- Bit-flipping attacks (exploit MIC weaknesses)
- Replay with modified payload

## Tools & Implementation
- LoRa32 (ESP32) with LMIC library
- Custom packet crafting scripts
- GNU Radio for PHY-level injection
- lorawan-parser for packet construction

---
**Related**: [[LoRa/README|LoRa Overview]] • [[Bluetooth/BLE/Injection/README|BLE Injection]]
