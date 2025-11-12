---
title: LoRa/LoRaWAN Protocol Security Research
tags: [LoRa, LoRaWAN, IoT, LPWAN, long-range]
category: Wireless Protocols
parent: "[[README]]"
status: planned
---

# LoRa/LoRaWAN Protocol Security Research

## Overview

**LoRa** (Long Range) is a low-power wide-area network (LPWAN) protocol designed for long-range communication (up to 15km) with minimal power consumption. It's widely used in IoT applications like smart cities, agriculture, asset tracking, and industrial monitoring.

> **Status**: 📋 Planned - Will begin after Zigbee research completion

## LoRa vs LoRaWAN

| Aspect | LoRa | LoRaWAN |
|--------|------|---------|
| **Layer** | Physical layer (PHY) | MAC layer protocol |
| **Function** | Modulation technique (CSS) | Network architecture & protocol |
| **Scope** | Radio communication | End-to-end communication |
| **Security** | None (physical modulation) | AES-128 encryption, authentication |

## Protocol Stack

```
┌─────────────────────────────────────────┐
│       Application Layer                 │ ← User applications
├─────────────────────────────────────────┤
│       LoRaWAN MAC Layer                 │ ← Network management, encryption
│  ┌───────────────────────────────────┐  │
│  │ Class A/B/C devices               │  │
│  │ Join procedure (OTAA/ABP)         │  │
│  │ Uplink/Downlink scheduling        │  │
│  └───────────────────────────────────┘  │
├─────────────────────────────────────────┤
│       LoRa Physical Layer (PHY)         │ ← Chirp Spread Spectrum modulation
│  ┌───────────────────────────────────┐  │
│  │ Frequency: 433/868/915 MHz        │  │
│  │ Bandwidth: 125/250/500 kHz        │  │
│  │ Spreading Factor: SF7-SF12        │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘

Network Architecture:
End Device ←→ Gateway ←→ Network Server ←→ Application Server
```

## Key Features

### LoRa Physical Layer
- **Modulation**: Chirp Spread Spectrum (CSS)
- **Frequency Bands**: ISM bands (433 MHz, 868 MHz EU, 915 MHz US)
- **Range**: Up to 15 km (rural), 2-5 km (urban)
- **Data Rate**: 0.3 - 50 kbps
- **Power Consumption**: Ultra-low (years on battery)

### LoRaWAN MAC Layer
- **Device Classes**: Class A (lowest power), Class B (scheduled downlink), Class C (continuous listening)
- **Activation**: OTAA (Over-The-Air Activation) or ABP (Activation By Personalization)
- **Security**: AES-128 encryption at network and application layers
- **Adaptive Data Rate (ADR)**: Dynamic SF adjustment

## Attack Surface

### 1. Physical Layer Attacks
- **Jamming**: Flood LoRa channels with noise
- **Replay Attacks**: Capture and replay uplink messages
- **Collision Attacks**: Interfere with packet reception at gateway
- **Eavesdropping**: Passive signal capture (if encryption weak/absent)

### 2. MAC Layer Attacks
- **Join Request Flooding**: Exhaust gateway resources during OTAA
- **Frame Counter Manipulation**: Exploit weak frame counter validation
- **ACK Spoofing**: Send fake acknowledgments
- **Downlink Injection**: Inject malicious downlink commands (requires key)

### 3. Network Attacks
- **Gateway Spoofing**: Deploy rogue gateways
- **Wormhole Attacks**: Relay packets between distant locations
- **Selective Forwarding**: Malicious gateway drops specific packets
- **Bit Flipping**: Modify encrypted payload (if MIC not properly checked)

### 4. Cryptographic Attacks
- **Key Extraction**: Extract keys from devices (hardware attacks)
- **ABP Key Reuse**: Exploit static keys in ABP mode
- **MIC Bruteforce**: Attempt to forge Message Integrity Code
- **Nonce Reuse**: Exploit poor random number generation

## Directory Structure

```
LoRa/
├── README.md (this file)
├── 01-protocol-overview.md (planned)
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

## Hardware Requirements

| Device | Purpose | Cost | Notes |
|--------|---------|------|-------|
| **LimeSDR Mini** | LoRa TX/RX, analysis | ~$150 | Full control |
| **HackRF One** | LoRa sniffing, jamming | ~$300 | Wideband SDR |
| **RTL-SDR** | Passive LoRa reception | ~$25 | Budget option |
| **LoRa32 (ESP32)** | LoRa dev board | ~$15 | Attack platform |
| **SX1276/78 Module** | LoRa transceiver | ~$5 | DIY projects |
| **Raspberry Pi** | Gateway emulation | ~$60 | With LoRa HAT |

## Software Stack

### Analysis Tools
- **GNU Radio**: SDR signal processing
- **LoRa Decoders**: gr-lora, gr-lorawan
- **Wireshark**: LoRaWAN packet analysis (with plugin)
- **ChirpStack**: Open-source LoRaWAN Network Server

### Attack Tools
- **LoRaWAN-attack-tools**: Research toolkit
- **lorawan-parser**: Packet parser
- **LoRa-SDR**: GNU Radio implementation
- **gr-lora**: GNU Radio LoRa decoder

### Development
- **Arduino LoRa Library**: LoRa32, ESP32
- **LMIC (LoRaWAN in C)**: LoRaWAN stack
- **PyLoRa**: Python LoRa library

## Attack Categories

### DoS Attacks
[[LoRa/DoS/README|DoS Overview]]
- Jamming (continuous noise on LoRa channels)
- Join request flooding (OTAA exhaustion)
- Gateway resource exhaustion
- Collision attacks (packet interference)

### MITM Attacks
[[LoRa/MITM/README|MITM Overview]]
- Rogue gateway deployment
- Downlink injection (if keys compromised)
- Join accept manipulation
- Wormhole attacks

### Injection Attacks
[[LoRa/Injection/README|Injection Overview]]
- Malicious uplink injection
- Downlink command injection
- MAC command injection
- Malformed packet fuzzing

### Sniffing & Reconnaissance
[[LoRa/Sniffing/README|Sniffing Overview]]
- Passive packet capture with SDR
- DevAddr enumeration
- Gateway discovery
- Traffic pattern analysis

## LoRaWAN Security

### Encryption Keys
- **AppSKey**: Application Session Key (end-to-end encryption)
- **NwkSKey**: Network Session Key (MIC, network-level encryption)
- **AppKey**: Application Key (join procedure, OTAA only)

### Vulnerabilities
- **ABP Mode**: Static keys (no perfect forward secrecy)
- **Frame Counter**: Potential rollover attacks if not validated
- **No Downlink Authentication**: Limited downlink slots
- **Gateway Security**: Gateways often unprotected

## Research Focus Areas

1. **Physical Layer Analysis**
   - LoRa modulation (CSS) reverse engineering
   - Spreading factor optimization for jamming
   - Collision attack effectiveness

2. **OTAA Security**
   - Join request flooding DoS
   - Join accept replay
   - Nonce analysis

3. **ABP Exploitation**
   - Static key extraction
   - Frame counter manipulation
   - Session hijacking

4. **Gateway Attacks**
   - Rogue gateway deployment
   - Selective forwarding
   - GPS spoofing (for Class B)

## Dataset Generation

Planned capture labels:
```yaml
protocol: "LoRaWAN"
frequency_mhz: 868 | 915 | 433
spreading_factor: 7-12
bandwidth_khz: 125 | 250 | 500
device_class: "A" | "B" | "C"
activation: "OTAA" | "ABP"
attack_type: "dos" | "mitm" | "injection" | "sniffing"
attack_vector: "jamming" | "join_flood" | "rogue_gw" | ...
duration_sec: 30
success: true | false
```

## Learning Resources

### Official Specifications
- [LoRa Alliance](https://lora-alliance.org/)
- [LoRaWAN 1.0.3 Specification](https://lora-alliance.org/resource_hub/lorawan-specification-v1-0-3/)
- [LoRaWAN 1.1 Specification](https://lora-alliance.org/resource_hub/lorawan-specification-v1-1/)

### Research Papers
- "Security Vulnerabilities in LoRaWAN" (IEEE)
- "LoRaWAN Security: A Survey" (ACM)
- "LoRa Physical Layer Attacks" (various conferences)

### Open Source Projects
- [ChirpStack](https://www.chirpstack.io/) - LoRaWAN Network Server
- [The Things Network](https://www.thethingsnetwork.org/) - Community network
- [gr-lora](https://github.com/rpp0/gr-lora) - GNU Radio LoRa decoder

## Ethical Guidelines

- ✅ Test only on owned devices and private gateways
- ✅ Isolated test environment (own LoRaWAN network)
- ✅ Use ISM band legally (respect regional regulations)
- ❌ **Never** jam public LoRaWAN networks
- ❌ **Never** attack critical infrastructure (smart grids, water systems)
- ❌ **Never** interfere with emergency services

---

**Related**:
- [[README|Home]]
- [[INDEX|Complete Index]]
- [[Bluetooth/README|Bluetooth]]
- [[WiFi/README|WiFi]]
- [[Zigbee/README|Zigbee]]

**Status**: Planned for post-Zigbee research phase
