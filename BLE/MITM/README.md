---
title: BLE MITM Attacks
tags: [BLE, MITM, man-in-the-middle, interception]
category: BLE Security
parent: "[[BLE/README]]"
status: active
---

# BLE Man-in-the-Middle (MITM) Attacks

## Overview

Man-in-the-Middle attacks on BLE involve intercepting and potentially manipulating communications between two devices during pairing, connection, or data exchange phases.

## Attack Vectors

### 1. Pairing MITM
- **Just Works** pairing exploitation (no authentication)
- Numeric comparison manipulation
- Passkey entry interception
- OOB (Out-of-Band) data interception

### 2. Connection Hijacking
- Connection parameter manipulation
- Session token theft
- Re-pairing attacks

### 3. Data Interception
- Unencrypted attribute reads/writes
- Downgrade attacks (force unencrypted communication)
- Characteristic value manipulation

## Tools & Techniques

- **GATTacker**: BLE MITM framework
- **BTLEJack**: BLE connection hijacking
- **Ubertooth**: Hardware-based interception
- **btproxy**: BLE proxy for MITM testing

## Implementation

Detailed implementation guides coming from analysis of existing research.

---
**Related**: [[BLE/DoS/README|BLE DoS]] • [[BLE/Injection/README|BLE Injection]] • [[BLE/README|BLE Home]]
