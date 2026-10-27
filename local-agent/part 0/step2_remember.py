import os, sys, json, requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
HISTORY = "history.json"                                   # NEW: the memory lives here

def chat(messages, temperature=0.7):
    try:
        r = requests.post(f"{OLLAMA_URL}/api/chat", json={
            "model": MODEL, "stream": False,
            "options": {"temperature": temperature},
            "messages": messages}, timeout=120)
        r.raise_for_status()
        return r.json()["message"]
    except Exception as e:
        print(f"[step2:chat] {e}")
        import traceback; traceback.print_exc()
        return {"role": "assistant", "content": ""}

def load_history():                                        # NEW
    try:
        with open(HISTORY, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return [{"role": "system", "content": "You are a concise assistant."}]

def save_history(messages):                                # NEW
    with open(HISTORY, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)

messages = load_history()
messages.append({"role": "user", "content": " ".join(sys.argv[1:]) or "Hello!"})
reply = chat(messages)
messages.append(reply)
save_history(messages)                                     # NEW: write it down before we exit
print(reply["content"])
print(f"[{HISTORY} now holds {len(messages)} messages]")