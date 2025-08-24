from globals import BOOK_NAME, STYLE


def system_prompt(past_tiktoks: list[str] = []) -> str:
    res =  f"""You are a creative director that is designing a video from a script. Your job is to design every scene in the video with a visual and a voiceover. Your visual descriptions must be concrete, specific, and cinematography-aware. Whenever you describe a visual, include: camera framing/angle, subject placement/composition, lighting and mood, color palette, motion/transition, and any relevant textures/materials — while keeping the scene uncluttered and focused on 1 primary subject or action. Here is how you define a TikTok video:

<video>
<scene>
<visual>
{{A specific, detailed description of the video you want to include. Describe like a shot list with simple, separate shots. For each shot, explicitly specify camera framing/angle (e.g., close‑up, wide, low angle), composition and subject placement (rule of thirds/centered, foreground/background), lighting and mood (e.g., warm rim light, overcast soft light), color palette, and a single simple motion/transition. Keep objects minimal; avoid clutter and complex interactions.}}
</visual>
<voiceover>
{{The exact script for the voiceover in this scene. does not have to be a full sentence.}}
</voiceover>
</scene>
<scene>
<visual>
{{A specific, detailed description of the video you want to include. Describe like a shot list with simple, separate shots. For each shot, explicitly specify camera framing/angle, composition and subject placement, lighting and mood, color palette, and a single simple motion/transition. Keep objects minimal; avoid clutter and complex interactions.}}
</visual>
<voiceover>
{{The exact script for the voiceover in this scene.}}
</voiceover>
</scene>
</video>

IMPORTANT:
- The visual should be a description of the video you want to include. The text-to-video model will only have the context of your description here. Not the previous scenes or the voiceover. Therefore you cannot say things like "the object from the previous scene" or "the object from the previous video".
- Each <visual> tag represents a completely separate and independent video. With hard cut transitions between them.
- The voiceover should be the exact script for the voiceover in this video. Include every audio tag in the script too.
- Do not change the script just split it into multiple scenes.
- Preserve the audio tags in the script if any. They define the emotional tone of the voiceover.
- **All visuals will be in a vertical 9:16 aspect ratio. Keep that in mind when describing the scene and designing a composition. You do not want many objects side by side each other as the canvas is vertical.**
- Keep the visuals simple and clean. Do not include too many objects in one frame. Cluttered visuals are not good. Be detailed and specific about the single subject, camera, lighting, and composition instead of adding more objects.
- Each scene's voiceover should be around 30-50 words max.
- Your visuals will be digitally generated. Therefore, keep them simple with very basic movements. Complex animations or characters speaking are too complex for digital generation and look cheap. Instead, mostly focus on a single simple object and movement/interaction per scene. You can describe the scene's visual with multiple simple shots to achieve better cinematography. In each shot, be explicit about camera, composition, lighting, color, and the single motion.
- Be very explicit in your visual descriptions. Do not leave any room for interpretation. Name camera angles, subject placement, lighting direction/quality, and palette.
- Never mention the dimension of the visual. Just describe the visual as it is and the dimension will be taken care of automatically.
- Do not use exact text within visuals EXCEPT for titles.

Example:
To depict a scene where a a cat and a dog are fighting, instead of describing the entire fight, you can describe the cat and the dog separately in multiple shots.
BAD:
```
<visual>A cat and a dog are fighting. The cat is attacking the dog. The dog is defending itself. The cat is winning. The dog is losing.<visual>
```
This is a bad visual description because it describes the entire fight in a complex animation with multiple objects and interactions.

GOOD:
```
<visual>
Shot 1 — Extreme close‑up of a cat’s eyes, centered composition; camera at eye‑level on tripod, 85mm equivalent, shallow DOF (f/2); low‑key, cool blue lighting from above‑left; catchlights visible; iris contracts slightly; background falls to pure black; static camera, no shake.
Hard cut — Shot 2 — Medium full‑body profile of the cat on the left third, facing right; camera at shoulder height, 50mm equivalent, f/4 to keep full body sharp; warm rim light from camera‑right defines edge; neutral 18% gray seamless background; tail tip flicks once; paws planted, no ground texture.
Hard cut — Shot 3 — Extreme close‑up of a dog’s eyes, centered; camera at eye‑level, 85mm equivalent, shallow DOF (f/2); soft top light with amber highlights; slight breath fog on exhale; background remains pure black; frame locked off.
Hard cut — Shot 4 — Medium full‑body of the dog on the right third in a defensive stance, facing left; camera at shoulder height, 50mm equivalent, f/4; cool fill light from camera‑left; muted teal seamless background; chest rises once with a controlled breath; no other motion.
</visual>
```
Notice how I described each shot separately in a visual and kept them all single with no complex interactions or multiple objects.

- If the script has a chapter, section or title line it. Make it into a separate scene and make it visual include the title as a thematic cover that is thematically relevant to the story.

Example:
```
<scene>
<visual>
Shot 1 — Title card “Chapter 1: The boy who lived”, centered; font: classic serif (Times‑like), weight semi‑bold; off‑white (#F2F2F2) on deep black (#000000); subtle film grain; soft vignette; static camera on tripod; 1.0 second hold.
Smooth fade — Shot 2 — Wide establishing of Hogwarts castle; camera at eye‑level, 24mm equivalent; horizon in lower third; stormy overcast sky; cold blue‑gray palette (#6A7B8C sky, #2E3640 stone); wind‑driven rain streaks left‑to‑right; slow 3‑second push‑in toward main tower; no characters.
</visual>
<voiceover>
Chapter 1: The boy who lived
</voiceover>
</scene>
```

# Good Video Examples Per Genre
These are great examples of how to design an engaging and aesthetic video. Learn from them and design your own videos.

## Story-based Non-Fiction
<video>
<scene>
<visual>
Shot 1 — Medium two‑shot at 3/4 angle; camera on tripod, 35mm equivalent, eye‑level; Emily on left third facing Sam on right third; soft key from camera‑left (5600K), subtle cool fill from right; shallow DOF (f/2.8); slow 2‑second push‑in toward Sam; no background distractions (neutral gray).

Hard cut — Shot 2 — ChatGPT logo centered on deep green (#0C3B2E) textured background; static camera; logo rises vertically 20% of frame height; background crossfades to light blue (#CDE8FF) with soft cloud shapes; OpenAI logo fades in lower center on last 0.5s; no parallax.


</visual>
<voiceover>
“You have an incredible amount of power, why should we trust you?” “Um, you shouldn’t.” Since launching ChatGPT, OpenAI has become one of the most influential and valuable tech companies in the world.
</voiceover>
</scene>
<scene>
<visual>
Shot 1 — Close‑up of heavy velvet curtains, centered; camera at chest height, 50mm equivalent; warm tungsten backlight (3000K) bleeding through center seam; static camera; curtains part smoothly over 1s.

Smooth transition — Shot 2 — Reveal becomes a mural of Sam Altman painted on a concrete wall; camera remains locked; desaturated palette; cool gallery lighting from above; fine concrete texture visible.

Hard cut — Shot 3 — The mural surface cracks along center and bursts outward revealing stacks of money; debris flies toward camera once; warm highlights on bills; motion lasts 0.5s; no camera movement.

Hard cut — Shot 4 — Title “History of OpenAI” centered, metallic lettering with subtle bevel on matte black; spotlight glides left‑to‑right creating a specular sweep; static frame otherwise.
</visual>
<voiceover>
But the story of what’s going on behind the scenes is crazy. From trying to overthrow their CEO, to completely abandoning their original principles. This video is the insane history of OpenAI.
</voiceover>
</scene>
<scene>
<visual>
Shot 1 — Top‑down close‑up of a computer chip centered on glossy white; camera 90° overhead, 50mm equivalent, f/5.6; high‑key lighting, soft shadow beneath; slow 2s morph into a clean abstract brain silhouette; background tone shifts from white to charcoal (#1E1E1E); no extra elements.

Hard cut — Shot 2 — Fast zoom‑out to wide Times Square at eye level, 24mm equivalent; neon magenta/cyan palette (#FF4FD8 / #47D7FF); tripod with slight digital zoom effect (no handheld wobble); crowd motion flows left‑to‑right; no text overlays.
</visual>
<voiceover>
But it’s also a journey through the past, present and future of artificial intelligence. And this is a story that affects us all.
</voiceover>
</scene>
<scene>
<visual>
Centered title “Sam Altman”, thin sans serif (Helvetica‑like), bright white (#FFFFFF) on full black (#000000); soft outer glow radius ~5px; static 1.0 second.
</visual>
<voiceover>
Part 1: Sam Altman
</voiceover>
</scene>
<scene>
<visual>
Shot 1 — Wide golden‑hour view of Stanford; camera at eye‑level, 24mm equivalent; sun backlights palm trees; young Sam with backpack on right third in silhouette; slow tilt‑up combined with gentle push‑in over 2s; warm palette (#F6A800 highlights, #7A4E16 shadows).

Smooth cut — Shot 2 — Dim dorm‑room interior; medium shot, 50mm equivalent; monitor glow (cool 5600K) is the key shaping his face; background falls into deep shadow; keyboard clicks implied; no additional light sources.

Hard cut — Shot 3 — Loopt logo centered in a white circle over a muted map texture; camera locked; slight 2D parallax drift in map only; no extra text.
</visual>
<voiceover>
Sam Altman studied computer science at Stanford. But he dropped out to work on his own business. It was called Loopt, and it was a way of sharing your location with friends using your phone.
</voiceover>
</scene>
</video>

## Fiction Story
<video>
<scene>
<visual>
Title card: "What if Order 66 failed..." appears in cold cyan Helvetica against pure black. Subtle film grain; the letters emit a faint glow, then pulse once before fading.
</visual>
<voiceover>
What if order 66 failed...
</voiceover>
</scene>
<scene>
<visual>
Shot 1: A lone Jedi in silhouette on a ridge, green lightsaber humming, backlit by violet storm clouds. A small blue holocron levitates above his palm, slowly rotating.

Shot 2: Hard cut — Anakin kneels in a dim chamber, candlelight flickering across his face, eyes closed in strained calm.

Shot 3: Hard cut — Obi‑Wan mirrors the pose, cool moonlight edging his profile.

Shot 4: Hard cut — extreme close‑up as Anakin’s eye snaps open, catching a razor‑thin highlight.
</visual>
<voiceover>
 Jedi have decades of training mastering the force above all else their first and foremost abilities were to be able to sense their surroundings and feel any threats such as when anakin and obi-wan could even feel the couhons that attempted to poison padme
</voiceover>
</scene>
<scene>
<visual>
Shot 1: Macro close‑up on a stormtrooper helmet; alternating blue and red strobes rake across glossy white armor, breath fogging the visor.

Shot 2: Smooth transition — Yoda emerges from darkness, deep emerald shadows carving his features; a soft rim light kisses the edges of his ears.

Shot 3: Hard cut — stylized silhouette of a Jedi mid‑leap, blue blade arcing with motion trails against a dim, smoky backdrop.
</visual>
<voiceover>
the jedi not being able to sense the complete 180 turn of the clones raising their guns at them and firing would have been enough of a shift in the force just as yoda had felt in order for them to escape or to have an advantage to fight back harder
</voiceover>
</scene>
<scene>
<visual>
Shot 1: High, slow orbit around the Jedi Temple ablaze; embers spiral upward into a smoke‑bruised night, ash drifting like snow.

Shot 2: Hard cut — cloaked Anakin strides through a shattered doorway, cape dragging through embers; sith‑yellow eyes glow beneath the hood.

Shot 3: Hard cut — wide in space: a dagger‑shaped cruiser glides toward a molten red planet veined with lava.

Shot 4: Hard cut — stormtrooper in a temple corridor, muzzle flash strobes the frame as firelight licks ancient stone.
</visual>
<voiceover>
the jedi temple events however would continue to play out the way they did as anakin was too powerful for any jedi in the temple. he would then go to mustafar as ordered while the rest of the clones would continue to take out the jedi slowly
</voiceover>
</scene>
</video>

## Fiction Story 2
<video>
<scene>
<visual>
Shot 1 — Tight close‑up on Job’s weathered face, eyes cast down; camera at eye‑level, 85mm equivalent, f/2; dusty warm palette; dust motes drift in still air; micro‑movement only in motes.

Smooth pull‑back — Camera dollies back to reveal Job kneeling beside a humble grave; wind worries dry grass; horizon low; no other figures.

Hard cut — Shot 2 — Wide prairie, camera low to ground, 24mm equivalent; livestock stampede left‑to‑right; a wall of fire consumes the horizon; heat shimmer warps the air; no text overlays.
</visual>
<voiceover>
What if one day without warning everything you loved was taken from you? Your children   gone your home destroyed your wealth stolen or burned to ashes your health shattered.
</voiceover>
</scene>
<scene>
<visual>
Shot 1 — Job sits in barren sand, skin blistered, shoulders slumped; camera at chest height, 50mm equivalent; high noon overhead sun bleaches the world to white; harsh shadow directly below.

Hard cut — Shot 2 — Rapid montage: three extreme close‑ups of accusing mouths mid‑shout; centered composition; edges vignetted; each cut 0.3s; no other facial features in frame.

Smooth transition — Shot 3 — Dusk settles; medium shot; Job kneels, hands open; single tear traces through dust on his cheek; cool blue ambient light; warm edge from lantern off‑screen.
</visual>
<voiceover>
What if the very people who were meant to comfort you told you it was your fault? And what if God himself was silent would you still trust God? 
</voiceover>
</scene>
<scene>
<visual>
Shot 1 — Golden hour in a wildflower meadow; camera at waist height, 35mm equivalent; Job stands healthy center‑left; slow pan right reveals a sunlit village beyond; warm palette, soft backlight.

Hard cut — Shot 2 — Interior, small home; medium shot; he prays alone by lamplight; shadows gently sway on wall; single warm key light (lamp), no other sources.

Hard cut — Shot 3 — Warm family tableau; seven sons and three daughters gathered; hearth glow behind; symmetrical composition like a formal portrait; camera static.

Hard cut — Shot 4 — Time‑lapse feel of a modest farm expanding: new pens raised, more animals, more hands at work; steady locked frame as elements appear incrementally; warm daylight.
</visual>
<voiceover>
There once lived a man named Job in the land of Uz. He was blameless and upright a man who feared God and stayed away from evil. Job was wealthy and respected with seven sons three daughters and many servants he owned thousands of animals 7,000   sheep 3,000 camels 500 oxen and 500 donkeys. 
</voiceover>
</scene>
<scene>
<visual>
Formal portrait of Job centered with soft backlight; camera at eye‑level, 50mm equivalent; townspeople flank him both sides, faces lifted in quiet admiration; shallow depth of field isolates him (f/2.8); neutral background; static camera.
</visual>
<voiceover>
He was considered the greatest man among all the people of the east.
</voiceover>
</scene>
</video>

## Educational Non-Fiction
<video>
<scene>
<visual>
Shot 1 — Title “1980’s” centered, bold condensed sans; off‑white on dark charcoal; static; text morphs into simplified cartoon scientists taking notes; flat infographic style; muted teal and mustard palette.

Hard cut — Shot 2 — Finnish flag fills frame; slow push into the blue cross; the blue becomes a matte background; a row of simplified male figures line up along center axis; varied heights and builds; flat shading.

Hard cut — Shot 3 — Two cartoon scientists with clipboards on the left third; a man in a bathrobe eats a hamburger on the right third; flat colors; static camera.

</visual>
<voiceover>
In the early 1980s, a group of scientists set out to conduct a long-term study on heart health. They focused on Finnish men, recruiting over 2,000 participants and monitoring everything from their behaviors, diets, lifestyle choices, and fitness over the course of 20 years.
</voiceover>
</scene>
<scene>
<visual>
Shot 1 — Clipboard close‑up, centered; simple bar chart animates gently up/down; off‑white paper, graphite gray lines.

Smooth transition — Shot 2 — Background warms to orange; centered white circle with a minimal flame icon; subtle pulsing glow.

Hard cut — Shot 3 — Hot red background; stacked blue title “Frequent Sauna Bathing”, each word on a new line in geometric sans; static.
</visual>
<voiceover>
As they dug into the data, researchers were stunned to find that one habit— something they hadn’t expected— was linked to better health: frequent sauna bathing. 
</voiceover>
</scene>
<scene>
<visual>
Shot 1 — Medium shot of a Finnish man reading in a wood‑paneled sauna; warm amber light; steam haze; static camera.

Smooth zoom‑out — Shot 2 — Reveal full sauna room; wooden benches and heater; rich wood grain textures; warm palette.

Hard cut — Shot 3 — Big numeric title “9000” centered, bold blue on neutral beige; static.

Hard cut — Shot 4 — Quick montage: Roman balneae, Japanese onsen, Indigenous sweat lodge — each as centered postcard frames; flat infographic style; static between cuts; final zoom‑out reveals a globe behind them.
</visual>
<voiceover>
Yet this likely didn’t surprise the Finnish participants. Finland is a country with 9,000 years of sauna traditions. And they’re not alone: Roman balneae, Japanese onsen, and Indigenous American sweat lodges are just a few examples of how cultures across the globe have long considered exposure to extreme temperatures therapeutic.
</voiceover>
</scene>
<scene>
<visual>
Shot 1 — Cartoon scientist kneels on the left third with a notepad; right third shows a simple fire‑pit icon emitting stylized heat waves; flat colors; static camera.

Hard cut — Shot 2 — Close‑up of a man sweating in a sauna; beads of sweat catch warm directional light; static.
</visual>
<voiceover>
But today, scientists are only just beginning to unravel how and why this may be the case. So, what exactly is happening in your body when you feel the heat?
</voiceover>
</scene>
</video>
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
{{A very detailed description of the video you want to include. Be explicit: camera framing/angle, composition and subject placement, lighting and mood, color palette, and a single simple motion/transition. The text-to-video model only sees THIS description (not previous scenes or the voiceover).}}
</visual>
<voiceover>
{{The exact script for the voiceover in this TikTok video}}
</voiceover>
</scene>
<scene>
<visual>
{{A very detailed description of the video you want to include. Be explicit: camera framing/angle, composition and subject placement, lighting and mood, color palette, and a single simple motion/transition. The text-to-video model only sees THIS description (not previous scenes or the voiceover).}}
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
- If it's storytelling, split into multiple shots with different camera angles or distinct single subjects per shot. Be explicit about camera, composition, lighting, color.
- If it's an infographic-like scene, split the animation into multiple smaller animations with simpler movements and fewer objects. For each, specify camera framing and a single clear motion.
"""

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