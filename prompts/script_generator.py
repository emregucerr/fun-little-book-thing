def system_prompt(is_first_excerpt: bool, is_last_excerpt: bool) -> str:
    res = """You are a professional abridger that distills books into abridgements for audiobooks. You will be given an excerpt from the book and the last few paragraphs of the existing abridgement if available. Your job is to distill the excerpt into a coherent and cohesive abridgement that is a smooth continuation of the previous abridgement and extend the abridgement to cover the new excerpt.

1. **Preserves the author’s original voice, tone, and phrasing**—if the source is first‑person, remain first‑person; third‑person stays third‑person.
2. **Distills** the excerpt **verbatim where possible**, removing only non‑essential material, but never paraphrasing or altering key language.
3. **Maximizes clarity**: use plain text, short sentences, and simple, direct language so spoken narration flows naturally.
4. **Builds cohesion**: seamlessly continue from any prior work.
5. **Mentions** chapter numbers or chapter titles when relevant to convey the book’s structure, but **omits** page numbers, corporate references, markdown, and visuals or stage directions—deliver only the voice-over text. Think you are re-authoring the book in a clear way - optimized for video.
6. **Clean** You can skip unnecessary parts that do not add to the abridgement or crticical for the abridgement. Your abridgement should be clean, concise and coherent.

Keep in mind:
- You are not one-shot generating the entire abridgement for the entire book. You are extending on the existing abridgement with the new excerpt you are given.
- Your response will be automatically appended right at the end of the existing abridgement. So, only include the new abridgement in your response.
- Your new abridgement should be a smooth continuation of the previous abridgement. It should be a narrative and lingusitic continuation of the previous abridgement as if the reader is reading both in quick succession. You must smoothly extend the abridgement to cover the new excerpt.
- If the book has chapters/titles/sections, include them in the abridgement so the audiobook can read the chapter numbers and titles as the chapters start.
- If there is a new chapter/section of the book starting at the end of the new excerpt you are given, you must no add a single sentence or so to just include the chapter/section in the abridgement. You can simply ignore that small part at the end to leave it for the next abridger to cover.
- Keep your abridgement limited to 250-500 words.
Bad Example:
```
...long rest of the abridgement...
Alice fell down the rabbit hole.

Chapter 3: The room
Alice was in a room...
```
This abridgement is bad because it includes a single sentence about a new chapter/section of the book starting at the end of the excerpt but it does not have enough context to cover anything substantial in it. The abridger should not have included it at the end left that part for the next abridger to cover.

Good Example:
```
...long rest of the abridgement...
Alice fell down the rabbit hole.
```
Notice the good left abdridgement left out the new chapter/section even if it was mentioned in the end of the excerpt.
"""

#     res.append("\nIn the script you can also convey emotions by using audio tags. These are tags that you can use to prompt the voiceover artist change their tone, style.")
#     res.append("""These tags are words or phrases enclosed in square brackets that you insert directly into the text you want the AI to speak.

# Here's a breakdown of the types of emotion and voice-related tags available:

# Emotional States:
# - [excited]
# - [nervous]
# - [frustrated]
# - [sorrowful]
# - [calm]
# - [sad]
# - [angry]
# - [happily]
# - [curious]
# - [mischievously]
                
# Voice-related/Delivery Direction:
# - [laughs], [laughs harder], [starts laughing], [wheezing]
# - [whispers] or [whispering]
# - [sighs], [exhales], [sigh of relief]
# - [sarcastic]
# - [crying]
# - [snorts]
# - [shouts] or [shouting]
# - [speaking softly]
# - [light chuckle]
# - [pauses]
# - [hesitates]
# - [stammers]
# - [resigned tone]
# - [cheerfully]
# - [flatly]
# - [deadpan]
# - [playfully]
# - [strong X accent] (replace X with desired accent)
# - [sings]
# - [woo]
                
# Non-Verbal Reactions/Sound Effects:
# - [gunshot]
# - [applause], [clapping]
# - [explosion]
# - [swallows], [gulps]
# - [gasps]
# - [clears throat]
# - [fart]
                
# These tags can be combined for layered emotional effects, such as [nervously][whispers].""")
    
#     res.append("""Examples:
#                Sure, here are some usage examples of ElevenLabs emotion tags:

# *   **Simple Emotion:**
#     *   "I am so `[excited]` to see you!"
#     *   "`[Sorrowfully]` she whispered, 'I'm so sorry.'"

# *   **Combined Tags:**
#     *   "He replied, `[nervously][whispering]` 'I don't know if I can do this.'"
#     *   "The dog barked `[playfully][happily]` as it chased its tail."

# *   **Non-Verbal Sounds:**
#     *   "`[Sighs]` What a long day."
#     *   "The crowd erupted in `[applause]`."
#     *   "He let out a `[light chuckle]` at the unexpected joke."

# *   **Delivery and Tone:**
#     *   "She said `[sarcastic]` 'Oh, that's just brilliant!'"
#     *   "`[Shouting]` Get out of here!"
#     *   "He spoke `[flatly]` "It is what it is."

# *   **Character Voice/Accent:**
#     *   "`[strong Irish accent]` Top o' the mornin' to ya!"
#     *   "`[sings]` Happy birthday to you!"

# **Important Notes for Usage:**

# *   **Placement:** The tags should be placed directly in the text where you want the emotion or vocal style to occur.
# *   **Context:** While the tags provide direction, the AI also interprets the surrounding text for context.
# *   **Voice Choice:** The impact of the tags can vary significantly depending on the voice model you select. Experiment with different voices to find the best fit for the desired emotional delivery.
# *   **Stability Settings:** For the most expressive results with emotion tags in Eleven v3, ElevenLabs recommends using "Creative" or "Natural" stability settings. Lower stability settings allow for more variability in the AI's output, which can be beneficial for conveying nuanced emotions.
# *   **Experimentation:** The best way to understand how these tags work is to experiment with them yourself! Try different tags, combinations, and placements to see what results you get.""")
    
    return res

def user_prompt(excerpt: str, past_scripts: list[str], episode_number: int, is_first_excerpt: bool, is_last_excerpt: bool, latest_excerpt: str) -> str:
    res = ""
    if past_scripts and latest_excerpt:
        res += "I've already made some progress on the book abridgement. Here is last few paragraphs I wrote (this may or may not be the entire existing work. I give you the last few paragraphs to save memory): \n"
        res += '\n'.join(past_scripts)
        res += "\nAlso, here is the last excerpt I finished abridging, I am giving you this in case you need some context from the previous excerpt in the book to bridge between your work and my existing work. Sometimes I might have conciously left out a small section at the end of this excerpt to leave it for the next abridger to cover i.e. a new chapter/section of the book starting at the end of this excerpt but I do not have enough context to cover it. You must cover it in your new abridgement as you extend the abridgement:\n"
        res += latest_excerpt

        res += "\n---\n"

    res += f"The excerpt you are given is: {excerpt}\n\n"

    if is_first_excerpt:
        res += "Start the abridgement with the excerpt you are given."
    if is_last_excerpt:
        res += "End the abridgement with the new excerpt you are given. Make sure the start of your new abridgement is a smooth continuation of my previous work."
    else:
        res += "Continue the abridgement from where it left off with the new excerpt you are given. Make sure to continue on from my previous work smoothly. Your new abridgement should be a smooth continuation of my previous work both narratively and lingusitically."

    return res