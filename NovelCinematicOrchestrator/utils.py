"""
Novel Cinematic Orchestrator - Utilities
=========================================
Shared utility functions for the node pack.
"""

import json
import re
import os
from typing import List, Dict, Any, Optional, Tuple


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely parse JSON string with fallback."""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else {}


def safe_json_dumps(obj: Any, **kwargs) -> str:
    """Safely serialize object to JSON string."""
    try:
        return json.dumps(obj, ensure_ascii=False, **kwargs)
    except (TypeError, ValueError):
        return "{}"


def clean_text_for_tts(text: str) -> str:
    """Clean text for TTS processing."""
    if not text:
        return ""
    
    # Remove markdown formatting
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.+?)\*', r'\1', text)       # Italic
    text = re.sub(r'_(.+?)_', r'\1', text)         # Underscore italic
    text = re.sub(r'~~(.+?)~~', r'\1', text)       # Strikethrough
    text = re.sub(r'`(.+?)`', r'\1', text)         # Inline code
    text = re.sub(r'#{1,6}\s*', '', text)          # Headers
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)  # Links
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    # Normalize whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\t', ' ', text)
    
    return text.strip()


def estimate_reading_duration(text: str, words_per_minute: int = 150) -> float:
    """Estimate reading duration in seconds."""
    if not text:
        return 0.0
    word_count = len(text.split())
    return (word_count / words_per_minute) * 60


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    if not text:
        return []
    
    # Simple sentence splitting
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def split_into_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs."""
    if not text:
        return []
    
    paragraphs = text.split('\n\n')
    return [p.strip() for p in paragraphs if p.strip()]


def extract_dialogue(text: str) -> List[Dict[str, str]]:
    """Extract dialogue from text."""
    if not text:
        return []
    
    # Pattern for quoted dialogue
    dialogue_pattern = r'["""]([^"""]+)["""]'
    
    dialogues = []
    for match in re.finditer(dialogue_pattern, text):
        dialogues.append({
            "text": match.group(1),
            "start": match.start(),
            "end": match.end()
        })
    
    return dialogues


def get_model_path(model_type: str, model_name: str) -> str:
    """Get the expected path for a model file."""
    base_paths = {
        "checkpoints": "models/checkpoints",
        "loras": "models/loras",
        "tts": "models/TTS",
        "vae": "models/vae",
        "controlnet": "models/controlnet",
        "embeddings": "models/embeddings"
    }
    
    base = base_paths.get(model_type, "models")
    return os.path.join(base, model_name)


def format_duration(seconds: float) -> str:
    """Format seconds into human-readable duration."""
    if seconds < 60:
        return f"{int(seconds)}s"
    
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    
    if minutes >= 60:
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m {secs}s"
    
    return f"{minutes}m {secs}s"


def create_progress_callback(total_steps: int):
    """Create a progress callback function."""
    current_step = [0]
    
    def callback(step_info: Optional[str] = None):
        current_step[0] += 1
        progress = (current_step[0] / total_steps) * 100
        print(f"[NovelCinematic] Progress: {progress:.1f}% - {step_info or 'Processing...'}")
        return progress
    
    return callback


def merge_configs(*configs: Dict) -> Dict:
    """Merge multiple configuration dictionaries."""
    result = {}
    for config in configs:
        if isinstance(config, dict):
            result.update(config)
    return result


def validate_json_structure(json_str: str, expected_type: type = list) -> Tuple[bool, str]:
    """Validate JSON structure and return status with message."""
    try:
        data = json.loads(json_str)
        if not isinstance(data, expected_type):
            return False, f"Expected {expected_type.__name__}, got {type(data).__name__}"
        return True, "Valid"
    except json.JSONDecodeError as e:
        return False, f"JSON parse error: {str(e)}"


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split a list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def generate_unique_id(prefix: str = "", length: int = 8) -> str:
    """Generate a unique identifier."""
    import hashlib
    import time
    import random
    
    seed = f"{time.time()}{random.random()}"
    hash_str = hashlib.md5(seed.encode()).hexdigest()[:length]
    
    if prefix:
        return f"{prefix}_{hash_str}"
    return hash_str


class ProgressTracker:
    """Track progress across multiple stages."""
    
    def __init__(self, stages: List[str]):
        self.stages = stages
        self.current_stage = 0
        self.stage_progress = 0.0
    
    def next_stage(self) -> str:
        """Move to next stage and return its name."""
        if self.current_stage < len(self.stages) - 1:
            self.current_stage += 1
            self.stage_progress = 0.0
        return self.stages[self.current_stage]
    
    def update_progress(self, progress: float):
        """Update progress within current stage (0-100)."""
        self.stage_progress = min(max(progress, 0), 100)
    
    def get_overall_progress(self) -> float:
        """Get overall progress across all stages."""
        if not self.stages:
            return 100.0
        
        stage_weight = 100.0 / len(self.stages)
        completed = self.current_stage * stage_weight
        current = (self.stage_progress / 100) * stage_weight
        
        return completed + current
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        return {
            "current_stage": self.stages[self.current_stage] if self.stages else "",
            "stage_index": self.current_stage,
            "stage_progress": self.stage_progress,
            "overall_progress": self.get_overall_progress(),
            "total_stages": len(self.stages)
        }


# Constants for the node pack
DEFAULT_STYLES = {
    "cinematic": "cinematic film still, dramatic lighting, shallow depth of field",
    "anime": "anime art style, vibrant colors, detailed linework",
    "realistic": "photorealistic, hyperdetailed, natural lighting",
    "painterly": "oil painting style, rich textures, artistic brushstrokes",
    "comic": "comic book art, bold lines, dynamic composition",
    "storyboard": "storyboard frame, concept art, key frame"
}

DEFAULT_QUALITY_TAGS = {
    "flux": "masterpiece, best quality, highly detailed, sharp focus",
    "sdxl": "masterpiece, best quality, ultra detailed, 8k uhd",
    "sd15": "best quality, highly detailed, sharp focus, intricate details",
    "cascade": "high quality, detailed, professional, sharp",
    "pixart": "high quality artwork, detailed, aesthetic, professional"
}

SUPPORTED_ENGINES = ["flux", "sdxl", "sd15", "cascade", "pixart"]
SUPPORTED_VOICE_MODES = ["index_tts", "index_clone", "xtts", "voxcpm", "chatterbox"]
SUPPORTED_SFX_MODES = ["mmaudio_auto", "mmaudio_prompted", "stable_audio", "none"]
SUPPORTED_STYLES = ["cinematic", "anime", "realistic", "painterly", "comic", "storyboard"]
SUPPORTED_TRANSITIONS = ["fade", "cut", "dissolve", "wipe"]
SUPPORTED_RESOLUTIONS = ["1920x1080", "1280x720", "3840x2160", "1080x1920", "720x1280"]
