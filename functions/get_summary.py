from prompts.get_summary import system_prompt, user_prompt
from utils.llm_completion import llm_completion

def get_summary(book: str) -> str:
    messages = [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user_prompt(book)}
    ]
    return llm_completion("claude-4-sonnet", messages)