import os, json, requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
HISTORY = "history.json"
SKILL = os.path.join(".agents", "skills", "terse-helper", "SKILL.md")   # NEW

def chat(messages, temperature=0.7):
    try:
        r = requests.post(f"{OLLAMA_URL}/api/chat", json={
            "model": MODEL, "stream": False,
            "options": {"temperature": temperature},
            "messages": messages}, timeout=120)
        r.raise_for_status()
        return r.json()["message"]
    except Exception as e:
        print(f"[step4:chat] {e}")
        import traceback; traceback.print_exc()
        return {"role": "assistant", "content": ""}

def strip_front_matter(text):                              # NEW: same helper as the Persona Pipeline
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text.strip()
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[i + 1:]).strip()
    return text.strip()

def load_skill(path):                                      # NEW: a skill is a file we read
    try:
        with open(path, encoding="utf-8") as f:
            return strip_front_matter(f.read())
    except FileNotFoundError as e:
        print(f"[step4:load_skill] no skill at {path}: {e}")
        return ""

def load_history():
    try:
        with open(HISTORY, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return [{"role": "system", "content": ""}]

def save_history(messages):
    with open(HISTORY, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)

messages = load_history()
system = "You are a concise assistant."
skill = load_skill(SKILL)
if skill:
    system += "\n\nFollow these rules exactly:\n\n" + skill  # NEW: the skill joins the system prompt
messages[0] = {"role": "system", "content": system}        # re-read on every start
print(f"[skill loaded: {bool(skill)}]  /quit exits.")
while True:
    user_text = input("you> ").strip()
    if user_text == "/quit":
        break
    messages.append({"role": "user", "content": user_text})
    reply = chat(messages)
    messages.append(reply)
    save_history(messages)
    print("model>", reply["content"])