# 🚀 Turnkey Novel to Images

**One node to rule them all!** Just upload your novel file, select a model, and generate.

## ✨ Features

- **File Upload Support** - Upload .txt, .docx, .pdf, .epub, .rtf, .html files
- **Truly Turnkey** - Just upload novel + connect model = images!
- **Unlimited Characters** - Automatically detects ALL characters with tiered references
- **Smart Analysis** - Extracts scenes, characters, settings automatically
- **Any Novel Size** - From short stories to epic fantasy sagas
- **GPU Time Estimates** - Know exactly how long generation will take
- **Full Calculation** - See exact image counts before generating

## 📂 Supported File Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| Plain Text | `.txt`, `.md`, `.text` | Best compatibility |
| Word Document | `.docx` | Full support |
| PDF | `.pdf` | Requires PyMuPDF or pdfplumber |
| EPUB | `.epub` | Ebooks fully supported |
| Rich Text | `.rtf` | Basic support |
| HTML | `.html`, `.htm` | Web content |

## 📦 Nodes (7 total)

| Node | Purpose |
|------|---------|
| 🚀 **Turnkey Novel to Images** | Main all-in-one node |
| 📂 **Novel File Loader** | Standalone file loader |
| 📊 **Novel Analyzer** | Detailed novel analysis |
| 🔢 **Image Calculator** | Exact image count calculation |
| ⚡ **Turnkey Batch Processor** | Feed prompts to sampler |
| 🔄 **Single Prompt Extractor** | For non-batch samplers |
| ⏱️ **GPU Time Estimator** | Time estimates for any GPU |

## 🎯 Simplest Possible Workflow

```
[🚀 Turnkey Novel to Images] → [⚡ Batch Processor] → [KSampler]
         ↑
    Just set:
    • input_mode: file_upload
    • novel_file: /path/to/your/novel.txt
    • image_density: standard
    • style: cinematic
    • quality: balanced
```

That's it! Everything else is automatic.

## 🔧 Two Input Modes

### Mode 1: File Upload (Recommended)
```
input_mode: file_upload
novel_file: /path/to/my_novel.docx
```
Supports: .txt, .docx, .pdf, .epub, .rtf, .html

### Mode 2: Paste Text
```
input_mode: paste_text
novel_text: [paste your entire novel here]
```
Best for short stories or testing

## 👥 Unlimited Character System

Characters are automatically detected and tiered:

| Tier | Mentions | References | Consistency |
|------|----------|------------|-------------|
| ⭐ Main | 20+ | 3 (front, 3/4, profile) | Maximum |
| 🔵 Supporting | 5-19 | 2 (front, 3/4) | High |
| ⚪ Minor | 2-4 | 1 (front) | Medium |
| · Background | 1 | 0 | Text only |

**No limits!** A fantasy epic with 50 characters? No problem - each gets appropriate references.

## 📊 Image Counts by Novel Size

| Novel Type | Words | Sparse | Standard | Cinematic |
|------------|-------|--------|----------|-----------|
| Short Story | 7,500 | 200 | 300 | 500 |
| Novella | 25,000 | 667 | 1,000 | 1,667 |
| Novel | 50,000 | 1,333 | 2,000 | 3,333 |
| Long Novel | 80,000 | 2,133 | 3,200 | 5,333 |
| Epic | 120,000 | 3,200 | 4,800 | 8,000 |
| Saga | 200,000 | 5,333 | 8,000 | 13,333 |

## ⏱️ Generation Times

### 50,000 Word Novel (Standard density = 2,000 images)

| GPU | Draft (4-step) | Balanced (8-step) | Quality (20-step) |
|-----|----------------|-------------------|-------------------|
| RTX 3060 | 13 min | 33 min | 83 min |
| RTX 4090 | 5 min | 13 min | 33 min |
| RTX 4090 ×2 | 2.5 min | 7 min | 17 min |
| A100 | 3 min | 8 min | 21 min |
| A100 ×4 | 50 sec | 2 min | 5 min |

### Cloud Costs (50k word novel)

| Provider | GPU | Time | Cost |
|----------|-----|------|------|
| Vast.ai | RTX 4090 | 13 min | ~$0.10 |
| Vast.ai | A100 | 8 min | ~$0.15 |
| RunPod | A100 | 8 min | ~$0.25 |
| Lambda | A100 ×4 | 2 min | ~$0.15 |

**Best Value**: Vast.ai A100 (~$0.15 for entire novel!)

## 🎨 Style Presets

| Style | Best For |
|-------|----------|
| `cinematic` | Drama, thriller, literary fiction |
| `anime` | Light novels, manga adaptations |
| `realistic` | Contemporary, historical fiction |
| `illustrated` | Children's books, graphic novels |
| `fantasy` | Epic fantasy, magic-heavy stories |
| `noir` | Mystery, crime, dark fiction |

## ⚙️ Quality Presets

| Quality | Steps | Speed | Best For |
|---------|-------|-------|----------|
| `draft` | 4 | 0.5s/img | Testing, previews |
| `balanced` | 8 | 1.0s/img | Production use |
| `quality` | 20 | 2.5s/img | Final renders |

## 📝 Usage Example

### Input
```
Novel Text: [Your 50,000 word fantasy novel]
Density: standard
Style: fantasy
Quality: balanced
```

### Automatic Output
```
✅ Characters Found: 23
   • 4 Main characters (12 reference images)
   • 8 Supporting characters (16 reference images)  
   • 11 Minor characters (11 reference images)

✅ Images to Generate: 2,039
   • 39 character references
   • 2,000 story images

✅ Estimated Time: 34 minutes (RTX 4090)
```

## 🔧 Custom Character Descriptions

Optionally provide descriptions for better consistency:

```
Elena: young woman, 25 years old, long flowing dark hair, piercing green eyes, leather armor with silver trim, determined fierce expression
Marcus: elderly wizard, 70 years old, long grey beard, deep blue robes with silver stars, kind wise eyes, carries wooden staff
```

If not provided, system uses: "character named [Name]"

## 📁 Output Structure

Images are named systematically:
```
ref_elena_front.png
ref_elena_three_quarter.png
ref_elena_profile.png
ref_marcus_front.png
...
scene_0001_shot_001.png
scene_0001_shot_002.png
scene_0001_shot_003.png
scene_0002_shot_001.png
...
```

## 🔌 Integration with ComfyUI

### With Batch Sampler
```
[Turnkey Novel to Images]
         ↓ all_prompts_json
[Turnkey Batch Processor] ← loop until has_more=false
         ↓ batch_prompts_json
[Your Batch KSampler]
```

### With Single Sampler
```
[Turnkey Novel to Images]
         ↓ all_prompts_json
[Single Prompt Extractor] ← loop until has_more=false
         ↓ prompt, negative_prompt
[Your KSampler]
```

## 💡 Tips

1. **Start with Draft** - Test your workflow with `draft` quality first
2. **Check Character Detection** - Review the analysis to ensure characters are found
3. **Add Descriptions** - Custom descriptions greatly improve consistency
4. **Use Cloud for Large Novels** - Vast.ai A100 is incredibly cost-effective
5. **Standard Density** - Good balance of coverage and speed

## 🛠️ Installation

1. Copy `TurnkeyNovelToImages` folder to `ComfyUI/custom_nodes/`
2. Restart ComfyUI
3. Find nodes under "📚 Novel to Images" category

## 📋 Requirements

- ComfyUI
- Any SDXL or Flux model
- (Optional) IP-Adapter for character consistency

## License

MIT License
