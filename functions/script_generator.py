from prompts.script_generator import system_prompt, user_prompt
from utils.llm_completion import llm_completion

SCRIPT_GENERATOR_MODEL = "gpt-5"
LEFT_OVER_EXCERPT = ""

def script_generator(excerpt: str, is_first_excerpt: bool, is_last_excerpt: bool, past_scripts: list[str], episode_number: int, latest_excerpt: str) -> str:
    system_prompt_text = system_prompt(is_first_excerpt, is_last_excerpt)
    user_prompt_text = user_prompt(excerpt, past_scripts, episode_number, is_first_excerpt, is_last_excerpt, latest_excerpt)

    messages = [
        {"role": "system", "content": system_prompt_text},
        {"role": "user", "content": user_prompt_text}
    ]

    return llm_completion(SCRIPT_GENERATOR_MODEL, messages)