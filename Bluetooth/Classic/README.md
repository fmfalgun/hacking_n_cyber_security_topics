---
title: Bluetooth Classic (BR/EDR) Security Research
tags: [bluetooth-classic, BR/EDR, A2DP, RFCOMM, SPP, wireless-security]
category: Wireless Protocols
parent: "[[Bluetooth/README]]"
status: planned
---

# Bluetooth Classic (BR/EDR) Security Research

## Overview

Bluetooth Classic, also known as **BR/EDR** (Basic Rate/Enhanced Data Rate), is the original Bluetooth technology designed for continuous wireless connections with higher data rates. It's used in audio streaming, file transfer, serial communication, and device pairing.

> **Status**: 📋 Planned - Will begin after WiFi research completion

## Protocol Stack

```
┌─────────────────────────────────────────┐
│       Application Profiles              │ ← A2DP, HFP, SPP, OBEX, etc.
├─────────────────────────────────────────┤
│       RFCOMM (Serial Emulation)         │ ← Serial port emulation
├─────────────────────────────────────────┤
│       SDP (Service Discovery)           │ ← Service enumeration
├─────────────────────────────────────────┤
│       L2CAP (Logical Link Control)      │ ← Multiplexing, segmentation
├─────────────────────────────────────────┤
│       HCI (Host Controller Interface)   │ ← Commands/Events/Data
├─────────────────────────────────────────┤
│       Link Manager Protocol (LMP)       │ ← Link setup, authentication
├─────────────────────────────────────────┤
│       Baseband (Link Controller)        │ ← Packet formatting, timing
├─────────────────────────────────────────┤
│       Physical Layer (Radio)            │ ← 2.4 GHz, FHSS, 79 channels
└─────────────────────────────────────────┘
```

## Key Differences from BLE

| Feature | Bluetooth Classic | BLE |
|---------|------------------|-----|
| **Data Rate** | 1-3 Mbps | 1-2 Mbps |
| **Power** | High | Ultra-low |
| **Channels** | 79 (1 MHz each) | 40 (2 MHz each) |
| **Hopping** | Adaptive FHSS | Fixed hopping |
| **Discovery** | Inquiry/Page | Advertising |
| **Services** | SDP | GATT |
| **Serial** | RFCOMM | Custom GATT characteristics |
| **Audio** | Native A2DP/HFP | Custom audio profiles |

## Attack Surface

### 1. Pairing & Authentication
- **PIN Cracking**: Brute-force 4-digit PINs (legacy pairing)
- **SSP Downgrade**: Force Secure Simple Pairing downgrade
- **MITM Attacks**: Intercept pairing process
- **KNOB Attack**: Key Negotiation of Bluetooth (CVE-2019-9506)
- **BIAS Attack**: Bluetooth Impersonation AttackS (CVE-2020-10135)

### 2. Profile Exploitation
- **A2DP**: Audio stream injection/capture
- **HFP**: Hands-Free Profile command injection
- **SPP**: Serial Port Profile hijacking
- **OBEX**: Object Exchange Protocol file manipulation
- **PAN**: Personal Area Network attacks

### 3. Protocol Vulnerabilities
- **BlueBorne** (CVE-2017-1000251): RCE via L2CAP
- **BleedingBit**: Chip-level vulnerabilities (TI CC2640, CC2650)
- **SweynTooth**: BLE/Classic firmware bugs
- **L2CAP Fuzzing**: Malformed packets causing crashes

### 4. Service Discovery
- **SDP Enumeration**: Enumerate all services
- **Hidden Services**: Discover non-advertised services with Redfang
- **Service Fingerprinting**: Identify device types

## Directory Structure

```
Bluetooth/Classic/
├── README.md (this file)
├── 01-protocol-overview.md (coming soon)
├── DoS/
│   ├── README.md
│   ├── 01-dos-attack-theory.md (planned)
│   ├── 02-dos-implementation-guide.md (planned)
│   └── 03-dos-attack-cheatsheet.md (planned)
├── MITM/
│   └── README.md
├── Injection/
│   └── README.md
├── Sniffing/
│   └── README.md
└── Scripting/
    └── README.md
```

## Planned Content

### Protocol Overview
- [ ] Complete BR/EDR stack breakdown
- [ ] Packet structures (ACL, SCO, eSCO)
- [ ] Link Manager Protocol (LMP) details
- [ ] Baseband and timing
- [ ] Service Discovery Protocol (SDP)
- [ ] RFCOMM virtual serial ports
- [ ] Profile specifications (A2DP, HFP, SPP, OBEX)

### Attack Categories

#### DoS Attacks
[[Bluetooth/Classic/DoS/README|DoS Overview]] (coming soon)
- L2CAP connection flooding
- SDP query flooding
- RFCOMM channel exhaustion
- Baseband packet flooding
- Adaptive frequency hopping interference

#### MITM Attacks
[[Bluetooth/Classic/MITM/README|MITM Overview]] (coming soon)
- Legacy pairing interception (PIN sniffing)
- SSP downgrade attacks
- KNOB attack implementation
- BIAS attack (impersonation without pairing)
- Audio stream hijacking (A2DP MITM)

#### Injection Attacks
[[Bluetooth/Classic/Injection/README|Injection Overview]] (coming soon)
- RFCOMM command injection
- A2DP audio injection
- HFP AT command injection
- OBEX object injection
- L2CAP fuzzing

#### Sniffing & Reconnaissance
[[Bluetooth/Classic/Sniffing/README|Sniffing Overview]] (coming soon)
- Device discovery (inquiry scan)
- Service enumeration (SDP)
- Audio stream capture (A2DP)
- RFCOMM serial traffic monitoring
- Device fingerprinting

## Hardware Requirements

| Device | Purpose | Cost | Notes |
|--------|---------|------|-------|
| **Ubertooth One** | Sniffing BR/EDR + BLE | ~$120 | Best for research |
| **CSR8510 Dongle** | Attacks, cheap testing | ~$5 | Budget option |
| **Intel AX200/201** | Modern Bluetooth 5.x target | ~$20 | Testing target |
| **ESP32** | Low-cost attack platform | ~$5 | Arduino compatible |
| **Linux Laptop** | BlueZ stack | N/A | Required |

## Software Tools

### Discovery & Enumeration
- **hcitool**: Device discovery (`hcitool scan`)
- **sdptool**: Service discovery (`sdptool browse`)
- **btscanner**: GUI-based scanner
- **Bluelog**: Device logger
- **Redfang**: Hidden device discovery

### Attack Tools
- **Bluebugger**: BlueBug attack
- **BlueSnarf**: Phone book/calendar theft
- **CarWhisperer**: A2DP audio injection
- **btlejack**: Connection hijacking (also works for Classic)
- **Scapy**: Packet crafting (Bluetooth support)

### Analysis Tools
- **Wireshark**: Protocol analysis (BTHCI plugin)
- **btmon**: HCI monitor (BlueZ)
- **Frontline Bluetooth Sniffer**: Commercial sniffer (expensive)

## Famous Attacks

### BlueBorne (2017)
- **CVE-2017-1000251**: Linux kernel RCE via L2CAP
- **CVE-2017-1000250**: Information leak
- **Impact**: Billions of devices affected
- **Vector**: No pairing required, proximity-based

### KNOB Attack (2019)
- **CVE-2019-9506**: Force 1-byte encryption key
- **Impact**: MITM on paired devices
- **Vector**: Key negotiation downgrade during pairing

### BIAS Attack (2020)
- **CVE-2020-10135**: Impersonate without pairing
- **Impact**: Bypass authentication
- **Vector**: Exploit role switch during connection

## Attack Implementation Priority

1. **Device Discovery & Enumeration** (Easy)
   - hcitool scan, sdptool browse
   - Service fingerprinting

2. **SDP DoS** (Medium)
   - Query flooding
   - Malformed requests

3. **Legacy Pairing PIN Sniffing** (Medium)
   - Requires Ubertooth
   - 4-digit PIN brute-force

4. **A2DP Audio Injection** (Medium-Hard)
   - CarWhisperer tool
   - Custom audio stream crafting

5. **BlueBorne Exploitation** (Hard)
   - Kernel exploit development
   - Requires vulnerable target

## Dataset Generation

Planned capture labels:
```yaml
protocol: "bluetooth_classic"
profile: "A2DP" | "SPP" | "HFP" | "OBEX"
attack_type: "dos" | "mitm" | "injection" | "sniffing"
attack_vector: "sdp_flood" | "pin_crack" | "audio_inject" | ...
duration_sec: 30
target_device: "CSR8510" | "Intel_AX200" | ...
success: true | false
```

## Learning Resources

### Official Specifications
- [Bluetooth Core Specification](https://www.bluetooth.com/specifications/specs/core-specification/) (v5.4)
- [A2DP Profile Specification](https://www.bluetooth.com/specifications/specs/a2dp-1-3-2/)
- [HFP Profile Specification](https://www.bluetooth.com/specifications/specs/hands-free-profile-1-8/)

### Research Papers
- BlueBorne: [Armis BlueBorne Technical White Paper](https://www.armis.com/blueborne/)
- KNOB: [ACM CCS 2019 Paper](https://knobattack.com/)
- BIAS: [IEEE S&P 2020 Paper](https://francozappa.github.io/about-bias/)

### Tools Documentation
- [BlueZ Documentation](http://www.bluez.org/)
- [Ubertooth Documentation](https://github.com/greatscottgadgets/ubertooth/wiki)

## Ethical Guidelines

- ✅ Test only on owned devices
- ✅ Isolated lab environment
- ✅ Responsible disclosure for new vulnerabilities
- ❌ **Never** target medical devices (hearing aids, insulin pumps)
- ❌ **Never** attack vehicles (car audio systems)
- ❌ **Never** intercept audio without consent

---

**Related**:
- [[Bluetooth/README|Bluetooth Home]]
- [[Bluetooth/BLE/README|BLE Research]] (active)
- [[README|Main Hub]]
- [[INDEX|Complete Index]]

**Status**: Planned for post-WiFi research phase
