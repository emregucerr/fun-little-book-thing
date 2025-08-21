import numpy as np
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ImageClip
from moviepy import vfx
import math


class BeautifulSubtitles:
    """A class for creating professional, beautiful subtitles with various animation styles."""
    
    def __init__(self, video_size, font_size=48, font_family="Helvetica-Bold", 
                 font_color="white", stroke_color="black", stroke_width=3):
        self.video_size = video_size
        self.font_size = font_size
        self.font_family = font_family
        self.font_color = font_color
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        
        # Calculate safe margins
        self.margin_x = int(video_size[0] * 0.1)  # 10% margin on each side
        self.margin_y = int(video_size[1] * 0.1)  # 10% margin top/bottom
        self.max_width = int(video_size[0] * 0.8)  # 80% of video width
        
    def create_text_clip(self, text, duration, start_time):
        """Create a beautifully styled text clip."""
        # Create the main text
        txt_clip = TextClip(
            text=text,
            font_size=self.font_size,
            font=self.font_family,
            color=self.font_color,
            stroke_color=self.stroke_color,
            stroke_width=self.stroke_width,
            method='caption',
            size=(self.max_width, None),
            horizontal_align='center',
            vertical_align='center'
        )
        
        txt_clip = txt_clip.with_start(start_time).with_duration(duration)
        
        return txt_clip
    
    def create_background_box(self, txt_clip, padding=20, opacity=180):
        """Create a semi-transparent background box for the text."""
        # Calculate background dimensions
        bg_width = txt_clip.w + padding * 2
        bg_height = txt_clip.h + padding
        
        # Create rounded rectangle background
        bg_array = self._create_rounded_rect(bg_width, bg_height, radius=10, opacity=opacity)
        
        bg_clip = ImageClip(bg_array, duration=txt_clip.duration)
        bg_clip = bg_clip.with_start(txt_clip.start)
        
        return bg_clip
    
    def _create_rounded_rect(self, width, height, radius=10, opacity=180):
        """Create a rounded rectangle with anti-aliasing."""
        # Create array with alpha channel
        img = np.zeros((height, width, 4), dtype=np.uint8)
        
        # Fill with semi-transparent black
        img[:, :] = [0, 0, 0, opacity]
        
        # Create rounded corners by setting alpha to 0 in corner areas
        for y in range(height):
            for x in range(width):
                # Check if in corner region
                if (x < radius and y < radius):
                    # Top-left corner
                    if (x - radius)**2 + (y - radius)**2 > radius**2:
                        img[y, x, 3] = 0
                elif (x >= width - radius and y < radius):
                    # Top-right corner
                    if (x - (width - radius))**2 + (y - radius)**2 > radius**2:
                        img[y, x, 3] = 0
                elif (x < radius and y >= height - radius):
                    # Bottom-left corner
                    if (x - radius)**2 + (y - (height - radius))**2 > radius**2:
                        img[y, x, 3] = 0
                elif (x >= width - radius and y >= height - radius):
                    # Bottom-right corner
                    if (x - (width - radius))**2 + (y - (height - radius))**2 > radius**2:
                        img[y, x, 3] = 0
        
        return img
    
    def apply_fade_animation(self, clips, fade_duration=0.5):
        """Apply smooth fade in/out animation."""
        animated_clips = []
        for clip in clips:
            duration = clip.duration
            fade_in = min(fade_duration, duration * 0.3)
            fade_out = min(fade_duration, duration * 0.3)
            
            animated_clip = clip.with_effects([
                vfx.FadeIn(fade_in),
                vfx.FadeOut(fade_out)
            ])
            animated_clips.append(animated_clip)
        
        return animated_clips
    
    def apply_slide_up_animation(self, txt_clip, bg_clip, slide_duration=0.5):
        """Apply slide up animation to clips."""
        y_bottom = self.video_size[1] - self.margin_y - txt_clip.h
        y_start = self.video_size[1] + 50
        
        def slide_pos(t):
            if t < slide_duration:
                progress = t / slide_duration
                # Ease-out cubic animation
                progress = 1 - (1 - progress) ** 3
                current_y = y_start + (y_bottom - y_start) * progress
            else:
                current_y = y_bottom
            return ('center', current_y)
        
        def bg_slide_pos(t):
            pos = slide_pos(t)
            return ('center', pos[1] - 10)
        
        txt_clip = txt_clip.with_position(slide_pos)
        bg_clip = bg_clip.with_position(bg_slide_pos)
        
        # Add fade out at the end
        fade_out_duration = min(0.3, txt_clip.duration * 0.2)
        txt_clip = txt_clip.with_effects([vfx.FadeOut(fade_out_duration)])
        bg_clip = bg_clip.with_effects([vfx.FadeOut(fade_out_duration)])
        
        return txt_clip, bg_clip
    
    def apply_typewriter_animation(self, text, duration, start_time):
        """Create a typewriter effect for the text."""
        clips = []
        char_duration = duration / len(text)
        
        for i in range(1, len(text) + 1):
            partial_text = text[:i]
            
            txt_clip = TextClip(
                text=partial_text,
                font_size=self.font_size,
                font=self.font_family,
                color=self.font_color,
                stroke_color=self.stroke_color,
                stroke_width=self.stroke_width,
                method='caption',
                size=(self.max_width, None),
                horizontal_align='center',
                vertical_align='center'
            )
            
            clip_start = start_time + (i - 1) * char_duration
            clip_duration = duration - (i - 1) * char_duration
            
            txt_clip = txt_clip.with_start(clip_start).with_duration(clip_duration)
            txt_clip = txt_clip.with_position(('center', self.video_size[1] - self.margin_y - txt_clip.h))
            
            clips.append(txt_clip)
        
        return clips
    
    def apply_bounce_animation(self, txt_clip, bg_clip, bounce_duration=0.5):
        """Apply bounce animation to clips."""
        y_bottom = self.video_size[1] - self.margin_y - txt_clip.h
        y_start = self.video_size[1] - self.margin_y - txt_clip.h - 100
        
        def bounce_pos(t):
            if t < bounce_duration:
                progress = t / bounce_duration
                # Bounce easing function
                if progress < 0.5:
                    current_y = y_start + (y_bottom - y_start) * (4 * progress * progress)
                else:
                    current_y = y_bottom - 20 * math.sin((progress - 0.5) * math.pi * 2) * (1 - progress)
            else:
                current_y = y_bottom
            return ('center', current_y)
        
        def bg_bounce_pos(t):
            pos = bounce_pos(t)
            return ('center', pos[1] - 10)
        
        txt_clip = txt_clip.with_position(bounce_pos)
        bg_clip = bg_clip.with_position(bg_bounce_pos)
        
        # Add fade in/out
        fade_duration = min(0.3, txt_clip.duration * 0.2)
        txt_clip = txt_clip.with_effects([vfx.FadeIn(fade_duration), vfx.FadeOut(fade_duration)])
        bg_clip = bg_clip.with_effects([vfx.FadeIn(fade_duration), vfx.FadeOut(fade_duration)])
        
        return txt_clip, bg_clip
    
    def create_animated_subtitle(self, text, duration, start_time, animation_style='fade_in'):
        """Create a complete animated subtitle with background."""
        clips = []
        
        if animation_style == 'typewriter':
            # Special handling for typewriter effect
            txt_clips = self.apply_typewriter_animation(text, duration, start_time)
            
            # Create a single background for all typewriter clips
            bg_clip = self.create_background_box(txt_clips[-1])  # Use final text for sizing
            bg_clip = bg_clip.with_position(('center', self.video_size[1] - self.margin_y - txt_clips[-1].h - 10))
            bg_clip = bg_clip.with_effects([vfx.FadeIn(0.2), vfx.FadeOut(0.2)])
            
            clips = [bg_clip] + txt_clips
        else:
            # Create text and background
            txt_clip = self.create_text_clip(text, duration, start_time)
            bg_clip = self.create_background_box(txt_clip)
            
            # Apply animation
            if animation_style == 'fade_in':
                y_pos = self.video_size[1] - self.margin_y - txt_clip.h
                txt_clip = txt_clip.with_position(('center', y_pos))
                bg_clip = bg_clip.with_position(('center', y_pos - 10))
                clips = self.apply_fade_animation([bg_clip, txt_clip])
            elif animation_style == 'slide_up':
                txt_clip, bg_clip = self.apply_slide_up_animation(txt_clip, bg_clip)
                clips = [bg_clip, txt_clip]
            elif animation_style == 'bounce':
                txt_clip, bg_clip = self.apply_bounce_animation(txt_clip, bg_clip)
                clips = [bg_clip, txt_clip]
            else:
                # Default positioning
                y_pos = self.video_size[1] - self.margin_y - txt_clip.h
                txt_clip = txt_clip.with_position(('center', y_pos))
                bg_clip = bg_clip.with_position(('center', y_pos - 10))
                clips = [bg_clip, txt_clip]
        
        return clips


def add_beautiful_subtitles(video_path, subtitles_data, output_path, **kwargs):
    """
    Add beautiful subtitles to a video.
    
    Args:
        video_path: Path to input video
        subtitles_data: List of dicts with 'text', 'start', 'end' keys
        output_path: Path for output video
        **kwargs: Additional styling options
    
    Returns:
        Path to output video
    """
    video = VideoFileClip(video_path)
    
    # Create subtitle generator
    subtitle_gen = BeautifulSubtitles(
        video_size=video.size,
        font_size=kwargs.get('font_size', 48),
        font_family=kwargs.get('font_family', 'Helvetica-Bold'),
        font_color=kwargs.get('font_color', 'white'),
        stroke_color=kwargs.get('stroke_color', 'black'),
        stroke_width=kwargs.get('stroke_width', 3)
    )
    
    # Create all subtitle clips
    all_clips = []
    animation_style = kwargs.get('animation_style', 'fade_in')
    
    for subtitle in subtitles_data:
        duration = subtitle['end'] - subtitle['start']
        clips = subtitle_gen.create_animated_subtitle(
            text=subtitle['text'],
            duration=duration,
            start_time=subtitle['start'],
            animation_style=animation_style
        )
        all_clips.extend(clips)
    
    # Composite video with subtitles
    final_video = CompositeVideoClip([video] + all_clips)
    
    # Write output
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
    
    # Cleanup
    video.close()
    final_video.close()
    
    return output_path 