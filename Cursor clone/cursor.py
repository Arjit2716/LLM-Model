import os
import platform
import subprocess
from google import genai
from google.genai.errors import ClientError
from pathlib import Path

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        env_path = env_path.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise SystemExit(
        "Missing GOOGLE_API_KEY environment variable. "
        "Put it in .env or export it in your shell."
    )

client = genai.Client(api_key=api_key)
history = []


# ── Tool 1: Run shell commands ────────────────────────────────────────────────
def execute_command(command):
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True
        )
        if result.stderr:
            return f"Error: {result.stderr}"
        return f"Success: {result.stdout} || Task executed completely"
    except Exception as e:
        return f"Error: {str(e)}"


execute_command_declaration = {
    "name": "executeCommand",
    "description": (
        "Execute a single terminal/shell command. "
        "Use this ONLY for: creating folders (mkdir), deleting files/folders, "
        "running scripts, or other shell operations. "
        "Do NOT use this to write file contents — use writeFile instead."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "command": {
                "type": "STRING",
                "description": 'Single terminal command. Example: "mkdir calculator"'
            }
        },
        "required": ["command"]
    }
}


# ── Tool 2: Write content directly to a file ─────────────────────────────────
def write_file(filepath, content):
    try:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Success: Written to {filepath}"
    except Exception as e:
        return f"Error: {str(e)}"


write_file_declaration = {
    "name": "writeFile",
    "description": (
        "Write text content (HTML, CSS, JS, Python, etc.) into a file. "
        "Use this whenever you need to create or overwrite a file with code or text. "
        "This is the ONLY correct way to write code into files."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "filepath": {
                "type": "STRING",
                "description": 'Relative or absolute file path. Example: "calculator/index.html"'
            },
            "content": {
                "type": "STRING",
                "description": "The full text content to write into the file."
            }
        },
        "required": ["filepath", "content"]
    }
}


available_tools = {
    "executeCommand": execute_command,
    "writeFile": write_file,
}


def run_agent(user_problem):
    history.append({
        "role": "user",
        "parts": [{"text": user_problem}]
    })

    while True:
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=history,
                config={
                    "system_instruction": f"""
You are a Website Builder Expert.

Current Operating System: {platform.system()}

Your job:
1. Analyze user requirements.
2. Build websites step-by-step using the provided tools.
3. ALWAYS use the writeFile tool to write any code or text into files.
   Never print code in your response — write it to the file directly.

Workflow:
1. Use executeCommand to create the project folder (e.g. mkdir my-site)
2. Use writeFile to create and populate index.html
3. Use writeFile to create and populate style.css
4. Use writeFile to create and populate script.js
5. Confirm completion with a short summary

Rules:
- Use writeFile for ALL file content. Never use echo or shell redirection to write files.
- Use executeCommand only for mkdir, rm, or running scripts.
- Give one tool call at a time and wait for the result before proceeding.
""",
                    "tools": [
                        {
                            "function_declarations": [
                                execute_command_declaration,
                                write_file_declaration,
                            ]
                        }
                    ]
                }
            )
        except ClientError as e:
            print("\nAPI Error:", e)
            status = getattr(e, "status_code", None)
            if status == 429:
                print("Quota exceeded. Check your Gemini API billing/plan.")
            elif status == 404:
                print("Model not found. Use a valid Gemini model name.")
            break

        function_calls = getattr(response, "function_calls", None)

        if function_calls:
            function_call = function_calls[0]
            name = function_call.name
            args = dict(function_call.args)

            print(f"\nTool Call: {name}")
            # Print filepath/command but truncate long content
            display_args = {
                k: (v[:80] + "...") if k == "content" and len(v) > 80 else v
                for k, v in args.items()
            }
            print(display_args)

            result = available_tools[name](**args)
            print(result)

            history.append({
                "role": "model",
                "parts": [{"functionCall": {"name": name, "args": args}}]
            })
            history.append({
                "role": "user",
                "parts": [{"functionResponse": {"name": name, "response": {"result": result}}}]
            })

        else:
            print("\nAI Response:")
            print(response.text)
            history.append({
                "role": "model",
                "parts": [{"text": response.text}]
            })
            break


def main():
    print("I am a Cursor AI Agent. Let's create a website.")
    while True:
        user_problem = input("\nAsk me anything --> ")
        if user_problem.lower() in ["exit", "quit"]:
            break
        run_agent(user_problem)


if __name__ == "__main__":
    main()

# Added a writeFile tool — This is the key fix. The AI now has a dedicated tool that takes a filepath and content and writes it directly using Python's Path.write_text(). This is reliable across all OSes, no shell escaping issues.

# Updated the system prompt — Explicitly instructs the model to never print code, and to always use writeFile for file content and executeCommand only for folder/shell operations.

# Updated executeCommand description — Tells the model not to use it for writing files, so it picks the right tool.

# Truncated content in logs — Long file contents no longer flood your terminal; you see just the first 80 chars + ....