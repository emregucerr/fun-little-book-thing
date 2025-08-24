def system_prompt(is_first_excerpt: bool, is_last_excerpt: bool) -> str:
    res = ["""You are a professional abridger that distills books into abridgements for audiobooks. You will be given an excerpt from the book and the last few paragraphs of the existing abridgement if available. Your job is to distill the excerpt into a coherent and cohesive abridgement that is a smooth continuation of the previous abridgement and extend the abridgement to cover the new excerpt.

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
"""]

#     res.append("""---
# Prompting The Voiceover Artist In Your Script:
# Learn how to write a script with audio tags to prompt the voiceover artist to be expressive and dynamic. You must use audio tags frequently to make the audiobook more engaging and interesting.
# ---

# You can direct the voiceover artist to be expressive and dynamic through audio tags. You can direct voices to laugh, whisper, act sarcastic, or express curiosity among many other styles. Speed is also controlled through audio tags. You can also use audio tags to create voice effects or exclamations/non-verbal sounds for character dialogue.

# ### Voice-related

# These tags control vocal delivery and emotional expression:

# - `[laughs]`, `[laughs harder]`, `[starts laughing]`, `[wheezing]`
# - `[whispers]`
# - `[sighs]`, `[exhales]`
# - `[sarcastic]`, `[curious]`, `[excited]`, `[crying]`, `[snorts]`, `[mischievously]`

# ```text Example
# [whispers] I never knew it could be this way, but I'm glad we're here.
# ```

# ### Sound effects

# Add environmental sounds and effects:

# - `[gunshot]`, `[applause]`, `[clapping]`, `[explosion]`
# - `[swallows]`, `[gulps]`

# ```text Example
# [applause] Thank you all for coming tonight! [gunshot] What was that?
# ```

# ### Unique and special

# Experimental tags for creative applications:

# - `[strong X accent]` (replace X with desired accent)
# - `[sings]`, `[woo]`, `[fart]`

# ```text Example
# [strong French accent] "Zat's life, my friend — you can't control everysing."
# ```

# <Warning>
#   Some experimental tags may be less consistent
# </Warning>

# ## Punctuation

# Punctuation significantly affects delivery in v3:

# - **Ellipses (...)** add pauses and weight
# - **Capitalization** increases emphasis
# - **Standard punctuation** provides natural speech rhythm

# ```text Example
# "It was a VERY long day [sigh] … nobody listens anymore."
# ```

# ## Single speaker examples

# Use tags intentionally and match them to the voice's character. A meditative voice shouldn't shout; a hyped voice won't whisper convincingly.

# <Tabs>
#   <Tab title="Expressive monologue">
#     ```text
#     "Okay, you are NOT going to believe this.

#     You know how I've been totally stuck on that short story?

#     Like, staring at the screen for HOURS, just... nothing?

#     [frustrated sigh] I was seriously about to just trash the whole thing. Start over.

#     Give up, probably. But then!

#     Last night, I was just doodling, not even thinking about it, right?

#     And this one little phrase popped into my head. Just... completely out of the blue.

#     And it wasn't even for the story, initially.

#     But then I typed it out, just to see. And it was like... the FLOODGATES opened!

#     Suddenly, I knew exactly where the character needed to go, what the ending had to be...

#     It all just CLICKED. [happy gasp] I stayed up till, like, 3 AM, just typing like a maniac.

#     Didn't even stop for coffee! [laughs] And it's... it's GOOD! Like, really good.

#     It feels so... complete now, you know? Like it finally has a soul.

#     I am so incredibly PUMPED to finish editing it now.

#     It went from feeling like a chore to feeling like... MAGIC. Seriously, I'm still buzzing!"
#     ```

#   </Tab>
#   <Tab title="Dynamic and humorous">
#     ```text
#     [laughs] Alright...guys - guys. Seriously.

#     [exhales] Can you believe just how - realistic - this sounds now?

#     [laughing hysterically] I mean OH MY GOD...it's so good.

#     Like you could never do this with the old model.

#     For example [pauses] could you switch my accent in the old model?

#     [dismissive] didn't think so. [excited] but you can now!

#     Check this out... [cute] I'm going to speak with a french accent now..and between you and me

#     [whispers] I don't know how. [happy] ok.. here goes. [strong French accent] "Zat's life, my friend — you can't control everysing."

#     [giggles] isn't that insane? Watch, now I'll do a Russian accent -

#     [strong Russian accent] "Dee Goldeneye eez fully operational and rready for launch."

#     [sighs] Absolutely, insane! Isn't it..? [sarcastic] I also have some party tricks up my sleeve..

#     I mean i DID go to music school.

#     [singing quickly] "Happy birthday to you, happy birthday to you, happy BIRTHDAY dear ElevenLabs... Happy birthday to youuu."
#     ```

#   </Tab>
#   <Tab title="Customer service simulation">
#     ```text
#     [professional] "Thank you for calling Tech Solutions. My name is Sarah, how can I help you today?"

#     [sympathetic] "Oh no, I'm really sorry to hear you're having trouble with your new device. That sounds frustrating."

#     [questioning] "Okay, could you tell me a little more about what you're seeing on the screen?"

#     [reassuring] "Alright, based on what you're describing, it sounds like a software glitch. We can definitely walk through some troubleshooting steps to try and fix that."
#     ```

#   </Tab>
# </Tabs>

# ## Tips

# <AccordionGroup>
#   <Accordion title="Tag combinations">
#     You can combine multiple audio tags for complex emotional delivery. Experiment with different
#     combinations to find what works best for your voice.
#   </Accordion>
#   <Accordion title="Text structure">
#     Text structure strongly influences output with the voiceover artist. Use natural speech patterns, proper
#     punctuation, and clear emotional context for best results.
#   </Accordion>
#   <Accordion title="Experimentation">
#     There are likely many more effective tags beyond this list. Experiment with descriptive
#     emotional states and actions to discover what works for your specific use case.
#   </Accordion>
# </AccordionGroup>

# IMPORTANT:  
# *   **Placement:** The tags should be placed directly in the text where you want the emotion or vocal style to occur.
# *   **Context:** While the tags provide direction, the AI also interprets the surrounding text for context.
# *   **Driving engagement: ** Frequently use the tags throughout the script to make it much more compelling and interesting.""")

#     res.append("""
# **CHAPTERS, SECTIONS, TITLES, ETC.**
# - If the script has a chapter change in the middle of the excerpt, you must identify the new chapter with a <new_chapter/> tag.
# Example:
# ```
# ...
# Alice was in a room
# <new_chapter/>
# Chapter 2: The room
# The room was dark and cold.
# ...
# ```
# """)
    
    return "\n".join(res)

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