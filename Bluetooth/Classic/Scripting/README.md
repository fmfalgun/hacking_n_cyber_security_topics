---
title: Bluetooth Classic Scripting & Implementation
tags: [bluetooth-classic, scripting, python, L2CAP, RFCOMM]
category: Bluetooth Security
parent: "[[Bluetooth/Classic/README]]"
status: planned
---

# Bluetooth Classic Scripting & Implementation

> **Status**: 📋 Planned - Coming after WiFi research

## Overview

Practical implementation guides for crafting Bluetooth Classic attacks using Python and C++ with BlueZ and PyBluez libraries.

## Planned Content

### L2CAP Socket Programming
- Raw L2CAP sockets in Python
- Connection establishment
- PSM handling
- Configuration requests

### RFCOMM Communication
- PyBluez RFCOMM sockets
- SPP emulation
- AT command injection
- Serial bridge attacks

### SDP Interaction
- Service registration
- Service browsing automation
- SDP record manipulation

### HCI Command Injection
- Raw HCI socket access
- Link Manager commands
- Custom connection parameters

### Profile Implementation
- A2DP source/sink
- HFP hands-free unit
- SPP virtual serial ports

## Tools & Libraries
- **PyBluez**: Python Bluetooth library
- **BlueZ**: Linux Bluetooth stack
- **Scapy**: Packet crafting (Bluetooth layers)
- **libbluetooth-dev**: C development

---
**Related**: [[Bluetooth/Classic/README|Classic Overview]] • [[Bluetooth/BLE/Scripting/README|BLE Scripting]]
