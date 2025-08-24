import os
import uuid
from pathlib import Path
from typing import Optional, Union

try:
    # ElevenLabs SDK (``pip install elevenlabs``)
    from elevenlabs.client import ElevenLabs  # type: ignore
    from elevenlabs import VoiceSettings  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "The `elevenlabs` package is required for voice generation. Install it via `pip install elevenlabs`."
    ) from exc

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    # dotenv not available, continue without it
    pass

__all__ = ["generate_voiceover"]


def generate_voiceover(
    text: str,
    *,
    voice_id: str,
    model_id: str = "eleven_turbo_v2_5",
    output_format: str = "mp3_44100_128",
    output_file: Optional[os.PathLike | str] = None,
    speed: float = 1.0,
) -> Union[bytes, str]:  # noqa: D401
    """Generate speech audio from *text* with ElevenLabs.

    Parameters
    ----------
    text : str
        The text that will be converted to speech.
    voice_id : str
        ID of the ElevenLabs voice to use (see the *Voices* tab in the ElevenLabs dashboard).
    model_id : str, default "eleven_multilingual_v2"
        Text-to-speech model to use. See ElevenLabs documentation for alternatives such as
        ``eleven_turbo_v2_5`` or ``eleven_flash_v2_5``.
    output_format : str, default "mp3_44100_128"
        Desired audio format. Examples: ``mp3_44100_128``, ``wav``.
    output_file : pathlike or str, optional
        If provided, the generated audio will be written to this path. The parent directory is
        created if it doesn't exist. If *None* (default), the raw audio bytes are returned.
    speed : float, default 1.0
        Speed of the generated speech. Values below 1.0 will slow down the voice (minimum 0.7).
        Values above 1.0 will speed up the voice (maximum 1.2). Default is 1.0 (no adjustment).

    Returns
    -------
    bytes | str
        * If *output_file* is *None*: the generated audio bytes.
        * Otherwise: the *output_file* path (as a string) where the audio was saved.

    Raises
    ------
    EnvironmentError
        If the ELEVENLABS_API_KEY environment variable is missing *and* the chosen voice requires it.
    RuntimeError
        If the ElevenLabs SDK call fails.
    """

    # Lazily validate the API key – public voices work without it, but we warn the user.
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if api_key is None:
        # The SDK allows unauthenticated calls for public voices, but we notify the user.
        # Use a soft warning instead of a hard failure.
        print(
            "[generate_voiceover] ELEVENLABS_API_KEY not set – proceeding unauthenticated. "
            "This only works with public voices."
        )

    # Initialise the client (key may be *None* – acceptable for public voices).
    client = ElevenLabs(api_key=api_key)

    # Prepare voice settings with speed parameter
    voice_settings = VoiceSettings(speed=speed)

    try:
        audio_generator = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            output_format=output_format,
            voice_settings=voice_settings,
        )
        # Collect all audio chunks into bytes
        audio_bytes = b"".join(audio_generator)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("ElevenLabs text-to-speech generation failed") from exc

    # If the caller wants to persist the audio, write to the specified file (or temp path).
    if output_file is not None:
        # Expand ~ and convert to Path for convenience.
        out_path = Path(output_file).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(audio_bytes)
        return str(out_path)

    # Otherwise return raw audio bytes.
    return audio_bytes


if __name__ == "__main__":
    # Quick CLI test (requires ELEVENLABS_API_KEY for private voices).
    sample_text = """
Chapter III: Attack by Stratagem

1. Sun Tzu said: In the practical art of war, the best thing of all is to take the enemy's country whole and intact; to shatter and destroy it is not so good. [whispers] To recapture an army entire is better than to destroy it.

2. Hence to fight and conquer in all your battles is not supreme excellence; supreme excellence consists in breaking the enemy's resistance without fighting.

3. Thus the highest form of generalship is to balk the enemy's plans; the next best is to prevent the junction of the enemy's forces; the next in order is to attack the enemy's army in the field; and the worst policy of all is to besiege walled cities.

4. The rule is, not to besiege walled cities if it can possibly be avoided.

5. The general, unable to control his irritation, will launch his men to the assault like swarming ants, with the result that one-third of his men are slain, while the town still remains untaken. [sighs] Such are the disastrous effects of a siege.

6. Therefore the skillful leader subdues the enemy's troops without any fighting; he captures their cities without laying siege to them; he overthrows their kingdom without lengthy operations in the field.

7. With his forces intact he will dispute the mastery of the Empire, and thus, without losing a man, his triumph will be complete. This is the method of attacking by stratagem.

[whispers] 8. It is the rule in war, if our forces are ten to the enemy's one, to surround him; if five to one, to attack him; if twice as numerous, to divide our army into two.

9. If equally matched, we can offer battle; if slightly inferior in numbers, we can avoid the enemy; if quite unequal in every way, we can flee..."""
    # Replace with a valid voice ID from your dashboard.
    default_voice = "EkK5I93UQWFDigLMpZcX" 
    saved_path = generate_voiceover(sample_text, voice_id=default_voice, output_file=f"voice_{uuid.uuid4().hex}.mp3")
