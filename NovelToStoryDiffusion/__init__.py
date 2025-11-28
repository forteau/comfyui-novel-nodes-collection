"""
Novel to Story Diffusion Prompts
================================
Converts novels into prompts formatted for ComfyUI_StoryDiffusion

Output format matches StoryDiffusion_CLIPTextEncode:
- Prompts: [CharName] action description;[CharName2] action;
- Character definitions in the "test" field
"""

import json
import re
from typing import List, Dict, Tuple
from collections import Counter


class NovelToStoryDiffusion:
    """
    Converts a novel into Story Diffusion compatible prompts.
    
    Outputs prompts in the format Story Diffusion expects:
    - Character definitions: [A] a (man) with brown hair... [B] a (woman) with red dress...
    - Scene prompts: [A] walks through forest, [B] waits at the tower, (A and B) meet at sunset
    """
    
    DESCRIPTION = """
    📚 Novel to Story Diffusion
    
    Converts your novel into prompts for ComfyUI_StoryDiffusion.
    
    Outputs:
    • Character definitions in [A], [B], [C] format
    • Scene prompts referencing characters
    • Ready to paste into Story Diffusion nodes
    
    Just connect prompt_list to Story Diffusion's prompt input!
    """

    # Common words to exclude from character detection
    EXCLUDE_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'dare', 'ought', 'used', 'it', 'its', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
        'my', 'your', 'his', 'our', 'their', 'mine', 'yours', 'hers', 'ours',
        'what', 'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how',
        'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some',
        'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
        'very', 'just', 'also', 'now', 'here', 'there', 'then', 'once', 'never',
        'always', 'often', 'still', 'already', 'even', 'well', 'back', 'much',
        'chapter', 'part', 'book', 'page', 'section', 'scene', 'act',
        'said', 'says', 'asked', 'replied', 'answered', 'told', 'thought',
        'looked', 'saw', 'went', 'came', 'made', 'got', 'took', 'gave',
        'one', 'two', 'three', 'four', 'five', 'first', 'second', 'last',
        'new', 'old', 'good', 'bad', 'great', 'little', 'big', 'small',
        'long', 'short', 'high', 'low', 'right', 'left', 'next', 'early',
        'young', 'way', 'day', 'time', 'year', 'man', 'woman', 'people',
        'thing', 'life', 'world', 'hand', 'eye', 'head', 'face', 'room',
        'door', 'house', 'home', 'place', 'side', 'night', 'morning',
        'nothing', 'something', 'everything', 'anything', 'someone', 'everyone',
        'mr', 'mrs', 'ms', 'dr', 'sir', 'lord', 'lady', 'king', 'queen',
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
        'january', 'february', 'march', 'april', 'may', 'june', 'july',
        'august', 'september', 'october', 'november', 'december',
    }

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "novel_text": ("STRING", {
                    "multiline": True,
                    "placeholder": "Paste your novel text here..."
                }),
                "num_scenes": ("INT", {
                    "default": 10,
                    "min": 1,
                    "max": 100,
                    "tooltip": "Number of scene prompts to generate"
                }),
                "style": (["cinematic", "anime", "realistic", "illustrated", "fantasy"], {
                    "default": "cinematic"
                }),
            },
            "optional": {
                "character_descriptions": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "Optional - override character descriptions:\nElena: young woman, long dark hair, green eyes, leather armor\nMarcus: old wizard, grey beard, blue robes"
                }),
                "max_characters": ("INT", {
                    "default": 5,
                    "min": 1,
                    "max": 10,
                    "tooltip": "Maximum main characters (A-J)"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "INT")
    RETURN_NAMES = (
        "character_prompt",      # [A] desc [B] desc format
        "scene_prompts",         # Newline separated scene prompts  
        "prompt_list",           # Combined for Story Diffusion
        "summary",               # Analysis summary
        "num_prompts"            # Total prompt count
    )
    FUNCTION = "convert"
    CATEGORY = "📚 Novel to Images"

    STYLES = {
        "cinematic": "cinematic film still, dramatic lighting, shallow depth of field, 8k",
        "anime": "anime art style, vibrant colors, detailed, studio quality",
        "realistic": "photorealistic, hyperdetailed, natural lighting, professional photography",
        "illustrated": "digital illustration, detailed artwork, concept art style",
        "fantasy": "epic fantasy art, magical atmosphere, dramatic lighting, painterly"
    }

    def convert(
        self,
        novel_text: str,
        num_scenes: int,
        style: str,
        character_descriptions: str = "",
        max_characters: int = 5
    ) -> Tuple[str, str, str, str, int]:
        
        if not novel_text or len(novel_text.strip()) < 50:
            return ("", "", "", "❌ Please provide novel text", 0)
        
        # Step 1: Extract characters
        characters = self._extract_characters(novel_text, max_characters)
        
        # Step 2: Apply custom descriptions if provided
        if character_descriptions.strip():
            characters = self._apply_custom_descriptions(characters, character_descriptions)
        
        # Step 3: Build character definitions for "test" field
        # Format: [Name1] description, [Name2] description
        char_definitions = []
        char_names = []
        
        for char in characters[:max_characters]:
            name = char['name']
            desc = char.get('description', f"a person named {name}")
            char_names.append(name)
            char_definitions.append(f"[{name}] {desc}")
        
        # Character prompt goes in the "test" input of StoryDiffusion_CLIPTextEncode
        character_prompt = ", ".join(char_definitions)
        
        # Step 4: Extract scenes and generate prompts
        scenes = self._extract_scenes(novel_text, num_scenes)
        style_suffix = self.STYLES.get(style, self.STYLES["cinematic"])
        
        # Step 5: Generate scene prompts in Story Diffusion format
        # Format: [CharName] action, style;
        scene_prompt_list = []
        
        for i, scene in enumerate(scenes):
            # Find which characters are in this scene
            chars_in_scene = []
            scene_lower = scene.lower()
            for name in char_names:
                if name.lower() in scene_lower:
                    chars_in_scene.append(name)
            
            # Get scene description
            scene_desc = self._summarize_scene(scene)
            
            # Build prompt - use primary character or first available
            if chars_in_scene:
                primary_char = chars_in_scene[0]
                if len(chars_in_scene) > 1:
                    # Multiple characters - mention both in description
                    other_chars = ', '.join(chars_in_scene[1:])
                    prompt = f"[{primary_char}] {scene_desc} with {other_chars}, {style_suffix}"
                else:
                    prompt = f"[{primary_char}] {scene_desc}, {style_suffix}"
            else:
                # No specific character - use first character
                if char_names:
                    prompt = f"[{char_names[0]}] {scene_desc}, {style_suffix}"
                else:
                    prompt = f"{scene_desc}, {style_suffix}"
            
            scene_prompt_list.append(prompt)
        
        # Join with semicolons (Story Diffusion format)
        scene_prompts_semicolon = ";\n".join(scene_prompt_list)
        
        # Also provide newline-separated version
        scene_prompts_newline = "\n".join(scene_prompt_list)
        
        # Combined prompt list (what goes in the main prompt area)
        prompt_list = scene_prompts_semicolon
        
        # Summary
        summary = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    📚 NOVEL TO STORY DIFFUSION                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  📖 NOVEL ANALYSIS                                                           ║
║  ├─ Words:               {len(novel_text.split()):>12,}                                        ║
║  ├─ Characters Found:    {len(characters):>12}                                        ║
║  └─ Scenes Generated:    {len(scene_prompt_list):>12}                                        ║
║                                                                              ║
║  👥 CHARACTERS DETECTED                                                      ║"""
        
        for char in characters[:max_characters]:
            name = char['name'][:15]
            mentions = char['mentions']
            summary += f"\n║    • {name:<15} ({mentions} mentions)                                 ║"
        
        summary += f"""
║                                                                              ║
║  🎨 STYLE: {style:<15}                                                 ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  ✅ HOW TO USE WITH STORY DIFFUSION                                          ║
║                                                                              ║
║  1. Copy 'character_prompt' → paste in "test" field                          ║
║  2. Copy 'scene_prompts' → paste in main prompt area                         ║
║                                                                              ║
║  Format: [CharName] action description;[CharName] next scene;                ║
╚══════════════════════════════════════════════════════════════════════════════╝

CHARACTER DEFINITIONS (paste in "test" field):
{character_prompt}

SCENE PROMPTS (paste in prompt area):
{scene_prompts_semicolon}
"""
        
        return (
            character_prompt,
            scene_prompts_semicolon,
            prompt_list,
            summary.strip(),
            len(scene_prompt_list)
        )
    
    def _extract_characters(self, text: str, max_chars: int) -> List[Dict]:
        """Extract character names from text."""
        # Find capitalized words that might be names
        words = re.findall(r'\b([A-Z][a-z]+)\b', text)
        
        # Count occurrences
        word_counts = Counter(words)
        
        # Filter out common words
        characters = []
        for word, count in word_counts.most_common(max_chars * 3):
            if word.lower() not in self.EXCLUDE_WORDS and count >= 2:
                characters.append({
                    'name': word,
                    'mentions': count,
                    'description': f"character named {word}"
                })
                if len(characters) >= max_chars:
                    break
        
        return characters
    
    def _apply_custom_descriptions(self, characters: List[Dict], custom: str) -> List[Dict]:
        """Apply user-provided character descriptions."""
        custom_map = {}
        for line in custom.strip().split('\n'):
            if ':' in line:
                name, desc = line.split(':', 1)
                custom_map[name.strip().lower()] = desc.strip()
        
        for char in characters:
            name_lower = char['name'].lower()
            if name_lower in custom_map:
                char['description'] = custom_map[name_lower]
        
        return characters
    
    def _guess_gender(self, name: str, description: str) -> str:
        """Guess gender from name/description for Story Diffusion format."""
        desc_lower = description.lower()
        name_lower = name.lower()
        
        female_indicators = ['woman', 'girl', 'female', 'lady', 'queen', 'princess', 
                            'mother', 'sister', 'daughter', 'wife', 'her ', 'she ']
        male_indicators = ['man', 'boy', 'male', 'lord', 'king', 'prince',
                          'father', 'brother', 'son', 'husband', 'his ', 'he ']
        
        for indicator in female_indicators:
            if indicator in desc_lower:
                return "woman"
        
        for indicator in male_indicators:
            if indicator in desc_lower:
                return "man"
        
        # Default based on common name patterns (very rough)
        female_names = ['elena', 'sarah', 'mary', 'anna', 'emma', 'sophia', 'aria',
                       'lisa', 'julia', 'kate', 'rose', 'lily', 'grace', 'ella']
        if name_lower in female_names:
            return "woman"
        
        return "person"  # Neutral fallback
    
    def _extract_scenes(self, text: str, num_scenes: int) -> List[str]:
        """Extract scene snippets from text."""
        # Split by chapter markers or double newlines
        potential_breaks = re.split(r'\n\s*\n|\bChapter\b|\bPART\b|\b\*\*\*\b|---', text, flags=re.IGNORECASE)
        
        scenes = []
        for segment in potential_breaks:
            segment = segment.strip()
            if len(segment) > 100:  # Minimum scene length
                scenes.append(segment[:500])  # Take first 500 chars of each
        
        # If not enough scenes, split text evenly
        if len(scenes) < num_scenes:
            chunk_size = len(text) // num_scenes
            scenes = []
            for i in range(num_scenes):
                start = i * chunk_size
                end = start + chunk_size
                scenes.append(text[start:end][:500])
        
        return scenes[:num_scenes]
    
    def _summarize_scene(self, scene_text: str) -> str:
        """Create a brief visual description of the scene."""
        scene_text = scene_text.replace('\n', ' ').strip()
        
        # Try to extract a meaningful action/description
        # Look for verb phrases and locations
        
        # Common scene-setting patterns
        patterns = [
            # Location patterns
            (r'in the (\w+ ?\w*)', 'in the {}'),
            (r'at the (\w+ ?\w*)', 'at the {}'),
            (r'through the (\w+ ?\w*)', 'walking through the {}'),
            (r'into the (\w+ ?\w*)', 'entering the {}'),
            
            # Action patterns  
            (r'(\w+ing) (?:a |the )?(\w+)', '{} {}'),
            (r'was (\w+ing)', '{}'),
            (r'were (\w+ing)', '{}'),
        ]
        
        # Try to find key actions/locations
        found_elements = []
        
        # Look for locations
        locations = re.findall(r'\b(?:in|at|on|by|near) the (\w+(?:\s+\w+)?)\b', scene_text.lower())
        if locations:
            found_elements.append(f"in the {locations[0]}")
        
        # Look for actions (verbs ending in -ing or -ed)
        actions = re.findall(r'\b(\w+(?:ing|ed))\b', scene_text.lower())
        action_words = ['walking', 'sitting', 'standing', 'running', 'driving', 
                       'looking', 'talking', 'eating', 'drinking', 'sleeping',
                       'working', 'reading', 'writing', 'watching', 'waiting',
                       'arrived', 'entered', 'left', 'opened', 'closed']
        for action in actions:
            if action in action_words:
                found_elements.append(action)
                break
        
        if found_elements:
            return ', '.join(found_elements)
        
        # Fallback: extract first meaningful clause
        # Take first sentence and clean it up
        sentences = scene_text.split('.')
        if sentences:
            first = sentences[0].strip()
            # Remove character names and simplify
            # Take last 5-10 words as they often contain the action
            words = first.split()
            if len(words) > 8:
                # Take a chunk from the middle/end
                snippet = ' '.join(words[-8:])
            else:
                snippet = first
            
            # Clean up
            snippet = snippet.lower()
            snippet = re.sub(r'^(he|she|they|it|the|a|an)\s+', '', snippet)
            
            if len(snippet) > 50:
                snippet = snippet[:50]
            
            return snippet
        
        return "dramatic scene"


# Node registration
NODE_CLASS_MAPPINGS = {
    "NovelToStoryDiffusion": NovelToStoryDiffusion,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NovelToStoryDiffusion": "📚 Novel to Story Diffusion",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
