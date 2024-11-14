#include "WiFi.h"
#include <esp_now.h>
#include <esp_mac.h> // For MAC2STR and MACSTR macros

/* Definitions */
#define ESPNOW_WIFI_CHANNEL 7
#define ESPNOW_WIFI_IFACE WIFI_IF_STA
#define ESPNOW_EXAMPLE_PMK "pmk1234567890123"

// Device-specific configuration
#define DEVICE_ID 3 // Set this to 1, 2, or 3 for each device

// GPIO Pins
#define BROADCAST_BUTTON_PIN 4
#define RESET_BUTTON_PIN 5
#define LED_RED_PIN 12
#define LED_GREEN_PIN 14

/* Hardcoded MAC Addresses (replace with actual MACs of the devices) */
const uint8_t DEVICE1_MAC[6] = {0x48, 0xE7, 0x29, 0x3F, 0xC4, 0x14};
const uint8_t DEVICE2_MAC[6] = {0xE8, 0x68, 0xE7, 0x30, 0x61, 0x44};
// e8:68:e7:30:2c:2c
// const uint8_t DEVICE2_MAC[6] = {0xE8, 0x68, 0xE7, 0x30, 0x2c, 0x2c};
const uint8_t DEVICE3_MAC[6] = {0x48, 0xE7, 0x29, 0x3F, 0x88, 0x6C};

/* Message Structure */
typedef struct {
    uint8_t sender_mac[6];   // Sender's MAC address
    uint8_t message_type;    // 0 = Broadcast, 1 = Return call
    uint8_t led_color;       // Sender's LED color (0 = red, 1 = green)
} __attribute__((packed)) message_t;

/* Global Variables */
volatile bool broadcast_triggered = false;
volatile bool reset_triggered = false;
bool can_receive_broadcasts = true; // Determines if the device can receive broadcasts

/* Function Prototypes */
void IRAM_ATTR onBroadcastButtonPress();
void IRAM_ATTR onResetButtonPress();
void broadcastMessage();
void sendReturnMessage(const uint8_t *receiver_mac, uint8_t led_color);
void resetDevice();
void lightLED(uint8_t led_color);
bool isValidMAC(const uint8_t *mac);
void onDataReceive(const esp_now_recv_info_t *recv_info, const uint8_t *data, int len);

/* Callbacks */
void onDataReceive(const esp_now_recv_info_t *recv_info, const uint8_t *data, int len) {
    if (len != sizeof(message_t)) {
        Serial.println("Invalid message length. Ignoring.");
        return;
    }

    message_t *msg = (message_t *)data;

    // Validate MAC address
    if (!isValidMAC(recv_info->src_addr)) {
        Serial.println("Invalid sender MAC. Ignoring.");
        return;
    }

    if (msg->message_type == 0 && can_receive_broadcasts) { // Broadcast
        Serial.printf("Received broadcast from " MACSTR "\n", MAC2STR(recv_info->src_addr));

        // Light up LED based on the sender
        if (memcmp(recv_info->src_addr, DEVICE1_MAC, 6) == 0) {
            lightLED((DEVICE_ID == 2) ? 0 : 1); // Device 2 = Red, Device 3 = Green
        } else if (memcmp(recv_info->src_addr, DEVICE2_MAC, 6) == 0) {
            lightLED((DEVICE_ID == 1) ? 0 : 1); // Device 1 = Red, Device 3 = Green
        } else if (memcmp(recv_info->src_addr, DEVICE3_MAC, 6) == 0) {
            lightLED((DEVICE_ID == 1) ? 0 : 1); // Device 1 = Red, Device 2 = Green
        }

        // Send return message to the broadcasting device
        sendReturnMessage(recv_info->src_addr, (DEVICE_ID == 1) ? 0 : 1);
    } else if (msg->message_type == 1) { // Return call
        Serial.printf("Received return call from " MACSTR "\n", MAC2STR(recv_info->src_addr));

        // Broadcasting device lights up based on first return call
        if (DEVICE_ID == 1 && memcmp(recv_info->src_addr, DEVICE2_MAC, 6) == 0) {
            lightLED(0); // Red
        } else if (DEVICE_ID == 1 && memcmp(recv_info->src_addr, DEVICE3_MAC, 6) == 0) {
            lightLED(1); // Green
        } else if (DEVICE_ID == 2 && memcmp(recv_info->src_addr, DEVICE1_MAC, 6) == 0) {
            lightLED(0); // Red
        } else if (DEVICE_ID == 2 && memcmp(recv_info->src_addr, DEVICE3_MAC, 6) == 0) {
            lightLED(1); // Green
        } else if (DEVICE_ID == 3 && memcmp(recv_info->src_addr, DEVICE1_MAC, 6) == 0) {
            lightLED(0); // Red
        } else if (DEVICE_ID == 3 && memcmp(recv_info->src_addr, DEVICE2_MAC, 6) == 0) {
            lightLED(1); // Green
        }
    }
}

/* LED Control */
void lightLED(uint8_t led_color) {
    if (led_color == 0) { // Red
        digitalWrite(LED_RED_PIN, HIGH);
        digitalWrite(LED_GREEN_PIN, LOW);
    } else if (led_color == 1) { // Green
        digitalWrite(LED_RED_PIN, LOW);
        digitalWrite(LED_GREEN_PIN, HIGH);
    }
}

/* Broadcast Logic */
void broadcastMessage() {
    message_t msg;
    WiFi.macAddress(msg.sender_mac);
    msg.message_type = 0; // Broadcast
    msg.led_color = (DEVICE_ID == 1) ? 0 : 1; // Example: 0 = red, 1 = green

    if (esp_now_send(NULL, (uint8_t *)&msg, sizeof(msg)) != ESP_OK) { // NULL for broadcast
        Serial.println("Broadcast failed");
    } else {
        Serial.println("Broadcast sent successfully");
        can_receive_broadcasts = false; // Disable receiving further broadcasts
    }
}

/* Return Message Logic */
void sendReturnMessage(const uint8_t *receiver_mac, uint8_t led_color) {
    message_t msg;
    WiFi.macAddress(msg.sender_mac);
    msg.message_type = 1; // Return call
    msg.led_color = led_color;

    if (esp_now_send(receiver_mac, (uint8_t *)&msg, sizeof(msg)) != ESP_OK) {
        Serial.println("Return message failed");
    } else {
        Serial.println("Return message sent successfully");
    }
}

/* Reset Logic */
void resetDevice() {
    can_receive_broadcasts = true; // Enable receiving broadcasts
    digitalWrite(LED_RED_PIN, LOW);
    digitalWrite(LED_GREEN_PIN, LOW);
    Serial.println("Device reset to receiving mode");
}

/* Validate MAC Address */
bool isValidMAC(const uint8_t *mac) {
    return (memcmp(mac, DEVICE1_MAC, 6) == 0 ||
            memcmp(mac, DEVICE2_MAC, 6) == 0 ||
            memcmp(mac, DEVICE3_MAC, 6) == 0);
}

/* Interrupt Handlers */
void IRAM_ATTR onBroadcastButtonPress() {
    broadcast_triggered = true;
}

void IRAM_ATTR onResetButtonPress() {
    reset_triggered = true;
}

/* Setup */
void setup() {
    Serial.begin(115200);

    pinMode(LED_RED_PIN, OUTPUT);
    pinMode(LED_GREEN_PIN, OUTPUT);
    pinMode(BROADCAST_BUTTON_PIN, INPUT_PULLUP);
    pinMode(RESET_BUTTON_PIN, INPUT_PULLUP);

    attachInterrupt(BROADCAST_BUTTON_PIN, onBroadcastButtonPress, FALLING);
    attachInterrupt(RESET_BUTTON_PIN, onResetButtonPress, FALLING);

    // WiFi setup
    WiFi.mode(WIFI_STA);
    WiFi.setChannel(ESPNOW_WIFI_CHANNEL);

    // ESP-NOW setup
    if (esp_now_init() != ESP_OK) {
        Serial.println("Failed to initialize ESP-NOW");
        ESP.restart();
    }

    // Add broadcast MAC to the peer list
    uint8_t broadcast_mac[6] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
    esp_now_peer_info_t peer_info = {};
    memcpy(peer_info.peer_addr, broadcast_mac, 6);
    peer_info.channel = ESPNOW_WIFI_CHANNEL;
    peer_info.ifidx = ESPNOW_WIFI_IFACE;

    if (esp_now_add_peer(&peer_info) != ESP_OK) {
        Serial.println("Failed to add broadcast peer");
        ESP.restart();
    }

    // Add individual device MACs to the peer list
    uint8_t device_macs[3][6] = {
        {0x48, 0xE7, 0x29, 0x3F, 0xC4, 0x14}, // DEVICE1_MAC
        {0xE8, 0x68, 0xE7, 0x30, 0x61, 0x44}, // DEVICE2_MAC
        {0x48, 0xE7, 0x29, 0x3F, 0x88, 0x6C}  // DEVICE3_MAC
    };

    for (int i = 0; i < 3; i++) {
        memcpy(peer_info.peer_addr, device_macs[i], 6);
        if (esp_now_add_peer(&peer_info) != ESP_OK) {
            Serial.printf("Failed to add peer %d\n", i + 1);
            ESP.restart();
        }
    }

    esp_now_register_recv_cb(onDataReceive);

    Serial.println("Setup complete. Ready to receive broadcasts.");
}


/* Main Loop */
void loop() {
    if (broadcast_triggered) {
        broadcast_triggered = false;
        Serial.println("Broadcast button pressed. Broadcasting...");
        WiFi.setChannel(0);
        broadcastMessage();
        WiFi.setChannel(ESPNOW_WIFI_CHANNEL);
    }

    if (reset_triggered) {
        reset_triggered = false;
        Serial.println("Reset button pressed. Resetting device...");
        resetDevice();
    }
}
