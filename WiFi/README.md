---
title: WiFi (802.11) Protocol Security Research
tags: [wifi, 802.11, wireless-security, WPA2, WPA3, deauth]
category: Wireless Protocols
parent: "[[README]]"
status: comprehensive
---

# WiFi (802.11) Protocol Security Research

## Overview

WiFi (802.11) is the most widely deployed wireless networking technology, operating in the 2.4 GHz and 5/6 GHz ISM bands. This research covers comprehensive security analysis of all 802.11 variants from legacy 802.11b through modern WiFi 6E (802.11ax) and WiFi 7 (802.11be).

> **📚 For complete protocol breakdown**: See protocol overview documents:
>
> **[[WiFi/01-protocol-overview|WiFi Protocol Overview (Practical Focus)]]**
> - Complete 802.11 MAC + PHY layer breakdown
> - OFDM modulation, CSMA/CA, frame types
> - WPA2 4-way handshake deep dive
> - Raspberry Pi 5 hardware guidance
> - Research implementation roadmap
>
> **[[WiFi/02-protocol-overview|WiFi Protocol Overview (Reference Focus)]]**
> - Cross-protocol comparison table (WiFi vs BLE vs Zigbee vs LoRa)
> - Frame type quick reference cheat sheet
> - Comprehensive attack surface analysis

## Attack Categories

### [[WiFi/DoS/README|Denial of Service]]
Deauthentication attacks, disassociation attacks, beacon flooding, channel saturation

### [[WiFi/MITM/README|Man-in-the-Middle]]
Evil Twin attacks, rogue AP deployment, Karma attacks, captive portal bypass

### [[WiFi/Injection/README|Injection Attacks]]
Packet injection, frame manipulation, ARP poisoning, DNS spoofing

### [[WiFi/Sniffing/README|Sniffing & Reconnaissance]]
Monitor mode capture, handshake capture, client probing, traffic analysis

### [[WiFi/Scripting/README|Scripting & Packet Crafting]]
Scapy packet crafting, custom frame generation, attack automation, tool integration

## Directory Structure

```
WiFi/
├── README.md (this file - navigation hub)
├── 01-protocol-overview.md (practical research focus)
├── 02-protocol-overview.md (comparison & reference)
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

**Related**: [[README|Home]] • [[INDEX|Index]] • [[Bluetooth/README|Bluetooth]] • [[Zigbee/README|Zigbee]] • [[LoRa/README|LoRa]]

**Status**: User-managed - User will populate detailed attack documentation
