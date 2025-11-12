---
title: LoRa/LoRaWAN MITM Attacks
tags: [LoRa, LoRaWAN, MITM, rogue-gateway, wormhole]
category: LoRa Security
parent: "[[LoRa/README]]"
status: comprehensive
---

# LoRa/LoRaWAN Man-in-the-Middle Attacks

> **Status**: 📋 Comprehensive framework

## Attack Vectors

### 1. Rogue Gateway
**Mechanism**: Deploy fake gateway closer to target devices

**Tools**: ChirpStack, LoRa32 gateway, Raspberry Pi + RAK concentrator

**Impact**: Capture uplink messages, inject malicious downlinks (if keys known)

### 2. Wormhole Attack
**Mechanism**: Relay packets between distant locations using two colluding gateways

**Impact**: Disrupt network topology, GPS spoofing for Class B devices

### 3. Join Accept Manipulation
**Mechanism**: Intercept OTAA join procedure, modify join accept

**Requirement**: Know AppKey (often default)

**Impact**: Session key control, parameter downgrade

### 4. Downlink Injection
**Mechanism**: Inject malicious downlink commands

**Requirement**: NwkSKey or AppSKey

**Impact**: MAC command manipulation, firmware update hijacking

### 5. Replay Attacks
**Mechanism**: Capture and replay uplink messages

**Requirement**: Weak frame counter validation

**Impact**: Trigger duplicate processing, state confusion

## Pseudocode

```python
# Rogue gateway pseudocode
# Required: LoRa32 + ChirpStack

import socket
import struct

def create_rogue_gateway(gateway_eui, network_server_ip):
    """
    Libraries:
    - socket: UDP communication with network server
    - struct: Binary packet formatting (Semtech protocol)
    - json: Gateway JSON format

    Why:
    - ChirpStack uses Semtech UDP protocol
    - Gateway forwards all received packets as-is
    - Can capture uplinks before legitimate gateway
    """

    # Configure LoRa radio to receive all SF (SF7-SF12)
    # for sf in range(7, 13):
    #     configure_radio(sf, bandwidth=125000)

    # Forward packets to network server
    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        # Receive LoRa packet
        # packet = receive_lora_packet()

        # Format as Semtech PUSH_DATA
        # push_data = format_semtech_packet(gateway_eui, packet)

        # Forward to network server
        # sock.sendto(push_data, (network_server_ip, 1700))
        pass


# Join accept interception pseudocode
# Required: Python, pycryptodome

from Crypto.Cipher import AES

def intercept_join_accept(appeui, appkey, join_request_packet):
    """
    Libraries:
    - Crypto.Cipher: AES encryption (pycryptodome)
    - struct: Binary unpacking

    Why:
    - Join Accept is AES-128 ECB encrypted with AppKey
    - Can decrypt with default/known AppKey
    - Modify NetID, DevAddr, DLSettings, RxDelay
    - Re-encrypt and forward modified version
    """

    # Parse join request
    # appeui_rx, deveui, devnonce = parse_join_request(join_request_packet)

    # Wait for join accept from network server
    # join_accept_encrypted = capture_downlink()

    # Decrypt with AppKey
    # cipher = AES.new(appkey, AES.MODE_ECB)
    # join_accept_plain = cipher.decrypt(join_accept_encrypted)

    # Modify parameters
    # modified = join_accept_plain
    # modified['DLSettings'] = 0x00  # Downgrade RX parameters

    # Re-encrypt
    # modified_encrypted = cipher.encrypt(modified)

    # Transmit to device
    # transmit_downlink(modified_encrypted)
    pass


# Downlink injection pseudocode
# Required: LoRa32, LMIC

def inject_downlink(dev_addr, fcnt, nwkskey, appskey, mac_command):
    """
    Libraries (C++):
    - <lmic.h>: LoRaWAN stack
    - <aes.h>: AES-128 for MIC and encryption

    Why:
    - Requires NwkSKey for MIC calculation
    - Requires AppSKey for payload encryption
    - LMIC provides MIC calculation (aes128_cmac)
    - Can inject MAC commands or application payload
    """

    # Construct downlink frame
    # mhdr = 0xA0  # Unconfirmed Data Down
    # fhdr = construct_fhdr(dev_addr, fcnt, FOpts=mac_command)
    # payload = encrypt_payload(appskey, payload_data, fcnt, DOWN)
    # mic = calculate_mic(nwkskey, mhdr + fhdr + payload)
    # frame = mhdr + fhdr + payload + mic

    # Transmit in RX1 or RX2 window
    # configure_radio(rx1_freq, rx1_datarate)
    # transmit_packet(frame)
    pass


# Replay attack pseudocode

def replay_uplink(captured_packet, delay_seconds):
    """
    Libraries:
    - gr-lora: LoRa transmission (GNU Radio)
    - time: Delay control

    Why:
    - Some devices/servers don't validate frame counter
    - Exact replay of captured packet
    - Can trigger duplicate processing
    """

    # Wait for time window
    # time.sleep(delay_seconds)

    # Retransmit captured packet as-is
    # configure_lora_tx(freq, sf, bw, cr, power)
    # transmit_lora_frame(captured_packet)
    pass
```

## Tools

- **ChirpStack**: LoRaWAN network server (rogue gateway)
- **LoRa32 (ESP32)**: Gateway hardware
- **Raspberry Pi + RAK concentrator**: Multi-channel gateway
- **Arduino-LMIC**: LoRaWAN stack for injection
- **GNU Radio + gr-lora**: Signal relay
- **pycryptodome**: AES encryption/decryption
- **lorawan-parser**: Packet analysis

---
**Related**: [[LoRa/README|LoRa Overview]] • [[Bluetooth/BLE/MITM/README|BLE MITM]] • [[Zigbee/MITM/README|Zigbee MITM]]
