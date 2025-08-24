import fal_client
from typing import Optional, List, Dict, Any
import time
import random
import globals as G
import io
import os
import re
import tempfile
from PIL import Image  # type: ignore
import requests  # type: ignore

from utils.generate_image import generate_image, get_image_urls as get_single_image_urls
from utils.generate_style_transfer import generate_style_transfer
from utils.upload_to_bunnycdn import upload_to_bunnycdn


def _parse_aspect_ratio(aspect_ratio: str) -> float:
    """
    Convert an aspect ratio string like "9:16" into a float (width / height).
    """
    try:
        parts = aspect_ratio.split(":")
        if len(parts) != 2:
            raise ValueError
        width_part = float(parts[0])
        height_part = float(parts[1])
        if width_part <= 0 or height_part <= 0:
            raise ValueError
        return width_part / height_part
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Invalid aspect_ratio format: {aspect_ratio}") from exc


def _ratios_close(r1: float, r2: float, tolerance: float = 0.01) -> bool:
    return abs(r1 - r2) <= tolerance


def _slugify(value: str) -> str:
    value = value.strip().lower()
    # Replace all non-word characters with hyphens
    value = re.sub(r"[^a-z0-9]+", "-", value)
    # Collapse multiple hyphens
    value = re.sub(r"-+", "-", value)
    return value.strip("-") or "generated"


def _ensure_aspect_ratio_and_upload_if_needed(
    image_url: str,
    desired_aspect_ratio: str,
    output_format: str = "jpeg",
    task_id: Optional[str] = None,
) -> str:
    """
    Download the image URL, verify aspect ratio, and if mismatched, center-crop
    to the target aspect ratio with minimal content loss. If cropped, upload to
    BunnyCDN and return the CDN URL. Otherwise, return the original URL.
    """
    try:
        # Fetch image bytes
        response = requests.get(image_url, timeout=60)
        response.raise_for_status()
        image_bytes = io.BytesIO(response.content)

        with Image.open(image_bytes) as img:
            width, height = img.size
            current_ratio = width / max(height, 1)
            target_ratio = _parse_aspect_ratio(desired_aspect_ratio)

            if _ratios_close(current_ratio, target_ratio):
                return image_url

            # Compute centered crop rectangle to match target_ratio
            if current_ratio > target_ratio:
                # Too wide: crop width
                new_width = int(round(height * target_ratio))
                new_width = max(1, min(new_width, width))
                left = (width - new_width) // 2
                top = 0
                right = left + new_width
                bottom = height
            else:
                # Too tall: crop height
                new_height = int(round(width / target_ratio))
                new_height = max(1, min(new_height, height))
                left = 0
                top = (height - new_height) // 2
                right = width
                bottom = top + new_height

            cropped = img.crop((left, top, right, bottom))

            # Prepare temp file
            fmt = (output_format or "jpeg").lower()
            ext = ".jpg" if fmt in ("jpeg", "jpg") else ".png"
            pil_format = "JPEG" if ext == ".jpg" else "PNG"

            if pil_format == "JPEG" and cropped.mode in ("RGBA", "P"):
                cropped = cropped.convert("RGB")

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
            temp_file_path = temp_file.name
            temp_file.close()

            save_kwargs: Dict[str, Any] = {}
            if pil_format == "JPEG":
                save_kwargs = {"quality": 95, "optimize": True}

            try:
                cropped.save(temp_file_path, pil_format, **save_kwargs)
            except Exception:
                # As a fallback, try PNG
                temp_file_path_png = temp_file_path[:-4] + ".png"
                cropped.save(temp_file_path_png, "PNG")
                temp_file_path = temp_file_path_png

            # Determine task_id
            if not task_id:
                try:
                    book = getattr(G, "BOOK_NAME", "generated")
                except Exception:
                    book = "generated"
                task_id = _slugify(str(book))

            # Upload to BunnyCDN
            cdn_url = upload_to_bunnycdn(temp_file_path, task_id=task_id)

            # Cleanup local temp file
            try:
                os.remove(temp_file_path)
            except Exception:
                pass

            if cdn_url:
                return cdn_url

            # If upload failed, fall back to original URL
            return image_url

    except Exception:
        # On any failure, do not block the flow; return original URL
        return image_url


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
    initial_delay: float = 1.0,
    auto_style_transfer: bool = True,
) -> str:
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
        str: URL of the generated image.

    Raises:
        Exception: If the API request fails after all retries.
    """
    # Validate inputs
    image_urls = image_urls[:3] if image_urls else []
    if not prompt:
        raise ValueError("Prompt cannot be empty")

    if not isinstance(image_urls, list) or len(image_urls) == 0:
        # Fallback to single-image generation and return first URL
        result = generate_image(
            prompt=prompt,
            aspect_ratio=aspect_ratio if aspect_ratio is not None else "9:16",
            num_images=1,
            seed=seed,
            max_retries=max_retries,
            initial_delay=initial_delay,
        )
        urls = get_single_image_urls(result)
        if not urls:
            raise Exception("Image generation returned no images")
        image_url = urls[0]
        if auto_style_transfer:
            image_url = generate_style_transfer(image_url, G.STYLE)
        # Ensure aspect ratio and upload cropped version if needed
        image_url = _ensure_aspect_ratio_and_upload_if_needed(
            image_url=image_url,
            desired_aspect_ratio=aspect_ratio if aspect_ratio is not None else "9:16",
            output_format=output_format,
        )
        return image_url

    if not all(isinstance(u, str) and u.strip() for u in image_urls):
        raise ValueError("All items in image_urls must be non-empty strings")

    if guidance_scale < 1 or guidance_scale > 20:
        raise ValueError("guidance_scale must be between 1 and 20")

    # Always generate exactly 1 image
    num_images = 1

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
        "num_images": 1,
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

            if "images" not in result or not result["images"]:
                raise Exception("Invalid response: missing 'images' or empty images list")

            print("Image generation successful!")
            image_url = result["images"][0]["url"]
            if auto_style_transfer:
                image_url = generate_style_transfer(image_url, G.STYLE)
            # Ensure aspect ratio and upload cropped version if needed
            image_url = _ensure_aspect_ratio_and_upload_if_needed(
                image_url=image_url,
                desired_aspect_ratio=aspect_ratio if aspect_ratio is not None else "9:16",
                output_format=output_format,
            )
            return image_url

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
        image_url = generate_image_from_images(
            prompt="Put the little duckling on top of the woman's t-shirt.",
            image_urls=[
                "https://v3.fal.media/files/penguin/XoW0qavfF-ahg-jX4BMyL_image.webp",
                "https://v3.fal.media/files/tiger/bml6YA7DWJXOigadvxk75_image.webp",
            ],
        )

        print("Generated image URL:", image_url)
        if image_url:
            save_image_from_url(image_url, "generated_multi_image.png")

    except Exception as e:
        print(f"Error: {e}")


