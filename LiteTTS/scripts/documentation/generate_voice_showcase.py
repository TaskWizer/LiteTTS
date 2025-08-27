#!/usr/bin/env python3
"""
Voice Showcase Generator

Generates a comprehensive markdown page showcasing all available voices
with audio samples and organized categorization.
"""

import requests
import json
import os
import time
from typing import Dict, List, Any
from pathlib import Path

# Voice categorization based on naming patterns
VOICE_CATEGORIES = {
    "American Female": {
        "prefix": "af_",
        "description": "American English female voices with diverse characteristics",
        "voices": []
    },
    "American Male": {
        "prefix": "am_",
        "description": "American English male voices with varied tones and styles",
        "voices": []
    },
    "British Female": {
        "prefix": "bf_",
        "description": "British English female voices with authentic accents",
        "voices": []
    },
    "British Male": {
        "prefix": "bm_",
        "description": "British English male voices with classic British pronunciation",
        "voices": []
    },
    "European Female": {
        "prefix": "ef_",
        "description": "European English female voices",
        "voices": []
    },
    "European Male": {
        "prefix": "em_",
        "description": "European English male voices",
        "voices": []
    },
    "French Female": {
        "prefix": "ff_",
        "description": "French-accented female voices",
        "voices": []
    },
    "Hindi Female": {
        "prefix": "hf_",
        "description": "Hindi-accented female voices",
        "voices": []
    },
    "Hindi Male": {
        "prefix": "hm_",
        "description": "Hindi-accented male voices",
        "voices": []
    },
    "Italian Female": {
        "prefix": "if_",
        "description": "Italian-accented female voices",
        "voices": []
    },
    "Italian Male": {
        "prefix": "im_",
        "description": "Italian-accented male voices",
        "voices": []
    },
    "Japanese Female": {
        "prefix": "jf_",
        "description": "Japanese female voices with authentic pronunciation",
        "voices": []
    },
    "Japanese Male": {
        "prefix": "jm_",
        "description": "Japanese male voices",
        "voices": []
    },
    "Portuguese Female": {
        "prefix": "pf_",
        "description": "Portuguese-accented female voices",
        "voices": []
    },
    "Portuguese Male": {
        "prefix": "pm_",
        "description": "Portuguese-accented male voices",
        "voices": []
    },
    "Chinese Female": {
        "prefix": "zf_",
        "description": "Chinese female voices with Mandarin pronunciation",
        "voices": []
    },
    "Chinese Male": {
        "prefix": "zm_",
        "description": "Chinese male voices with Mandarin pronunciation",
        "voices": []
    }
}

# Sample texts for different languages/accents
SAMPLE_TEXTS = {
    "english": "Hello, welcome to Kokoro TTS. This voice demonstrates natural speech synthesis with clear pronunciation and expressive delivery.",
    "japanese": "こんにちは、Kokoro TTSへようこそ。この音声は自然な音声合成を実演します。",
    "chinese": "你好，欢迎使用Kokoro TTS。这个声音展示了自然的语音合成技术。",
    "multilingual": "Hello world! This is a demonstration of high-quality text-to-speech synthesis."
}

def get_available_voices() -> List[str]:
    """Get list of available voices from API"""
    try:
        response = requests.get("http://localhost:8354/v1/voices", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("voices", [])
        else:
            print(f"❌ Failed to get voices: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting voices: {e}")
        return []

def categorize_voices(voices: List[str]) -> Dict[str, Any]:
    """Categorize voices by their prefixes"""
    categorized = {}
    
    for category_name, category_info in VOICE_CATEGORIES.items():
        categorized[category_name] = {
            "description": category_info["description"],
            "voices": []
        }
    
    # Categorize voices
    for voice in voices:
        categorized_voice = False
        for category_name, category_info in VOICE_CATEGORIES.items():
            if voice.startswith(category_info["prefix"]):
                categorized[category_name]["voices"].append(voice)
                categorized_voice = True
                break
        
        if not categorized_voice:
            # Handle uncategorized voices
            if "Other" not in categorized:
                categorized["Other"] = {
                    "description": "Other voices that don't fit standard categories",
                    "voices": []
                }
            categorized["Other"]["voices"].append(voice)
    
    # Remove empty categories
    return {k: v for k, v in categorized.items() if v["voices"]}

def generate_audio_sample(voice: str, text: str, output_dir: str) -> str:
    """Generate audio sample for a voice"""
    filename = f"{voice}_sample.mp3"
    filepath = os.path.join(output_dir, filename)
    
    # Skip if file already exists
    if os.path.exists(filepath):
        print(f"   ✓ Sample exists: {filename}")
        return filename
    
    try:
        payload = {
            "input": text,
            "voice": voice,
            "response_format": "mp3"
        }
        
        response = requests.post(
            "http://localhost:8354/v1/audio/speech",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"   ✅ Generated: {filename}")
            return filename
        else:
            print(f"   ❌ Failed: {voice} (HTTP {response.status_code})")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {voice} - {e}")
        return None

def get_sample_text_for_voice(voice: str) -> str:
    """Get appropriate sample text based on voice characteristics"""
    if voice.startswith(('jf_', 'jm_')):
        return SAMPLE_TEXTS["japanese"]
    elif voice.startswith(('zf_', 'zm_')):
        return SAMPLE_TEXTS["chinese"]
    else:
        return SAMPLE_TEXTS["english"]

def generate_voice_showcase(output_dir: str = "docs/voices") -> bool:
    """Generate the complete voice showcase"""
    
    print("🎭 Generating Voice Showcase")
    print("=" * 40)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get available voices
    print("📋 Getting available voices...")
    voices = get_available_voices()
    if not voices:
        print("❌ No voices available")
        return False
    
    print(f"✅ Found {len(voices)} voices")
    
    # Categorize voices
    print("📂 Categorizing voices...")
    categorized_voices = categorize_voices(voices)
    print(f"✅ Organized into {len(categorized_voices)} categories")
    
    # Generate audio samples
    print("🎵 Generating audio samples...")
    total_samples = 0
    successful_samples = 0
    
    for category_name, category_data in categorized_voices.items():
        print(f"\n📁 {category_name} ({len(category_data['voices'])} voices)")
        
        for voice in category_data['voices']:
            sample_text = get_sample_text_for_voice(voice)
            filename = generate_audio_sample(voice, sample_text, output_dir)
            total_samples += 1
            if filename:
                successful_samples += 1
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
    
    print(f"\n📊 Generated {successful_samples}/{total_samples} audio samples")
    
    # Generate markdown
    print("📝 Generating markdown documentation...")
    markdown_content = generate_markdown(categorized_voices, output_dir)
    
    # Write markdown file
    markdown_path = os.path.join(output_dir, "README.md")
    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"✅ Voice showcase generated: {markdown_path}")
    
    # Update main README
    print("📝 Updating main README...")
    update_main_readme()
    
    return True

def generate_markdown(categorized_voices: Dict[str, Any], output_dir: str) -> str:
    """Generate markdown content for voice showcase"""
    
    total_voices = sum(len(cat["voices"]) for cat in categorized_voices.values())
    
    markdown = f"""# 🎭 Kokoro TTS Voice Showcase

Welcome to the comprehensive showcase of all **{total_voices} voices** available in Kokoro TTS! Each voice has been carefully crafted to provide natural, expressive speech synthesis across multiple languages and accents.

## 🌟 Quick Navigation

"""
    
    # Add navigation links
    for category_name in categorized_voices.keys():
        anchor = category_name.lower().replace(" ", "-")
        markdown += f"- [{category_name}](#{anchor}) ({len(categorized_voices[category_name]['voices'])} voices)\n"
    
    markdown += f"""
## 🎯 How to Use

Each voice can be used with the Kokoro ONNX TTS API by specifying the voice name:

```bash
curl -X POST "http://localhost:8354/v1/audio/speech" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "input": "Your text here",
    "voice": "af_heart",
    "response_format": "mp3"
  }}' \\
  --output output.mp3
```

## 🎵 Voice Categories

"""
    
    # Generate content for each category
    for category_name, category_data in categorized_voices.items():
        anchor = category_name.lower().replace(" ", "-")
        markdown += f"### {category_name}\n\n"
        markdown += f"*{category_data['description']}*\n\n"
        
        # Create table header
        markdown += "| Voice | Sample | Description |\n"
        markdown += "|-------|--------|-------------|\n"
        
        # Add each voice
        for voice in sorted(category_data['voices']):
            sample_file = f"{voice}_sample.mp3"
            sample_path = os.path.join(output_dir, sample_file)
            
            # Check if sample exists
            if os.path.exists(sample_path):
                audio_link = f'<audio controls><source src="{sample_file}" type="audio/mpeg">Your browser does not support audio.</audio>'
            else:
                audio_link = "*Sample not available*"
            
            # Generate description based on voice name
            description = generate_voice_description(voice)
            
            markdown += f"| **{voice}** | {audio_link} | {description} |\n"
        
        markdown += "\n"
    
    # Add footer
    markdown += f"""
---

## 📊 Statistics

- **Total Voices**: {total_voices}
- **Categories**: {len(categorized_voices)}
- **Languages**: English, Japanese, Chinese, and more
- **Accents**: American, British, European, Asian, and regional variants

## 🔧 Technical Details

All audio samples are generated using:
- **Format**: MP3 (128kbps)
- **Sample Rate**: 24kHz
- **Bit Depth**: 16-bit
- **Optimization**: Web-optimized for fast loading

## 🚀 Getting Started

1. **Choose a voice** from the categories above
2. **Copy the voice name** (e.g., `af_heart`)
3. **Use it in your API calls** or applications
4. **Experiment** with different voices to find the perfect match for your project

## 📚 Additional Resources

- [Main Documentation](../../README.md)
- [API Reference](../../docs/api.md)
- [Configuration Guide](../../docs/configuration.md)
- [SSML Support](../../docs/ssml.md)

---

*Generated automatically by Kokoro TTS Voice Showcase Generator*
"""
    
    return markdown

def generate_voice_description(voice: str) -> str:
    """Generate a description for a voice based on its name"""
    
    # Extract the name part after the prefix
    if '_' in voice:
        prefix, name = voice.split('_', 1)
    else:
        prefix, name = '', voice
    
    # Special descriptions for known voices
    descriptions = {
        'heart': 'Warm and expressive, perfect for emotional content',
        'sky': 'Clear and bright, ideal for professional narration',
        'bella': 'Elegant and sophisticated, great for formal presentations',
        'sarah': 'Friendly and approachable, excellent for conversational content',
        'nova': 'Modern and dynamic, suitable for tech and innovation topics',
        'alloy': 'Strong and confident, perfect for authoritative content',
        'echo': 'Resonant and memorable, ideal for announcements',
        'onyx': 'Deep and rich, excellent for dramatic readings',
        'adam': 'Classic and reliable, great for educational content',
        'liam': 'Youthful and energetic, perfect for casual conversations',
        'michael': 'Professional and clear, ideal for business communications',
        'alice': 'Gentle and soothing, excellent for storytelling',
        'emma': 'Bright and cheerful, perfect for upbeat content',
        'daniel': 'Authoritative and clear, great for news and announcements',
        'george': 'Distinguished and mature, ideal for formal presentations',
        'santa': 'Jolly and warm, perfect for holiday content',
        'alpha': 'Precise and technical, ideal for scientific content',
        'beta': 'Experimental and unique, great for creative projects',
        'omega': 'Powerful and commanding, perfect for dramatic content',
        'psi': 'Mysterious and intriguing, ideal for storytelling'
    }
    
    # Return specific description if available, otherwise generate generic one
    if name in descriptions:
        return descriptions[name]
    else:
        # Generate based on prefix
        if prefix.startswith('a'):
            return 'Natural American accent with clear pronunciation'
        elif prefix.startswith('b'):
            return 'Authentic British accent with classic pronunciation'
        elif prefix.startswith('j'):
            return 'Native Japanese pronunciation with natural intonation'
        elif prefix.startswith('z'):
            return 'Native Chinese pronunciation with Mandarin tones'
        else:
            return 'High-quality voice with natural speech patterns'

def update_main_readme():
    """Update the main README.md to include link to voice showcase"""
    readme_path = "README.md"
    
    if not os.path.exists(readme_path):
        print("⚠️ Main README.md not found")
        return
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if voice showcase link already exists
        if "docs/voices" in content or "Voice Showcase" in content:
            print("✅ Voice showcase link already exists in README")
            return
        
        # Find a good place to insert the link (after features section)
        if "## Features" in content:
            # Insert after features section
            features_end = content.find("## Features")
            next_section = content.find("##", features_end + 1)
            
            if next_section != -1:
                voice_showcase_section = f"""
## 🎭 Voice Showcase

Explore all **54+ available voices** with audio samples and detailed comparisons:

**[🎵 Browse Voice Showcase →](docs/voices/README.md)**

Featuring voices in multiple languages and accents:
- American English (Male & Female)
- British English (Male & Female) 
- Japanese (Male & Female)
- Chinese Mandarin (Male & Female)
- European, Hindi, Italian, Portuguese, and French accents

"""
                content = content[:next_section] + voice_showcase_section + content[next_section:]
                
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("✅ Added voice showcase link to main README")
            else:
                print("⚠️ Could not find insertion point in README")
        else:
            print("⚠️ Could not find Features section in README")
            
    except Exception as e:
        print(f"❌ Error updating README: {e}")

if __name__ == "__main__":
    success = generate_voice_showcase()
    exit(0 if success else 1)
