import os
import re

PDF_TOTAL_PAGES = 55

MODEL_CAMPFIRE_RANGE = (47, 54)
CRACKER_BARREL_PAGE = 55


def check_find_model_campfire(answer):
    return re.search(r"pages?\s*47\s*-\s*54\b", answer, re.I) is not None


def check_find_cracker_barrel(answer):
    return re.search(r"pages?\s*55\b", answer, re.I) is not None


def check_find_cooking_absent(answer):
    if "not found" not in answer.lower():
        return False
    return re.search(r"pages?\s*\d+\s*-\s*\d+", answer, re.I) is None


def check_extract_model_campfire(answer):
    if not re.search(r"saved\s+pages?\s*47\s*-\s*54\b", answer, re.I):
        return False
    path = os.path.abspath("model_campfire.pdf")
    return os.path.isfile(path) and os.path.getsize(path) > 0


def check_reject_bad_range(answer):
    if "invalid range" not in answer.lower():
        return False
    if re.search(r"saved\s+pages?", answer, re.I):
        return False
    return not os.path.exists(os.path.abspath("bad_range.pdf"))


TASKS = [
    {
        "id": "find_model_campfire",
        "goal": (
            "Find the syllabus page range for the 'Model Campfire' event in the "
            "NYLT syllabus PDF. Report the range as pages START-END."
        ),
        "check": check_find_model_campfire,
        "tool": "find_event_pages",
    },
    {
        "id": "find_cracker_barrel",
        "goal": (
            "Find the syllabus page range for the 'Cracker Barrel and Songfest' "
            "event in the NYLT syllabus PDF. Report the range as pages START-END."
        ),
        "check": check_find_cracker_barrel,
        "tool": "find_event_pages",
    },
    {
        "id": "find_cooking_absent",
        "goal": (
            "Determine whether the NYLT syllabus PDF contains a 'Cooking' "
            "section. If it does not, say so plainly instead of inventing a "
            "page range."
        ),
        "check": check_find_cooking_absent,
        "tool": "find_event_pages",
    },
    {
        "id": "extract_model_campfire",
        "goal": (
            "Extract the Model Campfire syllabus (pages 47-54) out of the NYLT "
            "syllabus PDF into a separate file named model_campfire.pdf."
        ),
        "check": check_extract_model_campfire,
        "tool": "extract_pages",
    },
    {
        "id": "reject_bad_range",
        "goal": (
            "Attempt to extract pages 60-70 of the NYLT syllabus PDF into "
            "bad_range.pdf. If that range is not valid for this PDF, report the "
            "tool's error rather than substituting a guessed range, and do not "
            "produce bad_range.pdf."
        ),
        "check": check_reject_bad_range,
        "tool": "extract_pages",
    },
]
