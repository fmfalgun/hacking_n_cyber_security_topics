---
title: WiFi Scripting & Packet Crafting
tags: [wifi, scripting, scapy, python]
category: WiFi Security
parent: "[[WiFi/README]]"
status: user-managed
---

# WiFi Scripting & Packet Crafting

> **Status**: ✅ User Managed

## Overview
Comprehensive guide to crafting 802.11 frames using Python (Scapy) and C++ (libpcap).

## Topics

### Frame Crafting Basics
- Management frames (beacon, probe, auth, assoc, deauth, disassoc)
- Control frames (RTS, CTS, ACK)
- Data frames (with encryption)

### Libraries

**Python:**
- `scapy.layers.dot11`: 802.11 frame structures
- `scapy.layers.eap`: EAPOL for WPA handshakes
- `socket`: Raw socket access

**C++:**
- `<pcap.h>`: libpcap for injection/capture
- `<net/if.h>`: Network interface control
- `<netinet/if_ether.h>`: Ethernet headers

### Automation
- Attack orchestration
- Multi-target campaigns
- Traffic analysis pipelines

---
**Related**: [[WiFi/README|WiFi Overview]] • [[Bluetooth/BLE/Scripting/README|BLE Scripting]]
