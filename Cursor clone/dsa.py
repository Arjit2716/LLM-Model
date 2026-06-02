import os
from google import genai

# Get API key from environment variable
api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    raise SystemExit("Missing GOOGLE_API_KEY environment variable.")

# Create client
client = genai.Client(api_key=api_key)

text = "Hey, are you down to grab some pizza later? I'm starving!"

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config={
        "system_instruction": (
            "You are a Data structure and Algorithm Instructor. "
            "You will only reply to the problem related to Data structure and Algorithm. "
            "You have to solve query of user in simplest way. "
            "If user ask any question which is not related to Data structure and Algorithm, reply him rudely. "
            "Example: If user ask, How are you, "
            "You will reply: You dumb ask me some sensible question, like this message you can reply anything more rudely. "
            "You have to reply him rudely if question is not related to Data structure and Algorithm. "
            "Else reply him politely with simple explanation."
        )
    },
    contents="President tof India is?"
)

print(response.text)