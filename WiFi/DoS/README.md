---
title: WiFi Denial of Service Attacks
tags: [wifi, DoS, deauth, disassoc, beacon-flood]
category: WiFi Security
parent: "[[WiFi/README]]"
status: user-managed
---

# WiFi Denial of Service Attacks

> **Status**: ✅ User Managed - Comprehensive framework provided

## Overview

WiFi DoS attacks exploit the 802.11 MAC layer's lack of authentication for management frames (prior to 802.11w) and resource limitations in Access Points and clients.

## Attack Vectors

### 1. Deauthentication Attack
**Mechanism**: Send spoofed deauth frames from AP → Client

**Impact**: Force client disconnection, facilitate handshake capture

**Mitigation**: 802.11w (PMF - Protected Management Frames)

### 2. Disassociation Attack  
**Mechanism**: Send spoofed disassoc frames

**Impact**: Similar to deauth, breaks association

**Mitigation**: 802.11w (PMF)

### 3. Beacon Flooding
**Mechanism**: Broadcast fake beacon frames

**Impact**: Overwhelm scanners, hide legitimate APs

**Mitigation**: Rate limiting, WIDS detection

### 4. Authentication/Association Flooding
**Mechanism**: Rapid auth/assoc requests

**Impact**: Exhaust AP resources

**Mitigation**: Connection rate limiting

### 5. CTS/RTS Flooding
**Mechanism**: Continuous RTS or CTS frames

**Impact**: Reserve medium, block legitimate traffic

**Mitigation**: CTS-to-self detection

### 6. Virtual Carrier Sense Attack
**Mechanism**: Set large NAV (Network Allocation Vector) values

**Impact**: Make clients think medium is busy

**Mitigation**: NAV value validation

##Document Organization

- [[WiFi/DoS/01-dos-attack-theory|DoS Attack Theory]] - Detailed analysis of each vector
- [[WiFi/DoS/02-dos-implementation-guide|Implementation Guide]] - Step-by-step attack procedures
- [[WiFi/DoS/03-dos-attack-cheatsheet|Quick Reference]] - Frame structures and field values

## Tools

- **aireplay-ng**: Deauth/disassoc injection
- **mdk4**: Advanced DoS toolkit (beacon flood, auth flood)
- **Scapy**: Custom frame crafting

## Pseudocode Example

```python
# Deauth attack pseudocode
# Required: scapy, monitor mode interface

from scapy.layers.dot11 import Dot11, Dot11Deauth, RadioTap

def deauth_attack(ap_mac, client_mac, count=10):
    """
    Libraries:
    - scapy.layers.dot11: 802.11 frame structures
    - RadioTap: Radiotap header for injection
    
    Why:
    - Dot11: 802.11 MAC header with addr fields
    - Dot11Deauth: Deauth frame type with reason code
    - RadioTap: Required for monitor mode transmission
    """
    packet = RadioTap() / \
             Dot11(addr1=client_mac, addr2=ap_mac, addr3=ap_mac) / \
             Dot11Deauth(reason=7)  # reason=7: Class 3 frame from non-associated STA
    
    # sendp(packet, iface="wlan0mon", count=count, inter=0.1)
    pass
```

---
**Related**: [[WiFi/README|WiFi Overview]] • [[Bluetooth/BLE/DoS/README|BLE DoS]]
