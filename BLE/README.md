---
title: Bluetooth Low Energy (BLE) Security Research
tags: [BLE, bluetooth, wireless-security, protocol-analysis]
category: Wireless Protocols
parent: "[[README]]"
status: active
---

# Bluetooth Low Energy (BLE) Security Research

## Overview

This directory contains comprehensive research on Bluetooth Low Energy (BLE) protocol security, attack implementation, and defensive analysis. The goal is to understand BLE vulnerabilities through hands-on implementation and generate labeled datasets for machine learning-based intrusion detection.

## Research Objectives

1. **Protocol Understanding**: Deep dive into BLE stack (PHY → LL → L2CAP → ATT/GATT/SMP)
2. **Attack Implementation**: Practical implementation of 25+ attack vectors
3. **Dataset Generation**: Capture labeled traffic for ML model training
4. **Defensive Insights**: Identify vulnerabilities and mitigation strategies

## Directory Structure

### Core Documentation

- [[BLE/01-protocol-overview|01. BLE Protocol Overview]] - Complete protocol stack breakdown with all layers

### Attack Categories

#### Denial of Service (DoS)
- [[BLE/DoS/README|DoS Attacks Overview]]
  - [[BLE/DoS/01-dos-attack-theory|Attack Theory & Analysis]]
  - [[BLE/DoS/02-dos-implementation-guide|Implementation Guide]]
  - [[BLE/DoS/03-dos-attack-cheatsheet|Quick Reference Cheatsheet]]

#### Man-in-the-Middle (MITM)
- [[BLE/MITM/README|MITM Attacks Overview]]
  - Pairing interception
  - Connection hijacking
  - Data manipulation

#### Injection Attacks
- [[BLE/Injection/README|Injection Attacks Overview]]
  - Packet crafting
  - Protocol fuzzing
  - Malformed data injection

#### Sniffing & Reconnaissance
- [[BLE/Sniffing/README|Sniffing Overview]]
  - Passive monitoring
  - Service discovery
  - Traffic analysis

### Implementation & Scripting

- [[BLE/Scripting/README|Scripting & Packet Crafting]]
  - [[BLE/Scripting/01-packet-crafting-basics|Packet Crafting Basics (Python & C++)]]
  - HCI command implementation
  - Attack automation

## Hardware Requirements

| Device | Purpose | Cost | Status |
|--------|---------|------|--------|
| **Ubertooth One** | BLE sniffing, injection | ~$120 | Recommended |
| **nRF52840 Dongle** | BLE peripheral/central testing | ~$10 | Recommended |
| **Raspberry Pi 5** | Attack platform, capture server | ~$60 | Optional |
| **Linux Laptop** | Development, BlueZ tools | N/A | Required |

## Software Stack

- **BlueZ**: Linux Bluetooth stack with HCI tools
- **Wireshark**: Packet capture and analysis
- **btmon**: HCI traffic monitoring
- **Scapy**: Python packet crafting
- **Custom Scripts**: Attack implementation (Python/C++)

## Learning Path

### Beginner
1. Read [[BLE/01-protocol-overview|Protocol Overview]]
2. Understand advertising, connection, and data transfer phases
3. Run basic HCI commands (`hcitool`, `gatttool`)

### Intermediate
4. Study [[BLE/DoS/01-dos-attack-theory|DoS Attack Theory]]
5. Review [[BLE/Scripting/01-packet-crafting-basics|Packet Crafting Basics]]
6. Implement simple advertising flood

### Advanced
7. Implement multi-layer attacks (L2CAP, ATT, SMP)
8. Capture and label attack traffic
9. Analyze vendor-specific vulnerabilities

## Attack Surface Summary

| Layer | Attack Vectors | Complexity | Impact |
|-------|----------------|------------|--------|
| **Physical** | Jamming, RSSI tracking | High (requires SDR) | Medium |
| **Link Layer** | Adv flood, connection flood, retransmission | Medium | High |
| **L2CAP** | Parameter update storm, fragmentation | Medium | High |
| **ATT/GATT** | Write flood, read flood, notification storm | Low | High |
| **SMP** | Pairing spam, invalid crypto | Medium | Medium |

## Key Insights

- **No Authentication in Advertising**: Anyone can send ADV_IND packets
- **Write Without Response (0x52)**: Primary DoS vector (no flow control)
- **Connection Parameter Abuse**: Extreme values can cause crashes
- **Pairing Weaknesses**: "Just Works" mode vulnerable to MITM
- **Frequency Hopping**: Makes jamming harder but connection following possible

## Authorization & Ethics

**CRITICAL**: All attacks documented here are for:
- ✅ Authorized security testing on owned infrastructure
- ✅ Defensive research and vulnerability analysis
- ✅ Educational purposes in controlled environments
- ✅ ML dataset generation for intrusion detection

**NEVER** use these techniques on:
- ❌ Devices you do not own or have explicit permission to test
- ❌ Public infrastructure or commercial devices
- ❌ Medical devices or safety-critical systems

## Next Steps

- Complete BLE DoS implementation (in progress)
- Expand to [[WiFi/README|WiFi]] and [[Zigbee/README|Zigbee]] protocols
- Build [[Traffic-Capture/README|traffic capture pipeline]]
- Organize [[Dataset-Organization/README|labeled datasets]]
- Train [[Model-Training/README|ML detection models]]

---

**Related**: [[README|Home]] • [[INDEX|Full Index]] • [[Lab-Setup/README|Lab Setup]]

**Status**: Active research - DoS attacks implementation phase
