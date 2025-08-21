

from functions.generate_visual_style import generate_visual_style
from functions.get_summary import get_summary
from functions.script_generator import script_generator
from functions.tiktok_generator import tiktok_generator
from utils.convert_pdf_into_chunks import get_excerpts
import os
from pathlib import Path
from typing import List
import globals as G

BOOK_PATH = "dario_mock.md"
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
PAST_SCRIPT_COUNT = 5
PAST_TIKTOK_COUNT = 5

if __name__ == "__main__":
    pdf_name = Path(BOOK_PATH).stem

    # summary = get_summary(G.BOOK_NAME)
    # style, mood_board_image = generate_visual_style(book_summary=summary, book_title=G.BOOK_NAME)
    # G.STYLE = style
    # G.MOOD_BOARD_IMAGE = mood_board_image
    
    excerpts = get_excerpts(BOOK_PATH)

    past_scripts: List[str] = []
    past_tiktoks: List[str] = []


    for excerpt_index, excerpt in enumerate(excerpts):
        script = ""
        tiktok = ""
        video_path = ""

        # Create output directory
        output_dir = Path(pdf_name)
        output_dir.mkdir(exist_ok=True)

        excerpt_content = excerpt['content']

        is_first_excerpt = excerpt_index == 0
        is_last_excerpt = excerpt_index == len(excerpts) - 1
        
        # Generate TikTok with scene processing
        script_file = f"{output_dir}/script{excerpt_index}.txt"
        tiktok_file = f"{output_dir}/tiktok{excerpt_index}.txt"
        video_file = f"{output_dir}/{excerpt_index}.mp4"

        if os.path.exists(script_file) and os.path.exists(tiktok_file) and os.path.exists(video_file):
            script = open(script_file, "r").read()
            raw_tiktok = open(tiktok_file, "r").read()
            video_paths = [video_file]
            print(f"Using existing script, tiktok, and video for excerpt {excerpt_index + 1}")
        else:
            script = script_generator(excerpt_content, is_first_excerpt, is_last_excerpt, past_scripts[:PAST_SCRIPT_COUNT], excerpt_index, excerpts[excerpt_index - 1]['content'])
            print(f"Script: {script}")
            tiktok_data, raw_tiktok, video_paths = tiktok_generator(
                script, 
                past_tiktoks[:PAST_TIKTOK_COUNT],
                visual_style=G.STYLE,
                voice_id=VOICE_ID,
                excerpt_index=excerpt_index,
                output_dir=output_dir,
                process_videos=True
            )

        past_scripts.append(script)
        past_tiktoks.append(raw_tiktok)

        # Save script and tiktok text files
        with open(f"{output_dir}/script{excerpt_index}.txt", "w") as f:
            f.write(script)

        with open(f"{output_dir}/tiktok{excerpt_index}.txt", "w") as f:
            f.write(raw_tiktok)
        
        if video_paths:
            for i, video_path in enumerate(video_paths):
                print(f"Video saved to: {video_path}")
        else:
            print(f"No video generated for excerpt {excerpt_index + 1}")
        
        print(f"Completed excerpt {excerpt_index + 1}")