# What's In the Box? Anxiety.

An artful visualization of social anxiety with the aid of Mr Incredible and the Gom Jabbar box. Module 3 submission for CPSC 334 (Creative Embedded Systems).

## Code Walkthrough

### Heartbeat Sensor

On the code side, I modularized the heartbeat sensor reading and distance sensor reading into two separate functions, `photoTask` and `distanceTask`, meant to run on separate threads. This is because the built in delay in the distance sensor meant that the two tasks needed to be run at different rates.

`photoTask` required frequent updates so we wouldn’t miss peaks in the readings and allowed the updates to sync up to various rhythms of pulses. Let’s take a deep dive into the code, starting with the global variables:

```cpp
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
```

The code is largely self-explanatory, but I think there’s a couple key points worth drawing. First is `PEAK_THRESHOLD` . This was the heart of the whole operation—how much does the new reading need to deviate from the running average (used to smooth out the variance) for it to be labeled as a peak? I eventually settled on 5, which at first glance seems like an outlandishly small threshold. However, it’s important to remember that I’ve constructed the environment to block out essentially all light noise, combined with the weak power of the LED light (and the trouble it has shining through the flesh), a low threshold is appropriate here.

Naturally, with such a low threshold, we need to account for the possibility of overcounting peaks. This is where `last_peak_time` comes in.

```cpp
if (photo_value > avg_value + PEAK_THRESHOLD && millis() - last_peak_time > 100) {
    peak_count++;
    last_peak_time = millis();
    Serial.println("Heartbeat detected");
}
```

The idea here is once we register a peak, we start a little “cooldown” to completely forgo the possibility of a trigger due to oversensitivity in that duration. Overall, this addition makes the counting more consistent.

The core logic of the heartbeat reading henceforth becomes: count the number of peaks for every 5 second interval, and once the 5 seconds has elapsed, extrapolate the count in the 5 seconds to approximate the BPM.

```cpp
if (millis() - last_sample_time >= HEART_RATE_WINDOW) {
    last_sample_time = millis();
    heart_rate = (peak_count * 60000.0) / HEART_RATE_WINDOW;
    Serial.println("heart rate updated!");
    Serial.println(heart_rate);
    peak_count = 0;
}
```

### Distance Sensor

The distance sensor is a ready-to-use component, so let’s dive right into the code. I followed the example in [this article](https://www.upesy.com/blogs/tutorials/hc-sr04-ultrasonic-sensor-on-esp32-with-arduino-code-tutorial?srsltid=AfmBOoq8IFD15nkOi2oqhg6wCD1X64Av7sW_8DK79ZPIsOHjssBS_XuR#google_vignette) to set it up.

```cpp
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
```

The code boils down to shoot out a sound wave → wait for it to return → calculate the distance based on time it took to return. Basic algebra.

The more finicky part was to figure out a good delay in between readings. On one hand we want the set up to be responsive to the position of the approacher, and on the other hand the more frequently the sensor updated the more likely it is for one misread to mess up the whole experience (think single frame glitch-like cuts between scene because different reading → different scene). I eventually settled on 100 ms through some experimenting.

### RaspberryPi Code (`canny.py`)

This portion of the project was comparatively the simplest. However, it still gave me its fair share of headaches. The code is once again pretty straightforward, so we’ll just look at some interesting tidbits.

To communicate between the RPi and the ESP32 wirelessly, I adopted the code I devised during lab.

```cpp
#include <WiFi.h>

const char* ssid = "yale wireless";
const char* password = "";
...
WiFiServer server(80);
...
void setup() {
  ...
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
  ...
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
```

Essentially, we start a broadcasting server on port 80 of the ESP32 on the yalewireless wifi, and on the RPi side we use a complementary function to read in the packets of data:

```python
# ESP32 server settings
ESP32_IP = "10.67.73.44"
ESP32_PORT = 80
...
def update_sensor_data():
    global current_distance, current_heartrate
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((ESP32_IP, ESP32_PORT))
            sock.settimeout(2)

            # Receive a single packet of data and decode it
            data = sock.recv(1024).decode("utf-8").strip()
            if data:
                for line in data.splitlines():
                    if "Heart Rate (BPM):" in line:
                        current_heartrate = float(line.split(":")[1].strip())
                    elif "Distance (cm):" in line:
                        current_distance = float(line.split(":")[1].strip())
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        print(f"Connection error: {e}. Retrying next cycle.")

```

The idea here is that `update_sensor_data` updates the global variables with the data it reads from the ESP32 continuously so that these variables can be used in other parts of the program. To accomplish this, we also had to account for the different kinds data lines we may received from the ESP32, namely, a single line of heart rate data, a single line of distance data, or an empty line.

The rest of the application is simply a matter of embedded the update functions inside of a pygame loop and displaying the right image/playing the right audio file based on the distance/heart rate global variables.

One final thing to note here, and it’s something I have to remind myself every time I use pygame: `time.sleep` simply does not work with pygame. Use `pg.time.get_ticks()` and `clock.tick()` instead.
