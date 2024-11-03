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

const int SAMPLE_INTERVAL = 50;         // Sampling interval
const int HEART_RATE_WINDOW = 5000;     // 5-second window for heart rate
const int PEAK_THRESHOLD = 5;           // test for this
const int RUNNING_AVERAGE_WINDOW = 10;  // Number of samples for running average

unsigned long last_sample_time = 0;
float photo_values[RUNNING_AVERAGE_WINDOW] = {0};
int photo_index = 0;
int peak_count = 0;
unsigned long last_peak_time = 0;
float heart_rate = 0;

// Task handles
TaskHandle_t photoTaskHandle = NULL;
TaskHandle_t distanceTaskHandle = NULL;

void setup() {
  Serial.begin(115200);
  pinMode(photoresistorPin, INPUT);
  pinMode(trig_pin, OUTPUT);
  pinMode(echo_pin, INPUT);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to Wi-Fi...");
  }
  
  Serial.println("Connected to Wi-Fi");
  server.begin();
  Serial.print("Server started at: ");
  Serial.println(WiFi.localIP());

  // Create tasks for photoresistor and distance calculations
  xTaskCreatePinnedToCore(photoTask, "PhotoTask", 4096, NULL, 1, &photoTaskHandle, 0);  // Run on Core 0
  xTaskCreatePinnedToCore(distanceTask, "DistanceTask", 4096, NULL, 1, &distanceTaskHandle, 1);  // Run on Core 1
}

void loop() {
  WiFiClient client = server.available();  // Listen for incoming clients

  if (client) {
    Serial.println("Client connected");
    client.println("Distance (cm): "+ String(distance_cm));
    client.println("Heart Rate (BPM): " + String(heart_rate));
    client.stop();  // Close the connection
  }

  delay(100);  // Adjust this delay as needed
}

void distanceTask(void * parameter) {
  while (true) {
    // Set up the signal
    digitalWrite(trig_pin, LOW);
    delayMicroseconds(2);
    digitalWrite(trig_pin, HIGH);
    delayMicroseconds(TRIG_PULSE_DURATION_US);
    digitalWrite(trig_pin, LOW);

    // Return the wave propagation time (in µs)
    ultrason_duration = pulseIn(echo_pin, HIGH);

    // Distance calculation
    distance_cm = ultrason_duration * SOUND_SPEED / 2 * 0.0001;

    Serial.print("Distance: ");
    Serial.println(distance_cm);

    vTaskDelay(100);
  }
}

void photoTask(void * parameter) {
  while (true) {
    // Sample photoresistor data and calculate running average
    if (millis() - last_sample_time >= SAMPLE_INTERVAL) {
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
      if (photo_value > avg_value + PEAK_THRESHOLD && millis() - last_peak_time > 100) {
        peak_count++;
        last_peak_time = millis();
        Serial.println("Heartbeat detected");
      }

      // Calculate heart rate (BPM) over the 5-second window
      if (millis() - last_sample_time >= HEART_RATE_WINDOW) {
        last_sample_time = millis();
        heart_rate = (peak_count * 60000.0) / HEART_RATE_WINDOW;
        Serial.println("heart rate updated!");
        Serial.println(heart_rate);
        peak_count = 0;
      }

      Serial.print("Heart Rate: ");
      Serial.print(heart_rate);
      Serial.println(" BPM");
    }

    vTaskDelay(SAMPLE_INTERVAL / portTICK_PERIOD_MS);  // Delay for sampling interval
  }
}
