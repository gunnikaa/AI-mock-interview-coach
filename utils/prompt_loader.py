import os


def load_prompt(agent_name: str) -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prompt_path = os.path.join(base_dir, "prompts", f"{agent_name}.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()
