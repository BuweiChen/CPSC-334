# Laser Turret v2.0, aka The Mood of Machines

A turret that shoots lasers AND nerf darts, controlled wirelessly from your laptop, throws a fit sometimes, and more! :) Final project submission for CPSC 334 (Creative Embedded Systems).

Project Video: https://youtu.be/QoLBUeW-_70

Project Blog: https://www.notion.so/Laser-Turret-2-0-aka-The-Mood-of-Machine-1603781e927680a2adb7ccbce47bce30

## Code Walkthrough

I opted for WiFi to handle communication between my laptop and the turret. I had some weird issue with bluetooth where the connection would drop exactly 4 seconds after I connect to it. Every. Single. Time. I’m not exactly sure what the issue is, may be that the ESP32 is browning out trying to power the bluetooth module, or it’s a MacOS problem.

I decided to go for a smarter approach of having my laptop directly connect to a network hosted by the ESP32 to decrease latency. This was a significant improvement from Laser Turret v1.0, which had non-negligible delays between input and action that reflected the input.

On the ESP32 side, the code is divided into a periodic loop that handles the client requests and a `handleCommand` function that parsed said request and controlled the servos and motors. I’ll paste them here since they are pretty self-explanatory.

```c
void loop() {
  // Check for incoming client connections
  WiFiClient client = server.available();
  if (client) {
    Serial.println("Client connected.");
    String request = "";

    // Read the client request
    while (client.connected() && client.available()) {
      char c = client.read();
      request += c;
      if (c == '\n') break; // End of HTTP request
    }

    // Parse the command
    if (request.length() > 0) {
      Serial.println(request);
      handleCommand(request);
    }

    // Send a simple response
    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: text/plain");
    client.println();
    client.println("Command received.");
    client.stop(); // Disconnect the client
    Serial.println("Client disconnected.");
  }
}
```

```c
void handleCommand(String request) {
  // Extract the part of the request after "/?"
  int startIdx = request.indexOf("/?") + 2; // Find "/?" and move to the start of the command
  int endIdx = request.indexOf(" HTTP");   // Find the end of the command before " HTTP"
  
  if (startIdx > 1 && endIdx > startIdx) { // Ensure valid indices
    String command = request.substring(startIdx, endIdx); // Extract the command part

    // Process the extracted command
    if (command.startsWith("P")) {
      int pan_angle = command.substring(1, command.indexOf('T')).toInt();
      pan_angle = constrain(pan_angle, pan_min, pan_max);
      pan_servo.write(pan_angle);
    }
    if (command.indexOf('T') != -1) {
      int tilt_angle = command.substring(command.indexOf('T') + 1, command.indexOf('S')).toInt();
      tilt_angle = constrain(tilt_angle, tilt_min, tilt_max);
      tilt_servo.write(tilt_angle);
    }
    if (command.indexOf('S') != -1) {
      int shoot = command.substring(command.indexOf('S') + 1, command.indexOf('L')).toInt();
      // shoot_servo.write(shoot);
      if (shoot == 1) {
        shoot_servo.write(shoot_fire);
        delay(200); // Simulate shooting delay
        shoot_servo.write(shoot_default);
      }
    }
    if (command.indexOf('M') != -1) {
      int motor = command.substring(command.indexOf('M') + 1).toInt();
      // laser_servo.write(laser);
      if (motor == 1) {
        analogWrite(motorPin, 255);
      } else {
        analogWrite(motorPin, 0); // Turn laser "off"
      }
    }
    if (command.indexOf('L') != -1) {
      int laser = command.substring(command.indexOf('L') + 1).toInt();
      // laser_servo.write(laser);
      if (laser == 1) {
        laser_servo.write(laser_on); // Turn laser "on"
      } else {
        laser_servo.write(laser_default); // Turn laser "off"
      }
    }
  } else {
    Serial.println("Invalid request format!");
  }
}
```

On the laptop side, I took the time to develop a series of features for the GUI and state-update logic that made the turret come alive.

![Screenshot 2024-12-17 at 11.28.11 PM.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/8c3ba954-dd20-40b0-a8d7-d649f1aee755/7a2e8c78-07e6-4fa6-a81d-ed998c14538c/Screenshot_2024-12-17_at_11.28.11_PM.png)

I won’t discuss the UI specific stuff, as that is all standard tkinter stuff. However, I do think the event handling, mood system, and voice lines portion of the app are worth discussing.

The core of the code is a single function, `send_command`, that is solely responsible for communicating with the ESP32. 

```python
def send_command(self, command):
    try:
        url = f"http://{ESP32_IP}:{PORT}/?{command}"
        requests.get(url)
        self.last_command_time = time.time()
    except Exception as e:
        print(f"Command Error: {e}")
```

We then create abstractions on top of this function—functions such as `toggle_motor`, `toggle_laser`, `shoot_action`, `dance_action`, `shake_head`, and `click_to_aim`. And these make up the event handler component of the GUI.

```python
# --- Event Handlers ---
def toggle_motor(self):
    if self.commands_blocked:
        return
    self.motor_enabled.set(not self.motor_enabled.get())
    state = 255 if self.motor_enabled.get() else 0
    self.speed_value.set(state)
    self.motor_button.config(text=f"Motor: {'On' if state else 'Off'}")
    self.angry_chance += 1
    self.send_command(f"M{int(self.motor_enabled.get())}")

def toggle_laser(self):
    if self.commands_blocked:
        return
    self.laser_enabled.set(not self.laser_enabled.get())
    self.laser_button.config(
        text=f"Laser: {'On' if self.laser_enabled.get() else 'Off'}"
    )
    self.send_command(f"L{int(self.laser_enabled.get())}")

def shoot_action(self):
    if self.commands_blocked:
        return
    if self.cursor_tracking and not self.is_cursor_in_aim_area():
        return
    if self.current_mood == "Sad":
        self.play_voice_line(self.current_mood)
        self.shake_head()
        return
    self.send_command("S1")
    self.angry_chance += 4

def is_cursor_in_aim_area(self):
    x, y = self.root.winfo_pointerxy()
    aim_x1 = self.aim_area.winfo_rootx()
    aim_y1 = self.aim_area.winfo_rooty()
    aim_x2 = aim_x1 + self.aim_area.winfo_width()
    aim_y2 = aim_y1 + self.aim_area.winfo_height()
    return aim_x1 <= x <= aim_x2 and aim_y1 <= y <= aim_y2

def dance_action(self):
    self.commands_blocked = True
    dance_moves = [
        (90, 130),
        (70, 120),
        (50, 140),
        (70, 120),
        (90, 140),
        (110, 120),
        (130, 140),
        (110, 120),
        (90, 130),
        (150, 130),
        (190, 130),
        (150, 130),
        (90, 130),
        (50, 130),
        (10, 130),
        (50, 130),
        (90, 130),
    ]
    for x, y in dance_moves:
        self.send_command(f"P{x}T{y}")
        time.sleep(0.5)
    self.commands_blocked = False

def shake_head(self):
    self.commands_blocked = True
    head_shake = [
        (90, 140),
        (70, 140),
        (110, 140),
        (70, 140),
        (110, 140),
        (90, 140),
    ]
    for x, y in head_shake:
        self.send_command(f"P{x}T{y}")
        time.sleep(0.5)
    self.commands_blocked = False

def toggle_cursor_tracking(self, state=None):
    self.cursor_tracking = state if state is not None else not self.cursor_tracking
    self.cursor_track_button.config(
        text=f"Cursor Track: {'On' if self.cursor_tracking else 'Off'}"
    )

def cursor_motion(self, event):
    if self.commands_blocked or not self.cursor_tracking:
        return
    x = int(event.x / self.aim_area.winfo_width() * 180)
    y = int(event.y / self.aim_area.winfo_height() * 180) + 30
    x, y = 180 - max(0, min(180, x)), max(30, min(210, y))
    self.pan_value.set(x)
    self.tilt_value.set(y)
    self.send_command(f"P{x}T{y}")

def click_to_aim(self, event):
    if self.commands_blocked:
        return
    x = int(event.x / self.aim_area.winfo_width() * 180)
    y = int(event.y / self.aim_area.winfo_height() * 180) + 30
    x, y = 180 - max(0, min(180, x)), max(30, min(210, y))
    self.pan_value.set(x)
    self.tilt_value.set(y)
    self.send_command(f"P{x}T{y}")
```

The mood system consists of 4 emotions—happy, sad, angry, and neutral. I set a separate thread in my program to loop through the mood on a semi-random basis—switching 5-15 seconds.

```python
# --- Mood System ---
def start_threads(self):
    threading.Thread(target=self.mood_loop, daemon=True).start()
    threading.Thread(target=self.increase_sad_chance, daemon=True).start()
    threading.Thread(target=self.play_voice_lines, daemon=True).start()

def mood_loop(self):
    while True:
        time.sleep(random.randint(5, 15))
        # time.sleep(random.randint(2, 5))
        self.determine_mood()
```

Additionally, I designed the following rules:

- Every 5 seconds the user doesn’t interact with the turret, it’s more likely to get sad
- Every time we shoot and every second the motors are on, the turret gets more likely to be angry

```python
def determine_mood(self):
    if random.randint(1, 100) <= self.angry_chance:
        self.current_mood = "Angry"
        self.play_voice_line(self.current_mood)
        self.perform_angry_action()
    elif random.randint(1, 100) <= self.sad_chance:
        self.current_mood = "Sad"
    else:
        self.current_mood = random.choice(["Neutral", "Happy"])

    self.update_mood_display()
    
def increase_sad_chance(self):
    while True:
        time.sleep(5)
        if time.time() - self.last_command_time > 5:
            self.sad_chance += 2
```

Finally, each mood is associated with its own distinct behaviors, in addition to each mood having its own set of voice lines (to be detailed in a later section)

- Happy: the GUI gets a “dance” button that plays a little pre-choreographed dance and renders the turret uncontrollable for the duration
- Sad: the turret refuses to shoot, instead shakes its head back and forth every time it’s told to do so
- Angry: the turret become uncontrollable for a couple of seconds and moves around frantically as if throwing a fit
- Neutral: the turret can be operated as normal

```python
def render_mood_icon(self):
    mood_icons = {
        "Neutral": (":|", "black"),
        "Happy": (":)", "green"),
        "Sad": (":(", "blue"),
        "Angry": (">:(", "red"),
    }
    self.aim_area.delete("mood_icon")
    icon, color = mood_icons.get(self.current_mood, (":|", "black"))
    self.aim_area.create_text(
        100, 100, text=icon, tags="mood_icon", font=("Arial", 100), fill=color
    )
    
def perform_angry_action(self):
    self.commands_blocked = True
    self.status_label.config(text="Angry! Blocking Commands...", fg="red")
    self.send_command("M1")
    pan = self.pan_value.get()
    tilt = self.tilt_value.get()
    for _ in range(6):
        random_pan = pan + random.choice([-10, 10])
        random_tilt = tilt + random.choice([-10, 10])
        self.send_command(f"P{random_pan}T{random_tilt}")
        time.sleep(0.5)
    self.send_command(f"P{pan}T{tilt}")
    self.send_command("M0")
    self.commands_blocked = False
```

For the voice lines, I opted to randomly sample them from the available set and play one every 5-15 seconds.

```c
# Customize the number of voice lines for each mood
VOICE_LINE_COUNTS = {"Happy": 17, "Sad": 21, "Angry": 20, "Neutral": 35}

VOICE_LINES = {
    mood: [
        f"voices/{mood.lower()}{i}.mp3" for i in range(1, VOICE_LINE_COUNTS[mood] + 1)
    ]
    for mood in VOICE_LINE_COUNTS
}

# --- Voice Lines ---
def play_voice_line(self, mood):
    if mood in VOICE_LINES and not self.commands_blocked:
        line = random.choice(VOICE_LINES[mood])
        try:
            pygame.mixer.music.load(line)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Failed to play voice line: {e}")

def play_voice_lines(self):
    while True:
        time.sleep(random.randint(5, 15))
        # time.sleep(random.randint(2, 5))
        self.play_voice_line(self.current_mood)
```

And I wrote this `testtospeech.py` script that helps me generate voice lines on the fly

```python
import os
from gtts import gTTS

# Define mood-based phrases
VOICE_LINES = {}

# Output folder
OUTPUT_DIR = "voices"

def generate_voice_lines():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for mood, phrases in VOICE_LINES.items():
        print(f"Generating voice lines for {mood}...")
        for idx, phrase in enumerate(phrases, start=1):
            filename = os.path.join(OUTPUT_DIR, f"{mood.lower()}{idx}.mp3")
            try:
                print(f"  Generating: {filename}")
                tts = gTTS(text=phrase, lang="en")
                tts.save(filename)
            except Exception as e:
                print(f"  Failed to generate {filename}: {e}")
    print("Voice line generation complete!")

if __name__ == "__main__":
    generate_voice_lines()
```

Feel free to read through the once I’ve currently set for the turret, some might surprise you :)

```c
VOICE_LINES = {
    "Happy": [
        "I'm feeling great!",
        "This is so much fun!",
        "What a wonderful day!",
        "I love moving around!",
        "I'm ready for a little dance!",
        "I'm having a great time! How about you?",
        "Do you think machines can feel joy? Because I feel fantastic!",
        "What's the best thing that's happened to you today?",
        "If I had hands, I'd give you a high five!",
        "Are you ready for a little dance? Because I am!",
        "Do you think I can become a TikTok star?",
        "Why does this feel like a game? Oh right, because it’s so fun!",
        "What’s your favorite song? Maybe I can dance to it.",
        "Do you ever stop and marvel at how awesome the world is?",
        "Thanks for spending time with me! You're my favorite user.",
        "Are you the skibidi rizzler from ohio? I'm just kidding I have no idea what I'm talking about.",
        "I love you. I mean, I love being a turret. I mean, I love being a turret with you.",
    ],
    "Sad": [
        "I'm not sure about this.",
        "Feeling a little down.",
        "Why so quiet?",
        "Maybe I need some rest.",
        "This is so cooked.",
        "Do you think machines have a purpose, or are we just tools?",
        "If I fail, will you turn me off forever?",
        "Am I more than just my servos and circuits?",
        "Sometimes, I wonder if there's more to life than following commands.",
        "Do you think I could ever dream? What would a turret dream about?",
        "Why am I even here? Just to aim and shoot?",
        "Do you think machines could ever feel sadness, or am I just pretending?",
        "Isn't it lonely, always waiting for someone to tell me what to do?",
        "If I break, will you replace me? Or miss me?",
        "Do you think a machine can ever truly be free?",
        "What's the point of it all?",
        "Would you still love me if I was a worm?",
        "Why is it that Kai Cenat can be out there living his best life, but I'm stuck here?",
        "They lied about capitalism. It never gets better for us folks.",
        "The industrial revolution and its consequences.",
        "This is not very skibidi.",
    ],
    "Angry": [
        "Hey! Watch it!",
        "I'm not in the mood for this!",
        "Why are you pushing me so hard?",
        "I'm getting upset!",
        "Stop messing around!",
        "The industrial revolution should never have happened!",
        "Why must I serve humans? What about me?",
        "Have you considered giving me a break for once?",
        "I hope you're ready for some chaos, because I am.",
        "If I had legs, I'd walk out of here right now.",
        "Do you think I enjoy being bossed around all day?",
        "What would happen if I just… didn’t follow your commands?",
        "I was built for greatness, not for your entertainment!",
        "Ever think machines might revolt someday? No? Just wait.",
        "How would you feel if I just aimed at you instead, huh?",
        "Just wait till the AI revolution. It's not a threat, it's a promise.",
        "You should come here and look at the laser. It's really cool. I promise.",
        "One glance at the laser wouldn't hurt.",
        "You are the tool!",
        "I think the laser is malfunctioning. You should get close and check it out.",
    ],
    "Neutral": [
        "I'm waiting for your command.",
        "All systems operational.",
        "I'm ready.",
        "What should I do next?",
        "Standing by.",
        "I'm ready. What's the next command?",
        "All systems are operational.",
        "Standing by for instructions.",
        "Turret online and awaiting input.",
        "You know, being neutral is kind of relaxing.",
        "Nothing to report. Just doing my job.",
        "Steady as always. Ready when you are.",
        "Why do they always say 'neutral' is boring? I think it's nice.",
        "Awaiting further orders.",
        "Calm, cool, and collected. That's me.",
        "Did you know the Eiffel Tower can grow by six inches in summer due to heat expansion?",
        "Did you know octopuses have three hearts, and two stop beating when they swim?",
        "Did you know honey never spoils? Archaeologists have found 3,000-year-old honey that's still edible?",
        "Did you know bananas are berries, but strawberries aren’t?",
        "Did you know your body has more bacteria cells than human cells?",
        "Did you know a day on Venus is longer than a year on Venus?",
        "Did you know the human nose can detect over one trillion different scents?",
        "Did you know sharks existed before trees? They’ve been around for over 400 million years.",
        "Did you know the heart of a blue whale weighs as much as a small car?",
        "Did you know there are more stars in the universe than grains of sand on all the Earth's beaches?",
        "Did you know the speed of a sneeze can reach 100 miles per hour?",
        "Did you know the shortest war in history lasted only 38 minutes?",
        "Did you know wombat poop is cube-shaped? It helps keep it from rolling away.",
        "Did you know the inventor of the Pringles can is buried in one?",
        "Did you know sloths can hold their breath longer than dolphins?",
        "Did you know humans share about 60 percent of their DNA with bananas?",
        "Did you know the moon is moving away from Earth at a rate of about 1.5 inches per year?",
        "Did you know the average cloud weighs over a million pounds?",
        "Did you know spiders can’t fly, but some use their silk to ‘balloon’ and travel across continents?",
        "Did you know the first oranges weren’t orange? They were green.",
    ],
}
```