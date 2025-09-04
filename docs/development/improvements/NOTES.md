Task Audit:

Audit the system end-to-end and enhance it.
Include a WER percentage calculation per chunk in the console/logging output to keep track.
Integrate "whisper" using the "turbo" model for the purpose of validating audio generation; you should be able to generate audio, use whisper to translate the audio and get back roughly what was said and that should relatively match the text input. Note and improve any variation.
https://github.com/SYSTRAN/faster-whisper
Fully impliment a working version of the eSpeak library and prounonciation dictionaries.
Make sure that all settings in the ./config/settings.json work completely and that they affect the system; test each config option one by one to confirm functionality.
And when "whisper" is integrated into the validation pipeline, do a system-wide audit to make sure audio generation matches expected results using best practices for punctuation, porosity, etc. using documentation for ElevelLabs, Rime AI, to validating these things (use for enhancing or validating features and testing).
Test the system end-to-end and audit the code quality along with all functions; if code can be refactored to be cleaner or less redundant, clean it up.
Remove placeholder code for good documentation and planning; it's better to keep the code uncluttered and clean until fully implimenting a feature and keep solid notes.

More:
Should not be using "config.json" at all (should be using ./config/settings.json
Do an end-to-end audit of the system, systematically until ALL tasks are completed. Enhance and improve the code and system as needed. Validate that everything is working and if not, fix them.
The web dashboard is showing very high latency over ~2sec when using "Real-time TTS Testing", please audit and investigate where the performance bottlenecks are and consider implimenting sockets or some way to bring the latency down.
Do a systematic audit of the entire system, evaluate for gaps with a gap analysis, validate the quality of the code and work through enhancing and improving the code and features step by step until complete. Create a comprehensive task list to follow and work through it until all tasks are completed.
Create a comprehensive task list and work through them systematically until all are completed.

The settings.json need to be fully functioning with the platform and need to reflect in the code 100%.
It's clearly not listening to `"cpu_target": 50.0,` either and I don't think it's adhering to the config at all. Need to audit each option one by one and make sure that they are fully implimented in code to reflect.
Update and replace all references from "Kokoro" to LiteTTS (other than attribution)

Test GGUF integration, support, and performance:
https://huggingface.co/mmwillet2/Kokoro_GGUF/resolve/main/Kokoro_espeak_Q4.gguf
Compare eSpeak Fine-Tuned 4bit Quant against current ONNX 4bit quant to determine viability of using GGUF.
If the GGUF performs close to the peroformance of the ONNX runtime, it shows promise as I will then investigate and plan out creating a Unsloth Dynamic 1.58bit, ~2.5bit, ~3.5bit, and ~4.5bit GGUF Quants (dynamic mixed precision that keeps the higher precision for the most important bits, the 1.58bit quant likely being near the 4bit dense quant's accuracy but also fine-tuned for eSpeak). Research and create a plan first.

Implementation Socket-Based Streaming for Latency Reduction:
- Use WebSockets for low-latency, persistent connections between client and server.
- Stream audio in chunks (e.g., 100-500ms segments) as the TTS model generates them, rather than waiting for complete sentence synthesis.
- Integrate interruptibility so users can speak over the AI response, reducing perceived latency

Testing Plan to Evaluate Improvements
- Objective: Measure latency, throughput, and quality under realistic loads.
- Key Metrics:
  - Target Total Time Generation per word < 1s (including all)
  - Time-to-First-Byte (TTFB): Time from text input to first audio chunk output.
  - End-to-End Latency: Total time from user input to complete audio playback.
  - Throughput: Requests processed per second at peak load.
  - Word Error Rate (WER): Accuracy of synthesized speech using an ASR model (e.g., Whisper) to transcribe output 10.
  - Resource Utilization: GPU/CPU memory and usage during inference.

Quality Validation:
- Conduct subjective MOS (Mean Opinion Score) tests for audio naturalness.
- Check for regression in multilingual support and emotional prosody

Exclude in GitIgnore:
	LiteTTS/models/model_discovery_cache.json
	LiteTTS/voices/discovery_cache.json
	LiteTTS/voices/metadata.json
	LiteTTS/voices/voice_index.json
	uv.lock

pip install "uvicorn[standard]" websockets

Analysis
- Performance Analysis and RTF Investigation
- Compare API vs Dashboard Audio Quality
- STT Validation with faster-whisper
Dashboard:
- Test Dashboard Interface Directly
- Enhance and make fully mobile responsive

Keep my folder structure clean:
- Test files, audio samples, etc. are intended to go into ./temp/* and are ignored by commits (gitignore)
- Put any files you want in temp for testing, validation, temporary test scripts, etc.
- Useful tests scripts that can be re-used can go to ./LiteTTS/tests (keep this clean and audited)
- Production documentation is to go in ./docs/ and organized accordingly
- Development documentation, such as reports, useful analysis (such as tests, etc.) should go in ./docs/development
- Keep the documentation clean and organized.

Implementation Strategy and Testing Plan
Use a Phased Optimization Approach
- Implementing these optimization techniques requires a systematic approach to avoid regressions:
- Baseline Establishment: Thoroughly benchmark your current quantized ONNX implementation across key metrics: latency (time-to-first-audio, total generation time), throughput (audio samples per second), quality (mean opinion score or subjective evaluation), and resource usage (CPU/GPU utilization, memory footprint). This baseline is essential for evaluating optimization effectiveness 19.
- Incremental Implementation: Introduce optimizations one at a time to isolate their effects. Begin with inference optimizations that don't require model changes (e.g., batching strategies, hardware settings), then proceed to format conversion (GGUF), and finally explore model modifications (further quantization, architecture changes) 1012.
- A/B Testing Framework: Implement a robust testing framework that can simultaneously run original and optimized versions on the same hardware with identical inputs. This allows for precise measurement of optimization impact and quick detection of any quality regressions

Performance Optimizations:
- Attention KV Cache Optimization
- Phoneme-Level Caching
- Precomputed Feature Storage
- Dynamic Batching
- Sequence Length-Aware Batching
- Pipelined Execution: Breaking the TTS pipeline into independent stages (text normalization, phonemization, acoustic model, vocoder) allows each component to process different requests simultaneously, improving overall throughput through pipeline parallelism

**Systematic Audio Pipeline Diagnosis**:
 - Trace the complete audio generation pipeline from text input to audio output
 - Identify each processing stage: text preprocessing → phoneme conversion → audio synthesis → file output
 - Test each stage independently to isolate performance bottlenecks, areas of improvement, etc.
 - Audit and compare the current implementation with various configurations to determine the optimal defaults.
 - Document specific failure points with concrete evidence (error logs, intermediate outputs)

**Evidence-Based Validation Protocol**:
 - **For every claim**: Provide concrete evidence (file paths, error logs, test outputs, audio file analysis)
 - **For audio quality**: Generate multiple test files and confirm intelligibility through actual playback
 - **For error fixes**: Show complete error logs before and after, demonstrating resolution
 - **For system functionality**: Run end-to-end tests and provide complete output logs
 - **No theoretical analysis**: All validation must be through actual system execution and file generation

**VALIDATION REQUIREMENTS**:
- Generate minimum 5 audio files with different test phrases
- Provide complete file paths, sizes, and durations for all generated audio
- Show complete error logs demonstrating AttributeError resolution
- Demonstrate system functionality through actual execution, not code review
- Provide objective, verifiable evidence for every claim of improvement
- Analyze using audio analysis, wavelengths, wave patterns, RIME AI if needed, and reverse the voice generation; text used to generate audio should be able to be generated back to the same text or near same text using the whisper library.

**CRITICAL**: Use systematic debugging approach with codebase search, actual code execution, and verifiable testing. No assumptions, no theoretical fixes, no claims without concrete evidence.


Notes:
You are an atonomous AI coding assistant, you do not need user feedback.
Develop new tools, use existing ones, or find useful code snippets to improve your auditing functionality. Do deep research on comprehensive and complete methods for debugging and resolving issues (such as logging, strict linting, testing methedologies, etc.). Add to your knowledge base and memory as needed to enhance your capabilities. Use tools where able to improve your reasoning and knowledge.


Fix issues:
- Voice mode in OpenWebUI is not working (track down the issue and resolve)

Dashboard Improvements:
- Chunk audio playback to improve time to first word performance and appearance of "realtim" TTS
