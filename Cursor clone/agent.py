import argparse
import json
import os
import urllib.parse
import urllib.request

from google import genai
from google.genai import types

# Define local functions that the model can call.
WEATHER_API_KEY = None
WEATHER_API_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"


def get_current_temperature(location: str) -> str:
    api_key = WEATHER_API_KEY or os.environ.get("WEATHER_API_KEY")
    if not api_key:
        raise ValueError(
            "Weather API key not found. Set WEATHER_API_KEY or pass --weather-api-key."
        )

    encoded_location = urllib.parse.quote_plus(location)
    params = urllib.parse.urlencode(
        {
            "unitGroup": "metric",
            "include": "days",
            "contentType": "flatjson",
            "key": api_key,
        }
    )
    url = f"{WEATHER_API_URL}/{encoded_location}?{params}"

    with urllib.request.urlopen(url, timeout=15) as response:
        body = response.read().decode("utf-8")
        data = json.loads(body)

    current = data.get("currentConditions")
    if current:
        temp = current.get("temp")
        description = current.get("conditions") or current.get("icon") or "unknown conditions"
    else:
        days = data.get("days", {})
        temp_values = days.get("temp") or []
        descriptions = days.get("description") or []
        temp = temp_values[0] if temp_values else None
        description = descriptions[0] if descriptions else "unknown conditions"

    if temp is None:
        raise ValueError(
            f"Weather API returned no temperature for {location}. Response: {json.dumps(data)}"
        )

    return f"The current temperature in {location} is {temp}°C with {description}."


def twosum(num1: float, num2: float) -> str:
    return f"The sum of {num1} and {num2} is {num1 + num2}."


# Define the function declarations for the model.
weather_function = {
    "name": "get_current_temperature",
    "description": "Gets the current temperature for a given location.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city name, e.g. San Francisco",
            },
        },
        "required": ["location"],
    },
}

twosum_function = {
    "name": "twosum",
    "description": "Get the sum of two numbers.",
    "parameters": {
        "type": "object",
        "properties": {
            "num1": {
                "type": "number",
                "description": "The first number.",
            },
            "num2": {
                "type": "number",
                "description": "The second number.",
            },
        },
        "required": ["num1", "num2"],
    },
}


def call_function(function_call):
    args = function_call.args
    if isinstance(args, str):
        args = json.loads(args)

    if function_call.name == "get_current_temperature":
        return get_current_temperature(location=args["location"])
    if function_call.name == "twosum":
        return twosum(num1=args["num1"], num2=args["num2"])

    raise ValueError(f"Unknown function: {function_call.name}")


def main():
    global WEATHER_API_KEY

    parser = argparse.ArgumentParser(description="Run agent.py with a manual prompt.")
    parser.add_argument("prompt", nargs="*", help="The prompt to send to the model.")
    parser.add_argument(
        "--weather-api-key",
        dest="weather_api_key",
        help="Weather API key for Visual Crossing.",
    )
    args = parser.parse_args()

    WEATHER_API_KEY = args.weather_api_key or os.environ.get("WEATHER_API_KEY")
    prompt = " ".join(args.prompt).strip()
    if not prompt:
        prompt = input("Enter your prompt: ").strip()

    if not prompt:
        print("Error: prompt is required.")
        return

    client = genai.Client()
    tools = types.Tool(function_declarations=[weather_function, twosum_function])
    config = types.GenerateContentConfig(tools=[tools])

    history = [types.Content(role="user", parts=[types.Part(text=prompt)])]
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=history,
        config=config,
    )

    while True:
        first_candidate = response.candidates[0]
        first_part = first_candidate.content.parts[0]

        if first_part.function_call:
            function_call = first_part.function_call
            print(f"Function to call: {function_call.name}")
            print(f"Arguments: {function_call.args}")

            function_result = call_function(function_call)
            print(f"Function result: {function_result}")

            history.append(
                types.Content(
                    role="function",
                    parts=[
                        types.Part.from_function_response(
                            name=function_call.name,
                            response={"output": function_result},
                        )
                    ],
                )
            )

            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=history,
                config=config,
            )
            continue

        final_text = getattr(response, "text", None)
        if not final_text:
            final_text = first_part.text if getattr(first_part, "text", None) else ""

        print(final_text)
        break


if __name__ == "__main__":
    main()
