import json
import os

MEMORY_FILE_PATH = "data/org_memory.json"

def get_org_memory() -> dict:
    """Retrieves organizational memory from local storage."""
    if not os.path.exists(MEMORY_FILE_PATH):
        return {}
    
    with open(MEMORY_FILE_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_org_memory(data: dict) -> bool:
    """Saves organizational memory to local storage."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(MEMORY_FILE_PATH), exist_ok=True)
        with open(MEMORY_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving org memory: {e}")
        return False
