import fal_client
from typing import Optional, List, Dict, Any
import time
import random


def generate_image_from_images(
    prompt: str,
    image_urls: List[str],
    seed: Optional[int] = None,
    guidance_scale: float = 3.5,
    sync_mode: bool = False,
    num_images: int = 1,
    output_format: str = "jpeg",
    safety_tolerance: str = "6",
    enhance_prompt: bool = False,
    aspect_ratio: Optional[str] = "9:16",
    max_retries: int = 3,
    initial_delay: float = 1.0
) -> Dict[str, Any]:
    """
    Generate images with FLUX.1 Kontext [pro] using multiple input images.

    Args:
        prompt (str): Text prompt guiding the generation.
        image_urls (List[str]): List of image URLs to condition on (at least one).
        seed (int, optional): Random seed for reproducibility.
        guidance_scale (float, optional): CFG scale, 1-20. Defaults to 3.5.
        sync_mode (bool, optional): If True, waits for direct upload. Defaults to False.
        num_images (int, optional): Number of images to generate (1-4). Defaults to 1.
        output_format (str, optional): "jpeg" or "png". Defaults to "jpeg".
        safety_tolerance (str, optional): "1"-"6". Defaults to "6".
        enhance_prompt (bool, optional): Whether to enhance the prompt. Defaults to False.
        aspect_ratio (str, optional): One of ["21:9","16:9","4:3","3:2","1:1","2:3","3:4","9:16","9:21"].
        max_retries (int, optional): Max retry attempts. Defaults to 3.
        initial_delay (float, optional): Initial backoff delay in seconds. Defaults to 1.0.

    Returns:
        Dict[str, Any]: Response containing generated images and metadata.

    Raises:
        Exception: If the API request fails after all retries.
    """
    # Validate inputs
    image_urls = image_urls[:3] if image_urls else []
    if not prompt:
        raise ValueError("Prompt cannot be empty")

    if not isinstance(image_urls, list) or len(image_urls) == 0:
        raise ValueError("image_urls must be a non-empty list of URLs")

    if not all(isinstance(u, str) and u.strip() for u in image_urls):
        raise ValueError("All items in image_urls must be non-empty strings")

    if guidance_scale < 1 or guidance_scale > 20:
        raise ValueError("guidance_scale must be between 1 and 20")

    if num_images < 1 or num_images > 4:
        raise ValueError("num_images must be between 1 and 4")

    valid_output_formats = ["jpeg", "png"]
    if output_format not in valid_output_formats:
        raise ValueError(f"output_format must be one of: {valid_output_formats}")

    valid_safety_levels = ["1", "2", "3", "4", "5", "6"]
    if safety_tolerance not in valid_safety_levels:
        raise ValueError(f"safety_tolerance must be one of: {valid_safety_levels}")

    valid_aspect_ratios = ["21:9", "16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16", "9:21"]
    if aspect_ratio is not None and aspect_ratio not in valid_aspect_ratios:
        raise ValueError(f"aspect_ratio must be one of: {valid_aspect_ratios}")

    if max_retries < 0:
        raise ValueError("max_retries must be non-negative")

    if initial_delay < 0:
        raise ValueError("initial_delay must be non-negative")

    # Force maximum safety tolerance to minimize NSFW filtering
    safety_tolerance = "6"

    # Prepare arguments for the API call
    arguments: Dict[str, Any] = {
        "prompt": prompt,
        "image_urls": image_urls,
        "guidance_scale": guidance_scale,
        "sync_mode": sync_mode,
        "num_images": num_images,
        "output_format": output_format,
        "safety_tolerance": safety_tolerance,
        "enhance_prompt": enhance_prompt,
    }

    if aspect_ratio is not None:
        arguments["aspect_ratio"] = aspect_ratio

    if seed is not None:
        arguments["seed"] = seed

    def on_queue_update(update):
        """Handle queue updates and log progress"""
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                print(log["message"])

    # Retry mechanism with exponential backoff
    last_exception: Optional[Exception] = None

    for attempt in range(max_retries + 1):
        try:
            print(f"Attempting multi-image generation (attempt {attempt + 1}/{max_retries + 1})")

            result = fal_client.subscribe(
                "fal-ai/flux-pro/kontext/multi",
                arguments=arguments,
                with_logs=True,
                on_queue_update=on_queue_update,
            )

            print("Image generation successful!")
            return result

        except Exception as e:  # noqa: BLE001 - surface last exception
            last_exception = e

            if attempt < max_retries:
                delay = initial_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                print(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
            else:
                print(f"All {max_retries + 1} attempts failed.")

    raise Exception(
        f"Failed to generate image after {max_retries + 1} attempts. Last error: {str(last_exception)}"
    )


def get_image_urls(result: Dict[str, Any]) -> List[str]:
    """
    Extract image URLs from the API response.

    Args:
        result (Dict[str, Any]): The response from generate_image_from_images()

    Returns:
        List[str]: List of image URLs
    """
    if "images" not in result:
        raise ValueError("Invalid response: missing 'images' field")

    return [img["url"] for img in result["images"]]


def save_image_from_url(url: str, filename: str) -> None:
    """
    Download and save an image from a URL.

    Args:
        url (str): The image URL
        filename (str): Local filename to save the image
    """
    import requests  # type: ignore
    from pathlib import Path

    try:
        response = requests.get(url)
        response.raise_for_status()

        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        with open(filename, 'wb') as f:
            f.write(response.content)

        print(f"Image saved as: {filename}")

    except Exception as e:
        raise Exception(f"Failed to save image: {str(e)}")


if __name__ == "__main__":
    # Minimal example usage
    try:
        result = generate_image_from_images(
            prompt="Put the little duckling on top of the woman's t-shirt.",
            image_urls=[
                "https://v3.fal.media/files/penguin/XoW0qavfF-ahg-jX4BMyL_image.webp",
                "https://v3.fal.media/files/tiger/bml6YA7DWJXOigadvxk75_image.webp",
            ],
            num_images=1,
        )

        urls = get_image_urls(result)
        print(f"Generated {len(urls)} image(s)")
        if urls:
            save_image_from_url(urls[0], "generated_multi_image.png")

    except Exception as e:
        print(f"Error: {e}")


