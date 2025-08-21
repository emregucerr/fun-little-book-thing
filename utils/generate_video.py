import os
import time
import random
from typing import Callable, Dict, Optional

try:
    import fal_client  # type: ignore
except ImportError as e:
    raise ImportError("fal-client package is required. Install it via `pip install fal-client`." ) from e

# Constants
_FAL_MODEL_ID_LTX = "fal-ai/ltxv-13b-098-distilled"
_FAL_MODEL_ID_PRO = "fal-ai/bytedance/seedance/v1/pro/text-to-video"
_FAL_MODEL_ID_PRO_IMAGE = "fal-ai/bytedance/seedance/v1/pro/image-to-video"

# Type aliases for clarity
QueueUpdateCallback = Callable[[fal_client.Status], None]


def _default_on_queue_update(update: "fal_client.Status") -> None:  # noqa: D401
    """Default callback to print status updates coming from FAL queue.

    It prints any log messages emitted while the request is *InProgress*.
    The signature matches the callback expected by *fal_client.subscribe*.
    """
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            # Each log entry is a dict like {"message": "..."}
            msg = log.get("message")
            if msg:
                print(msg)


def _get_model_config():
    """Get model configuration based on environment."""
    is_development = os.getenv("ENVIRONMENT", "").lower() == "development"
    
    if is_development:
        # LTX-Video 13B 0.9.8 Distilled model configuration
        return {
            "model_id": _FAL_MODEL_ID_PRO,
            "default_aspect_ratio": "9:16",
            "default_resolution": "480p", 
            "default_duration": "12",
            "allowed_aspect_ratios": ["21:9", "16:9", "4:3", "1:1", "3:4", "9:16"],
            "allowed_resolutions": ["480p", "1080p"],
            "model_type": "seedance"
        }
    else:
        # ByteDance Seedance Pro model configuration
        return {
            "model_id": _FAL_MODEL_ID_PRO,
            "default_aspect_ratio": "9:16",
            "default_resolution": "480p", 
            "default_duration": "12",
            "allowed_aspect_ratios": ["21:9", "16:9", "4:3", "1:1", "3:4", "9:16"],
            "allowed_resolutions": ["480p", "1080p"],
            "model_type": "seedance"
        }


def generate_video(
    prompt: str,
    *,
    aspect_ratio: str | None = None,
    resolution: str | None = None,
    duration: str | None = None,
    num_frames: int | None = None,
    frame_rate: int | None = None,
    negative_prompt: str | None = None,
    expand_prompt: bool | None = None,
    enable_detail_pass: bool | None = None,
    camera_fixed: bool | None = None,
    seed: int = -1,
    with_logs: bool = True,
    on_queue_update: Optional[QueueUpdateCallback] = None,
    max_retries: int = 3,
    initial_delay: float = 1.0,
) -> Dict[str, str]:  # noqa: D401
    """Generate a video from *prompt* using either LTX-Video (development) or ByteDance Seedance (production) with retry mechanism.

    Uses LTX-Video 13B 0.9.8 Distilled when ENVIRONMENT=development, ByteDance Seedance Pro otherwise.

    Parameters
    ----------
    prompt : str
        Text prompt describing the desired video.
    aspect_ratio : str, optional
        Desired aspect ratio. If None, uses model-specific default.
        LTX model: "9:16", "1:1", "16:9" (default "9:16")
        Seedance model: "21:9", "16:9", "4:3", "1:1", "3:4", "9:16" (default "9:16")
    resolution : str, optional
        Video resolution. If None, uses model-specific default.
        LTX model: "480p", "720p" (default "720p")
        Seedance model: "480p", "1080p" (default "1080p")
    duration : str, optional
        Video length in seconds (Seedance only). If None, uses default "12".
        Only applies to Seedance model: "3"-"12" (default "12")
    num_frames : int, optional
        Number of frames in the video (LTX only). If None, uses default 121.
        Only applies to LTX model: 9-1441 (default 121)
    frame_rate : int, optional
        Frame rate of the video (LTX only). If None, uses default 24.
        Only applies to LTX model: 1-60 (default 24)
    negative_prompt : str, optional
        Negative prompt for generation (LTX only).
        Default: "worst quality, inconsistent motion, blurry, jittery, distorted"
    expand_prompt : bool, optional
        Whether to expand the prompt using a language model (LTX only). Default False.
    enable_detail_pass : bool, optional
        Whether to use detail pass for enhanced quality (LTX only). Default False.
        Note: This incurs 2.0x cost multiplier.
    camera_fixed : bool | None, optional
        Whether to fix camera position (Seedance only). If *None*, parameter is omitted.
    seed : int, default -1
        Random seed. Use -1 to allow the backend to pick one.
    with_logs : bool, default True
        Whether to request log streaming from FAL and attach *on_queue_update*.
    on_queue_update : Callable, optional
        Callback executed with every queue update. If *None*, a simple printer is used.
    max_retries : int, default 3
        Maximum number of retry attempts.
    initial_delay : float, default 1.0
        Initial delay between retries in seconds.

    Returns
    -------
    dict
        A dictionary containing at least the keys ``video_url``.

    Raises
    ------
    RuntimeError
        If the FAL request fails after all retries or the response is malformed.
    ValueError
        If parameters are invalid for the selected model.
    """

    # Validate that FAL_KEY is set – this is required by the fal-client SDK.
    if not (os.getenv("FAL_KEY")):
        raise EnvironmentError(
            "Environment variable FAL_KEY is not set – it holds your FAL API key."
        )
    
    # Validate retry parameters
    if max_retries < 0:
        raise ValueError("max_retries must be non-negative")
    
    if initial_delay < 0:
        raise ValueError("initial_delay must be non-negative")

    # Get model configuration
    config = _get_model_config()
    
    # Use defaults if not specified
    if aspect_ratio is None:
        aspect_ratio = config["default_aspect_ratio"]
    if resolution is None:
        resolution = config["default_resolution"]
    
    # Validate parameters
    if aspect_ratio not in config["allowed_aspect_ratios"]:
        raise ValueError(f"Invalid aspect_ratio '{aspect_ratio}' for model. Allowed: {config['allowed_aspect_ratios']}")
    
    if resolution not in config["allowed_resolutions"]:
        raise ValueError(f"Invalid resolution '{resolution}' for model. Allowed: {config['allowed_resolutions']}")

    # Prepare arguments based on model type
    if config["model_type"] == "ltx":
        # LTX-Video model arguments
        if num_frames is None:
            num_frames = config["default_num_frames"]
        if frame_rate is None:
            frame_rate = config["default_frame_rate"]
        if negative_prompt is None:
            negative_prompt = "worst quality, inconsistent motion, blurry, jittery, distorted"
        
        # Validate LTX-specific parameters
        if not (9 <= num_frames <= 1441):
            raise ValueError(f"num_frames must be between 9 and 1441, got {num_frames}")
        if not (1 <= frame_rate <= 60):
            raise ValueError(f"frame_rate must be between 1 and 60, got {frame_rate}")
        
        arguments: Dict[str, object] = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "num_frames": num_frames,
            "frame_rate": frame_rate,
            "negative_prompt": negative_prompt,
        }
        
        # Add optional parameters if specified
        if seed != -1:
            arguments["seed"] = seed
        if expand_prompt is not None:
            arguments["expand_prompt"] = expand_prompt
        if enable_detail_pass is not None:
            arguments["enable_detail_pass"] = enable_detail_pass
            
    else:
        # Seedance model arguments
        if duration is None:
            duration = config["default_duration"]
            
        arguments: Dict[str, object] = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "duration": duration,
            "seed": seed,
        }

        # Only include camera_fixed if user explicitly provided a value
        if camera_fixed is not None:
            arguments["camera_fixed"] = camera_fixed

    # Choose callback – either user-provided or default printer.
    queue_cb = on_queue_update or _default_on_queue_update

    # Submit synchronously with retry mechanism
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            print(f"Attempting video generation (attempt {attempt + 1}/{max_retries + 1})")
            
            result = fal_client.subscribe(
                config["model_id"],
                arguments=arguments,
                with_logs=with_logs,
                on_queue_update=queue_cb if with_logs else None,
            )
            
            print("Video generation successful!")
            break
            
        except Exception as exc:  # noqa: BLE001
            last_exception = exc
            
            if attempt < max_retries:
                # Calculate delay with exponential backoff and jitter
                delay = initial_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Attempt {attempt + 1} failed: {str(exc)}")
                print(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
            else:
                print(f"All {max_retries + 1} attempts failed.")
    else:
        # If we get here, all retries failed
        raise RuntimeError(f"FAL video generation failed after {max_retries + 1} attempts. Last error: {str(last_exception)}") from last_exception

    # Handle response based on model type
    try:
        if config["model_type"] == "ltx":
            # LTX model response format: {"video": {"url": "..."}, "prompt": "...", "seed": 42}
            video_url: str = result["video"]["url"]  # type: ignore[index]
        else:
            # Seedance model response format: {"video": {"url": "..."}, "seed": 42}
            video_url: str = result["video"]["url"]  # type: ignore[index]
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Unexpected response format: {result}") from exc

    return video_url

# ---------------------------------------------------------------------------
# Seedance 1.0 Pro – Image-to-Video convenience wrapper
# ---------------------------------------------------------------------------


def generate_video_from_image(
    prompt: str,
    image_url: str,
    *,
    resolution: str | None = None,
    duration: str | None = None,
    camera_fixed: bool | None = None,
    seed: int = -1,
    with_logs: bool = True,
    on_queue_update: Optional[QueueUpdateCallback] = None,
    max_retries: int = 3,
    initial_delay: float = 1.0,
) -> str:
    """Generate a video from *prompt* and *image_url* using ByteDance Seedance 1.0 Pro (image-to-video) with retry mechanism.

    Parameters
    ----------
    prompt : str
        Text prompt describing the desired video.
    image_url : str
        Publicly reachable URL of the reference image.
    resolution : str, optional
        Video resolution, "480p" or "1080p" (default "1080p").
    duration : str, optional
        Video length in seconds, "3"-"12" (default "5").
    camera_fixed : bool, optional
        Whether to fix the camera position. If *None*, parameter is omitted.
    seed : int, default -1
        Random seed. Use -1 to let backend pick one.
    with_logs : bool, default True
        Whether to request log streaming from FAL and attach *on_queue_update*.
    on_queue_update : Callable, optional
        Callback executed with every queue update. If *None*, a simple printer is used.
    max_retries : int, default 3
        Maximum number of retry attempts.
    initial_delay : float, default 1.0
        Initial delay between retries in seconds.

    Returns
    -------
    str
        URL of the generated video.
    """

    # Ensure API key is available
    if not os.getenv("FAL_KEY"):
        raise EnvironmentError(
            "Environment variable FAL_KEY is not set – it holds your FAL API key."
        )
    
    # Validate retry parameters
    if max_retries < 0:
        raise ValueError("max_retries must be non-negative")
    
    if initial_delay < 0:
        raise ValueError("initial_delay must be non-negative")

    # Apply defaults
    if resolution is None:
        resolution = "480p"
    if duration is None:
        duration = "5"

    # Validate parameters
    if resolution not in {"480p", "1080p"}:
        raise ValueError("resolution must be '480p' or '1080p'")
    if duration not in {str(i) for i in range(3, 13)}:
        raise ValueError("duration must be a string between '3' and '12' inclusive")

    # Build argument dict
    arguments: Dict[str, object] = {
        "prompt": prompt,
        "image_url": image_url,
        "resolution": resolution,
        "duration": duration,
        "seed": seed,
    }

    # Include optional parameter only if explicitly set
    if camera_fixed is not None:
        arguments["camera_fixed"] = camera_fixed

    queue_cb = on_queue_update or _default_on_queue_update

    # Submit with retry mechanism
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            print(f"Attempting image-to-video generation (attempt {attempt + 1}/{max_retries + 1})")
            
            result = fal_client.subscribe(
                _FAL_MODEL_ID_PRO_IMAGE,
                arguments=arguments,
                with_logs=with_logs,
                on_queue_update=queue_cb if with_logs else None,
            )
            
            print("Image-to-video generation successful!")
            break
            
        except Exception as exc:  # noqa: BLE001
            last_exception = exc
            
            if attempt < max_retries:
                # Calculate delay with exponential backoff and jitter
                delay = initial_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Attempt {attempt + 1} failed: {str(exc)}")
                print(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
            else:
                print(f"All {max_retries + 1} attempts failed.")
    else:
        # If we get here, all retries failed
        raise RuntimeError(f"FAL image-to-video generation failed after {max_retries + 1} attempts. Last error: {str(last_exception)}") from last_exception

    try:
        video_url: str = result["video"]["url"]  # type: ignore[index]
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Unexpected response format: {result}") from exc

    return video_url


if __name__ == "__main__":
    print(generate_video(
        "A bright blue race car speeds along a snowy racetrack. [Low-angle shot] Captures several cars speeding along the racetrack through a harsh snowstorm. [Overhead shot] The camera gradually pulls upward, revealing the full race scene illuminated by storm lights",
        max_retries=5,  # Retry up to 5 times
        initial_delay=2.0  # Start with 2 second delay
    ))