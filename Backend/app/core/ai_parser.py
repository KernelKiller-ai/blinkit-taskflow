import os
import re
import json
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

def parse_quick_add_mock(description: str) -> Dict[str, Any]:
    """
    Deterministic rule-based mock parser satisfying Section 3 rules (a-d).
    Runs with 0 API keys and 0 network calls.
    """
    text_lower = description.lower()
    
    # --- Step (b): Priority Determination ---
    has_high = "urgent" in text_lower or "asap" in text_lower
    has_low = "whenever" in text_lower or "low priority" in text_lower
    
    if has_high:
        priority = "high"
    elif has_low:
        priority = "low"
    else:
        priority = "medium"
        
    # --- Step (c): Due-date Hint Matching ---
    date_phrases = [
        "today",
        "tomorrow",
        "next week",
        "next monday", "next tuesday", "next wednesday", "next thursday", "next friday", "next saturday", "next sunday",
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
    ]
    
    matched_date = None
    for phrase in date_phrases:
        if phrase in text_lower:
            matched_date = phrase
            break
            
    # --- Step (d): Title Derivation ---
    keywords_to_strip = ["urgent", "asap", "whenever", "low priority"]
    if matched_date:
        keywords_to_strip.append(matched_date)
        
    title_work = description
    for kw in keywords_to_strip:
        # Case-insensitive removal preserving remaining text casing
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        title_work = pattern.sub("", title_work)
        
    title = title_work.strip()
    if not title:
        title = "Untitled task"
        
    return {
        "title": title,
        "priority": priority,
        "due_date_hint": matched_date
    }


def parse_quick_add(description: str) -> Dict[str, Any]:
    """
    Main entry point. Uses Gemini Interactions API when USE_REAL_LLM=true,
    otherwise defaults to zero-key mock parser.
    """
    use_real = os.getenv("USE_REAL_LLM", "false").lower() in ("true", "1", "yes")
    api_key = os.getenv("GEMINI_API_KEY")
    
    if use_real and api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            
            prompt = f"""
            You are a task parsing assistant.
            Extract details from this task description: "{description}"
            Return a JSON with:
            - 'title': task title without priority/date words
            - 'priority': 'low', 'medium', or 'high'
            - 'due_date_hint': extracted date string or null
            """
            
            interaction = client.interactions.create(
                model="gemini-3.6-flash",
                input=prompt,
                response_format={
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                            "due_date_hint": {"type": "string", "nullable": True}
                        },
                        "required": ["title", "priority"]
                    }
                }
            )
            parsed = json.loads(interaction.output_text)
            if not parsed.get("title", "").strip():
                parsed["title"] = "Untitled task"
            return parsed
        except Exception:
            # Fallback to mock if API call fails
            return parse_quick_add_mock(description)
    else:
        return parse_quick_add_mock(description)