"""
Novel Cinematic Orchestrator - TTS Batch Processing
=====================================================
Nodes for efficient TTS generation of entire novels with batching,
chunking, and audio assembly support.

Supports:
- IndexTTS / IndexTTS-2
- XTTS
- ChatterBox
- VoxCPM
- Any ComfyUI TTS node
"""

import json
import re
import math
from typing import List, Dict, Tuple, Any, Optional


class TTSCoverageCalculator:
    """
    Calculates TTS generation requirements and time estimates.
    """
    
    DESCRIPTION = """
    🎤 TTS Coverage Calculator
    
    Analyzes your novel and calculates:
    • Total audio duration needed
    • Number of TTS chunks required
    • Estimated generation time
    • Optimal chunk settings
    """

    # Typical TTS generation speeds (characters per second of real-time)
    TTS_SPEEDS = {
        "index_tts": 50,      # ~50 chars/sec generation
        "index_tts_2": 80,    # Faster
        "xtts": 30,           # Slower but high quality
        "chatterbox": 60,     # Good speed
        "voxcpm": 40,         # Medium
        "kokoro": 100,        # Very fast
    }
    
    # Max characters per chunk for different TTS engines
    TTS_MAX_CHARS = {
        "index_tts": 1000,
        "index_tts_2": 2000,
        "xtts": 500,
        "chatterbox": 1500,
        "voxcpm": 1000,
        "kokoro": 2000,
    }

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "word_count": ("INT", {
                    "default": 50000,
                    "min": 100,
                    "max": 500000
                }),
                "tts_engine": (["index_tts", "index_tts_2", "xtts", "chatterbox", "voxcpm", "kokoro"],),
                "narration_speed_wpm": ("INT", {
                    "default": 150,
                    "min": 100,
                    "max": 200,
                    "tooltip": "Target words per minute for narration"
                }),
                "parallel_instances": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 4,
                    "tooltip": "Number of parallel TTS generations (requires VRAM)"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "FLOAT", "FLOAT", "INT", "STRING")
    RETURN_NAMES = (
        "analysis_text",
        "total_chunks_needed",
        "audio_duration_hours",
        "generation_time_hours",
        "recommended_chunk_chars",
        "settings_json"
    )
    FUNCTION = "calculate_tts"
    CATEGORY = "🎬 Story Tools/TTS"

    def calculate_tts(self, word_count: int, tts_engine: str,
                      narration_speed_wpm: int, 
                      parallel_instances: int) -> Tuple[str, int, float, float, int, str]:
        
        # Calculate audio duration
        audio_minutes = word_count / narration_speed_wpm
        audio_hours = audio_minutes / 60
        audio_seconds = audio_minutes * 60
        
        # Calculate character count (avg 5 chars per word + spaces)
        total_chars = word_count * 6
        
        # Get engine specs
        max_chars = self.TTS_MAX_CHARS.get(tts_engine, 1000)
        gen_speed = self.TTS_SPEEDS.get(tts_engine, 50)
        
        # Calculate chunks needed
        chunks_needed = math.ceil(total_chars / max_chars)
        
        # Calculate generation time
        # Time = total_chars / gen_speed / parallel_instances
        gen_seconds = total_chars / gen_speed / parallel_instances
        gen_hours = gen_seconds / 3600
        
        # Real-time factor
        rtf = gen_seconds / audio_seconds if audio_seconds > 0 else 0
        
        # VRAM estimate per instance
        vram_estimates = {
            "index_tts": 4,
            "index_tts_2": 4,
            "xtts": 6,
            "chatterbox": 3,
            "voxcpm": 5,
            "kokoro": 2,
        }
        vram_per = vram_estimates.get(tts_engine, 4)
        total_vram = vram_per * parallel_instances
        
        analysis = f"""
╔══════════════════════════════════════════════════════════════════╗
║                   🎤 TTS GENERATION ANALYSIS                      ║
╠══════════════════════════════════════════════════════════════════╣
║  📖 NOVEL STATS                                                   ║
║  ├─ Word Count:           {word_count:>12,}                        ║
║  ├─ Character Count:      {total_chars:>12,}                        ║
║  └─ Target Speed:         {narration_speed_wpm:>12} WPM                      ║
╠══════════════════════════════════════════════════════════════════╣
║  🔊 AUDIO OUTPUT                                                  ║
║  ├─ Total Duration:       {audio_hours:>10.1f} hours                    ║
║  ├─ In Minutes:           {audio_minutes:>10.0f} min                      ║
║  └─ Audio Files:          {chunks_needed:>12} chunks                    ║
╠══════════════════════════════════════════════════════════════════╣
║  ⚙️  TTS ENGINE: {tts_engine.upper():<20}                          ║
║  ├─ Max Chars/Chunk:      {max_chars:>12}                        ║
║  ├─ Gen Speed:            {gen_speed:>12} char/sec                  ║
║  └─ VRAM per Instance:    {vram_per:>12} GB                        ║
╠══════════════════════════════════════════════════════════════════╣
║  ⏱️  GENERATION TIME (×{parallel_instances} parallel)                          ║
║  ├─ Total Time:           {gen_hours:>10.1f} hours                    ║
║  ├─ Real-Time Factor:     {rtf:>10.2f}x                        ║
║  └─ VRAM Required:        {total_vram:>12} GB                        ║
╠══════════════════════════════════════════════════════════════════╣
║  💡 RECOMMENDATIONS                                               ║
║  ├─ Chunk Size:           {max_chars:>12} chars                     ║
║  ├─ Process in Batches:   {min(50, chunks_needed):>12} at a time                ║
║  └─ Save Checkpoints:     Every {max(1, chunks_needed // 10):>6} chunks                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
        
        settings = {
            "tts_engine": tts_engine,
            "word_count": word_count,
            "total_chars": total_chars,
            "audio_hours": round(audio_hours, 2),
            "chunks_needed": chunks_needed,
            "generation_hours": round(gen_hours, 2),
            "recommended_chunk_chars": max_chars,
            "parallel_instances": parallel_instances,
            "vram_required_gb": total_vram,
            "real_time_factor": round(rtf, 2)
        }
        
        return (
            analysis.strip(),
            chunks_needed,
            round(audio_hours, 2),
            round(gen_hours, 2),
            max_chars,
            json.dumps(settings, indent=2)
        )


class NarrationToTTSChunks:
    """
    Converts narration JSON into optimized TTS chunks.
    Respects sentence boundaries and TTS length limits.
    """
    
    DESCRIPTION = """
    ✂️ Narration to TTS Chunks
    
    Splits narration into optimal chunks for TTS generation:
    • Respects sentence boundaries
    • Handles dialogue markers
    • Maintains speaker consistency
    • Outputs ready-to-process batches
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "narration_json": ("STRING", {"multiline": True}),
                "max_chars_per_chunk": ("INT", {
                    "default": 1000,
                    "min": 200,
                    "max": 3000,
                    "step": 100,
                    "tooltip": "Max characters per TTS generation"
                }),
                "overlap_words": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 20,
                    "tooltip": "Words to overlap for smoother transitions"
                }),
                "preserve_paragraphs": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Try to keep paragraphs together"
                }),
            },
            "optional": {
                "add_pauses": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Add pause markers between sections"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "FLOAT", "STRING")
    RETURN_NAMES = ("tts_chunks_json", "total_chunks", "estimated_audio_minutes", "chunk_summary")
    FUNCTION = "create_chunks"
    CATEGORY = "🎬 Story Tools/TTS"

    def create_chunks(self, narration_json: str, max_chars_per_chunk: int,
                      overlap_words: int, preserve_paragraphs: bool,
                      add_pauses: bool = True) -> Tuple[str, int, float, str]:
        
        try:
            narrations = json.loads(narration_json)
        except json.JSONDecodeError:
            return ("[]", 0, 0.0, "Error: Invalid JSON")
        
        all_chunks = []
        chunk_idx = 0
        
        for scene_idx, narration in enumerate(narrations):
            text = narration.get("text", "")
            if not text:
                continue
            
            # Clean text for TTS
            text = self._clean_for_tts(text)
            
            # Split into chunks
            if preserve_paragraphs:
                paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            else:
                paragraphs = [text]
            
            current_chunk = ""
            
            for para in paragraphs:
                # If paragraph fits, add it
                if len(current_chunk) + len(para) + 2 <= max_chars_per_chunk:
                    if current_chunk:
                        current_chunk += "\n\n" + para
                    else:
                        current_chunk = para
                else:
                    # Save current chunk if exists
                    if current_chunk:
                        all_chunks.append(self._create_chunk_obj(
                            current_chunk, chunk_idx, scene_idx, add_pauses
                        ))
                        chunk_idx += 1
                    
                    # Handle long paragraph - split by sentences
                    if len(para) > max_chars_per_chunk:
                        sentences = re.split(r'(?<=[.!?])\s+', para)
                        current_chunk = ""
                        
                        for sentence in sentences:
                            if len(current_chunk) + len(sentence) + 1 <= max_chars_per_chunk:
                                current_chunk = (current_chunk + " " + sentence).strip()
                            else:
                                if current_chunk:
                                    all_chunks.append(self._create_chunk_obj(
                                        current_chunk, chunk_idx, scene_idx, add_pauses
                                    ))
                                    chunk_idx += 1
                                
                                # Handle very long sentence
                                if len(sentence) > max_chars_per_chunk:
                                    # Split at commas or force split
                                    parts = self._force_split(sentence, max_chars_per_chunk)
                                    for part in parts[:-1]:
                                        all_chunks.append(self._create_chunk_obj(
                                            part, chunk_idx, scene_idx, add_pauses
                                        ))
                                        chunk_idx += 1
                                    current_chunk = parts[-1] if parts else ""
                                else:
                                    current_chunk = sentence
                    else:
                        current_chunk = para
            
            # Don't forget last chunk of scene
            if current_chunk:
                all_chunks.append(self._create_chunk_obj(
                    current_chunk, chunk_idx, scene_idx, add_pauses, is_scene_end=True
                ))
                chunk_idx += 1
        
        # Calculate estimated duration
        total_chars = sum(c["char_count"] for c in all_chunks)
        # Assume ~15 characters per second of speech at 150 WPM
        estimated_seconds = total_chars / 15
        estimated_minutes = estimated_seconds / 60
        
        # Summary
        summary = f"""
TTS Chunking Complete:
• Total chunks: {len(all_chunks)}
• Total characters: {total_chars:,}
• Estimated audio: {estimated_minutes:.1f} minutes ({estimated_minutes/60:.1f} hours)
• Avg chunk size: {total_chars // max(len(all_chunks), 1)} chars
• Scenes covered: {len(narrations)}
"""
        
        return (
            json.dumps(all_chunks, ensure_ascii=False, indent=2),
            len(all_chunks),
            round(estimated_minutes, 1),
            summary.strip()
        )
    
    def _clean_for_tts(self, text: str) -> str:
        """Clean text for TTS processing."""
        # Remove markdown
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        text = re.sub(r'#{1,6}\s*', '', text)
        
        # Normalize quotes for TTS
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        return text.strip()
    
    def _create_chunk_obj(self, text: str, idx: int, scene_idx: int, 
                          add_pauses: bool, is_scene_end: bool = False) -> Dict:
        """Create a chunk object."""
        # Add pause marker at end if requested
        if add_pauses and is_scene_end:
            text = text.rstrip() + " ..."
        
        word_count = len(text.split())
        
        return {
            "index": idx,
            "scene_idx": scene_idx,
            "text": text,
            "char_count": len(text),
            "word_count": word_count,
            "estimated_seconds": len(text) / 15,  # ~15 chars/sec speech
            "is_scene_end": is_scene_end,
            "id": f"tts_chunk_{idx:04d}"
        }
    
    def _force_split(self, text: str, max_len: int) -> List[str]:
        """Force split very long text at natural boundaries."""
        parts = []
        
        # Try splitting at commas first
        if ',' in text:
            segments = text.split(',')
            current = ""
            for seg in segments:
                if len(current) + len(seg) + 1 <= max_len:
                    current = (current + "," + seg).strip(',').strip()
                else:
                    if current:
                        parts.append(current)
                    current = seg.strip()
            if current:
                parts.append(current)
        else:
            # Force split at max_len
            for i in range(0, len(text), max_len):
                parts.append(text[i:i + max_len])
        
        return parts


class TTSChunkIterator:
    """
    Iterates through TTS chunks one at a time.
    """
    
    DESCRIPTION = """
    🔄 TTS Chunk Iterator
    
    Get one TTS chunk at a time for processing.
    Use with a loop to generate all audio.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tts_chunks_json": ("STRING", {"multiline": True}),
                "chunk_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 99999
                }),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "INT", "FLOAT", "BOOLEAN", "BOOLEAN")
    RETURN_NAMES = (
        "chunk_text",
        "chunk_idx",
        "total_chunks",
        "estimated_seconds",
        "is_scene_end",
        "has_more"
    )
    FUNCTION = "get_chunk"
    CATEGORY = "🎬 Story Tools/TTS"

    def get_chunk(self, tts_chunks_json: str, 
                  chunk_index: int) -> Tuple[str, int, int, float, bool, bool]:
        
        try:
            chunks = json.loads(tts_chunks_json)
        except json.JSONDecodeError:
            return ("", 0, 0, 0.0, False, False)
        
        total = len(chunks)
        
        if chunk_index >= total or chunk_index < 0:
            return ("", chunk_index, total, 0.0, False, False)
        
        chunk = chunks[chunk_index]
        has_more = chunk_index < total - 1
        
        return (
            chunk.get("text", ""),
            chunk_index,
            total,
            chunk.get("estimated_seconds", 0.0),
            chunk.get("is_scene_end", False),
            has_more
        )


class TTSBatchProcessor:
    """
    Creates batches of TTS chunks for parallel processing.
    """
    
    DESCRIPTION = """
    📦 TTS Batch Processor
    
    Groups TTS chunks into batches for parallel processing.
    Useful for multi-GPU setups or queue management.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tts_chunks_json": ("STRING", {"multiline": True}),
                "batch_size": ("INT", {
                    "default": 10,
                    "min": 1,
                    "max": 100,
                    "tooltip": "Chunks per batch"
                }),
                "batch_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9999
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "INT", "BOOLEAN")
    RETURN_NAMES = (
        "batch_texts_json",
        "batch_ids_json",
        "total_batches",
        "chunks_in_batch",
        "has_more_batches"
    )
    FUNCTION = "get_batch"
    CATEGORY = "🎬 Story Tools/TTS"

    def get_batch(self, tts_chunks_json: str, batch_size: int,
                  batch_index: int) -> Tuple[str, str, int, int, bool]:
        
        try:
            chunks = json.loads(tts_chunks_json)
        except json.JSONDecodeError:
            return ("[]", "[]", 0, 0, False)
        
        total_batches = math.ceil(len(chunks) / batch_size)
        
        if batch_index >= total_batches:
            return ("[]", "[]", total_batches, 0, False)
        
        start_idx = batch_index * batch_size
        end_idx = min(start_idx + batch_size, len(chunks))
        
        batch_chunks = chunks[start_idx:end_idx]
        
        batch_texts = [c.get("text", "") for c in batch_chunks]
        batch_ids = [c.get("id", f"chunk_{i}") for i, c in enumerate(batch_chunks)]
        
        has_more = batch_index < total_batches - 1
        
        return (
            json.dumps(batch_texts, ensure_ascii=False, indent=2),
            json.dumps(batch_ids, ensure_ascii=False, indent=2),
            total_batches,
            len(batch_chunks),
            has_more
        )


class TTSProgressTracker:
    """
    Tracks TTS generation progress with time estimates.
    """
    
    DESCRIPTION = """
    📊 TTS Progress Tracker
    
    Track progress through TTS generation with:
    • Completion percentage
    • Time remaining estimate
    • Chunks processed
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "current_chunk": ("INT", {"default": 0}),
                "total_chunks": ("INT", {"default": 100}),
                "avg_seconds_per_chunk": ("FLOAT", {
                    "default": 5.0,
                    "min": 0.1,
                    "max": 60.0,
                    "tooltip": "Average generation time per chunk"
                }),
                "elapsed_seconds": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0
                }),
            }
        }

    RETURN_TYPES = ("STRING", "FLOAT", "FLOAT", "BOOLEAN")
    RETURN_NAMES = ("progress_text", "percent_complete", "estimated_remaining_minutes", "is_complete")
    FUNCTION = "track_progress"
    CATEGORY = "🎬 Story Tools/TTS"

    def track_progress(self, current_chunk: int, total_chunks: int,
                       avg_seconds_per_chunk: float,
                       elapsed_seconds: float) -> Tuple[str, float, float, bool]:
        
        if total_chunks <= 0:
            total_chunks = 1
        
        percent = (current_chunk / total_chunks) * 100
        is_complete = current_chunk >= total_chunks
        
        # Estimate remaining time
        remaining_chunks = total_chunks - current_chunk
        
        if current_chunk > 0 and elapsed_seconds > 0:
            # Use actual average
            actual_avg = elapsed_seconds / current_chunk
            remaining_seconds = remaining_chunks * actual_avg
        else:
            remaining_seconds = remaining_chunks * avg_seconds_per_chunk
        
        remaining_minutes = remaining_seconds / 60
        
        # Progress bar
        bar_width = 40
        filled = int(bar_width * current_chunk / total_chunks)
        bar = '█' * filled + '░' * (bar_width - filled)
        
        elapsed_min = elapsed_seconds / 60
        
        progress_text = f"""
╔══════════════════════════════════════════════════════╗
║              🎤 TTS GENERATION PROGRESS              ║
╠══════════════════════════════════════════════════════╣
║  [{bar}]  ║
║  Chunks: {current_chunk:>6} / {total_chunks:<6} ({percent:>5.1f}%)           ║
╠══════════════════════════════════════════════════════╣
║  ⏱️  Elapsed:     {elapsed_min:>8.1f} minutes                  ║
║  ⏳ Remaining:   {remaining_minutes:>8.1f} minutes                  ║
║  📊 Status:      {"✅ COMPLETE!" if is_complete else "⏳ Processing...":^20}       ║
╚══════════════════════════════════════════════════════╝
"""
        
        return (
            progress_text.strip(),
            round(percent, 1),
            round(remaining_minutes, 1),
            is_complete
        )


class AudioSegmentInfo:
    """
    Generates metadata for audio segment assembly.
    """
    
    DESCRIPTION = """
    🔊 Audio Segment Info
    
    Creates metadata for assembling audio segments
    in the correct order with proper timing.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tts_chunks_json": ("STRING", {"multiline": True}),
                "output_format": (["wav", "mp3", "ogg", "flac"],),
                "sample_rate": (["22050", "44100", "48000"],),
                "crossfade_ms": ("INT", {
                    "default": 50,
                    "min": 0,
                    "max": 500,
                    "tooltip": "Crossfade between segments in milliseconds"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("assembly_config_json", "file_list_json", "total_segments")
    FUNCTION = "create_assembly_info"
    CATEGORY = "🎬 Story Tools/TTS"

    def create_assembly_info(self, tts_chunks_json: str, output_format: str,
                             sample_rate: str, 
                             crossfade_ms: int) -> Tuple[str, str, int]:
        
        try:
            chunks = json.loads(tts_chunks_json)
        except json.JSONDecodeError:
            return ("{}", "[]", 0)
        
        # Create file list
        file_list = []
        scene_breaks = []
        
        for chunk in chunks:
            file_name = f"{chunk['id']}.{output_format}"
            file_list.append({
                "file": file_name,
                "chunk_id": chunk["id"],
                "scene_idx": chunk.get("scene_idx", 0),
                "estimated_duration": chunk.get("estimated_seconds", 0),
                "is_scene_end": chunk.get("is_scene_end", False)
            })
            
            if chunk.get("is_scene_end", False):
                scene_breaks.append(chunk["index"])
        
        # Assembly config
        config = {
            "format": output_format,
            "sample_rate": int(sample_rate),
            "crossfade_ms": crossfade_ms,
            "total_segments": len(chunks),
            "scene_breaks": scene_breaks,
            "estimated_total_seconds": sum(c.get("estimated_seconds", 0) for c in chunks),
            "assembly_order": [c["id"] for c in chunks]
        }
        
        return (
            json.dumps(config, indent=2),
            json.dumps(file_list, indent=2),
            len(chunks)
        )


class DialogueSplitter:
    """
    Splits text into dialogue and narration for different voices.
    """
    
    DESCRIPTION = """
    💬 Dialogue Splitter
    
    Separates dialogue from narration for multi-voice TTS:
    • Extracts quoted dialogue
    • Identifies speakers (if tagged)
    • Keeps narration separate
    
    Useful for audiobook-style generation with different voices.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True}),
                "narrator_tag": ("STRING", {
                    "default": "NARRATOR",
                    "tooltip": "Tag for narration segments"
                }),
                "default_speaker": ("STRING", {
                    "default": "CHARACTER",
                    "tooltip": "Default tag for unattributed dialogue"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "INT", "STRING")
    RETURN_NAMES = ("segments_json", "dialogue_count", "narration_count", "speaker_list")
    FUNCTION = "split_dialogue"
    CATEGORY = "🎬 Story Tools/TTS"

    def split_dialogue(self, text: str, narrator_tag: str,
                       default_speaker: str) -> Tuple[str, int, int, str]:
        
        if not text.strip():
            return ("[]", 0, 0, "")
        
        segments = []
        speakers = set([narrator_tag])
        
        # Pattern for dialogue with optional speaker
        # Matches: "dialogue" or "dialogue," said Character or Character said, "dialogue"
        dialogue_pattern = r'(["""])([^"""]+)\1'
        
        # Find all dialogue
        last_end = 0
        dialogue_count = 0
        narration_count = 0
        
        for match in re.finditer(dialogue_pattern, text):
            # Add narration before this dialogue
            narration = text[last_end:match.start()].strip()
            if narration:
                segments.append({
                    "type": "narration",
                    "speaker": narrator_tag,
                    "text": narration,
                    "index": len(segments)
                })
                narration_count += 1
            
            # Try to find speaker attribution
            dialogue_text = match.group(2)
            speaker = default_speaker
            
            # Look for "said X" or "X said" patterns nearby
            context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
            speaker_match = re.search(r'(\b[A-Z][a-z]+)\s+said|said\s+(\b[A-Z][a-z]+)', context)
            if speaker_match:
                speaker = speaker_match.group(1) or speaker_match.group(2)
                speakers.add(speaker)
            
            segments.append({
                "type": "dialogue",
                "speaker": speaker,
                "text": dialogue_text,
                "index": len(segments)
            })
            dialogue_count += 1
            
            last_end = match.end()
        
        # Add remaining narration
        remaining = text[last_end:].strip()
        if remaining:
            segments.append({
                "type": "narration",
                "speaker": narrator_tag,
                "text": remaining,
                "index": len(segments)
            })
            narration_count += 1
        
        return (
            json.dumps(segments, ensure_ascii=False, indent=2),
            dialogue_count,
            narration_count,
            ", ".join(sorted(speakers))
        )


class VoiceAssignmentConfig:
    """
    Creates voice assignment configuration for multi-speaker TTS.
    """
    
    DESCRIPTION = """
    🎭 Voice Assignment Config
    
    Configure different voices for different speakers:
    • Narrator voice
    • Character voices
    • Voice reference audio mapping
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "characters_json": ("STRING", {"multiline": True}),
                "narrator_voice": ("STRING", {
                    "default": "default_narrator",
                    "tooltip": "Voice ID or reference for narrator"
                }),
            },
            "optional": {
                "voice_mapping": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "Elena: female_voice_1\nMarcus: male_voice_1"
                }),
                "default_male_voice": ("STRING", {"default": "default_male"}),
                "default_female_voice": ("STRING", {"default": "default_female"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("voice_config_json",)
    FUNCTION = "create_config"
    CATEGORY = "🎬 Story Tools/TTS"

    def create_config(self, characters_json: str, narrator_voice: str,
                      voice_mapping: str = "", default_male_voice: str = "default_male",
                      default_female_voice: str = "default_female") -> Tuple[str]:
        
        try:
            characters = json.loads(characters_json)
        except json.JSONDecodeError:
            characters = []
        
        # Parse voice mapping
        voice_map = {"NARRATOR": narrator_voice}
        
        if voice_mapping:
            for line in voice_mapping.strip().split('\n'):
                if ':' in line:
                    name, voice = line.split(':', 1)
                    voice_map[name.strip()] = voice.strip()
        
        # Assign default voices to unmapped characters
        for char in characters:
            name = char.get("name", "")
            if name and name not in voice_map:
                # Simple heuristic - could be improved
                voice_map[name] = default_female_voice
        
        config = {
            "narrator": narrator_voice,
            "voice_mapping": voice_map,
            "default_male": default_male_voice,
            "default_female": default_female_voice,
            "total_voices": len(set(voice_map.values()))
        }
        
        return (json.dumps(config, indent=2),)


class TTSQueueManager:
    """
    Manages a queue of TTS jobs with checkpointing.
    """
    
    DESCRIPTION = """
    📋 TTS Queue Manager
    
    Manage TTS generation queue with:
    • Checkpoint saving
    • Resume from failure
    • Progress persistence
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tts_chunks_json": ("STRING", {"multiline": True}),
                "completed_indices": ("STRING", {
                    "default": "[]",
                    "tooltip": "JSON array of completed chunk indices"
                }),
                "batch_size": ("INT", {
                    "default": 20,
                    "min": 1,
                    "max": 100
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "INT", "FLOAT", "BOOLEAN")
    RETURN_NAMES = (
        "next_batch_json",
        "next_batch_indices",
        "remaining_chunks",
        "completed_count",
        "percent_complete",
        "all_complete"
    )
    FUNCTION = "get_next_batch"
    CATEGORY = "🎬 Story Tools/TTS"

    def get_next_batch(self, tts_chunks_json: str, completed_indices: str,
                       batch_size: int) -> Tuple[str, str, int, int, float, bool]:
        
        try:
            chunks = json.loads(tts_chunks_json)
            completed = set(json.loads(completed_indices))
        except json.JSONDecodeError:
            return ("[]", "[]", 0, 0, 0.0, False)
        
        total = len(chunks)
        completed_count = len(completed)
        
        # Find remaining chunks
        remaining = [c for c in chunks if c.get("index", 0) not in completed]
        remaining_count = len(remaining)
        
        # Get next batch
        next_batch = remaining[:batch_size]
        next_indices = [c.get("index", 0) for c in next_batch]
        next_texts = [{"index": c.get("index"), "text": c.get("text", "")} for c in next_batch]
        
        percent = (completed_count / total) * 100 if total > 0 else 100.0
        all_complete = remaining_count == 0
        
        return (
            json.dumps(next_texts, ensure_ascii=False, indent=2),
            json.dumps(next_indices),
            remaining_count,
            completed_count,
            round(percent, 1),
            all_complete
        )
