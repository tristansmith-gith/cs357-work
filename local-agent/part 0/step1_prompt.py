import os, requests

# In a container, set OLLAMA_URL=http://host.docker.internal:11434 (Section 3a explains why)
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

def chat(messages, temperature=0.7):
    try:
        r = requests.post(f"{OLLAMA_URL}/api/chat", json={
            "model": MODEL, "stream": False,
            "options": {"temperature": temperature},
            "messages": messages}, timeout=120)
        r.raise_for_status()
        return r.json()["message"]        # {"role": "assistant", "content": "..."}
    except Exception as e:
        print(f"[step1:chat] {e}")
        import traceback; traceback.print_exc()
        return {"role": "assistant", "content": ""}

reply = chat([{"role": "user", "content": "In one sentence, what is a local model?"}])
print(reply["content"])