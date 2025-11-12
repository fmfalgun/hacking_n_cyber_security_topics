---
title: Zigbee Scripting & Packet Crafting
tags: [zigbee, scripting, KillerBee, scapy]
category: Zigbee Security
parent: "[[Zigbee/README]]"
status: comprehensive
---

# Zigbee Scripting & Packet Crafting

> **Status**: 📋 Comprehensive framework

## Overview

Comprehensive guide to Zigbee packet crafting using KillerBee (Python) and custom firmware (C/C++).

## Libraries

**Python:**
- `killerbee`: Zigbee protocol stack
- `scapy.layers.zigbee`: Packet structures (802.15.4, ZigbeeNWK, ZCL)
- `pycryptodome`: AES-CCM encryption

**C++:**
- Z-Stack, ZBOSS, EmberZNet: Zigbee stacks
- `<aes.h>`: Encryption
- `<802.15.4.h>`: PHY/MAC layer

## Topics

- 802.15.4 frame crafting
- Network layer routing
- APS/ZCL command construction
- Key derivation and encryption
- Attack automation

---
**Related**: [[Zigbee/README|Zigbee Overview]] • [[Bluetooth/BLE/Scripting/README|BLE Scripting]]
