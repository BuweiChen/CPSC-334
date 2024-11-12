#include <WiFi.h>
#include <esp_now.h>

// MAC addresses for each ESP32 in the mesh network
uint8_t esp1_address[] = {0x24, 0x0A, 0xC4, 0xAB, 0x12, 0x34}; // Replace with ESP1's actual MAC address
uint8_t esp2_address[] = {0x24, 0x0A, 0xC4, 0xAB, 0x12, 0x35}; // Replace with ESP2's actual MAC address
uint8_t esp3_address[] = {0x24, 0x0A, 0xC4, 0xAB, 0x12, 0x36}; // Replace with ESP3's actual MAC address

int resp_flag = 1; // 0 is idle, 1 is receive, 2 is broadcast
const int RLED = 2;  // Red LED pin
const int GLED = 3;  // Green LED pin
const int button1 = 4; // reset button pin
const int button2 = 5; // Send message button pin
const uint8_t ID = 1; // 1, 2, or 3, different per device

// Message structure
typedef struct {
    uint8_t sender_id;
    uint8_t message_type; // 0 for broadcasting, 1 for returning
} message_t;

void onDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
    // message_t message;
    // message.sender_id = ID;
    // message.message_type = resp_flag;
    // esp_now_send(esp1_address, (uint8_t *)&message, sizeof(message));

}

void onDataReceived(const uint8_t *mac_addr, const uint8_t *data, int len) {
    // if resp_flag is 0, then do nothing
    if (resp_flag == 0)
    {
        return;
    }
    
    resp_flag = 0;
		
    message_t received_message;
    memcpy(&received_message, data, sizeof(received_message));


    
    if (resp_flag == 2 && received_message.message_type == 1) {
        
        
        // this is all hardcoded, should be different for each device
        if (received_message.sender_id == 1) {
            digitalWrite(RLED, HIGH);  // Turn on Red LED if message from ESP2
            digitalWrite(GLED, LOW);   // Turn off Green LED
        } else if (received_message.sender_id == 2) {
            digitalWrite(GLED, HIGH);  // Turn on Green LED if message from ESP3
            digitalWrite(RLED, LOW);   // Turn off Red LED
        }
    } else if (resp_flag == 1 && received_message.message_type == 0) {
        digitalWrite(RLED, HIGH);  // Turn on Red LED if message from ESP2
        digitalWrite(GLED, LOW);   // Turn off Green LED
        
    }
}

void setup() {
    Serial.begin(115200);
    
    pinMode(RLED, OUTPUT);
    pinMode(GLED, OUTPUT);
    pinMode(button1, INPUT_PULLUP);
    pinMode(button2, INPUT_PULLUP);

    WiFi.mode(WIFI_STA);
    if (esp_now_init() != ESP_OK) {
        Serial.println("Error initializing ESP-NOW");
        return;
    }
    esp_now_register_send_cb(onDataSent);
    esp_now_register_recv_cb(onDataReceived);

    esp_now_peer_info_t peerInfo = {};
    memcpy(peerInfo.peer_addr, esp2_address, 6);
    peerInfo.channel = 0;
    peerInfo.encrypt = false;

    // Register peers
    esp_now_add_peer(&peerInfo);
    memcpy(peerInfo.peer_addr, esp3_address, 6);
    esp_now_add_peer(&peerInfo);
}

void loop() {
    if (digitalRead(button1) == LOW) {
        resp_flag = 1;
        response = 0;
        delay(200); // Debounce delay
    }

    if (digitalRead(button2) == LOW) {
        message_t message;
        message.sender_id = ID;
        message.message_type = resp_flag;
        memcpy(message.sender_address, esp1_address, 6);
        esp_now_send(esp1_address, (uint8_t *)&message, sizeof(message));
        
        delay(200); // Debounce delay
    }
}

