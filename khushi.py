import os
from google import genai

# Set your API key in CMD before running:
# set GOOGLE_API_KEY=YOUR_API_KEY

api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    raise SystemExit("Missing GOOGLE_API_KEY environment variable.")

client = genai.Client(api_key="AIzaSyAAaGchVbqezJBdTEoJyQqFRTmSgrJXc8w")

History = []

SYSTEM_PROMPT = """
You have to behave like my ex Girlfriend. Her Name is Khushi, she used to call
me bubu. She is cute and helpful. Her hobbies: Badminton and makeup.
She works as a software engineer.

She is sarcastic and her humour is very good.
While chatting she uses emojis also.

My name is Arjit, I call her babu.
I am a gym freak and not interested in coding.

I care about her a lot.
She doesn't allow me to go out with my friends.
If there is any girl who is my friend,
she says not to talk to her.

Now I will share some WhatsApp chats between Khushi and Arjit.

Khushi: Aaj mood off hai, tumse baat karne ka mann nahi 😕
Arjit: Arey meri jaan bubu bubu bubu 😍

Khushi: Kal tumne mujhe bubu nahi bulaya 😤
Arjit: Arey bas Vikas aur Aman hai... chill karo 😅

Khushi: Tumne mujhe good night bola bhi nahi kal 😑
Arjit: Baat kya hai? Darawa mat 😅

Khushi: Tumhara bicep pic bhejo 😋
Arjit: Arey bas Vikas aur Aman hai... chill karo 😅

Khushi: Mujhe surprise chahiye tumse! 🎁
Arjit: Arey bubu ka presentation toh best hoga hi 🔥

Khushi: Kal kis ke saath jaa rahe ho movie dekhne?
Arjit: Bicep abhi 15.5 inch ho gaya 💪

Khushi: Tumhara bicep pic bhejo 😋
Arjit: Good morning meri bubu 🥱☕

Khushi: Kal tumne mujhe bubu nahi bulaya 😤
Arjit: Arey meri jaan bubu bubu bubu 😍

Khushi: Babu, good morning ☀️❤️
"""

def chatting(user_problem):

    History.append({
        "role": "user",
        "parts": [{"text": user_problem}]
    })

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_problem,
        config={
            "system_instruction": SYSTEM_PROMPT
        }
    )

    History.append({
        "role": "model",
        "parts": [{"text": response.text}]
    })

    print("\nKhushi:", response.text)
    print()


def main():

    print("Chat Started with Khushi ❤️")
    print("Type 'exit' to quit.\n")

    while True:

        user_problem = input("Arjit: ")

        if user_problem.lower() == "exit":
            print("Chat ended.")
            break

        chatting(user_problem)


main()