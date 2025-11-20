# Makefile for WiFi Beacon Flood Attack (C Implementation)
# ===========================================================

# Compiler and flags
CC = gcc
CFLAGS = -Wall -Wextra -O3 -std=c11
LDFLAGS = -lpcap

# Debug flags
DEBUG_CFLAGS = -Wall -Wextra -g -O0 -std=c11 -DDEBUG -fsanitize=address -fsanitize=undefined
DEBUG_LDFLAGS = -lpcap -fsanitize=address -fsanitize=undefined

# Directories
PREFIX = /usr/local
BINDIR = $(PREFIX)/bin

# Target
TARGET = beacon_flood
TEST_TARGET = test_beacon_flood

# Source files
SRC = beacon_flood.c
TEST_SRC = test_beacon_flood.c
OBJ = $(SRC:.c=.o)
TEST_OBJ = $(TEST_SRC:.c=.o)

# ============================================================================
# Build Targets
# ============================================================================

.PHONY: all clean install uninstall debug test help

# Default target
all: $(TARGET)

# Production build
$(TARGET): $(SRC)
	@echo "[+] Building $(TARGET) (optimized)..."
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) $(LDFLAGS)
	@echo "[+] Build complete: ./$(TARGET)"

# Debug build
debug: $(SRC)
	@echo "[+] Building $(TARGET) (debug mode with sanitizers)..."
	$(CC) $(DEBUG_CFLAGS) -o $(TARGET) $(SRC) $(DEBUG_LDFLAGS)
	@echo "[+] Debug build complete: ./$(TARGET)"

# Test build
test: $(TEST_SRC)
	@echo "[+] Building test suite..."
	@if [ ! -f $(TEST_SRC) ]; then \
		echo "[!] Test file $(TEST_SRC) not found"; \
		echo "[*] Skipping tests..."; \
	else \
		$(CC) $(CFLAGS) -o $(TEST_TARGET) $(TEST_SRC) $(LDFLAGS); \
		echo "[+] Test build complete: ./$(TEST_TARGET)"; \
		echo "[+] Running tests..."; \
		sudo ./$(TEST_TARGET); \
	fi

# Install
install: $(TARGET)
	@echo "[+] Installing $(TARGET) to $(BINDIR)..."
	@install -d $(BINDIR)
	@install -m 0755 $(TARGET) $(BINDIR)
	@echo "[+] Installed: $(BINDIR)/$(TARGET)"

# Uninstall
uninstall:
	@echo "[+] Removing $(TARGET) from $(BINDIR)..."
	@rm -f $(BINDIR)/$(TARGET)
	@echo "[+] Uninstalled"

# Clean
clean:
	@echo "[+] Cleaning build artifacts..."
	@rm -f $(TARGET) $(TEST_TARGET) $(OBJ) $(TEST_OBJ) core
	@echo "[+] Clean complete"

# Help
help:
	@echo "WiFi Beacon Flood - Makefile"
	@echo "=============================="
	@echo ""
	@echo "Targets:"
	@echo "  make                 Build optimized release version"
	@echo "  make debug           Build debug version with sanitizers"
	@echo "  make test            Build and run test suite"
	@echo "  make install         Install to $(BINDIR) (requires sudo)"
	@echo "  make uninstall       Remove from $(BINDIR) (requires sudo)"
	@echo "  make clean           Remove build artifacts"
	@echo "  make help            Show this help message"
	@echo ""
	@echo "Usage:"
	@echo "  sudo ./$(TARGET) -i wlan0mon --random-ssids"
	@echo "  sudo ./$(TARGET) -i wlan0mon --ssid \"FakeAP\" --random-bssid"
	@echo "  sudo ./$(TARGET) -i wlan0mon --rate 5000 --count 100000"
	@echo ""
	@echo "Requirements:"
	@echo "  - libpcap-dev"
	@echo "  - Monitor mode wireless interface"
	@echo "  - Root privileges"
	@echo ""
	@echo "Install dependencies:"
	@echo "  sudo apt-get install libpcap-dev"
	@echo ""
