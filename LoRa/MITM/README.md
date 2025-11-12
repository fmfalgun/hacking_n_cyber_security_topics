---
title: LoRa/LoRaWAN MITM Attacks
tags: [LoRa, LoRaWAN, MITM, rogue-gateway, wormhole]
category: LoRa Security
parent: "[[LoRa/README]]"
status: planned
---

# LoRa/LoRaWAN Man-in-the-Middle Attacks

> **Status**: 📋 Planned - Coming after Zigbee research

## Attack Vectors

### 1. Rogue Gateway
- Deploy fake gateway closer to target devices
- Capture uplink messages
- Inject malicious downlinks (if keys known)
- Requires ChirpStack or custom gateway software

### 2. Wormhole Attack
- Relay packets between distant locations
- Two colluding gateways
- Disrupt network topology
- GPS spoofing for Class B devices

### 3. Join Accept Manipulation
- Intercept OTAA join procedure
- Modify join accept (requires AppKey)
- Downgrade security parameters

### 4. Downlink Injection
- Inject malicious downlink commands
- Requires NwkSKey or AppSKey
- MAC command manipulation
- Firmware update hijacking

### 5. Replay Attacks
- Capture and replay uplink messages
- Exploit weak frame counter validation
- Trigger duplicate processing

## Tools & Implementation
- ChirpStack (rogue gateway)
- LoRa32 with custom firmware
- SDR for signal relay
- LoRaWAN packet parser

---
**Related**: [[LoRa/README|LoRa Overview]] • [[Bluetooth/BLE/MITM/README|BLE MITM]]
