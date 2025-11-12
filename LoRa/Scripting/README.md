---
title: LoRa/LoRaWAN Scripting & Packet Crafting
tags: [LoRa, LoRaWAN, scripting, python, arduino, GNU-Radio]
category: LoRa Security
parent: "[[LoRa/README]]"
status: comprehensive
---

# LoRa/LoRaWAN Scripting & Packet Crafting

> **Status**: 📋 Comprehensive framework

## Overview

Comprehensive guide to LoRa/LoRaWAN packet crafting using GNU Radio, Arduino-LMIC (C++), and Python.

## Libraries

**Python:**
- `gnuradio`: Signal processing framework
- `gr-lora`: LoRa PHY encoder/decoder
- `pycryptodome`: AES-128 encryption
- `lorawan-parser`: Frame parsing

**C++ (Arduino/ESP32):**
- `<lmic.h>`: LoRaWAN MAC in C
- `<hal/hal.h>`: Hardware abstraction
- `<SPI.h>`: LoRa radio communication
- `<aes.h>`: AES encryption

**SDR:**
- `osmosdr`: Universal SDR interface (HackRF, LimeSDR)
- `gnuradio.blocks`: Signal sources/sinks

## Topics

- LoRa PHY modulation (chirp generation)
- LoRaWAN frame construction
- OTAA/ABP session management
- AES-128 encryption and MIC calculation
- Multi-SF reception
- Attack automation

## Pseudocode Examples

```python
# GNU Radio LoRa transmission pseudocode
# Required: HackRF, GNU Radio, gr-lora

from gnuradio import gr, blocks
import osmosdr
import numpy as np

def transmit_lora_packet(freq_mhz, sf, bw, cr, payload):
    """
    Libraries:
    - gnuradio: Flowgraph framework
    - gr-lora: LoRa encoder
    - osmosdr: HackRF sink
    - numpy: Data manipulation

    Why:
    - gr-lora: Generates LoRa chirp modulation
    - osmosdr: Transmits via SDR hardware
    - Parameters: SF (7-12), BW (125/250/500 kHz), CR (4/5-4/8)
    """

    # Create flowgraph
    # tb = gr.top_block()

    # LoRa encoder
    # lora_encoder = lora.encoder(sf, bw, cr)

    # SDR sink
    # sdr = osmosdr.sink()
    # sdr.set_center_freq(freq_mhz * 1e6)
    # sdr.set_sample_rate(bw * 8)
    # sdr.set_gain(20)

    # Vector source (payload)
    # src = blocks.vector_source_b(payload)

    # Connect blocks
    # tb.connect(src, lora_encoder, sdr)
    # tb.run()
    pass


# Arduino LMIC LoRaWAN uplink pseudocode
# Required: LoRa32 (ESP32), Arduino-LMIC

def send_lorawan_uplink_cpp():
    """
    Libraries (C++):
    - <lmic.h>: LoRaWAN 1.0.x stack
    - <hal/hal.h>: Pin mapping for SPI
    - <SPI.h>: LoRa radio (SX1276/RFM95)

    Why:
    - LMIC: Complete LoRaWAN implementation (MAC + PHY)
    - Handles encryption, MIC, frame counter
    - Supports OTAA and ABP
    - Manages join procedure and retransmissions
    """

    # Arduino C++ pseudocode
    #
    # #include <lmic.h>
    # #include <hal/hal.h>
    # #include <SPI.h>
    #
    # // ABP credentials
    # static const u4_t DEVADDR = 0x26011234;
    # static const PROGMEM u1_t NWKSKEY[16] = { ... };
    # static const PROGMEM u1_t APPSKEY[16] = { ... };
    #
    # void setup() {
    #     LMIC_reset();
    #     LMIC_setSession(0x1, DEVADDR, NWKSKEY, APPSKEY);
    # }
    #
    # void send_uplink() {
    #     uint8_t payload[] = {0x01, 0x02, 0x03};
    #     LMIC_setTxData(1, payload, sizeof(payload), 0);
    # }
    pass


# LoRaWAN frame construction pseudocode
# Required: Python, pycryptodome

from Crypto.Cipher import AES
from Crypto.Hash import CMAC
import struct

def construct_lorawan_frame(dev_addr, fcnt, nwkskey, appskey, payload, fport=1):
    """
    Libraries:
    - Crypto.Cipher: AES encryption (pycryptodome)
    - Crypto.Hash: CMAC for MIC calculation
    - struct: Binary packing

    Why:
    - LoRaWAN frame structure:
    #   MHDR (1) | FHDR (7-22) | FPort (1) | FRMPayload (0-N) | MIC (4)
    - Payload encrypted with AppSKey (AES-128 CTR mode)
    - MIC calculated with NwkSKey (AES-128 CMAC)
    """

    # MHDR
    mhdr = bytes([0x40])  # Unconfirmed Data Up, LoRaWAN R1

    # FHDR (Frame Header)
    fhdr = struct.pack('<I', dev_addr)  # DevAddr (4 bytes, little-endian)
    fctrl = bytes([0x00])  # FCtrl (ADR=0, ACK=0, FOptsLen=0)
    fcnt_bytes = struct.pack('<H', fcnt)  # FCnt (2 bytes)
    fhdr += fctrl + fcnt_bytes

    # Encrypt payload
    # encrypted_payload = encrypt_frm_payload(appskey, dev_addr, fcnt, payload, direction=0)

    # FPort
    fport_byte = bytes([fport])

    # Calculate MIC
    # B0 block for MIC
    # b0 = bytes([0x49, 0x00, 0x00, 0x00, 0x00, 0x00])
    # b0 += struct.pack('<I', dev_addr)
    # b0 += struct.pack('<I', fcnt)
    # b0 += bytes([0x00, len(mhdr + fhdr + fport_byte + encrypted_payload)])

    # cmac = CMAC.new(nwkskey, ciphermod=AES)
    # cmac.update(b0 + mhdr + fhdr + fport_byte + encrypted_payload)
    # mic = cmac.digest()[:4]

    # Complete frame
    # frame = mhdr + fhdr + fport_byte + encrypted_payload + mic
    # return frame
    pass


def encrypt_frm_payload(key, dev_addr, fcnt, payload, direction):
    """
    Libraries:
    - Crypto.Cipher: AES encryption

    Why:
    - LoRaWAN uses AES-128 in counter mode
    - Counter block: 0x01 | 4×0x00 | direction | DevAddr | FCnt | 0x00 | counter
    - XOR payload with keystream
    """

    # cipher = AES.new(key, AES.MODE_ECB)
    # encrypted = bytearray()

    # for i in range(0, len(payload), 16):
    #     # Construct A block
    #     a_block = bytes([0x01, 0x00, 0x00, 0x00, 0x00, direction])
    #     a_block += struct.pack('<I', dev_addr)
    #     a_block += struct.pack('<I', fcnt)
    #     a_block += bytes([0x00, i // 16 + 1])

    #     # Encrypt A block to get S block (keystream)
    #     s_block = cipher.encrypt(a_block)

    #     # XOR with payload
    #     chunk = payload[i:i+16]
    #     encrypted.extend(bytes([chunk[j] ^ s_block[j] for j in range(len(chunk))]))

    # return bytes(encrypted)
    pass


# OTAA join procedure pseudocode

def perform_otaa_join(appeui, deveui, appkey):
    """
    Libraries (C++):
    - <lmic.h>: OTAA join implementation

    Why:
    - Join Request: AppEUI | DevEUI | DevNonce | MIC
    - MIC = aes128_cmac(AppKey, MHDR | AppEUI | DevEUI | DevNonce)
    - Join Accept encrypted with AppKey (AES-128 ECB)
    - Derives NwkSKey and AppSKey from Join Accept
    """

    # C++ pseudocode
    #
    # void join_otaa() {
    #     LMIC_reset();
    #     LMIC_startJoining();
    #
    #     // LMIC automatically:
    #     // 1. Constructs Join Request with DevNonce
    #     // 2. Calculates MIC with AppKey
    #     // 3. Waits for Join Accept
    #     // 4. Decrypts Join Accept
    #     // 5. Derives session keys:
    #     //    NwkSKey = aes128_encrypt(AppKey, 0x01 | AppNonce | NetID | DevNonce | pad)
    #     //    AppSKey = aes128_encrypt(AppKey, 0x02 | AppNonce | NetID | DevNonce | pad)
    # }
    pass


# Multi-SF reception pseudocode
# Required: GNU Radio, gr-lora

def receive_multi_sf(center_freq_mhz, bandwidth=125000):
    """
    Libraries:
    - gnuradio: Parallel processing
    - gr-lora: Multiple decoder instances

    Why:
    - LoRaWAN uses adaptive data rate (SF7-SF12)
    - Simultaneous SF reception requires parallel decoders
    - Each decoder locks to specific SF
    - Increases capture probability
    """

    # Create parallel flowgraph
    # tb = gr.top_block()

    # Single SDR source
    # sdr = osmosdr.source()
    # sdr.set_center_freq(center_freq_mhz * 1e6)
    # sdr.set_sample_rate(bandwidth * 8)

    # Multiple LoRa decoders
    # for sf in range(7, 13):
    #     decoder = lora.decoder(sf, bandwidth, 4/5)
    #     socket_pdu = blocks.socket_pdu("UDP_SERVER", "localhost", f"500{sf}")
    #     tb.connect(sdr, decoder, socket_pdu)

    # tb.run()
    pass


# ChirpStack gateway simulation pseudocode

import socket
import json
import base64

def simulate_gateway(gateway_eui, network_server_ip):
    """
    Libraries:
    - socket: UDP communication
    - json: Gateway protocol format
    - base64: Payload encoding

    Why:
    - ChirpStack uses Semtech UDP protocol
    - Gateway forwards PHYPayload to network server
    - Can inject arbitrary LoRaWAN frames
    - PUSH_DATA format: version | token | identifier | gateway_eui | json
    """

    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Construct PUSH_DATA
    # version = bytes([0x02])
    # token = bytes([0x12, 0x34])
    # identifier = bytes([0x00])  # PUSH_DATA

    # rxpk = {
    #     "rxpk": [{
    #         "time": "2025-11-12T12:00:00Z",
    #         "tmst": 123456789,
    #         "freq": 868.1,
    #         "chan": 0,
    #         "rfch": 0,
    #         "stat": 1,
    #         "modu": "LORA",
    #         "datr": "SF7BW125",
    #         "codr": "4/5",
    #         "rssi": -50,
    #         "lsnr": 10.0,
    #         "size": len(phypayload),
    #         "data": base64.b64encode(phypayload).decode()
    #     }]
    # }

    # packet = version + token + identifier + gateway_eui + json.dumps(rxpk).encode()
    # sock.sendto(packet, (network_server_ip, 1700))
    pass
```

## Tools

- **GNU Radio**: Signal processing framework
- **gr-lora**: LoRa modulation/demodulation
- **Arduino-LMIC**: LoRaWAN stack for ESP32/Arduino
- **pycryptodome**: Python AES encryption
- **lorawan-parser**: Frame parsing library
- **HackRF One / LimeSDR**: SDR hardware
- **LoRa32 (ESP32)**: LoRa development board
- **ChirpStack**: Network server for testing

---
**Related**: [[LoRa/README|LoRa Overview]] • [[Bluetooth/BLE/Scripting/README|BLE Scripting]] • [[Zigbee/Scripting/README|Zigbee Scripting]]
