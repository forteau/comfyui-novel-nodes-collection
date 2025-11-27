"""
Novel Cinematic Orchestrator - Enhanced Image Coverage
=======================================================
Improved image generation with better story coverage analysis
and adaptive density based on content.
"""

import json
import re
import math
from typing import List, Dict, Tuple, Any, Optional


class ImageCoverageCalculator:
    """
    Calculates optimal image settings for complete story coverage.
    """
    
    DESCRIPTION = """
    🎯 Image Coverage Calculator
    
    Calculates how many images you need for proper story coverage
    and recommends optimal settings.
    
    Target: 1 new image every 5-10 seconds of narration
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "word_count": ("INT", {
                    "default": 50000,
                    "min": 100,
                    "max": 500000
                }),
                "target_image_interval_seconds": ("FLOAT", {
                    "default": 8.0,
                    "min": 3.0,
                    "max": 30.0,
                    "step": 0.5,
                    "tooltip": "How often to show a new image (seconds)"
                }),
                "narration_speed_wpm": ("INT", {
                    "default": 150,
                    "min": 100,
                    "max": 200,
                    "tooltip": "Words per minute for TTS narration"
                }),
                "parallax_duration_per_image": ("FLOAT", {
                    "default": 4.0,
                    "min": 2.0,
                    "max": 15.0,
                    "step": 0.5,
                    "tooltip": "How long each parallax animation lasts"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "INT", "INT", "FLOAT", "STRING")
    RETURN_NAMES = (
        "analysis_text",
        "total_images_needed",
        "recommended_broll_density",
        "recommended_scene_chars",
        "estimated_video_hours",
        "settings_json"
    )
    FUNCTION = "calculate_coverage"
    CATEGORY = "🎬 Story Tools/Planning"

    def calculate_coverage(self, word_count: int, target_image_interval_seconds: float,
                          narration_speed_wpm: int, 
                          parallax_duration_per_image: float) -> Tuple[str, int, int, int, float, str]:
        
        # Calculate narration duration
        narration_minutes = word_count / narration_speed_wpm
        narration_seconds = narration_minutes * 60
        narration_hours = narration_minutes / 60
        
        # Calculate images needed for target interval
        images_needed = math.ceil(narration_seconds / target_image_interval_seconds)
        
        # Calculate optimal scene settings
        # Assume average 5 chars per word
        total_chars = word_count * 5
        
        # Try different combinations to find optimal
        best_config = None
        best_diff = float('inf')
        
        for scene_chars in range(1000, 5001, 250):
            num_scenes = max(1, total_chars // scene_chars)
            for density in range(4, 25):
                total_images = num_scenes * density
                diff = abs(total_images - images_needed)
                if diff < best_diff:
                    best_diff = diff
                    best_config = {
                        "scene_chars": scene_chars,
                        "broll_density": density,
                        "num_scenes": num_scenes,
                        "total_images": total_images
                    }
        
        # Ensure we have a config
        if best_config is None:
            num_scenes = max(1, total_chars // 2000)
            best_config = {
                "scene_chars": 2000,
                "broll_density": max(4, images_needed // num_scenes),
                "num_scenes": num_scenes,
                "total_images": images_needed
            }
        
        # Calculate actual coverage with recommended settings
        actual_interval = narration_seconds / best_config["total_images"]
        
        # Video duration estimate (accounting for parallax)
        video_seconds = max(narration_seconds, best_config["total_images"] * parallax_duration_per_image)
        video_hours = video_seconds / 3600
        
        # Format analysis
        analysis = f"""
╔══════════════════════════════════════════════════════════════════╗
║                  🎯 IMAGE COVERAGE ANALYSIS                       ║
╠══════════════════════════════════════════════════════════════════╣
║  📖 NOVEL STATS                                                   ║
║  ├─ Word Count:           {word_count:>12,}                        ║
║  ├─ Narration Duration:   {narration_hours:>10.1f} hours                    ║
║  └─ Narration Speed:      {narration_speed_wpm:>10} wpm                      ║
╠══════════════════════════════════════════════════════════════════╣
║  🎯 TARGET COVERAGE                                               ║
║  ├─ Target Interval:      {target_image_interval_seconds:>10.1f} seconds                  ║
║  ├─ Images Needed:        {images_needed:>12,}                        ║
║  └─ Quality Level:        {"Cinematic" if target_image_interval_seconds <= 8 else "Standard":>12}                        ║
╠══════════════════════════════════════════════════════════════════╣
║  ⚙️  RECOMMENDED SETTINGS                                         ║
║  ├─ max_scene_chars:      {best_config["scene_chars"]:>12,}                        ║
║  ├─ broll_density:        {best_config["broll_density"]:>12}                        ║
║  ├─ Resulting Scenes:     {best_config["num_scenes"]:>12,}                        ║
║  └─ Total Images:         {best_config["total_images"]:>12,}                        ║
╠══════════════════════════════════════════════════════════════════╣
║  📊 ACTUAL COVERAGE                                               ║
║  ├─ Image Interval:       {actual_interval:>10.1f} seconds                  ║
║  ├─ Coverage Quality:     {self._rate_coverage(actual_interval):>12}                        ║
║  └─ Est. Video Length:    {video_hours:>10.1f} hours                    ║
╠══════════════════════════════════════════════════════════════════╣
║  💾 GENERATION ESTIMATE                                           ║
║  ├─ At 10 sec/image:      {(best_config["total_images"] * 10 / 3600):>10.1f} hours                    ║
║  ├─ At 30 sec/image:      {(best_config["total_images"] * 30 / 3600):>10.1f} hours                    ║
║  └─ VRAM (batch=4):       ~{max(8, best_config["broll_density"] * 2):>7} GB                        ║
╚══════════════════════════════════════════════════════════════════╝
"""
        
        settings = {
            "word_count": word_count,
            "narration_hours": round(narration_hours, 2),
            "images_needed": images_needed,
            "recommended_scene_chars": best_config["scene_chars"],
            "recommended_broll_density": best_config["broll_density"],
            "expected_scenes": best_config["num_scenes"],
            "expected_total_images": best_config["total_images"],
            "actual_image_interval": round(actual_interval, 1),
            "estimated_video_hours": round(video_hours, 2)
        }
        
        return (
            analysis.strip(),
            images_needed,
            best_config["broll_density"],
            best_config["scene_chars"],
            round(video_hours, 2),
            json.dumps(settings, indent=2)
        )
    
    def _rate_coverage(self, interval: float) -> str:
        if interval <= 5:
            return "Excellent"
        elif interval <= 8:
            return "Cinematic"
        elif interval <= 12:
            return "Good"
        elif interval <= 20:
            return "Standard"
        else:
            return "Sparse"


class AdaptiveDensityOrchestrator:
    """
    An orchestrator that adapts image density based on scene content.
    Action scenes get more images, quiet scenes get fewer.
    """
    
    DESCRIPTION = """
    📖 Adaptive Density Orchestrator
    
    Intelligently varies image density based on scene content:
    • Action scenes → More images (faster cuts)
    • Dialogue scenes → Moderate images
    • Descriptive scenes → Fewer images (longer holds)
    
    Results in more accurate story representation.
    """

    # Keywords that indicate different pacing needs
    ACTION_KEYWORDS = [
        'fight', 'battle', 'ran', 'running', 'chase', 'attacked', 'explosion',
        'sword', 'gun', 'punch', 'kick', 'dodge', 'jump', 'fell', 'crash',
        'scream', 'shout', 'quick', 'fast', 'sudden', 'burst', 'race'
    ]
    
    DIALOGUE_KEYWORDS = [
        'said', 'asked', 'replied', 'whispered', 'shouted', 'muttered',
        'spoke', 'told', 'answered', 'exclaimed', 'murmured', 'stammered'
    ]
    
    DESCRIPTIVE_KEYWORDS = [
        'beautiful', 'ancient', 'vast', 'silent', 'peaceful', 'serene',
        'landscape', 'horizon', 'sky', 'mountain', 'forest', 'ocean',
        'slowly', 'gently', 'quietly', 'calmly'
    ]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "novel_text": ("STRING", {"multiline": True}),
                "base_density": ("INT", {
                    "default": 6,
                    "min": 2,
                    "max": 12,
                    "tooltip": "Base images per scene (adjusted by content)"
                }),
                "max_scene_chars": ("INT", {
                    "default": 2000,
                    "min": 500,
                    "max": 8000
                }),
                "image_engine": (["flux", "sdxl", "sd15", "cascade", "pixart"],),
                "image_style": (["cinematic", "anime", "realistic", "painterly", "comic", "storyboard"],),
                "action_multiplier": ("FLOAT", {
                    "default": 1.5,
                    "min": 1.0,
                    "max": 3.0,
                    "step": 0.1,
                    "tooltip": "Multiply density for action scenes"
                }),
                "dialogue_multiplier": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.5,
                    "max": 2.0,
                    "step": 0.1
                }),
                "descriptive_multiplier": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.3,
                    "max": 1.5,
                    "step": 0.1,
                    "tooltip": "Reduce density for slow descriptive scenes"
                }),
            },
            "optional": {
                "character_profile": ("STRING", {"default": ""}),
                "custom_style_prompt": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "scenes_json",
        "image_prompts_json",
        "narration_json",
        "sfx_cues_json",
        "config_json",
        "density_analysis",
        "summary_text"
    )
    FUNCTION = "process_novel"
    CATEGORY = "🎬 Story Tools/Orchestration"

    def process_novel(
        self,
        novel_text: str,
        base_density: int,
        max_scene_chars: int,
        image_engine: str,
        image_style: str,
        action_multiplier: float,
        dialogue_multiplier: float,
        descriptive_multiplier: float,
        character_profile: str = "",
        custom_style_prompt: str = ""
    ) -> Tuple[str, str, str, str, str, str, str]:
        
        if not novel_text.strip():
            empty = json.dumps([])
            return (empty, empty, empty, empty, "{}", "", "No text provided")
        
        # Split into scenes
        scenes = self._split_scenes(novel_text, max_scene_chars)
        
        all_scenes = []
        all_prompts = []
        all_narration = []
        all_sfx = []
        density_info = []
        
        total_images = 0
        
        for idx, scene_text in enumerate(scenes):
            # Analyze scene content
            scene_type, density = self._analyze_scene(
                scene_text, base_density,
                action_multiplier, dialogue_multiplier, descriptive_multiplier
            )
            
            density_info.append({
                "scene": idx + 1,
                "type": scene_type,
                "density": density,
                "words": len(scene_text.split())
            })
            
            # Generate prompts with adaptive density
            prompts = self._generate_prompts(
                scene_text, idx, density, image_style, image_engine, custom_style_prompt
            )
            total_images += len(prompts)
            
            # Process narration
            narration = self._process_narration(scene_text, idx)
            
            # Generate SFX
            sfx = self._generate_sfx(scene_text, idx)
            
            all_scenes.append({
                "id": f"scene_{idx+1:03d}",
                "index": idx,
                "text": scene_text,
                "type": scene_type,
                "image_count": len(prompts)
            })
            all_prompts.append(prompts)
            all_narration.append(narration)
            all_sfx.append(sfx)
        
        # Build config
        config = {
            "image_engine": image_engine,
            "image_style": image_style,
            "base_density": base_density,
            "adaptive_density": True,
            "total_scenes": len(scenes),
            "total_images": total_images,
            "character_profile": character_profile
        }
        
        # Density analysis
        action_scenes = len([d for d in density_info if d["type"] == "action"])
        dialogue_scenes = len([d for d in density_info if d["type"] == "dialogue"])
        descriptive_scenes = len([d for d in density_info if d["type"] == "descriptive"])
        mixed_scenes = len([d for d in density_info if d["type"] == "mixed"])
        
        density_analysis = f"""
╔══════════════════════════════════════════════════════════════╗
║              📊 ADAPTIVE DENSITY ANALYSIS                     ║
╠══════════════════════════════════════════════════════════════╣
║  Scene Types Detected:                                        ║
║  ├─ ⚔️  Action:      {action_scenes:>4} scenes (density × {action_multiplier})          ║
║  ├─ 💬 Dialogue:    {dialogue_scenes:>4} scenes (density × {dialogue_multiplier})          ║
║  ├─ 🏞️  Descriptive: {descriptive_scenes:>4} scenes (density × {descriptive_multiplier})          ║
║  └─ 🔀 Mixed:       {mixed_scenes:>4} scenes (base density)            ║
╠══════════════════════════════════════════════════════════════╣
║  Image Distribution:                                          ║
║  ├─ Total Scenes:     {len(scenes):>6}                                  ║
║  ├─ Total Images:     {total_images:>6}                                  ║
║  ├─ Avg per Scene:    {total_images/max(len(scenes),1):>6.1f}                                  ║
║  └─ Base Density:     {base_density:>6}                                  ║
╚══════════════════════════════════════════════════════════════╝
"""
        
        # Summary
        word_count = len(novel_text.split())
        duration_min = word_count / 150
        
        summary = f"""
📖 Processed {word_count:,} words into {len(scenes)} scenes
🖼️ Generated {total_images:,} image prompts (adaptive density)
⏱️ Estimated duration: {duration_min:.0f} minutes
📊 Avg image interval: {(duration_min * 60) / total_images:.1f} seconds
"""
        
        return (
            json.dumps(all_scenes, ensure_ascii=False, indent=2),
            json.dumps(all_prompts, ensure_ascii=False, indent=2),
            json.dumps(all_narration, ensure_ascii=False, indent=2),
            json.dumps(all_sfx, ensure_ascii=False, indent=2),
            json.dumps(config, ensure_ascii=False, indent=2),
            density_analysis.strip(),
            summary.strip()
        )
    
    def _split_scenes(self, text: str, max_chars: int) -> List[str]:
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        scenes = []
        current = ""
        
        for p in paragraphs:
            if len(current) + len(p) + 2 > max_chars and current:
                scenes.append(current.strip())
                current = p
            else:
                current = current + "\n\n" + p if current else p
        
        if current:
            scenes.append(current.strip())
        
        return scenes
    
    def _analyze_scene(self, text: str, base_density: int,
                       action_mult: float, dialogue_mult: float, 
                       desc_mult: float) -> Tuple[str, int]:
        """Analyze scene and return type + adjusted density."""
        text_lower = text.lower()
        
        # Count keyword occurrences
        action_score = sum(1 for kw in self.ACTION_KEYWORDS if kw in text_lower)
        dialogue_score = sum(1 for kw in self.DIALOGUE_KEYWORDS if kw in text_lower)
        desc_score = sum(1 for kw in self.DESCRIPTIVE_KEYWORDS if kw in text_lower)
        
        # Determine dominant type
        scores = {
            "action": action_score,
            "dialogue": dialogue_score,
            "descriptive": desc_score
        }
        
        max_score = max(scores.values())
        
        if max_score < 2:
            scene_type = "mixed"
            multiplier = 1.0
        elif action_score == max_score:
            scene_type = "action"
            multiplier = action_mult
        elif dialogue_score == max_score:
            scene_type = "dialogue"
            multiplier = dialogue_mult
        else:
            scene_type = "descriptive"
            multiplier = desc_mult
        
        # Calculate density
        density = max(2, min(24, int(base_density * multiplier)))
        
        return scene_type, density
    
    def _generate_prompts(self, scene: str, idx: int, density: int,
                          style: str, engine: str, custom: str) -> List[Dict]:
        """Generate prompts for a scene."""
        styles = {
            "cinematic": "cinematic film still, dramatic lighting, shallow depth of field",
            "anime": "anime art style, vibrant colors, detailed linework",
            "realistic": "photorealistic, natural lighting, hyperdetailed",
            "painterly": "oil painting style, artistic brushstrokes",
            "comic": "comic book art, bold lines, dynamic composition",
            "storyboard": "storyboard frame, concept art, key frame"
        }
        
        quality = {
            "flux": "masterpiece, best quality, highly detailed",
            "sdxl": "masterpiece, best quality, ultra detailed, 8k",
            "sd15": "best quality, highly detailed, sharp focus",
            "cascade": "high quality, detailed, professional",
            "pixart": "high quality artwork, detailed, aesthetic"
        }
        
        flat = " ".join(scene.split())
        chunk_size = max(len(flat) // density, 30)
        
        prompts = []
        shot_types = [
            "establishing wide shot", "medium shot", "close-up", "over-the-shoulder",
            "POV shot", "detail shot", "two-shot", "reaction shot",
            "tracking shot", "low angle", "high angle", "dutch angle"
        ]
        
        for i in range(density):
            start = i * chunk_size
            snippet = flat[start:start + chunk_size][:80]
            
            if not snippet:
                break
            
            shot = shot_types[i % len(shot_types)]
            
            prompt_parts = [
                f"Scene {idx + 1}, Shot {i + 1}",
                shot,
                styles.get(style, styles["cinematic"]),
                f"depicting: {snippet}",
                quality.get(engine, quality["flux"])
            ]
            
            if custom:
                prompt_parts.append(custom)
            
            prompts.append({
                "prompt": ", ".join(prompt_parts),
                "negative_prompt": "blurry, low quality, distorted, deformed, text, watermark",
                "scene_idx": idx,
                "shot_idx": i,
                "shot_type": shot,
                "id": f"scene_{idx+1:03d}_shot_{i+1:02d}"
            })
        
        return prompts
    
    def _process_narration(self, scene: str, idx: int) -> Dict:
        word_count = len(scene.split())
        return {
            "text": scene,
            "scene_idx": idx,
            "word_count": word_count,
            "estimated_duration_seconds": (word_count / 150) * 60,
            "id": f"narration_{idx+1:03d}"
        }
    
    def _generate_sfx(self, scene: str, idx: int) -> Dict:
        scene_lower = scene.lower()
        cues = []
        
        sfx_map = {
            "forest": "forest ambience, birds, rustling leaves",
            "rain": "rain sounds, thunder, water drops",
            "battle": "combat sounds, metal clashing, impacts",
            "city": "urban ambience, traffic, crowd murmur",
            "ocean": "waves crashing, seashore, seagulls",
            "fire": "crackling flames, fire ambience",
            "night": "night ambience, crickets, owl",
            "wind": "wind blowing, air movement"
        }
        
        for kw, sfx in sfx_map.items():
            if kw in scene_lower:
                cues.append({"keyword": kw, "prompt": sfx})
        
        if not cues:
            cues.append({"keyword": "ambient", "prompt": "subtle room tone"})
        
        return {
            "cues": cues,
            "combined_prompt": ", ".join(c["prompt"] for c in cues[:3]),
            "scene_idx": idx
        }


class KeyMomentExtractor:
    """
    Extracts key story moments that MUST have images.
    Ensures important plot points are visually represented.
    """
    
    DESCRIPTION = """
    🎯 Key Moment Extractor
    
    Identifies critical story moments that must have visual representation:
    • Character introductions
    • Major plot points
    • Emotional peaks
    • Scene transitions
    • Climactic moments
    
    Ensures these moments get dedicated image prompts.
    """

    # Patterns that indicate important moments
    IMPORTANCE_PATTERNS = [
        (r'\bfor the first time\b', 'first_encounter', 1.5),
        (r'\bsuddenly\b', 'sudden_event', 1.3),
        (r'\brealized\b', 'realization', 1.2),
        (r'\bdiscovered\b', 'discovery', 1.4),
        (r'\bfinally\b', 'culmination', 1.3),
        (r'\bnever before\b', 'unique_event', 1.4),
        (r'\bchanged everything\b', 'turning_point', 1.5),
        (r'\blast\b.*\btime\b', 'finality', 1.3),
        (r'\bdeath\b|\bdied\b|\bkilled\b', 'death', 1.5),
        (r'\blove\b|\bkiss\b|\bembrace\b', 'romance', 1.3),
        (r'\bwar\b|\bbattle\b|\bfight\b', 'conflict', 1.4),
        (r'\bvictory\b|\bwon\b|\btriumph\b', 'victory', 1.4),
        (r'\bdefeat\b|\blost\b|\bfailed\b', 'defeat', 1.3),
        (r'\bsecret\b|\bhidden\b|\brevealed\b', 'revelation', 1.3),
    ]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "novel_text": ("STRING", {"multiline": True}),
                "importance_threshold": ("FLOAT", {
                    "default": 1.3,
                    "min": 1.0,
                    "max": 2.0,
                    "step": 0.1,
                    "tooltip": "Minimum importance score to flag as key moment"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("key_moments_json", "analysis_text", "key_moment_count")
    FUNCTION = "extract_moments"
    CATEGORY = "🎬 Story Tools/Planning"

    def extract_moments(self, novel_text: str, 
                        importance_threshold: float) -> Tuple[str, str, int]:
        
        if not novel_text.strip():
            return ("[]", "No text provided", 0)
        
        # Split into paragraphs for analysis
        paragraphs = [p.strip() for p in novel_text.split('\n\n') if p.strip()]
        
        key_moments = []
        
        for para_idx, para in enumerate(paragraphs):
            para_lower = para.lower()
            moment_types = []
            importance = 1.0
            
            for pattern, moment_type, weight in self.IMPORTANCE_PATTERNS:
                if re.search(pattern, para_lower):
                    moment_types.append(moment_type)
                    importance = max(importance, weight)
            
            if importance >= importance_threshold:
                # Extract a snippet for the image prompt
                sentences = re.split(r'(?<=[.!?])\s+', para)
                key_sentence = sentences[0] if sentences else para[:200]
                
                key_moments.append({
                    "paragraph_index": para_idx,
                    "importance": round(importance, 2),
                    "moment_types": moment_types,
                    "text_snippet": key_sentence[:200],
                    "full_paragraph": para,
                    "suggested_prompt": f"Key moment: {', '.join(moment_types)}, {key_sentence[:100]}"
                })
        
        # Sort by importance
        key_moments.sort(key=lambda x: -x["importance"])
        
        # Analysis text
        type_counts = {}
        for km in key_moments:
            for mt in km["moment_types"]:
                type_counts[mt] = type_counts.get(mt, 0) + 1
        
        type_summary = "\n".join([f"  • {t}: {c}" for t, c in sorted(type_counts.items(), key=lambda x: -x[1])[:10]])
        
        analysis = f"""
╔══════════════════════════════════════════════════════════════╗
║              🎯 KEY MOMENT ANALYSIS                           ║
╠══════════════════════════════════════════════════════════════╣
║  Total Paragraphs:    {len(paragraphs):>6}                                  ║
║  Key Moments Found:   {len(key_moments):>6}                                  ║
║  Coverage:            {(len(key_moments)/max(len(paragraphs),1)*100):>5.1f}%                                 ║
╠══════════════════════════════════════════════════════════════╣
║  Moment Types:                                                ║
{type_summary}
╚══════════════════════════════════════════════════════════════╝

These {len(key_moments)} paragraphs contain critical story moments
that should have dedicated, high-quality image prompts.
"""
        
        return (
            json.dumps(key_moments, ensure_ascii=False, indent=2),
            analysis.strip(),
            len(key_moments)
        )


class EnhancedPromptGenerator:
    """
    Generates more detailed, story-accurate image prompts.
    """
    
    DESCRIPTION = """
    🎨 Enhanced Prompt Generator
    
    Creates more detailed prompts by:
    • Extracting specific visual details from text
    • Identifying characters in scene
    • Detecting time of day, weather, mood
    • Building layered, comprehensive prompts
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "scene_text": ("STRING", {"multiline": True}),
                "scene_index": ("INT", {"default": 0}),
                "num_prompts": ("INT", {
                    "default": 6,
                    "min": 1,
                    "max": 24
                }),
                "style": (["cinematic", "anime", "realistic", "painterly", "comic"],),
                "include_characters": ("BOOLEAN", {"default": True}),
                "include_environment": ("BOOLEAN", {"default": True}),
                "include_mood": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "character_descriptions": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "Elena: young woman, dark hair, green eyes\nMarcus: tall man, grey beard, blue cloak"
                }),
                "style_keywords": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompts_json", "extraction_summary")
    FUNCTION = "generate_prompts"
    CATEGORY = "🎬 Story Tools/Generation"

    def generate_prompts(
        self,
        scene_text: str,
        scene_index: int,
        num_prompts: int,
        style: str,
        include_characters: bool,
        include_environment: bool,
        include_mood: bool,
        character_descriptions: str = "",
        style_keywords: str = ""
    ) -> Tuple[str, str]:
        
        if not scene_text.strip():
            return ("[]", "No text provided")
        
        # Extract visual elements
        extraction = self._extract_all_elements(scene_text)
        
        # Parse character descriptions
        char_desc_map = {}
        if character_descriptions:
            for line in character_descriptions.split('\n'):
                if ':' in line:
                    name, desc = line.split(':', 1)
                    char_desc_map[name.strip().lower()] = desc.strip()
        
        # Style templates
        styles = {
            "cinematic": "cinematic film still, dramatic lighting, shallow depth of field, professional cinematography",
            "anime": "anime art style, vibrant colors, detailed linework, studio quality",
            "realistic": "photorealistic, hyperdetailed, natural lighting, 8K",
            "painterly": "oil painting style, rich textures, artistic brushstrokes",
            "comic": "comic book art, bold lines, dynamic composition"
        }
        
        # Generate prompts
        prompts = []
        flat_text = " ".join(scene_text.split())
        chunk_size = max(len(flat_text) // num_prompts, 50)
        
        shot_types = [
            "establishing shot", "medium shot", "close-up", "wide shot",
            "detail shot", "two-shot", "reaction shot", "POV shot"
        ]
        
        for i in range(num_prompts):
            snippet = flat_text[i * chunk_size:(i + 1) * chunk_size][:100]
            if not snippet:
                break
            
            prompt_parts = []
            
            # Shot type
            shot = shot_types[i % len(shot_types)]
            prompt_parts.append(f"Scene {scene_index + 1}, Shot {i + 1}, {shot}")
            
            # Style
            prompt_parts.append(styles.get(style, styles["cinematic"]))
            
            # Environment
            if include_environment and extraction["locations"]:
                loc = extraction["locations"][i % len(extraction["locations"])]
                prompt_parts.append(f"setting: {loc}")
            
            # Time/weather
            if extraction["time_of_day"]:
                prompt_parts.append(f"{extraction['time_of_day'][0]} lighting")
            if extraction["weather"]:
                prompt_parts.append(extraction["weather"][0])
            
            # Mood
            if include_mood and extraction["mood"]:
                prompt_parts.append(f"{extraction['mood'][0]} atmosphere")
            
            # Characters
            if include_characters and extraction["characters"]:
                chars_in_shot = extraction["characters"][:2]
                char_parts = []
                for char in chars_in_shot:
                    char_lower = char.lower()
                    if char_lower in char_desc_map:
                        char_parts.append(f"{char} ({char_desc_map[char_lower]})")
                    else:
                        char_parts.append(char)
                if char_parts:
                    prompt_parts.append(f"featuring: {', '.join(char_parts)}")
            
            # Content
            prompt_parts.append(f"depicting: {snippet}")
            
            # Custom style keywords
            if style_keywords:
                prompt_parts.append(style_keywords)
            
            # Quality
            prompt_parts.append("masterpiece, best quality, highly detailed")
            
            prompts.append({
                "prompt": ", ".join(prompt_parts),
                "negative_prompt": "blurry, low quality, distorted, deformed, ugly, text, watermark, signature",
                "scene_idx": scene_index,
                "shot_idx": i,
                "shot_type": shot,
                "id": f"scene_{scene_index+1:03d}_shot_{i+1:02d}"
            })
        
        # Summary
        summary = f"""
Extracted from scene:
• Characters: {', '.join(extraction['characters'][:5]) or 'None detected'}
• Locations: {', '.join(extraction['locations'][:3]) or 'None detected'}
• Time: {', '.join(extraction['time_of_day']) or 'Not specified'}
• Weather: {', '.join(extraction['weather']) or 'Not specified'}
• Mood: {', '.join(extraction['mood'][:3]) or 'Neutral'}
• Generated {len(prompts)} detailed prompts
"""
        
        return (
            json.dumps(prompts, ensure_ascii=False, indent=2),
            summary.strip()
        )
    
    def _extract_all_elements(self, text: str) -> Dict[str, List[str]]:
        """Extract all visual elements from text."""
        text_lower = text.lower()
        
        elements = {
            "characters": [],
            "locations": [],
            "time_of_day": [],
            "weather": [],
            "mood": [],
            "objects": [],
            "colors": []
        }
        
        # Characters (capitalized names)
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'
        common_words = {'the', 'a', 'an', 'and', 'but', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'i', 'he', 'she', 'it', 'they', 'we', 'you'}
        for match in re.findall(name_pattern, text):
            if match.lower() not in common_words and len(match) > 2:
                elements["characters"].append(match)
        elements["characters"] = list(dict.fromkeys(elements["characters"]))[:10]
        
        # Locations
        loc_keywords = ['forest', 'city', 'room', 'house', 'castle', 'village', 'street', 
                       'garden', 'mountain', 'cave', 'ocean', 'beach', 'desert', 'temple',
                       'palace', 'tower', 'library', 'kitchen', 'bedroom', 'hall']
        for kw in loc_keywords:
            if kw in text_lower:
                elements["locations"].append(kw)
        
        # Time of day
        time_keywords = ['dawn', 'sunrise', 'morning', 'noon', 'afternoon', 'dusk', 
                        'sunset', 'evening', 'night', 'midnight', 'twilight']
        for kw in time_keywords:
            if kw in text_lower:
                elements["time_of_day"].append(kw)
        
        # Weather
        weather_keywords = ['rain', 'snow', 'storm', 'sunny', 'cloudy', 'fog', 'mist',
                          'wind', 'thunder', 'lightning', 'clear']
        for kw in weather_keywords:
            if kw in text_lower:
                elements["weather"].append(kw)
        
        # Mood
        mood_keywords = ['dark', 'bright', 'gloomy', 'cheerful', 'tense', 'peaceful',
                        'mysterious', 'eerie', 'warm', 'cold', 'romantic', 'dramatic',
                        'melancholic', 'hopeful', 'ominous', 'serene']
        for kw in mood_keywords:
            if kw in text_lower:
                elements["mood"].append(kw)
        
        # Colors
        color_keywords = ['red', 'blue', 'green', 'gold', 'silver', 'black', 'white',
                         'crimson', 'azure', 'emerald', 'purple', 'orange', 'pink']
        for kw in color_keywords:
            if kw in text_lower:
                elements["colors"].append(kw)
        
        return elements
