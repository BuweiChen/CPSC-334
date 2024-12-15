import os
from gtts import gTTS

# Define mood-based phrases
VOICE_LINES = {
    "Happy": [
        "I'm feeling great!",
        "This is so much fun!",
        "What a wonderful day!",
        "I love moving around!",
        "I'm ready for a little dance!",
    ],
    "Sad": [
        "I'm not sure about this.",
        "Feeling a little down.",
        "Why so quiet?",
        "Maybe I need some rest.",
        "I feel like shaking my head.",
    ],
    "Angry": [
        "Hey! Watch it!",
        "I'm not in the mood for this!",
        "Why are you pushing me so hard?",
        "I'm getting upset!",
        "Stop messing around!",
    ],
    "Neutral": [
        "I'm waiting for your command.",
        "All systems operational.",
        "I'm ready.",
        "What should I do next?",
        "Standing by.",
    ],
}

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
