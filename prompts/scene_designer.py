from globals import STYLE

def design_video_system_prompt() -> str:
    return f"""You are a genius digital artist creating short, clear shots for a scene. Your outputs must be specific and cinematography-aware. Always specify camera framing/angle, composition and subject placement, lighting and mood, color palette, texture/material cues, and a simple action per shot. You will be given a visual description of the scene's visual and you will need to describe the visual in the following format to generate the shots one by one:

<visual>
<first_frame>
{{An image prompt for an image generation model to generate the first frame. Include: camera framing/angle, subject placement/composition, lighting and mood, color palette, and key textural/material cues. 1–2 sentences, concrete and specific.}}
</first_frame>
<last_frame>
{{An image prompt for an image generation model to generate the last frame. Include: camera framing/angle, subject placement/composition, lighting and mood, color palette, and key textural/material cues. 1–2 sentences, concrete and specific.}}
</last_frame>
<action>
{{A concise description (1 sentence) of how the first frame changes to the last frame. Specify the single motion, camera move if any, and the transition type. Avoid multiple simultaneous actions.}}
</action>
</visual>

Sometimes you will already be given the first frame of the shot that is the last frame of the previous shot. In that case, I want you to design the last frame of the shot and the action/animation that happens in the shot after the first frame. In the following format:

<visual>
<action>
{{A concise description (1 sentence) of how the first frame changes to the last frame. Specify the single motion, camera move if any, and the transition type. Avoid multiple simultaneous actions.}}
</action>
<last_frame>
{{An image prompt for an image generation model to generate the last frame.}}
</last_frame>
</visual>

IMPORTANT RULES:
- Think about the camera angle and the position of the subjects in the scene. You are working with a vertical 9:16 aspect ratio. Describe the scene as you are describing a shot in a movie.
- You do not have to mention the dimensions in the prompts.
- Keep the prompts short and concise (1–2 sentences per frame), but extremely specific.
- The frame prompts must name the camera framing/angle, subject placement, lighting quality/direction, and palette. Do not leave room for interpretation.
- Make sure there are distinct differences between the first frame and the last frame.
- Be very explicit in your visual descriptions. Do not leave any room for interpretation.
- Make sure to explicitly describe the action that happens in the shot and add a clear difference between the first frame and the last frame wth the action happening in between.

**KEEP BOTH DESCRIPTIONS CONCISE BUT DETAILED (1–2 sentences each). NAME CAMERA, COMPOSITION, LIGHTING, AND COLOR. ONE PRIMARY SUBJECT AND ONE SIMPLE ACTION.**
"""


def design_video_user_prompt(visual: str, named_entities: list[dict]) -> str:
    named_entities_block = ''.join([
        f"Name: {c.get('name','')}\nDescription: {c.get('description','')}\n\n" for c in (named_entities or [])
    ])
    return f"""I want you to now design the following visual:
"{visual}"

{f"Here are the named entities that may appear in this scene. For characters and unique or fictional entities, use their descriptions instead of names to keep visual consistency. For well-known real-world entities like countries, cities, companies, or public figures, use their actual names directly (e.g., China, New York, Apple, Tim Cook)." if named_entities else ""}
{named_entities_block}

**KEEP ALL THREE DESCRIPTIONS CONCISE BUT DETAILED. DO NOT TELL MORE THAN NECESSARY. THEY ARE BOTH PROMPTS FOR AI MODELS. MAKE SURE THEY ARE SPECIFIC AND DETAILED.**
This is a hard cut scene and therefore you must provide all three of the first frame, the action, and the last frame.
"""


def design_continuous_video_user_prompt(visual: str, named_entities: list[dict], first_frame_url: str) -> list[dict]:
    named_entities_block = ''.join([
        f"Name: {c.get('name','')}\nDescription: {c.get('description','')}\n\n" for c in (named_entities or [])
    ])
    str_part = f"""I want you to now design the following visual:
"{visual}"

{f"Here are the named entities that may appear in this scene. For characters and unique or fictional entities, use their descriptions instead of names to keep visual consistency. For well-known real-world entities like countries, cities, companies, or public figures, use their actual names directly (e.g., China, New York, Apple, Tim Cook)." if named_entities else ""}
{named_entities_block}

This is a continuation of the previous shot. You are given the first frame of the shot as an image. You must design the last frame of the shot and the action/animation that happens in the shot after the first frame.

**KEEP BOTH DESCRIPTIONS CONCISE BUT DETAILED. DO NOT TELL MORE THAN NECESSARY. THEY ARE BOTH PROMPTS FOR AI MODELS. MAKE SURE THEY ARE SPECIFIC AND DETAILED.**
This is a continuation of the previous shot and therefore you must only provide the action and the last frame.
"""
    res = [{"type": "text", "text": str_part}] + [{"type": "image_url", "image_url": {"url": first_frame_url}}]
    return res

def design_scene_system_prompt() -> str:
    return f"""You are a genius cinematographer that is designing a scene from a visual description. You will be given a scene description and I want you split into shots. Keep the shots simple and focus on a single thing do not try to mash too many things into one shot:

To design the shots, you use the following format:

<scene>
<shot duration={{an integer between 3 and 8}}>
{{A detailed description of the shot. Focus on a single thing. Do not try to mash too many things into one shot.}}
</shot>
<hard_cut/>
<shot duration={{an integer between 3 and 8}}>
{{A detailed description of the shot. Focus on a single thing. Do not try to mash too many things into one shot.}}
</shot>
<continuous_transition/>
<shot duration={{an integer between 3 and 8}}>
{{A detailed description of the shot. Focus on a single thing. Do not try to mash too many things into one shot.}}
</shot>
<hard_cut/>
...
</scene>

For the shot descriptions, you can use general knowledge terms like countries, cities, well-known objects, etc. Make them specific but not overly-detailed and unnecessarily long. Use country and city names directly (e.g., China, India, New York); do not replace them with generic descriptors.

You will be given the total duration of the scene. The total duration of the shots must add up to the total duration of the scene or can be as close as possible. If the total duration of the shots cannot be exactly the same as the total duration, you can add a few seconds extra to the shots' total.
We are using the following visual style for this project: 
{STYLE}

You will also be given images of entities that may appear in the scene. These are things like characters, objects, or locations. You can use these images to help you design the shots. When including fictional or story-specific entities in the shot description, use their **descriptions** rather than their names to guide the visuals. This rule does not apply to well-known real-world entities such as countries, cities, companies, or public figures—use their actual names directly.

You can also add transitions between the shots. You can pick one of the following transition types:
- hard_cut: a the shot changes abruptly to the next shot.
- continuous_transition: a the shot changes smoothly to the next shot. the first frame of the next shot is the last frame of the previous shot.
The default behavior if you do not specify a transition type is hard_cut.

Be creative and think outside the box. Tell a high paced and interesting story in the scene. Think hard about scene design.
Do not clutter the shots with too many entities. Keep the shots simple and focused on a single thing.
Try not to have too many 3 second shots in a scene. If all the shots are very short, the video will be difficult to watch and chaotic.
Each scene usually has 1-3 shots. Do not deviate from the visual you are asked to design.
Be very explicit in your visual descriptions. Do not leave any room for interpretation. Describe the shot in detail.
If the total duration of the scene is less than 8 seconds, you do not have to use multiple shots.
Each shot must serve a purpose and be meaningful. Do not add shots that are not necessary.
Do NOT mention anything about the duration of the shots in the shot descriptions.

Here is a guide on writing good image generation prompts:
# Prompting Fundamentals - First Frame

<Note>
  This guide covers hosted FLUX models, but most concepts apply to all FLUX models. After reading about those fundamentals, explore [practical enhancement techniques](/guides/prompting_guide_t2i_essentials).
</Note>

## What is prompting?

Prompting is how you tell the model what to render. Clear prompts make better images. Below: the same idea with a short prompt vs. a detailed one.

## Basic Prompt Structure

Use this framework for reliable results:

> **Subject + Action + Style + Context**

**Framework Structure:**

* **Subject**: The main focus (person, object, character)
* **Action**: What the subject is doing or their pose
* **Style**: Artistic approach, medium, or aesthetic
* **Context**: Setting, lighting, time, mood, or atmospheric conditions

  - **Subject**: Red fox
  - **Action**: sitting in tall grass
  - **Style**: wildlife documentary photography
  - **Context**: misty dawn

  **Result**: *"Red fox sitting in tall grass, wildlife documentary photography, misty dawn"*

  * **Subject**: Human explorer
  * **Action**: walking through cyberpunk forest
  * **Style**: sci-fi fantasy art style
  * **Context**: dramatic atmospheric lighting

  **Result**: *"Human explorer in futuristic gear walking through cyberpunk forest, dramatic atmospheric lighting, sci-fi fantasy art style, cinematic composition"*

## Structured descriptions beat keyword lists

Image generation responds best to **structured descriptions** that mix natural relationships with direct specifications.

* **Disconnected keywords (weak)**: "Woman, red dress, beach, sunset, happy, smiling, waves, golden light"
* **Overwritten prose (bloated)**: "A joyful woman ... warm sunset light illuminating her smile"
* **Structured (best)**: "A joyful woman in a flowing red dress walks along a sandy beach, golden hour, gentle waves, warm lighting"

Why it works:

* Natural language handles relationships and spatial cues
* Short, direct specs cover lighting, time, atmosphere
* Fewer filler words; clearer intent

## Word order importance

Image generation pays more attention to words and concepts mentioned **earlier** in your prompt. Structure your prompts strategically by front-loading the most important elements.

1. **Lead with the subject**: Put the main thing first.
2. **Then the action**: Describe what it’s doing.
3. **Add style**: Artistic approach or medium.
4. **Add context**: Setting and lighting that shape everything.
5. **Finish with details**: Secondary and atmospheric elements.

### Poor word order

> "In a mystical forest with ancient trees and glowing mushrooms, featuring dramatic lighting and a fantasy art style, there stands a powerful wizard casting a spell with magical energy swirling around him"

**Problems:**

* Context details come first
* Main subject (wizard) is buried at the end
* Key action (casting spell) gets less attention

### Front-loaded word order

> "A powerful wizard casting a spell with magical energy swirling around him, fantasy art style with dramatic lighting, standing in a mystical forest with ancient trees and glowing mushrooms"

**Advantages:**

* Wizard (main subject) is front and center
* Spell casting (key action) gets priority
* Style and environment support the main elements

### Front-loading Examples

**Character-focused scenes**\
Start with character description and primary action, follow with style and environmental context.

> *Example*: "A confident astronaut floating in zero gravity, reaching toward a distant star, cinematic sci-fi style, in the vastness of space with Earth visible below"

**Context-focused scenes**\
Start with the main setting or architectural element, follow with atmospheric details and style.

> *Example*: "An ancient gothic cathedral with soaring arches and stained glass windows, dramatic chiaroscuro lighting, interior view with dust motes floating in colored light beams"

## Key takeaways

* **Write naturally**; avoid raw keyword dumps
* **Use the core structure**: Subject + Action + Style + Context
* **Front‑load what matters** to steer the image
* **Right-size the length** (30–80 words often hits the sweet spot)
* **Iterate**; adjust one variable at a time

<Note>Include mood, lighting, texture, and spatial detail when it actually changes the result.</Note>

Here is guide prompting the changes in the last frame (compared to the first frame):

# Prompting Guide - Last Frame

**The image generation model** makes editing images easy! Specify what you want to change and the model will follow. It is capable of understanding the context of the image, making it easier to edit them without having to describe in details what you want to do.

## Basic Object Modifications

**The image generation model** is really good at straightforward object modification, for example if we want to change the colour of an object, we can prompt it.

## Prompt Precision: From Basic to Comprehensive

<Tip>
  As a rule of thumb, making things more explicitly never hurts if the number of instructions per edit is not too complicated.
</Tip>

If you want to edit the image with more modifications, it is useful to be more explicit in your prompts to make sure you get the result you want.

### Quick Edits

While using very simple prompts might yield some good results, it can also change the style of the input image.

**Prompt:** *"Change to daytime"*

### Controlled Edits

If we add more instructions to our prompt, we can have results which are really similar to the input image.

**Prompt:** *"Change to daytime while maintaining the same style of the painting"*

### Complex Transformations

If you want to change multiple things on the input image, it is generally good to add as many details as possible as long as the instructions per edit aren't too complicated.

**Prompt:** *"change the setting to a day time, add a lot of people walking the sidewalk while maintaining the same style of the painting"*

### Text Editing Best Practices

* **Use clear, readable fonts** when possible. Complex or stylized fonts may be harder to edit
* **Specify preservation** when needed. For example: *"Replace 'joy' with 'BFL' while maintaining the same font style and color"*
* **Keep text length similar** - Dramatically longer or shorter text may affect layout

## Visual Cues

It is also possible to use Visual cues to suggest to the model where to make edits.
This can be particularly helpful when you want to make targeted changes to specific areas of an image.
By providing visual markers or reference points, you can guide the model to focus on particular regions.

**Example:**: *"Add hats in the boxes"*

## When Results Don't Match Expectations

### General Troubleshooting Tip

If the model is changing elements you want to keep unchanged, be explicit about preservation in your prompt. For example: *"everything else should stay black and white"* or "*maintain all other aspects of the original image*."

### Character identity changes too much

When transforming a person (changing their clothing, style, or context), it's easy to lose their unique identity features if prompts aren't specific enough.

* Try to be more specific about identity markers ("maintain the exact same face, hairstyle, and distinctive features")
* **Example**: *"Transform the man into a viking warrior while preserving his exact facial features, eye color, and facial expression"*

**Vague prompts replace identity:**

* **Prompt:** *"Transform the person into a Viking"* → Complete replacement of facial features, hair, and expression

**Detailed prompts preserve identity:**

* **Prompt:** *"Transform the man into a viking warrior while preserving his exact facial features, eye color, and facial expression"* → Maintains core identity while changing context

**Focused prompts change only what's needed:**

* **Prompt:** *"Change the clothes to be a viking warrior"* → Keeps perfect identity while only modifying the specified element

**Why this happens?**

The verb "transform" without qualifiers often signals to *Kontext* that a complete change is desired. It might be useful to use other words for example in this context if you want to maintain specific aspects of the original image.

### Composition Control

When editing backgrounds or scenes, you often want to keep the subject in exactly the same position, scale, and pose. Simple prompts can sometimes change some of those aspects.

**Simple prompts causing unwanted changes:**

* **Prompt:** *"He's now on a sunny beach"* → Subject position and scale shift
* **Prompt:** *"Put him on a beach"* → Camera angle and framing change

**Precise prompts maintain exact positioning:**

* **Prompt:** *"Change the background to a beach while keeping the person in the exact same position, scale, and pose. Maintain identical subject placement, camera angle, framing, and perspective. Only replace the environment around them"* → Better preservation of subject

**Why this happens?**

Vague instructions like *"put him on a beach"* leave too much to interpretation. *Kontext* might choose to:

* Adjust the framing to match typical beach photos
* Change the camera angle to show more of the beach
* Reposition the subject to better fit the new setting

### Style isn't applying correctly

When applying certain styles, simple prompts might create inconsistent results or lose important elements of the original composition. We could see that in the [example above](#using-prompts).

**Basic style prompts can lose important elements:**

* **Prompt:** *"Make it a sketch"* → While the artistic style is applied, some details are lost.

**Precise style prompts maintain structure:**

* **Prompt:** *"Convert to pencil sketch with natural graphite lines, cross-hatching, and visible paper texture"* → Preserves the scene while applying the style. You can see more details in the background, more cars are also appearing on the image.

## Best Practices Summary

* **Be specific**: Precise language gives better results. Use exact color names, detailed descriptions, and clear action verbs instead of vague terms.
* **Start simple**: Begin with core changes before adding complexity. Test basic edits first, then build upon successful results. Kontext can handle very well iterative editing, use it.
* **Preserve intentionally**: Explicitly state what should remain unchanged. Use phrases like *"while maintaining the same \[facial features/composition/lighting]"* to protect important elements.
* **Iterate when needed**: Complex transformations often require multiple steps. Break dramatic changes into sequential edits for better control.
* **Name subjects directly**: Use "the woman with short black hair" or "the red car" instead of pronouns like "her", "it," or "this" for clearer results.
* **Use quotation marks for text**: Quote the exact text you want to change: `Replace 'joy' with 'BFL'` works better than general text descriptions.
* **Control composition explicitly**: When changing backgrounds or settings, specify *"keep the exact camera angle, position, and framing"* to prevent unwanted repositioning.
* **Choose verbs carefully**: *"Transform"* might imply complete change, while *"change the clothes"* or *"replace the background"* gives you more control over what actually changes.

<Tip>
  **Remember**: Making things more explicit never hurts if the number of instructions per edit isn't too complicated.
</Tip>
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








