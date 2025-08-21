from typing import Tuple
from prompts.generate_visual_style import mood_board_prompt, motive_question, system_prompt, user_prompt
from utils.generate_image import generate_image, get_image_urls
from utils.llm_completion import llm_completion

VISUAL_STYLE_GENERATOR_MODEL = "claude-4-sonnet"

def generate_visual_style(book_title: str, book_summary: str) -> Tuple[str, str]:
    system_prompt_text = system_prompt()
    user_prompt_text = user_prompt(book_title, book_summary)

    messages = [
        {"role": "system", "content": system_prompt_text},
        {"role": "user", "content": user_prompt_text}
    ]

    response = llm_completion(VISUAL_STYLE_GENERATOR_MODEL, messages)
    style = response.split('<style>')[1].split('</style>')[0].strip()

    messages.append({"role": "assistant", "content": response})

    motive_question_text = motive_question()
    messages.append({"role": "user", "content": motive_question_text})

    motives = llm_completion(VISUAL_STYLE_GENERATOR_MODEL, messages)

    result = generate_image(prompt=mood_board_prompt(motives, style), aspect_ratio="16:9")
    image_urls = get_image_urls(result)
    mood_board_image = image_urls[0] if image_urls else ""

    return style, mood_board_image

if __name__ == "__main__":
    print(generate_visual_style("Harry Potter", "Harry Potter is a young wizard who discovers he is a wizard and attends Hogwarts School of Witchcraft and Wizardry."))