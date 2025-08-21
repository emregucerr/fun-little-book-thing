import os
import tempfile
import openai
from moviepy import VideoFileClip, TextClip, CompositeVideoClip


def _srt_time_to_seconds(time_str: str) -> float:
    """Convert an SRT timestamp (HH:MM:SS,mmm) to seconds."""
    hours, minutes, rest = time_str.split(":")
    seconds, milliseconds = rest.split(",")
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000.0


def _parse_srt(srt_str: str):
    """Parse a minimal SRT string into a list of (start_sec, end_sec, text) tuples."""
    captions = []
    for block in srt_str.strip().split("\n\n"):
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 3:
            continue  # not a valid caption block
        # lines[0] is the caption index, ignore
        time_range = lines[1]
        start_str, end_str = [t.strip() for t in time_range.split("-->")]
        text = " ".join(lines[2:])
        captions.append((_srt_time_to_seconds(start_str), _srt_time_to_seconds(end_str), text))
    return captions


def _transcribe_video_to_srt(video_path: str, model: str = "whisper-1") -> str:
    """Run OpenAI Whisper transcription and obtain the result in SRT format."""
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError(
            "OPENAI_API_KEY environment variable is not set. Please set it to use transcription.")
    with open(video_path, "rb") as f:
        response = openai.audio.transcriptions.create(
            model=model,
            file=f,
            response_format="srt",
        )
    # The v1 OpenAI library returns a plain str when response_format is "srt"
    return response if isinstance(response, str) else response.text  # type: ignore


def add_subtitles_to_video(
    video_path: str,
    output_path: str,
    font_size: int = 60,
    font_family: str = "Arial-Bold",
    whisper_model: str = "whisper-1",
):
    """Automatically transcribe *video_path* and burn subtitles into *output_path*.

    Parameters
    ----------
    video_path: str
        Path to the input video file (any format supported by FFmpeg).
    output_path: str
        Where the subtitled video will be written.
    font_size: int, optional
        Font size for the subtitles (default 60).
    font_family: str, optional
        Font to use for the subtitles (default "Arial-Bold").
    whisper_model: str, optional
        Whisper model name to use (default "whisper-1").
    """

    # 1. Transcribe the video to SRT using Whisper
    print("Transcribing video with OpenAI Whisper – this may take a while …")
    srt_data = _transcribe_video_to_srt(video_path, model=whisper_model)
    captions = _parse_srt(srt_data)
    if not captions:
        raise RuntimeError("No captions were produced from the transcription.")

    # 2. Create subtitle clips
    video = VideoFileClip(video_path)
    subtitle_clips = []
    bottom_y = int(video.h * 0.85)  # 15% from the bottom of the frame

    for start, end, text in captions:
        # Create a simple text clip without fancy font options
        txt_clip = (
            TextClip(
                text=text,
                font_size=int(font_size),
                color="white",
                method="caption",
                size=(int(video.w * 0.8), None),
            )
            .with_start(start)
            .with_end(end)
            .with_position(("center", bottom_y))
        )
        subtitle_clips.append(txt_clip)

    # 3. Composite and export
    final = CompositeVideoClip([video, *subtitle_clips])
    final.write_videofile(output_path, codec="libx264", audio_codec="aac")

    # Cleanup resources
    final.close()
    video.close()
    for clip in subtitle_clips:
        clip.close()

    return output_path


if __name__ == "__main__":
    # Test with a video file from the project
    test_video = "simple_test.mp4"
    output_video = "auto_subtitle_test.mp4"
    
    if os.path.exists(test_video):
        print(f"Testing automatic subtitles with {test_video}")
        try:
            result = add_subtitles_to_video(test_video, output_video)
            print(f"Success! Created subtitled video: {result}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Test video {test_video} not found. Available videos:")
        for file in os.listdir("."):
            if file.endswith((".mp4", ".avi", ".mov")):
                print(f"  - {file}") 