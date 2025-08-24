import fal_client
from typing import Optional, Dict, Any, List
import time
import random


def generate_style_transfer(
    image_url: str,
    prompt: Optional[str] = "Van Gogh's Starry Night",
    guidance_scale: float = 9,
    num_inference_steps: int = 30,
    safety_tolerance: str = "6",
    output_format: str = "jpeg",
    aspect_ratio: Optional[str] = None,
    seed: Optional[int] = None,
    sync_mode: bool = False,
    max_retries: int = 3,
    initial_delay: float = 1.0,
) -> str:
    """
    Apply an artistic style transfer to an input image using fal.ai's Style Transfer model.

    Endpoint/Model: fal-ai/image-editing/style-transfer

    Args:
        image_url (str): URL to the input image to stylize.
        prompt (str, optional): Artistic style description (e.g., "Van Gogh's Starry Night").
        guidance_scale (float, optional): CFG scale 0-20. Defaults to 9.
        num_inference_steps (int, optional): Sampling steps 1-50. Defaults to 30.
        safety_tolerance (str, optional): Safety level "1"-"6". Defaults to "6".
        output_format (str, optional): "jpeg" or "png". Defaults to "jpeg".
        aspect_ratio (str, optional): One of ["21:9","16:9","4:3","3:2","1:1","2:3","3:4","9:16","9:21"].
        seed (int, optional): Seed for reproducibility.
        sync_mode (bool, optional): Wait for direct upload in response. Defaults to False.
        max_retries (int, optional): Maximum retry attempts. Defaults to 3.
        initial_delay (float, optional): Initial backoff delay in seconds. Defaults to 1.0.

    Returns:
        str: URL of the generated stylized image.

    Raises:
        Exception: If the API request fails after all retries.
    """
    # Validate inputs
    if not isinstance(image_url, str) or not image_url.strip():
        raise ValueError("image_url must be a non-empty string")

    if prompt is not None and not isinstance(prompt, str):
        raise ValueError("prompt must be a string if provided")

    if guidance_scale < 0 or guidance_scale > 20:
        raise ValueError("guidance_scale must be between 0 and 20")

    if num_inference_steps < 1 or num_inference_steps > 50:
        raise ValueError("num_inference_steps must be between 1 and 50")

    valid_safety_levels = ["1", "2", "3", "4", "5", "6"]
    if safety_tolerance not in valid_safety_levels:
        raise ValueError(f"safety_tolerance must be one of: {valid_safety_levels}")

    valid_output_formats = ["jpeg", "png"]
    if output_format not in valid_output_formats:
        raise ValueError(f"output_format must be one of: {valid_output_formats}")

    valid_aspect_ratios = ["21:9", "16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16", "9:21"]
    if aspect_ratio is not None and aspect_ratio not in valid_aspect_ratios:
        raise ValueError(f"aspect_ratio must be one of: {valid_aspect_ratios}")

    if max_retries < 0:
        raise ValueError("max_retries must be non-negative")

    if initial_delay < 0:
        raise ValueError("initial_delay must be non-negative")

    if sync_mode not in (True, False):
        raise ValueError("sync_mode must be a boolean")

    # Prepare arguments for the API call
    arguments: Dict[str, Any] = {
        "image_url": image_url,
        "guidance_scale": guidance_scale,
        "num_inference_steps": num_inference_steps,
        "safety_tolerance": safety_tolerance,
        "output_format": output_format,
        "sync_mode": sync_mode,
    }

    if prompt is not None:
        arguments["prompt"] = prompt

    if aspect_ratio is not None:
        arguments["aspect_ratio"] = aspect_ratio

    if seed is not None:
        arguments["seed"] = seed

    def on_queue_update(update):
        """Handle queue updates and log progress."""
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                print(log["message"])  # noqa: T201

    # Retry mechanism with exponential backoff
    last_exception: Optional[Exception] = None

    for attempt in range(max_retries + 1):
        try:
            print(  # noqa: T201
                f"Attempting style transfer (attempt {attempt + 1}/{max_retries + 1})"
            )

            result = fal_client.subscribe(
                "fal-ai/image-editing/style-transfer",
                arguments=arguments,
                with_logs=True,
                on_queue_update=on_queue_update,
            )

            if "images" not in result or not result["images"]:
                raise Exception("Invalid response: missing 'images' or empty images list")

            image_url_result = result["images"][0]["url"]
            print("Style transfer successful!")  # noqa: T201
            return image_url_result

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
        f"Failed to perform style transfer after {max_retries + 1} attempts. Last error: {str(last_exception)}"
    )


def get_image_urls(result: Dict[str, Any]) -> List[str]:
    """
    Extract image URLs from the API response.

    Args:
        result (Dict[str, Any]): The response from generate_style_transfer()

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

        with open(filename, "wb") as f:
            f.write(response.content)

        print(f"Image saved as: {filename}")  # noqa: T201

    except Exception as e:  # noqa: BLE001 - surface last exception
        raise Exception(f"Failed to save image: {str(e)}")


if __name__ == "__main__":
    # Minimal example usage
    try:
        image_url_result = generate_style_transfer(
            image_url="https://v3.fal.media/files/zebra/hAjCkcyly4gsS9-cptD3Y_image%20(20).png",
            prompt="Van Gogh's Starry Night",
            output_format="jpeg",
        )

        print("Generated image URL:", image_url_result)  # noqa: T201
        if image_url_result:
            save_image_from_url(image_url_result, "generated_style_transfer.jpg")

    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}")  # noqa: T201


