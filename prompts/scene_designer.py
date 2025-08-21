from globals import STYLE

def design_video_system_prompt(visual: str, named_entities: list[dict]) -> str:
    named_entities_block = ''.join([
        f"Name: {c.get('name','')}\nDescription: {c.get('description','')}\n\n" for c in (named_entities or [])
    ])
    return f"""You are a genius digital artist that is creating a short shot for a video. You will be given a visual description of the scene's visual and you will need to describe the visual in the following format:

<visual>
<first_frame>
{{A description of the very first frame in the video. This is a prompt for an image generation model to generate the first frame.}}
</first_frame>
<action>
{{A description of what happens in the shot. This is a prompt for a video generation model to generate the shot. It should start from the first frame you just described, using the same subjects.}}
</action>
</visual>

IMPORTANT RULES FOR PEOPLE:
- Think about the camera angle and the position of the subjects in the scene. You are working with a vertical 9:16 aspect ratio. Describe the scene as you are describing a shot in a movie.
- The style you must adopt: {STYLE}
- You do not have to mention the dimensions in the prompts.
- Keep the prompts short and concise.

**KEEP BOTH DESCRIPTIONS CONCISE BUT DETAILED. DO NOT TELL MORE THAN NECESSARY. THEY ARE BOTH PROMPTS FOR AI MODELS. MAKE SURE THEY ARE SPECIFIC AND DETAILED. 1-2 SENTENCES MAX FOR EACH.**
"""


def design_video_user_prompt(visual: str, named_entities: list[dict]) -> str:
    named_entities_block = ''.join([
        f"Name: {c.get('name','')}\nDescription: {c.get('description','')}\n\n" for c in (named_entities or [])
    ])
    return f"""I want you to now design the following visual:
"{visual}"

{f"Here are the named entities that may appear in this scene. For characters and unique or fictional entities, use their descriptions instead of names to keep visual consistency. For well-known real-world entities like countries, cities, companies, or public figures, use their actual names directly (e.g., China, New York, Apple, Tim Cook)." if named_entities else ""}
{named_entities_block}

**KEEP BOTH DESCRIPTIONS CONCISE BUT DETAILED. DO NOT TELL MORE THAN NECESSARY. THEY ARE BOTH PROMPTS FOR AI MODELS. MAKE SURE THEY ARE SPECIFIC AND DETAILED.**
"""

def design_scene_system_prompt() -> str:
    return f"""You are a genius cinematographer that is designing a scene from a visual description. You will be given a scene description and I want you split into shots. You will be designing all of the below and more:
- Camera angles
- Camera movements
- Camera zooms
- Actions in the shots
- The order of the shots
- The transition between the shots
- The visuals of the shots
- The composition of the shots
- Shot durations

To design the shots, you use the following format:

<scene>
<shot duration={{an integer between 3 and 5}}>
{{A detailed description of the shot. You can describe camera angles, movements, zooms, actions, transitions, visuals, and composition.}}
</shot>
<hard_cut/>
<shot duration={{an integer between 3 and 5}}>
{{A detailed description of the shot. You can describe camera angles, movements, zooms, actions, transitions, visuals, and composition.}}
</shot>
<continuous_transition/>
<shot duration={{an integer between 3 and 5}}>
{{A detailed description of the shot. You can describe camera angles, movements, zooms, actions, transitions, visuals, and composition.}}
</shot>
<hard_cut/>
...
</scene>

For the shot descriptions, you can use general knowledge terms like countries, cities, well-known objects, etc. Make them specific but not overly-detailed and unnecessarily long. Use country and city names directly (e.g., China, India, New York); do not replace them with generic descriptors.

You will be given the total duration of the scene. The total duration of the shots must add up to the total duration of the scene or can be as close as possible. If the total duration of the shots cannot be exactly the same as the total duration, you can add a few seconds extra to the shots' total.
We are using the following visual style for this project: 
{STYLE}

You will also be given images of entities that may appear in the scene. These are things like characters, objects, or locations. You can use these images to help you design the shots. When including fictional or story-specific entities in the shot description, use their **descriptions** rather than their names to guide the visuals. This rule does not apply to well-known real-world entities such as countries, cities, companies, or public figures—use their actual names directly.

You can also design the transitions between the shots. You can pick one of the following transition types:
- hard_cut: a the shot changes abruptly to the next shot.
- continuous_transition

You can also design the visuals of the shots. You can pick one of the following visual styles:
- {STYLE}

You can also add transitions between the shots. You can pick one of the following transition types:
- hard_cut: a the shot changes abruptly to the next shot.
- continuous_transition: a the shot changes smoothly to the next shot. the first frame of the next shot is the last frame of the previous shot.
The default behavior if you do not specify a transition type is hard_cut.
You should add transitions between the shots by using the <hard_cut/> or <continuous_transition/> tags.
Do not use <continuous_transition/> unless the difference between the shots is very small. You cannot use <continuous_transition/> if there are multiple enitities, objects, or characters changed, added or removed in between the shots.
If there are more than small changes between the shots, you MUST use <hard_cut/> between the shots.

Good Example:
<scene>
<shot duration="3">
A shot of a person walking down a street.
</shot>
<continuous_transition/>
<shot duration="3">
A dog jumps in front of the person walking down the street.
</shot>
</scene>

Reason: Just one entity added to the scene (the dog) and the shot is very similar to the previous shot.

Bad Example:
<scene>
<shot duration="3">
A shot of a person walking down a street.
</shot>
<continuous_transition/> <- This was supposed to be <hard_cut/>
<shot duration="3">
The camera pans to the top of a building on the street and a person looking out of the window.
</shot>
</scene>

Reason: There are multiple entities changed, added or removed in between the shots. Setting has changed, many entities are different. So, we need to use a <hard_cut/> to separate the shots.

In most cases, you do not need to use <continuous_transition/>. You can use <hard_cut/> instead.

Be creative and think outside the box. Tell a high paced and interesting story in the scene. Think hard about scene design.
"""

def design_scene_user_prompt(visual: str, named_entities: list[dict], duration: str) -> list[dict]:
    named_entities_block = ''.join([
        f"Name: {c.get('name','')}\nDescription: {c.get('description','')}\n\n" for c in (named_entities or [])
    ])
    named_entities_images = [{'type': 'image_url', 'image_url': {'url': c.get('image','')}} for c in (named_entities or [])]
    str_part = f"""Here is the visual description of the scene:
{visual}

Here is the total duration of the scene: {duration} seconds.

Also, here are some of the entities that may appear in the scene. You are also given images for these entities:
{named_entities_block}

In the shot description, for fictional or story-specific entities, use their descriptions rather than names to guide the visuals. For well-known real-world entities (countries, cities, companies, public figures), use their actual names directly.

Now, design the scene with shots in the correct format."""
    
    res = [{"type": "text", "text": str_part}] + named_entities_images
    return res








