# Wireless Protocol Attack Implementations

> **Complete multi-language implementation suite for WiFi, BLE, Zigbee, and LoRa security research**

---

## 📋 Overview

This directory contains **560+ attack implementations** across 4 wireless protocols in 7 programming languages, providing a comprehensive framework for security research, dataset generation, and defensive analysis.

### Protocol Coverage

| Protocol | Attacks | Languages | Status |
|----------|---------|-----------|--------|
| **WiFi (802.11)** | 15 vectors | Python, C, C++, JS, C#, Java, Go | ✅ Complete |
| **BLE (Bluetooth Low Energy)** | 25 vectors | Python, C, C++, JS, C#, Java, Go | ✅ Complete |
| **Zigbee (IEEE 802.15.4)** | 20 vectors | Python, C, C++, JS, C#, Java, Go | ✅ Complete |
| **LoRa/LoRaWAN** | 20 vectors | Python, C, C++, JS, C#, Java, Go | ✅ Complete |

**Total**: 80 attack vectors × 7 languages = **560 implementations**

---

## 🗂️ Directory Structure

```
Implementations/
├── WiFi/
│   ├── DoS/                    # Denial of Service attacks
│   │   ├── deauth_attack/      # Each attack has 7 language dirs
│   │   │   ├── python/
│   │   │   │   ├── python38/deauth.py
│   │   │   │   ├── python310/deauth.py
│   │   │   │   ├── python311plus/deauth.py
│   │   │   │   ├── requirements.txt
│   │   │   │   └── version_comparison.md
│   │   │   ├── c/
│   │   │   │   ├── deauth.c
│   │   │   │   ├── Makefile
│   │   │   │   └── README.md
│   │   │   ├── cpp/
│   │   │   ├── javascript/
│   │   │   ├── csharp/
│   │   │   ├── java/
│   │   │   ├── go/
│   │   │   └── COMPARISON.md   # Cross-language comparison
│   │   ├── beacon_flood/
│   │   ├── disassoc_attack/
│   │   └── ... (12 more)
│   ├── MITM/                   # Man-in-the-Middle attacks
│   │   ├── evil_twin/
│   │   ├── karma_attack/
│   │   └── ... (3 more)
│   ├── Injection/              # Packet injection attacks
│   └── README.md
├── BLE/
│   ├── DoS/
│   │   ├── att_write_flood/
│   │   ├── advertising_flood/
│   │   ├── connection_flood/
│   │   └── ... (10 more)
│   ├── MITM/
│   ├── Injection/
│   └── README.md
├── Zigbee/
│   ├── DoS/
│   ├── MITM/
│   ├── Injection/
│   └── README.md
├── LoRa/
│   ├── DoS/
│   ├── MITM/
│   ├── Injection/
│   └── README.md
└── README.md (this file)
```

---

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone repository
cd /path/to/hacking_n_cyber_security_topics

# Install Python dependencies
pip install -r requirements.txt

# Or protocol-specific
pip install -e .[wifi]    # WiFi only
pip install -e .[ble]     # BLE only
pip install -e .[all]     # Everything
```

### 2. Run an Attack (Python Example)

```bash
# WiFi deauthentication attack
cd Implementations/WiFi/DoS/deauth_attack/python/python310
python deauth.py --interface wlan0mon --target AA:BB:CC:DD:EE:FF --duration 30

# BLE ATT Write flood
cd Implementations/BLE/DoS/att_write_flood/python/python310
python att_write_flood.py --target AA:BB:CC:DD:EE:FF --rate 100 --duration 60

# Zigbee beacon flood
cd Implementations/Zigbee/DoS/beacon_flood/python/python310
python beacon_flood.py --channel 15 --panid 0x1234 --rate 50

# LoRa join request flood
cd Implementations/LoRa/DoS/join_request_flood/python/python310
python join_flood.py --deveui 00:00:00:00:00:00:00:01 --rate 10
```

### 3. Using Docker

```bash
# Start WiFi attack container
docker-compose up -d wifi
docker-compose exec wifi bash

# Inside container
cd /workspace/wifi/DoS/deauth_attack/python/python310
python deauth.py --help

# Start all protocols
docker-compose up -d
```

---

## 📊 Python Version Comparison

Each Python attack is implemented in **3 versions** to demonstrate language evolution:

| Version | Target Systems | Key Features | Performance |
|---------|----------------|--------------|-------------|
| **3.8** | Ubuntu 20.04, Debian 10 | Maximum compatibility, conservative syntax | Baseline |
| **3.10** | Ubuntu 22.04, Debian 11 | `match/case`, `T \| None`, better errors | +5-10% |
| **3.11+** | Ubuntu 23.04+ | Exception groups, task groups, speed | +15-25% |

**Example differences**:

```python
# Python 3.8 - Compatible
from typing import Optional
def parse_packet(data: bytes) -> Optional[dict]:
    if len(data) < 10:
        return None
    # ... if/elif chains for parsing

# Python 3.10 - Modern
def parse_packet(data: bytes) -> dict | None:
    match len(data):
        case n if n < 10:
            return None
        # ... match/case for cleaner logic

# Python 3.11+ - Optimized
def parse_packet(data: bytes) -> dict | None:
    match len(data):
        case n if n < 10:
            return None
        # ... + exception groups + 25% faster execution
```

See individual `version_comparison.md` files for detailed analysis.

---

## 🔧 Language-Specific Guides

### Python (All Protocols)
**Best for**: Rapid prototyping, high-level attacks, scripting
**Libraries**: `scapy`, `bleak`, `bluepy`, `killerbee`, `pyLoRa`

```bash
cd Implementations/WiFi/DoS/deauth_attack/python/python310
pip install -r requirements.txt
python deauth.py --help
```

### C (Performance-Critical)
**Best for**: Low-level control, embedded systems, kernel-space
**Libraries**: `libpcap`, BlueZ headers, libusb

```bash
cd Implementations/WiFi/DoS/deauth_attack/c
make
sudo ./deauth --help
```

### C++ (OOP + Performance)
**Best for**: Object-oriented protocol implementations
**Libraries**: `libpcap++`, `tins`, Qt Bluetooth

```bash
cd Implementations/WiFi/DoS/deauth_attack/cpp
mkdir build && cd build
cmake ..
make
sudo ./deauth --help
```

### JavaScript/Node.js (Web Integration)
**Best for**: Web dashboards, API integration, cross-platform
**Libraries**: `noble`, `bleno`, `node-wifi`, `cap`

```bash
cd Implementations/BLE/DoS/att_write_flood/javascript
npm install
node att_write_flood.js --help
```

### C# (Windows Native)
**Best for**: Windows environments, .NET integration
**Libraries**: `SharpPcap`, `PacketDotNet`, Windows.Devices.Bluetooth

```bash
cd Implementations/WiFi/DoS/deauth_attack/csharp
dotnet build
sudo dotnet run -- --help
```

### Java (Cross-Platform)
**Best for**: Android integration, desktop apps
**Libraries**: `jNetPcap`, `Pcap4J`, Android BluetoothGatt

```bash
cd Implementations/WiFi/DoS/deauth_attack/java
mvn package
sudo java -jar target/deauth-attack.jar --help
```

### Go (Concurrent Operations)
**Best for**: Modern systems programming, goroutines
**Libraries**: `gopacket`, `go-ble`

```bash
cd Implementations/WiFi/DoS/deauth_attack/go
go build
sudo ./deauth --help
```

---

## 🛡️ Safety & Ethics

### ⚠️ CRITICAL WARNING

All implementations in this repository are intended for:
- **Educational purposes** in controlled lab environments
- **Authorized penetration testing** with written permission
- **Defensive security research** to build better protections
- **Dataset generation** for machine learning IDS development

### Legal Requirements

1. ✅ **Obtain written authorization** before testing on any network/device
2. ✅ **Use only in isolated lab environments** (Faraday cage recommended)
3. ✅ **Comply with local laws** (illegal in many jurisdictions without permission)
4. ✅ **Log all attack execution** for audit trails
5. ❌ **NEVER use on production networks** without explicit authorization

### Built-in Safety Features

Every attack implementation includes:
- **Authorization check prompts** before execution
- **Rate limiting** to prevent excessive impact
- **Logging** of all actions for accountability
- **Kill switches** (Ctrl+C handling)
- **Maximum duration limits** (default: 60 seconds)

---

## 📈 Attack Catalog

### WiFi Attacks (15 Vectors)

#### DoS Attacks
1. **Deauthentication** - Spoofed deauth frames to disconnect clients
2. **Disassociation** - Spoofed disassoc frames
3. **Beacon Flooding** - Fake AP beacon spam
4. **CTS/RTS Flooding** - Control frame abuse
5. **Authentication Flooding** - Auth request exhaustion
6. **Association Flooding** - Assoc request exhaustion
7. **Virtual Carrier Sense** - NAV manipulation

#### MITM Attacks
8. **Evil Twin** - Rogue AP with legitimate SSID
9. **Karma Attack** - Respond to all probe requests
10. **Rogue AP** - Malicious access point deployment

#### Injection Attacks
11. **Packet Injection** - Arbitrary 802.11 frame crafting
12. **ARP Poisoning** - ARP cache poisoning
13. **DNS Spoofing** - DNS response manipulation
14. **Frame Manipulation** - Modify frames in transit
15. **SSL Stripping** - Downgrade HTTPS to HTTP

### BLE Attacks (25 Vectors)

#### DoS Attacks
1. **ATT Write Flood** - Overwhelming write commands (primary)
2. **Advertising Flood** - Rapid ADV_IND packet spam
3. **Connection Request Flood** - Connection exhaustion
4. **Scan Response Amplification** - SCAN_REQ reflection
5. **Connection Parameter Abuse** - Invalid param updates
6. **Retransmission Storm** - SN/NESN manipulation
7. **Notification Flood** - GATT notification spam
8. **Indication Flood** - GATT indication spam
9. **SMP Pairing Spam** - Pairing request flood
10. **L2CAP Signaling Storm** - Signaling channel abuse
11. **ATT Read Flood** - Read request exhaustion
12. **Empty Packet Flood** - Zero-payload LL packets
13. **Address Rotation Flood** - Rapid MAC changes

#### MITM Attacks
14. **Pairing Interception** - Capture pairing process
15. **Connection Hijacking** - Take over active connection
16. **Data Manipulation** - Modify encrypted data

#### Injection Attacks
17. **Packet Crafting** - Custom BLE packet injection
18. **Protocol Fuzzing** - Malformed packet testing
19. **Malformed AdvData** - Invalid advertising data

### Zigbee Attacks (20 Vectors)

#### DoS Attacks
1. **RF Jamming** - 2.4 GHz spectrum denial
2. **Beacon Flooding** - Fake coordinator beacons
3. **Association Request Flooding** - Network join exhaustion
4. **ACK Spoofing** - Acknowledgment manipulation
5. **PAN ID Conflict** - Conflicting PAN identifiers

#### MITM Attacks
6. **Malicious Coordinator** - Fake PAN deployment
7. **Touchlink Commissioning MITM** - Intercept commissioning
8. **Key Transport Interception** - Capture key exchange
9. **Router Impersonation** - Fake routing node

#### Injection Attacks
10. **ZCL On/Off Injection** - Light control commands
11. **ZCL Level Control** - Dimming command injection
12. **Replay Attacks** - Captured packet replay
13. **Malicious OTA Firmware** - Firmware update injection
14. **Routing Manipulation** - Alter routing tables

#### Key Extraction
15. **Default Key Exploitation** - "ZigBeeAlliance09" usage
16. **Insecure Rejoin** - Rejoin attack for keys
17. **Touchlink Factory Reset** - Device reset via touchlink

### LoRa Attacks (20 Vectors)

#### DoS Attacks
1. **Join Request Flooding** - OTAA join exhaustion
2. **Uplink Flooding** - Excessive device transmissions
3. **Collision Attacks** - Overlapping transmissions
4. **RF Jamming** - 868/915 MHz jamming
5. **Acknowledgment Flooding** - ACK spam to gateway

#### MITM Attacks
6. **Rogue Gateway** - Fake LoRaWAN gateway
7. **Wormhole Attack** - Relay attacks between distant nodes
8. **Join Accept Manipulation** - Modify join accept messages
9. **Downlink Injection** - Inject gateway downlinks
10. **Replay Attacks** - Packet replay with counter manipulation

#### Injection Attacks
11. **Malicious Uplink** - Craft arbitrary uplink frames
12. **Downlink Command Injection** - MAC command injection
13. **Payload Fuzzing** - Fuzz application payloads
14. **MAC Command Injection** - DevStatus, LinkCheck commands
15. **Application Payload Injection** - LoRaWAN port injection

---

## 🔬 Usage Examples

### WiFi: Deauthentication Attack

```bash
# Python 3.10 version
cd Implementations/WiFi/DoS/deauth_attack/python/python310

# Target specific client
sudo python deauth.py \
    --interface wlan0mon \
    --bssid AA:BB:CC:DD:EE:FF \
    --client 11:22:33:44:55:66 \
    --duration 30 \
    --rate 10

# Broadcast deauth (all clients)
sudo python deauth.py \
    --interface wlan0mon \
    --bssid AA:BB:CC:DD:EE:FF \
    --broadcast \
    --duration 60
```

### BLE: ATT Write Flood

```bash
# Python 3.11+ (fastest)
cd Implementations/BLE/DoS/att_write_flood/python/python311plus

# Flood with maximum MTU
sudo python att_write_flood.py \
    --target AA:BB:CC:DD:EE:FF \
    --handle 0x0010 \
    --payload-size 512 \
    --rate 100 \
    --duration 60 \
    --capture  # Optional: auto-capture traffic
```

### Zigbee: Malicious Coordinator

```bash
# Python implementation
cd Implementations/Zigbee/MITM/malicious_coordinator/python/python310

# Deploy fake PAN
sudo python malicious_coordinator.py \
    --channel 15 \
    --panid 0x1234 \
    --extended-panid 00:11:22:33:44:55:66:77 \
    --allow-joins \
    --duration 300
```

### LoRa: Join Request Flood

```bash
# Python with GNU Radio
cd Implementations/LoRa/DoS/join_request_flood/python/python310

# Flood network server with join requests
python join_flood.py \
    --deveui 00:00:00:00:00:00:00:01 \
    --appeui 01:01:01:01:01:01:01:01 \
    --frequency 868.1 \
    --spreading-factor 7 \
    --rate 10 \
    --duration 120
```

---

## 📖 Documentation

### Per-Attack Documentation
Each attack implementation includes:
- **README.md** - Usage guide, requirements, ethical warnings
- **version_comparison.md** (Python) - Feature/performance differences
- **COMPARISON.md** - Cross-language comparison
- **config.yaml** - Default parameters
- **requirements.txt** / **package.json** / **pom.xml** - Dependencies

### Cross-Cutting Documentation
- **[Python Version Comparison](../Docs/PythonVersionComparison.md)** - Detailed 3.8 vs 3.10 vs 3.11+ analysis
- **[Language Performance Benchmarks](../Docs/LanguagePerformanceBenchmarks.md)** - Speed/memory comparisons
- **[Attack Matrix](../Docs/AttackMatrixComplete.md)** - Complete protocol × attack × language grid
- **[Library Selection Guide](../Docs/LibrarySelection.md)** - Why each library was chosen

---

## 🔧 Development

### Adding a New Attack

```bash
# Create directory structure
mkdir -p Implementations/WiFi/DoS/new_attack/{python,c,cpp,javascript,csharp,java,go}

# Implement in Python first (reference)
vim Implementations/WiFi/DoS/new_attack/python/python310/new_attack.py

# Port to other languages
# ... implement in C, C++, JS, C#, Java, Go

# Add comparison documentation
vim Implementations/WiFi/DoS/new_attack/COMPARISON.md
```

### Running Tests

```bash
# Python unit tests
pytest Infrastructure/HardwareValidation/test_suites/

# Hardware validation
wsr-validate --protocol all

# Performance benchmarks
wsr-benchmark --attack WiFi/DoS/deauth_attack --language all
```

---

## 🤝 Contributing

We welcome contributions! Please:
1. Follow existing code structure (7 languages per attack)
2. Include ethical warnings in all scripts
3. Add comprehensive documentation
4. Test on actual hardware before PR
5. Update attack matrix documentation

---

## 📝 License

**Educational/Research Use Only**

This software is provided for educational and authorized security research purposes only. Unauthorized use against networks or devices you do not own or have explicit written permission to test is illegal and unethical.

By using this software, you agree to:
- Only use in controlled lab environments or with written authorization
- Comply with all applicable laws and regulations
- Not use for malicious purposes
- Take responsibility for your actions

See [LICENSE](../LICENSE) for full terms.

---

## 🔗 Related

- [Main README](../README.md) - Project overview
- [Protocol Documentation](../) - Theoretical analysis (WiFi/, BLE/, Zigbee/, LoRa/)
- [Infrastructure Tools](../Infrastructure/) - Traffic capture, dataset pipeline
- [Docker Setup](../Infrastructure/Docker/) - Containerized environments

---

**Built with ❤️ for defensive security research and ML-based intrusion detection**
