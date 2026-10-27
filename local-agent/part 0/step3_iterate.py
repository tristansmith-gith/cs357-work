import os, json, requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
HISTORY = "history.json"

def chat(messages, temperature=0.7):
    try:
        r = requests.post(f"{OLLAMA_URL}/api/chat", json={
            "model": MODEL, "stream": False,
            "options": {"temperature": temperature},
            "messages": messages}, timeout=120)
        r.raise_for_status()
        return r.json()["message"]
    except Exception as e:
        print(f"[step3:chat] {e}")
        import traceback; traceback.print_exc()
        return {"role": "assistant", "content": ""}

def load_history():
    try:
        with open(HISTORY, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return [{"role": "system", "content": "You are a concise assistant."}]

def save_history(messages):
    with open(HISTORY, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)

messages = load_history()
print("Type a message.  /forget erases the memory file, /quit exits.")
while True:                                                # NEW: the loop
    user_text = input("you> ").strip()
    if user_text == "/quit":
        break
    if user_text == "/forget":
        if os.path.exists(HISTORY):
            os.remove(HISTORY)
        messages = load_history()
        print("[memory erased]")
        continue
    messages.append({"role": "user", "content": user_text})
    reply = chat(messages)
    messages.append(reply)                                 # delete this line to see amnesia
    save_history(messages)
    print("model>", reply["content"])