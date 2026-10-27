import requests
import json
import traceback
import re
import os
from pypdf import PdfReader, PdfWriter

SYLLABUS_PDF = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "NYLT 2021 Edition with 2024 Updates.pdf")

def load_config(path="config.json"):
    with open(path) as f:
        return json.load(f)

def call_model(messages, config):
    """Send message history to the model provider and return the assistant reply string."""
    url = config["provider_url"]
    headers = {}
    if config.get("api_key"):
        # Hosted providers need a key; local Ollama does not, so api_key is null there.
        headers["Authorization"] = f"Bearer {config['api_key']}"

    if url.rstrip("/").endswith("/chat/completions"):
        # OpenAI-style providers: sampling settings sit at the top level.
        payload = {
            "model": config["model"],
            "messages": messages,
            "stream": False,
            "temperature": config["temperature"],
            "seed": config["seed"]
        }
    else:
        # Ollama (local or hosted): sampling settings sit under "options".
        payload = {
            "model": config["model"],
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": config["temperature"],
                "seed": config["seed"]
            }
        }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]   # OpenAI-style reply
        return data["message"]["content"]                     # Ollama reply
    except Exception as e:
        print(f"[lab1:call_model] {e}")
        traceback.print_exc()
        raise

def parse_response(text):
    """
    Returns ("action", tool_name, argument) or ("final", None, answer_text).
    Returns ("unknown", None, text) if neither pattern is found.
    """
    # Try to match "Final Answer:" first
    final_match = re.search(r"Final Answer:\s*(.+)", text, re.IGNORECASE | re.DOTALL)
    if final_match:
        return ("final", None, final_match.group(1).strip())

    # Try to match "Action: tool_name(argument)"
    action_match = re.search(r"Action:\s*(\w+)\(([^)]*)\)", text, re.IGNORECASE)
    if action_match:
        return ("action", action_match.group(1).strip(), action_match.group(2).strip())

    return ("unknown", None, text)

def find_event_pages(title):
    """Locate an event's syllabus in the NYLT PDF: pass the event title, get back its 1-based PDF page range as 'pages START-END', or a note that it is not in this PDF."""
    query = title.strip().lower()
    if not query:
        return "pass the event title, e.g. Model Campfire"

    reader = PdfReader(SYLLABUS_PDF)
    headings = []
    for index, page in enumerate(reader.pages):
        for line in (page.extract_text() or "").splitlines():
            match = re.match(r"\s*Day\s+\w+\s*:\s*(.+)", line)
            if match:
                headings.append((index + 1, match.group(1).strip()))

    hits = [(position, name) for position, name in headings
            if query in name.lower() or name.lower() in query]
    if not hits:
        toc_pages = [i + 1 for i, page in enumerate(reader.pages)
                     if query in (page.extract_text() or "").lower()]
        if toc_pages:
            return ("not found as a section: the title only appears in the "
                    f"table of contents on page {toc_pages[0]}, "
                    "so those pages are not in this PDF")
        return f"not found: no section matching '{title.strip()}' in this PDF"

    start = hits[0][0]
    end = len(reader.pages)
    for position, _ in headings:
        if position > start:
            end = position - 1
            break
    return f"pages {start}-{end}" if end > start else f"page {start}"


def extract_pages(spec):
    """Copy a page range out of the NYLT syllabus into its own PDF: pass 'START-END' or 'START-END,filename.pdf' using 1-based PDF pages, get back the saved file's path."""
    parts = [part.strip() for part in spec.split(",")]
    range_match = re.fullmatch(r"(\d+)(?:\s*-\s*(\d+))?", parts[0])
    if not range_match:
        return "invalid range: pass START-END using 1-based PDF pages, e.g. 47-52"

    start = int(range_match.group(1))
    end = int(range_match.group(2) or range_match.group(1))

    reader = PdfReader(SYLLABUS_PDF)
    total = len(reader.pages)
    if start < 1 or end < start or end > total:
        return f"invalid range {start}-{end}: this PDF has {total} pages"

    name = parts[1] if len(parts) > 1 and parts[1] else f"NYLT_pages_{start}-{end}.pdf"
    name = os.path.basename(name)
    if not name.lower().endswith(".pdf"):
        name += ".pdf"
    path = os.path.abspath(name)

    writer = PdfWriter()
    for page_number in range(start, end + 1):
        writer.add_page(reader.pages[page_number - 1])
    with open(path, "wb") as handle:
        writer.write(handle)
    return f"saved pages {start}-{end} to {path}"


TOOLS = {
    "find_event_pages": find_event_pages,
    "extract_pages": extract_pages,
}

def build_system_prompt(tools):
    role = (
    	"ROLE\n"
    	"You are an NYLT syllabus organization assistant. "
    	"You help NYLT staff locate individual event syllabi within a large course syllabus "
    	"and extract them into separate documents. "
    	"Be precise and methodical, and do not assume page ranges without evidence."
    )

    goal = (
        "GOAL\n"
        "Work toward the user's goal by reasoning step by step, calling tools "
        "when they help, and returning a final answer when you can."
    )

    tool_lines = []
    for name, fn in tools.items():
        doc = (fn.__doc__ or "").strip()
        tool_lines.append(f"- {name}: {doc}" if doc else f"- {name}")
    tools_section = "TOOLS\n" + ("\n".join(tool_lines) if tool_lines else "(no tools available)")

    format_section = (
        "FORMAT\n"
        "Respond with exactly one of:\n"
        "Action: <tool_name>(<argument>)\n"
        "Final Answer: <answer>"
    )

    guardrails = (
    	"GUARDRAILS\n"
    	"Do not invent page numbers or claim an event was found without evidence from the PDF. "
    	"Use search_pdf before extracting pages when the correct page range is not known. "
    	"Do not modify the original syllabus. "
    	"If you cannot determine the correct page range, explain the uncertainty instead of guessing. "
    	"Use only the tools listed in the TOOLS section. Do not invent tool names. "
    	"Follow each tool's documented argument format exactly. "
    	"When a tool returns the information needed to answer the user's goal, stop calling tools and provide the final answer."
    )

    return "\n\n".join([role, goal, tools_section, format_section, guardrails])

def run_agent(goal, config, tools):
    """
    Perceive-plan-act loop.
    tools: dict mapping tool_name (str) -> callable
    Returns (final_answer, steps_used, termination_reason)
    """
    system_prompt = build_system_prompt(tools)  # implemented in Part 2

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Goal: {goal}"}
    ]

    for step in range(1, config["step_budget"] + 1):
        print(f"\n--- Step {step} ---")

        reply = call_model(messages, config)
        print(f"Model: {reply}")

        messages.append({"role": "assistant", "content": reply})

        kind, tool_name, payload = parse_response(reply)

        if kind == "final":
            return (payload, step, "final_answer")

        if kind == "action":
            if tool_name in tools:
                try:
                    observation = str(tools[tool_name](payload))
                except Exception as e:
                    observation = f"[lab1:tool:{tool_name}] Error: {e}"
                    traceback.print_exc()
            else:
                observation = f"Unknown tool: {tool_name}"
            print(f"Observation: {observation}")
            messages.append({"role": "user", "content": f"Observation: {observation}"})
        else:
            # Unrecognized format - ask the model to reformat
            messages.append({"role": "user", "content": "Please respond with either 'Action: tool(arg)' or 'Final Answer: ...'."})

    # Budget exhausted
    last_reply = messages[-1]["content"] if messages else "(no reply)"
    return (last_reply, config["step_budget"], "budget_exhausted")

if __name__ == "__main__":
    config = load_config()
    goal = ("Find the page range for the 'Model Campfire' event in the NYLT syllabus PDF, "
            "then extract that range into a file named model_campfire.pdf.")
    answer, steps, reason = run_agent(goal, config, TOOLS)
    print(f"\nFinal answer: {answer}")
    print(f"Steps used: {steps}")
    print(f"Termination: {reason}")
