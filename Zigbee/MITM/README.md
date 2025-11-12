---
title: Zigbee Man-in-the-Middle Attacks
tags: [zigbee, MITM, coordinator-impersonation, key-interception]
category: Zigbee Security
parent: "[[Zigbee/README]]"
status: comprehensive
---

# Zigbee Man-in-the-Middle Attacks

> **Status**: 📋 Comprehensive framework

## Attack Vectors

### 1. Malicious Coordinator
**Mechanism**: Create fake PAN, lure devices to join

**Tools**: KillerBee, custom coordinator firmware

**Impact**: Key extraction, command interception

### 2. Key Transport Interception
**Mechanism**: Capture network key during join process

**Requirement**: Know Trust Center Link Key (often default)

### 3. Touchlink Commissioning MITM
**Mechanism**: Intercept touchlink pairing with high-gain antenna

**Impact**: Device control, network access

### 4. Router Impersonation
**Mechanism**: Spoof legitimate router

**Impact**: Traffic interception, routing manipulation

## Pseudocode

```python
# Malicious coordinator pseudocode
# Required: KillerBee, ATUSB

from killerbee import KillerBee

def create_malicious_coordinator(panid, channel):
    """
    Libraries:
    - killerbee: Zigbee stack implementation
    - scapy.layers.zigbee: Packet crafting
    
    Why:
    - KillerBee provides coordinator functionality
    - Can intercept join requests
    - Extract network keys from traffic
    """
    
    kb = KillerBee(channel=channel)
    
    # Send beacons as coordinator
    # Permit joining
    # Capture association requests
    # Intercept key transport
    pass
```

---
**Related**: [[Zigbee/README|Zigbee Overview]] • [[Zigbee/DoS/README|DoS Attacks]]
