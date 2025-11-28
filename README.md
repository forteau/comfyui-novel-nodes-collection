# 📚 ComfyUI Novel Nodes Collection

A comprehensive collection of ComfyUI custom nodes for transforming novels and stories into complete cinematic video productions with AI-generated images, consistent characters, TTS narration, and sound effects.

![ComfyUI](https://img.shields.io/badge/ComfyUI-compatible-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Python](https://img.shields.io/badge/python-3.8+-blue)

## 📦 What's Included

This repository contains three powerful node packages:

### 1. 🎬 Novel Cinematic Orchestrator
A comprehensive node pack for advanced novel-to-video production with fine-grained control.

**Key Features:**
- 🎬 Intelligent scene segmentation with natural break detection
- 👤 Character extraction and tracking for consistency
- 🖼️ Image prompt generation with multiple style options
- 🎤 Narration processing with TTS support
- 🔊 SFX cue generation
- 📦 Batch processing helpers
- 📚 Large novel support (50k+ words) with memory-efficient processing
- 🔀 Multi-engine support (Flux, SDXL, SD1.5, Cascade, PixArt)

**Best For:** Users who want granular control over the production pipeline, professional workflows, and large novel processing.

### 2. 🚀 Turnkey Novel to Images
An all-in-one, ultra-simple node for instant novel-to-image generation.

**Key Features:**
- 📂 File upload support (.txt, .docx, .pdf, .epub, .rtf, .html)
- 🎯 One-node solution - just upload and generate
- 👥 Unlimited character detection with tiered references
- 📊 Smart analysis and GPU time estimates
- ⚡ Batch processing built-in
- 🎨 Style and quality presets

**Best For:** Beginners, quick prototyping, and users who want a simple turnkey solution.

### 3. 📚 Novel to Story Diffusion
A specialized node for converting novels into prompts compatible with **ComfyUI_StoryDiffusion**.

**Key Features:**
- 🎭 Automatic character extraction and formatting
- 📝 Scene-by-scene prompt generation
- 🔄 Direct Story Diffusion compatibility
- 👥 Character consistency with "has same clothes" formatting
- ⚡ Simple copy-paste workflow

**Best For:** Users working with Story Diffusion who want consistent character generation across multiple scenes.

---

## 🚀 Quick Start

### Installation via ComfyUI Manager (Recommended)

1. Open ComfyUI Manager
2. Click "Install Custom Nodes"
3. Search for "Novel Nodes Collection"
4. Click Install

### Manual Installation

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/forteau/comfyui-novel-nodes-collection.git
cd comfyui-novel-nodes-collection
pip install -r requirements.txt
```

Then restart ComfyUI.

---

## 📖 Usage Examples

### Option 1: Turnkey Approach (Simplest)

Perfect for beginners or quick projects:

```
[🚀 Turnkey Novel to Images]
    • input_mode: file_upload
    • novel_file: /path/to/novel.txt
    • image_density: standard
    • style: cinematic
    • quality: balanced
         ↓
[⚡ Turnkey Batch Processor]
         ↓
[KSampler] → Images!
```

### Option 2: Advanced Orchestrator (Full Control)

For professional workflows:

```
[Novel Text Input]
         ↓
[📖 Novel → Cinematic Plan]
         ↓
    ├── scenes_json ────→ [Scene Iterator] → [Processing]
    ├── image_prompts_json ─→ [Prompt Batcher] → [Flux/SDXL]
    ├── narration_json ──→ [Narration Iterator] → [IndexTTS]
    ├── sfx_cues_json ──→ [SFX Cue Iterator] → [MMAudio]
    ├── characters_json ─→ [Character Extractor] → [IPAdapter]
    └── config_json ────→ [Config Extractor] → [Pipeline]
```

### Option 3: Story Diffusion (Character Consistency)

Perfect for Story Diffusion users:

```
[📚 Novel to Story Diffusion]
    • novel_text: [Your novel]
    • character_descriptions: Taylor: young woman, brown hair...
    • num_scenes: 8
         ↓
    ├── character_prompt → [StoryDiffusion CLIPTextEncode] → "test" field
    └── scene_prompts → [StoryDiffusion CLIPTextEncode] → main prompt
```

### Option 4: Large Novel Processing (50k+ words)

Memory-efficient workflow for epic novels:

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

---

## 🎨 Supported Styles

| Style | Description | Best For |
|-------|-------------|----------|
| **cinematic** | Film-like with dramatic lighting | Drama, thriller, literary fiction |
| **anime** | Japanese animation style | Light novels, manga adaptations |
| **realistic** | Photorealistic rendering | Contemporary, historical fiction |
| **fantasy** | Epic fantasy aesthetic | Fantasy novels, magic-heavy stories |
| **illustrated** | Artistic illustration style | Children's books, graphic novels |
| **noir** | Dark, moody atmosphere | Mystery, crime fiction |
| **painterly** | Oil painting aesthetic | Artistic, literary works |
| **comic** | Bold comic book style | Action, superhero stories |

---

## 🔧 Supported Image Engines

| Engine | Description | Best For |
|--------|-------------|----------|
| **flux** | High quality, detailed images | Professional production |
| **sdxl** | Fast, high-resolution generation | Balanced quality/speed |
| **sd15** | Compatible with most LoRAs | Character consistency |
| **cascade** | Efficient multi-stage generation | Large batches |
| **pixart** | Artistic, aesthetic outputs | Stylized content |

---

## 📊 Performance Estimates

### 50,000 Word Novel (Standard density = 2,000 images)

| GPU | Draft (4-step) | Balanced (8-step) | Quality (20-step) |
|-----|----------------|-------------------|-------------------|
| RTX 3060 | 13 min | 33 min | 83 min |
| RTX 4090 | 5 min | 13 min | 33 min |
| RTX 4090 ×2 | 2.5 min | 7 min | 17 min |
| A100 | 3 min | 8 min | 21 min |
| A100 ×4 | 50 sec | 2 min | 5 min |

### Cloud Costs (50k word novel, balanced quality)

| Provider | GPU | Time | Estimated Cost |
|----------|-----|------|----------------|
| Vast.ai | RTX 4090 | 13 min | ~$0.10 |
| Vast.ai | A100 | 8 min | ~$0.15 |
| RunPod | A100 | 8 min | ~$0.25 |
| Lambda | A100 ×4 | 2 min | ~$0.15 |

---

## 🔌 Recommended Companion Nodes

For a complete pipeline, consider installing:

### Image Generation
- Standard ComfyUI samplers (Flux/SDXL/SD1.5)

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

## 📚 Documentation

### Novel Cinematic Orchestrator
See [NovelCinematicOrchestrator/README.md](NovelCinematicOrchestrator/README.md) for:
- Detailed node reference
- JSON output formats
- Advanced workflows
- Large novel processing guide

### Turnkey Novel to Images
See [TurnkeyNovelToImages/README.md](TurnkeyNovelToImages/README.md) for:
- File format support
- Character detection system
- Image count calculations
- Simple workflow examples

### Novel to Story Diffusion
See [NovelToStoryDiffusion/README.md](NovelToStoryDiffusion/README.md) for:
- Story Diffusion integration
- Character prompt formatting
- Scene prompt generation
- Usage tips for consistency

---

## 💡 Tips & Best Practices

1. **Start Simple**: Use Turnkey Novel to Images first to understand the workflow
2. **Test with Draft**: Always test with `draft` quality before full generation
3. **Character Descriptions**: Provide custom descriptions for better consistency
4. **Batch Size**: Use batch sizes of 4-8 for optimal GPU utilization
5. **Scene Length**: Keep scenes 1500-2000 characters for best results
6. **Cloud Processing**: For large novels, cloud GPUs (Vast.ai) are very cost-effective

---

## 🛠️ Requirements

- **ComfyUI** (latest version recommended)
- **Python** 3.8+
- **Image Model**: Any SDXL, Flux, or SD1.5 checkpoint
- **Optional**: IP-Adapter for character consistency
- **Optional**: TTS nodes for narration
- **Optional**: Audio generation nodes for SFX

### Python Dependencies

All dependencies are included in `requirements.txt`:
- Standard Python libraries (no external packages required for basic functionality)
- Optional: `python-docx`, `PyMuPDF`, `ebooklib` for additional file format support

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 🐛 Bug Reports & Feature Requests

Please use the [GitHub Issues](https://github.com/forteau/comfyui-novel-nodes-collection/issues) page to:
- Report bugs
- Request new features
- Ask questions
- Share your workflows

---

## 📄 License

MIT License - Feel free to use in personal and commercial projects.

See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built for the ComfyUI community with inspiration from:
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [IndexTTS](https://github.com/billwuhao/ComfyUI_IndexTTS)
- [Depthflow](https://github.com/akatz-ai/ComfyUI-Depthflow-Nodes)
- [MMAudio](https://github.com/kijai/ComfyUI-MMAudio)
- [VideoHelperSuite](https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite)

---

## 📞 Support

- **Documentation**: Check the README files in each node package folder
- **Issues**: [GitHub Issues](https://github.com/forteau/comfyui-novel-nodes-collection/issues)
- **Discussions**: [GitHub Discussions](https://github.com/forteau/comfyui-novel-nodes-collection/discussions)

---

**Happy storytelling! 📚🎬✨**
