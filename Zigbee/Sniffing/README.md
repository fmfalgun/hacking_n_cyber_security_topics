---
title: Zigbee Sniffing & Reconnaissance
tags: [zigbee, sniffing, KillerBee, network-discovery]
category: Zigbee Security
parent: "[[Zigbee/README]]"
status: comprehensive
---

# Zigbee Sniffing & Reconnaissance

> **Status**: 📋 Comprehensive framework

## Techniques

### 1. Network Discovery
**Tool**: zbstumbler (KillerBee)

**Captures**: PAN IDs, channels, device counts

### 2. Traffic Analysis
**Tool**: zbdump, Wireshark

**Extracts**: Packet types, addressing, encryption status

### 3. Key Extraction
**Methods**: Default keys, hardware dumps, side-channel

### 4. Topology Mapping
**Goal**: Identify coordinator, routers, end devices

## Pseudocode

```python
# Network discovery pseudocode

from killerbee import KillerBee

def discover_zigbee_networks():
    """
    Libraries:
    - killerbee: Zigbee sniffer
    
    Why:
    - zbstumbler scans all channels
    - Identifies active PANs
    - Passive, undetectable
    """
    
    for channel in range(11, 27):  # 2.4 GHz channels
        kb = KillerBee(channel=channel)
        # Capture beacons
        # Extract PAN ID, coordinator address
        pass
```

---
**Related**: [[Zigbee/README|Zigbee Overview]]
