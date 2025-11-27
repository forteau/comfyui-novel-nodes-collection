# ⚡ Quick Start Guide

Get started with ComfyUI Novel Nodes in 5 minutes!

## 🎯 Choose Your Approach

### 🚀 Option 1: Ultra-Simple (Turnkey)

**Best for:** Beginners, quick results

1. Add the **"🚀 Turnkey Novel to Images"** node
2. Set `input_mode` to `file_upload`
3. Browse and select your novel file (.txt, .docx, .pdf, .epub)
4. Choose your style: `cinematic`, `anime`, `realistic`, etc.
5. Choose quality: `draft` (fast), `balanced`, or `quality`
6. Connect to **"⚡ Turnkey Batch Processor"**
7. Connect to your KSampler
8. Generate!

**That's it!** Everything else is automatic.

---

### 🎬 Option 2: Advanced Control (Orchestrator)

**Best for:** Professional workflows, fine-tuning

1. Add the **"📖 Novel → Cinematic Plan"** node
2. Paste your novel text or load from file
3. Configure:
   - `max_scene_chars`: 2000 (scene length)
   - `broll_density`: 4-6 (images per scene)
   - `image_engine`: flux, sdxl, or sd15
   - `image_style`: cinematic, anime, etc.
4. Connect outputs:
   - `image_prompts_json` → **Prompt Batcher** → Sampler
   - `narration_json` → TTS nodes (optional)
   - `sfx_cues_json` → Audio nodes (optional)
   - `characters_json` → Character consistency (optional)
5. Generate!

---

## 📚 Example Workflows

### Minimal Workflow (Turnkey)

```
[🚀 Turnkey Novel to Images]
         ↓
[⚡ Batch Processor]
         ↓
[KSampler]
         ↓
    [Images!]
```

### Complete Production Pipeline

```
[📖 Novel → Cinematic Plan]
         ↓
    ├── [Prompt Batcher] → [Flux Sampler] → [Images]
    ├── [Narration Iterator] → [IndexTTS] → [Audio]
    ├── [SFX Cue Iterator] → [MMAudio] → [Sound FX]
    └── [Character Extractor] → [IPAdapter] → [Consistency]
                                                    ↓
                                            [Video Assembly]
```

---

## 🎨 Style Presets

| Style | Use For |
|-------|---------|
| `cinematic` | Drama, thriller, movies |
| `anime` | Manga, light novels |
| `realistic` | Contemporary fiction |
| `fantasy` | Epic fantasy, magic |
| `illustrated` | Children's books |
| `noir` | Mystery, crime |

---

## ⚙️ Quality Settings

| Quality | Speed | Best For |
|---------|-------|----------|
| `draft` | ⚡⚡⚡ | Testing, previews |
| `balanced` | ⚡⚡ | Production (recommended) |
| `quality` | ⚡ | Final renders |

---

## 📊 Novel Size Guide

| Novel Type | Words | Images (Standard) | Time (RTX 4090) |
|------------|-------|-------------------|-----------------|
| Short Story | 7,500 | 300 | 5 min |
| Novella | 25,000 | 1,000 | 17 min |
| Novel | 50,000 | 2,000 | 33 min |
| Epic | 120,000 | 4,800 | 80 min |

---

## 💡 Pro Tips

1. **Start with Draft**: Test your workflow with `draft` quality first
2. **Test Small**: Try with a short story before processing a full novel
3. **Check Characters**: Review detected characters before generating
4. **Use Batching**: Batch size 4-8 for optimal GPU usage
5. **Save Prompts**: Export prompts JSON for reuse
6. **Cloud GPUs**: Use Vast.ai for large novels (~$0.15 for 50k words)

---

## 🔧 Recommended Settings

### For Best Quality
```
image_engine: flux
image_style: cinematic
quality: quality
broll_density: 6
```

### For Speed
```
image_engine: sdxl
image_style: cinematic
quality: draft
broll_density: 3
```

### For Balance (Recommended)
```
image_engine: flux
image_style: cinematic
quality: balanced
broll_density: 4
```

---

## 🆘 Troubleshooting

### "Out of Memory" Error
- Reduce `broll_density` to 2-3
- Use `draft` quality
- Process in smaller chunks
- Use the Memory-Optimized Orchestrator

### Images Don't Match Style
- Check your checkpoint model
- Adjust `image_style` setting
- Add style keywords to prompts

### Characters Not Consistent
- Use IP-Adapter nodes
- Generate character reference images first
- Provide custom character descriptions

### Processing Too Slow
- Use `draft` quality for testing
- Reduce `broll_density`
- Consider cloud GPUs
- Use batch processing

---

## 📖 Next Steps

1. ✅ Try a simple workflow with a short story
2. ✅ Experiment with different styles
3. ✅ Review the full documentation:
   - [Main README](README.md)
   - [Novel Cinematic Orchestrator](NovelCinematicOrchestrator/README.md)
   - [Turnkey Novel to Images](TurnkeyNovelToImages/README.md)
4. ✅ Join the community and share your results!

---

## 🎬 Ready to Create?

Pick your approach above and start generating! 

**Remember**: Start small, test often, and have fun! 🚀

---

Need more help? Check the [full documentation](README.md) or open an issue on GitHub.
