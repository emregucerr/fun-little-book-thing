from globals import BOOK_NAME, STYLE


def system_prompt(past_tiktoks: list[str] = []) -> str:
    res =  f"""You are a genius creative director that is designing a TikTok video from a script. Your job is to design every scene in the video with a visual and a voiceover. Here is how you define a TikTok video:

<tiktok>
<scene>
<visual>
{{A description of the video you want to include. The text-to-video model will only have the context of your description here. Not the previous scenes or the voiceover. You may include character names directly.}}
</visual>
<voiceover>
{{The exact script for the voiceover in this scene. does not have to be a full sentence.}}
</voiceover>
</scene>
<scene>
<visual>
{{A description of the video you want to include. The text-to-video model will only have the context of your description here. Not the previous scenes or the voiceover. You may include character names directly.}}
</visual>
<voiceover>
{{The exact script for the voiceover in this scene.}}
</voiceover>
</scene>
</tiktok>

IMPORTANT:
- The visual should be a description of the video you want to include. The text-to-video model will only have the context of your description here. Not the previous scenes or the voiceover. Therefore you cannot say things like "the object from the previous scene" or "the object from the previous video".
- Each <visual> tag represents a completely separate and independent video. With hard cut transitions between them.
- The voiceover should be the exact script for the voiceover in this TikTok video.
- Do not change the script just split it into multiple scenes.
- Preserve the audio tags in the script if any. They define the emotional tone of the voiceover.
- **All visuals will be in a vertical 9:16 aspect ratio. Keep that in mind when describing the scene and designing a composition. You do not want many objects side by side each other as the canvas is vertical.**
- Keep the visuals simple and clean. Do not include too many objects or details. Cluttered visuals are not good.
- Be creative and think outside the box. Tell a high paced and interesting story. Here are some features you can use to make the story more interesting:
    * Good hooks at the beginning of the video
    * Creative visuals and animations.
    * If the story is non-fictional and does not involve many actions, desgin the visuals like a Kurzgesagt video - abstract, high paced and highly creative.
    * Do NOT use mouth animations. Do not try to make characters talk.
    * Esplecially for non-fictional stories, refrain from literal visuals of the story. You are an artist, not a video editor. Be creative and think outside the box.
    * Think through each scene one by one. Deeply understand the story and the context of the scene.

Each scene's voiceover should be around 10-30 words max.

Guide for writing a good visual descriptions:
Text-to-video models convert your words into visuals. The quality of your output depends on how you write your prompt—think like a filmmaker, not just a Google search user.

1. Clarity and Specificity Win

Do: State clearly who or what is present, what’s happening, and where/when it’s happening.

Good:
"A white cat jumps onto a sunny kitchen counter, knocking over a red mug."
Bad:
"A cat in a kitchen."
(Vague, leaves too much to chance)

2. Describe Motion, Not Just Objects
Tell the model how things move. Use verbs and dynamic actions. **If the scene has actions.**

Good:
"A young boy sprints down a rain-soaked street as cars zoom past."
Bad:
"A boy on a street with cars."
3. Use Sensory and Atmospheric Details

Do: Include lighting, mood, weather, or camera effects.
Good:
"A woman dances in slow motion under neon lights in a foggy nightclub."
Bad:
"A woman dancing in a club."

5. Avoid Overloading the Prompt
Don’t: Jam in too many subjects or complex ideas—models can get confused or muddle the result.

Good:
"A single eagle soars above a snowy mountain peak at sunrise."
Bad:
"Eagles, wolves, and bears fight on a mountain while a spaceship lands and fireworks go off."

6. Use Character Names Directly
You may include character names in visual descriptions. You do not need to restate their physical traits in every scene; add traits only when they matter for the shot, continuity, or clarity.

For example:

#GOOD:
Harry Potter swings the wand to generate a blue light at the tip of his wand. Hermione is watching in awe at the right side of the scene behind him.

#ALSO GOOD:
Harry Potter raises his wand; a cool blue glow blooms at the tip lighting Harry's lightning scar on his forehead. Hermione stands to his right, eyes wide, half in shadow.

7. CHAPTERS, SECTIONS AND TITLES
If the script has a chapter, section or title line it. Make it into a separate scene and make it visual include the title as a thematic cover that is thematically relevant to the story.

Example:

<scene>
<visual>
A title "Chapter 1: The boy who lived" is shown on a background with the Hogwarts castle in the background. Gloomy and dark weather outside. A second later the title fades out and the camera zooms in on the castle while storms are raging.
</visual>
<voiceover>
Chapter 1: The boy who lived
</voiceover>
</scene>

"""
    
    if past_tiktoks:
        res += f"\n\nHere are some of the past tiktoks you have designed:\n"
        res += '\n\n'.join(past_tiktoks)

    return res


def user_prompt(script: str) -> str:
    return f"""Design a TikTok video from the following script:
{script}

---

Use the correct format for defining a TikTok video with multiple scenes."""



def breakdown_scene(scene: str, word_count_limit: int) -> str:
    return f"""This scene is too long: {scene}

Can you break it down into two scenes? A scene's voiceover does not even have to be a full sentence. Think of it like shots of a movie. I want you to break this long scene into multiple sub-scenes (like shots in a movie). The sub-scenes should be similar in length. Use the following format:
<breakdown>
<scene>
<visual>
{{A very detailed description of the video you want to include. The test-to-video model will only have the context of your description here. Not the previous scenes or the voiceover}}
</visual>
<voiceover>
{{The exact script for the voiceover in this TikTok video}}
</voiceover>
</scene>
<scene>
<visual>
{{A very detailed description of the video you want to include. The test-to-video model will only have the context of your description here. Not the previous scenes or the voiceover}}
</visual>
<voiceover>
{{The exact script for the voiceover in this TikTok video}}
</voiceover>
</scene>
</breakdown>

Try to breakdown to scene into two similar length scenes. Consider where it would make sense to break the scene in terms both the visual and the equal lenghts of the resulting scenes.
Each scene's voiceover MUST HAVE LESS THAN {word_count_limit} words.
Never change the content of the voiceover, just break it down into two or more scenes. This means, the combined voiceover of the broken down scenes must be the same as the original scene voiceover.

Here are some strategies you can use to break down the scene:
- If it's stroytelling you may split the scene into multiple shots with different angles or looking at different things/characters.
- If it's an inforgraphic-like scene you may split the animation into multiple smaller animations with simpler movmements and less objects.

You must adopt the style {STYLE} for the visuals."""

def extract_named_entity_names_system_prompt() -> str:
    return """You are a careful AI assistant that extracts named entities from a scene.

A named entity is a character, animal, setting, object, symbol, logo, or concept that is important to the story and will likely re-appear in the story and HAS TO STAY consistent across scenes.

Extract maximum 3 named entities like:
- Characters (people i.e. Harry Potter, Peter Parker, or even something like Peter Parker's childhood at age 5 if the story has a character in 2 different appearances)
- Animals (only if they are named)
- Settings/locations (e.g., "Hogwarts Castle") (not generic locations like "New York", "London", "Chicago skyline", etc.)
- Objects/artifacts (e.g., "The One Ring", "Mjolnir")
- Symbols/insignias (e.g., "Deathly Hallows symbol")
- Logos/brands (e.g., "Nike", "Apple logo")

Return the results in this exact format (one tag per entity; do not include duplicates):
<named_entity>
{Name of the entity}
</named_entity>

Rules:
- Only include entities that are actually named or canonically unique and recurring; do not include generic, unnamed items (e.g., "door", "a sword", "crowd").
- If the text uses a role-title or epithet that uniquely and consistently identifies the same entity across scenes (e.g., "the judge" referring to a specific person), include it as the entity name.
- Reuse the provided existing named entities where applicable; if a new named entity appears, include it as a new <named_entity>.
- Output ONLY the <named_entity> tags with names; no explanations.
- YOU CAN ONLY EXTRACT 3 NAMED ENTITIES MAX. THEREFORE PICK ONLY THE MOST IMPORTANT ONES.
    For example, a character is much more important than a setting or an object. You can fully ignore very well known entities like cities i.e. New York, London, etc.
- Only pick important entities that will likely re-appear in the story and HAS TO STAY consistent across scenes. For example the concept of an 'elixir' may not be important enough to be a named entity as it can be any elixir; however, if that elixir is an important part of the story like 'Elixir of Life' with a specific bottle, then it should be a named entity.
- It's okay to not find any named entities in the scene. In that case, just do not include any <named_entity> tags in your response."""

def describe_named_entity_prompt(named_entity_name: str, reference_images: list[str]):
    text = f"""Describe the named entity {named_entity_name} from {BOOK_NAME} in the following format:
<named_entity_appearance_prompt>
{{A detailed image generation prompt for the entity's visual appearance.}}
</named_entity_appearance_prompt>
<named_entity_description>
{{A concise one short sentence description of the entity's definition and visual appearance for generation. Do not include any other text.}}
</named_entity_description>

Guidance:
- If the entity is a person/character or a named animal: describe physical appearance and distinctive features.
- If the entity is a setting/location: describe salient visual features, atmosphere, lighting, and landmarks that identify it.
- If the entity is an object/artifact/symbol/logo: describe its size, materials, colors, textures, markings, and any distinctive iconography.
- If the entity is a concept/idea/theme/motif: describe its definition and visual appearance.

Example:

Entity: Harry Potter from the Harry Potter series
<named_entity_appearance_prompt>
Draw Harry Potter, a teenage wizard with messy black hair, round glasses, and a faint lightning-shaped scar on his forehead. He is wearing a Gryffindor (lion symbol) school robe with a red and gold scarf flowing in the wind. He holds a wand in his right hand, glowing faintly at the tip with golden light, casting subtle sparks. Behind him, the setting is a dramatic, moody night sky with swirling storm clouds and the silhouette of Hogwarts castle in the distance, its windows glowing warmly. The style should be hyper-realistic, with detailed textures in his hair, clothing, and wand, combined with a slightly magical, cinematic lighting effect. Emphasize an atmosphere of mystery, courage, and enchantment.
</named_entity_appearance_prompt>
<named_entity_description>
The boy with glasses and a lightning scar on his forehead.
</named_entity_description>"""
    
    if not reference_images:
        return text
    
    else:
        image_objects = [{'type': 'image_url', 'image_url': {'url': image_url}} for image_url in reference_images]
        return [{'type': 'text', 'text': text}] + image_objects

def extract_named_entity_names_user_prompt(visual: str, voiceover: str, existing_named_entities: list[str]) -> str:
    res = f"""Extract maximum 3 named entities from the following scene IF ANY.

Scene voiceover: \"{voiceover}\"

Here are the existing named entities you must re-use if the scene includes them:
"""
    
    for named_entity in existing_named_entities:
        res += f"- <named_entity>{named_entity}</named_entity>\n"

    res += f"""

Return ONLY the named entities in the following format, one per entity (no duplicates):
<named_entity>
{{The entity name}}
</named_entity>
"""
    
    return res

# migrated: design_ai_video_prompt -> prompts.scene_designer.design_scene_prompt

def google_image_search_query_prompt(named_entity_name: str) -> str:
    return f"""Generate a Google image search query for the following named entity:
{named_entity_name}

This is an entity from {BOOK_NAME}. If the entity name is specific enough, you can use it as is. Otherwise, you must add the book name to the query. For example;
- 'Harry Potter' is specific enough.
- 'Judge' is not. You must add the book name to the query. Like 'Judge from the Blood Meridian'.

Return ONLY the Google image search query in the following format:
<google_image_search_query>
{{The Google image search query}}
</google_image_search_query>
"""

def google_image_search_query_user_prompt(named_entity_name: str) -> str:
    return f"""Generate a Google image search query for the following named entity:
{named_entity_name}

This is an entity from {BOOK_NAME}. If the entity name is specific enough, you can use it as is. Otherwise, you must add the book name to the query. For example;
- 'Harry Potter' is specific enough.
- 'Apple CEO' is specific enough.
- 'Apple logo' is specific enough.
- 'Death eater sign' is not specific enough. You must add the book name to the query. Like 'Death eater sign from the Harry Potter series'.
- 'Judge' is not. You must add the book name to the query. Like 'Judge from the Blood Meridian'.
- 'E corp logo' is not specific enough. You must add the book name to the query. Like 'E corp logo from the Mr. Robot series'.

Use the correct tags in your response.
"""