# All-in-One Wireless Research Platform - Dockerfile
# ===================================================
# Complete environment for WiFi, BLE, Zigbee, and LoRa research

FROM kalilinux/kali-rolling:latest

LABEL maintainer="Wireless Security Research"
LABEL description="All-in-One Wireless Research Platform"
LABEL version="1.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV WORKSPACE=/workspace
ENV LANG=C.UTF-8

# ============================================================================
# Base System
# ============================================================================

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    git \
    wget \
    curl \
    python3 \
    python3-pip \
    python3-dev \
    vim \
    nano \
    tmux \
    screen \
    htop \
    && apt-get clean

# ============================================================================
# WiFi Tools
# ============================================================================

RUN apt-get update && apt-get install -y \
    iproute2 \
    wireless-tools \
    iw \
    rfkill \
    aircrack-ng \
    tcpdump \
    wireshark \
    tshark \
    libpcap-dev \
    && apt-get clean

# ============================================================================
# BLE Tools
# ============================================================================

RUN apt-get update && apt-get install -y \
    bluez \
    bluez-tools \
    bluetooth \
    libbluetooth-dev \
    btmon \
    hcitool \
    && apt-get clean

# ============================================================================
# Zigbee Tools
# ============================================================================

RUN apt-get update && apt-get install -y \
    libusb-1.0-0-dev \
    libgcrypt20-dev \
    && apt-get clean

# Install KillerBee (Zigbee toolkit)
RUN git clone https://github.com/riverloopsec/killerbee.git /tmp/killerbee && \
    cd /tmp/killerbee && \
    pip3 install . && \
    rm -rf /tmp/killerbee

# ============================================================================
# LoRa Tools
# ============================================================================

# GNU Radio for SDR (if using HackRF/LimeSDR)
RUN apt-get update && apt-get install -y \
    gnuradio \
    gr-osmosdr \
    && apt-get clean

# ============================================================================
# Python Packages
# ============================================================================

RUN pip3 install --no-cache-dir \
    # Core
    scapy>=2.5.0 \
    pyshark>=0.6.0 \
    pandas>=2.0.0 \
    numpy>=1.24.0 \
    pyyaml>=6.0 \
    # WiFi
    pyric>=0.1.6.3 \
    netifaces>=0.11.0 \
    # BLE
    bleak>=0.21.0 \
    bluepy>=1.3.0 \
    pybluez>=0.23 \
    # LoRa
    pyserial>=3.5 \
    pycryptodome>=3.18.0 \
    # ML/Dataset
    scikit-learn>=1.3.0 \
    matplotlib>=3.7.0 \
    seaborn>=0.12.0 \
    joblib>=1.3.0 \
    pyarrow>=12.0.0 \
    # Utilities
    click>=8.1.0 \
    colorama>=0.4.6 \
    tqdm>=4.65.0 \
    rich>=13.4.0

# ============================================================================
# Jupyter (optional for analysis)
# ============================================================================

RUN pip3 install --no-cache-dir \
    jupyter>=1.0.0 \
    jupyterlab>=4.0.0 \
    ipython>=8.14.0

# ============================================================================
# Workspace Setup
# ============================================================================

RUN mkdir -p $WORKSPACE/implementations \
             $WORKSPACE/datasets \
             $WORKSPACE/infrastructure \
             $WORKSPACE/models

WORKDIR $WORKSPACE

# ============================================================================
# Ports
# ============================================================================

# Jupyter Lab
EXPOSE 8888
# TensorBoard
EXPOSE 6006
# Custom web services
EXPOSE 8000 8080

# ============================================================================
# Startup
# ============================================================================

# Start D-Bus for BlueZ
RUN mkdir -p /run/dbus

# Create startup script
RUN echo '#!/bin/bash\n\
dbus-daemon --system\n\
echo "================================================================="\n\
echo "  Wireless Security Research Platform"\n\
echo "================================================================="\n\
echo "Protocols: WiFi | BLE | Zigbee | LoRa"\n\
echo "Workspace: /workspace"\n\
echo ""\n\
echo "Quick Start:"\n\
echo "  cd /workspace/implementations"\n\
echo "  python3 generate_implementations.py --help"\n\
echo "================================================================="\n\
/bin/bash\n\
' > /entrypoint.sh && chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
