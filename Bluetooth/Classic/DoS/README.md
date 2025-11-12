---
title: Bluetooth Classic DoS Attacks
tags: [bluetooth-classic, DoS, L2CAP, SDP, flooding]
category: Bluetooth Security
parent: "[[Bluetooth/Classic/README]]"
status: planned
---

# Bluetooth Classic Denial of Service Attacks

> **Status**: 📋 Planned - Coming after WiFi research

## Attack Vectors

### 1. L2CAP Connection Flooding
- Rapid connection requests to exhaust connection table
- Malformed L2CAP packets causing crashes
- Channel flooding (max 65535 PSMs)

### 2. SDP Query Flooding
- Rapid ServiceSearchRequest floods
- ServiceAttributeRequest with large result sets
- Malformed SDP records

### 3. RFCOMM Channel Exhaustion
- Open max channels (30) per connection
- Never close channels (resource leak)
- Malformed RFCOMM frames

### 4. Baseband Flooding
- ACL packet flooding at link layer
- SCO/eSCO audio channel saturation
- Page scan flooding during discovery

## Tools & Implementation
- BlueZ hcitool/l2ping for connection testing
- Custom Python/C scripts for flooding
- Scapy for malformed packet crafting

---
**Related**: [[Bluetooth/Classic/README|Classic Overview]] • [[Bluetooth/BLE/DoS/README|BLE DoS]]
