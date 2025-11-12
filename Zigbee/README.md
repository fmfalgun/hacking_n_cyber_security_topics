---
title: Zigbee (IEEE 802.15.4) Protocol Security Research
tags: [zigbee, 802.15.4, IoT, smart-home, industrial-iot]
category: Wireless Protocols
parent: "[[README]]"
status: comprehensive
---

# Zigbee (IEEE 802.15.4) Protocol Security Research

## Overview

Zigbee is a low-power, low-data-rate wireless mesh networking protocol built on IEEE 802.15.4, widely deployed in smart homes (Philips Hue, SmartThings), industrial automation, and IoT devices. Operating in 2.4 GHz (global), 868 MHz (EU), and 915 MHz (US) bands.

> **📚 For complete protocol breakdown**: See **[[Zigbee/01-protocol-overview|Complete Zigbee Protocol Overview]]**
>
> Comprehensive technical documentation covering:
> - Complete protocol stack (PHY → MAC → NWK → APS → ZCL)
> - Frame structures and packet formats
> - Security mechanisms (AES-CCM*, key management)
> - Device types and network topology
> - Channel allocations and frequency planning
> - Attack surfaces and vulnerabilities

## Attack Categories

### [[Zigbee/DoS/README|Denial of Service]]
Channel jamming, beacon flooding, association request flooding, coordinator resource exhaustion

### [[Zigbee/MITM/README|Man-in-the-Middle]]
Malicious coordinator, router impersonation, key transport interception, touchlink commissioning MITM

### [[Zigbee/Injection/README|Injection Attacks]]
ZCL command injection, replay attacks, malicious firmware injection, routing manipulation

### [[Zigbee/Sniffing/README|Sniffing & Reconnaissance]]
Network discovery, key extraction, traffic analysis, device fingerprinting, topology mapping

### [[Zigbee/Scripting/README|Scripting & Packet Crafting]]
KillerBee framework, Scapy Zigbee layers, custom packet injection, automated attack scripts

## Directory Structure

```
Zigbee/
├── README.md (this file - navigation hub)
├── 01-protocol-overview.md (complete protocol breakdown)
├── DoS/
│   ├── README.md
│   ├── 01-dos-attack-theory.md
│   ├── 02-dos-implementation-guide.md
│   └── 03-dos-attack-cheatsheet.md
├── MITM/
│   ├── README.md
│   └── 01-mitm-attack-theory.md
├── Injection/
│   ├── README.md
│   └── 01-injection-attack-theory.md
├── Sniffing/
│   ├── README.md
│   └── 01-sniffing-techniques.md
└── Scripting/
    ├── README.md
    └── 01-packet-crafting-basics.md
```

---

**Related**: [[README|Home]] • [[INDEX|Index]] • [[Bluetooth/README|Bluetooth]] • [[WiFi/README|WiFi]] • [[LoRa/README|LoRa]]

**Status**: Comprehensive framework - Ready for Q2 2025 implementation
