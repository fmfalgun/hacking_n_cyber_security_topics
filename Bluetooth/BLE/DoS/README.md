---
title: BLE Denial of Service (DoS) Attacks
tags: [BLE, DoS, denial-of-service, flooding, resource-exhaustion]
category: BLE Security
parent: "[[Bluetooth/BLE/README]]"
status: active
---

# BLE Denial of Service (DoS) Attacks

## Overview

Denial of Service (DoS) attacks on BLE aim to disrupt communication, exhaust resources, or crash target devices. This section covers comprehensive analysis, implementation guides, and quick references for DoS attack vectors across all BLE protocol layers.

## Attack Categories

### 1. Advertising Phase Attacks
**Target**: Scanners and devices in discovery mode

| Attack Type | Mechanism | Impact |
|-------------|-----------|--------|
| **Advertising Flood** | Rapid transmission of ADV_IND packets | Scanner CPU saturation, UI lag |
| **Scan Response Amplification** | Max-size SCAN_RSP replies | Memory exhaustion, parser overload |
| **Address Rotation** | Spoofed advertiser addresses | Bypass duplicate filtering, tracking prevention |
| **Malformed AdvData** | Invalid AD structure lengths | Parser crashes, buffer overflows |

### 2. Connection Phase Attacks
**Target**: Devices during or after connection establishment

| Attack Type | Mechanism | Impact |
|-------------|-----------|--------|
| **Connection Request Flood** | Rapid CONNECT_REQ packets | Connection table exhaustion |
| **Parameter Abuse** | Extreme connection parameters | Connection instability, crashes |
| **Retransmission Storm** | Fixed SN/NESN values | Force infinite retransmissions |
| **Empty Packet Flood** | Zero-length data PDUs | Queue saturation, CPU waste |

### 3. Data Phase Attacks
**Target**: Established connections

| Attack Type | Mechanism | Impact |
|-------------|-----------|--------|
| **ATT Write Flood** | Write Without Response (0x52) at max rate | Server memory exhaustion, unresponsive |
| **ATT Read Flood** | Repeated Read Requests | Force continuous data retrieval, CPU load |
| **L2CAP Signaling Storm** | Rapid param update requests | Control plane saturation |
| **Notification/Indication Flood** | Max-rate server-initiated data | Client overload (if peripheral role) |

### 4. Security Layer Attacks
**Target**: Pairing and encryption mechanisms

| Attack Type | Mechanism | Impact |
|-------------|-----------|--------|
| **Pairing Spam** | Repeated SMP Pairing Requests | State table exhaustion, new pairing fails |
| **Invalid Crypto Data** | Malformed ECDH public keys | Parser crashes, pairing failures |
| **Encryption Downgrade** | Force legacy pairing methods | Security weakening (preparatory for MITM) |

## Document Organization

### Theory & Analysis
[[Bluetooth/BLE/DoS/01-dos-attack-theory|01. DoS Attack Theory & Analysis]]
- Layer-by-layer exploitation analysis (35k+ lines)
- Attack vector breakdown with technical details
- Hardware capability mapping
- Vendor vulnerability comparison

### Implementation Guide
[[Bluetooth/BLE/DoS/02-dos-implementation-guide|02. DoS Implementation Guide]]
- Step-by-step attack implementation
- Python and C++ code examples
- BlueZ and nRF52840 approaches
- Capture and labeling procedures

### Quick Reference
[[Bluetooth/BLE/DoS/03-dos-attack-cheatsheet|03. DoS Attack Cheatsheet]]
- Header field reference tables
- OpCode and value quick lookups
- Attack vector to field mappings
- Exploitation knobs (rate, size, timing)

## Attack Effectiveness Matrix

| Attack | Hardware | Difficulty | Success Rate | Detection Difficulty |
|--------|----------|------------|--------------|----------------------|
| **Advertising Flood** | BlueZ, nRF52840 | Low | Very High | Medium |
| **ATT Write Flood** | BlueZ, nRF52840 | Low | Very High | Low |
| **Connection Flood** | nRF52840 (custom FW) | Medium | High | Medium |
| **Retransmission Storm** | nRF52840 (custom FW) | High | Medium | High |
| **L2CAP Param Storm** | BlueZ | Low | High | Low |
| **SMP Pairing Spam** | BlueZ | Low | Medium | Medium |
| **Invalid Crypto** | BlueZ, Scapy | Medium | Medium | High |

## Primary Attack Vectors (Prioritized)

Based on implementation ease and effectiveness:

1. **ATT Write Without Response Flood** (Opcode 0x52)
   - No flow control, max MTU payloads
   - Achievable with BlueZ gatttool or Scapy
   - 200+ packets/sec possible

2. **Advertising Flood with Address Rotation**
   - Bypass scanner duplicate filtering
   - Achievable with HCI commands
   - 50-100 Hz advertising rate

3. **L2CAP Connection Parameter Update Storm**
   - Extreme parameter values
   - Achievable with BlueZ L2CAP sockets
   - Multiple requests per second

4. **SMP Pairing Request Spam**
   - Never complete pairing handshake
   - Achievable with BlueZ/Scapy
   - Exhaust pairing state tables

## Exploit able Header Fields Reference

Quick lookup for attack parameters:

| Layer | Field | Normal Range | Attack Values |
|-------|-------|--------------|---------------|
| **LL Adv** | Length | 6-37 bytes | 37 (max) |
| **LL Adv** | AdvAddr | Device MAC | Rotated addresses |
| **LL Data** | SN/NESN | Alternating | Fixed (retrans storm) |
| **LL Data** | Length | 0-251 | 0 or 251 (extremes) |
| **L2CAP** | Length | Actual | 65535 (mismatch) |
| **L2CAP Sig** | Code 0x12 | Param update | Extreme params |
| **ATT** | Opcode 0x52 | Write cmd | Max MTU payload |
| **SMP** | Code 0x01 | Pair req | Min key size (7) |

## Implementation Workflow

```
1. Study Protocol → [[Bluetooth/BLE/01-protocol-overview|Protocol Overview]]
   └─ Understand target layer

2. Craft Attack Packets → [[Bluetooth/BLE/Scripting/01-packet-crafting-basics|Packet Crafting]]
   └─ Use Python/C++ examples

3. Implement Attack Script
   └─ Test on controlled devices

4. Capture Traffic → [[Traffic-Capture/README|Traffic Capture]]
   └─ Wireshark + btmon + Ubertooth

5. Label Dataset → [[Dataset-Organization/README|Dataset Organization]]
   └─ Tag attack type, parameters

6. Train Model → [[Model-Training/README|Model Training]]
   └─ Feature extraction → ML training
```

## Hardware Comparison for DoS

| Device | Adv Flood | Conn Flood | ATT Flood | L2CAP Storm | SMP Spam |
|--------|-----------|------------|-----------|-------------|----------|
| **Linux + BlueZ** | ✅ (HCI) | ✅ (HCI) | ✅ (gatttool/Scapy) | ✅ (Scapy) | ✅ (Scapy) |
| **nRF52840** | ✅✅ (best) | ✅✅ (best) | ✅ (custom FW) | ⚠️ (complex) | ✅ (custom FW) |
| **Ubertooth** | ❌ (RX only) | ❌ | ❌ | ❌ | ❌ |

**Legend**: ✅ = Possible, ✅✅ = Optimal, ⚠️ = Limited, ❌ = Not possible

## Target Vulnerability Analysis

Common vulnerable implementations:

- **Android BLE Stack**: Susceptible to ATT write floods, adv floods
- **iOS BLE Stack**: Better filtering, but L2CAP param storms effective
- **ESP32 Arduino**: Very vulnerable to all attacks (limited resources)
- **nRF5x SDK**: Moderate resilience, param validation present
- **BlueZ (Linux)**: Vulnerable to SMP spam, ATT floods

## Defensive Observations

During attack research, we observed these defenses:

1. **Rate Limiting**: Some stacks limit connection requests per second
2. **Duplicate Filtering**: Scanners filter duplicate AdvAddr
3. **Parameter Validation**: Reject extreme connection parameters
4. **Queue Limits**: ATT write queues have size limits (overflow = disconnect)
5. **Pairing Timeouts**: SMP state machines timeout after 30 seconds

## Dataset Labeling Strategy

For ML training, label captures with:
```yaml
attack_type: "att_write_flood"
layer: "ATT"
opcode: "0x52"
rate_hz: 200
payload_size_bytes: 512
duration_sec: 30
target_device: "ESP32_DevKit"
success: true
impact: "server_unresponsive"
```

## Ethical Guidelines

- ✅ Test only on devices you own
- ✅ Isolated test environment (no public Bluetooth interference)
- ✅ Document all findings for defensive research
- ❌ Never target medical devices or safety-critical systems
- ❌ Never deploy attacks on public infrastructure

---

**Related**:
- [[Bluetooth/BLE/README|BLE Home]]
- [[Bluetooth/BLE/01-protocol-overview|Protocol Overview]]
- [[Bluetooth/BLE/Scripting/01-packet-crafting-basics|Packet Crafting]]
- [[Bluetooth/BLE/MITM/README|MITM Attacks]]
- [[Bluetooth/BLE/Injection/README|Injection Attacks]]

**Status**: Implementation phase - Attack scripts in development
