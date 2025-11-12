```markdown
# BLE Protocol Headers Reference for DoS Testing
## Quick Reference Cheat-Sheet for Packet Crafting

> **Purpose:** This guide provides a structured reference of all BLE protocol layers and their exploitable header fields for DoS attack implementation and security testing.

---

## Table of Contents
1. [Link Layer Headers](#1-link-layer-headers)
2. [HCI Layer Headers](#2-hci-layer-headers)
3. [L2CAP Layer Headers](#3-l2cap-layer-headers)
4. [ATT/GATT Layer Headers](#4-attgatt-layer-headers)
5. [SMP Layer Headers](#5-smp-layer-headers)
6. [GAP Layer Headers](#6-gap-layer-headers)
7. [Attack Vector Mapping](#7-attack-vector-mapping)
8. [Exploitation Knobs](#8-exploitation-knobs)

---

## 1. Link Layer Headers

### 1.1 Advertising PDU

| Field | Size (bits) | Format | Values | Exploitation Notes |
|-------|-------------|--------|--------|-------------------|
| **PDU Type** | 4 | Binary | `0x0`=ADV_IND, `0x1`=ADV_DIRECT_IND, `0x2`=ADV_NONCONN_IND, `0x3`=SCAN_REQ, `0x4`=SCAN_RSP, `0x6`=CONNECT_IND | Change type rapidly for flood variants |
| **RFU** | 2 | Binary | Reserved (set to 0) | Set to non-zero for fuzzing |
| **TxAdd** | 1 | Binary | `0`=Public, `1`=Random | Toggle for address type confusion |
| **RxAdd** | 1 | Binary | `0`=Public, `1`=Random | Used in CONNECT_IND, SCAN_REQ |
| **Length** | 6 | Binary | 6-37 (legacy), up to 255 (extended) | Max length (37) for resource exhaustion |
| **AdvAddr** | 48 | MAC Address | 6 bytes | Rotate addresses to bypass duplicate filtering |
| **AdvData** | 0-248 | Binary | AD structures | Max size (31 bytes legacy) for memory stress |

**Byte Structure:**
```
Byte 0:    [PDU Type:4][RFU:2][TxAdd:1][RxAdd:1]
Byte 1:    [Length:6][RFU:2]
Bytes 2-7: AdvAddr (6 bytes)
Bytes 8-N: AdvData (0-31 bytes legacy)
```

**Python Crafting:**
```python
header = (pdu_type << 0) | (tx_add << 6) | (rx_add << 7)
pdu = struct.pack('<BB', header, length) + adv_addr + adv_data
```

---

### 1.2 Data Channel PDU (ACL)

| Field | Size (bits) | Format | Values | Exploitation Notes |
|-------|-------------|--------|--------|-------------------|
| **LLID** | 2 | Binary | `0x1`=LL Data (continuation), `0x2`=LL Data (start), `0x3`=LL Control PDU | Empty packets (LLID=0x1, Length=0) |
| **NESN** | 1 | Binary | Next Expected Sequence Number | Fix at 1 to never ACK victim |
| **SN** | 1 | Binary | Sequence Number | Fix at 0 to force retransmissions |
| **MD** | 1 | Binary | More Data flag | Set to 1 to keep victim listening |
| **RFU** | 3 | Binary | Reserved | Set non-zero for fuzzing |
| **Length** | 8 | Binary | 0-251 bytes | Max (251) for resource exhaustion |
| **Payload** | 0-2008 | Binary | Up to 251 bytes | Malformed L2CAP/ATT within |

**Byte Structure:**
```
Bytes 0-1: [LLID:2][NESN:1][SN:1][MD:1][RFU:3][Length:8]
Bytes 2-N: Payload (0-251 bytes)
```

**Python Crafting:**
```python
header = (llid << 0) | (nesn << 2) | (sn << 3) | (md << 4) | (length << 8)
pdu = struct.pack('<H', header) + payload
```

**C++ Crafting:**
```cpp
uint16_t header = (llid & 0x3) | ((nesn & 0x1) << 2) | ((sn & 0x1) << 3) | ((md & 0x1) << 4) | (length << 8);
```

---

### 1.3 Connect Request PDU

| Field | Size (bits) | Format | Values | Exploitation Notes |
|-------|-------------|--------|--------|-------------------|
| **Access Address** | 32 | Binary | Randomly generated | Craft deterministic values for tracking |
| **CRCInit** | 24 | Binary | CRC initialization | Invalid values may crash parsers |
| **WinSize** | 8 | Binary | Transmit window size (1.25ms units) | Min (1) or max (255) for timing issues |
| **WinOffset** | 16 | Binary | Transmit window offset | Extreme values for collision |
| **Interval** | 16 | Binary | Connection interval (1.25ms units) | Min (6=7.5ms) or max (3200=4s) |
| **Latency** | 16 | Binary | Slave latency (events) | Max (499) for delayed responses |
| **Timeout** | 16 | Binary | Supervision timeout (10ms units) | Min (10=100ms) for quick drops |
| **Channel Map** | 40 | Binary | 37 data channels bitmap | All 0s (invalid) or all 1s (stress) |
| **Hop** | 5 | Binary | Hop increment | 0 or extreme values |
| **SCA** | 3 | Binary | Sleep clock accuracy | Non-standard values |

**Total Size:** 22 bytes (after AdvAddr in CONNECT_IND PDU)

**Python Crafting:**
```python
connect_req = struct.pack('<IIHHHHHQHB',
    access_addr,    # 32 bits
    crc_init,       # 24 bits (as 32, use lower 24)
    win_size,       # 8 bits
    win_offset,     # 16 bits
    interval,       # 16 bits
    latency,        # 16 bits
    timeout,        # 16 bits
    channel_map,    # 40 bits (as 64, use lower 40)
    hop_sca         # Hop (5) + SCA (3) = 8 bits
)
```

---

## 2. HCI Layer Headers

### 2.1 HCI Command Packet

| Field | Size (bytes) | Format | Values | Exploitation Notes |
|-------|--------------|--------|--------|-------------------|
| **Packet Type** | 1 | Hex | `0x01` (Command) | Always 0x01 for commands |
| **OpCode** | 2 | Hex (LE) | OGF (6 bits) + OCF (10 bits) | See OpCode table below |
| **Param Length** | 1 | Decimal | 0-255 | Mismatch with actual params for fuzzing |
| **Parameters** | 0-255 | Binary | Command-specific | Malformed values |

**OpCode Calculation:**
```python
opcode = (ogf << 10) | ocf
```

**Common OpCodes for Attacks:**

| OpCode | OGF | OCF | Name | Exploitation |
|--------|-----|-----|------|--------------|
| 0x200A | 0x08 | 0x000A | LE Set Advertising Enable | Rapid toggle for adv flood |
| 0x2008 | 0x08 | 0x0008 | LE Set Advertising Data | Change AdvData rapidly |
| 0x200D | 0x08 | 0x000D | LE Create Connection | Connection exhaustion |
| 0x2006 | 0x08 | 0x0006 | LE Set Scan Parameters | Scanner exhaustion |
| 0x0C03 | 0x03 | 0x0003 | Reset | Force controller reset (self-DoS) |
| 0x2016 | 0x08 | 0x0016 | LE Read Remote Features | Trigger feature exchange storm |

**Python Crafting:**
```python
opcode = (ogf << 10) | ocf
cmd = struct.pack('<BHB', 0x01, opcode, len(params)) + params
```

---

### 2.2 HCI Event Packet

| Field | Size (bytes) | Format | Values | Exploitation Notes |
|-------|--------------|--------|--------|-------------------|
| **Packet Type** | 1 | Hex | `0x04` (Event) | Always 0x04 for events |
| **Event Code** | 1 | Hex | Various | Monitor for errors (0x0F=Command Status) |
| **Param Length** | 1 | Decimal | 0-255 | - |
| **Parameters** | 0-255 | Binary | Event-specific | Parse for attack feedback |

**Key Event Codes:**

| Code | Name | Use in Attacks |
|------|------|----------------|
| 0x0E | Command Complete | Verify command success |
| 0x0F | Command Status | Check for errors/NACKs |
| 0x05 | Disconnection Complete | Detect victim disconnect |
| 0x3E | LE Meta Event | LE-specific events (connection, advertising) |

---

### 2.3 HCI ACL Data Packet

| Field | Size (bytes) | Format | Values | Exploitation Notes |
|-------|--------------|--------|--------|-------------------|
| **Packet Type** | 1 | Hex | `0x02` (ACL Data) | Always 0x02 for ACL |
| **Handle** | 2 (12 bits) | Hex (LE) | Connection handle | Target specific connection |
| **PB Flag** | 2 bits | Binary | `0x2`=First, `0x1`=Continuing, `0x0`=Continuation, `0x3`=Complete | Send continuing without first for reassembly DoS |
| **BC Flag** | 2 bits | Binary | `0x0`=Point-to-point, `0x1`=Active Broadcast | Unused in LE typically |
| **Data Total Length** | 2 | Decimal (LE) | 0-65535 | Declare large, send small (length mismatch) |
| **Data** | 0-65535 | Binary | L2CAP packet | Malformed L2CAP within |

**Handle + Flags Packing:**
```python
handle_flags = (handle & 0x0FFF) | ((pb_flag & 0x3) << 12) | ((bc_flag & 0x3) << 14)
packet = struct.pack('<BHH', 0x02, handle_flags, data_length) + data
```

**Fragmentation Attack:**
```python
# Send continuing fragments without initial fragment
pb_flag = 0x1  # Continuing
# Victim allocates reassembly buffer indefinitely
```

---

## 3. L2CAP Layer Headers

### 3.1 L2CAP Basic Header

| Field | Size (bytes) | Format | Values | Exploitation Notes |
|-------|--------------|--------|--------|-------------------|
| **Length** | 2 | Decimal (LE) | 0-65535 | Declare 65535, send 10 (mismatch attack) |
| **Channel ID (CID)** | 2 | Hex (LE) | See CID table | Target specific channels |

**L2CAP CIDs:**

| CID | Channel | Protocol | Attack Target |
|-----|---------|----------|---------------|
| **0x0004** | ATT | Attribute Protocol | **Primary DoS target (GATT floods)** |
| **0x0005** | Signaling | LE L2CAP Signaling | **Param update storms** |
| **0x0006** | SMP | Security Manager | **Pairing abuse** |
| 0x0040-0x007F | Dynamic | Credit-Based | Credit exhaustion |

**Python Crafting:**
```python
l2cap_header = struct.pack('<HH', length, cid)
l2cap_packet = l2cap_header + payload
```

---

### 3.2 L2CAP Signaling Header

| Field | Size (bytes) | Format | Values | Exploitation Notes |
|-------|--------------|--------|--------|-------------------|
| **Code** | 1 | Hex | Command type | See Signaling Codes table |
| **Identifier** | 1 | Decimal | 1-255 | Increment for each request (match req/resp) |
| **Length** | 2 | Decimal (LE) | 0-65535 | Length of Command Data |
| **Command Data** | 0-65535 | Binary | Code-specific | Malformed parameters |

**Signaling Command Codes:**

| Code | Name | Exploitation |
|------|------|--------------|
| **0x12** | Connection Parameter Update Request | **Rapid requests with extreme params** |
| 0x13 | Connection Parameter Update Response | - |
| 0x14 | LE Credit Based Connection Request | Exhaust credit-based channels |
| 0x15 | LE Credit Based Connection Response | - |
| 0x16 | LE Flow Control Credit | Manipulate credits |

**Connection Parameter Update Request Structure:**
```python
code = 0x12
identifier = 1  # Increment per request
params = struct.pack('<HHHH', 
    interval_min,  # 7.5ms = 0x0006
    interval_max,  # 4s = 0x0C80 (conflicting!)
    latency,       # 499 = 0x01F3 (max)
    timeout        # 100ms = 0x000A (min)
)
signaling_pdu = struct.pack('<BBH', code, identifier, len(params)) + params
```

---

## 4. ATT/GATT Layer Headers

### 4.1 ATT PDU Header

| Field | Size (bytes) | Format | Values | Exploitation Notes |
|-------|--------------|--------|--------|-------------------|
| **Opcode** | 1 | Hex | Request/Response/Command/Notification | See ATT Opcodes table |
| **Attribute Handle** | 2 (optional) | Hex (LE) | 0x0001-0xFFFF | Target specific characteristics |
| **Value/Params** | 0-512 | Binary | Opcode-dependent | Max MTU (512 bytes) for floods |

**Critical ATT Opcodes:**

| Opcode | Method | Name | Request/Response | Exploitation |
|--------|--------|------|------------------|--------------|
| **0x52** | Command | **Write Command** | **No response required** | **PRIMARY DoS (max rate floods)** |
| 0x12 | Request | Write Request | Response required (0x13) | Queue exhaustion (victim must respond) |
| 0x0A | Request | Read Request | Response required (0x0B) | Force data retrieval repeatedly |
| **0x1B** | Notification | Handle Value Notification | No confirm required | **Notification storm (peripheral → central)** |
| 0x1D | Indication | Handle Value Indication | Confirm required (0x1E) | Indication flood (requires confirm) |
| 0x02 | Request | Exchange MTU Request | Response required | MTU negotiation abuse |
| 0x08 | Request | Read By Type Request | Response required | Service discovery flood |

**Write Command (0x52) - Primary Attack Vector:**
```python
opcode = 0x52
handle = 0x0010  # Target characteristic
value = b'\xFF' * 512  # Max MTU payload
att_pdu = struct.pack('<BH', opcode, handle) + value
```

**Wrap in L2CAP:**
```python
l2cap_packet = struct.pack('<HH', len(att_pdu), 0x0004) + att_pdu
```

---

### 4.2 GATT Operations (Application View)

| GATT Operation | ATT Opcode | Response | Handle Required | Exploitation |
|----------------|-----------|----------|-----------------|--------------|
| **Write Without Response** | 0x52 | No | Yes | **Highest DoS potential (no flow control)** |
| Write | 0x12 | Yes (0x13) | Yes | Queue exhaustion |
| Read | 0x0A | Yes (0x0B) | Yes | Force data retrieval |
| **Notify** | 0x1B | No | Yes | **Storm clients (if peripheral role)** |
| Indicate | 0x1D | Yes (0x1E) | Yes | Confirmation queue exhaustion |
| Discover Services | 0x10 | Yes (0x11) | No | Service enumeration abuse |

---

## 5. SMP Layer Headers

### 5.1 SMP PDU Header

| Field | Size (bytes) | Format | Values | Exploitation Notes |
|-------|--------------|--------|--------|-------------------|
| **Code** | 1 | Hex | Pairing command type | See SMP Codes table |
| **Payload** | 0-64 | Binary | Code-specific | Malformed crypto parameters |

**SMP Command Codes:**

| Code | Name | Payload Size | Exploitation |
|------|------|--------------|--------------|
| **0x01** | **Pairing Request** | 6 bytes | **Repeated requests without completion** |
| 0x02 | Pairing Response | 6 bytes | Malformed parameters |
| 0x03 | Pairing Confirm | 16 bytes | Invalid confirm values |
| 0x04 | Pairing Random | 16 bytes | Nonce manipulation |
| 0x05 | Pairing Failed | 1 byte | Trigger error handling loops |
| **0x0C** | **Pairing Public Key** | 64 bytes | **Invalid elliptic curve points (crashes)** |
| 0x0D | Pairing DHKey Check | 16 bytes | DHKey check manipulation |

**Pairing Request Structure:**
```python
code = 0x01
io_capability = 0x03  # NoInputNoOutput (Just Works - weak)
oob_flag = 0x00       # No OOB
auth_req = 0x01       # Bonding only, no MITM
max_key_size = 0x07   # Minimum (7 bytes) - weak!
initiator_keys = 0x01 # EncKey
responder_keys = 0x01 # EncKey

smp_pdu = struct.pack('<BBBBBBB', code, io_capability, oob_flag, auth_req, 
                       max_key_size, initiator_keys, responder_keys)
```

**Wrap in L2CAP:**
```python
l2cap_packet = struct.pack('<HH', len(smp_pdu), 0x0006) + smp_pdu
```

**Invalid Public Key Attack:**
```python
code = 0x0C
# Public key X and Y (all zeros - not on curve)
invalid_key = b'\x00' * 64
smp_pdu = struct.pack('<B', code) + invalid_key
```

---

## 6. GAP Layer Headers

> **Note:** GAP is a profile layer (procedures), not a wire protocol. GAP procedures are implemented using Link Layer Advertising PDUs and GATT operations.

### 6.1 GAP Procedures to Wire Protocol Mapping

| GAP Procedure | Wire Protocol | Key Fields | Exploitation |
|---------------|--------------|------------|--------------|
| **Broadcasting** | LL Advertising PDU (ADV_NONCONN_IND) | PDU Type=0x2, AdvData | Broadcast flood |
| **Discovery** | LL Advertising PDU (SCAN_REQ/SCAN_RSP) | PDU Type=0x3/0x4 | Scan response amplification |
| **Connection Establishment** | LL Advertising PDU (ADV_IND → CONNECT_IND) | PDU Type=0x0 → 0x6 | Connection request flood |
| **Bonding** | SMP over L2CAP CID 0x0006 | SMP Code 0x01-0x0D | Pairing abuse |

**GAP Advertising Data (AD) Structures:**

| AD Type | Hex | Name | Size | Exploitation |
|---------|-----|------|------|--------------|
| 0x01 | Flags | Flags | 1-3 bytes | Invalid flag combinations |
| 0x02 | UUID16 (incomplete) | 16-bit UUIDs | Varies | Long lists for parsing stress |
| 0x03 | UUID16 (complete) | 16-bit UUIDs | Varies | - |
| 0x09 | Local Name (complete) | Device Name | Varies | Max length (31 bytes) |
| 0xFF | Manufacturer Data | Vendor-specific | Varies | Malformed structures |

**AD Structure Format:**
```
Byte 0:    Length (N, including Type byte but not Length byte)
Byte 1:    Type (e.g., 0x09 for Complete Local Name)
Bytes 2-N: Data
```

**Malformed AD Example:**
```python
# Length mismatch
adv_data = b'\x1F\x09' + b'Short'  # Length=31, but only 5 data bytes

# Length=0 (immediate next structure)
adv_data = b'\x00' + b'\x05\x09Test'

# Nested AD structures (parser confusion)
adv_data = b'\x10\xFF' + b'\x05\x09Name' + b'padding'
```

---

## 7. Attack Vector Mapping

### 7.1 Attack Type to Header Fields

| Attack Name | Layer | Protocol | Primary Target Fields | Manipulation Type |
|-------------|-------|----------|----------------------|-------------------|
| **Advertising Flood** | Link Layer | Advertising PDU | `PDU Type=0x0`, `Length=37`, `AdvData=max` | Rate (Hz), Size (bytes) |
| **Scan Response Amplification** | Link Layer | Advertising PDU | `PDU Type=0x4`, `ScanRspData=max`, `AdvAddr` | Rate, Address rotation |
| **Connection Request Flood** | Link Layer | Connect PDU | `Interval=min/max`, `Timeout=min`, All fields | Count, Parameters |
| **Retransmission Storm** | Link Layer | Data PDU | `SN=fixed`, `NESN=1` | Sequence numbers |
| **Empty Packet Flood** | Link Layer | Data PDU | `LLID=0x1`, `Length=0` | Rate |
| **HCI Command Storm** | HCI | Command | `OpCode=0x200A`, `Params` | Rate, OpCode variety |
| **HCI Fragmentation DoS** | HCI | ACL Data | `PB=0x1`, No final fragment | Fragmentation pattern |
| **L2CAP Param Update Storm** | L2CAP | Signaling | `Code=0x12`, `Identifier`, Extreme params | Rate, Parameter values |
| **L2CAP Length Mismatch** | L2CAP | Basic Header | `Length=65535`, Actual data=10 | Length field |
| **ATT Write Without Response Flood** | ATT | ATT PDU | `Opcode=0x52`, `Handle`, `Value=max MTU` | Rate, Payload size |
| **ATT Write Request Flood** | ATT | ATT PDU | `Opcode=0x12`, `Handle`, `Value` | Rate, Queue depth |
| **ATT Read Flood** | ATT | ATT PDU | `Opcode=0x0A`, `Handle` | Rate |
| **GATT Notification Storm** | GATT | ATT PDU | `Opcode=0x1B`, `Handle`, `Value=max` | Rate (peripheral attack) |
| **GATT Indication Flood** | GATT | ATT PDU | `Opcode=0x1D`, `Handle`, Delay confirm | Rate, Confirm timing |
| **SMP Pairing Spam** | SMP | SMP PDU | `Code=0x01`, Weak params, No completion | Rate, Parameter weakness |
| **SMP Invalid Public Key** | SMP | SMP PDU | `Code=0x0C`, `PublicKey=invalid` | Malformed crypto |

---

## 8. Exploitation Knobs

### 8.1 Rate-Based Attacks

| Parameter | Unit | Range | Recommended Test Values | Attack Impact |
|-----------|------|-------|------------------------|---------------|
| **Packet Rate** | Hz | 1-1000+ | 1, 10, 50, 100, 200, 500 | Controller saturation |
| **Burst Size** | Packets | 1-1000 | 10, 50, 100, 500 | Queue overflow |
| **Inter-Burst Delay** | ms | 0-1000 | 0, 10, 50, 100, 500 | Thermal/power stress |
| **Attack Duration** | Seconds | 1-3600 | 10, 30, 60, 300 | Sustained load |

---

### 8.2 Size-Based Attacks

| Parameter | Unit | Range | Recommended Test Values | Attack Impact |
|-----------|------|-------|------------------------|---------------|
| **Payload Size** | Bytes | 0-512 | 0, 1, 10, 100, 512 (max ATT MTU) | Memory allocation |
| **AdvData Length** | Bytes | 0-31 | 0, 10, 31 (max legacy) | Parser stress |
| **L2CAP Length** | Bytes | 0-65535 | 10, 1000, 65535 (max) | Reassembly buffers |

---

### 8.3 Malformed Value Attacks

| Field | Normal Range | Malformed Values | Expected Behavior |
|-------|--------------|------------------|-------------------|
| **Connection Interval** | 7.5ms - 4s (6-3200) | 0, 1, 5, 4000, 65535 | Reject or crash |
| **Slave Latency** | 0-499 | 500, 1000, 65535 | Reject or hang |
| **Supervision Timeout** | 100ms - 32s (10-3200) | 0, 9, 5000, 65535 | Connection drops |
| **Max Key Size** | 7-16 bytes | 0, 1, 6, 17, 255 | Pairing fail or weak crypto |
| **AD Structure Length** | Actual length | 0, 255, Length+10 | Parser crash |
| **L2CAP Length** | Actual length | 0, Actual-10, 65535 | Buffer issues |

---

### 8.4 Timing-Based Attacks

| Parameter | Unit | Range | Attack Scenario |
|-----------|------|-------|-----------------|
| **Response Delay** | ms | 0-30000 | Delayed ATT Write Response → timeout |
| **Pairing Timeout** | s | 0-30 | Never complete pairing (state exhaustion) |
| **Connection Timeout** | s | 0-32 | Hold connection idle (resource hold) |
| **Notification Interval** | ms | 0-1000 | Burst notifications (0ms = max rate) |

---

## 9. Quick Reference: Byte Sizes

| Layer | Structure | Total Bytes | Notes |
|-------|-----------|-------------|-------|
| LL Adv PDU Header | Header + Length | 2 | + 6 (AdvAddr) + AdvData |
| LL Data PDU Header | Header | 2 | + Payload (0-251) |
| LL Connect PDU | Full structure | 22 | After AdvAddr in CONNECT_IND |
| HCI Command Header | Type + OpCode + Length | 4 | + Parameters |
| HCI ACL Header | Type + Handle/Flags + Length | 5 | + Data |
| L2CAP Header | Length + CID | 4 | + Payload |
| L2CAP Signaling Header | Code + ID + Length | 4 | + Command Data |
| ATT PDU Minimum | Opcode | 1 | + Handle (optional) + Value |
| SMP PDU Minimum | Code | 1 | + Payload |

---

## 10. Usage Examples

### Example 1: Advertising Flood Attack Plan
```
Target: LL Advertising PDU
Fields: PDU Type=0x0 (ADV_IND), Length=37, AdvData=31 bytes
Knobs:
  - Rate: 10 Hz → 50 Hz → 100 Hz
  - AdvAddr rotation: Yes (256 addresses)
  - Duration: 30 seconds per trial
Expected: Scanner CPU spike, UI lag
```

### Example 2: ATT Write Flood Attack Plan
```
Target: ATT Write Command (0x52)
Fields: Opcode=0x52, Handle=0x0010, Value=512 bytes
Knobs:
  - Rate: 10 Hz → 50 Hz → 200 Hz
  - Payload size: 100 → 512 bytes (max MTU)
  - Duration: 30 seconds per trial
Expected: Server memory exhaustion, app unresponsive
```

### Example 3: SMP Pairing Spam Attack Plan
```
Target: SMP Pairing Request (0x01)
Fields: Code=0x01, IO Cap=0x03 (Just Works), Max Key=7 (min)
Knobs:
  - Rate: 1 request per 500ms
  - Never complete pairing (no response to Pairing Response)
  - Duration: 5 minutes
Expected: Pairing state table exhaustion, new pairing fails
```

---

## 11. Validation Checklist

Before deploying attacks, validate packet structure:

- [ ] Correct endianness (BLE uses little-endian)
- [ ] Field sizes match specification (no overflow/underflow)
- [ ] OpCodes/Codes are valid enum values
- [ ] Length fields match actual payload length (unless intentionally malformed)
- [ ] CRC/MIC fields omitted (controller adds these)
- [ ] Packet captured in Wireshark matches crafted bytes
- [ ] btmon shows expected HCI commands
- [ ] Ubertooth shows expected over-the-air PDUs

---

## 12. Field Size Quick Reference

```
1 bit   = 0 or 1
2 bits  = 0-3
3 bits  = 0-7
4 bits  = 0-15 (nibble)
6 bits  = 0-63
8 bits  = 0-255 (byte)
12 bits = 0-4095
16 bits = 0-65535 (2 bytes)
24 bits = 0-16777215 (3 bytes)
32 bits = 0-4294967295 (4 bytes)
48 bits = MAC address (6 bytes)
```

---

## Conclusion

This reference provides:
- ✅ Structured tables for all BLE protocol layers
- ✅ Exploitable header fields per layer
- ✅ Attack vector to header field mappings
- ✅ Concrete value ranges for testing
- ✅ Validation checklist
- ✅ Quick reference for byte sizes and opcodes

**Use this as your primary reference when implementing DoS attacks for dataset generation.**

---

## Appendix: Layer Stack Diagram

```
┌─────────────────────────────────────────────┐
│  GAP (Profile Layer - Procedures)          │ ← Not wire protocol
├─────────────────────────────────────────────┤
│  GATT (Attribute-based operations)         │ ← Application layer
├─────────────────────────────────────────────┤
│  ATT (Attribute Protocol)                  │ ← CID 0x0004
├─────────────────────────────────────────────┤
│  SMP (Security Manager Protocol)           │ ← CID 0x0006
├─────────────────────────────────────────────┤
│  L2CAP (Logical Link Control)              │ ← Multiplexing, Signaling
├─────────────────────────────────────────────┤
│  HCI (Host Controller Interface)           │ ← Commands, Events, ACL Data
├─────────────────────────────────────────────┤
│  Link Layer (LL)                           │ ← Advertising, Data PDUs
├─────────────────────────────────────────────┤
│  Physical Layer (PHY)                      │ ← 2.4 GHz Radio
└─────────────────────────────────────────────┘
```

**Attack Surface:** All layers except PHY are exploitable via software.

---

**Last Updated:** 2025-11-12  
**Maintainer:** Your BLE Research Team  
**License:** For educational and authorized security research only
```

This structured README provides comprehensive tables for all BLE protocol layers with their exploitable fields, attack mappings, and quick reference information. Use it as your primary guide when implementing DoS attacks!
