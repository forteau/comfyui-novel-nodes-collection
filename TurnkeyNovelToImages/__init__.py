"""
Turnkey Novel to Images Generator
==================================
Complete automatic pipeline - just select model, upload novel, generate!

Features:
- Fully automatic character extraction and reference generation
- Unlimited tiered character references (main/supporting/minor)
- Novel statistics and image count calculation
- One-click generation with progress tracking
- Works with any SDXL/Flux model in ComfyUI
- Supports file upload (.txt, .md, .epub, .pdf, .docx, .rtf)
"""

import json
import math
import re
import os
import hashlib
from typing import List, Dict, Tuple, Any, Optional
from collections import Counter


# =============================================================================
# FILE LOADER - Handles all novel file formats
# =============================================================================

class NovelFileLoader:
    """
    Loads novel text from various file formats.
    Supports: .txt, .md, .text, .epub, .pdf, .docx, .rtf, .html
    """
    
    DESCRIPTION = """
    📂 Novel File Loader
    
    Upload your novel in any format:
    • Plain text (.txt, .md, .text)
    • Word documents (.docx)
    • PDF files (.pdf)
    • EPUB ebooks (.epub)
    • Rich text (.rtf)
    • HTML files (.html)
    
    Automatically extracts and cleans text!
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {
                    "default": "",
                    "placeholder": "Path to novel file or drag & drop"
                }),
            },
            "optional": {
                "encoding": (["auto", "utf-8", "latin-1", "cp1252", "ascii"], {
                    "default": "auto"
                }),
                "clean_text": ("BOOLEAN", {"default": True}),
                "remove_headers_footers": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "STRING")
    RETURN_NAMES = ("novel_text", "file_info", "word_count", "load_status")
    FUNCTION = "load"
    CATEGORY = "📚 Novel to Images"

    def load(
        self,
        file_path: str,
        encoding: str = "auto",
        clean_text: bool = True,
        remove_headers_footers: bool = True
    ) -> Tuple[str, str, int, str]:
        
        if not file_path or not os.path.exists(file_path):
            return ("", "{}", 0, f"❌ File not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        try:
            # Load based on file type
            if file_ext in ['.txt', '.md', '.text']:
                text = self._load_text_file(file_path, encoding)
            elif file_ext == '.docx':
                text = self._load_docx(file_path)
            elif file_ext == '.pdf':
                text = self._load_pdf(file_path)
            elif file_ext == '.epub':
                text = self._load_epub(file_path)
            elif file_ext == '.rtf':
                text = self._load_rtf(file_path)
            elif file_ext in ['.html', '.htm']:
                text = self._load_html(file_path, encoding)
            else:
                # Try as plain text
                text = self._load_text_file(file_path, encoding)
            
            # Clean text if requested
            if clean_text:
                text = self._clean_text(text)
            
            if remove_headers_footers:
                text = self._remove_headers_footers(text)
            
            word_count = len(text.split())
            
            file_info = json.dumps({
                "file_name": file_name,
                "file_path": file_path,
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / (1024*1024), 2),
                "file_type": file_ext,
                "word_count": word_count,
                "character_count": len(text),
                "line_count": len(text.split('\n')),
                "paragraph_count": len([p for p in text.split('\n\n') if p.strip()])
            }, indent=2)
            
            status = f"✅ Loaded: {file_name} ({word_count:,} words)"
            
            return (text, file_info, word_count, status)
            
        except Exception as e:
            return ("", "{}", 0, f"❌ Error loading file: {str(e)}")
    
    def _load_text_file(self, path: str, encoding: str) -> str:
        """Load plain text file."""
        encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'ascii'] if encoding == 'auto' else [encoding]
        
        for enc in encodings_to_try:
            try:
                with open(path, 'r', encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        # Fallback: read as binary and decode with errors='replace'
        with open(path, 'rb') as f:
            return f.read().decode('utf-8', errors='replace')
    
    def _load_docx(self, path: str) -> str:
        """Load Word document."""
        try:
            from docx import Document
            doc = Document(path)
            paragraphs = [para.text for para in doc.paragraphs]
            return '\n\n'.join(paragraphs)
        except ImportError:
            # Fallback: try to extract text manually from docx (it's a zip)
            import zipfile
            from xml.etree import ElementTree
            
            with zipfile.ZipFile(path) as z:
                xml_content = z.read('word/document.xml')
                tree = ElementTree.fromstring(xml_content)
                
                # Extract text from all w:t elements
                namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                texts = []
                for elem in tree.iter():
                    if elem.tag.endswith('}t') and elem.text:
                        texts.append(elem.text)
                    elif elem.tag.endswith('}p'):
                        texts.append('\n')
                
                return ''.join(texts)
    
    def _load_pdf(self, path: str) -> str:
        """Load PDF file."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(path)
            text = ""
            for page in doc:
                text += page.get_text() + "\n\n"
            doc.close()
            return text
        except ImportError:
            try:
                # Fallback to pdfplumber
                import pdfplumber
                text = ""
                with pdfplumber.open(path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"
                return text
            except ImportError:
                raise ImportError("Install PyMuPDF (fitz) or pdfplumber: pip install pymupdf pdfplumber")
    
    def _load_epub(self, path: str) -> str:
        """Load EPUB ebook."""
        try:
            import ebooklib
            from ebooklib import epub
            from bs4 import BeautifulSoup
            
            book = epub.read_epub(path)
            text_parts = []
            
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    text_parts.append(soup.get_text())
            
            return '\n\n'.join(text_parts)
        except ImportError:
            # Fallback: epub is a zip file with HTML content
            import zipfile
            from xml.etree import ElementTree
            
            text_parts = []
            with zipfile.ZipFile(path) as z:
                for name in z.namelist():
                    if name.endswith(('.html', '.xhtml', '.htm')):
                        content = z.read(name).decode('utf-8', errors='replace')
                        # Simple HTML tag removal
                        clean = re.sub(r'<[^>]+>', ' ', content)
                        clean = re.sub(r'\s+', ' ', clean)
                        text_parts.append(clean.strip())
            
            return '\n\n'.join(text_parts)
    
    def _load_rtf(self, path: str) -> str:
        """Load RTF file."""
        try:
            from striprtf.striprtf import rtf_to_text
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                rtf_content = f.read()
            return rtf_to_text(rtf_content)
        except ImportError:
            # Basic RTF parsing
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Remove RTF control words
            content = re.sub(r'\\[a-z]+\d*\s?', '', content)
            content = re.sub(r'[{}]', '', content)
            content = re.sub(r'\s+', ' ', content)
            return content.strip()
    
    def _load_html(self, path: str, encoding: str) -> str:
        """Load HTML file."""
        content = self._load_text_file(path, encoding)
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            return soup.get_text(separator='\n')
        except ImportError:
            # Basic HTML tag removal
            clean = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL | re.IGNORECASE)
            clean = re.sub(r'<[^>]+>', ' ', clean)
            clean = re.sub(r'\s+', ' ', clean)
            return clean.strip()
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove excessive whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{4,}', '\n\n\n', text)
        
        # Remove common artifacts
        text = re.sub(r'Page \d+', '', text)
        text = re.sub(r'\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Clean up quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text.strip()
    
    def _remove_headers_footers(self, text: str) -> str:
        """Remove common headers/footers."""
        lines = text.split('\n')
        cleaned = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Skip common header/footer patterns
            if any([
                re.match(r'^page\s+\d+', line_lower),
                re.match(r'^\d+$', line_lower),
                re.match(r'^chapter\s+\d+$', line_lower) and len(line) < 15,
                'all rights reserved' in line_lower,
                'copyright ©' in line_lower,
                'isbn' in line_lower and len(line) < 30,
            ]):
                continue
            
            cleaned.append(line)
        
        return '\n'.join(cleaned)


# =============================================================================
# NOVEL ANALYZER - Extracts everything automatically
# =============================================================================

class NovelAnalyzer:
    """
    Analyzes novel text and extracts all necessary information.
    """
    
    DESCRIPTION = """
    📊 Novel Analyzer
    
    Automatically analyzes your novel and extracts:
    • All characters with mention counts
    • Scene breaks and chapter structure
    • Mood and setting information
    • Time and location references
    • Recommended image counts
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "novel_text": ("STRING", {
                    "multiline": True,
                    "placeholder": "Paste your novel text here or connect from file loader..."
                }),
            },
            "optional": {
                "custom_character_list": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "Optional: Add character names not auto-detected\nOne per line"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "INT", "INT", "INT", "FLOAT")
    RETURN_NAMES = (
        "novel_data_json",
        "characters_json",
        "scenes_json",
        "analysis_summary",
        "word_count",
        "character_count",
        "scene_count",
        "estimated_video_hours"
    )
    FUNCTION = "analyze"
    CATEGORY = "📚 Novel to Images"

    # Common words to exclude from character detection
    COMMON_WORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
        "be", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "must", "shall", "can", "need",
        "he", "she", "it", "they", "we", "you", "i", "me", "him", "her",
        "his", "hers", "its", "their", "our", "your", "my", "this", "that",
        "these", "those", "then", "than", "when", "where", "what", "who",
        "which", "how", "why", "all", "each", "every", "both", "few", "more",
        "most", "other", "some", "such", "no", "not", "only", "own", "same",
        "so", "just", "now", "here", "there", "also", "very", "even", "back",
        "well", "way", "long", "little", "good", "new", "first", "last",
        "great", "old", "young", "right", "big", "high", "small", "large",
        "next", "early", "late", "still", "never", "always", "often", "once",
        "upon", "time", "day", "night", "year", "years", "hand", "hands",
        "eyes", "face", "head", "man", "woman", "people", "thing", "things",
        "place", "world", "life", "room", "door", "house", "home", "city",
        "chapter", "part", "one", "two", "three", "four", "five", "six",
        "seven", "eight", "nine", "ten", "said", "asked", "told", "thought",
        "looked", "saw", "knew", "felt", "made", "came", "went", "got",
        "took", "gave", "found", "called", "seemed", "left", "turned",
        "began", "keep", "let", "put", "set", "show", "try", "ask", "tell",
        "think", "call", "keep", "hear", "mean", "hold", "stand", "turn",
        "move", "live", "believe", "bring", "happen", "write", "sit", "wait",
        "end", "moment", "finally", "suddenly", "something", "anything",
        "everything", "nothing", "someone", "anyone", "everyone", "maybe",
        "perhaps", "almost", "already", "really", "actually", "probably"
    }

    # Titles to strip from names
    TITLES = {"mr", "mrs", "ms", "miss", "dr", "prof", "sir", "lady", "lord", "king", "queen", "prince", "princess"}

    def analyze(
        self,
        novel_text: str,
        custom_character_list: str = ""
    ) -> Tuple[str, str, str, str, int, int, int, float]:
        
        # Basic stats
        word_count = len(novel_text.split())
        
        # Extract characters
        characters = self._extract_characters(novel_text, custom_character_list)
        
        # Extract scenes
        scenes = self._extract_scenes(novel_text)
        
        # Calculate video duration (150 WPM narration)
        video_minutes = word_count / 150
        video_hours = video_minutes / 60
        
        # Build novel data
        novel_data = {
            "word_count": word_count,
            "character_count": len(novel_text),
            "paragraph_count": len([p for p in novel_text.split('\n\n') if p.strip()]),
            "scene_count": len(scenes),
            "total_characters": len(characters),
            "main_characters": len([c for c in characters if c["tier"] == "main"]),
            "supporting_characters": len([c for c in characters if c["tier"] == "supporting"]),
            "minor_characters": len([c for c in characters if c["tier"] == "minor"]),
            "background_characters": len([c for c in characters if c["tier"] == "background"]),
            "estimated_video_minutes": video_minutes,
            "estimated_video_hours": video_hours,
            "hash": hashlib.md5(novel_text.encode()).hexdigest()[:12]
        }
        
        # Summary
        summary = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          📊 NOVEL ANALYSIS COMPLETE                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  BASIC STATISTICS                                                            ║
║  ├─ Word Count:              {word_count:>10,}                                     ║
║  ├─ Paragraphs:              {novel_data['paragraph_count']:>10,}                                     ║
║  ├─ Scenes Detected:         {len(scenes):>10}                                     ║
║  └─ Est. Video Duration:     {video_hours:>10.1f} hours                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  CHARACTERS DETECTED                                                         ║
║  ├─ Main Characters:         {novel_data['main_characters']:>10} (20+ mentions → 3 refs each)        ║
║  ├─ Supporting Characters:   {novel_data['supporting_characters']:>10} (5-19 mentions → 2 refs each)       ║
║  ├─ Minor Characters:        {novel_data['minor_characters']:>10} (2-4 mentions → 1 ref each)         ║
║  ├─ Background Characters:   {novel_data['background_characters']:>10} (1 mention → no refs)              ║
║  └─ TOTAL:                   {len(characters):>10} characters                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  TOP CHARACTERS                                                              ║
"""
        for i, char in enumerate(characters[:10]):
            tier_icon = {"main": "⭐", "supporting": "🔵", "minor": "⚪", "background": "·"}
            icon = tier_icon.get(char["tier"], "·")
            summary += f"║  {icon} {char['name']:<25} {char['mentions']:>4} mentions ({char['tier']:<10})     ║\n"
        
        if len(characters) > 10:
            summary += f"║  ... and {len(characters) - 10} more characters                                         ║\n"
        
        summary += "╚══════════════════════════════════════════════════════════════════════════════╝"
        
        return (
            json.dumps(novel_data, indent=2),
            json.dumps(characters, indent=2),
            json.dumps(scenes, indent=2),
            summary.strip(),
            word_count,
            len(characters),
            len(scenes),
            video_hours
        )
    
    def _extract_characters(self, text: str, custom_list: str) -> List[Dict]:
        """Extract character names from text with mention counts."""
        
        # Find capitalized words that might be names
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'
        potential_names = re.findall(name_pattern, text)
        
        # Count occurrences
        name_counts = Counter(potential_names)
        
        # Add custom characters
        if custom_list.strip():
            for name in custom_list.strip().split('\n'):
                name = name.strip()
                if name:
                    # Count mentions in text
                    count = len(re.findall(r'\b' + re.escape(name) + r'\b', text, re.IGNORECASE))
                    name_counts[name] = max(name_counts.get(name, 0), count)
        
        # Filter and classify
        characters = []
        for name, count in name_counts.most_common():
            # Skip common words and short names
            if name.lower() in self.COMMON_WORDS:
                continue
            if len(name) < 2:
                continue
            # Skip if it's just a title
            if name.lower() in self.TITLES:
                continue
            # Skip if appears only at start of sentences (likely not a name)
            if count < 2:
                continue
            
            # Determine tier based on mentions
            if count >= 20:
                tier = "main"
                refs_needed = 3
            elif count >= 5:
                tier = "supporting"
                refs_needed = 2
            elif count >= 2:
                tier = "minor"
                refs_needed = 1
            else:
                tier = "background"
                refs_needed = 0
            
            characters.append({
                "name": name,
                "mentions": count,
                "tier": tier,
                "refs_needed": refs_needed,
                "id": f"char_{name.lower().replace(' ', '_')}"
            })
        
        return characters
    
    def _extract_scenes(self, text: str) -> List[Dict]:
        """Extract scenes from text."""
        scenes = []
        
        # Split by common scene breaks
        scene_breaks = re.split(
            r'\n\s*(?:\*\s*\*\s*\*|\#\#\#|---+|___+|\n\n\n+|Chapter\s+\d+|CHAPTER\s+\d+)\s*\n',
            text,
            flags=re.IGNORECASE
        )
        
        # If no breaks found, split by double newlines
        if len(scene_breaks) <= 1:
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            # Group paragraphs into scenes (roughly 500 words each)
            current_scene = []
            current_words = 0
            scene_idx = 0
            
            for para in paragraphs:
                para_words = len(para.split())
                current_scene.append(para)
                current_words += para_words
                
                if current_words >= 500:
                    scene_text = '\n\n'.join(current_scene)
                    scenes.append({
                        "id": f"scene_{scene_idx+1:04d}",
                        "index": scene_idx,
                        "text": scene_text,
                        "word_count": current_words,
                        "paragraph_count": len(current_scene)
                    })
                    scene_idx += 1
                    current_scene = []
                    current_words = 0
            
            # Add remaining
            if current_scene:
                scene_text = '\n\n'.join(current_scene)
                scenes.append({
                    "id": f"scene_{scene_idx+1:04d}",
                    "index": scene_idx,
                    "text": scene_text,
                    "word_count": current_words,
                    "paragraph_count": len(current_scene)
                })
        else:
            for idx, scene_text in enumerate(scene_breaks):
                scene_text = scene_text.strip()
                if scene_text:
                    scenes.append({
                        "id": f"scene_{idx+1:04d}",
                        "index": idx,
                        "text": scene_text,
                        "word_count": len(scene_text.split()),
                        "paragraph_count": len([p for p in scene_text.split('\n\n') if p.strip()])
                    })
        
        return scenes


# =============================================================================
# IMAGE CALCULATOR - Determines exact image counts
# =============================================================================

class ImageCalculator:
    """
    Calculates exactly how many images will be generated.
    """
    
    DESCRIPTION = """
    🔢 Image Calculator
    
    Calculates exact image counts based on:
    • Novel length and structure
    • Image density setting
    • Character reference needs
    • Total generation time estimate
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "novel_data_json": ("STRING", {"multiline": True}),
                "characters_json": ("STRING", {"multiline": True}),
                "image_density": (["sparse", "standard", "cinematic", "dense"], {
                    "default": "standard"
                }),
            },
            "optional": {
                "custom_interval_seconds": ("FLOAT", {
                    "default": 0,
                    "min": 0,
                    "max": 30,
                    "step": 0.5,
                    "tooltip": "Override interval (0 = use density preset)"
                }),
                "include_establishing_shots": ("BOOLEAN", {"default": True}),
                "include_character_closeups": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "INT", "INT", "STRING")
    RETURN_NAMES = (
        "image_plan_json",
        "total_story_images",
        "total_reference_images",
        "total_all_images",
        "calculation_summary"
    )
    FUNCTION = "calculate"
    CATEGORY = "📚 Novel to Images"

    DENSITY_INTERVALS = {
        "sparse": 15,      # 1 image every 15 seconds
        "standard": 10,    # 1 image every 10 seconds
        "cinematic": 6,    # 1 image every 6 seconds
        "dense": 4         # 1 image every 4 seconds
    }

    def calculate(
        self,
        novel_data_json: str,
        characters_json: str,
        image_density: str,
        custom_interval_seconds: float = 0,
        include_establishing_shots: bool = True,
        include_character_closeups: bool = True
    ) -> Tuple[str, int, int, int, str]:
        
        try:
            novel_data = json.loads(novel_data_json)
            characters = json.loads(characters_json)
        except:
            return ("{}", 0, 0, 0, "Error: Invalid JSON input")
        
        # Determine interval
        interval = custom_interval_seconds if custom_interval_seconds > 0 else self.DENSITY_INTERVALS[image_density]
        
        # Calculate video duration
        word_count = novel_data.get("word_count", 0)
        video_seconds = (word_count / 150) * 60  # 150 WPM
        
        # Base story images
        base_images = int(video_seconds / interval)
        
        # Additional images
        establishing_shots = novel_data.get("scene_count", 0) if include_establishing_shots else 0
        
        # Character closeups (1 per main character per 10 scenes)
        main_chars = len([c for c in characters if c.get("tier") == "main"])
        scene_count = novel_data.get("scene_count", 1)
        closeups = int(main_chars * (scene_count / 10)) if include_character_closeups else 0
        
        total_story_images = base_images + establishing_shots + closeups
        
        # Reference images
        ref_images = sum(c.get("refs_needed", 0) for c in characters)
        
        total_all = total_story_images + ref_images
        
        # Build image plan
        image_plan = {
            "density": image_density,
            "interval_seconds": interval,
            "video_duration_seconds": video_seconds,
            "video_duration_hours": video_seconds / 3600,
            
            "story_images": {
                "base_images": base_images,
                "establishing_shots": establishing_shots,
                "character_closeups": closeups,
                "total": total_story_images
            },
            
            "reference_images": {
                "main_characters": len([c for c in characters if c.get("tier") == "main"]) * 3,
                "supporting_characters": len([c for c in characters if c.get("tier") == "supporting"]) * 2,
                "minor_characters": len([c for c in characters if c.get("tier") == "minor"]) * 1,
                "total": ref_images
            },
            
            "total_all_images": total_all,
            
            "storage_estimate_mb": total_all * 5,  # ~5MB per image average
            "storage_estimate_gb": (total_all * 5) / 1024
        }
        
        # Summary
        summary = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          🔢 IMAGE CALCULATION                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  SETTINGS                                                                    ║
║  ├─ Density:                 {image_density:>12}                                    ║
║  ├─ Image Interval:          {interval:>12} seconds                               ║
║  └─ Video Duration:          {video_seconds/3600:>12.1f} hours                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STORY IMAGES                                                                ║
║  ├─ Base Images:             {base_images:>12,}                                    ║
║  ├─ Establishing Shots:      {establishing_shots:>12,}                                    ║
║  ├─ Character Closeups:      {closeups:>12,}                                    ║
║  └─ SUBTOTAL:                {total_story_images:>12,}                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  CHARACTER REFERENCES                                                        ║
║  ├─ Main (3 refs each):      {image_plan['reference_images']['main_characters']:>12,}                                    ║
║  ├─ Supporting (2 each):     {image_plan['reference_images']['supporting_characters']:>12,}                                    ║
║  ├─ Minor (1 each):          {image_plan['reference_images']['minor_characters']:>12,}                                    ║
║  └─ SUBTOTAL:                {ref_images:>12,}                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  ════════════════════════════════════════════════════════════════════════    ║
║  📸 TOTAL IMAGES:            {total_all:>12,}                                    ║
║  💾 Storage Needed:          {image_plan['storage_estimate_gb']:>12.1f} GB                                  ║
║  ════════════════════════════════════════════════════════════════════════    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        return (
            json.dumps(image_plan, indent=2),
            total_story_images,
            ref_images,
            total_all,
            summary.strip()
        )


# =============================================================================
# TURNKEY GENERATOR - Main all-in-one node
# =============================================================================

class TurnkeyNovelToImages:
    """
    Complete turnkey solution - just add model and novel!
    """
    
    DESCRIPTION = """
    🚀 TURNKEY NOVEL TO IMAGES
    
    The ONLY node you need! Just:
    1. Connect your model (SDXL/Flux)
    2. Upload novel file OR paste text
    3. Click Generate!
    
    Supported file formats:
    📄 .txt, .md, .text (plain text)
    📘 .docx (Word documents)
    📕 .pdf (PDF files)
    📗 .epub (Ebooks)
    📙 .rtf (Rich text)
    📓 .html (Web pages)
    
    Automatically handles:
    ✅ Character extraction (unlimited)
    ✅ Tiered reference generation
    ✅ Scene detection
    ✅ Image prompt creation
    ✅ Parallel batch processing
    ✅ Progress tracking
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_mode": (["file_upload", "paste_text"], {
                    "default": "file_upload",
                    "tooltip": "Choose how to provide your novel"
                }),
                "image_density": (["sparse", "standard", "cinematic", "dense"], {
                    "default": "standard",
                    "tooltip": "sparse=fast, cinematic=quality"
                }),
                "style": (["cinematic", "anime", "realistic", "illustrated", "fantasy", "noir"], {
                    "default": "cinematic"
                }),
                "generation_quality": (["draft", "balanced", "quality"], {
                    "default": "balanced",
                    "tooltip": "draft=fast(4step), balanced=good(8step), quality=best(20step)"
                }),
            },
            "optional": {
                "novel_file": ("STRING", {
                    "default": "",
                    "placeholder": "Path to novel file (.txt, .docx, .pdf, .epub, etc.)"
                }),
                "novel_text": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "Or paste your novel text here..."
                }),
                "custom_characters": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "Optional character descriptions:\nElena: young woman, dark hair, green eyes\nMarcus: old wizard, grey beard"
                }),
                "custom_style_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "Optional: Add to all prompts (e.g., 'oil painting style')"
                }),
                "negative_prompt": ("STRING", {
                    "default": "blurry, low quality, distorted, deformed, ugly, bad anatomy, text, watermark, signature, logo",
                    "multiline": True
                }),
                "seed": ("INT", {"default": -1, "min": -1, "max": 2147483647}),
                "batch_size": ("INT", {"default": 4, "min": 1, "max": 16}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "INT", "INT", "STRING")
    RETURN_NAMES = (
        "all_prompts_json",
        "reference_prompts_json",
        "story_prompts_json",
        "characters_json",
        "generation_config_json",
        "total_images",
        "total_batches",
        "full_summary"
    )
    FUNCTION = "process"
    CATEGORY = "📚 Novel to Images"
    
    # Style templates
    STYLES = {
        "cinematic": "cinematic film still, dramatic lighting, shallow depth of field, color graded, 8k, photorealistic",
        "anime": "anime art style, studio ghibli inspired, vibrant colors, detailed linework, expressive",
        "realistic": "photorealistic, hyperdetailed, natural lighting, professional photography, 8k uhd",
        "illustrated": "digital illustration, detailed artwork, artstation trending, concept art",
        "fantasy": "epic fantasy art, magical atmosphere, detailed environment, dramatic lighting, painterly",
        "noir": "film noir style, high contrast, black and white with color accents, dramatic shadows, moody"
    }
    
    # Quality presets
    QUALITY_PRESETS = {
        "draft": {"steps": 4, "cfg": 1.0, "speed": 0.5},
        "balanced": {"steps": 8, "cfg": 2.0, "speed": 1.0},
        "quality": {"steps": 20, "cfg": 7.0, "speed": 2.5}
    }
    
    # Density intervals
    DENSITY_INTERVALS = {
        "sparse": 15,
        "standard": 10,
        "cinematic": 6,
        "dense": 4
    }

    def process(
        self,
        input_mode: str,
        image_density: str,
        style: str,
        generation_quality: str,
        novel_file: str = "",
        novel_text: str = "",
        custom_characters: str = "",
        custom_style_prompt: str = "",
        negative_prompt: str = "",
        seed: int = -1,
        batch_size: int = 4
    ) -> Tuple[str, str, str, str, str, int, int, str]:
        
        # ===== STEP 0: Load Novel from File or Text =====
        if input_mode == "file_upload" and novel_file:
            loader = NovelFileLoader()
            loaded_text, file_info, loaded_words, load_status = loader.load(
                file_path=novel_file,
                encoding="auto",
                clean_text=True,
                remove_headers_footers=True
            )
            
            if not loaded_text:
                # Return error state
                error_summary = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          ❌ FILE LOAD ERROR                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Status: {load_status:<60} ║
║                                                                              ║
║  Please check:                                                               ║
║  • File path is correct                                                      ║
║  • File exists and is readable                                               ║
║  • File format is supported (.txt, .docx, .pdf, .epub, .rtf, .html)         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
                return ("[]", "[]", "[]", "[]", "{}", 0, 0, error_summary.strip())
            
            actual_novel_text = loaded_text
            source_info = f"File: {os.path.basename(novel_file)}"
        else:
            # Use pasted text
            actual_novel_text = novel_text
            source_info = "Pasted text"
        
        if not actual_novel_text or len(actual_novel_text.strip()) < 100:
            error_summary = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                          ❌ NO NOVEL TEXT PROVIDED                            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Please provide your novel by either:                                        ║
║                                                                              ║
║  1. FILE UPLOAD (Recommended)                                                ║
║     • Set input_mode to "file_upload"                                        ║
║     • Enter the path to your novel file in "novel_file"                      ║
║     • Supported: .txt, .docx, .pdf, .epub, .rtf, .html                       ║
║                                                                              ║
║  2. PASTE TEXT                                                               ║
║     • Set input_mode to "paste_text"                                         ║
║     • Paste your novel into the "novel_text" field                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
            return ("[]", "[]", "[]", "[]", "{}", 0, 0, error_summary.strip())
        
        # ===== STEP 1: Analyze Novel =====
        analyzer = NovelAnalyzer()
        novel_data_json, characters_json, scenes_json, analysis_summary, word_count, char_count, scene_count, video_hours = analyzer.analyze(
            novel_text=actual_novel_text,
            custom_character_list=custom_characters.split('\n')[0] if ':' not in custom_characters else ""
        )
        
        novel_data = json.loads(novel_data_json)
        characters = json.loads(characters_json)
        scenes = json.loads(scenes_json)
        
        # Parse custom character descriptions
        char_descriptions = {}
        if custom_characters.strip():
            for line in custom_characters.strip().split('\n'):
                if ':' in line:
                    name, desc = line.split(':', 1)
                    char_descriptions[name.strip().lower()] = desc.strip()
        
        # Update characters with descriptions
        for char in characters:
            char_name_lower = char["name"].lower()
            if char_name_lower in char_descriptions:
                char["description"] = char_descriptions[char_name_lower]
            else:
                char["description"] = f"character named {char['name']}"
        
        # ===== STEP 2: Calculate Images =====
        calculator = ImageCalculator()
        image_plan_json, total_story_images, total_ref_images, total_all_images, calc_summary = calculator.calculate(
            novel_data_json=novel_data_json,
            characters_json=characters_json,
            image_density=image_density
        )
        
        image_plan = json.loads(image_plan_json)
        
        # ===== STEP 3: Generate Reference Prompts =====
        style_template = self.STYLES.get(style, self.STYLES["cinematic"])
        quality_preset = self.QUALITY_PRESETS.get(generation_quality, self.QUALITY_PRESETS["balanced"])
        
        reference_prompts = []
        
        for char in characters:
            refs_needed = char.get("refs_needed", 0)
            if refs_needed == 0:
                continue
            
            name = char["name"]
            desc = char.get("description", f"character named {name}")
            
            views = [
                ("front", "front view portrait, facing camera, head and shoulders"),
                ("three_quarter", "three-quarter view portrait, slight turn, head and shoulders"),
                ("profile", "side profile portrait, head and shoulders")
            ]
            
            for view_name, view_desc in views[:refs_needed]:
                prompt = f"character portrait of {name}, {desc}, {view_desc}, {style_template}, neutral background, high quality detailed face"
                if custom_style_prompt:
                    prompt += f", {custom_style_prompt}"
                
                reference_prompts.append({
                    "type": "reference",
                    "id": f"ref_{name.lower().replace(' ', '_')}_{view_name}",
                    "character": name,
                    "view": view_name,
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "width": 1024,
                    "height": 1024,
                    "seed": seed if seed >= 0 else None
                })
        
        # ===== STEP 4: Generate Story Prompts =====
        story_prompts = []
        interval = self.DENSITY_INTERVALS.get(image_density, 10)
        
        shot_types = [
            ("establishing", "wide establishing shot showing the environment"),
            ("medium", "medium shot"),
            ("close_up", "close-up shot showing emotion"),
            ("detail", "detail shot of important element"),
            ("wide", "wide shot showing full scene"),
            ("over_shoulder", "over-the-shoulder shot"),
            ("two_shot", "two-shot showing characters together"),
            ("reaction", "reaction shot capturing expression")
        ]
        
        prompt_idx = 0
        
        for scene in scenes:
            scene_text = scene.get("text", "")
            scene_word_count = scene.get("word_count", len(scene_text.split()))
            scene_duration = (scene_word_count / 150) * 60  # seconds
            images_for_scene = max(1, int(scene_duration / interval))
            
            # Find characters in this scene
            chars_in_scene = []
            for char in characters:
                if char["name"].lower() in scene_text.lower():
                    chars_in_scene.append(char)
            
            # Extract scene context
            scene_snippet = scene_text[:200].replace('\n', ' ')
            
            for img_idx in range(images_for_scene):
                shot_type, shot_desc = shot_types[img_idx % len(shot_types)]
                
                # Build character portion
                char_prompt = ""
                char_refs_for_prompt = []
                
                if chars_in_scene and shot_type not in ["establishing", "detail"]:
                    # Include character descriptions
                    char_descs = []
                    for c in chars_in_scene[:2]:
                        char_descs.append(f"{c['name']}, {c.get('description', '')}")
                        if c.get("refs_needed", 0) > 0:
                            char_refs_for_prompt.append({
                                "name": c["name"],
                                "ref_id": f"ref_{c['name'].lower().replace(' ', '_')}_front"
                            })
                    char_prompt = f"featuring {' and '.join(char_descs)}"
                
                # Build full prompt
                prompt = f"{shot_desc}, {style_template}, {char_prompt}, scene: {scene_snippet}"
                if custom_style_prompt:
                    prompt += f", {custom_style_prompt}"
                
                story_prompts.append({
                    "type": "story",
                    "id": f"scene_{scene['index']+1:04d}_shot_{img_idx+1:03d}",
                    "scene_idx": scene["index"],
                    "shot_idx": img_idx,
                    "shot_type": shot_type,
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "width": 1024,
                    "height": 576,  # 16:9 cinematic
                    "characters": [c["name"] for c in chars_in_scene],
                    "character_refs": char_refs_for_prompt,
                    "seed": seed if seed >= 0 else None
                })
                prompt_idx += 1
        
        # ===== STEP 5: Combine All Prompts =====
        all_prompts = reference_prompts + story_prompts
        total_images = len(all_prompts)
        total_batches = math.ceil(total_images / batch_size)
        
        # ===== STEP 6: Generation Config =====
        generation_config = {
            "total_images": total_images,
            "total_reference_images": len(reference_prompts),
            "total_story_images": len(story_prompts),
            "batch_size": batch_size,
            "total_batches": total_batches,
            "quality_preset": generation_quality,
            "quality_settings": quality_preset,
            "style": style,
            "density": image_density,
            "interval_seconds": interval,
            
            "estimated_time": {
                "per_image_seconds": quality_preset["speed"],
                "total_seconds": total_images * quality_preset["speed"],
                "total_minutes": (total_images * quality_preset["speed"]) / 60,
                "total_hours": (total_images * quality_preset["speed"]) / 3600
            },
            
            "character_summary": {
                "total": len(characters),
                "main": len([c for c in characters if c["tier"] == "main"]),
                "supporting": len([c for c in characters if c["tier"] == "supporting"]),
                "minor": len([c for c in characters if c["tier"] == "minor"]),
                "with_refs": len([c for c in characters if c.get("refs_needed", 0) > 0])
            }
        }
        
        # ===== STEP 7: Full Summary =====
        est_time = generation_config["estimated_time"]
        time_str = f"{est_time['total_minutes']:.1f} min" if est_time['total_minutes'] < 60 else f"{est_time['total_hours']:.1f} hrs"
        
        full_summary = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     🚀 TURNKEY NOVEL TO IMAGES - READY!                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  📂 SOURCE: {source_info:<55} ║
║                                                                              ║
║  📖 NOVEL                                                                    ║
║  ├─ Words:               {word_count:>12,}                                        ║
║  ├─ Scenes:              {scene_count:>12}                                        ║
║  └─ Video Duration:      {video_hours:>12.1f} hours                                  ║
║                                                                              ║
║  👥 CHARACTERS (Unlimited - Tiered References)                               ║
║  ├─ Main (⭐ 3 refs):    {generation_config['character_summary']['main']:>12} characters                           ║
║  ├─ Supporting (🔵 2):   {generation_config['character_summary']['supporting']:>12} characters                           ║
║  ├─ Minor (⚪ 1 ref):    {generation_config['character_summary']['minor']:>12} characters                           ║
║  └─ TOTAL:               {generation_config['character_summary']['total']:>12} characters                           ║
║                                                                              ║
║  🖼️  IMAGES                                                                   ║
║  ├─ Reference Images:    {len(reference_prompts):>12}                                        ║
║  ├─ Story Images:        {len(story_prompts):>12,}                                        ║
║  ├─ TOTAL:               {total_images:>12,}                                        ║
║  └─ Batches:             {total_batches:>12}                                        ║
║                                                                              ║
║  ⚙️  SETTINGS                                                                 ║
║  ├─ Style:               {style:>12}                                        ║
║  ├─ Density:             {image_density:>12}                                        ║
║  ├─ Quality:             {generation_quality:>12}                                        ║
║  └─ Steps:               {quality_preset['steps']:>12}                                        ║
║                                                                              ║
║  ⏱️  ESTIMATED TIME                                                           ║
║  └─ Generation:          {time_str:>12}                                        ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ✅ READY TO GENERATE!                                                        ║
║                                                                              ║
║  Connect outputs to:                                                         ║
║  • all_prompts_json → TurnkeyBatchProcessor → Your Sampler                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        return (
            json.dumps(all_prompts, indent=2),
            json.dumps(reference_prompts, indent=2),
            json.dumps(story_prompts, indent=2),
            json.dumps(characters, indent=2),
            json.dumps(generation_config, indent=2),
            total_images,
            total_batches,
            full_summary.strip()
        )


# =============================================================================
# BATCH PROCESSOR - Feeds prompts to sampler
# =============================================================================

class TurnkeyBatchProcessor:
    """
    Processes prompts in batches for the sampler.
    """
    
    DESCRIPTION = """
    ⚡ Turnkey Batch Processor
    
    Feeds prompts to your sampler in batches:
    • Automatic batch sizing
    • Progress tracking
    • Reference/Story separation
    • Ready for any sampler node
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "all_prompts_json": ("STRING", {"multiline": True}),
                "generation_config_json": ("STRING", {"multiline": True}),
                "batch_index": ("INT", {"default": 0, "min": 0}),
            },
            "optional": {
                "process_references_first": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "INT", "INT", "INT", "BOOLEAN", "STRING", "STRING")
    RETURN_NAMES = (
        "batch_prompts_json",
        "batch_negative_json",
        "batch_width",
        "batch_height", 
        "current_batch",
        "total_batches",
        "has_more",
        "progress_text",
        "batch_ids_json"
    )
    FUNCTION = "get_batch"
    CATEGORY = "📚 Novel to Images"

    def get_batch(
        self,
        all_prompts_json: str,
        generation_config_json: str,
        batch_index: int,
        process_references_first: bool = True
    ) -> Tuple[str, str, int, int, int, int, bool, str, str]:
        
        try:
            all_prompts = json.loads(all_prompts_json)
            config = json.loads(generation_config_json)
        except:
            return ("[]", "[]", 1024, 1024, 0, 0, False, "Error", "[]")
        
        batch_size = config.get("batch_size", 4)
        
        # Optionally sort references first
        if process_references_first:
            refs = [p for p in all_prompts if p.get("type") == "reference"]
            story = [p for p in all_prompts if p.get("type") == "story"]
            all_prompts = refs + story
        
        total_prompts = len(all_prompts)
        total_batches = math.ceil(total_prompts / batch_size)
        
        # Get batch
        start = batch_index * batch_size
        end = min(start + batch_size, total_prompts)
        
        if start >= total_prompts:
            return ("[]", "[]", 1024, 1024, batch_index, total_batches, False, "Complete!", "[]")
        
        batch = all_prompts[start:end]
        
        # Extract data
        prompts = [p["prompt"] for p in batch]
        negatives = [p.get("negative_prompt", "") for p in batch]
        ids = [p["id"] for p in batch]
        
        # Use dimensions from first prompt in batch
        width = batch[0].get("width", 1024)
        height = batch[0].get("height", 1024)
        
        has_more = batch_index < total_batches - 1
        
        # Progress
        completed = end
        percent = (completed / total_prompts) * 100
        bar_filled = int(percent / 5)
        bar = "█" * bar_filled + "░" * (20 - bar_filled)
        
        # Determine what we're processing
        batch_types = set(p.get("type", "unknown") for p in batch)
        type_str = "/".join(batch_types)
        
        progress_text = f"[{bar}] {percent:.0f}% | Batch {batch_index+1}/{total_batches} | {type_str} | {completed}/{total_prompts} images"
        
        return (
            json.dumps(prompts),
            json.dumps(negatives),
            width,
            height,
            batch_index,
            total_batches,
            has_more,
            progress_text,
            json.dumps(ids)
        )


# =============================================================================
# SINGLE PROMPT EXTRACTOR - For non-batch samplers
# =============================================================================

class TurnkeySinglePrompt:
    """
    Extracts single prompts for samplers that don't support batching.
    """
    
    DESCRIPTION = """
    🔄 Single Prompt Extractor
    
    For samplers that process one image at a time:
    • Extracts individual prompts
    • Provides all necessary parameters
    • Tracks progress
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "all_prompts_json": ("STRING", {"multiline": True}),
                "prompt_index": ("INT", {"default": 0, "min": 0}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "INT", "STRING", "STRING", "INT", "BOOLEAN", "STRING")
    RETURN_NAMES = (
        "prompt",
        "negative_prompt",
        "width",
        "height",
        "image_id",
        "image_type",
        "total_images",
        "has_more",
        "progress_text"
    )
    FUNCTION = "extract"
    CATEGORY = "📚 Novel to Images"

    def extract(
        self,
        all_prompts_json: str,
        prompt_index: int
    ) -> Tuple[str, str, int, int, str, str, int, bool, str]:
        
        try:
            all_prompts = json.loads(all_prompts_json)
        except:
            return ("", "", 1024, 1024, "", "", 0, False, "Error")
        
        total = len(all_prompts)
        
        if prompt_index >= total:
            return ("", "", 1024, 1024, "", "", total, False, "Complete!")
        
        prompt_data = all_prompts[prompt_index]
        
        prompt = prompt_data.get("prompt", "")
        negative = prompt_data.get("negative_prompt", "")
        width = prompt_data.get("width", 1024)
        height = prompt_data.get("height", 1024)
        image_id = prompt_data.get("id", f"img_{prompt_index}")
        image_type = prompt_data.get("type", "unknown")
        
        has_more = prompt_index < total - 1
        
        percent = ((prompt_index + 1) / total) * 100
        bar_filled = int(percent / 5)
        bar = "█" * bar_filled + "░" * (20 - bar_filled)
        progress_text = f"[{bar}] {percent:.0f}% | {prompt_index+1}/{total} | {image_type} | {image_id}"
        
        return (
            prompt,
            negative,
            width,
            height,
            image_id,
            image_type,
            total,
            has_more,
            progress_text
        )


# =============================================================================
# GPU TIME ESTIMATOR
# =============================================================================

class GPUTimeEstimator:
    """
    Estimates generation time for different GPU configurations.
    """
    
    DESCRIPTION = """
    ⏱️ GPU Time Estimator
    
    Shows generation time estimates for:
    • Different GPU models
    • Different quality settings
    • Multi-GPU configurations
    • Cloud rental costs
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "total_images": ("INT", {"default": 1000, "min": 1}),
                "generation_quality": (["draft", "balanced", "quality"],),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("time_estimates",)
    FUNCTION = "estimate"
    CATEGORY = "📚 Novel to Images"

    GPU_SPEEDS = {
        # GPU: base seconds per image at "balanced" quality
        "RTX 3060 12GB": 2.0,
        "RTX 3070 8GB": 1.7,
        "RTX 3080 10GB": 1.3,
        "RTX 3090 24GB": 1.0,
        "RTX 4070 Ti 12GB": 1.1,
        "RTX 4080 16GB": 0.8,
        "RTX 4090 24GB": 0.6,
        "A6000 48GB": 0.7,
        "A100 40GB": 0.5,
        "A100 80GB": 0.45,
        "H100 80GB": 0.3,
    }
    
    QUALITY_MULTIPLIERS = {
        "draft": 0.4,      # 4-step
        "balanced": 1.0,   # 8-step
        "quality": 2.5     # 20-step
    }
    
    CLOUD_COSTS = {
        "Vast.ai RTX 4090": 0.40,
        "Vast.ai A100": 1.20,
        "RunPod RTX 4090": 0.74,
        "RunPod A100": 1.99,
        "Lambda A100": 1.10,
        "Lambda A100x4": 4.40,
    }

    def estimate(
        self,
        total_images: int,
        generation_quality: str
    ) -> Tuple[str]:
        
        quality_mult = self.QUALITY_MULTIPLIERS.get(generation_quality, 1.0)
        
        estimates = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ⏱️  GPU TIME ESTIMATES FOR {total_images:,} IMAGES                     ║
║                         Quality: {generation_quality.upper():^10}                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  💻 CONSUMER GPUs                                                            ║
"""
        
        consumer_gpus = ["RTX 3060 12GB", "RTX 3080 10GB", "RTX 4070 Ti 12GB", "RTX 4090 24GB"]
        for gpu in consumer_gpus:
            base_speed = self.GPU_SPEEDS[gpu]
            total_sec = total_images * base_speed * quality_mult
            time_str = self._format_time(total_sec)
            estimates += f"║  ├─ {gpu:<18}  {time_str:>12}                              ║\n"
        
        estimates += """║                                                                              ║
║  🏢 PROFESSIONAL GPUs                                                        ║
"""
        
        pro_gpus = ["A6000 48GB", "A100 80GB", "H100 80GB"]
        for gpu in pro_gpus:
            base_speed = self.GPU_SPEEDS[gpu]
            total_sec = total_images * base_speed * quality_mult
            time_str = self._format_time(total_sec)
            estimates += f"║  ├─ {gpu:<18}  {time_str:>12}                              ║\n"
        
        estimates += """║                                                                              ║
║  🔄 MULTI-GPU (RTX 4090 × N)                                                 ║
"""
        
        base_4090 = self.GPU_SPEEDS["RTX 4090 24GB"]
        for num_gpus in [2, 4, 8]:
            total_sec = (total_images * base_4090 * quality_mult) / num_gpus
            time_str = self._format_time(total_sec)
            estimates += f"║  ├─ {num_gpus}× RTX 4090           {time_str:>12}                              ║\n"
        
        estimates += """║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  ☁️  CLOUD RENTAL COSTS                                                       ║
"""
        
        for provider, hourly_cost in self.CLOUD_COSTS.items():
            if "4090" in provider:
                speed = self.GPU_SPEEDS["RTX 4090 24GB"]
            elif "x4" in provider:
                speed = self.GPU_SPEEDS["A100 80GB"] / 4
            else:
                speed = self.GPU_SPEEDS["A100 80GB"]
            
            total_sec = total_images * speed * quality_mult
            hours = total_sec / 3600
            cost = hours * hourly_cost
            time_str = self._format_time(total_sec)
            
            estimates += f"║  ├─ {provider:<20}  {time_str:>10}  ~${cost:>6.2f}                  ║\n"
        
        estimates += """║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  💡 RECOMMENDATIONS                                                          ║
║                                                                              ║
"""
        
        # Add recommendations based on image count
        if total_images < 100:
            estimates += """║  • Any modern GPU will work fine for this small batch                       ║
║  • Use "draft" quality for testing, "balanced" for final                    ║
"""
        elif total_images < 500:
            estimates += """║  • RTX 4070 Ti or better recommended                                        ║
║  • Consider cloud GPU for faster results                                    ║
"""
        elif total_images < 2000:
            estimates += """║  • RTX 4090 recommended for reasonable turnaround                           ║
║  • Cloud A100 offers best value (~$2-5 total)                               ║
"""
        else:
            estimates += """║  • Multi-GPU or cloud strongly recommended                                  ║
║  • Consider running overnight with checkpoint saves                         ║
║  • Best value: Vast.ai A100 (~$2-8 total)                                  ║
"""
        
        estimates += """║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        return (estimates.strip(),)
    
    def _format_time(self, seconds: float) -> str:
        if seconds < 60:
            return f"{seconds:.0f} sec"
        elif seconds < 3600:
            return f"{seconds/60:.1f} min"
        else:
            return f"{seconds/3600:.1f} hrs"


# =============================================================================
# NODE MAPPINGS
# =============================================================================

NODE_CLASS_MAPPINGS = {
    "NovelFileLoader": NovelFileLoader,
    "NovelAnalyzer": NovelAnalyzer,
    "ImageCalculator": ImageCalculator,
    "TurnkeyNovelToImages": TurnkeyNovelToImages,
    "TurnkeyBatchProcessor": TurnkeyBatchProcessor,
    "TurnkeySinglePrompt": TurnkeySinglePrompt,
    "GPUTimeEstimator": GPUTimeEstimator,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NovelFileLoader": "📂 Novel File Loader",
    "NovelAnalyzer": "📊 Novel Analyzer",
    "ImageCalculator": "🔢 Image Calculator",
    "TurnkeyNovelToImages": "🚀 Turnkey Novel to Images",
    "TurnkeyBatchProcessor": "⚡ Turnkey Batch Processor",
    "TurnkeySinglePrompt": "🔄 Single Prompt Extractor",
    "GPUTimeEstimator": "⏱️ GPU Time Estimator",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
