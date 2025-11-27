"""
Novel Cinematic Orchestrator - Helper Nodes
============================================
Utility nodes for processing the orchestrator's output in the ComfyUI pipeline.

Includes:
- PromptBatcher: Flatten and batch image prompts for faster generation
- SceneIterator: Loop through scenes one at a time
- JSONParser: Parse JSON outputs into usable strings
- ConfigSelector: Extract specific config values
- NarrationSplitter: Split narration into TTS-friendly chunks
"""

import json
from typing import List, Dict, Tuple, Any, Optional


class PromptBatcher:
    """
    Flattens nested image prompts and groups them into batches for 
    efficient parallel generation.
    """
    
    DESCRIPTION = """
    📦 Prompt Batcher
    
    Takes the nested image_prompts_json from the Orchestrator and flattens 
    it into batches for parallel image generation.
    
    Outputs:
    • Batched prompts ready for sampler
    • Index map for reassembling scenes later
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_prompts_json": ("STRING", {"multiline": True}),
                "batch_size": ("INT", {
                    "default": 4,
                    "min": 1,
                    "max": 32,
                    "step": 1,
                    "tooltip": "Number of images to generate in parallel"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "STRING")
    RETURN_NAMES = ("batched_prompts_json", "index_map_json", "total_prompts", "first_batch_prompts")
    FUNCTION = "batch_prompts"
    CATEGORY = "🎬 Story Tools/Helpers"

    def batch_prompts(self, image_prompts_json: str, batch_size: int) -> Tuple[str, str, int, str]:
        try:
            all_prompts = json.loads(image_prompts_json)
        except json.JSONDecodeError:
            return ("[]", "[]", 0, "")
        
        # Flatten all prompts with index tracking
        flat_prompts = []
        index_map = []
        
        for scene_idx, scene_prompts in enumerate(all_prompts):
            for shot_idx, prompt_obj in enumerate(scene_prompts):
                flat_prompts.append(prompt_obj)
                index_map.append({
                    "flat_idx": len(flat_prompts) - 1,
                    "scene_idx": scene_idx,
                    "shot_idx": shot_idx,
                    "prompt_id": prompt_obj.get("id", f"s{scene_idx}_sh{shot_idx}")
                })
        
        # Create batches
        batches = []
        for i in range(0, len(flat_prompts), batch_size):
            batch = flat_prompts[i:i + batch_size]
            batches.append({
                "batch_idx": len(batches),
                "start_idx": i,
                "end_idx": min(i + batch_size, len(flat_prompts)),
                "prompts": batch,
                "prompt_texts": [p.get("prompt", "") for p in batch],
                "negative_prompts": [p.get("negative_prompt", "") for p in batch]
            })
        
        # Extract first batch for direct use
        first_batch_prompts = ""
        if batches:
            first_batch_prompts = "\n---\n".join(batches[0]["prompt_texts"])
        
        return (
            json.dumps(batches, ensure_ascii=False, indent=2),
            json.dumps(index_map, ensure_ascii=False, indent=2),
            len(flat_prompts),
            first_batch_prompts
        )


class SceneIterator:
    """
    Iterates through scenes, outputting one scene at a time for sequential processing.
    """
    
    DESCRIPTION = """
    🔄 Scene Iterator
    
    Extracts a single scene by index from the scenes JSON.
    Use with a counter node to loop through all scenes.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "scenes_json": ("STRING", {"multiline": True}),
                "scene_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9999,
                    "step": 1
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "BOOLEAN")
    RETURN_NAMES = ("scene_text", "scene_id", "total_scenes", "has_more")
    FUNCTION = "get_scene"
    CATEGORY = "🎬 Story Tools/Helpers"

    def get_scene(self, scenes_json: str, scene_index: int) -> Tuple[str, str, int, bool]:
        try:
            scenes = json.loads(scenes_json)
        except json.JSONDecodeError:
            return ("", "", 0, False)
        
        total = len(scenes)
        
        if scene_index >= total or scene_index < 0:
            return ("", "", total, False)
        
        scene = scenes[scene_index]
        scene_text = scene.get("text", "")
        scene_id = scene.get("id", f"scene_{scene_index}")
        has_more = scene_index < total - 1
        
        return (scene_text, scene_id, total, has_more)


class NarrationIterator:
    """
    Iterates through narration entries for TTS processing.
    """
    
    DESCRIPTION = """
    🎤 Narration Iterator
    
    Extracts narration for a specific scene, ready for TTS processing.
    Includes word count and duration estimates.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "narration_json": ("STRING", {"multiline": True}),
                "scene_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9999
                }),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "FLOAT", "BOOLEAN")
    RETURN_NAMES = ("narration_text", "word_count", "duration_estimate", "has_dialogue")
    FUNCTION = "get_narration"
    CATEGORY = "🎬 Story Tools/Helpers"

    def get_narration(self, narration_json: str, scene_index: int) -> Tuple[str, int, float, bool]:
        try:
            narrations = json.loads(narration_json)
        except json.JSONDecodeError:
            return ("", 0, 0.0, False)
        
        if scene_index >= len(narrations) or scene_index < 0:
            return ("", 0, 0.0, False)
        
        narration = narrations[scene_index]
        
        return (
            narration.get("text", ""),
            narration.get("word_count", 0),
            narration.get("estimated_duration_seconds", 0.0),
            narration.get("has_dialogue", False)
        )


class SFXCueIterator:
    """
    Iterates through SFX cues for audio generation.
    """
    
    DESCRIPTION = """
    🔊 SFX Cue Iterator
    
    Extracts SFX cues for a specific scene, ready for MMAudio or StableAudio.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "sfx_cues_json": ("STRING", {"multiline": True}),
                "scene_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9999
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("combined_sfx_prompt", "all_cues_json", "cue_count")
    FUNCTION = "get_sfx"
    CATEGORY = "🎬 Story Tools/Helpers"

    def get_sfx(self, sfx_cues_json: str, scene_index: int) -> Tuple[str, str, int]:
        try:
            sfx_cues = json.loads(sfx_cues_json)
        except json.JSONDecodeError:
            return ("", "[]", 0)
        
        if scene_index >= len(sfx_cues) or scene_index < 0:
            return ("", "[]", 0)
        
        sfx = sfx_cues[scene_index]
        
        return (
            sfx.get("combined_prompt", ""),
            json.dumps(sfx.get("cues", []), ensure_ascii=False),
            sfx.get("cue_count", 0)
        )


class ImagePromptIterator:
    """
    Iterates through image prompts for a specific scene.
    """
    
    DESCRIPTION = """
    🖼️ Image Prompt Iterator
    
    Extracts image prompts for a specific scene and shot index.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_prompts_json": ("STRING", {"multiline": True}),
                "scene_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9999
                }),
                "shot_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 99
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "INT")
    RETURN_NAMES = ("prompt", "negative_prompt", "shot_type", "total_shots_in_scene")
    FUNCTION = "get_prompt"
    CATEGORY = "🎬 Story Tools/Helpers"

    def get_prompt(self, image_prompts_json: str, scene_index: int, 
                   shot_index: int) -> Tuple[str, str, str, int]:
        try:
            all_prompts = json.loads(image_prompts_json)
        except json.JSONDecodeError:
            return ("", "", "", 0)
        
        if scene_index >= len(all_prompts) or scene_index < 0:
            return ("", "", "", 0)
        
        scene_prompts = all_prompts[scene_index]
        total_shots = len(scene_prompts)
        
        if shot_index >= total_shots or shot_index < 0:
            return ("", "", "", total_shots)
        
        prompt_obj = scene_prompts[shot_index]
        
        return (
            prompt_obj.get("prompt", ""),
            prompt_obj.get("negative_prompt", ""),
            prompt_obj.get("shot_type", ""),
            total_shots
        )


class ConfigExtractor:
    """
    Extracts specific configuration values from the config JSON.
    """
    
    DESCRIPTION = """
    ⚙️ Config Extractor
    
    Extracts specific values from the configuration JSON for use
    in conditional routing and node configuration.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "config_json": ("STRING", {"multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "BOOLEAN", "INT", "FLOAT", "STRING", "STRING")
    RETURN_NAMES = (
        "image_engine", 
        "voice_mode", 
        "parallax_enabled", 
        "num_scenes",
        "total_duration",
        "resolution",
        "sfx_mode"
    )
    FUNCTION = "extract_config"
    CATEGORY = "🎬 Story Tools/Helpers"

    def extract_config(self, config_json: str) -> Tuple[str, str, bool, int, float, str, str]:
        try:
            config = json.loads(config_json)
        except json.JSONDecodeError:
            return ("flux", "index_tts", True, 0, 0.0, "1920x1080", "mmaudio_auto")
        
        return (
            config.get("image_engine", "flux"),
            config.get("voice_mode", "index_tts"),
            config.get("parallax_enabled", True),
            config.get("num_scenes", 0),
            config.get("estimated_duration_seconds", 0.0),
            config.get("target_resolution", "1920x1080"),
            config.get("sfx_mode", "mmaudio_auto")
        )


class CharacterExtractor:
    """
    Extracts character information for consistency processing.
    """
    
    DESCRIPTION = """
    👤 Character Extractor
    
    Extracts detected character names and their mention counts.
    Use for LoRA loading and character consistency.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "characters_json": ("STRING", {"multiline": True}),
                "max_characters": ("INT", {
                    "default": 5,
                    "min": 1,
                    "max": 20
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("character_names", "character_list_json", "character_count")
    FUNCTION = "extract_characters"
    CATEGORY = "🎬 Story Tools/Helpers"

    def extract_characters(self, characters_json: str, max_characters: int) -> Tuple[str, str, int]:
        try:
            characters = json.loads(characters_json)
        except json.JSONDecodeError:
            return ("", "[]", 0)
        
        # Limit to max_characters
        limited = characters[:max_characters]
        
        # Create comma-separated list
        names = ", ".join([c.get("name", "") for c in limited])
        
        return (
            names,
            json.dumps(limited, ensure_ascii=False, indent=2),
            len(limited)
        )


class NarrationChunker:
    """
    Splits long narration into smaller chunks for TTS processing.
    Useful for TTS models with length limitations.
    """
    
    DESCRIPTION = """
    ✂️ Narration Chunker
    
    Splits long narration text into smaller chunks suitable for TTS.
    Respects sentence boundaries for natural-sounding output.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "narration_text": ("STRING", {"multiline": True}),
                "max_chars_per_chunk": ("INT", {
                    "default": 500,
                    "min": 100,
                    "max": 2000,
                    "step": 50
                }),
                "respect_paragraphs": ("BOOLEAN", {
                    "default": True
                }),
            }
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("chunks_json", "chunk_count")
    FUNCTION = "chunk_narration"
    CATEGORY = "🎬 Story Tools/Helpers"

    def chunk_narration(self, narration_text: str, max_chars_per_chunk: int,
                        respect_paragraphs: bool) -> Tuple[str, int]:
        import re
        
        if not narration_text:
            return ("[]", 0)
        
        chunks = []
        
        if respect_paragraphs:
            # Split by paragraphs first
            paragraphs = [p.strip() for p in narration_text.split("\n\n") if p.strip()]
        else:
            paragraphs = [narration_text]
        
        current_chunk = ""
        
        for para in paragraphs:
            # If paragraph itself is too long, split by sentences
            if len(para) > max_chars_per_chunk:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 1 > max_chars_per_chunk:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence
                    else:
                        current_chunk += " " + sentence if current_chunk else sentence
            else:
                if len(current_chunk) + len(para) + 2 > max_chars_per_chunk:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = para
                else:
                    current_chunk += "\n\n" + para if current_chunk else para
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        chunks_data = [
            {"index": i, "text": chunk, "char_count": len(chunk)}
            for i, chunk in enumerate(chunks)
        ]
        
        return (
            json.dumps(chunks_data, ensure_ascii=False, indent=2),
            len(chunks)
        )


class SceneToVideoConfig:
    """
    Generates video assembly configuration for a scene.
    """
    
    DESCRIPTION = """
    🎬 Scene Video Config
    
    Generates configuration for video assembly, including
    timing, transitions, and audio sync settings.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "narration_json": ("STRING", {"multiline": True}),
                "config_json": ("STRING", {"multiline": True}),
                "scene_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9999
                }),
                "parallax_duration_per_shot": ("FLOAT", {
                    "default": 3.0,
                    "min": 1.0,
                    "max": 10.0,
                    "step": 0.5
                }),
            }
        }

    RETURN_TYPES = ("STRING", "FLOAT", "INT", "STRING")
    RETURN_NAMES = ("video_config_json", "scene_duration", "frame_count", "transition_type")
    FUNCTION = "generate_video_config"
    CATEGORY = "🎬 Story Tools/Video"

    def generate_video_config(self, narration_json: str, config_json: str,
                               scene_index: int, 
                               parallax_duration_per_shot: float) -> Tuple[str, float, int, str]:
        try:
            narrations = json.loads(narration_json)
            config = json.loads(config_json)
        except json.JSONDecodeError:
            return ("{}", 0.0, 0, "fade")
        
        if scene_index >= len(narrations):
            return ("{}", 0.0, 0, "fade")
        
        narration = narrations[scene_index]
        fps = config.get("target_video_fps", 24)
        transition = config.get("scene_transition_style", "fade")
        
        # Calculate duration based on narration
        narration_duration = narration.get("estimated_duration_seconds", 10.0)
        
        # Ensure minimum duration for visuals
        min_visual_duration = parallax_duration_per_shot * config.get("broll_density", 4)
        scene_duration = max(narration_duration, min_visual_duration)
        
        frame_count = int(scene_duration * fps)
        
        video_config = {
            "scene_index": scene_index,
            "duration_seconds": scene_duration,
            "frame_count": frame_count,
            "fps": fps,
            "transition": transition,
            "resolution": config.get("target_resolution", "1920x1080"),
            "parallax_enabled": config.get("parallax_enabled", True),
            "audio_sync": {
                "narration_duration": narration_duration,
                "buffer_seconds": 0.5
            }
        }
        
        return (
            json.dumps(video_config, ensure_ascii=False, indent=2),
            scene_duration,
            frame_count,
            transition
        )


class LoRAProfileParser:
    """
    Parses the character_profile string into individual LoRA names.
    """
    
    DESCRIPTION = """
    🎨 LoRA Profile Parser
    
    Parses comma-separated LoRA names from the character profile
    for use with LoRA loader nodes.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "character_profile": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "INT")
    RETURN_NAMES = ("lora_1", "lora_2", "lora_3", "lora_count")
    FUNCTION = "parse_loras"
    CATEGORY = "🎬 Story Tools/Helpers"

    def parse_loras(self, character_profile: str) -> Tuple[str, str, str, int]:
        if not character_profile:
            return ("", "", "", 0)
        
        # Split by comma and clean up
        loras = [l.strip() for l in character_profile.split(",") if l.strip()]
        
        # Pad with empty strings
        while len(loras) < 3:
            loras.append("")
        
        return (loras[0], loras[1], loras[2], len([l for l in loras if l]))


class EngineSelector:
    """
    Routes to different checkpoint loaders based on engine selection.
    """
    
    DESCRIPTION = """
    🔀 Engine Selector
    
    Outputs engine-specific settings for routing to the correct
    checkpoint loader and sampler configuration.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_engine": ("STRING", {"default": "flux"}),
            }
        }

    RETURN_TYPES = ("BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN", "STRING")
    RETURN_NAMES = ("is_flux", "is_sdxl", "is_sd15", "is_cascade", "is_pixart", "recommended_sampler")
    FUNCTION = "select_engine"
    CATEGORY = "🎬 Story Tools/Helpers"

    def select_engine(self, image_engine: str) -> Tuple[bool, bool, bool, bool, bool, str]:
        engine = image_engine.lower()
        
        samplers = {
            "flux": "euler",
            "sdxl": "dpmpp_2m_sde",
            "sd15": "dpmpp_2m",
            "cascade": "euler_ancestral",
            "pixart": "dpmpp_2m"
        }
        
        return (
            engine == "flux",
            engine == "sdxl",
            engine == "sd15",
            engine == "cascade",
            engine == "pixart",
            samplers.get(engine, "euler")
        )


class TextCombiner:
    """
    Combines multiple text outputs for batch processing.
    """
    
    DESCRIPTION = """
    📝 Text Combiner
    
    Combines multiple scene texts or prompts into a single
    output for batch processing.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_array": ("STRING", {"multiline": True}),
                "separator": ("STRING", {"default": "\n---\n"}),
                "field_name": ("STRING", {"default": "text"}),
            }
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("combined_text", "item_count")
    FUNCTION = "combine_texts"
    CATEGORY = "🎬 Story Tools/Helpers"

    def combine_texts(self, json_array: str, separator: str, 
                      field_name: str) -> Tuple[str, int]:
        try:
            items = json.loads(json_array)
        except json.JSONDecodeError:
            return ("", 0)
        
        if not isinstance(items, list):
            return ("", 0)
        
        texts = []
        for item in items:
            if isinstance(item, dict):
                texts.append(str(item.get(field_name, "")))
            elif isinstance(item, str):
                texts.append(item)
        
        return (separator.join(texts), len(texts))
