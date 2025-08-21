import globals as G
from prompts.scene_designer import design_scene_system_prompt, design_scene_user_prompt, design_video_system_prompt, design_video_user_prompt
from utils.generate_image import get_image_urls
from utils.generate_image_from_images import generate_image_from_images
from utils.generate_video import generate_video_from_image
from utils.llm_completion import llm_completion
from utils.upload_to_bunnycdn import upload_to_bunnycdn
from typing import List, Dict, Any
import re
import xml.etree.ElementTree as ET
import os
import uuid
import requests

try:
    from moviepy import VideoFileClip  # type: ignore[import-not-found]
except ImportError:
    VideoFileClip = None  # type: ignore[assignment]

TIKTOK_GENERATOR_MODEL = "gpt-5"


def _parse_scene_fallback(scene_text: str) -> List[Dict[str, Any]]:
    """Fallback parser to handle both quoted/unquoted durations and transition wrappers.

    Scans the scene text sequentially, capturing an optional preceding transition tag
    and the following <shot duration=...>...<\shot> block.
    """
    shots: List[Dict[str, Any]] = []
    pending_transition = "hard_cut"

    token_regex = re.compile(
        r"(?P<trans><\s*(?:hard_cut|continuous_transition)\s*(?:/)?\s*>)?\s*"
        r"<\s*shot\s+duration\s*=\s*(?:\"|\')?(?P<dur>\d+)(?:\"|\')?\s*>"
        r"(?P<desc>.*?)"
        r"</\s*shot\s*>",
        re.DOTALL | re.IGNORECASE,
    )

    for match in token_regex.finditer(scene_text):
        trans_tag = match.group("trans") or ""
        duration_text = match.group("dur") or "3"
        description_text = (match.group("desc") or "").strip()

        if trans_tag:
            if "continuous_transition" in trans_tag.lower():
                pending_transition = "continuous_transition"
            else:
                pending_transition = "hard_cut"

        try:
            dur_int = int(duration_text)
        except Exception:
            dur_int = 3

        shots.append({
            "description": description_text,
            "duration": str(max(1, min(5, dur_int))),
            "transition_from_prev": pending_transition,
        })

        # Reset after consuming a shot
        pending_transition = "hard_cut"

    return shots


def design_ai_video(visual: str, style: str, duration: str, named_entities: List[dict], first_frame_url: str = "") -> str:
    duration_int = int(duration)
    duration_int = max(duration_int, 3)
    duration_int = min(duration_int, 12)
    duration = str(duration_int)
    if not first_frame_url:
        """Design a single scene video from a visual description."""
        scene_messages = [{"role": "system", "content": design_video_system_prompt(visual, named_entities)}, {"role": "user", "content": design_video_user_prompt(visual, named_entities)}]
        response = llm_completion(TIKTOK_GENERATOR_MODEL, scene_messages)
        first_frame = response.split("<first_frame>")[1].split("</first_frame>")[0].strip()
        action = response.split("<action>")[1].split("</action>")[0].strip()
        image_prompt = first_frame + " " + style + " This is style must match the style in the style board you are given as an image."
        entitiy_images = [c['image'] for c in named_entities[:3]] if named_entities else []
        entitiy_images = [G.MOOD_BOARD_IMAGE] + entitiy_images
        result = generate_image_from_images(image_prompt, entitiy_images)
        urls = get_image_urls(result)
        image_url = urls[0]
        video_url = generate_video_from_image(prompt=action, image_url=image_url, duration=duration)
    else:
        video_url = generate_video_from_image(prompt=visual, image_url=first_frame_url, duration=duration)

    return video_url

def design_scene(visual: str, style: str, duration: str, named_entities: List[dict]) -> str:
    if int(duration) < 5:
        return design_ai_video(visual, style, duration, named_entities)
    else:
        cinema_messages: List[Dict[str, Any]] = [
            {"role": "system", "content": design_scene_system_prompt()},
            {"role": "user", "content": design_scene_user_prompt(visual, named_entities, duration)},
        ]
        cinema_response = llm_completion(TIKTOK_GENERATOR_MODEL, cinema_messages)
        print(cinema_response)

        # Ensure we have a <scene> payload
        scene_match = re.search(r"<scene>(.*?)</scene>", cinema_response, re.DOTALL)
        if not scene_match:
            # Fallback: just generate a single video if parsing fails
            return design_ai_video(visual, style, str(min(int(duration), 5)), named_entities)

        # Parse the <scene> block directly. Normalize minor syntax deviations (e.g., unquoted attributes)
        scene_inner = scene_match.group(1).strip()
        # Normalize <shot duration=2> → <shot duration="2">
        scene_inner = re.sub(r"<\s*shot\s+duration\s*=\s*(\d+)\s*>", r'<shot duration="\1">', scene_inner)
        scene_xml = f"<scene>{scene_inner}</scene>"

        # Parse XML into shots with transition info
        shots: List[Dict[str, Any]] = []
        try:
            root = ET.fromstring(scene_xml)
            # Traverse children in order, tracking the transition preceding each shot
            pending_transition = "hard_cut"
            for elem in list(root):
                tag = elem.tag.strip().lower()
                if tag in {"hard_cut", "continuous_transition"}:
                    pending_transition = "continuous_transition" if tag == "continuous_transition" else "hard_cut"
                    # There may also be nested <shot> elements inside transition tags
                    for sub in elem:
                        if sub.tag.strip().lower() == "shot":
                            dur_text = sub.attrib.get("duration", "3").strip()
                            try:
                                dur_int = int(dur_text)
                            except Exception:
                                dur_int = 3
                            desc = (sub.text or "").strip()
                            shots.append({
                                "description": desc,
                                "duration": str(max(1, min(5, dur_int))),
                                "transition_from_prev": pending_transition,
                            })
                            pending_transition = "hard_cut"
                elif tag == "shot":
                    dur_text = elem.attrib.get("duration", "3").strip()
                    try:
                        dur_int = int(dur_text)
                    except Exception:
                        dur_int = 3
                    desc = (elem.text or "").strip()
                    shots.append({
                        "description": desc,
                        "duration": str(max(1, min(5, dur_int))),
                        "transition_from_prev": pending_transition,
                    })
                    pending_transition = "hard_cut"
        except ET.ParseError as e:
            print(f"Failed to parse scene XML: {e}")
            # Fallback: regex-based tolerant parser
            shots = _parse_scene_fallback(scene_inner)
            if not shots:
                return design_ai_video(visual, style, str(min(int(duration), 5)), named_entities)

        # Generate per-shot videos, chaining continuous transitions via last-frame seeding
        generated_urls: List[str] = []
        prev_url: str | None = None
        for shot in shots:
            shot_visual = f"{shot['description']} {style}".strip()
            shot_duration = str(shot.get("duration", "3"))
            transition = shot.get("transition_from_prev", "hard_cut")

            first_frame_url: str = ""
            if transition == "continuous_transition" and prev_url:
                # Prepare first frame from the last frame of previous video
                try:
                    # Download previous video
                    temp_video_path = f"temp_prev_{uuid.uuid4().hex}.mp4"
                    r = requests.get(prev_url, timeout=60)
                    r.raise_for_status()
                    with open(temp_video_path, "wb") as f:
                        f.write(r.content)

                    # Extract last frame
                    if VideoFileClip is None:
                        raise ImportError("moviepy is required to extract frames. Install with `pip install moviepy`." )
                    clip = VideoFileClip(temp_video_path)
                    # Save last frame slightly before end to avoid boundary issues
                    last_frame_time = max(0.0, (clip.duration or 0) - 1e-3)
                    temp_image_path = f"temp_frame_{uuid.uuid4().hex}.png"
                    clip.save_frame(temp_image_path, t=last_frame_time)
                    clip.close()

                    # Upload frame to CDN
                    task_id = f"scene_{uuid.uuid4().hex}"
                    cdn_url = upload_to_bunnycdn(temp_image_path, task_id)
                    if cdn_url:
                        first_frame_url = cdn_url
                    # Cleanup
                    try:
                        if os.path.exists(temp_video_path):
                            os.remove(temp_video_path)
                        if os.path.exists(temp_image_path):
                            os.remove(temp_image_path)
                    except Exception:
                        pass
                except Exception as e:
                    print(f"Failed to seed continuous transition: {e}")

            shot_url = design_ai_video(
                shot_visual,
                style,
                shot_duration,
                named_entities,
                first_frame_url,
            )
            generated_urls.append(shot_url)
            prev_url = shot_url

        # If only one shot, return its URL
        if len(generated_urls) == 1:
            return generated_urls[0]

        # Merge multiple shot URLs into a single video, upload to CDN, and return CDN URL
        local_paths: List[str] = []
        clips = []
        try:
            if VideoFileClip is None:
                # Fallback: return the first URL if moviepy is unavailable
                return generated_urls[0]

            for url in generated_urls:
                temp_path = f"temp_shot_{uuid.uuid4().hex}.mp4"
                resp = requests.get(url, timeout=120)
                resp.raise_for_status()
                with open(temp_path, "wb") as f:
                    f.write(resp.content)
                local_paths.append(temp_path)
                clips.append(VideoFileClip(temp_path))

            # Concatenate
            from moviepy import concatenate_videoclips  # type: ignore[import-not-found]
            final = concatenate_videoclips(clips)
            merged_path = f"merged_scene_{uuid.uuid4().hex}.mp4"
            final.write_videofile(merged_path, codec='libx264', audio_codec='aac')
            final.close()
            for c in clips:
                c.close()

            cdn_merged = upload_to_bunnycdn(merged_path, f"scene_{uuid.uuid4().hex}")
            # Cleanup
            try:
                for p in local_paths:
                    if os.path.exists(p):
                        os.remove(p)
                if os.path.exists(merged_path):
                    os.remove(merged_path)
            except Exception:
                pass

            return cdn_merged or generated_urls[0]
        except Exception as e:
            print(f"Failed to merge shot videos: {e}")
            # Cleanup best-effort
            try:
                for c in clips:
                    c.close()
                for p in local_paths:
                    if os.path.exists(p):
                        os.remove(p)
            except Exception:
                pass
            return generated_urls[0]





