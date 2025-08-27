I need you to conduct a comprehensive production-readiness assessment and improvement plan for the Kokoro ONNX TTS API project. This should be a systematic, multi-phase approach that transforms the current system into a production-ready TTS service.

**Phase 1: System Audit & Gap Analysis**
1. **Current State Assessment**: Perform a complete technical audit of the codebase, identifying:
   - Model loading issues: The config.json file specifies "model_q4.onnx" but the system is actually downloading and using "model_fp16.onnx". Fix the model path resolution to use the correct quantized model (model_q4.onnx) as specified in configuration
   - Configuration system integrity: Implement proper config.json → override.json hierarchy where override.json (if present) takes precedence over config.json settings
   - Feature implementation gaps: Audit text processing pipeline, voice handling system, and API endpoints against the feature specifications in ./docs/development/features/
   - Performance bottlenecks and resource utilization patterns
   - Error handling coverage and logging implementation quality
   - Documentation completeness and accuracy across all components

2. **Competitive Analysis**: Research and compare against industry TTS standards:
   - Implement example UI frontends demonstrating: voice cloning capabilities, emotion control features, and testing tools (latency measurement, quality statistics, etc.)
   - Verify all features documented in ./docs/development/features/ have been fully implemented and are functional
   - Benchmark performance metrics and audio quality against industry standards
   - Analyze API design patterns and best practices from leading TTS services
   - Review pricing models and deployment strategies from competitors

3. **Gap Analysis Report**: Provide a detailed assessment covering:
   - Critical bugs that prevent basic TTS functionality
   - Missing features compared to documented requirements and competitor offerings
   - Performance optimization opportunities with specific metrics
   - Security vulnerabilities and reliability concerns
   - Documentation gaps and user experience friction points

**Phase 2: Critical System Fixes**
1. **Model Loading Resolution**: Fix the model path resolution logic to properly load model_q4.onnx instead of model_fp16.onnx, and implement the configuration hierarchy: override.json (user overrides, if file exists) → config.json → system defaults
2. **Configuration System Validation**: Ensure all settings in config.json are properly connected to their corresponding implementations in the codebase
3. **Text Processing Pipeline**: Implement missing features for contractions, currency formatting, date parsing, and acronym expansion (note: contraction_handling is for user overrides only, not required in base configuration)
4. **Voice Management System**: Validate that all 55 documented voices are accessible, properly configured, and functional
5. **Web UI Functionality**: Ensure the dashboard loads correctly on port 8354 with full feature access and proper error handling

**Phase 3: Production Enhancements**
1. **Audio Tagging System**: Implement multi-speaker support, whisper detection capabilities, and comprehensive audio metadata management
2. **Advanced Voice Cloning**: Create a web-based voice cloning interface with step-by-step usage instructions and validation
3. **Hot Configuration Reloading**: Enable real-time monitoring and automatic reloading of config.json and override.json file changes without service restart
4. **Performance Optimization**: Implement intelligent caching strategies, connection pooling, and efficient resource management
5. **Monitoring & Observability**: Add comprehensive structured logging, performance metrics collection, and health check endpoints

**Phase 4: Testing & Validation**
1. **End-to-End Testing**: Create a comprehensive test suite covering all TTS features, edge cases, and error conditions
2. **Performance Testing**: Validate system performance under realistic load conditions with concurrent users and various text inputs
3. **Integration Testing**: Test all API endpoints, voice options, configuration combinations, and feature interactions
4. **User Acceptance Testing**: Validate dashboard functionality, user workflows, and overall system usability
5. **Test coverage**: Create complete test coverage for the API as well as all compentents and features.

**Phase 5: Production Readiness Report**
Provide a detailed final report including:
- Current system status with functionality verification results
- Performance benchmarks and optimization impact measurements
- Feature completeness assessment against requirements and competitor analysis
- Security assessment with specific vulnerability findings and mitigations
- Production deployment readiness checklist with specific criteria
- Documentation quality evaluation and completeness scoring
- Prioritized recommendations for next development phases

**Technical Implementation Guidelines:**
- Remove unnecessary backup folder creation during cleanup operations (rely on Git version control instead)
- Prioritize fixing existing broken functionality before implementing new features
- Implement comprehensive error handling with user-friendly feedback messages throughout the system
- Ensure all changes maintain backwards compatibility with existing configurations where possible
- Focus on system reliability, maintainability, and scalability for production deployment
- Use proper logging levels and structured logging for production monitoring

**Expected Deliverables:**
1. Comprehensive technical audit report with current state analysis and specific findings
2. Prioritized implementation plan with before/after functionality demonstrations
3. Production readiness assessment with quantitative metrics and pass/fail criteria
4. Complete deployment and maintenance documentation with operational procedures
5. Competitive analysis report with feature gap identification and implementation recommendations

**Success Criteria:**
- All 55 voices are functional and accessible via API
- Model loading uses correct quantized model (model_q4.onnx) as configured
- Configuration hierarchy works properly with override.json taking precedence
- Web dashboard loads and functions correctly on port 8354
- All features in ./docs/development/features/ are implemented and tested
- System can handle concurrent requests with acceptable performance
- Comprehensive error handling prevents system crashes
- Documentation is complete and accurate for all implemented features


Todo:
- Add inpreceptable Watermarking?

Kokoro Notes:
- Kokoro leverages the StyleTTS 2 architecture and ISTFTNet vocoder for natural-sounding speech generation.
- Struggles with expressive speech (e.g., laughter, anger) due to neutral training data
- Cannot clone arbitrary voices; relies on pre-trained embeddings?
- Japanese/Korean support is experimental, with unnatural intonation in some cases?
- espeak-ng may mispronounce complex words or non-English text

Future Feature Planning:
* Multimodal Input Processing:
  - Accepts both text and audio inputs (e.g., past conversation snippets) for context-aware synthesis.
  - Uses Mimi audio codec (1.1kbps compression) for efficient high-fidelity output.
* Contextual Awareness:
  - Maintains dialogue history to adjust tone, prosody, and emotional expressiveness.
  - Handles interruptions, backchannels, and speaker turns.
* Voice Flexibility:
  - Zero-shot voice cloning (via audio prompts).
  - Speaker ID tags (e.g., [0]) for multi-speaker consistency
  - Support zero-shot cloning but limit sample length (e.g., 10 sec max for lightweight needs).
* Evaluation Metrics:
  - Homograph disambiguation (e.g., "lead" vs. "lead") and pronunciation consistency tests.
  - CMOS scores show parity with human speech in non-contextual settings
  - Add watermarking (inspired by Sesame) to detect synthetic audio
* Hyper-Realistic Dialogue:
  - Multi-speaker support with [S1], [S2] tags and non-verbal cues (e.g., (laughs)).
  - Emotion/tone control via audio conditioning
* Zero-Shot Voice Cloning:
  - Clones voices from 5–30 sec audio samples.
  - Fixed seeds for voice consistency
* Non-Verbal Expressions:
  - Supports laughter, sighs, coughs, etc.

And all the issues still exist, except the URL reading one. But is also reads "somepage" aka "some page" incorrectly as "some bidge".

Only one that seems to work okay is the URL naming, and it only kind of works direct from the API itself using Curl, it does not seem to working or following the rules through the OpenWebUI. Please audit this end to end and make sure that everything is working consistantly, the endpoints are valid and routing correctly, all rules and behaviors are being followed, etc. Part of the issue may be cache but I tried different voices and different prompts/responses and was still getting the same behavior.
OpenWebUI is using the "http://192.168.1.139:8354/v1" endpoint (it handles it's own routing from there). Read documentation and do deep research as needed to fix this.

## Known Issues
- Poor punctuation
  - Reads "wasn't" as "wawsnt" but should be "wAHz-uhnt"
  - Reads "Hmm" as "hum" but should be "hm-m-m"
  - Reads "TSLA" as "TEE-SLAW" but should be "T-S-L-A"
  - Reads "acquisition" as "ek-wah-zi·shn" but should be "a·kwuh·zi·shn"
  - Reads "Elon as "alon, but should be "EE-lawn"
  - Reads "Joy" as "joie", but should be "JOY"
- Date and currency handling is poor:
  - Reads "~$568.91" as "tildy dollar five sixty eight... ninety one" but should be "five hundred sixty eight dollars and ninety one cents" or "five hundred sixty eight point ninety one dollars"
  - Reads "$5,681.52" as "Dollar five, six hundred eighty one fifty two" but should be "five thousand, six hundred eighty one dollars and fifty two cents" or "five thousand, six hundred eighty one point fifty two dollars"
  - Reads "12/18/2013" as "twelve slash eighteen slash two-thousand thirteen" but should be "December eighteenth two-thousand thirteen".
  - Reads "05/06/19" as "five slash six slash nineteen" but should read "may sixth two-thousand ninteeen"".
  - Reads "2023-05-12" as "two thousand twenty three dash zero five dash twelve" but should be "May may twelveth, two-thousand twenty three"
  - Reads "November 21, 2025" as "November twenty one, two-thousand twenty five" but should be "November twenty-first, two-thousand twenty five"
- Poor URL reading
  - Reads "https://www.google.com" as "H-T-T-P-S slash slash W-W-W google com" but should be "W-W-W dot Google dot com"
  - Reads "https://www.somesite.com/somepage" as "H-T-T-P-S slash slash W-W-W somesite com" but should be "W-W-W dot some site dot com forward slash somepage"
- Reads "His resume is long and detailed" as "His re-zoom is long and detailed" but should be "REZ-oo-mey" (in this context)


Also, launching the service from a clean instance (git clone, etc.), I see an error on the debug console:
Failed to load configuration: ModelConfig.__init__() got an unexpected keyword argument 'performance_mode'

Make sure that the config.json is being honored and all of the settings within it are working. On that note, make sure that all the expected behaviors and features are implimented.


Old Notes:
Implement Voice Caching System
Create voice_cache.json system with metadata, checksums, and cache invalidation logic

Finish: Implement Streaming TTS Endpoint
Add /v1/audio/stream endpoint with chunked audio response and incremental generation

Comprehensive Testing and Validation
Test all new functionality, ensure backward compatibility, and validate performance improvements

Performance Optimization Implementation
Implement intelligent pre-caching and comprehensive system cleanup to achieve near-instant voice chat capabilities with the current model_fp16.onnx configuration

Documentation Enhancement
Expand and enhance documentation with detailed technical specifications and optimization strategies

System-Wide Production Readiness
Perform comprehensive system cleanup, validation, and production readiness assessment

Finish: Enhance Configuration Management
Add missing configuration values (default speed, language, retry attempts, endpoints) and consolidate hardcoded values into config.json

Medium: Symbol Processing Overhaul
Comprehensive audit of _build_symbol_words_map() and other symbol processing for natural speech patterns.

Low: Enhanced Pre-Caching Strategy
Audit current 92 pre-cached phrases and add high-frequency conversational phrases for better cache performance.

FEATURE: Advanced Audio Format Support
Implement PCM, μ-law, and Opus audio format support beyond current MP3/WAV/OGG.

FEATURE: Voice Blending Implementation
Implement Kokoro's native voice blending capability with customizable weights.

FEATURE: Prosody and Emotional Control
Add dynamic prosody tokens, emotional range controls, and advanced pronunciation support.

FEATURE: Competitive Feature Parity
Research and implement features from Rime AI and ElevenLabs for competitive parity.

DOCS: Comprehensive Documentation Update
Update all README.md files, API docs, and create comprehensive system documentation.

CLEANUP: Code Consolidation
Remove redundancy, enhance organization, and improve maintainability.

VALIDATION: System-wide Testing
Perform comprehensive testing for reliability, cross-platform compatibility, and feature completeness.

Look into/Fix
2025-08-15 07:21:58,189 | INFO | app                       | ✅ Generated 0 samples in 0.33s (attempt 1)
2025-08-15 07:21:58,189 | WARNING | app                       | ⚠️ Empty audio generated on attempt 1 with text: 'But true!...'

I moved debug_kokoro_onnx, debug_voice_format, run_tests, start_server to kokoro folder.

Audit the system, validate everything and cleanup to polish out our MVP.


New List:
- [ ] Pronunciation Accuracy Audit and Enhancement
Comprehensive audit and improvement of pronunciation accuracy and phonetic processing capabilities
  - [ ] Research and Documentation Integration
    Research RIME AI techniques and integrate best practices with comprehensive documentation
  - [ ] Quality Assurance Implementation
    Create pronunciation test suite, validation metrics, and regression testing
- [ ] Implement SSML Background Noise Enhancement
  Implement <background> SSML tag functionality for ambient noise synthesis supporting predefined ambient sounds (coffee shop, office, nature, rain, wind), configurable volume levels, proper audio level balancing to maintain speech clarity, and comprehensive documentation with usage examples.
- [ ] Create Voices Showcase Page
  Generate comprehensive markdown page showcasing all 54+ available voices with consistent sample text, embedded audio samples for direct comparison, organize voices by categories/characteristics, link prominently from README.md, and ensure audio samples are optimized for web delivery.
- [ ] RTF Optimization & Code Audit
  Analyze current Real-Time Factor (RTF) performance and identify bottlenecks, conduct comprehensive code review focusing on performance optimization, optimize audio processing pipelines and memory usage, add RTF monitoring and reporting to dashboard, document performance improvements with before/after metrics.
- [ ] Update Documentation & Testing
  Update README.md with all new features, API endpoints, and configuration options. Document all new SSML tags with usage examples. Include performance benchmarks, RTF measurements, and optimization guidelines. Add troubleshooting section for common configuration issues. Implement comprehensive test suites for all new functionality and create performance regression tests.
- [~] CRITICAL: Fix TTS Synthesis Failures
  Investigate and resolve critical TTS synthesis failures causing truncated/silent output and pronunciation regressions. Blocking P0 issue.


Temp:
curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "https://www.google.com/somewebsite", "voice": "af_heart", "response_format": "mp3"}' \
  --output hello.mp3

curl -X POST "http://localhost:8354/v1/audio/speech" -H "Content-Type: application/json" -d '{"input": "Hmm... it wasn't the TSLA acquisition Elon musk made, but rather the joy of buying it on 12/18/2013 for $44,305,150,000.00 USD. His resume is long and detailed, but please resume for details. See https://www.somewebsite.com/somepage for ~$55.75/mo", "voice": "af_heart", "response_format": "mp3"}' --output audio_test.mp3

curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "Hmm... it wasn't the TSLA acquisition Elon musk made, but rather the joy of buying it on 12/18/2013 for $44,305,150,000.00 USD. His resume is long and detailed, but please resume for details. See https://www.somewebsite.com/somepage for ~$55.75/mo", "voice": "af_heart", "response_format": "mp3"}' \
  --output hard_test.mp3



I don't see any real reason to use the combined voices, it just takes space and only one voice should really be used at a time. If a combined voice is needed, or cloned voice, then individual voice files can be created and each loaded as needed. Honestly, I don't even see it as an optimization as it uses more memory, more complicated (for no reason) and just takes up extra space and it's an extra step (would be fine if it had a purpose but doesn't seem to.

So just impliment Individual Voice Loading, for:
Lower memory usage
Faster startup time
Better for dynamic voice selection
Easier maintenance

Continue the task list systematically until all are completed.

Also, can you do deep research on "Chatterbox", which is an open source TTS client (but much heaver than this one). I would like to know if this system could benifit from some of the source code. Please take a deep dive, do deep research as needed, use whatever tools you have available to you, look at the code (cloning the repo to review it is perfectly fine). Analyze it end-to-end to see if we could utilize and of the features, improve our own, and add enhancements, etc. And give me a nice little summary and plan of action.
