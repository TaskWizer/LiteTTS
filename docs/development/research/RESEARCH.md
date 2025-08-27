# RESEARCH

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../FEATURES.md) | [Configuration](../../CONFIGURATION.md) | [Performance](../../PERFORMANCE.md) | [Monitoring](../../MONITORING.md) | [Testing](../../TESTING.md) | [Troubleshooting](../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../DEPENDENCIES.md) | [Quick Start](../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../api/API_REFERENCE.md) | [Development](../README.md) | [Voice System](../../voices/README.md) | [Watermarking](../../WATERMARKING.md)

**Project:** [Changelog](../../CHANGELOG.md) | [Roadmap](../../ROADMAP.md) | [Contributing](../../CONTRIBUTIONS.md) | [Beta Features](../../BETA_FEATURES.md)

---
This research outlines the plan to create Light weight, Realtime (low latency) a AI Voice Assistant API wrapper for the Kokoro TTS ONNX 
optimized runtime, with out of the box support for Docker and OpenWebUI with solid user documentation. Include support for the OpenAI-Like
API schema to be easily integrated with any system with useful front-end web-application examples (with support for deploying to Cloudflare 
Workers/Pages with PWA support).

## Features:
- Super light weight TTS/STT API service under 100MB
- Add TTS (Text to Speech) and STT (Speech to Text)
- Create docker compose file and all requirements for an easy sandbox deployment
- Add speed control and other "emotion" controls
- Add phonetic controls and etc. 
- Create documentation (README.md, USAGE.md) on how to use it as well as system prompt for the AI to be able to use the controls.
- Use chunking and MP3 streaming for performance optimization
- Add documentation and support for setting up with Docker, Native, and OpenWebUI
- Balance between High Quality and Low latency
- OpenWebUI Integration out-of-the-box
- Serves an easy to use API endpoint with interactive documentation
- Kuman-like imperfections (e.g., em, huh, um, laughter, breathing, etc.)
- Dynamic prosody control (e.g., laughter tokens like <laugh>) 8.
- Advanced pronunciation for brand names, currencies, and lists 
- Advanced Linguistics and TTS, Speed Control, Homographs, Pauses, Punctuation, Custom Pronunciation, Spell Function
- Audio streaming and chunking for performance optimization
- Only pre-download two voice models (af_heart and am_puck), only download the others when selected?

## Optimization Ideas
- Pre-compile filler words like "um, huh, oh"
  - Could build a cache of common words (though this could cause issues with flow, tone, etc.)
  - Such as common words like: Hello, Hi, Welcome, Like, You know, etc.
  - Possibly cache tokens or some other method I'm not considering?
  - Optimize Python code or calls to the code, etc.
- Find the sweet spot for chunking/streaming the data

## Deep Research
- Which format provides the best balance between latency, processing overhead, and quality? MULAW, MP3, WAV, or PCM?
- Research VAPI, 11Labs, OpenAI, Rime AI, and Deepgram for a deeper understanding of the features and scope for Advanced Voice AI.
- Do deep research and planning on how to optimize the API platform (reduce latency, system resources, load time, etc.)
  - Keep in mind that this may include "tricks" that make the system "feel" faster than it actually is.

## Todo
- Download all voices
- Add multi-language support
- Voice cloning
- Voice dubbing support
  - Speaker separation Automatically detect multiple speakers, even with overlapping speech.
  - Preserve original voices and retain the speaker’s identity, timing, and emotional tone.
  - Support distinct voices for each speaker.
- Sound effects and background audio
- Music generation with instruments
- Conversational AI (including turn taking, allow interruption, start/end call, etc.)
- Group voices by category with API metadata (type:narrator/conversational/etc., gender, voice type, rating, language, etc.)
  - Note that "af_heart" means "American Female: Heart" voice, "af" for "American Male", etc.
  - Should be able to filter by each of these options through the API (for use in UI)
- Create/include front end examples (voice chat, testing tool, voice cloning, etc.)
  - Use free API endpoint or light model for Transcriber and LLM (for AI features)

## Goals
- Human-like conversational AI
- Professional quality with avanced features (balance)
- Sub 100ms latency (same machine for TTS/STT and OpenWebUI)
- Low system resource requirements (can run on a budget CPU only VPS)
- Easy to deploy with either deployment scripts or docker
- Clean and clear documentation with ease of use (such as interactive API reference)
- Small overall size footprint

## ONNX Runtime Files
- The official ONNX-Community q8f16 ONNX model (~86MB):
  https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main/onnx/model_q8f16.onnx

- These are the only voices I want (only one's that seemed "human-like"; ~4.5MB):
  https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main/voices/af_alloy.bin
  https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main/voices/af_aoede.bin
  https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main/voices/af_bella.bin
  https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main/voices/af_heart.bin
  https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main/voices/af_jessica.bin
  https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main/voices/af_nicole.bin
  https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main/voices/af_sky.bin
  https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main/voices/am_puck.bin
  https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main/voices/am_liam.bin

## Resources:
https://github.com/hexgrad/kokoro
https://mikeesto.com/posts/kokoro-82m-pi/
https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX
https://docs.openwebui.com/tutorials/text-to-speech/Kokoro-FastAPI-integration/
https://docs.rime.ai/api-reference/quickstart
https://github.com/thewh1teagle/kokoro-onnx/releases
https://elevenlabs.io/docs/capabilities/text-to-dialogue
https://github.com/thewh1teagle/kokoro-onnx/blob/main/examples/english.py