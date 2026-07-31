# claude_cli.py
"""
Simple terminal CLI to interact with Anthropic Claude via OpenRouter API.
Uses the model "tencent/hy3:free".
Requires an environment variable `OPENROUTER_API_KEY` containing your OpenRouter API key.

Usage:
  python claude_cli.py [--model MODEL] [--system SYSTEM_PROMPT]

You can then type messages; the assistant will respond. Type 'exit' or press Ctrl+C to quit.
"""

import os
import sys
import json
import argparse
import requests
import readline  # Optional, for command history and line editing

API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "tencent/hy3:free"

def get_api_key():
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        sys.stderr.write("Error: OPENROUTER_API_KEY environment variable not set.\n")
        sys.exit(1)
    return key

def build_headers(api_key: str):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/your-repo/claude-cli",
        "X-Title": "Claude CLI Tool",
    }

def build_payload(messages, model, system_prompt=None):
    payload = {
        "model": model,
        "messages": messages,
    }
    if system_prompt:
        payload["system"] = system_prompt
    return payload

def chat_loop(model: str, system_prompt: str = None):
    api_key = get_api_key()
    headers = build_headers(api_key)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    print("Claude CLI – type your message and press Enter. Type 'exit' to quit.")
    while True:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if user_input.strip().lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        messages.append({"role": "user", "content": user_input})
        payload = build_payload(messages, model, system_prompt)
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
        except Exception as e:
            print(f"[Error] Request failed: {e}")
            messages.pop()
            continue
        data = response.json()
        if "choices" not in data or not data["choices"]:
            print("[Error] Unexpected response format.")
            messages.pop()
            continue
        assistant_msg = data["choices"][0]["message"]["content"]
        print(f"Claude: {assistant_msg}\n")
        messages.append({"role": "assistant", "content": assistant_msg})

def main():
    parser = argparse.ArgumentParser(description="Claude CLI via OpenRouter")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model identifier (default: tencent/hy3:free)")
    parser.add_argument("--system", default=None, help="Optional system prompt to set behavior")
    args = parser.parse_args()
    chat_loop(args.model, args.system)

if __name__ == "__main__":
    main()

"""# End of script"""
