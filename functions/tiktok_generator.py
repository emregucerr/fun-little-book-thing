import globals as G
from prompts.tiktok_generator import breakdown_scene, describe_named_entity_prompt, extract_named_entity_names_system_prompt, extract_named_entity_names_user_prompt, google_image_search_query_prompt, google_image_search_query_user_prompt, system_prompt, user_prompt
from functions.scene_designer import design_scene
from utils.generate_image import generate_image, get_image_urls
from utils.generate_image_from_images import generate_image_from_images
from utils.google_images_light import search_google_images_light_urls
from utils.llm_completion import llm_completion
import re
import xml.etree.ElementTree as ET
import os
import requests
import uuid
import math
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# You'll need to install moviepy: pip install moviepy
try:
    from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, VideoClip, ImageSequenceClip, CompositeAudioClip, ColorClip, AudioArrayClip  # type: ignore[import-not-found]
    import numpy as np
except ImportError:
    print("Please install moviepy: pip install moviepy")
    exit(1)

# Import utilities for scene processing
from utils.generate_voiceover import generate_voiceover
from utils.generate_video import generate_video, generate_video_from_image
from utils.add_subtitles import auto_generate_subtitles

TIKTOK_GENERATOR_MODEL = "gpt-5"


def _dedupe_named_entities_list() -> None:
    """De-duplicate NAMED_ENTITIES_LIST in-place by character name."""
    seen_names: set[str] = set()
    deduped: List[Dict[str, Any]] = []
    for named_entity in G.NAMED_ENTITIES_LIST:
        name = named_entity.get('name')
        if not name:
            continue
        normalized_name = normalize_text_for_comparison(name)
        if normalized_name not in seen_names:
            seen_names.add(normalized_name)
            deduped.append(named_entity)
    G.NAMED_ENTITIES_LIST[:] = deduped


def normalize_text_for_comparison(text: str) -> str:
    """Normalize text by removing whitespace and punctuation for comparison."""
    # Convert to lowercase and remove all whitespace and punctuation
    normalized = re.sub(r'[^\w]', '', text.lower())
    return normalized

def ensure_named_entity_generated(named_entity_name: str, messages: List[Dict[str, str]]) -> dict:
    """Ensure a named entity entry (with image) exists."""
    # Fast path: already present (case/whitespace/punctuation-insensitive)
    canonical_name = normalize_text_for_comparison(named_entity_name)
    for existing in G.NAMED_ENTITIES_LIST:
        existing_name = existing.get("name") or ""
        if normalize_text_for_comparison(existing_name) == canonical_name:
            return existing
        
    google_image_search_query_messages = [{"role": "system", "content": google_image_search_query_prompt(named_entity_name)}, {"role": "user", "content": google_image_search_query_user_prompt(named_entity_name)}]
    google_image_search_query_response = llm_completion(TIKTOK_GENERATOR_MODEL, google_image_search_query_messages)
    google_image_search_query_match = re.search(r"<google_image_search_query>(.*?)</google_image_search_query>", google_image_search_query_response, re.DOTALL)
    google_image_search_query = google_image_search_query_match.group(1).strip() if google_image_search_query_match and google_image_search_query_match.group(1) else ""

    google_image_urls = search_google_images_light_urls(
        google_image_search_query,
        device="mobile",
        prefer_original=True,
        verify_reachable=True,
        fal_strict=True,
        max_results=20,
    )
    reference_images = google_image_urls[:3] if google_image_urls else []
    reference_images = [G.MOOD_BOARD_IMAGE] + reference_images

    describe_named_entity_messages = messages.copy()
    describe_named_entity_messages.append({
        "role": "user",
        "content": describe_named_entity_prompt(named_entity_name, reference_images)
    })
    named_entity_description = llm_completion(TIKTOK_GENERATOR_MODEL, describe_named_entity_messages)

    prompt_match = re.search(r"<named_entity_appearance_prompt>(.*?)</named_entity_appearance_prompt>", named_entity_description, re.DOTALL)
    desc_match = re.search(r"<named_entity_description>(.*?)</named_entity_description>", named_entity_description, re.DOTALL)
    prompt = prompt_match.group(1).strip() if prompt_match and prompt_match.group(1) else ""
    description = desc_match.group(1).strip() if desc_match and desc_match.group(1) else ""
    if not prompt:
        prompt = f"Portrait of {named_entity_name} from {G.BOOK_NAME}"
    if not description:
        description = f"{named_entity_name} in {G.BOOK_NAME}"

    prompt = f"{prompt}. How this look like in the real life given in the reference images. In this style: {G.STYLE}. The style must match the style board you are given as an image."

    entity_image = ""
    while google_image_urls and not entity_image:
        try:
            reference_images = google_image_urls[:3] if google_image_urls else []
            reference_images = [G.MOOD_BOARD_IMAGE] + reference_images
            entity_image_result = generate_image_from_images(prompt, reference_images)
            image_urls = get_image_urls(entity_image_result)
            entity_image = image_urls[0]
            break
        except Exception as e:
            print(f"Error generating image for {named_entity_name}: {e}")
            google_image_urls = google_image_urls[3:]

    if not entity_image:
        print(f"Falling back to simple image generation for {named_entity_name}...")
        reference_images = [G.MOOD_BOARD_IMAGE]
        entity_image_result = generate_image_from_images(prompt, reference_images)
        image_urls = get_image_urls(entity_image_result)
        entity_image = image_urls[0]

    new_named_entity = {
        "name": named_entity_name,
        "description": description,
        "prompt": prompt,
        "image": entity_image,
    }

    existing_normalized = {normalize_text_for_comparison((c.get('name') or "")) for c in G.NAMED_ENTITIES_LIST}
    if canonical_name not in existing_normalized:
        G.NAMED_ENTITIES_LIST.append(new_named_entity)
        _dedupe_named_entities_list()

    return new_named_entity

def validate_breakdown_scenes(original_voiceover: str, broken_down_scenes: List[Dict[str, str]]) -> bool:
    """Validate that the combined voiceover of broken down scenes matches the original."""
    if not broken_down_scenes:
        return False
    
    # Combine all voiceover texts from broken down scenes
    combined_voiceover = " ".join(scene['voiceover'] for scene in broken_down_scenes)
    
    # Normalize both texts for comparison
    original_normalized = normalize_text_for_comparison(original_voiceover)
    combined_normalized = normalize_text_for_comparison(combined_voiceover)
    
    return original_normalized == combined_normalized

def download_video(url: str, output_path: str) -> str:
    """Download video from URL to local file"""
    response = requests.get(url)
    response.raise_for_status()
    with open(output_path, 'wb') as f:
        f.write(response.content)
    return output_path

def combine_video_audio(video_path: str, audio_path: str, output_path: str) -> None:
    """Combine video and audio files into one output file"""
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)
    
    video_duration = video_clip.duration
    audio_duration = audio_clip.duration
    
    # If the video is longer than the audio, center the audio in the video with silence padding
    if video_duration > audio_duration:
        # Calculate the silence duration needed before and after the audio
        silence_duration = (video_duration - audio_duration) / 2
        
        # Use a simpler approach: set audio start time and let MoviePy handle the rest
        # Since we want the total duration to match video duration, we'll extend the audio
        audio_clip = audio_clip.with_start(silence_duration)
        
        # If there's still a mismatch, we need to ensure the audio fills the video duration
        # Create a silent audio track for the full video duration, then overlay our audio
        
        # Create silence for the full video duration
        sample_rate = audio_clip.fps if hasattr(audio_clip, 'fps') else 44100
        silence_samples = int(video_duration * sample_rate)
        
        # Check if the audio is mono or stereo and create appropriate silence
        try:
            # Try to get a small sample to determine audio channels
            test_sample = audio_clip.subclipped(0, min(0.1, audio_duration)).to_soundarray(fps=sample_rate)
            if len(test_sample.shape) == 1 or test_sample.shape[1] == 1:
                # Mono audio
                silence_array = np.zeros((silence_samples, 1))
            else:
                # Stereo audio
                silence_array = np.zeros((silence_samples, 2))
        except:
            # Fallback to stereo if we can't determine
            silence_array = np.zeros((silence_samples, 2))
            
        silence_track = AudioArrayClip(silence_array, fps=sample_rate)
        
        # Overlay the actual audio on the silence track
        audio_clip = CompositeAudioClip([silence_track, audio_clip]).with_duration(video_duration)
    
    # If the audio is longer than the video, slow down the video to match audio duration
    elif audio_duration > video_duration:
        # MoviePy doesn't have a built-in slowdown that works well
        # We'll use the frame extraction approach which repeats frames to extend duration
        # This creates a slow-motion effect by stretching the video timeline
        
        # Calculate how much we need to slow down
        slow_factor = audio_duration / video_duration
        
        # Extract all frames and repeat them to match the desired duration
        # This approach avoids the complex time manipulation
        fps = video_clip.fps
        total_frames = int(fps * video_duration)
        new_total_frames = int(fps * audio_duration)
        
        # Create frames list by repeating frames proportionally
        frames = []
        for i in range(new_total_frames):
            # Calculate which frame from the original video to use
            original_frame_index = int(i / slow_factor)
            if original_frame_index >= total_frames:
                original_frame_index = total_frames - 1
            
            # Get the time for this frame in the original video
            original_time = original_frame_index / fps
            frame = video_clip.get_frame(original_time)
            frames.append(frame)
        
        # Create a new video from the frames
        video_clip = ImageSequenceClip(frames, fps=fps)
    
    # Set the audio of the video clip to the generated voiceover
    final_video = video_clip.with_audio(audio_clip)
    
    # Write the final video
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
    
    # Clean up
    video_clip.close()
    audio_clip.close()
    final_video.close()

def parse_tiktok_response(response: str) -> Dict[str, Any]:
    """Parse the TikTok XML response into a dictionary structure."""
    try:
        # Find the tiktok content between tags
        tiktok_match = re.search(r'<tiktok>(.*?)</tiktok>', response, re.DOTALL)
        if not tiktok_match:
            return {"error": "No tiktok tags found in response"}
        
        tiktok_content = tiktok_match.group(1).strip()
        
        # Wrap in a root element for proper XML parsing
        xml_content = f"<root>{tiktok_content}</root>"
        
        # Parse the XML
        root = ET.fromstring(xml_content)
        
        # Convert to dictionary
        scenes = []
        for scene_elem in root.findall('scene'):
            scene = {}
            
            visual_elem = scene_elem.find('visual')
            if visual_elem is not None:
                scene['visual'] = visual_elem.text.strip() if visual_elem.text else ""
            
            voiceover_elem = scene_elem.find('voiceover')
            if voiceover_elem is not None:
                scene['voiceover'] = voiceover_elem.text.strip() if voiceover_elem.text else ""
            
            scenes.append(scene)
        
        return {
            "tiktok": {
                "scenes": scenes
            }
        }
        
    except ET.ParseError as e:
        return {"error": f"XML parsing error: {str(e)}"}
    except Exception as e:
        return {"error": f"Parsing error: {str(e)}"}

def extract_named_entity_names(visual: str, voiceover: str) -> List[str]:
    existing_named_entity_names_for_prompt = [c['name'] for c in G.NAMED_ENTITIES_LIST]
    extract_named_entity_messages = [
        {"role": "system", "content": extract_named_entity_names_system_prompt()},
        {"role": "user", "content": extract_named_entity_names_user_prompt(visual, voiceover, existing_named_entity_names_for_prompt)}
    ]
    named_entity_names_response = llm_completion(TIKTOK_GENERATOR_MODEL, extract_named_entity_messages)

    named_entity_names: List[str] = []
    for match in re.findall(r"<named_entity>\s*(.*?)\s*</named_entity>", named_entity_names_response, re.DOTALL):
        name = match.strip()
        if name:
            named_entity_names.append(name)

    # Ensure uniqueness and preserve order
    named_entity_names = list(dict.fromkeys(named_entity_names))

    return named_entity_names

# migrated: design_ai_video -> functions.scene_designer.design_scene

def process_single_scene(scene_data: Tuple[int, int, Dict[str, str], str, str, List[Dict[str, str]]], named_entities: List[dict]) -> Tuple[Optional[str], str, List[str]]:
    """Process a single scene to generate video only (no audio merge).
    
    Args:
        scene_data: Tuple containing (excerpt_index, scene_index, scene, visual_style, voice_id, messages)
    
    Returns:
        Tuple of (scene_video_path, voiceover_text, temp_files_used)
    """
    excerpt_index, scene_index, scene, visual_style, voice_id, messages = scene_data
    
    visual = scene['visual'] + " " + visual_style
    voiceover = scene['voiceover'].strip()
    
    print(f"Processing excerpt {excerpt_index + 1}, scene {scene_index + 1}")
    
    # Create temporary files
    temp_video_path = f"temp_video_{uuid.uuid4().hex}.mp4"
    temp_audio_path = f"temp_audio_{uuid.uuid4().hex}.mp3"
    temp_cropped_video_path = f"temp_cropped_video_{uuid.uuid4().hex}.mp4"
    
    temp_files = [temp_video_path, temp_audio_path, temp_cropped_video_path]
    
    try:
        # Generate voiceover temporarily just to get duration
        print(f"Generating voiceover for duration calculation for scene {scene_index + 1}...")
        generate_voiceover(voiceover, voice_id=voice_id, output_file=temp_audio_path)
        
        # Get the exact duration of the voiceover
        print(f"Getting voiceover duration for scene {scene_index + 1}...")
        audio_clip = AudioFileClip(temp_audio_path)
        exact_audio_duration = audio_clip.duration
        audio_clip.close()
        
        # Round up to the nearest integer for video generation (to ensure we have enough video content)
        video_generation_duration = math.ceil(exact_audio_duration)
        video_generation_duration = min(video_generation_duration, 12)
        video_generation_duration = max(video_generation_duration, 3)
        
        # Generate video with the rounded duration (to ensure we have enough content)
        video_url = design_scene(visual, visual_style, str(video_generation_duration), named_entities)
        
        # Download video
        print(f"Downloading video for scene {scene_index + 1}...")
        download_video(video_url, temp_video_path)
        
        # Crop the video to exactly match the audio duration
        print(f"Cropping video to exact audio duration ({exact_audio_duration:.2f}s) for scene {scene_index + 1}...")
        video_clip = VideoFileClip(temp_video_path)
        
        # Crop video to exact audio duration
        if exact_audio_duration < video_clip.duration:
            cropped_video = video_clip.subclipped(0, exact_audio_duration)
        else:
            cropped_video = video_clip
            
        cropped_video.write_videofile(temp_cropped_video_path, codec='libx264', audio_codec='aac')
        
        # Clean up original video clip
        video_clip.close()
        cropped_video.close()
        
        return temp_cropped_video_path, voiceover, temp_files
            
    except Exception as e:
        print(f"Error processing scene {scene_index + 1}: {e}")
        return None, voiceover, temp_files

def process_scenes(scenes: List[Dict[str, str]], visual_style: str, voice_id: str, excerpt_index: int, messages: List[Dict[str, str]]) -> Tuple[List[str], List[str], List[str]]:
    """Process all scenes to generate videos (no audio merge) using parallel processing."""
    scene_videos = []
    scene_voiceovers = []
    all_temp_files = []
    
    NUM_WORKERS = 10
    
    # 1) Pre-extract named entities from all scenes in parallel (before processing scenes)
    def _extract_entities(scene: Dict[str, str]) -> List[str]:
        visual_text = scene.get('visual', '')
        voiceover_text = scene.get('voiceover', '')
        return extract_named_entity_names(visual_text, voiceover_text)
    
    if scenes:
        named_entities_per_scene: List[List[dict]] = []
        for scene in scenes:
            names = _extract_entities(scene)
            scene_entities: List[dict] = []
            for name in names:
                # Eagerly ensure each named entity is generated and added to the global list
                entity = ensure_named_entity_generated(name, messages)
                scene_entities.append(entity)
            named_entities_per_scene.append(scene_entities)
    else:
        named_entities_per_scene = []
    
    # Prepare data for parallel scene processing
    scene_data_list = [
        (excerpt_index, scene_index, scene, visual_style, voice_id, messages)
        for scene_index, scene in enumerate(scenes)
    ]
    
    # 2) Process scenes in parallel with NUM_WORKERS workers
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        # Submit all scene processing tasks
        future_to_scene = {
            executor.submit(
                process_single_scene,
                scene_data,
                named_entities_per_scene[scene_index] if scene_index < len(named_entities_per_scene) else []
            ): scene_index 
            for scene_index, scene_data in enumerate(scene_data_list)
        }
        
        # Collect results as they complete
        scene_results: List[Optional[Tuple[Optional[str], str]]] = [None] * len(scenes)  # Initialize with correct size
        
        for future in as_completed(future_to_scene):
            scene_index = future_to_scene[future]
            try:
                scene_video_path, voiceover_text, temp_files = future.result()
                scene_results[scene_index] = (scene_video_path, voiceover_text)
                all_temp_files.extend(temp_files)
                
                if scene_video_path:
                    print(f"Completed scene {scene_index + 1}")
                else:
                    print(f"Failed to process scene {scene_index + 1}")
                    
            except Exception as e:
                print(f"Error processing scene {scene_index + 1}: {e}")
                scene_results[scene_index] = (None, scenes[scene_index]['voiceover'])
    
    # Extract video paths and voiceover texts, maintaining order
    for result in scene_results:
        if result and result[0] is not None:  # If we have both result and video path
            scene_videos.append(result[0])
            scene_voiceovers.append(result[1])
    
    return scene_videos, scene_voiceovers, all_temp_files

def merge_scenes_with_audio_and_subtitles(scene_videos: List[str], scene_voiceovers: List[str], 
                                       voice_id: str, output_path: Path) -> bool:
    """Merge all scene videos, add single voiceover, and add subtitles."""
    clips: List[VideoFileClip] = []  # Initialize clips list at function scope
    try:
        print(f"Merging {len(scene_videos)} scenes with audio and subtitles...")
        
        # Step 1: Load all scene video clips and merge them
        for scene_video_path in scene_videos:
            if os.path.exists(scene_video_path):
                clip = VideoFileClip(scene_video_path)
                clips.append(clip)
        
        if not clips:
            print("No valid video clips to merge")
            return False
            
        # Concatenate all video clips
        merged_video = concatenate_videoclips(clips)
        
        # Verify merged_video was created successfully
        if merged_video is None:
            print("Failed to concatenate video clips")
            # Clean up individual clips
            for clip in clips:
                clip.close()
            return False
        
        # Step 2: Generate single voiceover for all scenes
        print("Generating combined voiceover...")
        combined_voiceover_text = " ".join(scene_voiceovers)
        temp_combined_audio_path = f"temp_combined_audio_{uuid.uuid4().hex}.mp3"
        generate_voiceover(combined_voiceover_text, voice_id=voice_id, output_file=temp_combined_audio_path)
        
        # Step 3: Combine merged video with single voiceover
        print("Combining merged video with voiceover...")
        audio_clip = AudioFileClip(temp_combined_audio_path)
        
        video_duration = merged_video.duration
        audio_duration = audio_clip.duration
        
        # If the video is longer than the audio, center the audio in the video with silence padding
        if video_duration > audio_duration:
            # Calculate the silence duration needed before and after the audio
            silence_duration = (video_duration - audio_duration) / 2
            
            # Use a simpler approach: set audio start time and let MoviePy handle the rest
            # Since we want the total duration to match video duration, we'll extend the audio
            audio_clip = audio_clip.with_start(silence_duration)
            
            # If there's still a mismatch, we need to ensure the audio fills the video duration
            # Create a silent audio track for the full video duration, then overlay our audio
            
            # Create silence for the full video duration
            sample_rate = audio_clip.fps if hasattr(audio_clip, 'fps') else 44100
            silence_samples = int(video_duration * sample_rate)
            
            # Check if the audio is mono or stereo and create appropriate silence
            try:
                # Try to get a small sample to determine audio channels
                test_sample = audio_clip.subclipped(0, min(0.1, audio_duration)).to_soundarray(fps=sample_rate)
                if len(test_sample.shape) == 1 or test_sample.shape[1] == 1:
                    # Mono audio
                    silence_array = np.zeros((silence_samples, 1))
                else:
                    # Stereo audio
                    silence_array = np.zeros((silence_samples, 2))
            except:
                # Fallback to stereo if we can't determine
                silence_array = np.zeros((silence_samples, 2))
                
            silence_track = AudioArrayClip(silence_array, fps=sample_rate)
            
            # Overlay the actual audio on the silence track
            audio_clip = CompositeAudioClip([silence_track, audio_clip]).with_duration(video_duration)
        
        # If the audio is longer than the video, slow down the video to match audio duration
        elif audio_duration > video_duration:
            # MoviePy doesn't have a built-in slowdown that works well
            # We'll use the frame extraction approach which repeats frames to extend duration
            # This creates a slow-motion effect by stretching the video timeline
            
            # Calculate how much we need to slow down
            slow_factor = audio_duration / video_duration
            
            # Extract all frames and repeat them to match the desired duration
            # This approach avoids the complex time manipulation
            fps = merged_video.fps
            total_frames = int(fps * video_duration)
            new_total_frames = int(fps * audio_duration)
            
            # Create frames list by repeating frames proportionally
            frames = []
            for i in range(new_total_frames):
                # Calculate which frame from the original video to use
                original_frame_index = int(i / slow_factor)
                if original_frame_index >= total_frames:
                    original_frame_index = total_frames - 1
                
                # Get the time for this frame in the original video
                original_time = original_frame_index / fps
                frame = merged_video.get_frame(original_time)
                frames.append(frame)
            
            # Create a new video from the frames
            merged_video = ImageSequenceClip(frames, fps=fps)
        
        # Set the audio of the video clip to the generated voiceover
        final_video_with_audio = merged_video.with_audio(audio_clip)
        
        # Step 4: Save the video with audio (temporary file for subtitles)
        temp_video_with_audio_path = f"temp_video_with_audio_{uuid.uuid4().hex}.mp4"
        final_video_with_audio.write_videofile(temp_video_with_audio_path, codec='libx264', audio_codec='aac')
        
        # Clean up clips
        merged_video.close()
        audio_clip.close()
        final_video_with_audio.close()
        
        # Clean up individual clips
        for clip in clips:
            clip.close()
        
        # Step 5: Add subtitles using ZapCap
        print("Adding subtitles to final video...")
        subtitled_video_path = auto_generate_subtitles(
            video_path=temp_video_with_audio_path,
            output_path=str(output_path)
        )
        
        # Clean up temporary files
        # if os.path.exists(temp_combined_audio_path):
        #     os.remove(temp_combined_audio_path)
        # if os.path.exists(temp_video_with_audio_path):
        #     os.remove(temp_video_with_audio_path)
        
        if subtitled_video_path:
            print(f"Final video with subtitles saved to: {output_path}")
            return True
        else:
            print("Failed to add subtitles")
            return False
        
    except Exception as e:
        print(f"Error merging scenes with audio and subtitles: {e}")
        # Clean up individual clips if they exist
        try:
            for clip in clips:
                clip.close()
        except:
            pass
        return False

def merge_scenes(scene_videos: List[str], output_path: Path) -> bool:
    """Merge all scene videos into a single video (simple version without audio/subtitles)."""
    clips: List[VideoFileClip] = []  # Initialize clips list at function scope
    try:
        print(f"Merging {len(scene_videos)} scenes...")
        
        # Load all scene video clips
        for scene_video_path in scene_videos:
            if os.path.exists(scene_video_path):
                clip = VideoFileClip(scene_video_path)
                clips.append(clip)
        
        if clips:
            # Concatenate all clips
            final_video = concatenate_videoclips(clips)
            
            # Verify final_video was created successfully
            if final_video is None:
                print("Failed to concatenate video clips")
                # Clean up individual clips
                for clip in clips:
                    clip.close()
                return False
            
            # Save the merged video
            final_video.write_videofile(str(output_path), codec='libx264', audio_codec='aac')
            
            print(f"Saved merged video to: {output_path}")
            
            # Clean up clips
            final_video.close()
            for clip in clips:
                clip.close()
            
            return True
        
    except Exception as e:
        print(f"Error merging scenes: {e}")
        # Clean up individual clips if they exist
        try:
            for clip in clips:
                clip.close()
        except:
            pass
        return False
    
    return False

def cleanup_temp_files(temp_files: List[str]) -> None:
    """Clean up all temporary files."""
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def split_scenes_into_equal_parts(scenes: List[Dict[str, str]], max_scenes_per_part: int = 20) -> List[List[Dict[str, str]]]:
    """Split scenes into equal parts if there are more than max_scenes_per_part scenes."""
    if len(scenes) <= max_scenes_per_part:
        return [scenes]
    
    # Calculate the optimal number of parts
    num_scenes = len(scenes)
    num_parts = math.ceil(num_scenes / max_scenes_per_part)
    
    # Calculate scenes per part to make them as equal as possible
    scenes_per_part = num_scenes // num_parts
    extra_scenes = num_scenes % num_parts
    
    # Split the scenes
    parts = []
    start_idx = 0
    
    for i in range(num_parts):
        # Add one extra scene to the first 'extra_scenes' parts
        current_part_size = scenes_per_part + (1 if i < extra_scenes else 0)
        end_idx = start_idx + current_part_size
        
        parts.append(scenes[start_idx:end_idx])
        start_idx = end_idx
    
    return parts

def tiktok_generator(script: str, past_tiktoks: List[str] = [], 
                    visual_style: str = "", voice_id: str = "JBFqnCBsd6RMkjVDRZzb", 
                    excerpt_index: int = 0, output_dir: Optional[Path] = None, 
                    process_videos: bool = True) -> Tuple[Dict[str, Any], str, List[str]]:
    """Generate TikTok scenes and optionally process them into final video(s).
    
    If there are more than 20 scenes, they will be split into equal parts,
    with each part becoming a separate video file.
    
    Returns:
        Tuple containing:
        - parsed_response: Dictionary with scene data
        - raw_tiktok: Raw XML response from LLM
        - video_output_paths: List of paths to generated video files
    """
    system_prompt_text = system_prompt(past_tiktoks)
    user_prompt_text = user_prompt(script)

    messages = [
        {"role": "system", "content": system_prompt_text},
        {"role": "user", "content": user_prompt_text}
    ]

    response = llm_completion(TIKTOK_GENERATOR_MODEL, messages)

    while '<tiktok>' not in response:
        temp_messages = messages.copy()
        temp_messages.append({"role": "user", "content": "Your response is not valid. It does not contain the <tiktok> tags. Please try again with a valid <tiktok> object."})
        response = llm_completion(TIKTOK_GENERATOR_MODEL, temp_messages)

    print("Tiktok response: ", response)

    messages.append({"role": "assistant", "content": response})

    raw_tiktok = response

    # Parse the initial response into a dictionary
    parsed_response = parse_tiktok_response(response)
    
    # # If parsing was successful, break down long scenes
    # if "tiktok" in parsed_response and "scenes" in parsed_response["tiktok"]:
    #     initial_scenes = parsed_response["tiktok"]["scenes"]
    #     updated_scenes = breakdown_long_scenes(initial_scenes, messages)
        
    #     # Update the parsed response with the broken down scenes
    #     parsed_response["tiktok"]["scenes"] = updated_scenes
    
    # If video processing is requested and we have valid scenes
    video_output_paths = []
    if process_videos and "tiktok" in parsed_response and "scenes" in parsed_response["tiktok"] and output_dir:
        scenes = parsed_response["tiktok"]["scenes"]
        
        # Split scenes into equal parts if there are more than 20 scenes
        scene_parts = split_scenes_into_equal_parts(scenes, max_scenes_per_part=20)
        
        print(f"Split {len(scenes)} scenes into {len(scene_parts)} parts")
        for i, part_scenes in enumerate(scene_parts):
            print(f"Part {i+1}: {len(part_scenes)} scenes")
        
        all_temp_files = []
        
        # Process each part separately
        for part_index, part_scenes in enumerate(scene_parts):
            # Use a combination of excerpt_index and part_index for unique naming
            current_excerpt_index = excerpt_index * 1000 + part_index if len(scene_parts) > 1 else excerpt_index
            
            # Process scenes to generate videos for this part
            scene_videos, scene_voiceovers, temp_files = process_scenes(part_scenes, visual_style, voice_id, current_excerpt_index, messages)
            all_temp_files.extend(temp_files)
            
            # Merge all scenes for this part
            if scene_videos:
                if len(scene_parts) > 1:
                    if part_index == 0:
                        final_output_path = output_dir / f"{excerpt_index}.mp4"
                    else:
                        final_output_path = output_dir / f"{excerpt_index}_part{part_index + 1}.mp4"
                else:
                    final_output_path = output_dir / f"{excerpt_index}.mp4"
                    
                if merge_scenes_with_audio_and_subtitles(scene_videos, scene_voiceovers, voice_id, final_output_path):
                    video_output_paths.append(str(final_output_path))
                    print(f"Completed excerpt {excerpt_index + 1} of {len(scene_parts)} parts, part {part_index + 1} of {len(scene_parts)} parts")
                else:
                    print(f"Failed to merge scenes for excerpt {excerpt_index + 1} of {len(scene_parts)} parts, part {part_index + 1} of {len(scene_parts)} parts")
            else:
                print(f"No scene videos generated for excerpt {excerpt_index + 1} of {len(scene_parts)} parts, part {part_index + 1} of {len(scene_parts)} parts")
        
        # Clean up all temporary files
        cleanup_temp_files(all_temp_files)
    
    return parsed_response, raw_tiktok, video_output_paths

