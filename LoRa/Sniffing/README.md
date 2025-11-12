---
title: LoRa/LoRaWAN Sniffing & Reconnaissance
tags: [LoRa, LoRaWAN, sniffing, SDR, reconnaissance]
category: LoRa Security
parent: "[[LoRa/README]]"
status: comprehensive
---

# LoRa/LoRaWAN Sniffing & Reconnaissance

> **Status**: 📋 Comprehensive framework

## Techniques

### 1. Passive Packet Capture
**Tool**: RTL-SDR, HackRF, LimeSDR with gr-lora

**Captures**: LoRa PHY decoding, LoRaWAN frame extraction

**Coverage**: All spreading factors (SF7-SF12), all bandwidths

### 2. Device Enumeration
**Tool**: Wireshark with LoRaWAN dissector

**Extracts**: DevAddr, DevEUI (OTAA), AppEUI, device class

### 3. Gateway Discovery
**Tool**: GNU Radio flowgraphs for downlink monitoring

**Extracts**: Gateway EUI, network server, coverage mapping

### 4. Traffic Pattern Analysis
**Tool**: Custom Python scripts, lorawan-parser

**Analyzes**: Transmission intervals, data rates, duty cycle, payload patterns

### 5. Join Procedure Monitoring
**Tool**: Wireshark, gr-lora

**Captures**: OTAA join requests, DevNonce, encrypted join accept

## Pseudocode

```python
# LoRa passive sniffing pseudocode
# Required: RTL-SDR, gr-lora, GNU Radio

from gnuradio import gr, blocks
import osmosdr

def sniff_lora_channel(center_freq_mhz, spreading_factor, bandwidth=125000):
    """
    Libraries:
    - gnuradio: Signal processing framework
    - osmosdr: RTL-SDR/HackRF source
    - gr-lora: LoRa demodulation and decoding

    Why:
    - gr-lora: Implements LoRa PHY decoder (chirp demodulation)
    - Can decode all spreading factors (SF7-SF12)
    - Outputs LoRa frames to file or socket
    - osmosdr: Universal SDR interface
    """

    # Create flowgraph
    # tb = gr.top_block()

    # SDR source
    # sdr = osmosdr.source()
    # sdr.set_center_freq(center_freq_mhz * 1e6)
    # sdr.set_sample_rate(bandwidth * 8)
    # sdr.set_gain(30)

    # LoRa decoder
    # lora_decoder = lora.lora_receiver(sdr, center_freq, spreading_factor, bandwidth)

    # File sink
    # file_sink = blocks.file_sink(gr.sizeof_gr_complex, "lora_capture.bin")

    # tb.connect(sdr, lora_decoder, file_sink)
    # tb.run()
    pass


# Multi-SF sniffing pseudocode
# Required: HackRF, GNU Radio

def sniff_all_spreading_factors(center_freq_mhz, bandwidth=125000):
    """
    Libraries:
    - gnuradio: Parallel flowgraph
    - gr-lora: Multiple decoder instances

    Why:
    - LoRaWAN devices use different SFs simultaneously
    - Need parallel decoders for SF7-SF12
    - Each decoder processes same IQ stream
    - Captures all traffic on channel
    """

    # Create parallel decoders
    # for sf in range(7, 13):
    #     decoder = create_lora_decoder(center_freq_mhz, sf, bandwidth)
    #     connect_to_wireshark(decoder, port=5000 + sf)
    pass


# Device enumeration pseudocode

import struct

def enumerate_devices(pcap_file):
    """
    Libraries:
    - scapy: PCAP file parsing
    - lorawan_parser: LoRaWAN frame parsing (JavaScript/Python port)

    Why:
    - Parse captured LoRa frames
    - Extract DevAddr (4 bytes) from FHDR
    - Extract DevEUI (8 bytes) from join requests
    - Build device inventory
    """

    devices = {}

    # for packet in read_pcap(pcap_file):
    #     if is_lorawan_uplink(packet):
    #         dev_addr = extract_dev_addr(packet)
    #         devices[dev_addr] = {
    #             'first_seen': timestamp,
    #             'packet_count': 0,
    #             'spreading_factor': detect_sf(packet)
    #         }

    # return devices
    pass


# OTAA join request capture pseudocode

def capture_join_requests(channel_freq):
    """
    Libraries:
    - gr-lora: LoRa decoder
    - struct: Binary unpacking

    Why:
    - Join Request contains:
    #   - AppEUI (8 bytes)
    #   - DevEUI (8 bytes)
    #   - DevNonce (2 bytes)
    #   - MIC (4 bytes, computed with AppKey)
    - Can attempt offline AppKey brute-force
    - Identify device trying to join network
    """

    while True:
        # packet = receive_lora_packet()

        # Check MHDR (MType = 0x00 for Join Request)
        # if packet[0] & 0xE0 == 0x00:
        #     appeui = packet[1:9]
        #     deveui = packet[9:17]
        #     devnonce = struct.unpack('<H', packet[17:19])[0]
        #     mic = packet[19:23]

        #     print(f"Join Request: DevEUI={deveui.hex()}, DevNonce={devnonce}")
        #     save_for_bruteforce(appeui, deveui, devnonce, mic)
        pass


# Traffic pattern analysis pseudocode

import time
from collections import defaultdict

def analyze_traffic_patterns(pcap_file):
    """
    Libraries:
    - scapy/dpkt: PCAP parsing
    - numpy: Statistical analysis
    - matplotlib: Visualization (optional)

    Why:
    - Identify transmission intervals (periodic sensors)
    - Data rate distribution (SF usage)
    - Payload size patterns (identify device types)
    - Duty cycle compliance checking
    """

    device_stats = defaultdict(lambda: {
        'timestamps': [],
        'spreading_factors': [],
        'payload_sizes': []
    })

    # for packet in read_pcap(pcap_file):
    #     dev_addr = extract_dev_addr(packet)
    #     device_stats[dev_addr]['timestamps'].append(packet.time)
    #     device_stats[dev_addr]['spreading_factors'].append(detect_sf(packet))
    #     device_stats[dev_addr]['payload_sizes'].append(len(packet.payload))

    # For each device, calculate:
    # - Average interval: mean(diff(timestamps))
    # - SF distribution: histogram(spreading_factors)
    # - Payload characteristics
    pass


# Gateway discovery pseudocode

def discover_gateways(frequency_range):
    """
    Libraries:
    - gr-lora: Monitor downlink channels
    - osmosdr: SDR control

    Why:
    - Gateways transmit downlinks in RX1/RX2 windows
    - RX1: Same freq as uplink, 1 second delay
    - RX2: Fixed freq (869.525 MHz EU), 2 second delay, SF12
    - Extract Gateway EUI from packet metadata (if available)
    """

    # Monitor RX2 frequency (869.525 MHz for EU868)
    # sdr = configure_sdr(869525000, sf=12, bw=125000)

    # Capture downlinks
    # while True:
    #     packet = receive_lora_packet()
    #     if is_downlink(packet):
    #         # Gateway location can be triangulated
    #         # RSSI and SNR indicate distance
    #         record_gateway_signal(packet)
    pass
```

## Tools

- **RTL-SDR**: Low-cost LoRa sniffing ($20-30)
- **HackRF One**: Full-duplex, wider bandwidth
- **LimeSDR**: High performance SDR
- **GNU Radio**: Signal processing framework
- **gr-lora**: LoRa demodulation blocks
- **Wireshark**: LoRaWAN dissector plugin
- **lorawan-parser**: Frame parsing library
- **Python scapy**: PCAP analysis

---
**Related**: [[LoRa/README|LoRa Overview]] • [[Bluetooth/BLE/Sniffing/README|BLE Sniffing]] • [[Zigbee/Sniffing/README|Zigbee Sniffing]]
