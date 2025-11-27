"""
Novel Cinematic Orchestrator
=============================
A comprehensive ComfyUI custom node pack for transforming novels and stories
into complete cinematic video production plans.

Features:
- Intelligent scene segmentation
- Character extraction and consistency tracking
- Image prompt generation with style support
- Narration text processing for TTS
- SFX cue generation for audio
- Helper nodes for pipeline integration

Compatible with:
- IndexTTS / IndexTTS-2 for voice cloning
- Depthflow for 3D parallax effects
- MMAudio / StableAudio for SFX generation
- Flux / SDXL / SD1.5 for image generation
- VideoHelperSuite for video assembly

Author: Claude AI Assistant
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Claude AI"

# Import main orchestrator
from .orchestrator import NovelCinematicOrchestrator

# Import helper nodes
from .helpers import (
    PromptBatcher,
    SceneIterator,
    NarrationIterator,
    SFXCueIterator,
    ImagePromptIterator,
    ConfigExtractor,
    CharacterExtractor,
    NarrationChunker,
    SceneToVideoConfig,
    LoRAProfileParser,
    EngineSelector,
    TextCombiner
)

# Import large novel support nodes
from .large_novel_support import (
    NovelFileLoader,
    NovelTextSplitter,
    ChunkIterator,
    OutputMerger,
    ProgressTracker,
    LargeNovelStats,
    MemoryOptimizedOrchestrator
)

# Import enhanced coverage nodes
from .enhanced_coverage import (
    ImageCoverageCalculator,
    AdaptiveDensityOrchestrator,
    KeyMomentExtractor,
    EnhancedPromptGenerator
)

# Import TTS support nodes
from .tts_support import (
    TTSCoverageCalculator,
    NarrationToTTSChunks,
    TTSChunkIterator,
    TTSBatchProcessor,
    TTSProgressTracker,
    AudioSegmentInfo,
    DialogueSplitter,
    VoiceAssignmentConfig,
    TTSQueueManager
)

# Import batch processing nodes
from .batch_processing import (
    UniversalBatchConfig,
    PipelineProgressTracker,
    ImageBatchGenerator,
    ImageBatchToIndividual,
    ParallaxBatchGenerator,
    ParallaxItemIterator,
    SFXBatchGenerator,
    SFXItemIterator,
    VideoAssemblyBatcher,
    VideoSegmentIterator,
    CheckpointManager,
    BatchResumeHelper,
    PipelineTimeEstimator
)

# Node class mappings for ComfyUI registration
NODE_CLASS_MAPPINGS = {
    # Main orchestrator
    "NovelCinematicOrchestrator": NovelCinematicOrchestrator,
    
    # Large novel support
    "NovelFileLoader": NovelFileLoader,
    "NovelTextSplitter": NovelTextSplitter,
    "ChunkIterator": ChunkIterator,
    "OutputMerger": OutputMerger,
    "ProgressTracker": ProgressTracker,
    "LargeNovelStats": LargeNovelStats,
    "MemoryOptimizedOrchestrator": MemoryOptimizedOrchestrator,
    
    # Enhanced coverage & adaptive density
    "ImageCoverageCalculator": ImageCoverageCalculator,
    "AdaptiveDensityOrchestrator": AdaptiveDensityOrchestrator,
    "KeyMomentExtractor": KeyMomentExtractor,
    "EnhancedPromptGenerator": EnhancedPromptGenerator,
    
    # TTS Support
    "TTSCoverageCalculator": TTSCoverageCalculator,
    "NarrationToTTSChunks": NarrationToTTSChunks,
    "TTSChunkIterator": TTSChunkIterator,
    "TTSBatchProcessor": TTSBatchProcessor,
    "TTSProgressTracker": TTSProgressTracker,
    "AudioSegmentInfo": AudioSegmentInfo,
    "DialogueSplitter": DialogueSplitter,
    "VoiceAssignmentConfig": VoiceAssignmentConfig,
    "TTSQueueManager": TTSQueueManager,
    
    # Batch Processing - Universal
    "UniversalBatchConfig": UniversalBatchConfig,
    "PipelineProgressTracker": PipelineProgressTracker,
    "CheckpointManager": CheckpointManager,
    "BatchResumeHelper": BatchResumeHelper,
    "PipelineTimeEstimator": PipelineTimeEstimator,
    
    # Batch Processing - Images
    "ImageBatchGenerator": ImageBatchGenerator,
    "ImageBatchToIndividual": ImageBatchToIndividual,
    
    # Batch Processing - Parallax
    "ParallaxBatchGenerator": ParallaxBatchGenerator,
    "ParallaxItemIterator": ParallaxItemIterator,
    
    # Batch Processing - SFX
    "SFXBatchGenerator": SFXBatchGenerator,
    "SFXItemIterator": SFXItemIterator,
    
    # Batch Processing - Video
    "VideoAssemblyBatcher": VideoAssemblyBatcher,
    "VideoSegmentIterator": VideoSegmentIterator,
    
    # Helper nodes - Batching & Iteration
    "PromptBatcher": PromptBatcher,
    "SceneIterator": SceneIterator,
    "NarrationIterator": NarrationIterator,
    "SFXCueIterator": SFXCueIterator,
    "ImagePromptIterator": ImagePromptIterator,
    
    # Helper nodes - Extraction & Parsing
    "ConfigExtractor": ConfigExtractor,
    "CharacterExtractor": CharacterExtractor,
    "LoRAProfileParser": LoRAProfileParser,
    "EngineSelector": EngineSelector,
    
    # Helper nodes - Processing
    "NarrationChunker": NarrationChunker,
    "SceneToVideoConfig": SceneToVideoConfig,
    "TextCombiner": TextCombiner,
}

# Display name mappings for ComfyUI UI
NODE_DISPLAY_NAME_MAPPINGS = {
    # Main orchestrator
    "NovelCinematicOrchestrator": "📖 Novel → Cinematic Plan",
    
    # Large novel support
    "NovelFileLoader": "📂 Novel File Loader",
    "NovelTextSplitter": "✂️ Novel Text Splitter",
    "ChunkIterator": "🔄 Chunk Iterator",
    "OutputMerger": "🔗 Output Merger",
    "ProgressTracker": "📊 Progress Tracker",
    "LargeNovelStats": "📈 Novel Statistics",
    "MemoryOptimizedOrchestrator": "📖 Memory-Optimized Orchestrator",
    
    # Enhanced coverage & adaptive density
    "ImageCoverageCalculator": "🎯 Image Coverage Calculator",
    "AdaptiveDensityOrchestrator": "📖 Adaptive Density Orchestrator",
    "KeyMomentExtractor": "🎯 Key Moment Extractor",
    "EnhancedPromptGenerator": "🎨 Enhanced Prompt Generator",
    
    # TTS Support
    "TTSCoverageCalculator": "🎤 TTS Coverage Calculator",
    "NarrationToTTSChunks": "✂️ Narration to TTS Chunks",
    "TTSChunkIterator": "🔄 TTS Chunk Iterator",
    "TTSBatchProcessor": "📦 TTS Batch Processor",
    "TTSProgressTracker": "📊 TTS Progress Tracker",
    "AudioSegmentInfo": "🔊 Audio Segment Info",
    "DialogueSplitter": "💬 Dialogue Splitter",
    "VoiceAssignmentConfig": "🎭 Voice Assignment Config",
    "TTSQueueManager": "📋 TTS Queue Manager",
    
    # Batch Processing - Universal
    "UniversalBatchConfig": "⚙️ Universal Batch Config",
    "PipelineProgressTracker": "📊 Pipeline Progress Tracker",
    "CheckpointManager": "💾 Checkpoint Manager",
    "BatchResumeHelper": "🔄 Batch Resume Helper",
    "PipelineTimeEstimator": "⏱️ Pipeline Time Estimator",
    
    # Batch Processing - Images
    "ImageBatchGenerator": "🖼️ Image Batch Generator",
    "ImageBatchToIndividual": "🖼️ Image Batch to Individual",
    
    # Batch Processing - Parallax
    "ParallaxBatchGenerator": "🎬 Parallax Batch Generator",
    "ParallaxItemIterator": "🔄 Parallax Item Iterator",
    
    # Batch Processing - SFX
    "SFXBatchGenerator": "🔊 SFX Batch Generator",
    "SFXItemIterator": "🔄 SFX Item Iterator",
    
    # Batch Processing - Video
    "VideoAssemblyBatcher": "🎥 Video Assembly Batcher",
    "VideoSegmentIterator": "🔄 Video Segment Iterator",
    
    # Helper nodes - Batching & Iteration
    "PromptBatcher": "📦 Prompt Batcher",
    "SceneIterator": "🔄 Scene Iterator",
    "NarrationIterator": "🎤 Narration Iterator",
    "SFXCueIterator": "🔊 SFX Cue Iterator",
    "ImagePromptIterator": "🖼️ Image Prompt Iterator",
    
    # Helper nodes - Extraction & Parsing
    "ConfigExtractor": "⚙️ Config Extractor",
    "CharacterExtractor": "👤 Character Extractor",
    "LoRAProfileParser": "🎨 LoRA Profile Parser",
    "EngineSelector": "🔀 Engine Selector",
    
    # Helper nodes - Processing
    "NarrationChunker": "✂️ Narration Chunker",
    "SceneToVideoConfig": "🎬 Scene Video Config",
    "TextCombiner": "📝 Text Combiner",
}

# Web directory for any custom JavaScript (optional)
WEB_DIRECTORY = "./web"

# Export all for proper module discovery
__all__ = [
    'NODE_CLASS_MAPPINGS',
    'NODE_DISPLAY_NAME_MAPPINGS',
    'WEB_DIRECTORY',
    '__version__'
]

# Print load confirmation
print(f"\n{'='*60}")
print(f"📖 Novel Cinematic Orchestrator v{__version__} loaded!")
print(f"   {len(NODE_CLASS_MAPPINGS)} nodes registered")
print(f"{'='*60}\n")
