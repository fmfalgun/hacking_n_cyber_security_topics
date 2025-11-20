# BLE Attack Research Platform - Dockerfile
# ==========================================
# Container for BLE security research with BlueZ and tools

FROM kalilinux/kali-rolling:latest

LABEL maintainer="Wireless Security Research"
LABEL description="BLE Attack Research Platform"
LABEL version="1.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV PROTOCOL=BLE
ENV WORKSPACE=/workspace
ENV LANG=C.UTF-8

# Update and install base packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    git \
    wget \
    python3 \
    python3-pip \
    python3-dev \
    # Bluetooth tools
    bluez \
    bluez-tools \
    bluetooth \
    libbluetooth-dev \
    # HCI tools
    btmon \
    hcitool \
    hciconfig \
    hcidump \
    gatttool \
    # Libraries
    libglib2.0-dev \
    libdbus-1-dev \
    libical-dev \
    libreadline-dev \
    libudev-dev \
    # Packet capture
    wireshark \
    tshark \
    # Utilities
    vim \
    nano \
    tmux \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install --no-cache-dir \
    scapy>=2.5.0 \
    bleak>=0.21.0 \
    bluepy>=1.3.0 \
    pybluez>=0.23 \
    pyshark>=0.6.0 \
    pandas>=2.0.0 \
    numpy>=1.24.0 \
    pyyaml>=6.0 \
    click>=8.1.0 \
    colorama>=0.4.6

# Install Ubertooth tools (if hardware available)
RUN git clone https://github.com/greatscottgadgets/ubertooth.git /tmp/ubertooth && \
    cd /tmp/ubertooth/host && \
    mkdir build && cd build && \
    cmake .. && make && make install && \
    ldconfig && \
    rm -rf /tmp/ubertooth

# Create workspace
RUN mkdir -p $WORKSPACE/ble \
             $WORKSPACE/datasets \
             $WORKSPACE/infrastructure

WORKDIR $WORKSPACE

# Start D-Bus (required for BlueZ)
RUN mkdir -p /run/dbus

EXPOSE 8000 8080

CMD ["/bin/bash", "-c", "dbus-daemon --system && /bin/bash"]
