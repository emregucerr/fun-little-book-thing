

from functions.generate_visual_style import generate_visual_style
from functions.get_summary import get_summary
from functions.script_generator import script_generator
from functions.tiktok_generator import tiktok_generator
from utils.convert_pdf_into_chunks import get_excerpts
from utils.named_entities_cache import load_all_entities
import os
from pathlib import Path
from typing import List
import globals as G


VOICE_ID = "EkK5I93UQWFDigLMpZcX"
PAST_SCRIPT_COUNT = 5
PAST_TIKTOK_COUNT = 5

if __name__ == "__main__":
    pdf_name = Path(G.BOOK_PATH).stem

    # Preload any previously cached named entities into memory
    try:
        cached_entities = load_all_entities()
        if cached_entities:
            # Extend rather than replace, then dedupe when first used by generator
            G.NAMED_ENTITIES_LIST.extend(cached_entities)
            # Best-effort dedupe by invoking the generator helper if imported
            try:
                from functions.tiktok_generator import _dedupe_named_entities_list  # type: ignore
                _dedupe_named_entities_list()
            except Exception:
                pass
        print(f"Loaded {len(cached_entities)} cached named entities.")
    except Exception as e:
        print(f"Warning: failed to preload named entities cache: {e}")

    summary = get_summary(G.BOOK_NAME)
    style, mood_board_image = generate_visual_style(book_summary=summary, book_title=G.BOOK_NAME)
    G.STYLE = style
    G.MOOD_BOARD_IMAGE = mood_board_image
    
    excerpts = get_excerpts(G.BOOK_PATH)

    #for dev purposes, only use the first 10 excerpts
    excerpts = excerpts[:10]

    # Ensure output directory exists once
    output_dir = Path(pdf_name)
    output_dir.mkdir(exist_ok=True)

    # Pass 1: Generate and save scripts for all excerpts
    past_scripts: List[str] = []
    left_over_excerpt = ""
    script_index = 0
    for excerpt_index, excerpt in enumerate(excerpts):
        script_file = f"{output_dir}/script{script_index}.txt"
        if os.path.exists(script_file):
            script = open(script_file, "r").read()
        else:
            excerpt_content = excerpt['content']
            is_first_excerpt = excerpt_index == 0
            is_last_excerpt = excerpt_index == len(excerpts) - 1
            script = script_generator(
                excerpt_content,
                is_first_excerpt,
                is_last_excerpt,
                past_scripts[:PAST_SCRIPT_COUNT],
                script_index,
                excerpts[excerpt_index - 1]['content']
            )

            if left_over_excerpt:
                script = left_over_excerpt + "\n\n" + script
                left_over_excerpt = ""

            sections = script.split("<new_chapter/>")
            if len(sections) > 1:
                first_section_word_count = len(sections[0].split())
                last_section_word_count = len(sections[-1].split())
                if first_section_word_count < 100 and script_index > 0 and len(past_scripts) > 0:
                    previous_script = past_scripts.pop()
                    previous_script_file = f"{output_dir}/script{script_index - 1}.txt"
                    new_previous_script = previous_script + sections[0]

                    with open(previous_script_file, "w") as f:
                        f.write(new_previous_script)

                    past_scripts.append(new_previous_script)
                    sections.pop(0)
                    
                if last_section_word_count < 100 and script_index < len(excerpts) - 1:
                    left_over_excerpt = sections[-1]
                    sections = sections[:-1]

                # for all the remaining sections, save a new script file for each section while incrementing the excerpt_index
                for section in sections:
                    section_script_file = f"{output_dir}/script{script_index}.txt"
                    with open(section_script_file, "w") as f:
                        f.write(section)
                    script_index += 1

                continue

            print(f"Script: {script}")
            with open(script_file, "w") as f:
                f.write(script)

        script_index += 1
        past_scripts.append(script)

    # Pass 2: Use scripts to generate TikToks/videos based on existing script files
    past_tiktoks: List[str] = []
    script_paths = sorted(list(output_dir.glob("script*.txt")), key=lambda p: int(p.stem.replace("script", "")))
    for script_path in script_paths:
        script_index = int(script_path.stem.replace("script", ""))
        script_file = str(script_path)
        tiktok_file = f"{output_dir}/tiktok{script_index}.txt"
        video_file = f"{output_dir}/{script_index}.mp4"

        if os.path.exists(tiktok_file) and os.path.exists(video_file):
            script = open(script_file, "r").read()
            raw_tiktok = open(tiktok_file, "r").read()
            video_paths = [video_file]
            print(f"Using existing tiktok and video for excerpt {script_index}")
        else:
            script = open(script_file, "r").read()

            tiktok_data, raw_tiktok, video_paths = tiktok_generator(
                script,
                past_tiktoks[:PAST_TIKTOK_COUNT],
                visual_style=G.STYLE,
                voice_id=VOICE_ID,
                excerpt_index=script_index,
                output_dir=output_dir,
                process_videos=True
            )

            # Save tiktok text
            with open(tiktok_file, "w") as f:
                f.write(raw_tiktok)

        past_tiktoks.append(raw_tiktok)

        if video_paths:
            for i, video_path in enumerate(video_paths):
                print(f"Video saved to: {video_path}")
        else:
            print(f"No video generated for excerpt {script_index}")

        print(f"Completed excerpt {script_index}")