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
