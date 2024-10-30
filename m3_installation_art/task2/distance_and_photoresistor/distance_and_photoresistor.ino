#include <WiFi.h>

const char* ssid = "yale wireless";
const char* password = "";

#define SOUND_SPEED 340
#define TRIG_PULSE_DURATION_US 10

WiFiServer server(80);

const int photoresistorPin = 34;
const int trig_pin = 26;
const int echo_pin = 25;

long ultrason_duration;
float distance_cm;

const int SAMPLE_INTERVAL = 50;   // Sampling interval
const int HEART_RATE_WINDOW = 5000;  // 5-second window for heart rate
const int PEAK_THRESHOLD = 100; // test for this
const int RUNNING_AVERAGE_WINDOW = 10;  // Number of samples for running average

unsigned long last_sample_time = 0;
float photo_values[RUNNING_AVERAGE_WINDOW] = {0};
int photo_index = 0;
int peak_count = 0;
unsigned long last_peak_time = 0;
float heart_rate = 0;

void setup() {
  Serial.begin(115200);
  pinMode(photoresistorPin, INPUT);
  pinMode(trig_pin, OUTPUT);
  pinMode(echo_pin, INPUT);

  // Connect to wifi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to Wi-Fi...");
  }
  
  Serial.println("Connected to Wi-Fi");
  server.begin();
  Serial.print("Server started at: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Set up the signal
  digitalWrite(trig_pin, LOW);
  delayMicroseconds(2);
  // Create a 10 µs impulse
  digitalWrite(trig_pin, HIGH);
  delayMicroseconds(TRIG_PULSE_DURATION_US);
  digitalWrite(trig_pin, LOW);

  // Return the wave propagation time (in µs)
  ultrason_duration = pulseIn(echo_pin, HIGH);

  // distance calculation
  distance_cm = ultrason_duration * SOUND_SPEED/2 * 0.0001;

  Serial.print("Distance: ");
  Serial.println(distance_cm);


  // Sample photoresistor data and calculate running average
  if (millis() - last_sample_time >= SAMPLE_INTERVAL) {
    last_sample_time = millis();
    
    // Read photoresistor value and update running average buffer
    float photo_value = analogRead(photoresistorPin);
    photo_values[photo_index] = photo_value;
    photo_index = (photo_index + 1) % RUNNING_AVERAGE_WINDOW;

    // Calculate running average
    float avg_value = 0;
    for (int i = 0; i < RUNNING_AVERAGE_WINDOW; i++) {
      avg_value += photo_values[i];
    }
    avg_value /= RUNNING_AVERAGE_WINDOW;

    // Detect peak based on the threshold and timing
    if (photo_value > avg_value + PEAK_THRESHOLD && millis() - last_peak_time > 250) {  // 250 ms debounce to avoid false peaks, also means we don't measure anything higher than 240 bpm
      peak_count++;
      last_peak_time = millis();
      Serial.println("Heartbeat detected");
    }

    // Calculate heart rate (BPM) over the 5-second window
    if (millis() - last_sample_time >= HEART_RATE_WINDOW) {
      heart_rate = (peak_count * 60000.0) / HEART_RATE_WINDOW;  // Convert to BPM
      peak_count = 0;  // Reset peak count for the next interval
    }
    
    Serial.print("Heart Rate: ");
    Serial.print(heart_rate);
    Serial.println(" BPM");
  }

  WiFiClient client = server.available();  // Listen for incoming clients

  if (client) {
    Serial.println("Client connected");
    client.println(String(distance_cm));
    client.println("Heart Rate (BPM): " + String(heart_rate));
    client.stop();  // Close the connection
  }
  delay(10);
}
