"""
Novel Cinematic Orchestrator - Main Node
========================================
A comprehensive ComfyUI custom node that transforms novels/stories into
cinematic visual story plans with consistent characters, TTS narration,
SFX cues, and 3D parallax support.

Author: Claude AI Assistant
Version: 1.0.0
"""

import json
import re
import textwrap
import hashlib
from typing import List, Dict, Tuple, Optional, Any


class NovelCinematicOrchestrator:
    """
    Master orchestrator node for novel-to-video pipeline.
    
    Takes a novel/story text and generates a complete production plan including:
    - Scene segmentation with intelligent paragraph analysis
    - Image prompts for B-roll generation
    - Narration text for TTS
    - SFX cues for audio generation
    - Configuration for downstream nodes
    """
    
    DESCRIPTION = """
    📖 Novel to Cinematic Video Orchestrator
    
    Transform your novel or story into a complete video production plan.
    This node analyzes your text and generates:
    
    • Intelligent scene segmentation
    • Image prompts for visual B-roll
    • Narration text for TTS/voice cloning
    • SFX cues for ambient audio
    • Character extraction for consistency
    
    Connect to IndexTTS, Depthflow, MMAudio, and video assembly nodes
    for fully automated video generation.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "novel_text": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "placeholder": "Paste your novel or story text here..."
                }),
                "max_scene_chars": ("INT", {
                    "default": 2000,
                    "min": 500,
                    "max": 10000,
                    "step": 100,
                    "display": "slider",
                    "tooltip": "Maximum characters per scene. Smaller = more scenes."
                }),
                "broll_density": ("INT", {
                    "default": 4,
                    "min": 1,
                    "max": 16,
                    "step": 1,
                    "display": "slider",
                    "tooltip": "Number of image prompts per scene."
                }),
                "image_engine": (["flux", "sdxl", "sd15", "cascade", "pixart"],),
                "image_style": (["cinematic", "anime", "realistic", "painterly", "comic", "storyboard"],),
                "character_profile": ("STRING", {
                    "default": "",
                    "placeholder": "MC_lora, heroine_lora, fantasy_style...",
                    "tooltip": "Comma-separated LoRA names for character consistency"
                }),
                "voice_mode": (["index_tts", "index_clone", "xtts", "voxcpm", "chatterbox"],),
                "parallax_enabled": ("BOOLEAN", {
                    "default": True,
                    "label_on": "3D Parallax ON",
                    "label_off": "2D Ken Burns"
                }),
                "sfx_mode": (["mmaudio_auto", "mmaudio_prompted", "stable_audio", "none"],),
            },
            "optional": {
                "voice_reference_audio": ("AUDIO",),
                "character_reference_images": ("IMAGE",),
                "custom_style_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "Additional style instructions for all image prompts..."
                }),
                "scene_transition_style": (["fade", "cut", "dissolve", "wipe"],),
                "target_video_fps": ("INT", {
                    "default": 24,
                    "min": 12,
                    "max": 60,
                    "step": 1
                }),
                "target_resolution": (["1920x1080", "1280x720", "3840x2160", "1080x1920", "720x1280"],),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "scenes_json",
        "image_prompts_json", 
        "narration_json",
        "sfx_cues_json",
        "characters_json",
        "config_json",
        "summary_text"
    )
    
    OUTPUT_TOOLTIPS = (
        "JSON array of scene texts",
        "JSON array of image prompts per scene",
        "JSON array of narration text per scene",
        "JSON array of SFX cues per scene",
        "JSON array of extracted character names",
        "JSON configuration object for downstream nodes",
        "Human-readable summary of the production plan"
    )
    
    FUNCTION = "process_novel"
    CATEGORY = "🎬 Story Tools/Orchestration"
    
    # ============== Character & Entity Extraction ==============
    
    COMMON_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'it', 'its', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
        'she', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your',
        'his', 'our', 'their', 'what', 'which', 'who', 'whom', 'whose',
        'where', 'when', 'why', 'how', 'all', 'each', 'every', 'both',
        'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
        'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'also',
        'now', 'here', 'there', 'then', 'once', 'said', 'asked', 'replied',
        'thought', 'knew', 'felt', 'looked', 'seemed', 'made', 'went', 'came',
        'got', 'took', 'saw', 'put', 'told', 'gave', 'found', 'called',
        'yes', 'no', 'oh', 'ah', 'well', 'please', 'thank', 'thanks',
        'mr', 'mrs', 'ms', 'dr', 'prof', 'sir', 'madam', 'lord', 'lady'
    }
    
    def _extract_characters(self, text: str) -> List[Dict[str, Any]]:
        """Extract character names and their mention counts from text."""
        # Pattern for capitalized names (potential character names)
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'
        
        # Find all potential names
        matches = re.findall(name_pattern, text)
        
        # Count occurrences and filter
        name_counts = {}
        for name in matches:
            name_lower = name.lower()
            # Skip common words and short names
            if name_lower not in self.COMMON_WORDS and len(name) > 2:
                name_counts[name] = name_counts.get(name, 0) + 1
        
        # Filter to names that appear multiple times (likely characters)
        characters = []
        for name, count in sorted(name_counts.items(), key=lambda x: -x[1]):
            if count >= 2:  # Must appear at least twice
                characters.append({
                    "name": name,
                    "mentions": count,
                    "id": hashlib.md5(name.encode()).hexdigest()[:8]
                })
        
        return characters[:20]  # Limit to top 20 characters
    
    # ============== Scene Segmentation ==============
    
    def _detect_scene_breaks(self, text: str) -> List[int]:
        """Detect natural scene breaks in text."""
        # Patterns that indicate scene changes
        scene_break_patterns = [
            r'\n\s*\*\s*\*\s*\*\s*\n',  # *** dividers
            r'\n\s*---+\s*\n',           # --- dividers
            r'\n\s*#{1,3}\s+',           # Markdown headers
            r'\nChapter\s+\d+',          # Chapter markers
            r'\nPart\s+\d+',             # Part markers
            r'\n\s*\d+\.\s+',            # Numbered sections
            r'\n{3,}',                    # Multiple blank lines
        ]
        
        breaks = set()
        for pattern in scene_break_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                breaks.add(match.start())
        
        return sorted(breaks)
    
    def _chunk_scenes(self, text: str, max_chars: int) -> List[Dict[str, Any]]:
        """
        Split text into scenes with intelligent paragraph analysis.
        Returns scene objects with text and metadata.
        """
        # First, try to use natural scene breaks
        scene_breaks = self._detect_scene_breaks(text)
        
        # Split by paragraphs
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        
        scenes = []
        current_scene = {
            "text": "",
            "paragraphs": [],
            "start_idx": 0
        }
        current_len = 0
        
        for i, paragraph in enumerate(paragraphs):
            para_len = len(paragraph)
            
            # Check if we should start a new scene
            should_break = False
            
            # Check if this paragraph starts after a scene break
            if scene_breaks:
                para_start = text.find(paragraph)
                for break_pos in scene_breaks:
                    if para_start > break_pos and break_pos > current_scene["start_idx"]:
                        should_break = True
                        break
            
            # Check if adding this paragraph exceeds max_chars
            if current_len + para_len + 2 > max_chars and current_scene["text"]:
                should_break = True
            
            if should_break and current_scene["text"]:
                # Save current scene
                current_scene["char_count"] = len(current_scene["text"])
                current_scene["para_count"] = len(current_scene["paragraphs"])
                scenes.append(current_scene)
                
                # Start new scene
                current_scene = {
                    "text": paragraph,
                    "paragraphs": [paragraph],
                    "start_idx": text.find(paragraph) if paragraph in text else 0
                }
                current_len = para_len
            else:
                # Add to current scene
                if current_scene["text"]:
                    current_scene["text"] += "\n\n" + paragraph
                else:
                    current_scene["text"] = paragraph
                current_scene["paragraphs"].append(paragraph)
                current_len += para_len + 2
        
        # Don't forget the last scene
        if current_scene["text"]:
            current_scene["char_count"] = len(current_scene["text"])
            current_scene["para_count"] = len(current_scene["paragraphs"])
            scenes.append(current_scene)
        
        # Add scene indices
        for i, scene in enumerate(scenes):
            scene["index"] = i
            scene["id"] = f"scene_{i+1:03d}"
        
        return scenes
    
    # ============== Image Prompt Generation ==============
    
    STYLE_TEMPLATES = {
        "cinematic": "cinematic film still, dramatic lighting, shallow depth of field, professional cinematography, 4K, HDR",
        "anime": "anime art style, vibrant colors, detailed linework, studio quality animation, expressive characters",
        "realistic": "photorealistic, hyperdetailed, natural lighting, 8K resolution, professional photography",
        "painterly": "oil painting style, rich textures, artistic brushstrokes, masterful composition, gallery quality",
        "comic": "comic book art, bold lines, dynamic composition, vibrant panel art, graphic novel style",
        "storyboard": "storyboard frame, concept art, key frame, professional pre-visualization"
    }
    
    ENGINE_QUALITY = {
        "flux": "masterpiece, best quality, highly detailed, sharp focus",
        "sdxl": "masterpiece, best quality, ultra detailed, 8k uhd",
        "sd15": "best quality, highly detailed, sharp focus, intricate details",
        "cascade": "high quality, detailed, professional, sharp",
        "pixart": "high quality artwork, detailed, aesthetic, professional"
    }
    
    def _extract_visual_elements(self, text: str) -> Dict[str, List[str]]:
        """Extract visual elements (locations, objects, actions) from text."""
        elements = {
            "locations": [],
            "objects": [],
            "actions": [],
            "atmosphere": [],
            "time_of_day": []
        }
        
        # Location keywords
        location_patterns = [
            r'\b(?:in|at|inside|outside|near|beside|through)\s+(?:the\s+)?([a-z]+(?:\s+[a-z]+)?)',
            r'\b(forest|city|room|house|castle|village|street|garden|mountain|cave|ocean|beach|desert)\b',
            r'\b(kitchen|bedroom|hallway|library|tower|dungeon|palace|temple|church|school)\b'
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text.lower())
            elements["locations"].extend(matches if isinstance(matches[0] if matches else '', str) else [m for m in matches])
        
        # Time of day
        time_patterns = [
            r'\b(dawn|sunrise|morning|noon|afternoon|dusk|sunset|evening|night|midnight|twilight)\b'
        ]
        for pattern in time_patterns:
            elements["time_of_day"].extend(re.findall(pattern, text.lower()))
        
        # Atmosphere
        atmosphere_patterns = [
            r'\b(dark|bright|gloomy|cheerful|tense|peaceful|chaotic|mysterious|eerie|warm|cold)\b'
        ]
        for pattern in atmosphere_patterns:
            elements["atmosphere"].extend(re.findall(pattern, text.lower()))
        
        # Remove duplicates while preserving order
        for key in elements:
            elements[key] = list(dict.fromkeys(elements[key]))
        
        return elements
    
    def _generate_image_prompts(self, scene: Dict, scene_idx: int, 
                                  broll_density: int, style: str, 
                                  engine: str, custom_style: str,
                                  characters: List[Dict]) -> List[Dict[str, Any]]:
        """Generate detailed image prompts for a scene."""
        text = scene["text"]
        
        # Extract visual elements
        visual_elements = self._extract_visual_elements(text)
        
        # Get style and quality modifiers
        style_mod = self.STYLE_TEMPLATES.get(style, self.STYLE_TEMPLATES["cinematic"])
        quality_mod = self.ENGINE_QUALITY.get(engine, self.ENGINE_QUALITY["flux"])
        
        # Split scene into chunks for different shots
        flat_text = " ".join(text.replace("\n", " ").split())
        chunk_size = max(len(flat_text) // max(broll_density, 1), 50)
        
        prompts = []
        
        for i in range(broll_density):
            start = i * chunk_size
            snippet = flat_text[start:start + chunk_size]
            
            if not snippet:
                continue
            
            # Determine shot type based on position
            shot_types = ["establishing shot", "medium shot", "close-up", "wide shot", 
                         "over-the-shoulder", "POV shot", "detail shot", "reaction shot"]
            shot_type = shot_types[i % len(shot_types)]
            
            # Build prompt components
            components = []
            
            # Shot info
            components.append(f"Scene {scene_idx + 1}, Shot {i + 1}, {shot_type}")
            
            # Location context
            if visual_elements["locations"]:
                loc = visual_elements["locations"][i % len(visual_elements["locations"])] if i < len(visual_elements["locations"]) else visual_elements["locations"][0]
                components.append(f"setting: {loc}")
            
            # Time/atmosphere
            if visual_elements["time_of_day"]:
                components.append(visual_elements["time_of_day"][0] + " lighting")
            if visual_elements["atmosphere"]:
                components.append(visual_elements["atmosphere"][0] + " atmosphere")
            
            # Content from text
            # Extract key phrases (simplified - in production, use NLP)
            key_phrase = snippet[:100].strip()
            if key_phrase:
                components.append(f"depicting: {key_phrase}")
            
            # Character reference if available
            scene_characters = [c["name"] for c in characters if c["name"].lower() in text.lower()][:3]
            if scene_characters:
                components.append(f"featuring: {', '.join(scene_characters)}")
            
            # Style modifiers
            components.append(style_mod)
            components.append(quality_mod)
            
            # Custom style
            if custom_style:
                components.append(custom_style)
            
            prompt_text = ", ".join(components)
            
            prompts.append({
                "prompt": prompt_text,
                "scene_idx": scene_idx,
                "shot_idx": i,
                "shot_type": shot_type,
                "id": f"scene_{scene_idx+1:03d}_shot_{i+1:02d}",
                "negative_prompt": "blurry, low quality, distorted, deformed, ugly, bad anatomy, watermark, text, signature"
            })
        
        return prompts
    
    # ============== Narration Processing ==============
    
    def _process_narration(self, scene_text: str, scene_idx: int) -> Dict[str, Any]:
        """Process scene text into narration-ready format."""
        # Clean up the text for TTS
        narration = scene_text.strip()
        
        # Remove markdown/formatting artifacts
        narration = re.sub(r'\*\*(.+?)\*\*', r'\1', narration)  # Bold
        narration = re.sub(r'\*(.+?)\*', r'\1', narration)      # Italic
        narration = re.sub(r'#{1,6}\s*', '', narration)          # Headers
        narration = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', narration)  # Links
        
        # Normalize whitespace
        narration = re.sub(r'\n{3,}', '\n\n', narration)
        narration = re.sub(r' {2,}', ' ', narration)
        
        # Estimate duration (average reading speed: ~150 words per minute)
        word_count = len(narration.split())
        estimated_duration_seconds = (word_count / 150) * 60
        
        # Detect dialogue vs narration ratio
        dialogue_pattern = r'["""].*?["""]|\'.*?\''
        dialogue_matches = re.findall(dialogue_pattern, narration)
        dialogue_word_count = sum(len(d.split()) for d in dialogue_matches)
        dialogue_ratio = dialogue_word_count / max(word_count, 1)
        
        return {
            "text": narration,
            "scene_idx": scene_idx,
            "id": f"narration_scene_{scene_idx+1:03d}",
            "word_count": word_count,
            "estimated_duration_seconds": round(estimated_duration_seconds, 1),
            "dialogue_ratio": round(dialogue_ratio, 2),
            "has_dialogue": dialogue_ratio > 0.3
        }
    
    # ============== SFX Cue Generation ==============
    
    SFX_KEYWORDS = {
        # Weather & Nature
        "rain": ["rain ambience, water drops, wet surface", "light rain, gentle patter"],
        "storm": ["thunderstorm, heavy rain, thunder rumble", "storm ambience, wind howling"],
        "thunder": ["thunder crack, distant rumble, lightning"],
        "wind": ["wind blowing, air movement, breeze"],
        "snow": ["snow falling, winter ambience, soft crunch"],
        
        # Environment
        "forest": ["forest ambience, birds chirping, leaves rustling, nature sounds"],
        "ocean": ["ocean waves, seashore, water splashing, seagulls"],
        "river": ["flowing water, stream, river ambience"],
        "city": ["city ambience, traffic, distant sirens, urban soundscape"],
        "crowd": ["crowd murmur, people talking, busy atmosphere"],
        "market": ["marketplace bustle, vendors calling, busy crowd"],
        
        # Interior
        "fire": ["crackling fire, fireplace, warm flames"],
        "door": ["door opening, door closing, wooden creak"],
        "footsteps": ["footsteps, walking sounds"],
        "clock": ["clock ticking, time passing"],
        
        # Action
        "battle": ["battle sounds, swords clashing, combat"],
        "fight": ["fighting sounds, punches, impacts"],
        "sword": ["sword slash, metal clang, blade ring"],
        "gun": ["gunshot, weapon fire"],
        "explosion": ["explosion, blast, debris"],
        "running": ["running footsteps, rapid movement"],
        "chase": ["chase music tension, running, pursuit"],
        
        # Emotional
        "crying": ["soft crying, emotional moment, tears"],
        "laughing": ["laughter, joyful sounds"],
        "scream": ["scream, shout, alarmed voice"],
        "whisper": ["whispered voices, quiet conversation"],
        
        # Animals
        "horse": ["horse galloping, hooves, neigh"],
        "dog": ["dog barking, animal sounds"],
        "bird": ["birds chirping, bird calls"],
        "wolf": ["wolf howl, wild animal"],
        
        # Time of day
        "morning": ["morning ambience, birds, sunrise atmosphere"],
        "night": ["night ambience, crickets, owl, darkness"],
        "dawn": ["dawn sounds, early morning, quiet awakening"],
        "dusk": ["evening ambience, sunset sounds"]
    }
    
    def _generate_sfx_cues(self, scene_text: str, scene_idx: int) -> Dict[str, Any]:
        """Generate SFX cues based on scene content analysis."""
        text_lower = scene_text.lower()
        
        detected_cues = []
        cue_categories = {}
        
        for keyword, sfx_options in self.SFX_KEYWORDS.items():
            if keyword in text_lower:
                # Count occurrences for priority
                count = text_lower.count(keyword)
                category = self._categorize_sfx(keyword)
                
                if category not in cue_categories:
                    cue_categories[category] = []
                
                cue_categories[category].append({
                    "keyword": keyword,
                    "sfx_prompts": sfx_options,
                    "priority": count,
                    "primary_prompt": sfx_options[0]
                })
        
        # Build final cue list with priorities
        for category, cues in cue_categories.items():
            # Sort by priority and take top 2 per category
            sorted_cues = sorted(cues, key=lambda x: -x["priority"])[:2]
            detected_cues.extend(sorted_cues)
        
        # Add default ambient if nothing detected
        if not detected_cues:
            detected_cues.append({
                "keyword": "ambient",
                "sfx_prompts": ["subtle room tone", "quiet background ambience"],
                "priority": 1,
                "primary_prompt": "subtle room tone ambience"
            })
        
        # Generate combined SFX prompt for MMAudio
        combined_prompt = ", ".join([c["primary_prompt"] for c in detected_cues[:5]])
        
        return {
            "cues": detected_cues,
            "combined_prompt": combined_prompt,
            "scene_idx": scene_idx,
            "id": f"sfx_scene_{scene_idx+1:03d}",
            "cue_count": len(detected_cues)
        }
    
    def _categorize_sfx(self, keyword: str) -> str:
        """Categorize SFX keyword."""
        categories = {
            "weather": ["rain", "storm", "thunder", "wind", "snow"],
            "nature": ["forest", "ocean", "river", "bird", "wolf"],
            "urban": ["city", "crowd", "market", "traffic"],
            "action": ["battle", "fight", "sword", "gun", "explosion", "running", "chase"],
            "interior": ["fire", "door", "footsteps", "clock"],
            "emotional": ["crying", "laughing", "scream", "whisper"],
            "time": ["morning", "night", "dawn", "dusk"]
        }
        
        for cat, keywords in categories.items():
            if keyword in keywords:
                return cat
        return "other"
    
    # ============== Main Processing Function ==============
    
    def process_novel(
        self,
        novel_text: str,
        max_scene_chars: int,
        broll_density: int,
        image_engine: str,
        image_style: str,
        character_profile: str,
        voice_mode: str,
        parallax_enabled: bool,
        sfx_mode: str,
        voice_reference_audio: Optional[Any] = None,
        character_reference_images: Optional[Any] = None,
        custom_style_prompt: str = "",
        scene_transition_style: str = "fade",
        target_video_fps: int = 24,
        target_resolution: str = "1920x1080"
    ) -> Tuple[str, str, str, str, str, str, str]:
        """
        Main processing function that orchestrates the entire novel analysis.
        """
        
        # Validate input
        if not novel_text or not novel_text.strip():
            empty_result = json.dumps([], ensure_ascii=False)
            return (empty_result, empty_result, empty_result, empty_result, 
                    empty_result, "{}", "Error: No novel text provided.")
        
        # 1. Extract characters from the entire text
        characters = self._extract_characters(novel_text)
        
        # 2. Split novel into scenes
        scenes = self._chunk_scenes(novel_text, max_scene_chars)
        
        # 3. Process each scene
        all_scenes = []
        all_image_prompts = []
        all_narration = []
        all_sfx_cues = []
        
        total_duration = 0
        total_shots = 0
        
        for idx, scene in enumerate(scenes):
            # Generate image prompts
            scene_prompts = self._generate_image_prompts(
                scene, idx, broll_density, image_style, 
                image_engine, custom_style_prompt, characters
            )
            all_image_prompts.append(scene_prompts)
            total_shots += len(scene_prompts)
            
            # Process narration
            narration = self._process_narration(scene["text"], idx)
            all_narration.append(narration)
            total_duration += narration["estimated_duration_seconds"]
            
            # Generate SFX cues
            sfx = self._generate_sfx_cues(scene["text"], idx)
            all_sfx_cues.append(sfx)
            
            # Store scene metadata
            all_scenes.append({
                "id": scene["id"],
                "index": idx,
                "text": scene["text"],
                "char_count": scene["char_count"],
                "para_count": scene.get("para_count", 1),
                "shot_count": len(scene_prompts),
                "duration_estimate": narration["estimated_duration_seconds"]
            })
        
        # 4. Build configuration object
        config = {
            "image_engine": image_engine,
            "image_style": image_style,
            "character_profile": character_profile,
            "voice_mode": voice_mode,
            "parallax_enabled": parallax_enabled,
            "sfx_mode": sfx_mode,
            "broll_density": broll_density,
            "num_scenes": len(scenes),
            "total_shots": total_shots,
            "estimated_duration_seconds": round(total_duration, 1),
            "estimated_duration_formatted": self._format_duration(total_duration),
            "scene_transition_style": scene_transition_style,
            "target_video_fps": target_video_fps,
            "target_resolution": target_resolution,
            "has_voice_reference": voice_reference_audio is not None,
            "has_character_reference": character_reference_images is not None,
            "custom_style_prompt": custom_style_prompt
        }
        
        # 5. Generate summary
        summary = self._generate_summary(
            len(scenes), total_shots, total_duration, 
            len(characters), config
        )
        
        # 6. JSON encode everything
        scenes_json = json.dumps(
            [{"id": s["id"], "index": s["index"], "text": s["text"]} for s in all_scenes],
            ensure_ascii=False, indent=2
        )
        image_prompts_json = json.dumps(all_image_prompts, ensure_ascii=False, indent=2)
        narration_json = json.dumps(all_narration, ensure_ascii=False, indent=2)
        sfx_json = json.dumps(all_sfx_cues, ensure_ascii=False, indent=2)
        characters_json = json.dumps(characters, ensure_ascii=False, indent=2)
        config_json = json.dumps(config, ensure_ascii=False, indent=2)
        
        return (
            scenes_json,
            image_prompts_json,
            narration_json,
            sfx_json,
            characters_json,
            config_json,
            summary
        )
    
    def _format_duration(self, seconds: float) -> str:
        """Format seconds into human-readable duration."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        if minutes > 60:
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours}h {mins}m {secs}s"
        return f"{minutes}m {secs}s"
    
    def _generate_summary(self, num_scenes: int, num_shots: int, 
                          duration: float, num_characters: int,
                          config: Dict) -> str:
        """Generate a human-readable summary of the production plan."""
        duration_str = self._format_duration(duration)
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║              📖 NOVEL CINEMATIC PRODUCTION PLAN              ║
╠══════════════════════════════════════════════════════════════╣
║  📊 CONTENT ANALYSIS                                         ║
║  ├─ Scenes: {num_scenes:>4}                                          ║
║  ├─ Total Shots: {num_shots:>4}                                      ║
║  ├─ Characters Detected: {num_characters:>4}                               ║
║  └─ Estimated Duration: {duration_str:>10}                       ║
╠══════════════════════════════════════════════════════════════╣
║  🎨 VISUAL SETTINGS                                          ║
║  ├─ Image Engine: {config['image_engine']:<15}                       ║
║  ├─ Style: {config['image_style']:<20}                        ║
║  ├─ Resolution: {config['target_resolution']:<15}                    ║
║  └─ 3D Parallax: {'Enabled' if config['parallax_enabled'] else 'Disabled':<15}                       ║
╠══════════════════════════════════════════════════════════════╣
║  🎤 AUDIO SETTINGS                                           ║
║  ├─ Voice Mode: {config['voice_mode']:<20}                    ║
║  ├─ SFX Mode: {config['sfx_mode']:<20}                        ║
║  └─ Voice Reference: {'Yes' if config['has_voice_reference'] else 'No':<10}                       ║
╠══════════════════════════════════════════════════════════════╣
║  🎬 VIDEO SETTINGS                                           ║
║  ├─ FPS: {config['target_video_fps']:>3}                                             ║
║  ├─ Transitions: {config['scene_transition_style']:<15}                      ║
║  └─ B-Roll Density: {config['broll_density']:>2} shots/scene                       ║
╚══════════════════════════════════════════════════════════════╝

✅ Ready for pipeline execution!
Connect outputs to:
  • Image Prompts → Flux/SDXL/SD Sampler
  • Narration → IndexTTS/Voice Clone Node  
  • SFX Cues → MMAudio/StableAudio Node
  • Config → Pipeline Controller
"""
        return summary.strip()
