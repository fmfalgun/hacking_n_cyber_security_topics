---
title: Bluetooth Protocol Security Research
tags: [bluetooth, bluetooth-classic, BLE, wireless-security, protocol-analysis]
category: Wireless Protocols
parent: "[[README]]"
status: active
---

# Bluetooth Protocol Security Research

## Overview

This directory contains comprehensive security research on **both Bluetooth Classic (BR/EDR)** and **Bluetooth Low Energy (BLE)** protocols. These are two distinct protocol stacks with different architectures, use cases, and attack surfaces.

## Protocol Variants

### Bluetooth Classic (BR/EDR)
**Status**: 📋 Planned | **Start**: After WiFi completion

Classic Bluetooth (Basic Rate/Enhanced Data Rate) for higher-bandwidth applications like audio streaming, file transfer, and serial communication.

[[Bluetooth/Classic/README|→ Bluetooth Classic Research]]

**Key Features**:
- Higher data rates (1-3 Mbps)
- Longer range (up to 100m Class 1)
- Audio streaming (A2DP, HFP)
- File transfer (OBEX, FTP)
- Serial communication (SPP, RFCOMM)

**Attack Surface**:
- BlueBorne vulnerabilities
- Pairing attacks (PIN cracking, MITM)
- Audio injection/sniffing
- RFCOMM exploitation
- SDP service discovery abuse

---

### Bluetooth Low Energy (BLE)
**Status**: ✅ Active Research | **Phase**: DoS Attack Implementation

BLE for ultra-low power IoT devices, wearables, beacons, and smart home applications.

[[Bluetooth/BLE/README|→ BLE Research Hub]]

**Key Features**:
- Ultra-low power consumption
- Lower data rates (1-2 Mbps)
- Optimized for small data transfers
- GATT-based services
- Advertising and connection modes

**Current Progress**:
- ✅ Complete protocol documentation (7 layers, 230KB)
- ✅ 25+ DoS attack vectors analyzed
- ✅ Python & C++ packet crafting guides
- 🔄 Attack implementation scripts (in progress)

---

## Comparison: Classic vs BLE

| Aspect | Bluetooth Classic (BR/EDR) | Bluetooth Low Energy (BLE) |
|--------|---------------------------|----------------------------|
| **Power Consumption** | High | Ultra-low |
| **Data Rate** | 1-3 Mbps | 1-2 Mbps |
| **Range** | 10-100m | 10-50m |
| **Topology** | Point-to-point, piconet | Star, mesh (BLE 5+) |
| **Primary Use Cases** | Audio, file transfer, serial | IoT, wearables, beacons |
| **Pairing** | PIN/passkey (legacy/SSP) | SMP with multiple methods |
| **Protocol Stack** | L2CAP → RFCOMM → profiles | L2CAP → ATT → GATT |
| **Discovery** | Inquiry scan | Advertising |
| **Attack Complexity** | Medium-High | Medium |
| **Research Status** | Planned | ✅ Active |

---

## Directory Structure

```
Bluetooth/
├── README.md (this file)
├── Classic/
│   ├── README.md
│   ├── 01-protocol-overview.md (planned)
│   ├── DoS/
│   ├── MITM/
│   ├── Injection/
│   ├── Sniffing/
│   └── Scripting/
└── BLE/
    ├── README.md
    ├── 01-protocol-overview.md ✅
    ├── DoS/ ✅
    ├── MITM/ ✅
    ├── Injection/ ✅
    ├── Sniffing/ ✅
    └── Scripting/ ✅
```

---

## Research Objectives

### Bluetooth Classic Research (Upcoming)
1. **Protocol Analysis**: Complete BR/EDR stack breakdown
2. **Attack Implementation**: BlueBorne, pairing attacks, audio MITM
3. **Profile Exploitation**: A2DP, SPP, OBEX, HFP vulnerabilities
4. **Dataset Generation**: Capture labeled Classic Bluetooth attack traffic

### BLE Research (Current)
1. ✅ Protocol understanding (PHY → Application layers)
2. ✅ Attack vector identification (25+ DoS attacks)
3. 🔄 Attack implementation (Python/C++ scripts)
4. 📋 Traffic capture and ML dataset generation

---

## Hardware Requirements

### For Bluetooth Classic
| Device | Purpose | Cost | Status |
|--------|---------|------|--------|
| **Ubertooth One** | Classic + BLE sniffing | ~$120 | Recommended |
| **CSR8510 Dongle** | Classic attacks, cheap | ~$5 | Budget option |
| **Intel AX200** | Modern Bluetooth 5.2 | ~$20 | Testing target |
| **Linux Laptop** | BlueZ stack, development | N/A | Required |

### For BLE
| Device | Purpose | Cost | Status |
|--------|---------|------|--------|
| **Ubertooth One** | BLE sniffing, injection | ~$120 | Recommended |
| **nRF52840 Dongle** | BLE peripheral/central | ~$10 | Recommended |
| **Raspberry Pi 5** | Attack platform | ~$60 | Optional |
| **Linux Laptop** | BlueZ, development | N/A | Required |

---

## Software Stack

### Bluetooth Classic Tools
- **BlueZ**: Linux Bluetooth stack (hciconfig, hcitool, sdptool)
- **Wireshark**: Protocol analysis with BTHCI plugin
- **btscanner**: Device discovery and service enumeration
- **Bluelog**: Bluetooth device logger
- **Redfang**: Hidden Bluetooth device finder
- **Bluebugger**: BlueBug attack implementation

### BLE Tools (Already Set Up)
- **BlueZ**: Linux BLE stack (hcitool lescan, gatttool)
- **Wireshark**: BLE packet analysis
- **btmon**: HCI traffic monitoring
- **Scapy**: Packet crafting
- **Custom Scripts**: Python/C++ attack tools

---

## Attack Categories

### Classic Bluetooth Attacks (Planned)
- **DoS**: Connection flooding, L2CAP crashes, SDP abuse
- **MITM**: Pairing interception, SSP downgrade, audio hijacking
- **Injection**: RFCOMM injection, A2DP audio injection
- **Sniffing**: Audio capture, file transfer monitoring, device tracking
- **Exploitation**: BlueBorne (CVE-2017-1000251), KNOB attack

### BLE Attacks (Active Research)
- **DoS**: Advertising flood, ATT write flood, L2CAP param storms ✅
- **MITM**: Pairing interception, connection hijacking 🔄
- **Injection**: Malformed PDUs, fuzzing, protocol violations ✅
- **Sniffing**: Advertisement capture, GATT enumeration, traffic analysis ✅
- **Scripting**: Python/C++ packet crafting frameworks ✅

---

## Learning Path

### Start with BLE (Recommended)
1. [[Bluetooth/BLE/01-protocol-overview|BLE Protocol Overview]]
2. [[Bluetooth/BLE/DoS/README|BLE DoS Attacks]]
3. [[Bluetooth/BLE/Scripting/01-packet-crafting-basics|BLE Packet Crafting]]

### Then Move to Classic (After WiFi)
4. [[Bluetooth/Classic/01-protocol-overview|Classic Protocol Overview]] (coming soon)
5. [[Bluetooth/Classic/DoS/README|Classic DoS Attacks]] (coming soon)
6. [[Bluetooth/Classic/Scripting/README|Classic Exploitation Scripts]] (coming soon)

---

## Key Differences in Attack Approaches

### Bluetooth Classic
- **Pairing**: PIN/passkey cracking, SSP MITM
- **Audio**: A2DP stream injection/capture
- **Serial**: RFCOMM channel hijacking
- **Services**: SDP enumeration and abuse
- **Complexity**: Requires understanding of profiles (A2DP, SPP, etc.)

### BLE
- **Pairing**: SMP attacks, ECDH exploitation
- **Data**: GATT characteristic flooding
- **Discovery**: Advertising manipulation
- **Services**: GATT service enumeration
- **Complexity**: Layered protocol stack (LL → L2CAP → ATT → GATT)

---

## Ethical Guidelines

- ✅ Test only on devices you own
- ✅ Isolated test environment (no public interference)
- ✅ Document all findings for defensive research
- ❌ Never target medical devices (pacemakers, insulin pumps)
- ❌ Never attack vehicles or safety-critical systems
- ❌ Never deploy attacks on public infrastructure

---

**Related**:
- [[README|Home]]
- [[INDEX|Complete Index]]
- [[Bluetooth/BLE/README|BLE Research]]
- [[Bluetooth/Classic/README|Classic Research]]
- [[WiFi/README|WiFi]]
- [[Zigbee/README|Zigbee]]
- [[LoRa/README|LoRa]]

**Status**: BLE active research, Classic planned for post-WiFi phase
