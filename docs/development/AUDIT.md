TBD:
- Improvements to OpenWebUI:
  - Need to be able to control TTS auto start by "agent"
  - Stream text to TTS system to read while tokens being generated.



Todo (self):
- Improve documentation, create tutorials, etc.
- Link Sample Audio to play in docs (Wiki?)
- Get docker instance fully working and tested.
- Add additional voices by voice cloning (narrator, etc)
- Submit working alpha release to content creators when ready.
- Improve the implimentation of navigation
- Test Wiki features and navigation
- Publish final version to PyPi/Pip with instructions
- Make dashboard and example apps mobile responsive and more intuitive
- Make a front-end UI for the config options.
- Create a validation system to utilize Rime AI (API) to enhance and improve the system programatically

Examples:
- Audio visualizer application
- Dumb machine and audio mixer, etc.
- Podcast generator (multi-voice, etc.)
- Demo mult-agent voice conferencing demo

Features:
- Ability to use multiple voices
- Enhance and add more demo examples
- Integrate into voice chat demo app.

Deep Research:
- OpenSLR - LibriSpeech ASR Corpus
- Microsoft SpeechTS (Legacy)
- Sesame/CSM-1b features
- RIME AI, ElevenLabs, etc.
- https://www.reddit.com/r/LocalLLaMA/comments/1f0awd6/best_local_open_source_texttospeech_and/


TTS:
"won't we" sounds like "want we"
"we'll" sounds like "wehl" (should be more like "wh-eel"
"a.m" sounds like "a (pause) m" and should just be "A-M"
"beautiful" sounds like ...
"happiness"

Gets currency and date formats wrong:
05/15/2018
$123.45 + 67.89 = ??



When I test the "Real-time TTS Testing" feature on the dashboard, aka. "http://localhost:8354/dashboard", some of the voices have an error:
TTS Error: {"detail":"Generation failed: Voice am_liam not found in available voices"}

On the current hardware with CPU only, we have a RTF of ~0.20 to ~0.25 which is pretty good, but also a ~1 second latency causing a bottleneck.
This latency is almost certainly due to the initial model loading and computation setup, not the actual inference speed. Warm up and prime the model on startup from storage (disk, cache, or network) into memory, set up the computation graph, and load weights into memory also. The First-Token Computation: The first inference run has additional overhead as everything is primed. Look into ways to improve the latency.

Tasks:
- Fix TTS Voice dropdown in OpenWebUI (if doable with API compatability)
- Audit contractions, porosity, tone, intanation, etc.
- Move "config.json" to `./config/settings.json` (review and merge and update references)
- Systematically go through each option in `./config/settings.json` and make sure all the features are implimented and can be modified with the settings.
- Do an end-to-end audit of the platform and create a list of performance optimization method and impliment them systematically.
- Impliment te eSpeak library to enhance the prounonciation of words.
- Audit the complete system end-to-end systematically until all tasks are complted and the system is completely working (varified programatically and with complete test coverage).
- Remove all junk and placeholder code, tests, etc and cleanup.
- A lot of the settings in settings.json do not seem to do anything... make sure all of these options work, test them one by one to validate.
- Continue the task list systematically until all are completed.
- Build a plan of action along with a comprehensive task list and work through it systematically until all tasks are completed.
- There are still old references to "kokoro" before the renaming of the project, audit and update any old references (but leave attribution, etc.)
- Audit and run end-to-end tests and validate everything is working reliably.

Get Warning when running:
Failed to load configuration: ModelConfig.__init__() got an unexpected keyword argument 'preload_models'

Some complicated text can generate error:
2025-08-26 22:31:57,918 | ERROR | __main__                  | ❌ Request failed in 0.001s: Out of range float values are not JSON compliant: inf
INFO:     192.168.1.152:62278 - "GET /dashboard/data HTTP/1.1" 500 Internal Server Error
ERROR:    Exception in ASGI application
  + Exception Group Traceback (most recent call last):
  |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/_utils.py", line 77, in collapse_excgroups
  |     yield
  |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/middleware/base.py", line 183, in __call__
  |     async with anyio.create_task_group() as task_group:
  |                ^^^^^^^^^^^^^^^^^^^^^^^^^
  |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/anyio/_backends/_asyncio.py", line 772, in __aexit__
  |     raise BaseExceptionGroup(
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/uvicorn/protocols/http/h11_impl.py", line 403, in run_asgi
    |     result = await app(  # type: ignore[func-returns-value]
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
    |     return await self.app(scope, receive, send)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/fastapi/applications.py", line 1054, in __call__
    |     await super().__call__(scope, receive, send)
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/applications.py", line 113, in __call__
    |     await self.middleware_stack(scope, receive, send)
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/middleware/errors.py", line 186, in __call__
    |     raise exc
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/middleware/errors.py", line 164, in __call__
    |     await self.app(scope, receive, _send)
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/middleware/base.py", line 182, in __call__
    |     with recv_stream, send_stream, collapse_excgroups():
    |                                    ^^^^^^^^^^^^^^^^^^^^
    |   File "/home/mkinney/.local/share/uv/python/cpython-3.12.10-linux-x86_64-gnu/lib/python3.12/contextlib.py", line 158, in __exit__
    |     self.gen.throw(value)
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/_utils.py", line 83, in collapse_excgroups
    |     raise exc
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/middleware/base.py", line 184, in __call__
    |     response = await self.dispatch_func(request, call_next)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/mkinney/Repos/LiteTTS-Fix/app.py", line 280, in log_requests
    |     response = await call_next(request)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/middleware/base.py", line 159, in call_next
    |     raise app_exc
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/middleware/base.py", line 144, in coro
    |     await self.app(scope, receive_or_disconnect, send_no_error)
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/middleware/cors.py", line 85, in __call__
    |     await self.app(scope, receive, send)
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/middleware/exceptions.py", line 63, in __call__
    |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/routing.py", line 716, in __call__
    |     await self.middleware_stack(scope, receive, send)
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/routing.py", line 736, in app
    |     await route.handle(scope, receive, send)
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/routing.py", line 290, in handle
    |     await self.app(scope, receive, send)
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/routing.py", line 78, in app
    |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/routing.py", line 75, in app
    |     response = await f(request)
    |                ^^^^^^^^^^^^^^^^
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/fastapi/routing.py", line 339, in app
    |     response = actual_response_class(content, **response_args)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/responses.py", line 190, in __init__
    |     super().__init__(content, status_code, headers, media_type, background)
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/responses.py", line 47, in __init__
    |     self.body = self.render(content)
    |                 ^^^^^^^^^^^^^^^^^^^^
    |   File "/home/mkinney/Repos/LiteTTS-Fix/.venv/lib/python3.12/site-packages/starlette/responses.py", line 193, in render
    |     return json.dumps(
    |            ^^^^^^^^^^^
    |   File "/home/mkinney/.local/share/uv/python/cpython-3.12.10-linux-x86_64-gnu/lib/python3.12/json/__init__.py", line 238, in dumps
    |     **kw).encode(obj)
    |           ^^^^^^^^^^^
    |   File "/home/mkinney/.local/share/uv/python/cpython-3.12.10-linux-x86_64-gnu/lib/python3.12/json/encoder.py", line 200, in encode
    |     chunks = self.iterencode(o, _one_shot=True)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/home/mkinney/.local/share/uv/python/cpython-3.12.10-linux-x86_64-gnu/lib/python3.12/json/encoder.py", line 258, in iterencode
    |     return _iterencode(o, 0)
    |            ^^^^^^^^^^^^^^^^^
    | ValueError: Out of range float values are not JSON compliant: inf
    +------------------------------------

Do a systematic audit of the entire system, evaluate for gaps with a gap analysis, validate the quality of the code and work through enhancing and improving the code and features step by step until complete. Create a comprehensive task list to follow and work through it until all tasks are completed.


Please do deep research on various CPU Optimization Approaches, such as:
* Instruction Set Optimization
* Batch Processing Optimization

Caching and Computation Reuse:
* Attention KV Cache Optimization
* Phoneme-Level Caching
* Precomputed Feature Storage (we are already doing this to a degree)

Pipelined Execution: Breaking the TTS pipeline into independent stages (text normalization, phonemization, acoustic model, vocoder) allows each component to process different requests simultaneously, improving overall throughput through pipeline parallelism
