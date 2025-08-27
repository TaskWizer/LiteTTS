# 🔌 OpenWebUI Integration Guide - Kokoro ONNX TTS API

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../FEATURES.md) | [Configuration](../CONFIGURATION.md) | [Performance](../PERFORMANCE.md) | [Monitoring](../MONITORING.md) | [Testing](../TESTING.md) | [Troubleshooting](../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../DEPENDENCIES.md) | [Quick Start](QUICK_START_COMMANDS.md) | [Docker Deployment](DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../api/API_REFERENCE.md) | [Development](../development/README.md) | [Voice System](../voices/README.md) | [Watermarking](../WATERMARKING.md)

**Project:** [Changelog](../CHANGELOG.md) | [Roadmap](../ROADMAP.md) | [Contributing](../CONTRIBUTIONS.md) | [Beta Features](../BETA_FEATURES.md)

---

**Complete setup tutorial for integrating Kokoro TTS with OpenWebUI for seamless AI conversations with voice**

## 🎯 Overview

This guide will help you integrate the Kokoro ONNX TTS API with OpenWebUI to add high-quality text-to-speech capabilities to your AI conversations. After setup, all AI responses can be automatically converted to natural-sounding speech.

## 📋 Prerequisites

### 1. **Kokoro ONNX TTS API Running**
```bash
# Ensure Kokoro TTS is running
cd kokoro_onnx_tts_api
uv run uvicorn app:app

# Verify it's working
curl http://localhost:8354/health
```

### 2. **OpenWebUI Installed**
```bash
# If not installed, install OpenWebUI
pip install open-webui

# Or using Docker
docker run -d -p 3000:8080 ghcr.io/open-webui/open-webui:main
```

## ⚙️ OpenWebUI Configuration

### Step 1: Access OpenWebUI Settings

1. Open OpenWebUI in your browser: `http://localhost:3000`
2. Click on your profile icon (top-right)
3. Select **"Settings"**
4. Navigate to **"Audio"** section

### Step 2: Configure TTS Settings

#### **Basic Configuration**
```
TTS Engine: OpenAI
API Base URL: http://localhost:8354/v1
TTS Model: kokoro
TTS Voice: af_heart
```

#### **Advanced Configuration**
```
TTS Engine: OpenAI
API Base URL: http://YOUR_SERVER_IP:8354/v1
TTS Model: kokoro
TTS Voice: af_heart
API Key: (leave empty - not required)
```

### Step 3: Network Configuration

#### **Local Setup (Same Machine)**
```
API Base URL: http://localhost:8354/v1
```

#### **Network Setup (Different Machines)**
```bash
# Find your server IP
ip addr show | grep inet

# Use the IP in OpenWebUI
API Base URL: http://192.168.1.100:8354/v1
```

#### **Docker Network Setup**
```bash
# If both are in Docker, use container networking
API Base URL: http://kokoro-tts:8354/v1

# Or use host networking
docker run --network host ghcr.io/open-webui/open-webui:main
```

## 🎭 Voice Selection Guide

### **Recommended Voices for Different Use Cases**

#### **General AI Assistant**
- **af_heart** - Warm, expressive female voice (recommended)
- **am_adam** - Strong, confident male voice

#### **Professional/Business**
- **af_sarah** - Professional, clear female voice
- **am_liam** - Professional, authoritative male voice

#### **Friendly/Casual**
- **af_bella** - Elegant, sophisticated female voice
- **am_echo** - Clear, resonant male voice

#### **International Users**
- **bf_alice** - Refined British female voice
- **bm_daniel** - Distinguished British male voice

### **Voice Testing**
```bash
# Test different voices before choosing
curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello! I am your AI assistant. How can I help you today?", "voice": "af_heart"}' \
  --output test_voice.mp3 && mpv test_voice.mp3
```

## 🔧 Advanced Integration

### Custom Agent Configuration

#### **1. Create TTS-Optimized System Prompt**
```
You are a helpful AI assistant. When responding:
- Use natural, conversational language
- Avoid excessive technical jargon
- Keep responses concise but informative
- Use proper punctuation for natural speech flow
- Add emotional context when appropriate (excitement, concern, etc.)
```

#### **2. Response Formatting for TTS**
```
You are an AI assistant optimized for text-to-speech output:
- Use contractions naturally (don't, won't, I'll)
- Spell out numbers under 10 (one, two, three)
- Use "and" instead of "&"
- Avoid special characters and symbols
- Add pauses with commas and periods
- Use exclamation points for emphasis!
```

### RAG Configuration for TTS

#### **Document Processing**
```
When processing documents for TTS responses:
- Summarize complex information clearly
- Use bullet points sparingly
- Convert lists to natural sentences
- Explain acronyms on first use
- Use descriptive language for better audio experience
```

## 🎛️ Audio Settings Optimization

### **Quality Settings**
```
TTS Engine: OpenAI
API Base URL: http://localhost:8354/v1
TTS Model: kokoro
TTS Voice: af_heart
Speed: 1.0 (normal speed)
```

### **Performance Settings**
```bash
# For faster responses, enable caching in Kokoro
# Edit config.json (optional):
{
  "performance": {
    "cache_enabled": true,
    "preload_models": true
  }
}
```

## 🌐 Multi-Language Setup

### **Language-Specific Voices**
```
English (US): af_heart, am_adam
English (UK): bf_alice, bm_daniel
French: ff_siwis
German: ef_dora
Spanish: em_alex
Italian: if_sara, im_nicola
Japanese: jf_alpha, jm_kumo
Chinese: zf_xiaobei, zm_yunxi
```

### **Language Detection Setup**
```
# Configure OpenWebUI to auto-detect language
# and switch TTS voice accordingly
# (This requires custom scripting)
```

## 🔊 SSML Integration

### **Enhanced Audio Experience**
```bash
# Test SSML features
curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "<speak><background type=\"rain\" volume=\"20\">The weather is quite rainy today</background></speak>", "voice": "af_heart"}' \
  --output weather.mp3
```

### **Background Audio Types**
- `rain` - Gentle rain sounds
- `ocean` - Ocean waves
- `forest` - Forest ambience
- `cafe` - Coffee shop atmosphere
- `library` - Quiet library sounds

## 🛠️ Troubleshooting

### **Common Issues**

#### **"TTS not working" / No audio**
```bash
# Check if Kokoro TTS is running
curl http://localhost:8354/health

# Check OpenWebUI can reach the API
curl http://localhost:8354/v1/voices
```

#### **"Connection refused"**
```bash
# Check firewall settings
sudo ufw allow 8354

# Check if service is bound to correct interface
netstat -tlnp | grep 8354
```

#### **"Slow TTS responses"**
```bash
# Enable caching for faster responses
# First request is slower (model loading)
# Subsequent requests should be ~29ms
```

#### **"Voice not found"**
```bash
# List available voices
curl http://localhost:8354/v1/voices

# Use exact voice name from the list
```

### **Performance Optimization**

#### **Network Optimization**
```bash
# Use local network for best performance
# Avoid VPN connections for TTS
# Consider dedicated TTS server for multiple users
```

#### **Caching Optimization**
```bash
# Preload common phrases
curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello! How can I help you today?", "voice": "af_heart"}' \
  --output /dev/null
```

## 📊 Performance Metrics

### **Expected Performance**
- **First TTS Request**: ~300ms (model loading)
- **Cached Requests**: ~29ms (lightning fast!)
- **Network Latency**: +10-50ms (depending on network)
- **Audio Quality**: 24kHz, 96kbps MP3

### **Monitoring**
```bash
# Check TTS performance
curl http://localhost:8354/dashboard

# Monitor OpenWebUI logs
docker logs -f open-webui
```

## 🎯 Best Practices

### **1. Voice Consistency**
- Use the same voice throughout a conversation
- Choose voice based on your AI assistant's personality
- Test voices with your typical AI responses

### **2. Response Optimization**
- Keep AI responses conversational
- Avoid long technical explanations
- Use natural punctuation for speech flow

### **3. User Experience**
- Provide audio controls (play/pause/stop)
- Allow voice selection in user preferences
- Consider auto-play settings carefully

### **4. Performance**
- Use local network when possible
- Enable caching for frequently used phrases
- Monitor TTS response times

## 🤖 Custom Voice Assistant Agents

Custom AI agent configurations and prompt templates are available in the `kokoro/prompts/` and `docs/prompts/` directories. These templates enable you to create specialized voice assistants with different personalities and conversation styles.

### Available Prompt Templates

#### System-Level Prompts (`kokoro/prompts/system/`)
- **Learning Support Agent** - Natural conversation patterns with human-like speech
- **TTS System Optimization** - Technical guidance for speech quality enhancement
- **Prosody Enhancement** - Advanced prosodic feature optimization

#### OpenWebUI Integration (`kokoro/prompts/openwebui/`)
- **Comprehensive LLM System** - Complete TTS API integration guide
- **Voice Assistant Configurations** - Pre-configured agent personalities
- **Conversation Flow Templates** - Dialogue management patterns

#### Legacy Prompts (`docs/prompts/`)
- **SYSTEM.md** - Core learning support AI prompt
- **TTS_SYSTEM.md** - Technical TTS system guidance
- **PROSODY_ENHANCEMENT.md** - Prosodic optimization techniques
- **KOKORO_LLM_SYSTEM_PROMPT.md** - Comprehensive API usage guide

### Implementation Example

To use these prompts in OpenWebUI:

1. **Copy a prompt template** from the appropriate directory
2. **Customize the personality** and conversation style as needed
3. **Paste into OpenWebUI** under Settings → Interface → System Prompt
4. **Test the voice synthesis** with the new agent configuration

### Voice Personality Customization

The prompt templates support various voice characteristics:
- **Professional** - Clear, authoritative delivery for business contexts
- **Conversational** - Natural, friendly tone for casual interactions
- **Educational** - Patient, supportive style for learning environments
- **Technical** - Precise pronunciation for scientific/technical content

## 🔗 Related Resources

- [Voice Showcase](../VOICES.md) - Explore all available voices
- [SSML Guide](SSML-GUIDE.md) - Advanced speech synthesis
- [Quick Start](../QUICK_START_COMMANDS.md) - Basic setup
- [Docker Deployment](DOCKER-DEPLOYMENT.md) - Production setup

## 🎉 Success Checklist

- [ ] Kokoro ONNX TTS API running on port 8354
- [ ] OpenWebUI can access the TTS API
- [ ] TTS settings configured in OpenWebUI
- [ ] Voice selection tested and working
- [ ] Audio playback working in browser
- [ ] Performance is acceptable (<1 second for responses)
- [ ] Network connectivity stable

---

**🎊 Congratulations!** You now have a fully integrated AI assistant with high-quality text-to-speech capabilities. Enjoy natural conversations with your AI! 🤖🔊
