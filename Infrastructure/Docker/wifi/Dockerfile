# WiFi Attack Research Platform - Dockerfile
# ==========================================
# Container for WiFi (802.11) security research with all tools and implementations

FROM kalilinux/kali-rolling:latest

# Metadata
LABEL maintainer="Wireless Security Research"
LABEL description="WiFi Attack Research Platform"
LABEL version="1.0"

# Set environment
ENV DEBIAN_FRONTEND=noninteractive
ENV PROTOCOL=WiFi
ENV WORKSPACE=/workspace
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Update and install base packages
RUN apt-get update && apt-get install -y \
    # Build essentials
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    git \
    wget \
    curl \
    # Python
    python3 \
    python3-pip \
    python3-dev \
    # Networking tools
    iproute2 \
    wireless-tools \
    net-tools \
    iw \
    rfkill \
    # WiFi specific tools
    aircrack-ng \
    airmon-ng \
    aireplay-ng \
    airodump-ng \
    # Packet capture
    tcpdump \
    wireshark \
    tshark \
    # Libraries
    libpcap-dev \
    libssl-dev \
    libnl-3-dev \
    libnl-genl-3-dev \
    # Utilities
    vim \
    nano \
    tmux \
    screen \
    htop \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install --no-cache-dir \
    scapy>=2.5.0 \
    pyshark>=0.6.0 \
    pandas>=2.0.0 \
    numpy>=1.24.0 \
    pyyaml>=6.0 \
    click>=8.1.0 \
    colorama>=0.4.6 \
    tqdm>=4.65.0 \
    pyric>=0.1.6.3 \
    netifaces>=0.11.0

# Create workspace
RUN mkdir -p $WORKSPACE/wifi \
             $WORKSPACE/datasets \
             $WORKSPACE/infrastructure

# Set working directory
WORKDIR $WORKSPACE

# Copy implementations and infrastructure (will be mounted)
# COPY Implementations/WiFi /workspace/wifi
# COPY Infrastructure /workspace/infrastructure

# Expose ports (if needed for web interfaces)
EXPOSE 8000 8080

# Default command
CMD ["/bin/bash"]
