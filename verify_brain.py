
import requests
import json
import sys

# Add current directory to path so we can import kernel
import os
sys.path.append(os.getcwd())

from kernel.llm import LLMClient, LLMRequest

def verify_brain():
    print("Step 1.1: Checking Ollama availability...")
    try:
        r = requests.get("http://localhost:11434")
        if r.status_code == 200:
            print("✅ Ollama is running.")
        else:
            print(f"❌ Ollama is running but returned {r.status_code}")
    except Exception as e:
        print(f"❌ Ollama check failed: {e}")
        return

    print("Step 1.2: Verifying model exists...")
    try:
        r = requests.get("http://localhost:11434/api/tags")
        data = r.json()
        models = [m['name'] for m in data['models']]
        print(f"Available models: {models}")
        if "qwen2.5:3b" in models or "qwen2.5:3b:latest" in models:
            print("✅ qwen2.5:3b found.")
        else:
            print("❌ qwen2.5:3b NOT found.")
            # return # Don't return, maybe we can list what we have
    except Exception as e:
        print(f"❌ Model check failed: {e}")
        return

    print("Step 1.3: Test generation...")
    try:
        client = LLMClient()
        response = client.generate(LLMRequest(
            prompt="Explain your purpose as an autonomous agent."
        ))
        print(f"Response: {response.content}")
        if "POST:" in response.content or len(response.content) > 10:
             print("✅ Generation successful.")
        else:
             print("❌ Generation suspicious.")
    except Exception as e:
        print(f"❌ Generation failed: {e}")

if __name__ == "__main__":
    verify_brain()
