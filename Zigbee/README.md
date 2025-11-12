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

> **Status**: 📋 Comprehensive documentation for Q2 2025 research

## Protocol Stack

```
┌─────────────────────────────────────────┐
│   Application Layer (APL)               │ ← ZCL, ZDO
│  ┌───────────────────────────────────┐  │
│  │ Zigbee Cluster Library (ZCL)      │  │ ← On/Off, Level Control, etc.
│  │ Zigbee Device Object (ZDO)        │  │ ← Device/service discovery
│  │ Application Framework (AF)        │  │ ← Endpoints, profiles
│  └───────────────────────────────────┘  │
├─────────────────────────────────────────┤
│   Application Support Sublayer (APS)   │ ← Reliable transmission, binding
├─────────────────────────────────────────┤
│   Network Layer (NWK)                   │ ← Routing, mesh networking
│  ┌───────────────────────────────────┐  │
│  │ Routing: AODV-based              │  │
│  │ Network formation/joining        │  │
│  │ Address assignment (16-bit)      │  │
│  └───────────────────────────────────┘  │
├─────────────────────────────────────────┤
│   MAC Layer (802.15.4 MAC)              │ ← CSMA/CA, beacons, GTS
│  ┌───────────────────────────────────┐  │
│  │ Beacon frames                     │  │
│  │ Data frames                       │  │
│  │ Command frames                    │  │
│  │ Acknowledgment frames             │  │
│  └───────────────────────────────────┘  │
├─────────────────────────────────────────┤
│   Physical Layer (802.15.4 PHY)         │ ← O-QPSK, DSSS
│  ┌───────────────────────────────────┐  │
│  │ 2.4 GHz: Channels 11-26 (global)  │  │
│  │ 868 MHz: Channel 0 (EU)           │  │
│  │ 915 MHz: Channels 1-10 (US)       │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Key Specifications

| Aspect | Specification |
|--------|---------------|
| **Standard** | IEEE 802.15.4 (PHY/MAC), Zigbee Alliance (upper layers) |
| **Frequency** | 2.4 GHz (250 kbps), 915 MHz (40 kbps), 868 MHz (20 kbps) |
| **Range** | 10-100m (depends on power class) |
| **Topology** | Star, Tree, Mesh |
| **Max Nodes** | 65,536 per network (16-bit addressing) |
| **Security** | AES-128 encryption, authentication |
| **Power** | Ultra-low (years on battery for end devices) |

## Device Types

### 1. Coordinator (ZC)
- One per network
- Forms the network, assigns addresses
- Cannot sleep (always powered)
- **Attack Target**: Network-wide DoS, key extraction

### 2. Router (ZR)
- Routes packets in mesh
- Can have children
- Cannot sleep
- **Attack Target**: Routing manipulation, traffic interception

### 3. End Device (ZED)
- Leaf nodes (sensors, actuators)
- Can sleep (low power)
- Communicates only with parent
- **Attack Target**: Impersonation, replay

## Security Mechanisms

### Key Types

| Key | Purpose | Scope | Distribution |
|-----|---------|-------|--------------|
| **Master Key** | Derive link keys | Pre-configured | Out-of-band or install code |
| **Network Key** | Network-wide encryption | All devices | Encrypted during joining |
| **Link Key** | End-to-end security | Device pairs | Derived from master or CBKE |
| **Trust Center Link Key** | Secure join | Device ↔ Coordinator | Pre-configured or default |

### Security Levels

| Level | Encryption | Authentication | Use Case |
|-------|------------|----------------|----------|
| **0x00** | None | None | Legacy, insecure |
| **0x04** | None | MIC-32 | Auth only (deprecated) |
| **0x05** | AES-128-CCM | MIC-32 | Modern Zigbee standard |
| **0x06** | AES-128-CCM | MIC-64 | High security |
| **0x07** | AES-128-CCM | MIC-128 | Maximum security |

### Joining Process

```
End Device                           Coordinator (Trust Center)
     │                                       │
     │──── Beacon Request (broadcast) ──────→│
     │                                       │
     │◄──── Beacon Response ────────────────│
     │      (PAN ID, permit join)            │
     │                                       │
     │──── Association Request ─────────────→│
     │                                       │
     │◄──── Association Response ────────────│
     │      (16-bit short address assigned)  │
     │                                       │
     │──── Transport Key Request ───────────→│
     │      (encrypted with TCLK)            │
     │                                       │
     │◄──── Transport Network Key ───────────│
     │      (encrypted, network key)         │
     │                                       │
     │      [Device now part of network]     │
```

## Attack Surface

### 1. IEEE 802.15.4 MAC Layer Attacks
- **Channel Jamming**: RF interference on 2.4 GHz channels
- **ACK Spoofing**: Send fake acknowledgments
- **Beacon Flooding**: Overwhelm with beacon frames
- **PAN ID Conflict**: Create networks with duplicate PAN IDs

### 2. Network Layer Attacks
- **Routing Manipulation**: Malicious route advertisements
- **Sinkhole Attack**: Attract all traffic to attacker node
- **Selective Forwarding**: Drop specific packets
- **Wormhole Attack**: Tunnel packets between distant nodes

### 3. Key Management Attacks
- **Default Key Exploitation**: Many devices ship with "ZigBeeAlliance09"
- **Insecure Rejoin**: Some devices use default TCLK during rejoin
- **Key Transport Attack**: Intercept network key during joining
- **Touchlink Commissioning**: Proximity-based pairing vulnerabilities

### 4. Application Layer Attacks
- **Command Injection**: Send unauthorized ZCL commands
- **Replay Attacks**: Capture and replay commands (if no replay protection)
- **Firmware Exploitation**: OTA firmware update hijacking
- **Brute-Force Short Address**: 16-bit address space is small

### 5. Physical Attacks
- **Hardware Debugging**: Extract keys via JTAG/SWD
- **Side-Channel Analysis**: Power analysis to extract AES key
- **Flash Dump**: Read firmware for hardcoded keys

## Directory Structure

```
Zigbee/
├── README.md (this file)
├── 01-protocol-overview.md
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

## Hardware Requirements

| Device | Purpose | Cost | Notes |
|--------|---------|------|-------|
| **Atmel RZRAVEN USB** | Zigbee sniffer | ~$50 | Official, good compatibility |
| **ATUSB** | 802.15.4 sniffer/injector | ~$40 | Open-source, USB dongle |
| **Ubertooth One** | Zigbee sniffing (limited) | ~$120 | Better for BLE, some 802.15.4 support |
| **nRF52840 Dongle** | 802.15.4 capable | ~$10 | With custom firmware |
| **Zigbee2MQTT Gateway** | Testing target | ~$30 | CC2531 USB stick + software |
| **Philips Hue Bulbs** | Smart home target | ~$15/bulb | Real-world testing |
| **SDR (HackRF/LimeSDR)** | Jamming, signal analysis | ~$300 | Advanced attacks |

## Software Stack

### Sniffing & Analysis
- **KillerBee**: Python framework for 802.15.4/Zigbee attacks
  - `zbstumbler`: Network discovery
  - `zbreplay`: Replay captured packets
  - `zbdump`: Packet capture
  - `zbgoodfind`: Find valid encryption keys
- **Wireshark**: 802.15.4/Zigbee dissectors
- **Scapy**: Zigbee layers (`scapy.layers.zigbee`)
- **Zigdiggity**: Zigbee pentesting toolkit

### Development & Testing
- **Zigbee2MQTT**: Open-source Zigbee bridge
- **Z-Stack**: Texas Instruments Zigbee stack
- **ZBOSS**: Silicon Labs Zigbee stack
- **EmberZNet**: Zigbee PRO stack (Silicon Labs)

### Reverse Engineering
- **Ghidra/IDA Pro**: Firmware analysis
- **JLink**: JTAG debugging
- **OpenOCD**: On-chip debugging

## Attack Categories

### [[Zigbee/DoS/README|Denial of Service]]
- Channel jamming (2.4 GHz, 915 MHz, 868 MHz)
- Beacon flooding
- Association request flooding
- Coordinator resource exhaustion
- Routing table overflow

### [[Zigbee/MITM/README|Man-in-the-Middle]]
- Malicious coordinator (fake PAN)
- Router impersonation
- Key transport interception
- Touchlink commissioning MITM
- Insecure rejoin exploitation

### [[Zigbee/Injection/README|Injection Attacks]]
- ZCL command injection (On/Off, Level Control)
- Replay attacks (if no frame counter)
- Malicious firmware injection (OTA)
- Routing manipulation
- Network layer command injection

### [[Zigbee/Sniffing/README|Sniffing & Reconnaissance]]
- Network discovery (zbstumbler)
- Key extraction (default keys, hardware dumps)
- Traffic analysis (KillerBee, Wireshark)
- Device fingerprinting
- Topology mapping

### [[Zigbee/Scripting/README|Scripting & Packet Crafting]]
- KillerBee Python framework
- Scapy Zigbee layers
- Custom packet injection
- Automated attack scripts

## Key Attacks Deep Dive

### 1. Default Key Attack

**Vulnerability**: Many Zigbee devices use default Trust Center Link Key

**Default Keys**:
- `ZigBeeAlliance09` (hex: `5A 69 67 42 65 65 41 6C 6C 69 61 6E 63 65 30 39`)
- All-zeros: `00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00`

**Pseudocode**:
```python
# KillerBee required: pip install killerbee

from killerbee import KillerBee

def test_default_keys(channel, panid):
    """
    Libraries:
    - killerbee: Zigbee protocol implementation
    - scapy.layers.zigbee: Zigbee packet structures

    Why:
    - KillerBee: Purpose-built for Zigbee security testing
    - Provides decryption with known keys
    """

    default_keys = [
        bytes.fromhex("5A6967426565416C6C69616E636530339"),  # ZigBeeAlliance09
        bytes(16),  # All zeros
    ]

    kb = KillerBee(channel=channel)

    for key in default_keys:
        # Try to decrypt captured traffic
        # kb.set_key(key)
        pass
```

**Required Libraries**:
- **Python**: `killerbee`, `scapy`, `pycrypto` (AES decryption)
- **C++**: `<aes.h>` (from crypto library), `<zigbee.h>` (if available)

### 2. Touchlink Commissioning Attack

**Vulnerability**: Proximity-based pairing can be exploited with high-gain antenna

**Mechanism**:
1. Send "Factory Reset" command via Touchlink
2. Device leaves network
3. Commission device into attacker's network
4. Extract network key from target device

**Pseudocode**:
```python
# Touchlink factory reset pseudocode

from scapy.layers.zigbee import ZigbeeNWK, ZigbeeAppDataPayload

def touchlink_factory_reset(target_mac):
    """
    Libraries:
    - scapy.layers.zigbee: Zigbee network/APS/ZCL layers
    - killerbee: Radio interface

    Why:
    - Touchlink operates at network layer
    - No network key required (inter-PAN)
    - Scapy provides Zigbee packet crafting
    """

    # Craft Touchlink Reset to Factory New Request
    # Transaction ID, Inter-PAN
    # Command ID: 0x07 (Reset to Factory New)

    packet = ZigbeeNWK() / ZigbeeAppDataPayload(cmd_identifier=0x07)

    # Send packet via killerbee
    pass
```

### 3. Key Extraction from Packet Capture

**Scenario**: Join process captured, extract network key

**Pseudocode**:
```python
# Extract network key from captured join

def extract_network_key(pcap_file, trust_center_link_key):
    """
    Libraries:
    - scapy: PCAP parsing
    - Crypto.Cipher.AES: AES-CCM decryption

    Why:
    - Network key is transported encrypted with TCLK
    - AES-CCM with MIC for authentication
    - Scapy provides 802.15.4/Zigbee parsing
    """

    from scapy.all import rdpcap
    from Crypto.Cipher import AES

    packets = rdpcap(pcap_file)

    for pkt in packets:
        # Look for Transport Key command
        # Decrypt with TCLK using AES-CCM
        # Extract network key
        pass
```

**Required Libraries**:
- **Python**: `pycryptodome` (AES-CCM), `scapy`
- **C++**: `<openssl/evp.h>` (AES), custom CCM implementation

## Channel Reference

### 2.4 GHz Band (IEEE 802.15.4)

| Channel | Frequency (MHz) | WiFi Overlap | Notes |
|---------|-----------------|--------------|-------|
| 11 | 2405 | WiFi 1 (2412) | Minimal overlap |
| 12 | 2410 | WiFi 1 | Overlaps |
| 13 | 2415 | WiFi 1 | Overlaps |
| 14 | 2420 | WiFi 1-2 | Overlaps |
| 15 | 2425 | WiFi 2-3 | **Use WiFi Ch 1, Zigbee Ch 15** |
| 16 | 2430 | WiFi 3-4 | Overlaps |
| 17 | 2435 | WiFi 4-5 | Overlaps |
| 18 | 2440 | WiFi 5-6 | Overlaps |
| 19 | 2445 | WiFi 6-7 | Overlaps |
| 20 | 2450 | WiFi 7-8 | **Use WiFi Ch 6, Zigbee Ch 20** |
| 21 | 2455 | WiFi 8-9 | Overlaps |
| 22 | 2460 | WiFi 9-10 | Overlaps |
| 23 | 2465 | WiFi 10-11 | Overlaps |
| 24 | 2470 | WiFi 11-12 | Overlaps |
| 25 | 2475 | WiFi 12-13 | **Use WiFi Ch 11, Zigbee Ch 25** |
| 26 | 2480 | WiFi 13-14 | Minimal overlap (WiFi 14 Japan only) |

**Optimal Combinations** (US):
- WiFi Ch 1 + Zigbee Ch 15 or 26
- WiFi Ch 6 + Zigbee Ch 20 or 26
- WiFi Ch 11 + Zigbee Ch 15 or 25

### Sub-GHz Bands

**868 MHz (EU)**:
- Single channel (Channel 0): 868.3 MHz
- 20 kbps data rate
- Better penetration, longer range

**915 MHz (Americas)**:
- 10 channels (1-10): 906-924 MHz
- 40 kbps data rate
- Less WiFi interference

## Zigbee Profiles

### Home Automation (HA)
- **Profile ID**: 0x0104
- **Devices**: Lights, locks, sensors, thermostats
- **Clusters**: On/Off (0x0006), Level Control (0x0008), Color Control (0x0300)

### Light Link (LL / Touchlink)
- **Profile ID**: 0xC05E
- **Devices**: Smart bulbs (Philips Hue)
- **Features**: Proximity commissioning, factory reset

### Smart Energy (SE)
- **Profile ID**: 0x0109
- **Devices**: Smart meters, energy management
- **Security**: Certificate-based (CBKE - Certificate-Based Key Establishment)

## Dataset Generation

```yaml
protocol: "Zigbee"
phy_standard: "802.15.4"
frequency_mhz: 2405-2480 | 868 | 906-924
channel: 11-26 | 0 | 1-10
panid: "0x1234"
device_type: "coordinator" | "router" | "end_device"
security_level: "0x00" | "0x05" | "0x06" | "0x07"
encryption_key: "default" | "custom" | "extracted"
attack_type: "dos" | "mitm" | "injection" | "sniffing" | "key_extraction"
attack_vector: "jamming" | "touchlink_reset" | "command_injection" | "replay"
target_device: "Philips_Hue" | "SmartThings_Sensor" | "CC2531_Coordinator"
duration_sec: 30
success: true | false
impact: "device_reset" | "network_key_extracted" | "command_executed"
```

## Industrial IoT Focus

### Protocols
- **Zigbee PRO**: Industrial mesh networking
- **WirelessHART**: Process automation (overlays on 802.15.4)
- **ISA100.11a**: Industrial wireless standard

### Attack Scenarios
- SCADA system penetration via Zigbee gateway
- Sensor data manipulation (temperature, pressure)
- Actuator control hijacking (valves, motors)
- Network segmentation bypass

### Tools
- **Z-Fuzzer**: Zigbee fuzzing framework
- **Sniffle**: Zigbee/802.15.4 sniffer for nRF52840
- **Attify Zigbee Framework**: IoT pentesting suite

## Ethical Guidelines

- ✅ Test only on owned Zigbee networks
- ✅ Isolated test environment (Faraday cage for RF containment)
- ✅ Do not interfere with critical infrastructure
- ❌ **Never** attack smart home devices you don't own
- ❌ **Never** interfere with industrial control systems
- ❌ **Never** attack medical devices or public safety systems

---

**Related**: [[README|Home]] • [[INDEX|Index]] • [[Bluetooth/README|Bluetooth]] • [[WiFi/README|WiFi]] • [[LoRa/README|LoRa]]

**Status**: Comprehensive framework - Ready for Q2 2025 implementation
