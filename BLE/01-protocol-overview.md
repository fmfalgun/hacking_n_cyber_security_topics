---
title: BLE Protocol Overview - Complete Stack Breakdown
tags: [BLE, protocol-analysis, PHY, link-layer, L2CAP, ATT, GATT, SMP, HCI]
category: BLE Security
parent: "[[BLE/README]]"
status: complete
---

# BLE Protocol Overview - Complete Stack Breakdown

> **Purpose**: Comprehensive technical breakdown of all BLE protocol layers from Physical (PHY) to Application (GATT), including packet structures, connection flows, and attack surfaces.


# **BLUETOOTH LOW ENERGY (BLE) - COMPLETE PROTOCOL BREAKDOWN**

## **1. BLE Architecture Overview**

BLE is fundamentally different from WiFi in architecture:

```
┌─────────────────────────────────────────┐
│         APPLICATION LAYER               │
├─────────────────────────────────────────┤
│  GATT (Generic Attribute Profile)      │ ← Services, Characteristics
├─────────────────────────────────────────┤
│  ATT (Attribute Protocol)               │ ← Read/Write/Notify operations
├─────────────────────────────────────────┤
│  L2CAP (Logical Link Control &          │ ← Packet fragmentation/reassembly
│         Adaptation Protocol)             │
├─────────────────────────────────────────┤
│  HCI (Host Controller Interface)        │ ← Commands/Events/Data
├─────────────────────────────────────────┤
│  LINK LAYER (LL)                        │ ← Connection, Advertising, Scanning
├─────────────────────────────────────────┤
│  PHYSICAL LAYER (PHY)                   │ ← 2.4 GHz, GFSK modulation
└─────────────────────────────────────────┘
```

**Key Differences from WiFi:**
- **WiFi**: Infrastructure-based (AP ↔ Clients)
- **BLE**: Peer-to-peer with roles (Central ↔ Peripheral, Advertiser ↔ Scanner)

---

## **2. BLE PHYSICAL LAYER**

### **2.1 Frequency & Channels**

```
Operating Band: 2.400 - 2.4835 GHz (same as WiFi!)

BLE uses 40 channels (2 MHz wide each):
├── 3 Advertising Channels (37, 38, 39) ← Used for discovery
└── 37 Data Channels (0-36)             ← Used for connections

Channel Frequencies:
- Channel 37: 2.402 GHz
- Channel 0-10: 2.404 - 2.424 GHz
- Channel 38: 2.426 GHz
- Channel 11-36: 2.428 - 2.478 GHz
- Channel 39: 2.480 GHz
```

**Why 3 advertising channels?**
- Positioned to avoid WiFi channels 1, 6, 11 (most common WiFi channels)
- Increases chance of discovery in crowded 2.4 GHz spectrum

### **2.2 Modulation**
- **GFSK** (Gaussian Frequency Shift Keying)
- **1 Mbps** data rate (BLE 4.x)
- **2 Mbps** optional (BLE 5.x)

---

## **3. BLE LINK LAYER - THE CORE**

This is where most BLE attacks happen! Similar to WiFi Layer 2.

### **3.1 Link Layer States**

```
┌─────────────┐
│  STANDBY    │ ← Initial state
└──────┬──────┘
       │
       ├──→ ┌─────────────┐
       │    │ ADVERTISING │ ← Broadcasting presence (Peripheral role)
       │    └─────────────┘
       │
       ├──→ ┌─────────────┐
       │    │  SCANNING   │ ← Listening for advertisements (Central role)
       │    └─────────────┘
       │
       ├──→ ┌─────────────┐
       │    │ INITIATING  │ ← Sending connection request
       │    └─────────────┘
       │
       └──→ ┌─────────────┐
            │ CONNECTION  │ ← Established connection
            └─────────────┘
```

---

## **4. BLE PACKET STRUCTURE (LINK LAYER)**

Every BLE packet has this structure:

```
┌─────────────┬──────────┬─────────────┬─────────┐
│  PREAMBLE   │  ACCESS  │   PAYLOAD   │   CRC   │
│   (1 byte)  │  ADDRESS │  (2-257 B)  │ (3 B)   │
│             │  (4 B)   │             │         │
└─────────────┴──────────┴─────────────┴─────────┘
```

### **4.1 Preamble (1 byte)**
- **Purpose**: Receiver synchronization
- **Value**: `0xAA` (if Access Address LSB = 0) or `0x55` (if LSB = 1)
- **Why**: Alternating bit pattern helps radio lock onto signal

### **4.2 Access Address (4 bytes)**
- **Purpose**: Identifies the connection or advertising channel
- **Advertising packets**: Always `0x8E89BED6` (fixed for all advertising)
- **Data packets**: Unique random value generated during connection
- **Why**: Allows multiple connections to coexist; receiver filters packets

### **4.3 Payload (2-257 bytes)**
This is where it gets interesting! Payload structure:

```
┌──────────┬─────────────────────────────┐
│  HEADER  │          PDU                │
│  (2 B)   │      (variable)             │
└──────────┴─────────────────────────────┘
```

#### **Link Layer Header (2 bytes / 16 bits)**

```
Bit Layout:
┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
│ 15 │ 14 │ 13 │ 12 │ 11 │ 10 │  9 │  8 │  7 │  6 │  5 │  4 │  3 │  2 │  1 │  0 │
├────┴────┴────┴────┼────┼────┼────┼────┴────┴────┴────┴────┴────┴────┴────┴────┤
│   PDU Type (4b)   │RSVD│ChSel│TxAdd│RxAdd│        Length (6-8 bits)          │
└───────────────────┴────┴────┴─────┴─────┴────────────────────────────────────┘
```

**Field Breakdown:**

| Field | Bits | Purpose | Values |
|-------|------|---------|--------|
| **PDU Type** | 4 | Packet type identifier | ADV_IND, CONNECT_REQ, etc. |
| **RFU** | 2 | Reserved for future use | 0 |
| **ChSel** | 1 | Channel selection algorithm | 0=Algorithm #1, 1=Algorithm #2 |
| **TxAdd** | 1 | Transmitter address type | 0=Public, 1=Random |
| **RxAdd** | 1 | Receiver address type | 0=Public, 1=Random |
| **Length** | 6-8 | Payload length | 6-255 bytes |

### **4.4 CRC (3 bytes)**
- **Purpose**: Error detection
- **Polynomial**: 0x00065B (different from WiFi!)
- **Why**: Detects bit errors in transmission

---

## **5. ADVERTISING PACKETS (Discovery Phase)**

This is BLE's equivalent of WiFi beacon frames!

### **5.1 Advertising PDU Types**

| PDU Type | Hex | Name | Purpose |
|----------|-----|------|---------|
| 0000 | 0x0 | **ADV_IND** | Connectable & scannable undirected advertising |
| 0001 | 0x1 | **ADV_DIRECT_IND** | Connectable directed advertising (high duty cycle) |
| 0010 | 0x2 | **ADV_NONCONN_IND** | Non-connectable undirected advertising (beacons) |
| 0011 | 0x3 | **SCAN_REQ** | Scan request from scanner to advertiser |
| 0100 | 0x4 | **SCAN_RSP** | Scan response from advertiser to scanner |
| 0101 | 0x5 | **CONNECT_REQ** | Connection request (WiFi's Association Request!) |
| 0110 | 0x6 | **ADV_SCAN_IND** | Scannable undirected advertising |

### **5.2 ADV_IND Packet Structure**

```
┌──────────────────────────────────────────────────────────┐
│                    LINK LAYER HEADER                     │
│  PDU Type: 0000 (ADV_IND) | Length: X bytes              │
├──────────────────────────────────────────────────────────┤
│                    ADVERTISER ADDRESS                     │
│                       (6 bytes)                          │
├──────────────────────────────────────────────────────────┤
│                      ADV DATA                            │
│                    (0-31 bytes)                          │
│  Format: [Length][Type][Data][Length][Type][Data]...    │
└──────────────────────────────────────────────────────────┘
```

**Example ADV_IND packet:**
```
Preamble: AA
Access Address: D6 BE 89 8E
Header: 40 09  ← PDU Type=0 (ADV_IND), Length=9
Advertiser Address: 12 34 56 78 9A BC
ADV Data: 02 01 06 05 09 48 65 6C 6C 6F
          │  │  │  │  │  └─ "Hello" (Device Name)
          │  │  │  │  └─ Complete Local Name (Type 0x09)
          │  │  │  └─ Length (5 bytes)
          │  │  └─ LE General Discoverable + BR/EDR Not Supported
          │  └─ Flags (Type 0x01)
          └─ Length (2 bytes)
CRC: XX XX XX
```

**Why ADV Data format?**
- TLV (Type-Length-Value) structure allows flexible data
- Can contain: Name, UUID, Manufacturer Data, TX Power, etc.

---

## **6. CONNECTION ESTABLISHMENT (Step-by-Step)**

Now the detailed flow - similar to WiFi association!

### **Step 1: ADVERTISING (Peripheral broadcasts)**

```
Peripheral                                Scanner/Central
   │                                            │
   │──── ADV_IND on Ch 37 ────────────────────→│
   │     [Device Name, Services, Flags]         │
   │                                            │
   │──── ADV_IND on Ch 38 ────────────────────→│
   │                                            │
   │──── ADV_IND on Ch 39 ────────────────────→│
   │                                            │
```

**Timing**: Peripheral sends ADV_IND on all 3 advertising channels
- **Advertising Interval**: 20ms - 10.24s (configurable)
- **Why multiple channels**: Increases discovery probability

### **Step 2: SCAN REQUEST/RESPONSE (Optional - Active Scanning)**

```
Peripheral                                Scanner/Central
   │                                            │
   │◄──── SCAN_REQ ─────────────────────────────│
   │      [Scanner Address]                     │
   │                                            │
   │──── SCAN_RSP ─────────────────────────────→│
   │     [Additional ADV Data]                  │
```

**SCAN_REQ Structure:**
```
┌──────────────────────────────────────────────────────────┐
│ Header: PDU Type=0011 (SCAN_REQ)                         │
├──────────────────────────────────────────────────────────┤
│ Scanner Address (6 bytes)                                │
├──────────────────────────────────────────────────────────┤
│ Advertiser Address (6 bytes) ← Who we're asking          │
└──────────────────────────────────────────────────────────┘
```

**Why SCAN_RSP?**
- ADV_IND limited to 31 bytes
- SCAN_RSP provides additional 31 bytes for more information

### **Step 3: CONNECTION REQUEST (Central initiates)**

This is BLE's "Association Request"!

```
Peripheral                                Scanner/Central
   │                                            │
   │◄──── CONNECT_REQ ──────────────────────────│
   │      [Connection Parameters]               │
   │                                            │
   │         [Connection Established]           │
   │                                            │
```

**CONNECT_REQ Structure (most important packet!):**

```
┌──────────────────────────────────────────────────────────┐
│ Header: PDU Type=0101 (CONNECT_REQ), Length=34          │
├──────────────────────────────────────────────────────────┤
│ Initiator Address (6 bytes) ← Central's address         │
├──────────────────────────────────────────────────────────┤
│ Advertiser Address (6 bytes) ← Peripheral's address     │
├──────────────────────────────────────────────────────────┤
│ LLData (22 bytes) - Connection Parameters:               │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Access Address (4 B) ← New unique AA for connection│ │
│  ├────────────────────────────────────────────────────┤ │
│  │ CRC Init (3 B) ← CRC initialization value          │ │
│  ├────────────────────────────────────────────────────┤ │
│  │ WinSize (1 B) ← Transmit window size               │ │
│  ├────────────────────────────────────────────────────┤ │
│  │ WinOffset (2 B) ← Transmit window offset           │ │
│  ├────────────────────────────────────────────────────┤ │
│  │ Interval (2 B) ← Connection interval               │ │
│  ├────────────────────────────────────────────────────┤ │
│  │ Latency (2 B) ← Peripheral latency                 │ │
│  ├────────────────────────────────────────────────────┤ │
│  │ Timeout (2 B) ← Supervision timeout                │ │
│  ├────────────────────────────────────────────────────┤ │
│  │ ChM (5 B) ← Channel Map (37 data channels)         │ │
│  ├────────────────────────────────────────────────────┤ │
│  │ Hop (5 bits) | SCA (3 bits) ← Frequency hopping   │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

**Parameter Details:**

| Parameter | Bytes | Purpose | Typical Values |
|-----------|-------|---------|----------------|
| **Access Address** | 4 | Unique connection ID | Random 32-bit value |
| **CRC Init** | 3 | CRC seed value | Random 24-bit value |
| **WinSize** | 1 | First packet timing window | 1.25ms - 10ms |
| **WinOffset** | 2 | Delay before first packet | 0 - 10ms |
| **Interval** | 2 | Time between connection events | 7.5ms - 4s (1.25ms units) |
| **Latency** | 2 | Peripheral can skip N events | 0 - 499 |
| **Timeout** | 2 | Connection supervision timeout | 100ms - 32s (10ms units) |
| **ChM** | 5 | Which data channels to use | 37-bit bitmap |
| **Hop** | 5 bits | Hop increment | 5 - 16 |
| **SCA** | 3 bits | Sleep clock accuracy | 0-7 (PPM ranges) |

**Why these parameters?**
- **Interval**: Power optimization (longer = less power, more latency)
- **Latency**: Peripheral can sleep through connection events
- **Timeout**: Detect dead connections
- **Channel Map**: Avoid interference from WiFi or other BLE devices
- **Hop**: Frequency hopping spread spectrum (FHSS) for robustness

### **Step 4: CONNECTION (Data Channel Phase)**

After CONNECT_REQ, devices switch from advertising channels to data channels!

```
Connection Event Timing:
────────────────────────────────────────────────────────
       │<─── Connection Interval ───→│
       │                             │
  ┌────┴────┐                   ┌────┴────┐
  │ Event 0 │                   │ Event 1 │
  └─────────┘                   └─────────┘
       │                             │
       ├→ Central sends packet       ├→ Central sends
       └→ Peripheral responds        └→ Peripheral responds
```

**Frequency Hopping:**
- Each connection event uses a different data channel
- Algorithm: `unmapped_channel = (lastChannel + hop) mod 37`
- Then map to enabled channels based on ChM

---

## **7. DATA PACKETS (Connected State)**

Once connected, devices exchange data using LL Data PDUs.

### **7.1 Data PDU Types (LLID Field)**

In connected state, PDU Type field becomes LLID (Link Layer Identifier):

| LLID | Binary | Name | Purpose |
|------|--------|------|---------|
| 00 | Reserved | N/A | Invalid |
| 01 | **LL Data** (continuation) | Data packet continuation | Multi-packet L2CAP data |
| 10 | **LL Data** (start) | Data packet start | First packet of L2CAP PDU |
| 11 | **LL Control** | Control packet | Link layer control (keep-alive, encryption, etc.) |

### **7.2 LL Data Packet Structure**

```
┌──────────────────────────────────────────────────────────┐
│                    LINK LAYER HEADER                     │
│  LLID: 01/10 | NESN | SN | MD | Length                  │
├──────────────────────────────────────────────────────────┤
│                    L2CAP PAYLOAD                         │
│                    (0-251 bytes)                         │
└──────────────────────────────────────────────────────────┘
```

**Header Bits (Connected State):**

```
┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
│ 15 │ 14 │ 13 │ 12 │ 11 │ 10 │  9 │  8 │  7 │  6 │  5 │  4 │  3 │  2 │  1 │  0 │
├────┴────┼────┼────┼────┼────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┤
│  LLID   │NESN│ SN │ MD │              Length (8 bits)                          │
│  (2b)   │(1b)│(1b)│(1b)│                                                       │
└─────────┴────┴────┴────┴───────────────────────────────────────────────────────┘
```

| Field | Bits | Purpose |
|-------|------|---------|
| **LLID** | 2 | Packet type (Data/Control) |
| **NESN** | 1 | Next Expected Sequence Number (ACK mechanism) |
| **SN** | 1 | Sequence Number (for this packet) |
| **MD** | 1 | More Data flag (1 = more packets coming) |
| **Length** | 8 | Payload length |

**Why NESN/SN?**
- Simple ARQ (Automatic Repeat Request) protocol
- NESN tells sender which packet to send next
- SN identifies current packet
- If NESN doesn't increment, sender retransmits

### **7.3 LL Control Packets**

Control packets manage the connection:

| Opcode | Name | Purpose |
|--------|------|---------|
| 0x00 | **LL_CONNECTION_UPDATE_IND** | Change connection parameters |
| 0x01 | **LL_CHANNEL_MAP_IND** | Update channel map |
| 0x02 | **LL_TERMINATE_IND** | Disconnect |
| 0x03 | **LL_ENC_REQ** | Start encryption (like EAPOL!) |
| 0x04 | **LL_ENC_RSP** | Encryption response |
| 0x05 | **LL_START_ENC_REQ** | Begin encrypted communication |
| 0x06 | **LL_START_ENC_RSP** | Confirm encryption started |
| 0x07 | **LL_UNKNOWN_RSP** | Unknown opcode response |
| 0x08 | **LL_FEATURE_REQ** | Query supported features |
| 0x09 | **LL_FEATURE_RSP** | Feature response |
| 0x0A | **LL_PAUSE_ENC_REQ** | Pause encryption |
| 0x0B | **LL_PAUSE_ENC_RSP** | Confirm encryption paused |
| 0x0C | **LL_VERSION_IND** | Exchange version info |
| 0x0D | **LL_REJECT_IND** | Reject request |
| 0x0E | **LL_PERIPHERAL_FEATURE_REQ** | Peripheral requests features |
| 0x0F | **LL_CONNECTION_PARAM_REQ** | Request parameter change |
| 0x10 | **LL_CONNECTION_PARAM_RSP** | Parameter change response |
| 0x11 | **LL_REJECT_EXT_IND** | Extended reject |
| 0x12 | **LL_PING_REQ** | Keep-alive ping |
| 0x13 | **LL_PING_RSP** | Ping response |
| 0x14 | **LL_LENGTH_REQ** | Request DLE (Data Length Extension) |
| 0x15 | **LL_LENGTH_RSP** | DLE response |

---

## **8. L2CAP LAYER (Logical Link Control)**

L2CAP sits above Link Layer and handles:
- Packet fragmentation/reassembly
- Protocol multiplexing
- QoS

### **8.1 L2CAP Packet Structure**

```
┌──────────────────────────────────────────────────────────┐
│                    L2CAP HEADER (4 bytes)                │
│  ┌──────────────────────┬──────────────────────────────┐ │
│  │  Length (2 bytes)    │  Channel ID (2 bytes)        │ │
│  └──────────────────────┴──────────────────────────────┘ │
├──────────────────────────────────────────────────────────┤
│                    L2CAP PAYLOAD                         │
│              (ATT/SMP/Signaling data)                    │
└──────────────────────────────────────────────────────────┘
```

**Channel IDs:**
| CID | Hex | Purpose |
|-----|-----|---------|
| 0x0000 | 0x0000 | Null (invalid) |
| 0x0001 | 0x0001 | ACL-U Signaling channel |
| 0x0002 | 0x0002 | Connectionless channel |
| 0x0003 | 0x0003 | AMP Manager |
| 0x0004 | 0x0004 | **ATT Protocol** ← GATT uses this! |
| 0x0005 | 0x0005 | LE-U Signaling channel |
| 0x0006 | 0x0006 | **SMP (Security Manager)** ← Pairing! |
| 0x0007 | 0x0007 | BR/EDR SMP |
| 0x0040-0xFFFF | - | Dynamically allocated |

**Why L2CAP?**
- Link Layer has 27-byte max payload (BLE 4.2)
- L2CAP allows larger payloads by fragmenting/reassembling
- Routes packets to correct upper-layer protocol

---

## **9. ATT LAYER (Attribute Protocol)**

ATT is how data is actually read/written in BLE!

### **9.1 ATT PDU Structure**

```
┌──────────────────────────────────────────────────────────┐
│  Opcode (1 byte) ← Command type                          │
├──────────────────────────────────────────────────────────┤
│  Parameters (variable) ← Handle, Value, etc.             │
└──────────────────────────────────────────────────────────┘
```

### **9.2 ATT Opcodes**

| Opcode | Name | Direction | Purpose |
|--------|------|-----------|---------|
| 0x01 | **Error Response** | Server→Client | Error occurred |
| 0x02 | **Exchange MTU Request** | Client→Server | Negotiate max packet size |
| 0x03 | **Exchange MTU Response** | Server→Client | MTU response |
| 0x04 | **Find Information Request** | Client→Server | Discover attributes |
| 0x05 | **Find Information Response** | Server→Client | Attribute info |
| 0x08 | **Find By Type Value Request** | Client→Server | Find specific attributes |
| 0x09 | **Find By Type Value Response** | Server→Client | Found attributes |
| 0x0A | **Read By Type Request** | Client→Server | Read attributes by UUID |
| 0x0B | **Read By Type Response** | Server→Client | Attribute values |
| 0x0C | **Read Request** | Client→Server | Read single attribute |
| 0x0D | **Read Response** | Server→Client | Attribute value |
| 0x0E | **Read Blob Request** | Client→Server | Read long attribute |
| 0x0F | **Read Blob Response** | Server→Client | Attribute chunk |
| 0x12 | **Write Request** | Client→Server | Write with response |
| 0x13 | **Write Response** | Server→Client | Write acknowledged |
| 0x1B | **Handle Value Notification** | Server→Client | Notify changed value |
| 0x1D | **Handle Value Indication** | Server→Client | Indicate changed value |
| 0x1E | **Handle Value Confirmation** | Client→Server | Confirm indication |
| 0x52 | **Write Command** | Client→Server | Write without response |

**Example: Read Request**
```
Opcode: 0x0A (Read By Type Request)
Start Handle: 0x0001 (2 bytes)
End Handle: 0xFFFF (2 bytes)
UUID: 0x2803 (2 bytes) ← Characteristic Declaration UUID
```

**Why ATT?**
- Provides standardized read/write operations
- Handle-based addressing (attributes have numeric handles)
- Notification/Indication mechanism for server-pushed data

---

## **10. GATT LAYER (Generic Attribute Profile)**

GATT builds on ATT and defines how data is organized!

### **10.1 GATT Hierarchy**

```
Profile
 │
 ├─ Service (e.g., Heart Rate Service)
 │   ├─ Characteristic (e.g., Heart Rate Measurement)
 │   │   ├─ Value
 │   │   ├─ Descriptor (e.g., Client Characteristic Config)
 │   │   └─ Descriptor (e.g., Characteristic User Description)
 │   │
 │   └─ Characteristic (e.g., Body Sensor Location)
 │       ├─ Value
 │       └─ Descriptor
 │
 └─ Service (e.g., Battery Service)
     └─ Characteristic (e.g., Battery Level)
         ├─ Value
         └─ Descriptor
```

**Example: Heart Rate Service**
```
Handle | UUID   | Type           | Value
-------+--------+----------------+---------------------------
0x0001 | 0x2800 | Primary Service| 0x180D (Heart Rate)
0x0002 | 0x2803 | Characteristic | Properties + Handle + UUID
0x0003 | 0x2A37 | Value          | Heart rate measurement data
0x0004 | 0x2902 | Descriptor     | Client Characteristic Config
0x0005 | 0x2803 | Characteristic | Properties + Handle + UUID
0x0006 | 0x2A38 | Value          | Body sensor location
```

**Service Discovery Flow:**

```
Client                                    Server (Peripheral)
  │                                             │
  │─── Read By Group Type (Services) ─────────→│
  │                                             │
  │←── Response: Service 1 (0x180D), etc. ─────│
  │                                             │
  │─── Read By Type (Characteristics) ────────→│
  │                                             │
  │←── Response: Char 1, Char 2, etc. ─────────│
  │                                             │
  │─── Read (Descriptor) ──────────────────────→│
  │                                             │
  │←── Response: Descriptor value ──────────────│
```

---

## **11. BLE SECURITY & PAIRING (BLE's WPA2!)**

### **11.1 Security Manager Protocol (SMP)**

SMP handles pairing and encryption - runs on L2CAP channel 0x0006.

### **11.2 Pairing Methods**

| Method | Security Level | Requirements |
|--------|----------------|--------------|
| **Just Works** | Low | No user interaction |
| **Passkey Entry** | Medium | 6-digit PIN |
| **Out of Band** | High | NFC, QR code, etc. |
| **Numeric Comparison** | High | User compares 6-digit number |

### **11.3 Pairing Flow (LE Legacy Pairing)**

```
Central                                  Peripheral
  │                                            │
  │─── LL_ENC_REQ ────────────────────────────→│ (Start encryption)
  │    [Random, EDIV, SKD, IV]                 │
  │                                            │
  │←── LL_ENC_RSP ─────────────────────────────│
  │    [Random, EDIV, SKD, IV]                 │
  │                                            │
  │─── Pairing Request ───────────────────────→│ (SMP on L2CAP CID 0x06)
  │    [IO Cap, OOB, Auth Req, etc.]           │
  │                                            │
  │←── Pairing Response ───────────────────────│
  │    [IO Cap, OOB, Auth Req, etc.]           │
  │                                            │
  │─── Pairing Confirm ───────────────────────→│
  │    [Confirm Value]                         │
  │                                            │
  │←── Pairing Confirm ────────────────────────│
  │    [Confirm Value]                         │
  │                                            │
  │─── Pairing Random ────────────────────────→│
  │    [Random Value]                          │
  │                                            │
  │←── Pairing Random ─────────────────────────│
  │    [Random Value]                          │
  │                                            │
  │  [Both devices compute STK (Short Term Key)]│
  │                                            │
  │─── LL_START_ENC_REQ ──────────────────────→│
  │                                            │
  │←── LL_START_ENC_RSP ───────────────────────│
  │                                            │
  │  [Encrypted communication begins]          │
```

### **11.4 LE Secure Connections (BLE 4.2+)**

Uses ECDH (Elliptic Curve Diffie-Hellman) - much more secure!

```
Central                                  Peripheral
  │                                            │
  │─── Pairing Request ───────────────────────→│
  │    [IO Cap, OOB, Auth Req, SC=1]           │
  │                                            │
  │←── Pairing Response ───────────────────────│
  │    [IO Cap, OOB, Auth Req, SC=1]           │
  │                                            │
  │─── Pairing Public Key ────────────────────→│
  │    [PKa - ECDH Public Key]                 │
  │                                            │
  │←── Pairing Public Key ─────────────────────│
  │    [PKb - ECDH Public Key]                 │
  │                                            │
  │  [Both compute DHKey using ECDH]           │
  │                                            │
  │─── Pairing Confirm ───────────────────────→│
  │                                            │
  │←── Pairing Confirm ────────────────────────│
  │                                            │
  │─── Pairing Random ────────────────────────→│
  │                                            │
  │←── Pairing Random ─────────────────────────│
  │                                            │
  │─── Pairing DHKey Check ───────────────────→│
  │                                            │
  │←── Pairing DHKey Check ────────────────────│
  │                                            │
  │  [LTK derived, encryption enabled]         │
```

**Encryption Details:**
- **Algorithm**: AES-CCM (Counter with CBC-MAC)
- **Key Size**: 128-bit (Legacy) or 128/192/256-bit (SC)
- **Keys**:
  - **LTK** (Long Term Key): Main encryption key
  - **IRK** (Identity Resolving Key): For privacy (resolvable addresses)
  - **CSRK** (Connection Signature Resolving Key): For data signing

---

## **12. COMPLETE CONNECTION FLOW WITH ALL LAYERS**

Let me show you a complete transaction from advertising to encrypted data transfer:

```
Time  | Link Layer            | L2CAP      | ATT/GATT        | Purpose
------+-----------------------+------------+-----------------+------------------
T0    | ADV_IND               | -          | -               | Peripheral advertises
T1    | SCAN_REQ              | -          | -               | Central requests more info
T2    | SCAN_RSP              | -          | -               | Peripheral responds
T3    | CONNECT_REQ           | -          | -               | Central requests connection
T4    | LL_FEATURE_REQ        | -          | -               | Query supported features
T5    | LL_FEATURE_RSP        | -          | -               | Feature response
T6    | LL_VERSION_IND        | -          | -               | Version exchange
T7    | LL_VERSION_IND        | -          | -               | Version exchange
T8    | Data (LLID=10)        | MTU Req    | 0x02 (MTU)      | Negotiate max packet size
T9    | Data (LLID=10)        | MTU Rsp    | 0x03 (MTU)      | MTU response
T10   | Data (LLID=10)        | GATT Req   | 0x10 (Read)     | Service discovery starts
T11   | Data (LLID=10)        | GATT Rsp   | 0x11 (Read)     | Services returned
T12   | LL_ENC_REQ            | -          | -               | Start encryption
T13   | LL_ENC_RSP            | -          | -               | Encryption response
T14   | Data (LLID=10)        | Pair Req   | SMP             | Pairing request
T15   | Data (LLID=10)        | Pair Rsp   | SMP             | Pairing response
T16   | Data (LLID=10)        | Pair Cfm   | SMP             | Pairing confirm
T17   | Data (LLID=10)        | Pair Cfm   | SMP             | Pairing confirm
T18   | Data (LLID=10)        | Pair Rnd   | SMP             | Pairing random
T19   | Data (LLID=10)        | Pair Rnd   | SMP             | Pairing random
T20   | LL_START_ENC_REQ      | -          | -               | Begin encryption
T21   | LL_START_ENC_RSP      | -          | -               | Confirm encryption
T22   | Data [Encrypted]      | GATT Req   | 0x0A (Read)     | Read characteristic
T23   | Data [Encrypted]      | GATT Rsp   | 0x0B (Read)     | Characteristic value
T24   | Data [Encrypted]      | GATT Req   | 0x12 (Write)    | Write characteristic
T25   | Data [Encrypted]      | GATT Rsp   | 0x13 (Write)    | Write acknowledged
T26   | Data [Encrypted]      | GATT Ntf   | 0x1B (Notify)   | Server pushes data
```

---

## **13. COMPARISON: BLE vs WiFi**

| Aspect | WiFi | BLE |
|--------|------|-----|
| **Discovery** | Beacon frames (AP broadcasts) | ADV_IND packets (Peripheral broadcasts) |
| **Scan** | Probe Request/Response | SCAN_REQ/SCAN_RSP |
| **Association** | Auth + Assoc Request/Response | CONNECT_REQ |
| **Handshake** | EAPOL 4-way handshake | LL_ENC_REQ/RSP + SMP pairing |
| **Data Transfer** | QoS Data frames | LL Data PDUs (LLID=01/10) |
| **Channels** | 14 channels (2.4 GHz) | 40 channels (3 adv + 37 data) |
| **Frequency** | Fixed channel | Frequency hopping |
| **Addressing** | MAC address (6 bytes) | BD_ADDR (6 bytes) |
| **Fragmentation** | 802.11 fragmentation | L2CAP fragmentation |
| **Upper Layer** | TCP/IP, UDP | GATT/ATT |
| **Max Payload** | ~2300 bytes | 27-251 bytes (depending on version) |
| **Power** | High | Ultra-low |

---

## **14. ATTACK SURFACES FOR YOUR ML RESEARCH**

Based on the protocol breakdown, here are the attack categories:

### **14.1 Advertising Phase Attacks**
| Attack | Target | Similar to WiFi |
|--------|--------|-----------------|
| **Flooding** | Spam ADV_IND packets | Beacon flooding |
| **Spoofing** | Fake advertising devices | Rogue AP |
| **Selective jamming** | Jam advertising channels 37/38/39 | Deauth attack |

### **14.2 Connection Phase Attacks**
| Attack | Target | Similar to WiFi |
|--------|--------|-----------------|
| **Connection flood** | Spam CONNECT_REQ | Association flood |
| **MITM** | Intercept CONNECT_REQ, modify parameters | Evil Twin |
| **Denial of connection** | Jam connection establishment | Deauth/Disassoc |

### **14.3 Data Phase Attacks**
| Attack | Target | Similar to WiFi |
|--------|--------|-----------------|
| **Jamming** | Prevent communication | Data frame jamming |
| **Sniffing** | Capture unencrypted data | Packet sniffing |
| **Injection** | Inject malicious LL Control packets | Frame injection |
| **Disconnect** | Send LL_TERMINATE_IND | Deauth |

### **14.4 Security Attacks**
| Attack | Target | Similar to WiFi |
|--------|--------|-----------------|
| **Downgrade** | Force Legacy Pairing | WPA→WEP downgrade |
| **MITM pairing** | Intercept pairing process | EAPOL MITM |
| **Brute-force** | Crack 6-digit passkey | WPA handshake crack |

---

## **15. TOOLS FOR BLE RESEARCH**

### **Ubertooth One:**
```bash
# Sniff advertising packets
ubertooth-btle -f -c adv_channel.pcap

# Follow connection
ubertooth-btle -f -t AA:BB:CC:DD:EE:FF

# Jam connections
ubertooth-btle -j
```

### **Built-in Bluetooth:**
```bash
# Scan for devices
sudo hcitool lescan

# Get device info
sudo hcitool leinfo AA:BB:CC:DD:EE:FF

# Connect to device
sudo gatttool -b AA:BB:CC:DD:EE:FF -I

# Sniff HCI traffic
sudo btmon -w capture.log
```

### **Bettercap:**
```bash
# BLE recon
sudo bettercap -eval "ble.recon on"

# Show devices
ble.show

# Enumerate services
ble.enum AA:BB:CC:DD:EE:FF
```

---

Alright, that's the comprehensive BLE breakdown! 

**Want me to:**
1. Dive deeper into any specific section?
2. Show you actual packet captures (hex dumps)?
3. Create attack scripts for specific vulnerabilities?
4. Compare BLE 4.x vs 5.x differences?
5. Explain LoRa or Zigbee next?

What's your next move? 🎯


---

**Related**:
- [[BLE/README|BLE Home]]
- [[BLE/DoS/01-dos-attack-theory|DoS Attack Analysis]]
- [[BLE/Scripting/01-packet-crafting-basics|Packet Crafting Basics]]
- [[README|Home]] • [[INDEX|Full Index]]
