---
title: WiFi (802.11) Protocol Security Research
tags: [wifi, 802.11, wireless-security, WPA2, WPA3, deauth]
category: Wireless Protocols
parent: "[[README]]"
status: user-managed
---

# WiFi (802.11) Protocol Security Research

## Overview

WiFi (802.11) is the most widely deployed wireless networking technology, operating in the 2.4 GHz and 5/6 GHz ISM bands. This research covers comprehensive security analysis of all 802.11 variants from legacy 802.11b through modern WiFi 6E (802.11ax) and WiFi 7 (802.11be).

> **Status**: ✅ User Managed - User will populate with their own research

## Protocol Variants

| Standard | Year | Band | Max Rate | Key Features |
|----------|------|------|----------|--------------|
| **802.11b** | 1999 | 2.4 GHz | 11 Mbps | Legacy, DSSS modulation |
| **802.11g** | 2003 | 2.4 GHz | 54 Mbps | OFDM modulation |
| **802.11a** | 1999 | 5 GHz | 54 Mbps | Less interference, shorter range |
| **802.11n** (WiFi 4) | 2009 | 2.4/5 GHz | 600 Mbps | MIMO, channel bonding |
| **802.11ac** (WiFi 5) | 2013 | 5 GHz | 6.9 Gbps | MU-MIMO, 160 MHz channels |
| **802.11ax** (WiFi 6/6E) | 2019 | 2.4/5/6 GHz | 9.6 Gbps | OFDMA, BSS coloring, 6 GHz |
| **802.11be** (WiFi 7) | 2024 | 2.4/5/6 GHz | 46 Gbps | 320 MHz, 4K-QAM, MLO |

## Protocol Stack

```
┌─────────────────────────────────────────┐
│       Application Layer                 │ ← HTTP, DNS, etc.
├─────────────────────────────────────────┤
│       Transport Layer (TCP/UDP)         │ ← End-to-end communication
├─────────────────────────────────────────┤
│       Network Layer (IP)                │ ← Routing, addressing
├─────────────────────────────────────────┤
│       LLC (Logical Link Control)        │ ← 802.2 framing
├─────────────────────────────────────────┤
│       MAC Layer (802.11)                │ ← CSMA/CA, frame types
│  ┌───────────────────────────────────┐  │
│  │ Management Frames                 │  │ ← Beacon, Probe, Auth, Assoc
│  │ Control Frames                    │  │ ← RTS, CTS, ACK
│  │ Data Frames                       │  │ ← Payload transmission
│  └───────────────────────────────────┘  │
├─────────────────────────────────────────┤
│       Physical Layer (PHY)              │ ← DSSS, OFDM, OFDMA modulation
│  ┌───────────────────────────────────┐  │
│  │ 2.4 GHz: Channels 1-14            │  │
│  │ 5 GHz: Channels 36-165            │  │
│  │ 6 GHz: Channels 1-233 (WiFi 6E)   │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Directory Structure

```
WiFi/
├── README.md (this file)
├── 01-protocol-overview.md (user-managed)
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

## Security Mechanisms

### WPA/WPA2/WPA3 Evolution

| Protocol | Year | Encryption | Key Exchange | Vulnerabilities |
|----------|------|------------|--------------|-----------------|
| **WEP** | 1999 | RC4 (40/104-bit) | Static key | Completely broken (FMS, PTW attacks) |
| **WPA** | 2003 | TKIP (RC4) | PSK/802.1X | TKIP deprecated, Michael MIC weak |
| **WPA2** | 2004 | AES-CCMP (128-bit) | 4-way handshake | KRACK, downgrade attacks |
| **WPA3** | 2018 | AES-CCMP/GCMP-256 | SAE (Dragonfly) | Dragonblood, timing attacks |

## Attack Categories

### [[WiFi/DoS/README|Denial of Service]]
- Deauthentication attacks
- Disassociation attacks
- Beacon flooding
- Channel saturation

### [[WiFi/MITM/README|Man-in-the-Middle]]
- Evil Twin attacks
- Rogue AP deployment
- Karma attacks
- Captive portal bypass

### [[WiFi/Injection/README|Injection Attacks]]
- Packet injection
- Frame manipulation
- ARP poisoning
- DNS spoofing

### [[WiFi/Sniffing/README|Sniffing & Reconnaissance]]
- Monitor mode capture
- Handshake capture
- Client probing
- Traffic analysis

### [[WiFi/Scripting/README|Scripting & Packet Crafting]]
- Scapy packet crafting
- Custom frame generation
- Attack automation
- Tool integration

## Hardware Requirements

| Device | Purpose | Cost | Notes |
|--------|---------|------|-------|
| **Alfa AWUS036ACH** | Monitor mode, injection | ~$50 | Dual-band, Realtek RTL8812AU |
| **Alfa AWUS036NHA** | 2.4 GHz attacks | ~$40 | Atheros AR9271, best compatibility |
| **TP-Link TL-WN722N v1** | Budget option | ~$15 | Atheros AR9271 (v1 only!) |
| **WiFi Pineapple** | Automated attacks, MITM | ~$100-200 | Hak5, turnkey solution |
| **Intel AX200/201** | WiFi 6 testing target | ~$20 | Test modern protocols |

## Software Stack

### Core Tools
- **Aircrack-ng Suite**: airmon-ng, airodump-ng, aireplay-ng, aircrack-ng
- **Wireshark**: Packet analysis with 802.11 dissectors
- **Scapy**: Python packet crafting
- **Bettercap**: Modern MITM framework
- **Hashcat**: GPU-accelerated password cracking
- **Hostapd**: Software Access Point

### Attack Tools
- **Wifite**: Automated WPA/WEP cracking
- **Mdk4**: Advanced DoS toolkit
- **Hostapd-wpe**: Evil Twin with credential capture
- **hcxdumptool/hcxtools**: PMKID attack
- **Kismet**: Wireless IDS/IPS

## Key Attack Vectors

### 1. Deauthentication Attack
Force client disconnect by sending spoofed deauth frames

### 2. WPA2 Handshake Capture
Capture 4-way handshake for offline dictionary attack

### 3. PMKID Attack
Extract PMKID from first EAPOL frame (no client needed)

### 4. Evil Twin
Create rogue AP to capture credentials

### 5. KRACK (Key Reinstallation)
CVE-2017-13077 - Replay attacks on WPA2

### 6. Dragonblood (WPA3)
Side-channel attacks on SAE handshake

## Dataset Generation

```yaml
protocol: "802.11"
standard: "802.11n" | "802.11ac" | "802.11ax"
band: "2.4GHz" | "5GHz" | "6GHz"
channel: 1-233
security: "Open" | "WEP" | "WPA2-PSK" | "WPA3-SAE"
attack_type: "dos" | "mitm" | "injection" | "sniffing"
attack_vector: "deauth" | "evil_twin" | "handshake_capture"
duration_sec: 30
success: true | false
```

## Ethical Guidelines

- ✅ Test only on owned networks
- ✅ Obtain written permission for penetration tests
- ✅ Isolated test environment
- ❌ **Never** attack public WiFi networks
- ❌ **Never** interfere with critical infrastructure

---

**Related**: [[README|Home]] • [[INDEX|Index]] • [[Bluetooth/README|Bluetooth]] • [[Zigbee/README|Zigbee]] • [[LoRa/README|LoRa]]

**Status**: User-managed - User will populate detailed attack documentation
