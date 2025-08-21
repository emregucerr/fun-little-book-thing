import os
import sys
import argparse
import uuid
import requests
from pathlib import Path
from typing import List, Dict

import globals as G
from functions.scene_designer import design_scene


def ensure_env() -> None:
    missing: List[str] = []
    for key in ["FAL_KEY", "BUNNY_STORAGE_ZONE", "BUNNY_API_KEY", "BUNNY_REGION"]:
        if not os.getenv(key):
            missing.append(key)
    if missing:
        print(f"Missing required environment variables: {', '.join(missing)}")
        print("Please export them before running this script.")
        sys.exit(1)


def build_default_entities() -> List[Dict[str, str]]:
    return []


def main() -> None:
    parser = argparse.ArgumentParser(description="Run design_scene and print resulting video URL")
    parser.add_argument("--visual", type=str, default="Minimalist depiction of semiconductor chips with export arrows pointing away from China; shadowy figures of tech leaders stand divided, some shaking hands, others turning away.", help="Visual description for the scene")
    parser.add_argument("--duration", type=str, default="9", help="Total duration in seconds (string between 3 and 12)")
    parser.add_argument("--style", type=str, default=G.STYLE, help="Visual style to apply")
    parser.add_argument("--download", action="store_true", help="Download the resulting video locally")
    parser.add_argument("--output", type=str, default=f"scene_{uuid.uuid4().hex}.mp4", help="Output file path if --download is set")

    args = parser.parse_args()

    ensure_env()

    named_entities = build_default_entities()

    print("Invoking design_scene... This can take a few minutes depending on generation.")
    try:
        video_url = design_scene(args.visual, args.style, args.duration, named_entities)
    except Exception as e:
        print(f"design_scene failed: {e}")
        sys.exit(1)

    print(f"Result video URL: {video_url}")

    if args.download:
        try:
            resp = requests.get(video_url, timeout=180)
            resp.raise_for_status()
            out_path = Path(args.output)
            out_path.write_bytes(resp.content)
            print(f"Video downloaded to: {out_path.resolve()}")
        except Exception as e:
            print(f"Failed to download video: {e}")


if __name__ == "__main__":
    main()


