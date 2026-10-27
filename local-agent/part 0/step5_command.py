import os, re, json, shlex, subprocess, requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
HISTORY = "history.json"
SKILL = os.path.join(".agents", "skills", "terse-helper", "SKILL.md")
TOOL_RULE = ("You can ask to run one shell command.  To do that, reply with exactly one line: "
             "RUN: <command>.  You will then receive its output as an Observation.  "
             "Otherwise, answer normally.")                # NEW: tell the model the protocol

def chat(messages, temperature=0.7):
    try:
        r = requests.post(f"{OLLAMA_URL}/api/chat", json={
            "model": MODEL, "stream": False,
            "options": {"temperature": temperature},
            "messages": messages}, timeout=120)
        r.raise_for_status()
        return r.json()["message"]
    except Exception as e:
        print(f"[step5:chat] {e}")
        import traceback; traceback.print_exc()
        return {"role": "assistant", "content": ""}

def strip_front_matter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text.strip()
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[i + 1:]).strip()
    return text.strip()

def load_skill(path):
    try:
        with open(path, encoding="utf-8") as f:
            return strip_front_matter(f.read())
    except FileNotFoundError as e:
        print(f"[step5:load_skill] no skill at {path}: {e}")
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

def run_command(cmd):                                      # NEW: the one place a command runs
    try:
        done = subprocess.run(shlex.split(cmd), capture_output=True, text=True, timeout=20)
        return f"exit code {done.returncode}\n{done.stdout}{done.stderr}"[:2000]
    except Exception as e:
        print(f"[step5:run_command] {e}")
        import traceback; traceback.print_exc()
        return f"the command failed to start: {e}"

messages = load_history()
system = "You are a concise assistant.\n\n" + TOOL_RULE
skill = load_skill(SKILL)
if skill:
    system += "\n\nFollow these rules exactly:\n\n" + skill
messages[0] = {"role": "system", "content": system}
print(f"[skill loaded: {bool(skill)}]  /quit exits.")
while True:
    user_text = input("you> ").strip()
    if user_text == "/quit":
        break
    messages.append({"role": "user", "content": user_text})
    reply = chat(messages)
    messages.append(reply)
    match = re.search(r"^\s*RUN:\s*(.+)$", reply["content"], re.MULTILINE)
    if match:                                              # NEW: the permission gate
        cmd = match.group(1).strip().strip("`")
        print(f"[the model wants to run]  {cmd}")
        if input("Type YES to allow it: ").strip() == "YES":
            observation = run_command(cmd)
        else:
            observation = "The user declined to run that command."
        print(f"[observation]  {observation}")
        messages.append({"role": "user", "content": f"Observation: {observation}"})
        reply = chat(messages)                             # let the model use what it saw
        messages.append(reply)
    save_history(messages)
    print("model>", reply["content"])