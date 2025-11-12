---
title: LoRa/LoRaWAN Protocol Security Research
tags: [LoRa, LoRaWAN, IoT, LPWAN, long-range]
category: Wireless Protocols
parent: "[[README]]"
status: comprehensive
---

# LoRa/LoRaWAN Protocol Security Research

## Overview

**LoRa** (Long Range) is a low-power wide-area network (LPWAN) protocol designed for long-range communication (up to 15km) with minimal power consumption. It's widely used in IoT applications like smart cities, agriculture, asset tracking, and industrial monitoring.

> **📚 For complete protocol breakdown**: See **[[LoRa/01-protocol-overview|Complete LoRa/LoRaWAN Protocol Overview]]**
>
> Comprehensive technical documentation covering:
> - LoRa Physical Layer (Chirp Spread Spectrum modulation, spreading factors, frequency bands)
> - LoRaWAN MAC Layer (Classes A/B/C, OTAA/ABP activation, frame formats)
> - Network architecture (End Device → Gateway → Network Server → Application Server)
> - Security mechanisms (AES-128, AppSKey, NwkSKey, AppKey)
> - Attack surfaces and vulnerabilities
> - Regional frequency allocations

## Attack Categories

### [[LoRa/DoS/README|Denial of Service]]
Jamming, join request flooding, gateway resource exhaustion, collision attacks

### [[LoRa/MITM/README|Man-in-the-Middle]]
Rogue gateway deployment, downlink injection, join accept manipulation, wormhole attacks

### [[LoRa/Injection/README|Injection Attacks]]
Malicious uplink injection, downlink command injection, MAC command injection, packet fuzzing

### [[LoRa/Sniffing/README|Sniffing & Reconnaissance]]
Passive packet capture with SDR, DevAddr enumeration, gateway discovery, traffic pattern analysis

## Directory Structure

```
LoRa/
├── README.md (this file - navigation hub)
├── 01-protocol-overview.md (complete protocol breakdown)
├── DoS/
│   └── README.md
├── MITM/
│   └── README.md
├── Injection/
│   └── README.md
├── Sniffing/
│   └── README.md
└── Scripting/
    └── README.md
```

---

**Related**:
- [[README|Home]]
- [[INDEX|Complete Index]]
- [[Bluetooth/README|Bluetooth]]
- [[WiFi/README|WiFi]]
- [[Zigbee/README|Zigbee]]

**Status**: Planned for post-Zigbee research phase
