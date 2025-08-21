import fal_client
from typing import Optional, List, Dict, Any
import time
import random


def generate_image(
    prompt: str,
    negative_prompt: str = "",
    aspect_ratio: str = "9:16", 
    num_images: int = 1,
    seed: Optional[int] = None,
    max_retries: int = 3,
    initial_delay: float = 1.0
) -> Dict[str, Any]:
    """
    Generate images using Fal AI's Imagen 4 model with retry mechanism.
    
    Args:
        prompt (str): The text prompt describing what you want to see
        negative_prompt (str, optional): Description of what to discourage in generated images. Defaults to "".
        aspect_ratio (str, optional): The aspect ratio of the generated image. Defaults to "9:16".
                                    Options: "1:1", "16:9", "9:16", "3:4", "4:3"
        num_images (int, optional): Number of images to generate (1-4). Defaults to 1.
        seed (int, optional): Random seed for reproducible generation. Defaults to None.
        max_retries (int, optional): Maximum number of retry attempts. Defaults to 3.
        initial_delay (float, optional): Initial delay between retries in seconds. Defaults to 1.0.
    
    Returns:
        Dict[str, Any]: Response containing:
            - images: List of generated images with URLs
            - seed: Seed used for generation
    
    Raises:
        Exception: If the API request fails after all retries
    """
    # Validate inputs
    if not prompt:
        raise ValueError("Prompt cannot be empty")
    
    if num_images < 1 or num_images > 4:
        raise ValueError("num_images must be between 1 and 4")
    
    valid_aspect_ratios = ["1:1", "16:9", "9:16", "3:4", "4:3"]
    if aspect_ratio not in valid_aspect_ratios:
        raise ValueError(f"aspect_ratio must be one of: {valid_aspect_ratios}")
    
    if max_retries < 0:
        raise ValueError("max_retries must be non-negative")
    
    if initial_delay < 0:
        raise ValueError("initial_delay must be non-negative")
    
    # Prepare arguments for the API call
    arguments = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "aspect_ratio": aspect_ratio,
        "num_images": num_images
    }
    
    # Add seed if provided
    if seed is not None:
        arguments["seed"] = seed
    
    def on_queue_update(update):
        """Handle queue updates and log progress"""
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                print(log["message"])
    
    # Retry mechanism with exponential backoff
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            print(f"Attempting image generation (attempt {attempt + 1}/{max_retries + 1})")
            
            # Make the API call
            result = fal_client.subscribe(
                "fal-ai/flux-pro/kontext/max/text-to-image",
                arguments=arguments,
                with_logs=True,
                on_queue_update=on_queue_update,
            )
            
            print("Image generation successful!")
            return result
            
        except Exception as e:
            last_exception = e
            
            if attempt < max_retries:
                # Calculate delay with exponential backoff and jitter
                delay = initial_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                print(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
            else:
                print(f"All {max_retries + 1} attempts failed.")
    
    # If we get here, all retries failed
    raise Exception(f"Failed to generate image after {max_retries + 1} attempts. Last error: {str(last_exception)}")


def get_image_urls(result: Dict[str, Any]) -> List[str]:
    """
    Extract image URLs from the API response.
    
    Args:
        result (Dict[str, Any]): The response from generate_image()
    
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
        
        # Ensure directory exists
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'wb') as f:
            f.write(response.content)
            
        print(f"Image saved as: {filename}")
        
    except Exception as e:
        raise Exception(f"Failed to save image: {str(e)}")


# Example usage
if __name__ == "__main__":
    # Example of how to use the function with retry mechanism
    try:
        result = generate_image(
            prompt="A beautiful sunset over mountains with vibrant colors",
            negative_prompt="blurry, low quality",
            aspect_ratio="9:16",
            num_images=1,
            max_retries=5,  # Retry up to 5 times
            initial_delay=2.0  # Start with 2 second delay
        )
        
        print("Generation completed!")
        print(f"Seed used: {result.get('seed')}")
        
        # Get image URLs
        urls = get_image_urls(result)
        print(f"Generated {len(urls)} image(s)")
        
        # Optionally save the first image
        if urls:
            save_image_from_url(urls[0], "generated_image.png")
            
    except Exception as e:
        print(f"Error: {e}")
