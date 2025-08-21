import os
import time
import requests
from typing import Optional, Dict, Any
import json

class ZapCapClient:
    """Client for interacting with ZapCap API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.zapcap.ai"
        self.headers = {
            "x-api-key": api_key
        }
    
    def upload_video(self, video_path: str) -> Optional[str]:
        """Upload video to ZapCap and return video ID"""
        print(f"🔄 Uploading video to ZapCap: {video_path}")
        
        with open(video_path, 'rb') as video_file:
            files = {'file': video_file}
            response = requests.post(
                f"{self.base_url}/videos",
                headers=self.headers,
                files=files
            )
        
        if response.status_code in [200, 201]:  # 200 OK or 201 Created
            video_data = response.json()
            video_id = video_data.get('id')
            print(f"✅ Video uploaded successfully. Video ID: {video_id}")
            return video_id
        else:
            print(f"❌ Failed to upload video: {response.status_code} - {response.text}")
            return None
    
    def create_task(self, video_id: str, template_id: Optional[str] = None, 
                   render_options: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Create a subtitle generation task"""
        print(f"🎬 Creating subtitle task for video: {video_id}")
        
        task_data = {
            "autoApprove": True
        }
        
        # Use default template if none provided - "Luke" template (basic, highlighted)
        if template_id is None:
            template_id = "eb5de878-2997-41fe-858a-726e9e3712df"  # Luke template
        
        task_data["templateId"] = template_id
        
        if render_options:
            task_data["renderOptions"] = render_options
        
        response = requests.post(
            f"{self.base_url}/videos/{video_id}/task",
            headers={**self.headers, "Content-Type": "application/json"},
            json=task_data
        )
        
        if response.status_code in [200, 201]:  # 200 OK or 201 Created
            task_data = response.json()
            task_id = task_data.get('taskId')  # API uses 'taskId' not 'id'
            print(f"✅ Task created successfully. Task ID: {task_id}")
            return task_id
        else:
            print(f"❌ Failed to create task: {response.status_code} - {response.text}")
            return None
    
    def get_task_status(self, video_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task"""
        response = requests.get(
            f"{self.base_url}/videos/{video_id}/task/{task_id}",
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get task status: {response.status_code} - {response.text}")
            return None
    
    def wait_for_completion(self, video_id: str, task_id: str, max_wait_time: int = 600) -> Optional[str]:
        """Wait for task completion and return download URL"""
        print("⏳ Waiting for subtitle generation to complete...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            task_status = self.get_task_status(video_id, task_id)
            
            if not task_status:
                return None
            
            status = task_status.get('status')
            print(f"📊 Task status: {status}")
            
            if status == 'completed':
                download_url = task_status.get('downloadUrl')
                if download_url:
                    print("✅ Subtitle generation completed!")
                    return download_url
                else:
                    print("❌ Task completed but no download URL found")
                    return None
            elif status == 'failed':
                error_message = task_status.get('error', 'Unknown error')
                print(f"❌ Task failed: {error_message}")
                return None
            
            # Wait before checking again
            time.sleep(10)
        
        print("⚠️ Task did not complete within the maximum wait time")
        return None
    
    def download_video(self, download_url: str, output_path: str) -> bool:
        """Download the processed video from ZapCap"""
        print(f"⬇️ Downloading processed video to: {output_path}")
        
        response = requests.get(download_url, stream=True)
        
        if response.status_code == 200:  # Download should be 200 OK
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Video downloaded successfully: {output_path}")
            return True
        else:
            print(f"❌ Failed to download video: {response.status_code}")
            return False


def auto_generate_subtitles(video_path: str, output_path: str, font_size: int = 28, 
                           font_family: Optional[str] = None, words_per_chunk: int = 3,
                           animation_style: str = 'fade_in', font_color: str = 'white',
                           shadow_color: str = 'black', shadow_offset: tuple = (2, 2),
                           template_id: Optional[str] = None) -> Optional[str]:
    """
    Auto-generate subtitles using ZapCap API.
    
    Args:
        video_path (str): Path to the input video file
        output_path (str): Path where the output video with subtitles should be saved
        font_size (int): Font size for subtitles (default: 28)
        font_family (str): Font family to use (default: None)
        words_per_chunk (int): Number of words to display per subtitle chunk (default: 3)
        animation_style (str): Animation style ('fade_in', 'slide_up', 'bounce', 'typewriter')
        font_color (str): Font color (default: 'white')
        shadow_color (str): Shadow/stroke color (default: 'black')
        shadow_offset (tuple): Shadow offset (default: (2, 2))
        template_id (str): ZapCap template ID to use (default: None - uses default template)
    
    Returns:
        str: Path to the output video file, or None if failed
    """
    print("🎬 Starting ZapCap subtitle generation...")
    
    # Get API key from environment
    api_key = os.getenv('ZAPCAP_API_KEY')
    if not api_key:
        print("❌ ZAPCAP_API_KEY not found in environment variables")
        return None
    
    # Initialize ZapCap client
    client = ZapCapClient(api_key)
    
    # Create render options based on parameters
    render_options = {
        "subsOptions": {
            "emoji": False,
            "animation": True,
            "emphasizeKeywords": True,
            "displayWords": 4,  # Show fewer words at once to reduce visual impact
            "punctuation": True
        },
        "styleOptions": {
            "fontSize": font_size,  # Use the provided font_size parameter
            "fontWeight": 500,  # Reduce font weight to make text less bold
            "fontUppercase": False,  # Don't force uppercase
            "fontShadow": "m",  # Medium shadow for readability
            "stroke": "s",  # Small stroke
            "top": 15,
            "strokeColor": "#000000"
        }
    }
    
    # Add font family if specified
    if font_family:
        render_options["styleOptions"]["fontFamily"] = font_family
    
    # Set font color (convert color names to hex if needed)
    color_map = {
        'white': '#FFFFFF',
        'black': '#000000',
        'red': '#FF0000',
        'blue': '#0000FF',
        'green': '#00FF00',
        'yellow': '#FFFF00'
    }
    hex_color = color_map.get(font_color.lower(), font_color)
    if hex_color.startswith('#'):
        render_options["styleOptions"]["fontColor"] = hex_color
    else:
        render_options["styleOptions"]["fontColor"] = "#FFFFFF"  # Default to white
    
    try:
        # Step 1: Upload video
        video_id = client.upload_video(video_path)
        if not video_id:
            return None
        
        # Step 2: Create task
        task_id = client.create_task(video_id, template_id, render_options)
        if not task_id:
            return None
        
        # Step 3: Wait for completion
        download_url = client.wait_for_completion(video_id, task_id)
        if not download_url:
            return None
        
        # Step 4: Download processed video
        if client.download_video(download_url, output_path):
            print(f"✅ Subtitled video saved to: {output_path}")
            return output_path
        else:
            return None
            
    except Exception as e:
        print(f"❌ Error during subtitle generation: {e}")
        return None


def add_subtitles_to_video(video_path: str, script_text: str, output_path: str, 
                          font_size: int = 28, font_family: Optional[str] = None,
                          template_id: Optional[str] = None) -> Optional[str]:
    """
    Add subtitles to a video using ZapCap API.
    Note: ZapCap automatically transcribes audio, so script_text parameter is not used
    but kept for compatibility with existing code.
    
    Args:
        video_path (str): Path to the input video file
        script_text (str): Script text (not used with ZapCap - auto-transcribed)
        output_path (str): Path where the output video with subtitles should be saved
        font_size (int): Font size for subtitles (default: 28)
        font_family (str): Font family to use (default: None)
        template_id (str): ZapCap template ID to use (default: None)
    
    Returns:
        str: Path to the output video file, or None if failed
    """
    print("📝 Note: ZapCap automatically transcribes audio. Provided script_text will be ignored.")
    
    return auto_generate_subtitles(
        video_path=video_path,
        output_path=output_path,
        font_size=font_size,
        font_family=font_family,
        template_id=template_id
    )


def get_available_templates() -> Optional[Dict[str, Any]]:
    """
    Get available ZapCap templates.
    
    Returns:
        dict: Available templates or None if failed
    """
    api_key = os.getenv('ZAPCAP_API_KEY')
    if not api_key:
        print("❌ ZAPCAP_API_KEY not found in environment variables")
        return None
    
    headers = {"x-api-key": api_key}
    
    try:
        response = requests.get(
            "https://api.zapcap.ai/templates",
            headers=headers
        )
        
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ Retrieved {len(templates)} available templates")
            return templates
        else:
            print(f"❌ Failed to get templates: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting templates: {e}")
        return None


# Legacy function names for backward compatibility
def speech_to_text(audio_path: str) -> Optional[str]:
    """
    Legacy function - ZapCap handles transcription automatically.
    This function is kept for backward compatibility.
    """
    print("⚠️ speech_to_text is deprecated when using ZapCap. Use auto_generate_subtitles instead.")
    return None


def create_animated_subtitles(*args, **kwargs):
    """
    Legacy function - ZapCap handles subtitle creation automatically.
    This function is kept for backward compatibility.
    """
    print("⚠️ create_animated_subtitles is deprecated when using ZapCap. Use auto_generate_subtitles instead.")
    return []


# For backwards compatibility
HAS_BEAUTIFUL_SUBTITLES = True  # ZapCap provides beautiful subtitles by default

if __name__ == "__main__":
    video_path = "to_do_subtitle.mp4"
    output_path = "ArtOfWar/7.mp4"
    auto_generate_subtitles(video_path, output_path)