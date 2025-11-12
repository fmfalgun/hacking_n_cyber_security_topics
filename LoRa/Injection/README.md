---
title: LoRa/LoRaWAN Injection Attacks
tags: [LoRa, LoRaWAN, injection, fuzzing, payload]
category: LoRa Security
parent: "[[LoRa/README]]"
status: comprehensive
---

# LoRa/LoRaWAN Injection Attacks

> **Status**: 📋 Comprehensive framework

## Attack Vectors

### 1. Malicious Uplink Injection
**Mechanism**: Inject fake sensor data with spoofed DevAddr/DevEUI

**Tools**: LoRa32, LMIC library

**Impact**: False sensor readings, network pollution

### 2. Downlink Command Injection
**Mechanism**: Inject MAC commands (requires NwkSKey)

**Tools**: LoRa32, Arduino-LMIC

**Impact**: Force device configuration changes, parameter manipulation

### 3. Payload Fuzzing
**Mechanism**: Malformed LoRaWAN frames to test parser robustness

**Impact**: Crash network server/devices, discover vulnerabilities

### 4. MAC Command Injection
**Mechanism**: Inject network management commands

**Impact**: Topology manipulation, DoS via configuration changes

### 5. Application Payload Injection
**Mechanism**: Encrypted payload with known/guessed keys

**Impact**: Application-level attacks, data manipulation

## Pseudocode

```python
# Malicious uplink injection pseudocode
# Required: LoRa32, LMIC

def inject_fake_uplink(target_dev_addr, fcnt, nwkskey, appskey, fake_data):
    """
    Libraries (C++):
    - <lmic.h>: LoRaWAN MAC implementation
    - <aes.h>: AES encryption for payload and MIC

    Why:
    - LMIC: Constructs proper LoRaWAN frame format
    - Requires NwkSKey for MIC (Message Integrity Code)
    - Requires AppSKey for payload encryption
    - Can spoof any DevAddr if keys known
    """

    # Configure ABP session
    # LMIC_setSession(0x1, target_dev_addr, nwkskey, appskey)

    # Set frame counter
    # LMIC.seqnoUp = fcnt

    # Transmit fake data
    # LMIC_setTxData(1, fake_data, sizeof(fake_data), 0)
    pass


# MAC command injection pseudocode
# Required: LoRa32, LMIC

def inject_mac_command(dev_addr, fcnt, nwkskey, command_cid, command_payload):
    """
    Libraries (C++):
    - <lmic.h>: LoRaWAN stack
    - <aes.h>: MIC calculation

    Why:
    - MAC commands in FOpts field (FHDR)
    - LinkADRReq (0x03): Change data rate/TX power
    - DutyCycleReq (0x04): Limit duty cycle
    - RXParamSetupReq (0x05): Change RX parameters
    - Requires valid MIC (NwkSKey needed)
    """

    # Construct downlink with MAC command in FOpts
    # mhdr = 0xA0  # Unconfirmed Data Down
    # fhdr = {
    #     'DevAddr': dev_addr,
    #     'FCtrl': 0x80,  # FOptsLen > 0
    #     'FCnt': fcnt,
    #     'FOpts': [command_cid, command_payload]
    # }

    # Calculate MIC
    # mic = aes128_cmac(nwkskey, mhdr + fhdr)
    # frame = mhdr + fhdr + mic

    # Transmit in RX1 window
    pass


# LoRaWAN payload fuzzing pseudocode

import struct
import random

def fuzz_lorawan_frame(dev_addr, nwkskey):
    """
    Libraries:
    - struct: Binary packing
    - random: Fuzzing data generation
    - gr-lora: LoRa transmission (GNU Radio)

    Why:
    - Test network server/device parser robustness
    - Malformed MHDR, FCtrl, FPort values
    - Invalid frame lengths
    - MIC collisions
    """

    while True:
        # Generate malformed frame
        # mhdr = random.randint(0, 255)  # Random MHDR
        # fhdr = generate_malformed_fhdr(dev_addr)
        # fport = random.randint(0, 255)
        # payload = bytes([random.randint(0, 255) for _ in range(random.randint(0, 255))])

        # Invalid MIC
        # mic = bytes(4)

        # frame = struct.pack('B', mhdr) + fhdr + struct.pack('B', fport) + payload + mic

        # Transmit
        # transmit_lora_frame(frame)
        pass


# LinkADRReq injection pseudocode

def inject_link_adr_req(dev_addr, fcnt, nwkskey, new_datarate, new_txpower):
    """
    Libraries (C++):
    - <lmic.h>: LoRaWAN MAC command format
    - <aes.h>: MIC calculation

    Why:
    - LinkADRReq (CID 0x03): Change data rate and TX power
    - DataRate: SF7-SF12, BW125/250/500
    - TXPower: 0-7 (region specific)
    - Can force device to lowest SF (easiest to jam)
    - Or highest SF (drain battery)
    """

    # Construct LinkADRReq payload
    # DataRate_TXPower = (new_datarate << 4) | new_txpower
    # ChMask = 0xFFFF  # Enable all channels
    # Redundancy = 0x00  # No redundancy

    # mac_payload = [0x03, DataRate_TXPower, ChMask & 0xFF, (ChMask >> 8) & 0xFF, Redundancy]

    # Inject as downlink MAC command
    # inject_mac_command(dev_addr, fcnt, nwkskey, 0x03, mac_payload)
    pass


# Application payload bit-flipping attack

def bit_flip_attack(captured_encrypted_payload, target_bit_position):
    """
    Libraries:
    - bytes/bytearray: Byte manipulation

    Why:
    - AES-128 in counter mode (LoRaWAN encryption)
    - Flipping ciphertext bit flips corresponding plaintext bit
    - If plaintext structure known, can modify values
    - MIC still validates (only covers unencrypted parts)
    """

    # Copy payload
    # modified = bytearray(captured_encrypted_payload)

    # Flip bit
    # byte_idx = target_bit_position // 8
    # bit_idx = target_bit_position % 8
    # modified[byte_idx] ^= (1 << bit_idx)

    # Replay with modified payload
    # transmit_lora_frame(modified)
    pass
```

## Tools

- **LoRa32 (ESP32)**: Hardware for packet injection
- **Arduino-LMIC**: LoRaWAN stack implementation
- **GNU Radio + gr-lora**: PHY-level packet crafting
- **pycryptodome**: Encryption/MIC calculation
- **lorawan-parser**: Packet construction and validation
- **ChirpStack**: Testing target (network server)

---
**Related**: [[LoRa/README|LoRa Overview]] • [[Bluetooth/BLE/Injection/README|BLE Injection]] • [[Zigbee/Injection/README|Zigbee Injection]]
