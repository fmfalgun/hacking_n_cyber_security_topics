---
title: WiFi Man-in-the-Middle Attacks
tags: [wifi, MITM, evil-twin, rogue-ap, karma]
category: WiFi Security
parent: "[[WiFi/README]]"
status: user-managed
---

# WiFi Man-in-the-Middle Attacks

> **Status**: ✅ User Managed

## Attack Vectors

### 1. Evil Twin
**Mechanism**: Create identical AP, de-associate clients from legitimate AP

**Tools**: hostapd, dnsmasq, iptables

**Impact**: Credential capture, traffic interception

### 2. Karma Attack
**Mechanism**: Respond to all probe requests from clients

**Impact**: Auto-connect exploitation

**Tools**: hostapd-karma, WiFi Pineapple

### 3. Rogue AP
**Mechanism**: Unauthorized AP on network

**Impact**: Bypass network security, pivot point

### 4. Captive Portal Bypass
**Mechanism**: DNS tunneling, MAC spoofing

**Tools**: nodogsplash, coovachilli

### 5. SSL Stripping
**Mechanism**: Downgrade HTTPS to HTTP

**Tools**: sslstrip, bettercap

## Pseudocode

```python
# Evil Twin setup pseudocode
# Required: hostapd, dnsmasq, subprocess

import subprocess

def setup_evil_twin(interface, ssid, channel):
    """
    Libraries:
    - subprocess: Execute system commands
    - hostapd: Software AP daemon
    - dnsmasq: DHCP/DNS server
    
    Why:
    - hostapd: Industry-standard software AP
    - dnsmasq: Automatic IP assignment to victims
    - iptables: NAT for traffic forwarding
    """
    
    hostapd_conf = f"""
interface={interface}
ssid={ssid}
channel={channel}
driver=nl80211
"""
    
    # Write config, start hostapd, dnsmasq, enable forwarding
    pass
```

---
**Related**: [[WiFi/README|WiFi Overview]] • [[WiFi/DoS/README|DoS Attacks]]
