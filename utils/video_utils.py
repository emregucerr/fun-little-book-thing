from typing import Any

from moviepy import VideoFileClip

try:
    # Import types lazily; function works with any MoviePy-like clip
    from moviepy import VideoClip  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - moviepy might not be installed in some environments
    VideoClip = Any  # type: ignore[assignment]


def retime_clip_to_duration(clip: Any, target_duration: float) -> Any:
    """Return a new clip retimed to match target_duration seconds.

    - Speeds up if original > target
    - Slows down if original < target
    - No change if invalid inputs or difference is negligible
    """
    try:
        if clip is None:
            return clip

        original_duration = float(getattr(clip, "duration", 0.0) or 0.0)
        if (
            target_duration is None
            or target_duration <= 0
            or original_duration <= 0
            or abs(original_duration - float(target_duration)) <= 1e-3
        ):
            return clip

        # Preferred: built-in speed scaling to set exact final duration
        try:
            return clip.with_speed_scaled(final_duration=float(target_duration))
        except Exception:
            # Fallback: manual time transform using scaling factor
            factor = original_duration / float(target_duration)
            return clip.time_transform(
                lambda t: factor * t, apply_to=["mask", "audio"], keep_duration=True
            )

    except Exception:
        # On any unexpected error, return the original clip unchanged
        return clip
    
if __name__ == "__main__":
    source_path = "/Users/ahmetemregucer/Downloads/K03B4R6B9FnwpBc4ItYW8_output.mp4"
    target_duration = 3.0

    original_clip = VideoFileClip(source_path)
    retimed_clip = original_clip
    try:
        original_duration = float(getattr(original_clip, "duration", 0.0) or 0.0)
        print(f"Original duration: {original_duration:.3f} seconds")

        retimed_clip = retime_clip_to_duration(original_clip, target_duration)
        new_duration = float(getattr(retimed_clip, "duration", 0.0) or 0.0)
        print(f"Retimed duration (target={target_duration:.3f}): {new_duration:.3f} seconds")

        retimed_clip.write_videofile("temp_shot_1_retimed.mp4", codec='libx264', audio_codec='aac')
    finally:
        try:
            original_clip.close()
        except Exception:
            pass
        try:
            if retimed_clip is not original_clip:
                retimed_clip.close()
        except Exception:
            pass


