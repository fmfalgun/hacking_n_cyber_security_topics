---
title: Complete Index - Wireless Protocol Security Research
tags: [index, navigation, table-of-contents]
category: Navigation
parent: "[[README]]"
---

# Complete Index - Wireless Protocol Security Research

> **Navigation Hub**: Comprehensive index of all research documentation, organized by protocol and attack category.

---

## Quick Navigation

- [[README|🏠 Home]]
- [[Bluetooth/README|📡 Bluetooth]] (Classic + BLE)
- [[WiFi/README|📶 WiFi]] (✅ Complete)
- [[Zigbee/README|🏠 Zigbee]] (✅ Complete)
- [[LoRa/README|📻 LoRa]] (✅ Complete)
- [[Lab-Setup/README|⚙️ Lab Setup]]
- [[Traffic-Capture/README|📊 Traffic Capture]]
- [[Dataset-Organization/README|🗂️ Dataset Organization]]
- [[Model-Training/README|🤖 Model Training]]

---

## 📡 Wireless Protocols

### 1. Bluetooth
[[Bluetooth/README|→ Bluetooth Research Hub]]

Comprehensive research on **Bluetooth Classic (BR/EDR)** and **Bluetooth Low Energy (BLE)**.

#### A. Bluetooth Low Energy (BLE)
**Status**: ✅ Active Research | **Progress**: DoS Implementation Phase

**Core Documentation**:
- [[Bluetooth/BLE/README|BLE Home & Overview]]
- [[Bluetooth/BLE/01-protocol-overview|Complete Protocol Breakdown]] (PHY, LL, L2CAP, ATT, GATT, SMP)

**Attack Categories**:

- **DoS Attacks**: [[Bluetooth/BLE/DoS/README|Overview]] • [[Bluetooth/BLE/DoS/01-dos-attack-theory|Theory (35k+ lines)]] • [[Bluetooth/BLE/DoS/03-dos-attack-cheatsheet|Cheatsheet]]
- **MITM Attacks**: [[Bluetooth/BLE/MITM/README|Overview]]
- **Injection Attacks**: [[Bluetooth/BLE/Injection/README|Overview]]
- **Sniffing**: [[Bluetooth/BLE/Sniffing/README|Overview]]

**Implementation**: [[Bluetooth/BLE/Scripting/README|Scripting]] • [[Bluetooth/BLE/Scripting/01-packet-crafting-basics|Packet Crafting (Python & C++)]]

#### B. Bluetooth Classic (BR/EDR)
**Status**: 📋 Planned | **Progress**: After WiFi

**Planned Coverage**:
- [[Bluetooth/Classic/README|Bluetooth Classic Overview]]
- BlueBorne, KNOB, BIAS attacks
- A2DP, RFCOMM, SPP exploitation
- Pairing attacks and SDP enumeration

**Attack Categories**: DoS, MITM, Injection, Sniffing, Scripting (all planned)

---

### 2. WiFi (802.11)
**Status**: ✅ Complete | **Progress**: Comprehensive Documentation

[[WiFi/README|→ WiFi Research Hub]]

**Coverage**:
- [[WiFi/README|Complete Protocol Analysis]] (802.11b through WiFi 7)
- [[WiFi/DoS/README|DoS Attacks]] (deauth, disassoc, beacon flooding, CTS flooding)
- [[WiFi/MITM/README|MITM Attacks]] (evil twin, rogue AP, karma attacks)
- [[WiFi/Injection/README|Injection Attacks]] (frame injection, fuzzing)
- [[WiFi/Sniffing/README|Sniffing Techniques]] (monitor mode, channel hopping)
- [[WiFi/Scripting/README|Packet Crafting]] (Scapy, Python)
- WPA/WPA2/WPA3 security analysis

---

### 3. Zigbee (IEEE 802.15.4)
**Status**: ✅ Complete | **Progress**: Comprehensive Documentation

[[Zigbee/README|→ Zigbee Research Hub]]

**Coverage**:
- [[Zigbee/README|Complete Protocol Analysis]] (802.15.4 PHY/MAC, Zigbee stack APL → PHY)
- [[Zigbee/DoS/README|DoS Attacks]] (RF jamming, beacon flooding, ACK spoofing)
- [[Zigbee/MITM/README|MITM Attacks]] (malicious coordinator, key interception, touchlink)
- [[Zigbee/Injection/README|Injection Attacks]] (ZCL commands, replay attacks, OTA hijacking)
- [[Zigbee/Sniffing/README|Sniffing Techniques]] (KillerBee, network discovery)
- [[Zigbee/Scripting/README|Packet Crafting]] (KillerBee, Scapy)
- Security mechanisms (AES-128-CCM, key types)
- Industrial IoT focus

---

### 4. LoRa/LoRaWAN
**Status**: ✅ Complete | **Progress**: Comprehensive Documentation

[[LoRa/README|→ LoRa Research Hub]]

**Coverage**:
- [[LoRa/README|Complete Protocol Analysis]] (LoRa PHY CSS, LoRaWAN MAC)
- [[LoRa/DoS/README|DoS Attacks]] (RF jamming, join request flooding, collision attacks)
- [[LoRa/MITM/README|MITM Attacks]] (rogue gateway, join accept manipulation, wormhole)
- [[LoRa/Injection/README|Injection Attacks]] (uplink/downlink injection, MAC commands, fuzzing)
- [[LoRa/Sniffing/README|Sniffing Techniques]] (SDR, gr-lora, multi-SF reception)
- [[LoRa/Scripting/README|Packet Crafting]] (GNU Radio, Arduino-LMIC, Python)
- OTAA/ABP security (AES-128, MIC calculation)
- Both frequency bands (868 MHz EU, 915 MHz US)

---

## 🛠️ Infrastructure & Tooling

### Lab Setup
**Status**: 📋 Planned

- [[Lab-Setup/README|Lab Setup Overview]]
- Hardware shopping list (Ubertooth, HackRF, nRF52840, ESP32)
- Software installation (BlueZ, Wireshark, Scapy)
- Virtual lab environment
- Safety and legal compliance

### Traffic Capture
**Status**: 📋 Planned

- [[Traffic-Capture/README|Traffic Capture Overview]]
- Wireshark configuration
- btmon/Ubertooth capture procedures
- PCAP organization and naming conventions
- Automated capture scripts

### Dataset Organization
**Status**: 📋 Planned

- [[Dataset-Organization/README|Dataset Organization Overview]]
- Directory structure for labeled datasets
- Metadata schemas (YAML/JSON)
- Train/test/validation splits
- Version control for datasets

### Model Training
**Status**: 📋 Planned

- [[Model-Training/README|Model Training Overview]]
- Feature extraction from packet captures
- Model architectures (Random Forest, LSTM, Transformer)
- Training pipelines
- Evaluation metrics and validation

---

## 📚 Reference Tables

### BLE Quick Reference

#### Attack Vectors by Layer
| Layer | Attack Type | Difficulty | Impact | Status |
|-------|-------------|------------|--------|--------|
| **Link Layer** | Advertising Flood | Low | High | ✅ Documented |
| **Link Layer** | Connection Flood | Medium | High | ✅ Documented |
| **L2CAP** | Param Update Storm | Low | High | ✅ Documented |
| **ATT** | Write Flood (0x52) | Low | Very High | ✅ Documented |
| **SMP** | Pairing Spam | Low | Medium | ✅ Documented |

#### Hardware Comparison
| Device | BLE TX | BLE RX | Cost | Best For |
|--------|--------|--------|------|----------|
| **Linux + BlueZ** | ✅ HCI | ✅ HCI | $0 | ATT/L2CAP attacks |
| **nRF52840** | ✅✅ Full | ✅✅ Full | $10 | All attacks, custom FW |
| **Ubertooth** | ⚠️ Limited | ✅✅ Full | $120 | Sniffing, analysis |
| **ESP32** | ✅ HCI | ✅ HCI | $5 | Budget testing |

#### Protocol Layer Stack
```
┌─────────────────────────────────┐
│  Application (GATT Services)   │ ← User data
├─────────────────────────────────┤
│  ATT (Attribute Protocol)      │ ← Read/Write/Notify (CID 0x0004)
├─────────────────────────────────┤
│  SMP (Security Manager)        │ ← Pairing/Encryption (CID 0x0006)
├─────────────────────────────────┤
│  L2CAP (Logical Link Control)  │ ← Multiplexing, Signaling
├─────────────────────────────────┤
│  HCI (Host Controller Interface│ ← Commands, Events, ACL Data
├─────────────────────────────────┤
│  Link Layer (LL)               │ ← Advertising, Connection, Data PDUs
├─────────────────────────────────┤
│  Physical Layer (PHY)          │ ← 2.4 GHz, GFSK, 40 channels
└─────────────────────────────────┘
```

### Key Opcodes & Commands

#### ATT Opcodes (L2CAP CID 0x0004)
| Opcode | Name | Response Required | DoS Potential |
|--------|------|-------------------|---------------|
| **0x52** | **Write Command** | **No** | **Very High** |
| 0x12 | Write Request | Yes (0x13) | High |
| 0x0A | Read Request | Yes (0x0B) | Medium |
| 0x1B | Notification | No | High (if peripheral) |
| 0x1D | Indication | Yes (0x1E) | Medium |

#### HCI Command OpCodes
| OpCode | OGF | OCF | Name | Use Case |
|--------|-----|-----|------|----------|
| 0x200A | 0x08 | 0x000A | LE Set Advertising Enable | Adv flood |
| 0x2008 | 0x08 | 0x0008 | LE Set Advertising Data | Change AdvData |
| 0x200D | 0x08 | 0x000D | LE Create Connection | Conn flood |

#### SMP Command Codes (L2CAP CID 0x0006)
| Code | Name | Payload Size | Attack Use |
|------|------|--------------|------------|
| **0x01** | **Pairing Request** | 6 bytes | **Pairing spam** |
| 0x0C | Pairing Public Key | 64 bytes | Invalid ECDH points |

---

## 🎯 Research Workflow

### Phase 1: Protocol Understanding
1. Read protocol overview documentation
2. Understand layer interactions and packet structures
3. Study legitimate communication flows

### Phase 2: Attack Implementation
4. Choose attack vector from analysis documents
5. Reference cheatsheet for header fields and opcodes
6. Craft packets using scripting guides
7. Test on controlled infrastructure

### Phase 3: Data Collection
8. Configure capture tools (Wireshark, btmon, Ubertooth)
9. Execute attack with varying parameters
10. Label captures with attack metadata

### Phase 4: Analysis & ML Training
11. Organize datasets by attack type
12. Extract features from packet captures
13. Train detection models
14. Evaluate model performance

---

## 📖 Learning Paths

### Beginner: Understanding BLE Basics
1. [[Bluetooth/BLE/01-protocol-overview|BLE Protocol Overview]] (Sections 1-6)
2. [[Bluetooth/BLE/DoS/03-dos-attack-cheatsheet|Header Field Reference]] (Sections 1-3)
3. Practice: Use `hcitool lescan` and `gatttool`

### Intermediate: Implementing Basic Attacks
4. [[Bluetooth/BLE/DoS/01-dos-attack-theory|DoS Theory]] (Sections 1-3)
5. [[Bluetooth/BLE/Scripting/01-packet-crafting-basics|Packet Crafting]] (Sections 1-3)
6. Implement: Advertising flood with address rotation

### Advanced: Full Attack Suite & ML Integration
7. [[Bluetooth/BLE/DoS/01-dos-attack-theory|Complete DoS Analysis]]
8. [[Bluetooth/BLE/Scripting/01-packet-crafting-basics|Advanced Crafting]] (All sections)
9. Build: Automated attack framework with traffic capture
10. Train: ML model on labeled datasets

---

## 📊 Documentation Statistics

### Protocol Documentation
- **BLE**: 13 files (~230 KB, 25+ attack vectors, 7 protocol layers)
- **WiFi**: 6 files (comprehensive 802.11b-WiFi 7, WPA/WPA2/WPA3)
- **Zigbee**: 6 files (complete 802.15.4 + Zigbee stack, industrial IoT)
- **LoRa**: 6 files (LoRa PHY + LoRaWAN MAC, OTAA/ABP)
- **Total Code Examples**: 150+ (Python, C++, GNU Radio)
- **Total Attack Vectors**: 75+ documented across all protocols

### Research Progress
- ✅ **BLE Protocol Analysis**: Complete
- ✅ **BLE DoS Theory**: Complete
- ✅ **BLE Packet Crafting**: Complete
- 🔄 **BLE DoS Implementation**: In Progress
- ✅ **WiFi Protocol & Attack Documentation**: Complete
- ✅ **Zigbee Protocol & Attack Documentation**: Complete
- ✅ **LoRa Protocol & Attack Documentation**: Complete
- 📋 **Bluetooth Classic Documentation**: Planned

---

## 🔗 External Resources

### Official Specifications
- [Bluetooth Core Specification](https://www.bluetooth.com/specifications/specs/) (Official BLE spec)
- [IEEE 802.11 Standards](https://standards.ieee.org/standard/802_11-2020.html) (WiFi)
- [IEEE 802.15.4 Standard](https://standards.ieee.org/standard/802_15_4-2020.html) (Zigbee)

### Security Research
- [Phrack Magazine](http://www.phrack.org/) - Hacking articles
- [BLE Security Papers](https://scholar.google.com/scholar?q=bluetooth+low+energy+security)

### Tools & Frameworks
- [BlueZ](http://www.bluez.org/) - Linux Bluetooth stack
- [Wireshark](https://www.wireshark.org/) - Packet analysis
- [Scapy](https://scapy.net/) - Python packet crafting
- [Ubertooth](https://github.com/greatscottgadgets/ubertooth) - BLE sniffing

### Learning Resources
- [Monkeytype](https://monkeytype.com) - Typing practice
- [CodeChef](https://www.codechef.com) - Competitive programming
- [LeetCode](https://leetcode.com) - Algorithm practice
- [ChatGPT](https://chat.openai.com) - AI assistant
- [Gemini](https://gemini.google.com) - AI assistant

---

## 🔐 Security & Ethics

### Authorized Use Only
All techniques documented in this repository are for:
- ✅ Authorized security testing on owned devices
- ✅ Defensive research and vulnerability analysis
- ✅ Educational purposes in controlled environments
- ✅ Machine learning dataset generation for IDS development

### Prohibited Activities
- ❌ Testing devices without explicit permission
- ❌ Attacking public infrastructure
- ❌ Medical or safety-critical system targeting
- ❌ Malicious use or distribution

### Legal Compliance
- Always obtain written authorization before testing
- Document scope and boundaries
- Follow responsible disclosure for vulnerabilities
- Comply with local and international laws

---

## 📝 Document Conventions

### Status Indicators
- ✅ **Complete**: Fully documented and reviewed
- 🔄 **In Progress**: Active development
- 📋 **Planned**: Scheduled for future work
- ⚠️ **Limited**: Partial implementation or restrictions
- ❌ **Not Available**: Not supported

### File Naming
- `XX-descriptive-name.md` - Numbered sequence for ordering
- `README.md` - Directory overview and navigation
- `INDEX.md` - Global navigation hub

### Cross-Linking Format
- `[[Directory/File|Display Name]]` - Obsidian-style wiki links
- Hierarchical parent-child relationships in YAML frontmatter
- Bidirectional links between related topics

---

## 🚀 Quick Start

### For New Researchers
1. Start with [[README|Main README]]
2. Review [[Lab-Setup/README|Lab Setup]] for hardware requirements
3. Read [[Bluetooth/BLE/01-protocol-overview|BLE Protocol Overview]]
4. Follow beginner learning path above

### For Experienced Security Researchers
1. Jump to [[Bluetooth/BLE/DoS/01-dos-attack-theory|DoS Attack Analysis]]
2. Reference [[Bluetooth/BLE/DoS/03-dos-attack-cheatsheet|Cheatsheet]] for quick lookups
3. Use [[Bluetooth/BLE/Scripting/01-packet-crafting-basics|Packet Crafting]] for implementation
4. Build custom attacks based on documented vectors

### For ML/Data Science Focus
1. Review attack documentation for context
2. Set up [[Traffic-Capture/README|capture pipeline]]
3. Organize data with [[Dataset-Organization/README|labeling standards]]
4. Follow [[Model-Training/README|ML training guides]]

---

## 📅 Last Updated

**Date**: 2025-11-12
**Version**: 1.0
**Maintainer**: CS Security Research Team
**License**: Educational and Authorized Research Use Only

---

**[[README|← Back to Home]]**
