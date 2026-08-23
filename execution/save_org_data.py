from core.memory import save_org_memory

def execute(data: dict) -> bool:
    """
    Executes Workflow A: Save Organizational Memory.
    A deterministic flow to write incoming org data to the filesystem.
    """
    return save_org_memory(data)

if __name__ == "__main__":
    # Example test usage
    sample_data = {
        "mission": "Our mission is to help people.",
        "programs": "1. Education\n2. Healthcare",
        "outcomes": "Improved 10,000 lives.",
        "stats": "100% success rate."
    }
    print(f"Saved: {execute(sample_data)}")
