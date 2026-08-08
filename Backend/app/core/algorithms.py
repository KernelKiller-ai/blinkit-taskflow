import re
from typing import List, Dict, Any, Optional

# ==========================================
# SECTION 2: ALGORITHMS ENGINE (SORT & SEARCH)
# ==========================================

def insertion_sort(records: List[Dict[str, Any]], key: str) -> None:
    """Sorts a list of dictionaries in place by record[key]."""
    for i in range(1, len(records)):
        current = records[i]
        j = i - 1
        while j >= 0 and records[j][key] > current[key]:
            records[j + 1] = records[j]
            j -= 1
        records[j + 1] = current
    # In-place mutation (no return)


def insertion_sort_count(records: List[Dict[str, Any]], key: str) -> int:
    """Sorts in place and returns ONLY the comparison count (int)."""
    comparisons = 0
    for i in range(1, len(records)):
        current = records[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if records[j][key] > current[key]:
                records[j + 1] = records[j]
                j -= 1
            else:
                break
        records[j + 1] = current
    return comparisons


def binary_search(sorted_records: List[Dict[str, Any]], target_value: Any, key: str) -> int:
    """Binary search on sorted list of dicts. Returns index or -1."""
    low = 0
    high = len(sorted_records) - 1
    while low <= high:
        mid = (low + high) // 2
        if sorted_records[mid][key] == target_value:
            return mid
        elif sorted_records[mid][key] < target_value:
            low = mid + 1
        else:
            high = mid - 1
    return -1


def binary_search_count(sorted_records: List[Dict[str, Any]], target_value: Any, key: str) -> Dict[str, Any]:
    """Returns dict: {"index": int, "comparison_count": int}"""
    low = 0
    high = len(sorted_records) - 1
    comparisons = 0
    while low <= high:
        mid = (low + high) // 2
        comparisons += 1
        if sorted_records[mid][key] == target_value:
            return {"index": mid, "comparison_count": comparisons}
        elif sorted_records[mid][key] < target_value:
            low = mid + 1
        else:
            high = mid - 1
    return {"index": -1, "comparison_count": comparisons}


def linear_search(records: List[Dict[str, Any]], target_value: Any, key: str) -> int:
    """Linear search on list of dicts. Returns first matching index or -1."""
    for i in range(len(records)):
        if records[i][key] == target_value:
            return i
    return -1


def linear_search_count(records: List[Dict[str, Any]], target_value: Any, key: str) -> Dict[str, Any]:
    """Returns dict: {"index": int, "comparison_count": int}"""
    comparisons = 0
    for i in range(len(records)):
        comparisons += 1
        if records[i][key] == target_value:
            return {"index": i, "comparison_count": comparisons}
    return {"index": -1, "comparison_count": comparisons}


# ==========================================
# SECTION 3: DETERMINISTIC MOCK QUICK-ADD PARSER
# ==========================================

def parse_quick_add(description: str) -> Dict[str, Any]:
    """
    Parses a free-text task description into structured task fields 
    following Section 3 Task 3 exact specifications.
    """
    if not isinstance(description, str):
        description = ""

    orig_text = description
    lower_text = orig_text.lower()

    # Step b: Priority Determination
    high_keywords = ["urgent", "asap"]
    low_keywords = ["whenever", "low priority"]

    priority = "medium"
    has_high = any(kw in lower_text for kw in high_keywords)
    has_low = any(kw in lower_text for kw in low_keywords)

    if has_high:
        priority = "high"
    elif has_low:
        priority = "low"

    # Priority keywords to strip from title (Group i and Group ii)
    all_priority_kws = high_keywords + low_keywords

    # Step c: Due Date Hint Determination
    date_phrases = [
        "today",
        "tomorrow",
        "next week",
        "next monday", "next tuesday", "next wednesday", "next thursday", "next friday", "next saturday", "next sunday",
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
    ]

    due_date_hint: Optional[str] = None
    matched_date_phrase: Optional[str] = None

    for phrase in date_phrases:
        if phrase in lower_text:
            due_date_hint = phrase
            matched_date_phrase = phrase
            break

    # Step d: Title Stripping Logic
    spans_to_remove = []

    # Collect priority keyword spans
    for kw in all_priority_kws:
        for match in re.finditer(re.escape(kw), lower_text):
            spans_to_remove.append(match.span())

    # Collect date keyword span
    if matched_date_phrase:
        for match in re.finditer(re.escape(matched_date_phrase), lower_text):
            spans_to_remove.append(match.span())

    # Sort spans by starting index
    spans_to_remove.sort(key=lambda x: x[0])

    # Reconstruct title from original-cased description by omitting matched spans
    title_chars = []
    last_idx = 0
    for start, end in spans_to_remove:
        if start > last_idx:
            title_chars.append(orig_text[last_idx:start])
        last_idx = max(last_idx, end)
    if last_idx < len(orig_text):
        title_chars.append(orig_text[last_idx:])

    raw_title = "".join(title_chars)
    clean_title = re.sub(r"\s+", " ", raw_title).strip()

    if not clean_title:
        clean_title = "Untitled task"

    return {
        "title": clean_title,
        "priority": priority,
        "due_date_hint": due_date_hint
    }