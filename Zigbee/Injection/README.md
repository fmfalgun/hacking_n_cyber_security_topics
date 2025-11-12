---
title: Zigbee Injection Attacks
tags: [zigbee, injection, ZCL-commands, replay]
category: Zigbee Security
parent: "[[Zigbee/README]]"
status: comprehensive
---

# Zigbee Injection Attacks

> **Status**: 📋 Comprehensive framework

## Attack Vectors

### 1. ZCL Command Injection
**Target**: Application layer commands (On/Off, Level Control)

**Tools**: KillerBee zbreplay, custom scripts

### 2. Replay Attacks
**Mechanism**: Capture and replay commands

**Requirement**: No frame counter validation

### 3. Malicious Firmware (OTA)
**Mechanism**: Hijack OTA update process

**Impact**: Persistent backdoor

### 4. Routing Manipulation
**Mechanism**: Inject malicious route advertisements

**Impact**: Traffic redirection, sinkhole

## Pseudocode

```python
# ZCL command injection pseudocode

from scapy.layers.zigbee import *

def inject_zcl_command(target_short_addr, cluster_id, command_id):
    """
    Libraries:
    - scapy.layers.zigbee: ZCL packet structures
    - killerbee: Radio transmission
    
    Why:
    - ZCL commands control device behavior
    - Cluster 0x0006 = On/Off switch
    - Command 0x01 = Turn On
    """
    
    packet = ZigbeeNWK(destination=target_short_addr) / \
             ZigbeeAppDataPayload(cluster=cluster_id, cmd_identifier=command_id)
    
    # kb.inject(packet)
    pass
```

---
**Related**: [[Zigbee/README|Zigbee Overview]]
