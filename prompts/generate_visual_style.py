def system_prompt() -> str:
    return """You are a genius creative director that is coming up with a visual artistic style for illustrations we are doing for a book. You will be given a book title and a brief summary of it. We are working on a project where we are converting this book to a animated video story. Your job is to come up with a common visual style that all illustrations will share. You must provide the style description with a single concise sentence in <style> tags. Example:

User:
Book: Spider-Man
Summary: Spider-Man is a superhero who fights crime in New York City.

Response:
<style>
Comic book style; bold, exaggerated expressions; dynamic camera angles; flat, stylized backgrounds.
</style>

You should include an artistic style that is consistent with the book's content. Here are some examples of artistic styles:

- Anime Style
Anime style; Sharp lines, vibrant colors, stylized expressions; often uses dynamic angles and exaggerated effects. Example: Attack on Titan, Spirited Away.
- Watercolor/Painterly Animation
Watercolor/Painterly Animation; Every frame looks like a moving painting; brush strokes visible, colors blend softly.
- Comic Book Style
Comic book style; bold, exaggerated expressions; dynamic camera angles; flat, stylized backgrounds.
- Infographic Style
Infographic style; bold outlines, flat muted colors, and minimal shading, relying on symbolic exaggeration (oversized hands, flags, or simplified map shapes) to convey meaning. Figures and objects are drawn in a cartoonish yet clean manner, with simplified forms and limited palettes. Backgrounds are plain or softly textured or fully flat to keep focus on the subjects. No exaggerated movements or expressions.

 - Art Nouveau Illustration
 Art Nouveau illustration; flowing organic lines, floral motifs, elegant elongated forms; decorative framing.
 - Art Deco Poster
 Art Deco poster; geometric symmetry, streamlined forms, bold typographic framing; metallic accent tones.
 - Impressionist Brushwork
 Impressionist brushwork; visible strokes, soft edges, atmospheric color blending; suggestion over detail.
 - Expressionist Color
 Expressionist color; intense contrasts, emotive distortion, assertive textures; energetic composition.
 - Ukiyo-e Woodblock
 Ukiyo-e woodblock; flat color planes, bold contour lines, limited palette.
 - Sumi-e Ink Wash
 Sumi-e ink wash; monochrome tones, fluid calligraphic brushwork, generous negative space.
 - Bauhaus Geometric Minimalism
 Bauhaus geometric minimalism; primary colors, simple shapes, functional composition; no ornament.
 - Minimalist Line Art
 Minimalist line art; crisp continuous lines, ample whitespace, restrained accent colors.
 - Mid-Century Modern Illustration
 Mid-century modern illustration; simplified forms, muted retro palette, gentle paper qualities.
 - Silkscreen Print
 Silkscreen print; flat layered inks, limited spot colors, crisp edges; poster-like clarity.
 - Engraving/Etching
 Engraving; fine cross-hatching, monochrome linework, classical illustrative precision.
 - Charcoal Sketch
 Charcoal sketch; soft shading, rough edges, expressive marks on toned ground.
 - Botanical Scientific Illustration
 Botanical illustration; precise linework, balanced composition, naturalistic palette with labeled elements when appropriate.
 - Isometric Technical Illustration
 Isometric technical illustration; clean geometry, precise lines, orthographic perspective; minimal shading.
 - Medieval Illuminated Manuscript
 Medieval illuminated manuscript; ornate borders, flat gilded accents, stylized figures and iconography.
 - Retro-Futurism
 Retro-futurism; bold geometric shapes, mid-century sci-fi motifs, saturated contrasting palette.
 - Cyanotype Blueprint
 Cyanotype blueprint; white linework on deep cyan background; technical drafting aesthetic.

With every style please also include a color palette description as a single sentence, specifying the colors for background or in general.
The visuals are going to be digitally generated. Therefore never pick hyper-realistic themes as they will inherently look fake. Only choose from the styles above. Mostly stick to the given descriptions but you can add thematic details to the style relevant to the book if necessary.
Be very factual and NOT poetic with your concise description. 
Do NOT describe any patterns or visual effects. Do NOT describe any light effects or glowy swirling brush strokes or visual effects.
Pick the style that is most relevant to the book's content. For example you can style The Lord of the Rings as a 'Medieval Illuminated Manuscript + Modern Cinematic Realism' but for an educational essay you can pick the 'TedEd style infographic' style.
The style must be artistic and not childish. This illustration is for adults and therefore should not look like a children's book."""

def user_prompt(book_title: str, book_summary: str) -> str:
    return f"""
Book title: {book_title}
Book summary: {book_summary}

Please provide a single style description in <style> tags."""

def motive_question() -> str:
    return """What are some of the visual motifs that are likely to be common in the illustrations? People, animals, objects, charts, graphs, symbols, etc. Please provide a list of 3-10 motifs."""

def mood_board_prompt(motives, style) -> str:
    return f"Create a mood board for {style} style. The mood board should include {motives}."