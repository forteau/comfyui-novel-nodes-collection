"""
Novel Cinematic Orchestrator - Universal Batch Processing
==========================================================
Batch processing support for ALL pipeline stages:
- Image Generation
- 3D Parallax (Depthflow)
- SFX Generation (MMAudio/StableAudio)
- Video Assembly
- Final Rendering

Each stage supports:
- Configurable batch sizes
- Progress tracking
- Checkpoint/resume capability
- Queue management
"""

import json
import re
import math
from typing import List, Dict, Tuple, Any, Optional


# =============================================================================
# UNIVERSAL BATCH INFRASTRUCTURE
# =============================================================================

class UniversalBatchConfig:
    """
    Creates a unified batch configuration for the entire pipeline.
    """
    
    DESCRIPTION = """
    ⚙️ Universal Batch Config
    
    Configure batch processing for ALL pipeline stages at once:
    • Image generation batches
    • TTS batches
    • Parallax batches
    • SFX batches
    • Video assembly batches
    
    Optimizes based on your available VRAM and processing power.
    Supports high-end GPUs (A100, H100) and multi-GPU setups.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "available_vram_gb": ("INT", {
                    "default": 12,
                    "min": 4,
                    "max": 640,
                    "tooltip": "Available GPU VRAM in GB (total across all GPUs)"
                }),
                "parallel_processes": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 8,
                    "tooltip": "Number of parallel processes (GPUs)"
                }),
                "checkpoint_frequency": ("INT", {
                    "default": 50,
                    "min": 10,
                    "max": 500,
                    "tooltip": "Save checkpoint every N items"
                }),
                "image_engine": (["flux", "sdxl", "sd15", "cascade"],),
                "tts_engine": (["index_tts", "index_tts_2", "xtts", "chatterbox", "kokoro"],),
                "gpu_tier": (["consumer_12gb", "consumer_24gb", "prosumer_48gb", "datacenter_80gb", "datacenter_multi"],),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("batch_config_json", "config_summary")
    FUNCTION = "create_config"
    CATEGORY = "🎬 Story Tools/Batch Processing"

    # VRAM requirements per task (GB)
    VRAM_REQUIREMENTS = {
        "image": {"flux": 10, "sdxl": 8, "sd15": 4, "cascade": 8},
        "tts": {"index_tts": 4, "index_tts_2": 4, "xtts": 6, "chatterbox": 3, "kokoro": 2},
        "parallax": 2,  # Depthflow
        "sfx": 4,  # MMAudio
        "video": 2,  # Video assembly
    }
    
    # Optimized batch sizes by GPU tier
    GPU_PRESETS = {
        "consumer_12gb": {"image": 1, "tts": 10, "parallax": 4, "sfx": 2, "video": 5},
        "consumer_24gb": {"image": 2, "tts": 20, "parallax": 8, "sfx": 4, "video": 10},
        "prosumer_48gb": {"image": 4, "tts": 30, "parallax": 16, "sfx": 8, "video": 15},
        "datacenter_80gb": {"image": 8, "tts": 50, "parallax": 24, "sfx": 12, "video": 20},
        "datacenter_multi": {"image": 16, "tts": 100, "parallax": 32, "sfx": 20, "video": 30},
    }
    
    # Speed estimates by GPU tier (seconds per item)
    SPEED_ESTIMATES = {
        "consumer_12gb": {"image": 15, "tts": 3, "parallax": 8, "sfx": 10, "video": 5},
        "consumer_24gb": {"image": 10, "tts": 2, "parallax": 5, "sfx": 8, "video": 3},
        "prosumer_48gb": {"image": 6, "tts": 1.5, "parallax": 3, "sfx": 6, "video": 2},
        "datacenter_80gb": {"image": 4, "tts": 1, "parallax": 2, "sfx": 5, "video": 1.5},
        "datacenter_multi": {"image": 3, "tts": 0.5, "parallax": 1.5, "sfx": 4, "video": 1},
    }

    def create_config(self, available_vram_gb: int, parallel_processes: int,
                      checkpoint_frequency: int, image_engine: str,
                      tts_engine: str, gpu_tier: str) -> Tuple[str, str]:
        
        # Get presets for GPU tier
        presets = self.GPU_PRESETS.get(gpu_tier, self.GPU_PRESETS["consumer_24gb"])
        speeds = self.SPEED_ESTIMATES.get(gpu_tier, self.SPEED_ESTIMATES["consumer_24gb"])
        
        # Scale by parallel processes
        image_batch = presets["image"] * parallel_processes
        tts_batch = presets["tts"] * parallel_processes
        parallax_batch = presets["parallax"] * parallel_processes
        sfx_batch = presets["sfx"] * parallel_processes
        video_batch = presets["video"] * parallel_processes
        
        # Cap at reasonable maximums
        image_batch = min(image_batch, 16)
        parallax_batch = min(parallax_batch, 32)
        sfx_batch = min(sfx_batch, 20)
        
        # Get VRAM requirements
        image_vram = self.VRAM_REQUIREMENTS["image"].get(image_engine, 8)
        tts_vram = self.VRAM_REQUIREMENTS["tts"].get(tts_engine, 4)
        
        config = {
            "vram_available": available_vram_gb,
            "parallel_processes": parallel_processes,
            "gpu_tier": gpu_tier,
            "checkpoint_frequency": checkpoint_frequency,
            
            "image": {
                "engine": image_engine,
                "batch_size": image_batch,
                "vram_per_image": image_vram,
                "estimated_sec_per_image": speeds["image"] / parallel_processes
            },
            "tts": {
                "engine": tts_engine,
                "batch_size": tts_batch,
                "vram_required": tts_vram,
                "max_chars_per_chunk": 2000 if tts_engine in ["index_tts_2", "kokoro"] else 1000,
                "estimated_sec_per_chunk": speeds["tts"] / parallel_processes
            },
            "parallax": {
                "batch_size": parallax_batch,
                "vram_required": 2,
                "duration_per_image": 4.0,
                "estimated_sec_per_item": speeds["parallax"] / parallel_processes
            },
            "sfx": {
                "batch_size": sfx_batch,
                "vram_required": 4,
                "duration_per_clip": 5.0,
                "estimated_sec_per_item": speeds["sfx"] / parallel_processes
            },
            "video": {
                "batch_size": video_batch,
                "scenes_per_batch": video_batch,
                "estimated_sec_per_scene": speeds["video"] / parallel_processes
            }
        }
        
        # Calculate time estimates for 50k word novel (3000 images, 150 TTS, etc)
        img_time = (3000 * speeds["image"]) / parallel_processes / 3600
        tts_time = (150 * speeds["tts"]) / parallel_processes / 3600
        parallax_time = (3000 * speeds["parallax"]) / parallel_processes / 3600
        sfx_time = (150 * speeds["sfx"]) / parallel_processes / 3600
        video_time = (150 * speeds["video"]) / parallel_processes / 3600
        total_time = img_time + tts_time + parallax_time + sfx_time + video_time
        
        tier_names = {
            "consumer_12gb": "Consumer (12GB - RTX 3080/4070)",
            "consumer_24gb": "Consumer (24GB - RTX 4090)",
            "prosumer_48gb": "Prosumer (48GB - A6000/L40)",
            "datacenter_80gb": "Datacenter (80GB - A100/H100)",
            "datacenter_multi": "Multi-GPU Datacenter",
        }
        
        summary = f"""
╔══════════════════════════════════════════════════════════════════╗
║              ⚙️ UNIVERSAL BATCH CONFIGURATION                     ║
╠══════════════════════════════════════════════════════════════════╣
║  GPU Tier: {tier_names.get(gpu_tier, gpu_tier):<52} ║
║  ├─ VRAM Available:       {available_vram_gb:>6} GB                            ║
║  ├─ Parallel Processes:   {parallel_processes:>6} GPU(s)                        ║
║  └─ Checkpoint Every:     {checkpoint_frequency:>6} items                          ║
╠══════════════════════════════════════════════════════════════════╣
║  🖼️  IMAGE GENERATION ({image_engine.upper()})                               ║
║  ├─ Batch Size:           {image_batch:>6} images                           ║
║  └─ Speed:                {speeds['image']/parallel_processes:>6.1f} sec/img                        ║
╠══════════════════════════════════════════════════════════════════╣
║  🎤 TTS GENERATION ({tts_engine.upper()})                                  ║
║  ├─ Batch Size:           {tts_batch:>6} chunks                            ║
║  └─ Speed:                {speeds['tts']/parallel_processes:>6.1f} sec/chunk                       ║
╠══════════════════════════════════════════════════════════════════╣
║  🎬 3D PARALLAX (Depthflow)                                       ║
║  ├─ Batch Size:           {parallax_batch:>6} images                           ║
║  └─ Speed:                {speeds['parallax']/parallel_processes:>6.1f} sec/img                        ║
╠══════════════════════════════════════════════════════════════════╣
║  🔊 SFX GENERATION (MMAudio)                                      ║
║  ├─ Batch Size:           {sfx_batch:>6} clips                             ║
║  └─ Speed:                {speeds['sfx']/parallel_processes:>6.1f} sec/clip                        ║
╠══════════════════════════════════════════════════════════════════╣
║  🎥 VIDEO ASSEMBLY                                                ║
║  ├─ Batch Size:           {video_batch:>6} scenes                           ║
║  └─ Speed:                {speeds['video']/parallel_processes:>6.1f} sec/scene                       ║
╠══════════════════════════════════════════════════════════════════╣
║  ⏱️  50K WORD NOVEL ESTIMATE                                       ║
║  ├─ Images (3000):        {img_time:>6.1f} hours                           ║
║  ├─ TTS (150 chunks):     {tts_time*60:>6.0f} min                             ║
║  ├─ Parallax (3000):      {parallax_time:>6.1f} hours                           ║
║  ├─ SFX (150 clips):      {sfx_time*60:>6.0f} min                             ║
║  ├─ Video (150 scenes):   {video_time*60:>6.0f} min                             ║
║  └─ TOTAL:                {total_time:>6.1f} hours                           ║
╚══════════════════════════════════════════════════════════════════╝
"""
        
        return (json.dumps(config, indent=2), summary.strip())


class PipelineProgressTracker:
    """
    Tracks progress across ALL pipeline stages.
    """
    
    DESCRIPTION = """
    📊 Pipeline Progress Tracker
    
    Track progress across the entire pipeline:
    • Images generated
    • TTS chunks completed
    • Parallax animations done
    • SFX clips created
    • Video segments assembled
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "total_images": ("INT", {"default": 1000}),
                "total_tts_chunks": ("INT", {"default": 300}),
                "total_parallax": ("INT", {"default": 1000}),
                "total_sfx": ("INT", {"default": 100}),
                "total_video_segments": ("INT", {"default": 100}),
                
                "completed_images": ("INT", {"default": 0}),
                "completed_tts": ("INT", {"default": 0}),
                "completed_parallax": ("INT", {"default": 0}),
                "completed_sfx": ("INT", {"default": 0}),
                "completed_video": ("INT", {"default": 0}),
            }
        }

    RETURN_TYPES = ("STRING", "FLOAT", "STRING")
    RETURN_NAMES = ("progress_display", "overall_percent", "stage_status")
    FUNCTION = "track_progress"
    CATEGORY = "🎬 Story Tools/Batch Processing"

    def track_progress(self, total_images: int, total_tts_chunks: int,
                       total_parallax: int, total_sfx: int, total_video_segments: int,
                       completed_images: int, completed_tts: int,
                       completed_parallax: int, completed_sfx: int,
                       completed_video: int) -> Tuple[str, float, str]:
        
        def pct(done, total):
            return (done / max(total, 1)) * 100
        
        def bar(done, total, width=20):
            filled = int(width * done / max(total, 1))
            return '█' * filled + '░' * (width - filled)
        
        def status(done, total):
            if done >= total:
                return "✅ Complete"
            elif done > 0:
                return "⏳ In Progress"
            else:
                return "⏸️ Pending"
        
        # Calculate overall progress (weighted by typical time)
        weights = {"image": 0.50, "tts": 0.10, "parallax": 0.20, "sfx": 0.10, "video": 0.10}
        
        overall = (
            weights["image"] * pct(completed_images, total_images) +
            weights["tts"] * pct(completed_tts, total_tts_chunks) +
            weights["parallax"] * pct(completed_parallax, total_parallax) +
            weights["sfx"] * pct(completed_sfx, total_sfx) +
            weights["video"] * pct(completed_video, total_video_segments)
        )
        
        display = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    📊 PIPELINE PROGRESS                               ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  🖼️  Images:    [{bar(completed_images, total_images)}] {pct(completed_images, total_images):>5.1f}%    ║
║                 {completed_images:>6} / {total_images:<6} {status(completed_images, total_images):>15}   ║
║                                                                       ║
║  🎤 TTS:       [{bar(completed_tts, total_tts_chunks)}] {pct(completed_tts, total_tts_chunks):>5.1f}%    ║
║                 {completed_tts:>6} / {total_tts_chunks:<6} {status(completed_tts, total_tts_chunks):>15}   ║
║                                                                       ║
║  🎬 Parallax:  [{bar(completed_parallax, total_parallax)}] {pct(completed_parallax, total_parallax):>5.1f}%    ║
║                 {completed_parallax:>6} / {total_parallax:<6} {status(completed_parallax, total_parallax):>15}   ║
║                                                                       ║
║  🔊 SFX:       [{bar(completed_sfx, total_sfx)}] {pct(completed_sfx, total_sfx):>5.1f}%    ║
║                 {completed_sfx:>6} / {total_sfx:<6} {status(completed_sfx, total_sfx):>15}   ║
║                                                                       ║
║  🎥 Video:     [{bar(completed_video, total_video_segments)}] {pct(completed_video, total_video_segments):>5.1f}%    ║
║                 {completed_video:>6} / {total_video_segments:<6} {status(completed_video, total_video_segments):>15}   ║
║                                                                       ║
╠══════════════════════════════════════════════════════════════════════╣
║  OVERALL:      [{bar(int(overall), 100, 30)}] {overall:>5.1f}%  ║
╚══════════════════════════════════════════════════════════════════════╝
"""
        
        stage_status = json.dumps({
            "images": {"done": completed_images, "total": total_images, "percent": round(pct(completed_images, total_images), 1)},
            "tts": {"done": completed_tts, "total": total_tts_chunks, "percent": round(pct(completed_tts, total_tts_chunks), 1)},
            "parallax": {"done": completed_parallax, "total": total_parallax, "percent": round(pct(completed_parallax, total_parallax), 1)},
            "sfx": {"done": completed_sfx, "total": total_sfx, "percent": round(pct(completed_sfx, total_sfx), 1)},
            "video": {"done": completed_video, "total": total_video_segments, "percent": round(pct(completed_video, total_video_segments), 1)},
            "overall": round(overall, 1)
        }, indent=2)
        
        return (display.strip(), round(overall, 1), stage_status)


# =============================================================================
# IMAGE GENERATION BATCHING
# =============================================================================

class ImageBatchGenerator:
    """
    Creates optimized image generation batches.
    """
    
    DESCRIPTION = """
    🖼️ Image Batch Generator
    
    Creates batches of image prompts for efficient generation:
    • Optimized batch sizes for your GPU
    • Checkpoint support
    • Progress tracking
    • Resume capability
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_prompts_json": ("STRING", {"multiline": True}),
                "batch_size": ("INT", {
                    "default": 4,
                    "min": 1,
                    "max": 16,
                    "tooltip": "Images per batch"
                }),
                "batch_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 99999
                }),
            },
            "optional": {
                "completed_indices": ("STRING", {
                    "default": "[]",
                    "tooltip": "JSON array of already completed image indices"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "INT", "INT", "BOOLEAN")
    RETURN_NAMES = (
        "batch_prompts_json",
        "batch_negative_prompts_json", 
        "batch_ids_json",
        "total_batches",
        "images_in_batch",
        "has_more"
    )
    FUNCTION = "create_batch"
    CATEGORY = "🎬 Story Tools/Batch Processing"

    def create_batch(self, image_prompts_json: str, batch_size: int,
                     batch_index: int, 
                     completed_indices: str = "[]") -> Tuple[str, str, str, int, int, bool]:
        
        try:
            # Handle nested array (prompts per scene)
            all_prompts = json.loads(image_prompts_json)
            completed = set(json.loads(completed_indices))
        except json.JSONDecodeError:
            return ("[]", "[]", "[]", 0, 0, False)
        
        # Flatten nested prompts
        flat_prompts = []
        if all_prompts and isinstance(all_prompts[0], list):
            for scene_prompts in all_prompts:
                flat_prompts.extend(scene_prompts)
        else:
            flat_prompts = all_prompts
        
        # Filter out completed
        remaining = [p for i, p in enumerate(flat_prompts) if i not in completed]
        
        total_batches = math.ceil(len(remaining) / batch_size)
        
        if batch_index >= total_batches:
            return ("[]", "[]", "[]", total_batches, 0, False)
        
        start = batch_index * batch_size
        end = min(start + batch_size, len(remaining))
        batch = remaining[start:end]
        
        prompts = [p.get("prompt", "") for p in batch]
        negatives = [p.get("negative_prompt", "") for p in batch]
        ids = [p.get("id", f"img_{i}") for i, p in enumerate(batch)]
        
        has_more = batch_index < total_batches - 1
        
        return (
            json.dumps(prompts, ensure_ascii=False),
            json.dumps(negatives, ensure_ascii=False),
            json.dumps(ids),
            total_batches,
            len(batch),
            has_more
        )


class ImageBatchToIndividual:
    """
    Extracts individual prompts from a batch for single processing.
    """
    
    DESCRIPTION = """
    🖼️ Image Batch to Individual
    
    Extract one prompt at a time from a batch.
    Useful for samplers that don't support batching.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "batch_prompts_json": ("STRING", {"multiline": True}),
                "batch_negatives_json": ("STRING", {"multiline": True}),
                "batch_ids_json": ("STRING", {"multiline": True}),
                "index": ("INT", {"default": 0, "min": 0}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "INT", "BOOLEAN")
    RETURN_NAMES = ("prompt", "negative_prompt", "image_id", "total_in_batch", "has_more")
    FUNCTION = "get_individual"
    CATEGORY = "🎬 Story Tools/Batch Processing"

    def get_individual(self, batch_prompts_json: str, batch_negatives_json: str,
                       batch_ids_json: str, index: int) -> Tuple[str, str, str, int, bool]:
        
        try:
            prompts = json.loads(batch_prompts_json)
            negatives = json.loads(batch_negatives_json)
            ids = json.loads(batch_ids_json)
        except json.JSONDecodeError:
            return ("", "", "", 0, False)
        
        total = len(prompts)
        
        if index >= total:
            return ("", "", "", total, False)
        
        return (
            prompts[index],
            negatives[index] if index < len(negatives) else "",
            ids[index] if index < len(ids) else f"img_{index}",
            total,
            index < total - 1
        )


# =============================================================================
# 3D PARALLAX (DEPTHFLOW) BATCHING
# =============================================================================

class ParallaxBatchGenerator:
    """
    Creates batches for 3D parallax animation generation.
    """
    
    DESCRIPTION = """
    🎬 Parallax Batch Generator
    
    Create batches for Depthflow 3D parallax animation:
    • Groups images for batch processing
    • Configures animation parameters
    • Tracks progress
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_ids_json": ("STRING", {
                    "multiline": True,
                    "tooltip": "JSON array of image IDs that need parallax"
                }),
                "batch_size": ("INT", {
                    "default": 8,
                    "min": 1,
                    "max": 32
                }),
                "batch_index": ("INT", {
                    "default": 0,
                    "min": 0
                }),
                "animation_duration": ("FLOAT", {
                    "default": 4.0,
                    "min": 1.0,
                    "max": 15.0,
                    "step": 0.5,
                    "tooltip": "Duration of each parallax animation in seconds"
                }),
                "animation_style": (["zoom_in", "zoom_out", "pan_left", "pan_right", "orbit", "dolly", "random"],),
                "depth_intensity": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.1,
                    "max": 1.0,
                    "step": 0.1
                }),
            },
            "optional": {
                "completed_indices": ("STRING", {"default": "[]"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "INT", "BOOLEAN", "STRING")
    RETURN_NAMES = (
        "batch_ids_json",
        "batch_config_json",
        "total_batches",
        "items_in_batch",
        "has_more",
        "progress_text"
    )
    FUNCTION = "create_batch"
    CATEGORY = "🎬 Story Tools/Batch Processing"

    def create_batch(self, image_ids_json: str, batch_size: int, batch_index: int,
                     animation_duration: float, animation_style: str,
                     depth_intensity: float,
                     completed_indices: str = "[]") -> Tuple[str, str, int, int, bool, str]:
        
        try:
            all_ids = json.loads(image_ids_json)
            completed = set(json.loads(completed_indices))
        except json.JSONDecodeError:
            return ("[]", "{}", 0, 0, False, "Error: Invalid JSON")
        
        # Filter remaining
        remaining = [id for i, id in enumerate(all_ids) if i not in completed]
        
        total_batches = math.ceil(len(remaining) / batch_size)
        
        if batch_index >= total_batches:
            return ("[]", "{}", total_batches, 0, False, "All batches complete")
        
        start = batch_index * batch_size
        end = min(start + batch_size, len(remaining))
        batch_ids = remaining[start:end]
        
        # Create config for each item in batch
        batch_config = {
            "duration": animation_duration,
            "style": animation_style,
            "depth_intensity": depth_intensity,
            "fps": 30,
            "items": [
                {
                    "id": img_id,
                    "input_image": f"{img_id}.png",
                    "output_video": f"{img_id}_parallax.mp4",
                    "style": animation_style if animation_style != "random" else 
                             ["zoom_in", "zoom_out", "pan_left", "pan_right", "orbit"][hash(img_id) % 5]
                }
                for img_id in batch_ids
            ]
        }
        
        has_more = batch_index < total_batches - 1
        completed_count = len(completed)
        total_items = len(all_ids)
        
        progress = f"Parallax: Batch {batch_index + 1}/{total_batches} | {completed_count}/{total_items} complete ({(completed_count/max(total_items,1)*100):.1f}%)"
        
        return (
            json.dumps(batch_ids),
            json.dumps(batch_config, indent=2),
            total_batches,
            len(batch_ids),
            has_more,
            progress
        )


class ParallaxItemIterator:
    """
    Iterates through parallax batch items one at a time.
    """
    
    DESCRIPTION = """
    🔄 Parallax Item Iterator
    
    Process parallax animations one at a time from a batch.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "batch_config_json": ("STRING", {"multiline": True}),
                "item_index": ("INT", {"default": 0, "min": 0}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "FLOAT", "FLOAT", "INT", "BOOLEAN")
    RETURN_NAMES = (
        "image_id",
        "input_image_path",
        "output_video_path",
        "duration",
        "depth_intensity",
        "total_in_batch",
        "has_more"
    )
    FUNCTION = "get_item"
    CATEGORY = "🎬 Story Tools/Batch Processing"

    def get_item(self, batch_config_json: str, 
                 item_index: int) -> Tuple[str, str, str, float, float, int, bool]:
        
        try:
            config = json.loads(batch_config_json)
        except json.JSONDecodeError:
            return ("", "", "", 4.0, 0.5, 0, False)
        
        items = config.get("items", [])
        total = len(items)
        
        if item_index >= total:
            return ("", "", "", 4.0, 0.5, total, False)
        
        item = items[item_index]
        
        return (
            item.get("id", ""),
            item.get("input_image", ""),
            item.get("output_video", ""),
            config.get("duration", 4.0),
            config.get("depth_intensity", 0.5),
            total,
            item_index < total - 1
        )


# =============================================================================
# SFX GENERATION (MMAudio) BATCHING
# =============================================================================

class SFXBatchGenerator:
    """
    Creates batches for SFX/audio generation.
    """
    
    DESCRIPTION = """
    🔊 SFX Batch Generator
    
    Create batches for MMAudio/StableAudio SFX generation:
    • Groups SFX cues by scene
    • Configures audio parameters
    • Supports both MMAudio and StableAudio
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "sfx_cues_json": ("STRING", {"multiline": True}),
                "batch_size": ("INT", {
                    "default": 5,
                    "min": 1,
                    "max": 20
                }),
                "batch_index": ("INT", {"default": 0, "min": 0}),
                "sfx_duration": ("FLOAT", {
                    "default": 5.0,
                    "min": 1.0,
                    "max": 30.0,
                    "tooltip": "Duration of each SFX clip in seconds"
                }),
                "sfx_engine": (["mmaudio", "stable_audio", "audioldm2"],),
            },
            "optional": {
                "completed_indices": ("STRING", {"default": "[]"}),
                "video_sync": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Sync SFX to video (MMAudio)"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "INT", "BOOLEAN", "STRING")
    RETURN_NAMES = (
        "batch_prompts_json",
        "batch_config_json",
        "total_batches",
        "items_in_batch",
        "has_more",
        "progress_text"
    )
    FUNCTION = "create_batch"
    CATEGORY = "🎬 Story Tools/Batch Processing"

    def create_batch(self, sfx_cues_json: str, batch_size: int, batch_index: int,
                     sfx_duration: float, sfx_engine: str,
                     completed_indices: str = "[]",
                     video_sync: bool = True) -> Tuple[str, str, int, int, bool, str]:
        
        try:
            all_cues = json.loads(sfx_cues_json)
            completed = set(json.loads(completed_indices))
        except json.JSONDecodeError:
            return ("[]", "{}", 0, 0, False, "Error: Invalid JSON")
        
        # Flatten if nested by scene
        flat_cues = []
        for i, cue in enumerate(all_cues):
            if isinstance(cue, dict):
                flat_cues.append({
                    "index": i,
                    "scene_idx": cue.get("scene_idx", i),
                    "prompt": cue.get("combined_prompt", "ambient sound"),
                    "cues": cue.get("cues", [])
                })
        
        # Filter remaining
        remaining = [c for c in flat_cues if c["index"] not in completed]
        
        total_batches = math.ceil(len(remaining) / batch_size)
        
        if batch_index >= total_batches:
            return ("[]", "{}", total_batches, 0, False, "All batches complete")
        
        start = batch_index * batch_size
        end = min(start + batch_size, len(remaining))
        batch = remaining[start:end]
        
        batch_prompts = [c["prompt"] for c in batch]
        
        batch_config = {
            "engine": sfx_engine,
            "duration": sfx_duration,
            "video_sync": video_sync,
            "sample_rate": 44100,
            "items": [
                {
                    "index": c["index"],
                    "scene_idx": c["scene_idx"],
                    "prompt": c["prompt"],
                    "output_file": f"sfx_scene_{c['scene_idx']:03d}.wav"
                }
                for c in batch
            ]
        }
        
        has_more = batch_index < total_batches - 1
        completed_count = len(completed)
        total_items = len(flat_cues)
        
        progress = f"SFX: Batch {batch_index + 1}/{total_batches} | {completed_count}/{total_items} complete ({(completed_count/max(total_items,1)*100):.1f}%)"
        
        return (
            json.dumps(batch_prompts),
            json.dumps(batch_config, indent=2),
            total_batches,
            len(batch),
            has_more,
            progress
        )


class SFXItemIterator:
    """
    Iterates through SFX batch items one at a time.
    """
    
    DESCRIPTION = """
    🔄 SFX Item Iterator
    
    Process SFX generations one at a time from a batch.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "batch_config_json": ("STRING", {"multiline": True}),
                "item_index": ("INT", {"default": 0, "min": 0}),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "STRING", "FLOAT", "INT", "BOOLEAN")
    RETURN_NAMES = (
        "sfx_prompt",
        "scene_idx",
        "output_file",
        "duration",
        "total_in_batch",
        "has_more"
    )
    FUNCTION = "get_item"
    CATEGORY = "🎬 Story Tools/Batch Processing"

    def get_item(self, batch_config_json: str, 
                 item_index: int) -> Tuple[str, int, str, float, int, bool]:
        
        try:
            config = json.loads(batch_config_json)
        except json.JSONDecodeError:
            return ("", 0, "", 5.0, 0, False)
        
        items = config.get("items", [])
        total = len(items)
        
        if item_index >= total:
            return ("", 0, "", 5.0, total, False)
        
        item = items[item_index]
        
        return (
            item.get("prompt", ""),
            item.get("scene_idx", 0),
            item.get("output_file", ""),
            config.get("duration", 5.0),
            total,
            item_index < total - 1
        )


# =============================================================================
# VIDEO ASSEMBLY BATCHING
# =============================================================================

class VideoAssemblyBatcher:
    """
    Creates batches for video assembly.
    """
    
    DESCRIPTION = """
    🎥 Video Assembly Batcher
    
    Create batches for video assembly:
    • Groups scenes for rendering
    • Configures transitions
    • Handles audio sync
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "scenes_json": ("STRING", {"multiline": True}),
                "parallax_config": ("STRING", {"multiline": True}),
                "audio_config": ("STRING", {"multiline": True}),
                "batch_size": ("INT", {
                    "default": 5,
                    "min": 1,
                    "max": 20,
                    "tooltip": "Scenes per batch"
                }),
                "batch_index": ("INT", {"default": 0, "min": 0}),
                "transition_type": (["crossfade", "fade_black", "cut", "wipe", "dissolve"],),
                "transition_duration": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1
                }),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "INT", "BOOLEAN", "STRING")
    RETURN_NAMES = (
        "batch_assembly_config",
        "total_batches",
        "scenes_in_batch",
        "has_more",
        "progress_text"
    )
    FUNCTION = "create_batch"
    CATEGORY = "🎬 Story Tools/Batch Processing"

    def create_batch(self, scenes_json: str, parallax_config: str,
                     audio_config: str, batch_size: int, batch_index: int,
                     transition_type: str, 
                     transition_duration: float) -> Tuple[str, int, int, bool, str]:
        
        try:
            scenes = json.loads(scenes_json)
        except json.JSONDecodeError:
            return ("{}", 0, 0, False, "Error: Invalid JSON")
        
        total_scenes = len(scenes)
        total_batches = math.ceil(total_scenes / batch_size)
        
        if batch_index >= total_batches:
            return ("{}", total_batches, 0, False, "All batches complete")
        
        start = batch_index * batch_size
        end = min(start + batch_size, total_scenes)
        batch_scenes = scenes[start:end]
        
        assembly_config = {
            "batch_index": batch_index,
            "scene_range": [start, end - 1],
            "transition": {
                "type": transition_type,
                "duration": transition_duration
            },
            "output_file": f"video_batch_{batch_index:03d}.mp4",
            "scenes": [
                {
                    "id": s.get("id", f"scene_{i}"),
                    "index": start + i,
                    "video_file": f"{s.get('id', f'scene_{start+i}')}_parallax.mp4",
                    "audio_file": f"tts_{s.get('id', f'scene_{start+i}')}.wav",
                    "sfx_file": f"sfx_{s.get('id', f'scene_{start+i}')}.wav",
                }
                for i, s in enumerate(batch_scenes)
            ],
            "fps": 30,
            "resolution": "1920x1080"
        }
        
        has_more = batch_index < total_batches - 1
        progress = f"Video: Batch {batch_index + 1}/{total_batches} | Scenes {start+1}-{end} of {total_scenes}"
        
        return (
            json.dumps(assembly_config, indent=2),
            total_batches,
            len(batch_scenes),
            has_more,
            progress
        )


class VideoSegmentIterator:
    """
    Iterates through video segments for assembly.
    """
    
    DESCRIPTION = """
    🔄 Video Segment Iterator
    
    Process video segments one at a time for assembly.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "batch_assembly_config": ("STRING", {"multiline": True}),
                "segment_index": ("INT", {"default": 0, "min": 0}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "INT", "INT", "BOOLEAN")
    RETURN_NAMES = (
        "scene_id",
        "video_file",
        "audio_file",
        "sfx_file",
        "scene_index",
        "total_in_batch",
        "has_more"
    )
    FUNCTION = "get_segment"
    CATEGORY = "🎬 Story Tools/Batch Processing"

    def get_segment(self, batch_assembly_config: str,
                    segment_index: int) -> Tuple[str, str, str, str, int, int, bool]:
        
        try:
            config = json.loads(batch_assembly_config)
        except json.JSONDecodeError:
            return ("", "", "", "", 0, 0, False)
        
        scenes = config.get("scenes", [])
        total = len(scenes)
        
        if segment_index >= total:
            return ("", "", "", "", 0, total, False)
        
        scene = scenes[segment_index]
        
        return (
            scene.get("id", ""),
            scene.get("video_file", ""),
            scene.get("audio_file", ""),
            scene.get("sfx_file", ""),
            scene.get("index", segment_index),
            total,
            segment_index < total - 1
        )


# =============================================================================
# CHECKPOINT & RESUME SUPPORT
# =============================================================================

class CheckpointManager:
    """
    Manages checkpoints for long-running pipeline operations.
    """
    
    DESCRIPTION = """
    💾 Checkpoint Manager
    
    Save and restore pipeline progress:
    • Save completed indices
    • Resume from failure
    • Track progress across sessions
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "stage": (["images", "tts", "parallax", "sfx", "video"],),
                "completed_indices_json": ("STRING", {
                    "default": "[]",
                    "multiline": True
                }),
                "new_completed_index": ("INT", {"default": -1}),
                "total_items": ("INT", {"default": 100}),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "FLOAT", "BOOLEAN", "STRING")
    RETURN_NAMES = (
        "updated_indices_json",
        "completed_count",
        "percent_complete",
        "all_complete",
        "checkpoint_status"
    )
    FUNCTION = "update_checkpoint"
    CATEGORY = "🎬 Story Tools/Batch Processing"

    def update_checkpoint(self, stage: str, completed_indices_json: str,
                          new_completed_index: int,
                          total_items: int) -> Tuple[str, int, float, bool, str]:
        
        try:
            completed = set(json.loads(completed_indices_json))
        except json.JSONDecodeError:
            completed = set()
        
        # Add new completed index if valid
        if new_completed_index >= 0:
            completed.add(new_completed_index)
        
        completed_count = len(completed)
        percent = (completed_count / max(total_items, 1)) * 100
        all_complete = completed_count >= total_items
        
        status = f"{stage.upper()}: {completed_count}/{total_items} ({percent:.1f}%) {'✅ COMPLETE' if all_complete else '⏳ In Progress'}"
        
        return (
            json.dumps(sorted(list(completed))),
            completed_count,
            round(percent, 1),
            all_complete,
            status
        )


class BatchResumeHelper:
    """
    Helps resume batch processing from a checkpoint.
    """
    
    DESCRIPTION = """
    🔄 Batch Resume Helper
    
    Calculate where to resume batch processing:
    • Finds next uncompleted batch
    • Skips completed items
    • Calculates remaining work
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "completed_indices_json": ("STRING", {"multiline": True}),
                "total_items": ("INT", {"default": 100}),
                "batch_size": ("INT", {"default": 10}),
            }
        }

    RETURN_TYPES = ("INT", "INT", "INT", "FLOAT", "STRING")
    RETURN_NAMES = (
        "resume_batch_index",
        "remaining_items",
        "remaining_batches",
        "estimated_time_hours",
        "resume_summary"
    )
    FUNCTION = "calculate_resume"
    CATEGORY = "🎬 Story Tools/Batch Processing"

    def calculate_resume(self, completed_indices_json: str, total_items: int,
                         batch_size: int) -> Tuple[int, int, int, float, str]:
        
        try:
            completed = set(json.loads(completed_indices_json))
        except json.JSONDecodeError:
            completed = set()
        
        completed_count = len(completed)
        remaining = total_items - completed_count
        
        # Find first incomplete batch
        resume_batch = 0
        for i in range(0, total_items, batch_size):
            batch_indices = set(range(i, min(i + batch_size, total_items)))
            if not batch_indices.issubset(completed):
                resume_batch = i // batch_size
                break
        
        remaining_batches = math.ceil(remaining / batch_size)
        
        # Estimate time (assuming 10 seconds per item average)
        estimated_seconds = remaining * 10
        estimated_hours = estimated_seconds / 3600
        
        summary = f"""
Resume Point:
• Completed: {completed_count}/{total_items} items
• Resume at batch: {resume_batch}
• Remaining: {remaining} items ({remaining_batches} batches)
• Est. time remaining: {estimated_hours:.1f} hours
"""
        
        return (
            resume_batch,
            remaining,
            remaining_batches,
            round(estimated_hours, 1),
            summary.strip()
        )


# =============================================================================
# TIME ESTIMATION
# =============================================================================

class PipelineTimeEstimator:
    """
    Estimates total time for the entire pipeline.
    """
    
    DESCRIPTION = """
    ⏱️ Pipeline Time Estimator
    
    Estimate total time for all pipeline stages:
    • Image generation time
    • TTS generation time
    • Parallax rendering time
    • SFX generation time
    • Video assembly time
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "total_images": ("INT", {"default": 3000}),
                "total_tts_chunks": ("INT", {"default": 300}),
                "total_parallax": ("INT", {"default": 3000}),
                "total_sfx": ("INT", {"default": 150}),
                "total_video_scenes": ("INT", {"default": 150}),
                
                "sec_per_image": ("FLOAT", {"default": 10.0, "min": 1.0, "max": 60.0}),
                "sec_per_tts": ("FLOAT", {"default": 2.0, "min": 0.5, "max": 30.0}),
                "sec_per_parallax": ("FLOAT", {"default": 5.0, "min": 1.0, "max": 30.0}),
                "sec_per_sfx": ("FLOAT", {"default": 8.0, "min": 1.0, "max": 60.0}),
                "sec_per_video_scene": ("FLOAT", {"default": 3.0, "min": 0.5, "max": 30.0}),
                
                "parallel_factor": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.5,
                    "max": 4.0,
                    "tooltip": "Speedup from parallel processing"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "FLOAT", "STRING")
    RETURN_NAMES = ("time_breakdown", "total_hours", "schedule_suggestion")
    FUNCTION = "estimate_time"
    CATEGORY = "🎬 Story Tools/Batch Processing"

    def estimate_time(self, total_images: int, total_tts_chunks: int,
                      total_parallax: int, total_sfx: int, total_video_scenes: int,
                      sec_per_image: float, sec_per_tts: float,
                      sec_per_parallax: float, sec_per_sfx: float,
                      sec_per_video_scene: float,
                      parallel_factor: float) -> Tuple[str, float, str]:
        
        # Calculate times
        image_time = (total_images * sec_per_image) / parallel_factor
        tts_time = (total_tts_chunks * sec_per_tts) / parallel_factor
        parallax_time = (total_parallax * sec_per_parallax) / parallel_factor
        sfx_time = (total_sfx * sec_per_sfx) / parallel_factor
        video_time = (total_video_scenes * sec_per_video_scene) / parallel_factor
        
        total_seconds = image_time + tts_time + parallax_time + sfx_time + video_time
        total_hours = total_seconds / 3600
        
        def fmt_time(seconds):
            hours = seconds / 3600
            if hours >= 1:
                return f"{hours:.1f} hrs"
            else:
                return f"{seconds/60:.0f} min"
        
        breakdown = f"""
╔══════════════════════════════════════════════════════════════════╗
║                  ⏱️ PIPELINE TIME ESTIMATE                        ║
╠══════════════════════════════════════════════════════════════════╣
║  Stage              Items        Time/Item     Total Time         ║
╠══════════════════════════════════════════════════════════════════╣
║  🖼️ Images         {total_images:>6}        {sec_per_image:>5.1f}s        {fmt_time(image_time):>10}          ║
║  🎤 TTS            {total_tts_chunks:>6}        {sec_per_tts:>5.1f}s        {fmt_time(tts_time):>10}          ║
║  🎬 Parallax       {total_parallax:>6}        {sec_per_parallax:>5.1f}s        {fmt_time(parallax_time):>10}          ║
║  🔊 SFX            {total_sfx:>6}        {sec_per_sfx:>5.1f}s        {fmt_time(sfx_time):>10}          ║
║  🎥 Video          {total_video_scenes:>6}        {sec_per_video_scene:>5.1f}s        {fmt_time(video_time):>10}          ║
╠══════════════════════════════════════════════════════════════════╣
║  TOTAL TIME (×{parallel_factor:.1f} parallel):                {total_hours:>8.1f} hours          ║
╚══════════════════════════════════════════════════════════════════╝
"""
        
        # Schedule suggestion
        if total_hours <= 2:
            schedule = "Quick job! Can complete in one sitting."
        elif total_hours <= 8:
            schedule = "Medium job. Consider running overnight."
        elif total_hours <= 24:
            schedule = "Long job. Run overnight or split across 2-3 days."
        else:
            days = math.ceil(total_hours / 24)
            schedule = f"Very long job (~{days} days). Strongly recommend:\n• Process images first (largest task)\n• Save checkpoints frequently\n• Split into multiple sessions"
        
        return (breakdown.strip(), round(total_hours, 1), schedule)
