# 📚 Novel to Story Diffusion

Converts novels into prompts for **ComfyUI_StoryDiffusion**.

## Output Format

Matches Story Diffusion's expected format exactly:

**Character definitions (for "test" field):**
```
[Taylor] young woman, brown hair, business clothes, has same clothes, [Jonas] tall man, dark hair, suit, has same clothes
```

**Scene prompts (for main prompt area):**
```
[Taylor] in the bed, cinematic film still, 8k;
[Taylor] in the kitchen making with Jonas, cinematic film still, 8k;
[Jonas] driving the car with Taylor, cinematic film still, 8k;
```

## Installation

1. Copy `NovelToStoryDiffusion` folder to `ComfyUI/custom_nodes/`
2. Restart ComfyUI

## Usage

1. Add **📚 Novel to Story Diffusion** node
2. Paste your novel text
3. Add character descriptions (important for consistency!)
4. Set number of scenes
5. Copy outputs to Story Diffusion nodes:

| Output | Paste Into |
|--------|------------|
| `character_prompt` | StoryDiffusion_CLIPTextEncode → "test" field |
| `scene_prompts` | StoryDiffusion_CLIPTextEncode → main prompt area |

## Tips

- **Always include "has same clothes"** in character descriptions for consistency
- Use 5-10 scenes for best results
- Keep character descriptions detailed but concise
