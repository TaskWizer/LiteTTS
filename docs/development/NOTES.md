# Kokoro ONNX TTS API

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../FEATURES.md) | [Configuration](../CONFIGURATION.md) | [Performance](../PERFORMANCE.md) | [Monitoring](../MONITORING.md) | [Testing](../TESTING.md) | [Troubleshooting](../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../DEPENDENCIES.md) | [Quick Start](../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../api/API_REFERENCE.md) | [Development](README.md) | [Voice System](../voices/README.md) | [Watermarking](../WATERMARKING.md)

**Project:** [Changelog](../CHANGELOG.md) | [Roadmap](../ROADMAP.md) | [Contributing](../CONTRIBUTIONS.md) | [Beta Features](../BETA_FEATURES.md)

---
Light weight and faster than real-time voice chat on CPU only (but GPU is supported). The API has a RTF (Real-time-factor) of 0.76 and pre-caches common words and phrases for precieved near-instant TTS generation (sub 100ms). In addition to this, it uses streaming and chunked responses for handling batched and parellel requests, making the API very scaleable.

## Message
If you can remotely appreciate how much effort has gone into this project to make it work as well and easy as it does, please consider sponering me with as little as a buck a month, or one time donation. I could could commercialize this code, I personally think it's that good but my actual goal is simple: I want to make enough money doing cool projects so that I don't have to keep a day job and I can continue to work on cool projects non-stop.

With that in mind, I am not designing this for you. I want it to be versitile, performant and customizable yes but so it's extensible for other projects that I am working on (some behind the vale and others public or open source).

# Install dependencies using UV
uv sync

# Start the server on port 8000
uv run uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Test basic functionality
curl -X POST 'http://localhost:8000/v1/audio/speech' \
  -H 'Content-Type: application/json' \
  -d '{
    "input": "Hello, this is a test of the Kokoro TTS API.",
    "voice": "af_heart",
    "response_format": "mp3",
    "speed": 1.0
  }' --output test.mp3

# Check available voices
curl http://localhost:8000/voices

# Health check
curl http://localhost:8000/health

## Docker Notes
docker run -d \
  -p 3000:8080 \
  -e OPENAI_API_KEY="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" \
  -e OPENAI_API_BASE_URL="https://openrouter.ai/api/v1" \
  -e DEFAULT_MODEL="openrouter/auto" \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main

Has to be actual IP address:
http://192.168.1.139:8000/v1

And not:
http://127.0.0.1:8000/v1 or
http://localhost:8000/v1

## Todo
Create marketting docs:
- X times faster than FastAPI
- X Times faster than Kokoro JS
- Output quality comparision
- Add graphics, charts, etc.
- TTS/STT Stats

Needs TLS, TTS v2, and Security.
- Backup first & test
- Deployment & backup scripts
- Docker setup/images/configs

Project:
- Code: 0.8mb
- Samples: 3.2mb
- Model: 86.0mb
- Voices: 28.2mb
- uv env: 231mb
- Total: 349.2mb

## OpenWebUI Integration Enhancements
- Audio pause button
- Highlight the text being read while the AI reads aloud
- TTS Streaming (send the output to the TTS in a stream to get "real-time" audio)
  - E.g. OpenWebUI the Settings --> General  --> "Advanced Parameters" --> "Stream Chat Response" is explicitly set to "On"
- Area to change advanced TTS configuration (and/or expand options)
- Ability to highlight sets of words (selection) and read aloud.
- Fix the localhost not routing to the internal IP address issue.

## Examples
- Create front end app for adding voices, including voice cloning and testing (validate and upload)
- Create a front end testing suite for audio options, configuration, "emotion", etc.
- Create a simple interactive voice chat app (with interupt, realtime audio, BYOK, etc.)
- Create a simple tool to generate samples for all selected voices using your own prompt (select language by default but can enable all, default to english)

Support models on "https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX"
Model Performance Audit:
    "available_variants": [
      "model.onnx",                 ~3 sec.
      "model_fp16.onnx",            ~2.5 sec.
      "model_q4.onnx",              ~3.5 sec.
      "model_q4f16.onnx",           ~3 sec.
      "model_q8f16.onnx",           ~7 sec.
      "model_quantized.onnx",       ~8 sec.
      "model_uint8.onnx",           ~3 sec. (maybe 2.5)
      "model_uint8f16.onnx"         ~3.5 sec.
    ],

### 🚀 Performance Achievements
⚡ Near-Instant Response: 2-6ms cache hit latency
🎯 Excellent RTF: 0.17-0.29 Real-Time Factor (3-6x faster than real-time)
🧠 Intelligent Pre-Caching: 92 common phrases automatically warmed
📊 Real-Time Monitoring: Comprehensive performance metrics
🌍 54+ Voices: Multi-language support with dynamic discovery

### 📊 Current Performance Metrics
* Cache Hit Latency: 2-6ms (near-instant)
* RTF Performance: 0.17-0.29 (excellent)
* Memory Usage: ~60MB (efficient)
* Voice Count: 54+ (comprehensive)
* Cache Warming: 92 phrases (intelligent)
* Success Rate: 100% (reliable)

The var[0] refers to the region:
A 🇺🇸 American English: 11F 9M
B 🇬🇧 British English: 4F 4M
J 🇯🇵 Japanese: 4F 1M
Z 🇨🇳 Mandarin Chinese: 4F 4M
S 🇪🇸 Spanish: 1F 2M
F 🇫🇷 French: 1F
H 🇮🇳 Hindi: 2F 2M
I 🇮🇹 Italian: 1F 1M
P 🇧🇷 Brazilian Portuguese:

## TODO
- The TTS made "Thinking, or" sound like "Thinking Gir" and "hi, that's'" into "hit that", "I'll" says "I and hashtag 27" (fix this for ALL cases smartly)
- Questions were said as statements "Need help coming up with something?" (should sound like an actual question)
- No excitement or tone change for "!" exclimations either.
- Cleanup the folder and files (get rid of temp files, move tests scripts to ./docs/tests, rename run.py --> /docs/tests/run_evals.py, etc.)
- Cleanup all test files, sample audio file generations, documentation, and etc. (only files in root should be README.md and LICENSE, the )
- Depreciate old documentation related to testing, summary, etc. (you made a mess of the root, etc.)
- Build out all planned features in the ./docs/features folder and work through them systematicly.
- Also, create full test coverage for the API and resolve all errors, warnings and etc. for the system (but organize files better)
- Add Voice blending with customizable weights (blend two voices together) which is supported by Kokoro
- Do a system wide cleanup and validation when completed with the enhancements.
- Add "ok", "okay", "let's see", etc. to pre-compiled words (if not already)
- Log stats (token usage, latency, time to first token, etc.)
- Continue tasks systematically until all are completed
- Cleanup and get polished (with clean end-user docs)


http://15.204.226.76:8880/v1

Correction:
  - Reads "TSLA" as "TEE-SLAW" but should instead spelt out like "T-S-L-A" for more compatability.

- More Wrong:
  - Says "Religions" as "really-gram-ions"
  - Says "Existentialism" as "Exi-stential-ism"
  - "The meaning of life" as "meters inches grams" of life (look into this deeper, seems like a weird bug, maybe bad code or logic)
  - Italicized quote symbols (eg. ") says "an quat"
  - Joy as "jyi"
  - "Carl Sagan" as "Carl Sagan" but should be "Carl S-A-gan"
  - "She'd" as "shed" instead of "Shee-d"
  - A chunk of audio was completely skipped (needs to be fixed and refined)

2025-08-15 23:30:51,472 | INFO | app                       | 🔍 Origin: not set
2025-08-15 23:30:51,472 | INFO | app                       | 🎵 TTS request: '“The Moon isn’t out there. It’s inside us. Always ...' voice='af_heart' format='mp3'
2025-08-15 23:30:51,473 | INFO | app                       | 🎵 Generating speech: '“The Moon isn’t out there. It’s inside us. Always ...' with voice 'af_heart'
2025-08-15 23:30:51,479 | WARNING | phonemizer                | words count mismatch on 200.0% of the lines (2/1)
2025-08-15 23:30:53,359 | INFO | app                       | ✅ Generated 0 samples in 1.88s (attempt 1)
2025-08-15 23:30:53,360 | WARNING | app                       | ⚠️ Empty audio generated on attempt 1 with text: 'The Moon isnt out there. Its inside us. Always has...'
2025-08-15 23:30:53,464 | WARNING | phonemizer                | words count mismatch on 200.0% of the lines (2/1)
2025-08-15 23:30:55,292 | INFO | app                       | ✅ Generated 0 samples in 1.83s (attempt 2)
2025-08-15 23:30:55,292 | WARNING | app                       | ⚠️ Empty audio generated on attempt 2 with text: '“The Moon isn’t out there. It’s inside us. Always ...'
2025-08-15 23:30:55,408 | WARNING | phonemizer                | words count mismatch on 200.0% of the lines (2/1)
2025-08-15 23:30:57,823 | INFO | app                       | ✅ Generated 0 samples in 2.43s (attempt 3)
2025-08-15 23:30:57,823 | WARNING | app                       | ⚠️ Empty audio generated on attempt 3 with text: 'The Moon isnt out there. Its inches side us. Alway...'
2025-08-15 23:30:57,823 | ERROR | app                       | ❌ Failed to generate audio after 3 attempts
2025-08-15 23:30:57,823 | ERROR | app                       | 📋 Input text: '“The Moon isn’t out there. It’s inside us. Always has been.”  From that day on, the village built a temple to the Moon, but Lila never spoke of the locket.'
2025-08-15 23:30:57,823 | ERROR | app                       | 📋 Processed text: 'The Moon isnt out there. Its inside us. Always has been. From that day on, the village built a temple to the Moon, but Lila never spoke of the locket.'
2025-08-15 23:30:57,823 | ERROR | app                       | 📋 Voice: af_heart, Speed: 1.0
2025-08-15 23:30:57,824 | ERROR | app                       | 📋 Preprocessing changes: ["Removed quote characters to prevent 'in quat' pronunciation"]
2025-08-15 23:30:57,824 | ERROR | app                       | Generation failed: Generated audio is empty after 3 attempts
2025-08-15 23:30:57,825 | ERROR | app                       | Full traceback: Traceback (most recent call last):
  File "/home/mkinney/Repos/kokoro_onyx_tts_api/app.py", line 574, in _generate_speech_internal
    raise ValueError(f"Generated audio is empty after {max_retries} attempts")
ValueError: Generated audio is empty after 3 attempts

2025-08-15 23:30:57,825 | INFO | app                       | 📤 POST /v1/audio/speech - Status: 500 - Time: 6.353s
2025-08-15 23:30:57,881 | INFO | app                       | 📥 POST /v1/audio/speech - Client: 172.17.0.2
2025-08-15 23:30:57,881 | INFO | app                       | 🔍 Content-Type: application/json
2025-08-15 23:30:57,881 | INFO | app                       | 🔍 User-Agent: Python/3.11 aiohttp/3.12.15
2025-08-15 23:30:57,881 | INFO | app                       | 🔍 Origin: not set
2025-08-15 23:30:57,882 | INFO | app                       | 🎵 TTS request: 'She simply smiled, knowing the truth: the Moon is ...' voice='af_heart' format='mp3'
2025-08-15 23:30:57,882 | INFO | app                       | 🎵 Generating speech: 'She simply smiled, knowing the truth: the Moon is ...' with voice 'af_heart'
2025-08-15 23:30:57,887 | WARNING | phonemizer                | words count mismatch on 100.0% of the lines (1/1)
2025-08-15 23:30:58,844 | INFO | app                       | ✅ Generated 104448 samples in 0.96s (attempt 1)
2025-08-15 23:30:58,844 | INFO | app                       | 🎵 Audio duration: 4.35s, RTF: 0.22
2025-08-15 23:30:58,871 | INFO | app                       | 💾 Audio cached for future requests
2025-08-15 23:30:58,871 | INFO | app                       | ⚡ Performance: 4.35s audio in 0.96s (RTF: 0.22)
2025-08-15 23:30:58,871 | INFO | app                       | 📤 POST /v1/audio/speech - Status: 200 - Time: 0.990s
2025-08-15 23:30:58,949 | INFO | app                       | 📥 POST /v1/audio/speech - Client: 172.17.0.2
2025-08-15 23:30:58,949 | INFO | app                       | 🔍 Content-Type: application/json
2025-08-15 23:30:58,949 | INFO | app                       | 🔍 User-Agent: Python/3.11 aiohttp/3.12.15
2025-08-15 23:30:58,949 | INFO | app                       | 🔍 Origin: not set
2025-08-15 23:30:58,950 | INFO | app                       | 🎵 TTS request: 'It is a reflection of the soul. Moral: Sometimes, ...' voice='af_heart' format='mp3'
2025-08-15 23:30:58,950 | INFO | app                       | 🎵 Generating speech: 'It is a reflection of the soul. Moral: Sometimes, ...' with voice 'af_heart'
2025-08-15 23:30:58,956 | WARNING | phonemizer                | words count mismatch on 300.0% of the lines (3/1)
2025-08-15 23:31:00,814 | INFO | app                       | ✅ Generated 216064 samples in 1.86s (attempt 1)
2025-08-15 23:31:00,814 | INFO | app                       | 🎵 Audio duration: 9.00s, RTF: 0.21
2025-08-15 23:31:00,876 | INFO | app                       | 💾 Audio cached for future requests
2025-08-15 23:31:00,876 | INFO | app                       | ⚡ Performance: 9.00s audio in 1.86s (RTF: 0.21)
2025-08-15 23:31:00,876 | INFO | app                       | 📤 POST /v1/audio/speech - Status: 200 - Time: 1.928s
2025-08-15 23:32:39,652 | INFO | app                       | 📥 POST /v1/audio/speech - Client: 172.17.0.2
2025-08-15 23:32:39,653 | INFO | app                       | 🔍 Content-Type: application/json
2025-08-15 23:32:39,653 | INFO | app                       | 🔍 User-Agent: Python/3.11 aiohttp/3.12.15
2025-08-15 23:32:39,653 | INFO | app                       | 🔍 Origin: not set
2025-08-15 23:32:39,654 | INFO | app                       | 🎵 TTS request: '“The Moon isn’t out there. It’s inside us. Always ...' voice='af_heart' format='mp3'
2025-08-15 23:32:39,655 | INFO | app                       | 🎵 Generating speech: '“The Moon isn’t out there. It’s inside us. Always ...' with voice 'af_heart'
2025-08-15 23:32:39,669 | WARNING | phonemizer                | words count mismatch on 200.0% of the lines (2/1)
2025-08-15 23:32:41,445 | INFO | app                       | ✅ Generated 0 samples in 1.79s (attempt 1)
2025-08-15 23:32:41,446 | WARNING | app                       | ⚠️ Empty audio generated on attempt 1 with text: 'The Moon isnt out there. Its inside us. Always has...'
2025-08-15 23:32:41,550 | WARNING | phonemizer                | words count mismatch on 200.0% of the lines (2/1)
2025-08-15 23:32:43,339 | INFO | app                       | ✅ Generated 0 samples in 1.79s (attempt 2)
2025-08-15 23:32:43,339 | WARNING | app                       | ⚠️ Empty audio generated on attempt 2 with text: '“The Moon isn’t out there. It’s inside us. Always ...'
2025-08-15 23:32:43,451 | WARNING | phonemizer                | words count mismatch on 200.0% of the lines (2/1)
2025-08-15 23:32:45,747 | INFO | app                       | ✅ Generated 0 samples in 2.31s (attempt 3)
2025-08-15 23:32:45,747 | WARNING | app                       | ⚠️ Empty audio generated on attempt 3 with text: 'The Moon isnt out there. Its inches side us. Alway...'
2025-08-15 23:32:45,747 | ERROR | app                       | ❌ Failed to generate audio after 3 attempts
2025-08-15 23:32:45,748 | ERROR | app                       | 📋 Input text: '“The Moon isn’t out there. It’s inside us. Always has been.”  From that day on, the village built a temple to the Moon, but Lila never spoke of the locket.'
2025-08-15 23:32:45,748 | ERROR | app                       | 📋 Processed text: 'The Moon isnt out there. Its inside us. Always has been. From that day on, the village built a temple to the Moon, but Lila never spoke of the locket.'
2025-08-15 23:32:45,748 | ERROR | app                       | 📋 Voice: af_heart, Speed: 1.0
2025-08-15 23:32:45,748 | ERROR | app                       | 📋 Preprocessing changes: ["Removed quote characters to prevent 'in quat' pronunciation"]
2025-08-15 23:32:45,748 | ERROR | app                       | Generation failed: Generated audio is empty after 3 attempts
2025-08-15 23:32:45,748 | ERROR | app                       | Full traceback: Traceback (most recent call last):
  File "/home/mkinney/Repos/kokoro_onyx_tts_api/app.py", line 574, in _generate_speech_internal
    raise ValueError(f"Generated audio is empty after {max_retries} attempts")
ValueError: Generated audio is empty after 3 attempts



These all still seem to be issues, dispite you saying they were completed and that the system was updated, dispite after several audits. Please audit (for real) and improve:
Audit the linquistics system and improve the human-like nuanceses, punctuation, tone, emotional range, etc.

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
  - Reads "https://www.google.com" as "H-T-T-P-S slash slash W-W-W google com" but should be "W-W-W Google dot com"
  - Reads "https://www.somesite.com/somepage" as "H-T-T-P-S slash slash W-W-W somesite com" but should be "W-W-W some site dot com forward slash somepage"
- Reads "His resume is long and detailed" as "His re-zoom is long and detailed" but should be "REZ-oo-mey" (in this context)

Do a full audit as well as Deep Research to find any other areas of improvement and voice enhancements.

Create a plan of action, build a task list and systematically work through them until all tasks are completed.

More:
- Use quiet voice (aka. blend with af_nicole) for messages is brackets e.g. (Imagine...)

- TSLA (stock) as Tee-slaw, should be Tesla
- Elon as alon, should be "EE-luwn"
- Aquasition is said like "equisition" (should be ak-wa-zition)
- "$XXX" as "dollar" amount (should be XXX dollars). Sometimes says tildy "~", should be "about"
- If reading a number with a decimal point, needs to say "point"
- Still getting "hash x27" sometimes (not always))
- When reading a url, don't say "https://" (H-T-T-P slash slash) should just say the {domain name} "dot com" forward slash {name}
- Questions (?) and exclamations (!) still don't sound any different.
- "Real (pause) Estate" should be read as one word "Real-e-state"

## Next:
Still issues:
I'll --> ill (not right)
"you'll" --> yaw-wl
I'd --> "I-D"
Still says astrisk (but I think it's reading markdown format because I don't see it, seems to be before brackets "(").
Quotes still as "in quat"
"am in x 27"
"resume" as "re-zoom" and not "re-sum-ey"
Use quiet voice (aka. blend with af_nicole) for messages is brackets e.g. (Imagine...)
Dates with dashes are read wrong 2023-10-27 as 2023 dash 10 dash 27 should be October, 27, 2023.
ASAP as "a (pause), sap." and should be either "A-S-A-P" or "As soon as possible" (config to read out abreviations)
Need to dynamically determine emotion to be used based on punctuation and look ahead. Question (?), Exclamation (!), emphasis (italicized), etc. This can be handled by a LLM with instructions on how to use the API, but the system should work well out of the box as well.

## Code Audit
- Path("kokoro/voices") is hard coded in many places, fix this.
- Linting warnings:
    - """The method "on_event" in class "FastAPI" is deprecated
      on_event is deprecated, use lifespan event handlers instead.

    Read more about it in the
    [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).Pylance
    (method) def on_event(event_type: str) -> ((DecoratedCallable@on_event) -> DecoratedCallable@on_event)
    Add an event handler for the application.

    on_event is deprecated, use lifespan event handlers instead.

    Read more about it in the FastAPI docs for Lifespan Events."""
    - """The method "dict" in class "BaseModel" is deprecated
      The `dict` method is deprecated; use `model_dump` instead.Pylance
    (method) def dict(
        *,
        include: IncEx | None = None,
        exclude: IncEx | None = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False
    ) -> Dict[str, Any]"""
These should not be in the code, move them to a config that gets dynamically loaded (and expand on them):
    number_words = {
        '0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four',
        '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine'
    }
    contractions = {
        "don't": "do not", "won't": "will not", "can't": "cannot",
        "n't": " not", "'re": " are", "'ve": " have", "'ll": " will",
        "'d": " would", "'m": " am", "'s": " is"
    }

## Next
- Critical: The system is currently not working, it's returning a single silable or nothing at all.
- Audit the logs and extract the first words from the AI's response to append to "Intelligent Pre-Caching"
- Do deep research, analysis, and audit of the code base. Create a plan to enhance or improve the code, tests, consistancy, etc. as needed.
- After you are done with the tasks, please give me a summary and stats (such as latency, RTF, etc.)
- Varify complete code coverage for the API system
- Audit the following features to confirm they are fully working:
  - human-like nuances and emotional range
  - Dynamic prosody control (e.g., laughter tokens like <laugh>)
  - Advanced pronunciation for brand names, currencies, and list
  - Improve/reduce word Error Rate (WER) at least primarily for english
  - Add supports MP3, FLAC, WAV, PCM, μ-law, and Opus
- Please test and enhance the docker deployment (I can test it with OpenWebUI running locally)
- I would expect for the URL http://localhost:8000/examples to work, but it gives a debug console error: 📤 GET /v1/examples - Status: 404 - Time: 0.000s
- Run a benchmark and give me the results for all models, american voices, etc. that I can review.

## Next
- Critical: The system is currently not working, it's returning a single silable or nothing at all.
- Make sure to detect changes to the config (voices, models, etc.) and re-load them.
- "thinking, or" is prounounced by the TTS system as "thinkinger" please fix.
- "joy" was prounonced "ju-ie"
- "I'm" is being prounonced "im" instead of "I-m
- "hmm" is prounonced "hum" (wrong)


## One-command:
git clone https://github.com/TaskWizer/LiteTTS.git litetts-test && cd litetts-test && uv run uvicorn app:app
git clone https://github.com/TaskWizer/LiteTTS.git && cd LiteTTS && uv run uvicorn app:app
uv add git+https://github.com/TaskWizer/LiteTTS.git

## VPS Notes:
git clone https://github.com/TaskWizer/LiteTTS.git
python -m venv venv
source venv/bin/activate

http://15.204.226.76:8880/v1

I installed this project on a VPS and I was hoping for better performance. Initially at fp16 I was getting ~2 RTF, so I had to change to q4 (4bit) quantization and now it gets between 0.81 and 1.2, averaging about 0.9. It's better but I was hoping I could make it do better. Can you audit and analyze the current code base to see if there are any ideas on how to optimize futher?

## Performance Optimizations:
- Worked on Spec'ed out performance optimizations
- Can you build into the system a quick system check on startup and optimize the configuration for best performance given the system constraints (or features, like GPU, etc.)?



## Future Scope
- Create sample audio files (for README.md, <1mb total, etc.)
- Restructure to work with `uv add git+{url}` using setup.py, etc. (kind of works but unclear on how to use it)
- Eventually publish pip package to PyPi registry and maintain automatically
- Generic: Continue tasks systematically until all are completed (auto-enhance prompt with context engine for specifics)
- Do deep research to find the best code to document generator and impliment it in the system to generate useful document reference.
- After you are done with the tasks, please give me a summary and stats (such as latency, RTF, etc.)
- Add more phrases to common starting words to the "Intelligent Pre-Caching" process.
- Do deep research and analysis of the code base.
- Get rid of bash scripts and get this system cross platform (Windows, Linux, and Mac) utilizing Python/UV
- Generate samples (against a single prompt) for all voices on build/first run?
- Specifically benchmark latency, RTF, time to first word, etc. of all ONNX models
- Compile info graphics, charts, diagrams and etc.
- Use strict linting, varification, and validation.
- Plan out best way to add multi-language support.
- Research advanced RIME AI, ElevenLabs, and VAPI features (etc.)
- Make deployment compatibile with `uv add git+{URL}` and PyPi with Setup.py, etc.
- Audit and manually clean up docs

## Validate:
- Add/improve human-like nuances and emotional range
- Dynamic prosody control (e.g., laughter tokens like <laugh>)
- Advanced pronunciation for brand names, currencies, and list
- Improve/reduce word Error Rate (WER) at least primarily for english
- Add supports PCM, μ-law, and Opus

## Testing:
- Lets test the streaming endpoint, docker deployment, then on VPS, etc.
- Future testing: how well does it work on GPU, or at all?
- Compare kokoro-v1.0.int8.onnx, kokoro-v1.0.onnx, and model_q8f16.onnx, etc. (aka. Benchmarks)
- Add HMR (for models and voices), fault tolerance, and resiliance into the system.
- Test/validate deployments (clean from scratch) with various method (docker, uv, python, etc.) for cross-platform (Windows, Linux, and Mac)
- Do different voices differ wildly in performance?
- Lets test the streaming endpoint, docker deployment, then on VPS, etc.
- Future testing: how well does it work on GPU, or at all?
- Compare kokoro-v1.0.int8.onnx, kokoro-v1.0.onnx, and model_q8f16.onnx
- Audit and improve http://192.168.1.139:8000/v1/audio/stream endpoints
- WAV format faster? Do testing

## Q & A:
- Should I use model name "tts-1" to be the same as OpenAI?
- Should the system do a systems hardware check for optimized config (CPU, GPU, RAM, HDD, I/O, etc)
- And then do a benchmark against all models to get the best configuration for the system (then this could be sent back to an API endpoint or something to improve the system over time; e.g. keep track of what settings are best for what hardware).
- Once published and open sourced, send to Cole Medin, Bijan Bowen, Sam Witteveen, ThePrimeTime, and ...
- Add support for GPU and test.
- How to improve performance for multiple instances
- Automatically translate input text to another language using LLM or service when creating "more accurate" samples?

## Done (varify/test):
- Look at ./kokoro/openapi.json for details on the API spec gotten from Kokoro TTS API (FastAPI)
- Didn't read 3,000 correctly, said "three" "zero" "zero" "zero" .
- Says the emoji's (sparkles). Don't read these by default (set in config)
- Says "here's" as "here and has 27", which is wrong.
- I feel like this is part of a larger issue and the system needs to be audited and improved for this type of issue across the board.
- There are several places where the static string "af_heart" is set. Only set this as a variable once (from config) and then set it.
- Fix: Still using "in quat" (but not always, less common but happens). Boy as "boi"?
- "Okay" being prounounced as "Awk-key". "Boy" prounonced fine but "boy" as "bow" (so lower case being the issue?).
- Resolve a critical issue where the TTS is not working, it either responds with a single silable or nothing at all.

## Notes
- Probably best not to use a Thinking model (or turn thinking off) for conversational AI

## Curl Samples
curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, world!", "voice": "af_heart", "response_format": "mp3"}' \
  --output hello.mp3

curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "Welcome to our comprehensive technology demonstration session. Today we will explore advanced parallel processing systems thoroughly. These systems utilize multiple computational instances simultaneously for efficiency. Each instance processes different segments concurrently without interference. The coordination between instances ensures seamless output delivery consistently. Modern algorithms optimize resource utilization effectively across all components. Performance improvements are measurable and significant in real scenarios. Quality assurance validates each processing stage thoroughly before deployment. Integration testing confirms system reliability consistently under various conditions. User experience remains smooth throughout operation regardless of complexity. Advanced monitoring tracks system performance metrics continuously during execution.", "voice": "af_heart", "response_format": "mp3"}' \
  --output hello.mp3

## Reference:
https://github.com/SYSTRAN/faster-whisper
https://github.com/nazdridoy/kokoro-tts
https://github.com/remsky/Kokoro-FastAPI?tab=readme-ov-file
https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/tree/main/voices
https://discuss.pytorch.org/t/does-onnx-increase-inference-efficiency-compared-to-pytorch-model/194980
https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX-timestamped
https://github.com/lucasjinreal/Kokoros


DONE (audit)!
Next:
I don't want the default to be expanding contractions. It should be an option in the config, but NOT default behavior. So it's good to have, but the AI should just by default to saying the punctuation correctly. So create punctuation rules for given words to be explicit, etc. Extend the config.json as needed.

Next (here):
The "pronunciation_rules" should be handled automatically and dynamically by the system. Don't include this in the config please unless more of an "override", same for "acronym_handling" as this should be global and not specific like this.

Also, in the config, the "audio", "performance", and "cache" are a bit dense, please split these out into logical groups.

Overall pretty good though, I would like the user to have control over everything but also a solid out-of-the-box experience for those who do not want to dig deeper or configure everything.

On that note, create a light weight test on start up the app to check system resources (CPU, GPU, RAM, HDD, etc.) to optimize the config on first-run, then cache it. Use the system id (name, mac address, etc.) or create a file flag to know not to re-run tests.

Next:
Expand the "text_processing" in the config.json and fully impliment the beta "Time-stretching optimization" feature in ./docs/TIME-STRETCHING-OPTIMIZATION.md for testing.

Next:
Cleanup and Polishing for Production:
Do a full systems audit of the structure and lets cleanup the repository for production readiness:

Clean up docs, consolidate as needed, consolidate analysis and summaries and remove irrelivant ones.
The "tests" folder in the root should be merged with ./kokoro/tests, cleaned up and references updated (in code, etc.)
Code should not be in docs, move them to where they make more sense and update references.
Only keep what documents are needed for the system moving forward (but keep NOTES.md, it's my raw notes).

Move ./docs/voices to ./samples and remove the "sample" from their names.
Move and cleanup all "benchmarks" code and put in ./kokoro/benchmarks and update references (and extend them with clear names)
Move json files in ./kokoro to ./kokoro/config and update references
Move all test related scripts to ./kokoro/tests and update references (including debug, etc.)
Audit and cleanup the .gitignore file, I like the notes and sections, but it's not sorted or clean (several things don't apply to this repo) please cleanup.

Create a ./docs/usage to house tutorials, guides, specific usage documentation, etc. (including quick start guides)
Create a ./docs/FEATURES.md file that contains a list of current features, planned features, etc.
Put a README.md in every root directory that summarizes it and links to all docs in the given folder tree, with descriptions, etc.
Link these documents in the ./README.md with a short description of each category (not individual files as they can link to the README.md in each) and a simplified overview of features in the README, simple getting started info (most common setup method and simple usage) with link to more detailed or specific instructions, etc.
Add a CONTRIBUTIONS.md file, update CHANGELOG.md, etc.
The main README should include a title, project sumary and overview, navigation/links with descriptions, some performance graphics, simple compact flow charts, and make adjustments as needed (to be more accurate to the default setup). Move structure to it's own document, voice samples, api info, etc. The ./README.md should be more of a marketting doc and overview for the average user, but allows someone if they want to dig deeper. Keep it clean with the ability to be VERY comprehensive by clicking on the area or document of interest.
Create a LICENSE file in the root of the repo with a copy of the MIT License verbage.

Create a comprehensive document/tutorial for setting up OpenWebUI with this API. It should include the audio settings (both general and admin) with the correct settings, voice, IP address, etc.
- It should also include how to setup a custom agent in OpenWebUI with the included custom LLM prompts, for the system prompt as well as knowledge/RAG for the "agent" for best results.
- I will audit this and improve it with the specific steps, but I would apprecaite you setting it up, building it out and boilerplating it for me (with best judgement)
- Do research as needed, and do your best!

Enhance the examples and dashboard.

Also, improve the documentaton, including technical docs. Read through the following feature documentation:
./docs/features/TECHNICAL-DOCUMENTATION-GENERATION.md

And impliment a comprehensive solution to generate documentation cleanly automatically.
Update code as needed to work well with the solution and keep a clean and easy to follow structure.


Next:
Audit the complete system, do deep research, and do a comprehensive gap anaysis as well as a full analysis of the current state of the system by all metrics.
Give me a detailed report of where we are sitting and how "production-ready" we are to distribute (include any testing/validation we need to do, etc.).
Make it clear that "contraction_handling" is for overwrides and does not need to be set; only setup an example in the config.json
There is no need during clean to create *_backup folders, etc. becasue everything has history saved to versioning (github).

Next:
Audit:
Looking at the "pronunciation_rules"" set in the config.json, there's a simple rule of just remove the Apostrophe.
So for example, this is wrong `"I'll": "eye-will",` and should be "eye-ll"; "eye-will" would be more like expanding a contraction (not correct).
So most are correct except for the ones that start with "I'" (but you do this correctly for "it's'"?) and this can be handled dynamically instead of one-by-one or explicitly.
So the only case that it might make sense to modify the spelling at all (other than removing the apostrophe) would be `"they're": "thair",` but I feel like theyre would probably also work, but would need to be varified. Please handle this cleaner.

Next:
Move the README sections for "Troubleshooting", "Performance Benchmarks", etc. to their own doc.
Also, you did not add the navigation to the docs in the readme with discription like I asked. Lets do that and reduce the README file to about a hundred lines or so, just what's needs and allow the user to dig deeper if they so choose.

Add at the top a note in bold and eye-catching for details on the TTS can be used free of charge but if the user appreciates the work that has gone into it, consider sponsering me (recurring donation) or gving a one-time donation. My goal is simple, make enough money working on cool projects so I don't have to work a 9to5.

Next:
Looks good so I will be testing. But I don't actually see any code changes, so can you audit everything and make sure it's working as intended by default?
Things generally done by the core/default system should NOT need to be handled in the config.json, UNLESS the user wishes to "OVERIDE" the default behavor.
So re-work the "contraction_handling" settings in the config.json beause the logic is wrong. What I expect: Handle this dynamically in code globally, and allow the user to modify the default behavior with the config.json.

I audited the README, and honestly it's great.
Please adjust the name "🎵 Kokoro TTS API - Production-Grade Voice Synthesis" to just "Kokoro ONNX TTS API" and update this everywhere as it is more specifically the ONNX optimized version of Kokoro TSS, and an API.
One other change for the "Quick Start". You are mixing Python and UV, so lets just assume UV as the default, and this is all you need to do:
```shell
    # Clone the repository
    git clone https://github.com/TaskWizer/LiteTTS.git
    cd LiteTTS

    # Run the API server (takes care of everything)
    uv run uvicorn app:app
```
This is effectively the equivilant of running `uv run uvicorn app:app --host 0.0.0.0 --port 8354 --workers 1` (the default config).
By default, port 8354 (represents "TTS" in English Gematria) is used but this is merely an arbitrary, unused, port.
Alternatively, you can use the "reload" flag emulates "HMR" to detect detects changes and can make the system more resliant but uses a little more overhead. Please see additional documentation.

Next:
Audit and test the system end to end, including gap analysis, checking that everything operates 100% with optimal performance, documentation is solid and looks good, etc.
Make sure that all features have been fully implimented, everything has been cleaned up and organized,
Then, with the comprehensive audit, use deep research, and provide feedback/analysis of the current state of the system by all metrics.

README enhancements:
Add to README Acknowledgments (and review it for useful insights):
- https://github.com/yl4579/StyleTTS
Add a tidbit on the meaning of Kokoro:
"Kokoro" (心) is a Japanese word that encompasses a rich and complex meaning, often translated as "heart," but extending to include "mind," "spirit," "feeling," and even "essence" or "core". It's not just a physical organ or a simple emotion, but rather the seat of consciousness, thoughts, feelings, and will.
Verbage change "An optimized model for your system is automatically downloaded on first run."


General:
Continue the task list systematically until all are completed.

Next:
Remove all of the excess documentation and files that are no longer needed (only need one config file, no audits, etc.)
Consolidate any useful information from the files and code being removed, into the core documents in a clean way.
"CONTRIBUTIONS.md" should be in ./docs/ and notes, assessments, summaries, etc. removed.
Make the gitignore file look "pretty": alphabetize by category, then by filename and/or type and make it look nicer.
Make sure to update the "Kokoro TTS API" name everywhere to "Kokoro ONNX TTS API"

And address the remaining gaps:
## Critical Issues - 🟡 MINOR
* Voice System Import: Minor import issue with dynamic_voice_manager (non-critical)
* Missing Documentation: 5 documentation files referenced but missing
## Minor Improvements Needed
* Documentation Completion: Create 5 missing documentation files
* Voice System Import: Fix minor import issue (non-critical)

./templates is pointless and a placeholder "dashboard.html" is useless, remove it.
On that note, please improve, make working, and finalize all the examples.
Move ./scipts to ./LiteTTS/scripts and update all references (links, code, notes, docs, etc.).
Enhance "benchmarks" and remove any such scripts to ./LiteTTS/benchmarks
The "debug_*.py" files should be moved to ./LiteTTS/tests and references updated.
If there's a "benchmark" script in the ./LiteTTS root, it should be `run_all_benchmarks.py` and runs them all.
Do a last run clean sweep audit and make sure everything is clean and consistant.
Remove any redundant or no longer used scripts.

Next:
Where are the prompts (library for LLM's to use)?
- Maybe refine and recover these from a prior commit/push.
Add to the README file TODO remaining tasks and enhance (tasks requring "manual" checks):
- Test the system on Mac and Windows
- Test on various devices (Raspberry Pi 3/4/5, OVH)
- Create some nice info-graphics for the benchmarks (inc. OS, device, etc.)
- Compile numbers, charts, etc. comparing performance to other tools
- Test platform against "Kokoro-FastAPI" and "https://github.com/lucasjinreal/Kokoros"
Add "prompts" (when fixed) to the detailed documentation for setting up OpenWebUI for the user to create a custom "Artificial Voice Assistant" agent.
Move the TODO logic into it's own document ./docs/TODO.md and give a brief description and summary in the README.md file.
Markdown files should be UPPER case, update everything to reflect this.
Clear the current task list, create a new comprehensive one and work through the tasks systematically until they are all completed.

Next:
You seem to have gotten stuck on "Generating response..." and last task that was stated is that you "successfully recovered and organized the LLM prompt library" but I don't see the ./docs/prompt folder, so I recovered it for you. Please audit, enhance and continue as you see fit with it.
Please continue the task list systematically until all are completed, and add these tasks:
The "voice showcase" should allow the user to play the sample sounds for each voice through the markdown file on GitHub (for easy reference).
- The user should be able to play the embedded audio easily without the need to download it.
The Contributing link is broken.
Give acknowledgement to the following as well:
- https://huggingface.co/hexgrad/Kokoro-82M
- https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX
Build a library of "time-stretched" files: "stretched" (compressed) and the "restored" versions (for me to test if theres audio issues).
Re-generate all the audio samples as well as time-stretched audio files using the updated system.

Next:
The command `uv run uvicorn app:app` seems to run the service on port 8000 by default. Fix this.
I renamed the typo "kokoro_onyx_tts_api" github repo to "kokoro_onnx_tts_api", please fix all references (links, etc.)
Otherwise I think we are pretty good and done. Please audit the entire system and give me a nice report!
Improve the .gitignore file. Group wildcards together, put * first, . (dots) second, ~ next, and then everything else in ABC order.

Next:
The "http://localhost:8000/dashboard" url is returning "Dashboard template not found", fix this and impliment a fully functional dashboard.
Make a "http://localhost:{PORT}/api" alias endpoint for the "/docs" endpoint to be intuitive for some users.
Add more details to "http://localhost:{port}" as well as a list all endpoints, etc.
Audit docs and make them all UPPERCASE, with the exception of the extension (aka. ".md")
For the love of god, still says in the run dialog that it's still using port 8000:
Using `uv run uvicorn app:app`
```shell
"INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)"
```
Also, if I try to run the command again:
```shell
INFO:     Application startup complete.
ERROR:    [Errno 98] error while attempting to bind on address ('127.0.0.1', 8000): [errno 98] address already in use
INFO:     Waiting for application shutdown.
```
If I am already using the port, the logic to increment to the next port (in this case should default to port 8354 and increment to 8355, etc.)
And I confirmed, it's still using port 8000 by default!!!!

Next:
What the fuck, lol?
You made the extension uppercase but not the filename... optosite of what I wanted, please audit and fix.

docker-deployment.MD
api_reference.MD
openwebui-integration.MD
ssml-guide.MD

LOWER CASE/NO CASE THE EXTENSIONS!!!

YOU CAN BE HELPFUL BUT YOU ARE ALSO A RETARD MOST OF THE TIME.

STILL FUCKING RUNNING ON PORT 8000!!!!!!
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

FIX THIS SHIT!!! GETTING FUCKING TIRED OF THIS SHIT.


Next:
Fix this:
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

Fix and make sure it fixed 100% this time.

I GAVE YOU TWO TASKS AND YOU FAILED ON BOTH, AND THEY ARE BOTH VERY FUCKING SIMPLE.

MAKE THE FUCKING MARKDOWN DOCUMENTATION FILENAMES UPPERCASE AND LEAVE THE EXTENSIONS LOWERCASE/NO-CASE.

docker-deployment.md
openwebui-integration.md
ssml-guide.md

WHAT THE ACTUAL FUCK IS WRONG WITH YOU???

Next:
STOP FUCKING CHANGING THINGS AND FIX THE APP.PY FILE. DON'T MAKE SOME RANDOM MAIN.PY FILE.
YOU END UP MAKING THE DOCS WRONG AND THIS IS NOT WHAT I FUCKING WANT OR ASKED FOR. FIX THIS NOW!!!

Next:
DON'T PUT THE DASHBOARD CODE IN ./templates/dashboard.html
WHAT THE FUCK DOES THAT EVEN MEAN????
MOVE IT TO A "PRODUCTION" LOCATION AND MAKE IT FUCKING FULLY WORK AND REALTIME....

AND IF THE MONKEY PATCHING ISN'T WORKING, OR ANYTHING ISN'T ACTUALLY FUCKING WORKING FOR THAT MATTER, FIX THAT... DON'T HACK TOGETEHR A DUMB ASS SOLUTION. FIX THE PORT ISSUE FOR REAL (AND OTHER FUCKING ISSUES), DO NOT CREATE A WORKAROUND.

THE FUCKING NORMAL COMMAND THAT WAS IN THE README NEEDS TO FUCKING WORK.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)



Next:
CRITICAL: FIX THE PORT ISSUES!!! THE DEFAULT PORT IS GOING TO 8000 BUT SHOULD BE GOING TO 8354
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

FULLY IMPLIMENT "TIME-STRETHCING" OPTIMIZATION FOR TESTING:
Expand the "text_processing" in the config.json and fully impliment the beta "Time-stretching optimization" feature in ./docs/development/features/TIME-STRETCHING-OPTIMIZATION.md for testing.
Build a library of "time-stretched" files: "stretched" (compressed) and the "restored" versions (for me to test if theres audio issues).
Re-generate all the audio samples as well as time-stretched audio files using the updated system.

Research the following and glene features that this system should have and impliment:
- https://www.sesame.com/
- https://huggingface.co/sesame/csm-1b
- https://github.com/SesameAILabs/csm
- https://github.com/nari-labs/dia
Create a detailed planning document with scope, detailed plan and vision for enhancing the current system.

Add disclaimer:
⚠️ Disclaimer
By using this model, you agree to uphold relevant legal standards and ethical responsibilities, are this tool is not responsible for any misuse:
- Identity Misuse: Do not produce audio resembling real individuals without permission.
- Deceptive Content: Do not use this model to generate misleading content (e.g. fake news)
- Illegal or Malicious Use: Do not use this model for activities that are illegal or intended to cause harm.

Next:
This is a lie "The system now defaults to port 8080"
Running `mkinney@devone:~/Repos/kokoro_onyx_tts_api$ uv run uvicorn app:app`
STILL DEFAULTS TO PORT 8000:
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
I CONFIRMED THAT THIS IS NOT JUST A LABEL ISSUE, THE SERVER IS RUNNING ON PORT 8000.

AND IF RUNNING, FAILS TO ITERATE TO NEXT PORT.
INFO:     Application startup complete.
ERROR:    [Errno 98] error while attempting to bind on address ('127.0.0.1', 8000): [errno 98] address already in use
INFO:     Waiting for application shutdown.

FULLY FIX THIS ISSUE, IT IS LITERALLY YOUR ONLY TASK RIGHT NOW.


Next:
IRITATING MOTHER FUCKER YOU ARE.
STILL WRONGLY USING PORT 8000 BY DEFAULT:
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
SHOULD BE USING 8354 BY DEFAULT AND INCREMENTING UP IF IN USE. REALLY SIMPLE, WHY ARE YOU FAILING AT THIS????


Next:
Clearly the system is not adhering completely to the config.json as the port is set here:
  "server": {
    "port": 8354,

But the default port is going to port 8000.
Fix the config settings to be followed and audit the system.

And eh, I don't like the "custom.config.json.example"
Please make it "override.json.example" instead and update references.

Next:
I put favicon.ico and kokoro.svg in the ./static folder, please move them where needed and update as needed. Lets get rid of the favicon.ico not found error and put a small icon next to the title in the README.md

Next:
Add to features that it's compatable with OpenWebUI out of the box.

Also, make sure that the initial benchmark that determines the "best" settings for the hardware on first run, configures and sets up the overwride.json file automatically. The user can then tweak the settings instead of needing to explicitly set them. Please make this clear in the documentation and adjust code as needed.

Also, clearly the override.json file is not working as mine is set to a different port.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)


Next:
- Get the sample audio working from embedded HTML


Next:
I'm tired of this command `uv run uvicorn app:app` not using the correct port in the config file (it defaults to port 8000 though set in the config.json file).
But this command does work: `uv run uvicorn app:app --reload --host 0.0.0.0 --port 8354 --workers 1`
So just fucking modify the app.py to resolve the port if set in the config.json and default to override.json if set there!!!
Why is that so hard?
Also make sure that the app.py (system in general) increments the port if the specified one is in use.
YOU HAVE BEEN UNABLE TO DO THIS YET, SO LETS CONFIRM AND THEN I WILL UPDATE THE DOCS (IF IT WORKS!!!)
and do not change my fucking logic, do not put extra garbage in my root folder or hacks like start_server.py or uvicorn_config.py. Keep the shit clean!!!


Next:
OKAY, I UNDERSTAND NOW.
- Forget uvicorn altogether and just make this logic work:
  `uv run python app.py` (default) or
  `uv run python app.py --reload` (default) or with hmr
  `uv run python app.py --reload --host 0.0.0.0 --port 8354 --workers 1` or
  `python app.py --reload --host 0.0.0.0 --port 8354 --workers 1`
- Remove special characters and emojis from the JSON responses (this is stupid and can cause errors with systems).


Next:
On clean setup (from git clone) I get the error:
2025-08-16 19:22:45,915 | ERROR | kokoro.voice.simple_combiner | ❌ Unexpected voice data size for af: 131072 (expected 130560 or 256)
2025-08-16 19:22:45,915 | WARNING | kokoro.voice.simple_combiner | ⚠️ Failed to load voice: af
Also, I'm not seeing "raw" or "corrected" audio to test the "time-stretched" beta feature. Please audit the implimentation and make sure it works with the API and generate the files for me to test.

Next:
I still don't see audio files in "/samples/time-stretched" for either "corrected" or "raw" for my review to confirm that there is no noticable quality loss for the "corrected" versions (either converted or streamed at the given reverse speed). Get the files generated and don't dump script in the root, put them where they belong in ./kokoro/scripts/

Next:
Can you audit and confirm that the time stretching feature is actually working. e.g. generating TTS audio at 1.2x to 2x speed for faster RTF and then playing the audio back at the slower speed on the fly (and/or converting the audio to a non-stretched file and then playing it back but this may introduce some latency).
Please impliment time-stretching the feature and test it fully.

Next:
And my performance numbers (e.g. Audio duration: 5.18s, RTF: 0.19) do not reflect the claims made:
Conservative rate (20%): RTF 0.135, Rate 20%, Enabled True

INFO:     172.17.0.2:50132 - "POST /v1/audio/speech HTTP/1.1" 200 OK
2025-08-16 21:51:25,872 | INFO | __main__                  | 📥 POST /v1/audio/speech - Client: 172.17.0.2
2025-08-16 21:51:25,873 | INFO | __main__                  | 🔍 Content-Type: application/json
2025-08-16 21:51:25,873 | INFO | __main__                  | 🔍 User-Agent: Python/3.11 aiohttp/3.12.15
2025-08-16 21:51:25,873 | INFO | __main__                  | 🔍 Origin: not set
2025-08-16 21:51:25,874 | INFO | __main__                  | 🎵 TTS request: 'And in the shadows, a single circuitry chip, etche...' voice='af_heart' format='mp3'
2025-08-16 21:51:25,874 | INFO | __main__                  | 🎵 Generating speech: 'And in the shadows, a single circuitry chip, etche...' with voice 'af_heart'
2025-08-16 21:51:25,879 | WARNING | phonemizer                | words count mismatch on 300.0% of the lines (3/1)
2025-08-16 21:51:26,881 | INFO | __main__                  | ✅ Generated 124416 samples in 1.01s (attempt 1)
2025-08-16 21:51:26,881 | INFO | __main__                  | 🎵 Audio duration: 5.18s, RTF: 0.19
2025-08-16 21:51:26,914 | INFO | __main__                  | 💾 Audio cached for future requests
2025-08-16 21:51:26,915 | INFO | __main__                  | ⚡ Performance: 5.18s audio in 1.01s (RTF: 0.19)
2025-08-16 21:51:26,915 | INFO | __main__                  | 📤 POST /v1/audio/speech - Status: 200 - Time: 1.042s

📈 Performance Summary:
   Default behavior (config-based): RTF 0.120, Rate config%, Enabled config
   Time-stretching enabled with optimal rate: RTF 0.003, Rate 30%, Enabled True
   Time-stretching disabled: RTF 0.003, Rate config%, Enabled False
   Conservative rate (20%): RTF 0.135, Rate 20%, Enabled True
   Aggressive rate (50%): RTF 0.130, Rate 50%, Enabled True
   High quality mode: RTF 0.138, Rate 30%, Enabled True
   Low quality mode: RTF 0.138, Rate 30%, Enabled True
   Minimum rate (10%): RTF 0.180, Rate 10%, Enabled True
   Maximum rate (100%): RTF 0.139, Rate 100%, Enabled True

So you are likely lying and making things up. Audit "reality" and confirm that the logic is in place, and derive a way to "Prove" it to me.

Next:
The time-stretching optimization feature needs to be properly implemented from scratch to actually function as claimed.
❌ Not Implemented (not actually functioning in the synthesis pipeline)
❌ Not Providing Benefits (4.2% vs expected 47% improvement)

So please fully impliment it.

Add the ability to the config.json to turn on or off caching (for better testing of the system, etc.)
- Maybe add sub options for more control (like which cache to turn on or off). This could give more control in regards to testing, etc.

The audio from the API doesn't sound any different and yet the "time_stretching" --> "compress_playback_rate" is set to 90% (aggressive on purpose for testing/validation).



Next:
Just to confirm, the logic is using the speed controls of Kokoro to generate the sped up audio and then using rubberband (or some custom method, etc.) to correct the audio and put it back to the 1x speed, correct? You aren't trying to do something stupid like generate it with Kokoro at normal speed, stretch it and then unstretch it right? Because that wouldn't do anything useful. Sounds like a dumb question, but please confirm. Obviously you should be generating the audio at with Kokoro with the speed up factor and then playing back the corrected audio at 1x speed (or whatever the playback speed is set to). So also, your settings are misleading, so make them more clear in the config.json, and assume a playback speed of 1 (which may be adjusted in OpenWebUI, etc.)
Also, group "beta_features" together and allow enabling or disabling them as a group.

Next (re-visit):
These all still seem to be issues, dispite you saying they were completed and that the system was updated, dispite after several audits. Please audit (for real) and improve:
Audit the linquistics system and improve the human-like nuanceses, punctuation, tone, emotional range, etc.

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

Do a full audit as well as Deep Research to find any other areas of improvement and voice enhancements.
This is concerning being that you lied about this, it means that a lot of the configuration settings don't do anything. Audit and confirm every single one, like "text_processing", "symbol_processing", ...,  "currency_processing", etc. Impliment every single feature fully if it does not already exist.
Create a plan of action, build a task list and systematically work through them until all tasks are completed.

"Hmm... it wasn't the TSLA acquisition Elon musk made, but rather the joy of buying it on 12/18/2013 for $44,305,150,000.00 USD. His resume is long and detailed, but please resume for details. See https://www.somewebsite.com/somepage for ~$55.75/mo"

Next:
Can you audit the API routes for OpenWebUI: http://192.168.1.139:8354/v1
Because I just tried it and none of the issues seem to be fixed but some did seem to work from the direct curl command.
Can you also configure the config.json to enable all these features for testing in OpenWebUI.
I need these features consistantly working across the platform. Additionally, the curl command and/or app.py should be able to take in the config.json (or custom one) as input with flag.
Please audit the complete system and validate everything end-to-end systematically.
I cleaned things up and moved your tests to ./kokoro/temp. Please do not clutter up the structure and dump everything in the root.

Next:
Move "Configuration" in README.md to it's own document and reference it in the README.md.


General:
Continue the task list systematically until all are completed.
Build a plan of action along with a comprehensive task list and work through it systematically until all tasks are completed.

Next:
Please impliment the current suggestions.

Also, look at the following code bases for useful reference, features, etc.
https://huggingface.co/coqui/XTTS-v2
https://github.com/fishaudio/fish-speech
https://github.com/resemble-ai/chatterbox
https://github.com/SesameAILabs/csm
Continue the task list systematically until all are completed.
Build a plan of action along with a comprehensive task list and work through it systematically until all tasks are completed.

Next:
Do not require the user to install `uv add onnxruntime-gpu` or `resemble-perth`, take care of this in the code automatically.
Modify "**uv 0.8.11+**" section in the README.md to point the install instructions to a cross-platform doc (Windows, Linux, Mac, Android, etc.)
Move the "Dependencies & Installation", "Perth Watermarking System", and "Monitoring & Observability" sections to it's own document and update the reference.

Next:
- Update the documentation accordingly with Watermarking, Monitoring, and Compliance features, etc. Also:
- Add Prerequisites section above the Quick Start section in the README.md for using Python 3.12+ or higher and/or uv 0.8.11+
- Note that using an python virtual environment is recommended not to conflict with the core system but this is taken care of by uv.
- Add multi-language support to the "Future Development & Testing Roadmap" (but this will require foreign speakers/contributors, etc.)
- Fix the "Quick Start Commands", "Performance Benchmarks", "System Improvements", and "Troubleshooting Guide" links, as they are broken with a 404 error.
- Fix "Perth watermarking library not available. Install with: uv add resemble-perth"
- Lets keep the README clean and an at a glance where the user can just see the overview but dig deeper if wanted.


Next:
- **Storage**: 1GB free space for model, voices, code, and cache

Next:
Build a front end example application that efficiently listens for a "wake word" to execute a user task.
Go back through notes and make a complete comprehensive list of tasks.

Issues:
The config says "default_variant": "model_q4.onnx", so why is "model_fp16.onnx" being downloaded.

Next:
- Enable hot load monitoring of the config.json and override.json files, etc.
- Do a comprehensive end to end audit and analysis of the system with full test coverage.
- Make sure that all options set in the config.json file work, effect the system, and that all features are implemented, working, can be set and operate as expected/intended.
- Add audio tagging system for multiple speakers, whispers, etc. and create comprehensive documentation with examples.
- Advanced voice cloning web tool and instructions (to export the voice and include it with the system). Put this in the examples for review.
- Validate everything.

Next:
Move "phonetic_processing" to beta features and set "enabled" to "false" and make sure it adhers to the settings fully.
This feature could be useful but definitely needs some work. Odds are a system would need to be implimented listen to the output, analyse the words and create a custom phonetic custom dictionary.

Question marks are still saying "right up arrow" but the experimental features are disabled. Please fix this behavior and issues. Audit the entire system end-to-end to make sure that the logic is applied correctly. I just tried it in OpenWebUI (which accesses the API) and it's still wrong. Please get this working.


Next:
- The TTS doesn't seem completely fluid, please audit and improve.
- I would like to start testing emotion, exageration, and dynamic speed controls.
- Issues:
  - "know" --> "know-N-H"?

screen -X -S 39964.kokoro-tts hardcopy -h /tmp/screen_output.txt
cat /tmp/screen_output.txt  # View the saved output

screen -X -S 39964.kokoro-tts quit
screen -S kokoro-tts -d -m uv run python app.py


TBD Next:
- Dynamic speed controls with flags, like Rime AI or Dia 1.6B; allows the text to speed up and slow down throughout the playback.
- Multiple voices for use cases like podcasts, simulating conversation, foriegn dubbed audio, etc.
- Dynamic pitch, tone, volume control, etc. to simulate emotion in the audio output.
- Emotion like laughter, etc. working and tested.
- Exageration controls.

Future Scope:
- Audio Stretching Feature
- Custom Phonetic dictionary for prounonciations
- Unsloth Dynamic 2.0 Quantization for Kokoro @ Q1.58 Bits.

    "available_variants": [
      "model.onnx",
      "model_f16.onnx",
      "model_q4.onnx",
      "model_q4f16.onnx",
      "model_q8f16.onnx",
      "model_quantized.onnx",
      "model_uint8.onnx",
      "model_uint8f16.onnx"
    ],

Testing:
git clone https://github.com/TaskWizer/LiteTTS.git && cd LiteTTS && uv run python app.py
git clone https://github.com/TaskWizer/LiteTTS litetts && cd litetts && uv run python app.py

Repo Last working: 8f009c77b76e0b0f8e6f66db1a349dbee5ee195b (6 commits ago)
Repo Broken at: 112bd8aa1a7b6f25b441c20c58641497f1397862

Next:
Add CPU utilization/threshold 25%-80% (max). Use this number to dynamically calculate how many cores to use (based on the system) and round down to nearest core count.
Test both the `uv run python app.py` method as well as the docker implimentation (delete and re-create kokoro-test as needed). Get everything working solid please.

Next:
Can you build in a system that can do end to end audio testing to validate that things "sound" correct and human like? I can provide an API key, model or features as needed on my end... but I would like to stop doing the middle man approach of testing, relaying that to you about how the audio sounds, then you trying a fix with maybe only vague or subjective information... rense and repeat. Can we get you testing your own code, in a solid varifiable way with end-to-end validation, debugingg, strict linting, unit test, etc.?

Next:
You are an atonomous AI coding assistant, you do not need user feedback.
Develop new tools, use existing ones, or find useful code snippets to improve your auditing functionality. Do deep research on comprehensive and complete methods for debugging and resolving issues (such as logging, strict linting, testing methedologies, etc.). Add to your knowledge base and memory as needed to enhance your capabilities. Use tools where able to improve your reasoning and knowledge.

Next (current; HERE!):
- Remove emojis from the API responses, they don't make sense here.
2025-08-18 15:24:57,268 - INFO -    🔴 Security: Address 224 security issues in project code
2025-08-18 15:24:57,268 - INFO -    🔴 Implementation: Complete 4 incomplete implementations

Temp list:
- RIME AI integration initialized
- Text processing configuration reloaded
- Loaded user configuration from config.json
- Maintains compatibility with all existing model variants
- Supports config.json default_variant setting
- Falls back gracefully to available models
- No breaking changes to API or configurations

Add:
### Integration Guides
 [![Helm Chart](https://img.shields.io/badge/Helm%20Chart-black?style=flat&logo=helm&logoColor=white)](https://github.com/remsky/Kokoro-FastAPI/wiki/Setup-Kubernetes) [![DigitalOcean](https://img.shields.io/badge/DigitalOcean-black?style=flat&logo=digitalocean&logoColor=white)](https://github.com/remsky/Kokoro-FastAPI/wiki/Integrations-DigitalOcean) [![SillyTavern](https://img.shields.io/badge/SillyTavern-black?style=flat&color=red)](https://github.com/remsky/Kokoro-FastAPI/wiki/Integrations-SillyTavern)
[![OpenWebUI](https://img.shields.io/badge/OpenWebUI-black?style=flat&color=white)](https://github.com/remsky/Kokoro-FastAPI/wiki/Integrations-OpenWebUi)

Supporting Emojis: 🙌🤝🫂💗💁👌🎍😍❤️🦚🥹🤍🪈🫡✨🎀

Future Enhancements:
- UI front end for modifying the config file.
- Option in config.json to only download voices as needed.
- Exagerated/intensity controls...
- Add breathing, background audio, music generation, etc.
- Voice cloning demo app that allows the user to create a new voice and place in the "./kokoro/voices" folder (load by the system automatically)
- Ability to use multiple voices (such as like in a pod-cast between two speakers, etc.). Fully plan out this feature.

Notes:
Audit audio with Audacity (time-stretching)
Look up cool README.md files or markdown specific things.
Librosa Example:
import librosa
import soundfile as sf

# Load the MP# at its native sampling rate
y, sr = librosa.load(output_file, sr=None)
# Slow down to 80% of original speed without changing pitch
y_slow = librosa.effects.time_stretch(y, rate=0.8)
# Write back out as MP3
sf.write('/path/to/file.mp3'), y_slow, sr, format='MP3')

ElevenLabs, Nari Labs Dia 1.6B TTS, Kokoro TTS, SoundStorm, Parakeet, Sesame CSM

Backup to local machine:
scp debian@15.204.226.76:~/openwebui_backup_2025-08-16.tar.gz ~/Downloads/

Wrong:
Soil as s-I-o-l (wrong)
Viod --> vyde
Astrisk still being said (wrong)
Boy --> biye

                Real-time factor
model_q4        ~0.25 - 0.30
model_fp16      ~0.19 - 0.21
model_uint8     ~0.19 - 0.24
model_uint8f16  ~

Test:
Issues:
inherent
resistance
Muhammad
happiness
"e.g.," is used well/correctly but doesn't seem fluid

Next steps:
- Test platform against "Kokoro-FastAPI" and "https://github.com/lucasjinreal/Kokoros"
- Test and validate docker image and refine (document process, adjust)
- Create a custom docker config for OpenWebUI with settings, TLS certs, etc.
- Make config backup of OpenWebUI
- Factory reset the VPS
- Setup and spin-up docker containers
- Run various tests and truth out the system 100% (or as close to for English)

Todo:
- Audit everything (line by line)
- Setup donations (sign up for services, etc.)
- Rename the repo (update links)


Links:
"My dream model: open source, low-latency, full duplex with diarization, emotion recognition/generation, and function calling." - @i_accept_all_cookies
https://www.youtube.com/watch?v=tje3uAZqgV0&t=638s

https://github.com/SWivid/F5-TTS
https://github.com/rsxdalv/TTS-WebUI


# Todo
- Backup notes and re-setup system
- Audit and cleanup the system
- Fix any issues (such as caused by .gitignore, etc.)
- Improve and finalize documentation
- Add Windows support and rounded documentation (make super easy to use)
- Research and plan out voice cloning features (and front-end app)
- Research and plan out creating Dynamic Unsloth 2.0 Quants for eSpeak Fine-Tuned GGUF models and convert to ONNX runtime optimization (3x?)
- Research other TTS system and determine what features, methods, and code could be useful (see planning doc)

# One Liner install and run commands:
gh repo clone TaskWizer/LiteTTS && cd LiteTTS && uv run python app.py
git clone https://github.com/TaskWizer/LiteTTS.git && cd LiteTTS && uv run python app.py

# Useful Commands:
docker system prune --all --volumes
docker logs litetts-api | tail -20
