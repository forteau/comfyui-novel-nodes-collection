# 📖 Novel Cinematic Orchestrator

A comprehensive ComfyUI custom node pack for transforming novels and stories into complete cinematic video production plans with consistent characters, TTS narration, SFX cues, and 3D parallax support.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![ComfyUI](https://img.shields.io/badge/ComfyUI-compatible-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## ✨ Features

- **🎬 Intelligent Scene Segmentation** - Automatically splits your novel into logical scenes with natural break detection
- **👤 Character Extraction** - Identifies and tracks character names for consistency
- **🖼️ Image Prompt Generation** - Creates detailed prompts for B-roll generation with multiple style options
- **🎤 Narration Processing** - Prepares text for TTS with duration estimates and dialogue detection
- **🔊 SFX Cue Generation** - Analyzes content to suggest appropriate sound effects
- **📦 Batch Processing** - Helper nodes for efficient parallel image generation
- **🔀 Multi-Engine Support** - Works with Flux, SDXL, SD1.5, Cascade, and PixArt

## 📦 Installation

### Via ComfyUI Manager (Recommended)
1. Open ComfyUI Manager
2. Click "Install Custom Nodes"
3. Search for "Novel Cinematic Orchestrator"
4. Click Install

### Manual Installation
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/your-repo/NovelCinematicOrchestrator.git
# or copy the folder directly
```

### Dependencies
Most dependencies are already included with ComfyUI. No additional packages required for basic functionality.

## 🚀 Quick Start

### Basic Workflow

1. **Add the Main Node**: Right-click → `🎬 Story Tools` → `📖 Novel → Cinematic Plan`

2. **Configure Inputs**:
   - Paste your novel/story text
   - Select image engine (Flux, SDXL, etc.)
   - Choose voice mode for TTS
   - Enable/disable 3D parallax

3. **Connect Outputs**:
   - `scenes_json` → Scene processing nodes
   - `image_prompts_json` → Image generation nodes
   - `narration_json` → TTS nodes (IndexTTS, etc.)
   - `sfx_cues_json` → Audio generation nodes (MMAudio, etc.)

### 📚 Large Novel Support (50k+ words)

For novels larger than ~10,000 words, use the dedicated large novel workflow:

1. **Load from File**: Use `📂 Novel File Loader` to load .txt files from `ComfyUI/input/`
2. **Analyze First**: Use `📈 Novel Statistics` to see word count and recommendations
3. **Split if Needed**: Use `✂️ Novel Text Splitter` to break into 15k word chunks
4. **Process Chunks**: Use `🔄 Chunk Iterator` + `📖 Memory-Optimized Orchestrator` in a loop
5. **Merge Results**: Use `🔗 Output Merger` to combine all chunks

**Memory-Efficient Workflow for 50k+ Words:**
```
[📂 Novel File Loader] → [📈 Novel Statistics]
         ↓
[✂️ Novel Text Splitter] → chunks_json
         ↓
[🔄 Chunk Iterator] ←─────────────────┐
         ↓                            │
[📖 Memory-Optimized Orchestrator]    │
         ↓                            │
[🔗 Output Merger] → [Loop back if has_more]
         ↓
[Final merged outputs to pipeline]
```

### Example Connection

```
[Novel Text Input]
        ↓
[📖 Novel → Cinematic Plan]
        ↓
    ├── scenes_json ────→ [Scene Iterator] → [Your scene processing]
    ├── image_prompts_json ─→ [Prompt Batcher] → [Flux/SDXL Sampler]
    ├── narration_json ──→ [Narration Iterator] → [IndexTTS]
    ├── sfx_cues_json ──→ [SFX Cue Iterator] → [MMAudio]
    ├── characters_json ─→ [Character Extractor] → [IPAdapter]
    └── config_json ────→ [Config Extractor] → [Pipeline control]
```

## 📚 Node Reference

### Main Orchestrator

#### 📖 Novel → Cinematic Plan
The master orchestrator node that processes your entire novel.

**Inputs:**
| Input | Type | Description |
|-------|------|-------------|
| novel_text | STRING | Your novel or story text |
| max_scene_chars | INT | Max characters per scene (500-10000) |
| broll_density | INT | Image prompts per scene (1-16) |
| image_engine | COMBO | flux, sdxl, sd15, cascade, pixart |
| image_style | COMBO | cinematic, anime, realistic, painterly, comic, storyboard |
| character_profile | STRING | Comma-separated LoRA names |
| voice_mode | COMBO | index_tts, index_clone, xtts, voxcpm, chatterbox |
| parallax_enabled | BOOLEAN | Enable 3D parallax effect |
| sfx_mode | COMBO | mmaudio_auto, mmaudio_prompted, stable_audio, none |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| scenes_json | STRING | JSON array of scene texts |
| image_prompts_json | STRING | Nested array of image prompts per scene |
| narration_json | STRING | Narration text with metadata |
| sfx_cues_json | STRING | SFX cues with prompts |
| characters_json | STRING | Detected character names |
| config_json | STRING | Pipeline configuration |
| summary_text | STRING | Human-readable production summary |

---

### Large Novel Support Nodes

#### 📂 Novel File Loader
Load novels directly from .txt or .md files instead of pasting.

```
[file_name] → [Novel File Loader] → [novel_text, word_count, char_count]
```

**Features:**
- Automatic encoding detection
- Text cleaning options
- Chapter header removal option

#### 📈 Novel Statistics
Analyze a novel before processing.

**Outputs:**
- Word count, paragraph count
- Estimated scenes and duration
- Dialogue ratio
- Processing recommendations

#### ✂️ Novel Text Splitter
Split large novels into manageable chunks.

| Parameter | Description |
|-----------|-------------|
| max_words_per_chunk | Target words per chunk (default: 15000) |
| overlap_sentences | Sentences to overlap for context (default: 3) |

#### 🔄 Chunk Iterator
Get one chunk at a time for memory-efficient processing.

#### 🔗 Output Merger
Combine outputs from multiple chunk processings.

#### 📖 Memory-Optimized Orchestrator
Process one scene at a time instead of the entire novel.

**Best for:**
- Novels over 50,000 words
- Systems with limited RAM
- Processing in loops

---

### Helper Nodes

#### 📦 Prompt Batcher
Flattens nested image prompts into batches for parallel generation.

```
[image_prompts_json] → [Prompt Batcher] → [batched_prompts] → [Sampler]
```

#### 🔄 Scene Iterator
Extracts a single scene by index for sequential processing.

```
[scenes_json] + [scene_index] → [Scene Iterator] → [scene_text]
```

#### 🎤 Narration Iterator
Extracts narration for a specific scene with metadata.

#### 🔊 SFX Cue Iterator
Extracts SFX cues for audio generation.

#### 🖼️ Image Prompt Iterator
Extracts specific prompts by scene and shot index.

#### ⚙️ Config Extractor
Extracts configuration values for conditional routing.

#### 👤 Character Extractor
Extracts character names for LoRA loading and consistency.

#### ✂️ Narration Chunker
Splits long narration into TTS-friendly chunks.

#### 🎬 Scene Video Config
Generates video assembly configuration for a scene.

#### 🎨 LoRA Profile Parser
Parses comma-separated LoRA names from character profile.

#### 🔀 Engine Selector
Routes to different checkpoint loaders based on engine.

#### 📝 Text Combiner
Combines multiple texts for batch processing.

---

## 🔧 Recommended Companion Nodes

For a complete pipeline, install these node packs:

### Image Generation
- **Flux/SDXL/SD1.5** - Standard ComfyUI samplers

### Voice & TTS
- **ComfyUI_IndexTTS** - High-quality voice cloning
- **ComfyUI-XTTS** - Multi-language TTS
- **TTS-Audio-Suite** - Multi-engine TTS

### 3D Parallax
- **ComfyUI-Depthflow-Nodes** - 2.5D parallax animations
- **DepthAnythingV2** - Depth map generation

### SFX & Audio
- **ComfyUI-MMAudio** - Video-synchronized audio
- **ComfyUI-StableAudioX** - Text-to-audio generation
- **ComfyUI_AudioTools** - Audio processing

### Video Assembly
- **ComfyUI-VideoHelperSuite** - Video creation and editing

---

## 📋 Output JSON Formats

### scenes_json
```json
[
  {
    "id": "scene_001",
    "index": 0,
    "text": "The story begins in a small village..."
  }
]
```

### image_prompts_json
```json
[
  [
    {
      "prompt": "cinematic film still, Scene 1, Shot 1, establishing shot...",
      "negative_prompt": "blurry, low quality...",
      "scene_idx": 0,
      "shot_idx": 0,
      "shot_type": "establishing shot",
      "id": "scene_001_shot_01"
    }
  ]
]
```

### narration_json
```json
[
  {
    "text": "The story begins in a small village...",
    "scene_idx": 0,
    "id": "narration_scene_001",
    "word_count": 150,
    "estimated_duration_seconds": 60.0,
    "dialogue_ratio": 0.35,
    "has_dialogue": true
  }
]
```

### sfx_cues_json
```json
[
  {
    "cues": [
      {
        "keyword": "forest",
        "sfx_prompts": ["forest ambience, birds chirping..."],
        "priority": 3,
        "primary_prompt": "forest ambience, birds chirping, leaves rustling"
      }
    ],
    "combined_prompt": "forest ambience, birds chirping...",
    "scene_idx": 0,
    "cue_count": 2
  }
]
```

---

## 🎨 Style Options

### Image Styles
| Style | Description |
|-------|-------------|
| cinematic | Film-like with dramatic lighting and depth of field |
| anime | Japanese animation style with vibrant colors |
| realistic | Photorealistic rendering |
| painterly | Oil painting aesthetic with visible brushstrokes |
| comic | Bold lines and dynamic comic book style |
| storyboard | Pre-visualization concept art style |

### Image Engines
| Engine | Best For |
|--------|----------|
| flux | High quality, detailed images |
| sdxl | Fast, high-res generation |
| sd15 | Compatible with most LoRAs |
| cascade | Efficient multi-stage generation |
| pixart | Artistic, aesthetic outputs |

---

## ⚡ Performance Tips

1. **Batch Size**: Use `Prompt Batcher` with batch_size 4-8 for optimal GPU utilization
2. **Scene Length**: Shorter scenes (1500-2000 chars) produce better image prompts
3. **B-Roll Density**: 4-6 shots per scene balances quality and generation time
4. **LoRAs**: List character LoRAs in order of importance

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📄 License

MIT License - Feel free to use in personal and commercial projects.

---

## 🙏 Acknowledgments

Built for the ComfyUI community with inspiration from:
- [IndexTTS](https://github.com/billwuhao/ComfyUI_IndexTTS)
- [Depthflow](https://github.com/akatz-ai/ComfyUI-Depthflow-Nodes)
- [MMAudio](https://github.com/kijai/ComfyUI-MMAudio)
- [VideoHelperSuite](https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite)

---

**Happy storytelling! 📚🎬**
