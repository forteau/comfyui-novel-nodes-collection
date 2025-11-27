"""
Novel Cinematic Orchestrator - File Loader & Large Text Support
================================================================
Nodes for loading large novels from files and processing them efficiently.
"""

import json
import os
import re
from typing import List, Dict, Tuple, Any, Optional


class NovelFileLoader:
    """
    Loads novel/story text from a file instead of pasting into a text widget.
    Supports .txt, .md, .rtf (plain text), and basic cleaning.
    """
    
    DESCRIPTION = """
    📂 Novel File Loader
    
    Load large novels (50k+ words) directly from text files.
    Much better than pasting into text widgets for large content.
    
    Supports:
    • .txt files
    • .md (Markdown) files
    • Automatic encoding detection
    • Basic text cleaning
    """

    @classmethod
    def INPUT_TYPES(cls):
        # Get list of text files from input directory
        input_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "input")
        
        txt_files = ["[Select a file]"]
        if os.path.exists(input_dir):
            for f in os.listdir(input_dir):
                if f.lower().endswith(('.txt', '.md', '.text', '.markdown')):
                    txt_files.append(f)
        
        return {
            "required": {
                "file_name": (txt_files,),
                "encoding": (["auto", "utf-8", "utf-16", "latin-1", "cp1252", "ascii"],),
                "clean_text": ("BOOLEAN", {
                    "default": True,
                    "label_on": "Clean formatting",
                    "label_off": "Keep raw"
                }),
                "remove_headers": ("BOOLEAN", {
                    "default": False,
                    "label_on": "Remove chapter headers",
                    "label_off": "Keep headers"
                }),
            },
            "optional": {
                "custom_path": ("STRING", {
                    "default": "",
                    "placeholder": "Or enter full path to file..."
                }),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "INT", "STRING")
    RETURN_NAMES = ("novel_text", "word_count", "char_count", "file_info")
    FUNCTION = "load_novel"
    CATEGORY = "🎬 Story Tools/Input"

    def load_novel(self, file_name: str, encoding: str, clean_text: bool,
                   remove_headers: bool, custom_path: str = "") -> Tuple[str, int, int, str]:
        
        # Determine file path
        if custom_path and os.path.exists(custom_path):
            file_path = custom_path
        else:
            input_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "input")
            file_path = os.path.join(input_dir, file_name)
        
        if not os.path.exists(file_path) or file_name == "[Select a file]":
            return ("", 0, 0, "Error: File not found. Place .txt files in ComfyUI/input/")
        
        # Try to read with encoding detection
        text = ""
        used_encoding = encoding
        
        if encoding == "auto":
            # Try common encodings
            for enc in ["utf-8", "utf-16", "latin-1", "cp1252"]:
                try:
                    with open(file_path, 'r', encoding=enc) as f:
                        text = f.read()
                    used_encoding = enc
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
        else:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    text = f.read()
            except Exception as e:
                return ("", 0, 0, f"Error reading file: {str(e)}")
        
        if not text:
            return ("", 0, 0, "Error: Could not read file with any encoding")
        
        # Clean text if requested
        if clean_text:
            text = self._clean_text(text)
        
        # Remove chapter headers if requested
        if remove_headers:
            text = self._remove_headers(text)
        
        # Calculate stats
        word_count = len(text.split())
        char_count = len(text)
        
        # File info
        file_size = os.path.getsize(file_path)
        file_info = f"Loaded: {os.path.basename(file_path)}\nEncoding: {used_encoding}\nSize: {file_size:,} bytes\nWords: {word_count:,}\nCharacters: {char_count:,}"
        
        return (text, word_count, char_count, file_info)
    
    def _clean_text(self, text: str) -> str:
        """Clean up common formatting issues."""
        # Remove BOM
        text = text.lstrip('\ufeff')
        
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove excessive blank lines (more than 2)
        text = re.sub(r'\n{4,}', '\n\n\n', text)
        
        # Remove trailing whitespace from lines
        text = '\n'.join(line.rstrip() for line in text.split('\n'))
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Remove page numbers (common patterns)
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        text = re.sub(r'\n\s*-\s*\d+\s*-\s*\n', '\n', text)
        
        return text.strip()
    
    def _remove_headers(self, text: str) -> str:
        """Remove chapter headers and similar."""
        # Common chapter patterns
        patterns = [
            r'^Chapter\s+\d+.*$',
            r'^CHAPTER\s+\d+.*$',
            r'^Part\s+\d+.*$',
            r'^PART\s+\d+.*$',
            r'^\d+\.\s*$',
            r'^#{1,6}\s+.*$',  # Markdown headers
        ]
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            is_header = False
            for pattern in patterns:
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    is_header = True
                    break
            if not is_header:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)


class NovelTextSplitter:
    """
    Splits a large novel into manageable chunks for processing.
    Useful for very large texts that might cause memory issues.
    """
    
    DESCRIPTION = """
    ✂️ Novel Text Splitter
    
    Splits large novels into parts for chunk-by-chunk processing.
    Useful for 100k+ word novels or memory-constrained systems.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "novel_text": ("STRING", {"multiline": True}),
                "max_words_per_chunk": ("INT", {
                    "default": 15000,
                    "min": 5000,
                    "max": 50000,
                    "step": 1000
                }),
                "overlap_sentences": ("INT", {
                    "default": 3,
                    "min": 0,
                    "max": 10,
                    "tooltip": "Sentences to overlap between chunks for context"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "INT")
    RETURN_NAMES = ("chunks_json", "total_chunks", "total_words")
    FUNCTION = "split_novel"
    CATEGORY = "🎬 Story Tools/Input"

    def split_novel(self, novel_text: str, max_words_per_chunk: int, 
                    overlap_sentences: int) -> Tuple[str, int, int]:
        
        if not novel_text:
            return ("[]", 0, 0)
        
        # Split by paragraphs first
        paragraphs = [p.strip() for p in novel_text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for para in paragraphs:
            para_words = len(para.split())
            
            if current_word_count + para_words > max_words_per_chunk and current_chunk:
                # Save current chunk
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append({
                    "index": len(chunks),
                    "text": chunk_text,
                    "word_count": current_word_count,
                    "paragraph_count": len(current_chunk)
                })
                
                # Start new chunk with overlap
                if overlap_sentences > 0:
                    # Get last few sentences for overlap
                    last_text = current_chunk[-1] if current_chunk else ""
                    sentences = re.split(r'(?<=[.!?])\s+', last_text)
                    overlap_text = ' '.join(sentences[-overlap_sentences:]) if len(sentences) >= overlap_sentences else last_text
                    current_chunk = [overlap_text, para]
                    current_word_count = len(overlap_text.split()) + para_words
                else:
                    current_chunk = [para]
                    current_word_count = para_words
            else:
                current_chunk.append(para)
                current_word_count += para_words
        
        # Don't forget last chunk
        if current_chunk:
            chunks.append({
                "index": len(chunks),
                "text": '\n\n'.join(current_chunk),
                "word_count": current_word_count,
                "paragraph_count": len(current_chunk)
            })
        
        total_words = sum(c["word_count"] for c in chunks)
        
        return (
            json.dumps(chunks, ensure_ascii=False, indent=2),
            len(chunks),
            total_words
        )


class ChunkIterator:
    """
    Iterates through novel chunks one at a time.
    """
    
    DESCRIPTION = """
    🔄 Chunk Iterator
    
    Get a specific chunk from the split novel for processing.
    Use with a counter node to process all chunks.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "chunks_json": ("STRING", {"multiline": True}),
                "chunk_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 999
                }),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "INT", "BOOLEAN")
    RETURN_NAMES = ("chunk_text", "word_count", "total_chunks", "has_more")
    FUNCTION = "get_chunk"
    CATEGORY = "🎬 Story Tools/Input"

    def get_chunk(self, chunks_json: str, chunk_index: int) -> Tuple[str, int, int, bool]:
        try:
            chunks = json.loads(chunks_json)
        except json.JSONDecodeError:
            return ("", 0, 0, False)
        
        total = len(chunks)
        
        if chunk_index >= total or chunk_index < 0:
            return ("", 0, total, False)
        
        chunk = chunks[chunk_index]
        has_more = chunk_index < total - 1
        
        return (
            chunk.get("text", ""),
            chunk.get("word_count", 0),
            total,
            has_more
        )


class OutputMerger:
    """
    Merges outputs from multiple chunk processings into unified outputs.
    """
    
    DESCRIPTION = """
    🔗 Output Merger
    
    Combines scene/prompt/narration outputs from multiple chunks
    into unified JSON arrays for the full novel.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "existing_json": ("STRING", {
                    "multiline": True,
                    "default": "[]"
                }),
                "new_json": ("STRING", {"multiline": True}),
                "is_nested_array": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "True for image_prompts (nested), False for scenes/narration (flat)"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("merged_json", "total_items")
    FUNCTION = "merge_outputs"
    CATEGORY = "🎬 Story Tools/Helpers"

    def merge_outputs(self, existing_json: str, new_json: str, 
                      is_nested_array: bool) -> Tuple[str, int]:
        try:
            existing = json.loads(existing_json) if existing_json.strip() else []
            new = json.loads(new_json) if new_json.strip() else []
        except json.JSONDecodeError:
            return (existing_json, 0)
        
        if not isinstance(existing, list):
            existing = []
        if not isinstance(new, list):
            new = []
        
        # Reindex new items
        if is_nested_array:
            # For image prompts - nested array of arrays
            base_scene_idx = len(existing)
            for scene_idx, scene_prompts in enumerate(new):
                for prompt in scene_prompts:
                    if isinstance(prompt, dict):
                        prompt["scene_idx"] = base_scene_idx + scene_idx
                        prompt["id"] = f"scene_{base_scene_idx + scene_idx + 1:03d}_shot_{prompt.get('shot_idx', 0) + 1:02d}"
        else:
            # For flat arrays (scenes, narration, sfx)
            base_idx = len(existing)
            for i, item in enumerate(new):
                if isinstance(item, dict):
                    item["index"] = base_idx + i
                    if "scene_idx" in item:
                        item["scene_idx"] = base_idx + i
                    if "id" in item:
                        # Update ID with new index
                        old_id = item["id"]
                        if "scene_" in old_id:
                            item["id"] = re.sub(r'scene_\d+', f'scene_{base_idx + i + 1:03d}', old_id)
        
        merged = existing + new
        
        return (
            json.dumps(merged, ensure_ascii=False, indent=2),
            len(merged)
        )


class ProgressTracker:
    """
    Tracks progress through chunk processing.
    """
    
    DESCRIPTION = """
    📊 Progress Tracker
    
    Track and display progress through chunk processing.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "current_chunk": ("INT", {"default": 0}),
                "total_chunks": ("INT", {"default": 1}),
                "stage_name": ("STRING", {"default": "Processing"}),
            }
        }

    RETURN_TYPES = ("STRING", "FLOAT", "BOOLEAN")
    RETURN_NAMES = ("progress_text", "progress_percent", "is_complete")
    FUNCTION = "track_progress"
    CATEGORY = "🎬 Story Tools/Helpers"

    def track_progress(self, current_chunk: int, total_chunks: int, 
                       stage_name: str) -> Tuple[str, float, bool]:
        
        if total_chunks <= 0:
            total_chunks = 1
        
        progress_percent = ((current_chunk + 1) / total_chunks) * 100
        is_complete = current_chunk >= total_chunks - 1
        
        progress_bar_width = 30
        filled = int(progress_bar_width * (current_chunk + 1) / total_chunks)
        bar = '█' * filled + '░' * (progress_bar_width - filled)
        
        progress_text = f"""
╔════════════════════════════════════════╗
║ 📊 {stage_name:^34} ║
╠════════════════════════════════════════╣
║ [{bar}] ║
║ Chunk {current_chunk + 1} of {total_chunks} ({progress_percent:.1f}%)             ║
║ Status: {'✅ Complete!' if is_complete else '⏳ Processing...':^28} ║
╚════════════════════════════════════════╝
"""
        
        return (progress_text.strip(), progress_percent, is_complete)


class LargeNovelStats:
    """
    Provides detailed statistics about a novel.
    """
    
    DESCRIPTION = """
    📈 Novel Statistics
    
    Analyze a novel and provide detailed statistics for planning.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "novel_text": ("STRING", {"multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "INT", "INT", "FLOAT", "STRING")
    RETURN_NAMES = ("stats_text", "word_count", "paragraph_count", "estimated_scenes", "estimated_duration_minutes", "recommendations")
    FUNCTION = "analyze_novel"
    CATEGORY = "🎬 Story Tools/Input"

    def analyze_novel(self, novel_text: str) -> Tuple[str, int, int, int, float, str]:
        if not novel_text:
            return ("No text provided", 0, 0, 0, 0.0, "")
        
        # Basic counts
        word_count = len(novel_text.split())
        char_count = len(novel_text)
        paragraphs = [p for p in novel_text.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)
        
        # Estimate scenes (roughly 2000 chars per scene)
        estimated_scenes = max(1, char_count // 2000)
        
        # Estimate duration (150 words per minute reading speed)
        estimated_duration_minutes = word_count / 150
        
        # Detect chapters
        chapter_pattern = r'(?:chapter|part)\s+\d+|#{1,3}\s+'
        chapters = len(re.findall(chapter_pattern, novel_text, re.IGNORECASE))
        
        # Character density estimate
        name_pattern = r'\b[A-Z][a-z]+\b'
        potential_names = len(set(re.findall(name_pattern, novel_text)))
        
        # Dialogue ratio
        dialogue_pattern = r'["""][^"""]+["""]'
        dialogue_matches = re.findall(dialogue_pattern, novel_text)
        dialogue_words = sum(len(d.split()) for d in dialogue_matches)
        dialogue_ratio = (dialogue_words / max(word_count, 1)) * 100
        
        # Generate recommendations
        recommendations = []
        
        if word_count > 50000:
            recommendations.append("📦 Large novel detected! Use 'Novel Text Splitter' to process in chunks of 15-20k words")
        
        if word_count > 100000:
            recommendations.append("⚠️ Very large novel! Consider processing in multiple sessions")
            recommendations.append("💡 Set batch_size to 2-4 to manage memory")
        
        if estimated_scenes > 50:
            recommendations.append(f"🎬 Will generate ~{estimated_scenes} scenes. Consider increasing max_scene_chars")
        
        if dialogue_ratio > 50:
            recommendations.append("💬 High dialogue content - consider using voice mode with emotion support")
        
        if chapters > 0:
            recommendations.append(f"📖 Detected {chapters} chapter markers - scene breaks will follow these")
        
        if not recommendations:
            recommendations.append("✅ Novel size is manageable for direct processing")
        
        # Format stats
        hours = int(estimated_duration_minutes // 60)
        mins = int(estimated_duration_minutes % 60)
        duration_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"
        
        stats_text = f"""
╔══════════════════════════════════════════════════════════════╗
║                    📈 NOVEL STATISTICS                        ║
╠══════════════════════════════════════════════════════════════╣
║  📝 Word Count:           {word_count:>15,}                    ║
║  📄 Character Count:      {char_count:>15,}                    ║
║  ¶  Paragraphs:          {paragraph_count:>15,}                    ║
║  📖 Chapters Detected:    {chapters:>15}                    ║
╠══════════════════════════════════════════════════════════════╣
║  🎬 Estimated Scenes:     {estimated_scenes:>15}                    ║
║  ⏱️  Estimated Duration:  {duration_str:>15}                    ║
║  💬 Dialogue Ratio:       {dialogue_ratio:>14.1f}%                    ║
║  👤 Potential Characters: {potential_names:>15}                    ║
╚══════════════════════════════════════════════════════════════╝
"""
        
        return (
            stats_text.strip(),
            word_count,
            paragraph_count,
            estimated_scenes,
            estimated_duration_minutes,
            "\n".join(recommendations)
        )


class MemoryOptimizedOrchestrator:
    """
    A memory-optimized version of the orchestrator that processes
    scenes on-demand rather than all at once.
    """
    
    DESCRIPTION = """
    📖 Memory-Optimized Orchestrator
    
    Processes one scene at a time to reduce memory usage.
    Better for very large novels (50k+ words).
    
    Use this in a loop with a counter node.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "novel_text": ("STRING", {"multiline": True}),
                "scene_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9999
                }),
                "max_scene_chars": ("INT", {
                    "default": 2000,
                    "min": 500,
                    "max": 10000
                }),
                "broll_density": ("INT", {
                    "default": 4,
                    "min": 1,
                    "max": 16
                }),
                "image_engine": (["flux", "sdxl", "sd15", "cascade", "pixart"],),
                "image_style": (["cinematic", "anime", "realistic", "painterly", "comic", "storyboard"],),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "INT", "BOOLEAN")
    RETURN_NAMES = ("scene_text", "scene_prompts_json", "scene_narration_json", "scene_sfx_json", "total_scenes", "has_more")
    FUNCTION = "process_scene"
    CATEGORY = "🎬 Story Tools/Orchestration"
    
    # Cache for scene splitting (to avoid re-splitting on each call)
    _cache = {}

    def process_scene(self, novel_text: str, scene_index: int, max_scene_chars: int,
                      broll_density: int, image_engine: str, 
                      image_style: str) -> Tuple[str, str, str, str, int, bool]:
        
        # Generate cache key
        cache_key = hash((novel_text[:100], max_scene_chars))
        
        # Get or create scene list
        if cache_key not in self._cache:
            scenes = self._split_scenes(novel_text, max_scene_chars)
            self._cache[cache_key] = scenes
            # Limit cache size
            if len(self._cache) > 10:
                self._cache.pop(next(iter(self._cache)))
        else:
            scenes = self._cache[cache_key]
        
        total_scenes = len(scenes)
        
        if scene_index >= total_scenes or scene_index < 0:
            return ("", "[]", "{}", "{}", total_scenes, False)
        
        scene_text = scenes[scene_index]
        has_more = scene_index < total_scenes - 1
        
        # Process just this scene
        prompts = self._generate_prompts(scene_text, scene_index, broll_density, image_style, image_engine)
        narration = self._process_narration(scene_text, scene_index)
        sfx = self._generate_sfx(scene_text, scene_index)
        
        return (
            scene_text,
            json.dumps(prompts, ensure_ascii=False, indent=2),
            json.dumps(narration, ensure_ascii=False, indent=2),
            json.dumps(sfx, ensure_ascii=False, indent=2),
            total_scenes,
            has_more
        )
    
    def _split_scenes(self, text: str, max_chars: int) -> List[str]:
        """Split text into scenes."""
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
    
    def _generate_prompts(self, scene: str, idx: int, density: int, style: str, engine: str) -> List[Dict]:
        """Generate prompts for a single scene."""
        styles = {
            "cinematic": "cinematic film still, dramatic lighting",
            "anime": "anime art style, vibrant colors",
            "realistic": "photorealistic, natural lighting",
            "painterly": "oil painting style, artistic",
            "comic": "comic book art, bold lines",
            "storyboard": "storyboard frame, concept art"
        }
        
        flat = " ".join(scene.split())
        chunk_size = max(len(flat) // density, 50)
        prompts = []
        
        shot_types = ["establishing shot", "medium shot", "close-up", "wide shot"]
        
        for i in range(density):
            snippet = flat[i * chunk_size:(i + 1) * chunk_size][:100]
            if not snippet:
                break
            
            prompts.append({
                "prompt": f"Scene {idx + 1}, Shot {i + 1}, {shot_types[i % 4]}, {styles.get(style, '')}, depicting: {snippet}",
                "negative_prompt": "blurry, low quality, distorted",
                "scene_idx": idx,
                "shot_idx": i,
                "id": f"scene_{idx + 1:03d}_shot_{i + 1:02d}"
            })
        
        return prompts
    
    def _process_narration(self, scene: str, idx: int) -> Dict:
        """Process narration for a single scene."""
        word_count = len(scene.split())
        duration = (word_count / 150) * 60
        
        return {
            "text": scene,
            "scene_idx": idx,
            "word_count": word_count,
            "estimated_duration_seconds": round(duration, 1),
            "id": f"narration_scene_{idx + 1:03d}"
        }
    
    def _generate_sfx(self, scene: str, idx: int) -> Dict:
        """Generate SFX for a single scene."""
        scene_lower = scene.lower()
        cues = []
        
        keywords = {
            "forest": "forest ambience, birds, leaves",
            "rain": "rain sounds, water drops",
            "city": "urban ambience, traffic",
            "battle": "combat sounds, impacts",
            "ocean": "waves, water, seashore"
        }
        
        for kw, sfx in keywords.items():
            if kw in scene_lower:
                cues.append({"keyword": kw, "sfx": sfx})
        
        if not cues:
            cues.append({"keyword": "ambient", "sfx": "subtle room tone"})
        
        return {
            "cues": cues,
            "combined_prompt": ", ".join([c["sfx"] for c in cues]),
            "scene_idx": idx,
            "id": f"sfx_scene_{idx + 1:03d}"
        }
