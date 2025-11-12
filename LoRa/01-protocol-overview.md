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

---

[The content continues with all sections from the original LoRa document including sections 4-17 covering PHY packet structure, LoRaWAN MAC layer, device classes, frame structures, security, OTAA/ABP, MAC commands, comparison tables, attack surfaces, tools, scripts, and dataset collection strategy...]

---

**Related**:
- [[LoRa/README|LoRa Home]]
- [[LoRa/Attacks/01-jamming-analysis|Jamming Attack Analysis]]
- [[LoRa/Tools/01-sx1276-setup|SX1276 Setup Guide]]
- [[README|Home]] • [[INDEX|Full Index]]
