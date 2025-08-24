import fal_client
from typing import Optional, Dict, Any
import time
import random


def generate_transition_video(
    prompt: str,
    first_image_url: str,
    last_image_url: str,
    aspect_ratio: str = "9:16",
    resolution: str = "720p",
    duration: str = "5",
    negative_prompt: str = "",
    style: Optional[str] = None,
    seed: Optional[int] = None,
    movement_amplitude: Optional[str] = None,
    max_retries: int = 3,
    initial_delay: float = 1.0,
) -> str:
    """
    Create a seamless transition video between two images using Vidu Q1 Start-End to Video.

    Args:
        prompt (str): The prompt guiding the transition.
        first_image_url (str): URL of the first frame image.
        last_image_url (str): URL of the last frame image.
        seed (int, optional): Seed for reproducibility.
        movement_amplitude (str, optional): One of ["auto", "small", "medium", "large"].
        max_retries (int, optional): Max retry attempts. Defaults to 3.
        initial_delay (float, optional): Initial backoff delay in seconds. Defaults to 1.0.

    Returns:
        str: URL of the generated video file.

    Raises:
        Exception: If the API request fails after all retries.
    """
    if not prompt or not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("prompt must be a non-empty string")

    if not first_image_url or not isinstance(first_image_url, str) or not first_image_url.strip():
        raise ValueError("first_image_url must be a non-empty string URL")

    if not last_image_url or not isinstance(last_image_url, str) or not last_image_url.strip():
        raise ValueError("last_image_url must be a non-empty string URL")

    valid_movement = ["auto", "small", "medium", "large"]
    if movement_amplitude is not None and movement_amplitude not in valid_movement:
        raise ValueError(f"movement_amplitude must be one of: {valid_movement}")

    if max_retries < 0:
        raise ValueError("max_retries must be non-negative")

    if initial_delay < 0:
        raise ValueError("initial_delay must be non-negative")

    arguments: Dict[str, Any] = {
        "prompt": prompt,
        "start_image_url": first_image_url,
        "end_image_url": last_image_url,
    }

    if seed is not None:
        arguments["seed"] = seed

    if movement_amplitude is not None:
        arguments["movement_amplitude"] = movement_amplitude

    def on_queue_update(update):
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                print(log["message"])  # noqa: T201

    last_exception: Optional[Exception] = None
    for attempt in range(max_retries + 1):
        try:
            print(  # noqa: T201
                f"Attempting Vidu start-end video generation (attempt {attempt + 1}/{max_retries + 1})"
            )

            result = fal_client.subscribe(
                "fal-ai/vidu/start-end-to-video",
                arguments=arguments,
                with_logs=True,
                on_queue_update=on_queue_update,
            )

            print("Video generation successful!")  # noqa: T201
            return get_video_url(result)

        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                delay = initial_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Attempt {attempt + 1} failed: {str(e)}")  # noqa: T201
                print(f"Retrying in {delay:.2f} seconds...")  # noqa: T201
                time.sleep(delay)
            else:
                print(f"All {max_retries + 1} attempts failed.")  # noqa: T201

    raise Exception(
        f"Failed to generate video after {max_retries + 1} attempts. Last error: {str(last_exception)}"
    )


def get_video_url(result: Dict[str, Any]) -> str:
    """
    Extract the video URL from the API response.

    Args:
        result (Dict[str, Any]): The response from generate_pixverse_transition_video()

    Returns:
        str: The URL to the generated video file.
    """
    if "video" not in result or not isinstance(result["video"], dict):
        raise ValueError("Invalid response: missing 'video' field")

    if "url" not in result["video"] or not isinstance(result["video"]["url"], str):
        raise ValueError("Invalid response: missing 'video.url' field")

    return result["video"]["url"]


def save_video_from_url(url: str, filename: str) -> None:
    """
    Download and save a video from a URL.

    Args:
        url (str): The video URL.
        filename (str): Local filename to save the video.
    """
    import requests  # type: ignore
    from pathlib import Path

    try:
        response = requests.get(url)
        response.raise_for_status()

        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        with open(filename, "wb") as f:
            f.write(response.content)

        print(f"Video saved as: {filename}")  # noqa: T201

    except Exception as e:  # noqa: BLE001
        raise Exception(f"Failed to save video: {str(e)}")


if __name__ == "__main__":
    try:
        video_url = generate_transition_video(
            prompt="Scene slowly transition into cat swimming under water",
            first_image_url="https://v3.fal.media/files/zebra/owQh2DAzk8UU7J02nr5RY_Co2P4boLv6meIZ5t9gKvL_8685da151df343ab8bf82165c928e2a5.jpg",
            last_image_url="https://v3.fal.media/files/kangaroo/RgedFs_WSnq5BgER7qDx1_ONrbTJ1YAGXz-9JnSsBoB_bdc8750387734bfe940319f469f7b0b2.jpg",
        )
        print("Generated video URL:", video_url)  # noqa: T201
        save_video_from_url(video_url, "generated_transition_video.mp4")

    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}")  # noqa: T201


