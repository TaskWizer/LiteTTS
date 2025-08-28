I need to replace all references to "kokoro.svg" with "LiteTTS.svg" throughout the codebase. Please:

1. Search the entire codebase to find all files that reference "kokoro.svg"
2. Update each occurrence to use "LiteTTS.svg" instead
3. This includes references in:
   - HTML files
   - CSS files
   - JavaScript/TypeScript files
   - Configuration files
   - Documentation files (README, etc.)
   - Any other file types that might contain this reference
4. Ensure the actual SVG file is also renamed from "kokoro.svg" to "LiteTTS.svg" if it exists
5. Verify that all changes maintain the correct file paths and functionality

Please show me what files will be affected before making the changes, and then proceed with the updates.

On first run:
mkinney@devone:~/Repos/LiteTTS$ uv run python app.py
Failed to load configuration: ModelConfig.__init__() got an unexpected keyword argument 'preload_models'

Dashboard

seems to be constantly checking...
INFO:     127.0.0.1:32954 - "GET /dashboard/data HTTP/1.1" 200 OK
INFO:     127.0.0.1:32954 - "GET /dashboard/data HTTP/1.1" 200 OK
INFO:     127.0.0.1:32954 - "GET /dashboard/data HTTP/1.1" 200 OK
INFO:     127.0.0.1:32954 - "GET /dashboard/data HTTP/1.1" 200 OK

Expand the Debug information.

Real-Time TTS Testing error: TTS Error: {"detail":{"error":"Voice 'af_heart' not found. Available voices: ","type":"validation_error"}}

static/examples/ is a broken url in the dashboard.




You fucked up a little bit but it seems fine. The system python environment is locked down, don't use it.
pip install soundfile fastapi uvicorn numpy onnxruntime psutil requests pydantic
Should be using uv.


mkinney@devone:~/Repos/LiteTTS$ docker-compose up -d
Creating network "litetts-network" with driver "bridge"
ERROR: invalid pool request: Pool overlaps with other one on this address space


mkinney@devone:~/Repos/LiteTTS$ docker compose up -d
WARN[0000] /home/mkinney/Repos/LiteTTS/docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion


Audit and improve the code base and quality.
Instead of setting up logging for every script or file, use a decorator function to streamline this and use @logging and @profiler (for auditing performance), etc. This will likely reduce hundreds if not thosands of lines and make the system easier to maintain. Consider using a more advanced logging library as well.
Cleanup tests and re-use code through parameterized functions, dynamic code, decorators, etc.


One docker config, so no: docker-compose.prod.yml, Dockerfile.dev,
Move tests to ./kokoro/tests (audit and cleanup)
Move scripts to ./kokoro/scripts (audit and cleanup)
Get examples fully functional and working from the web front-end
Do an end-to-end audit and validate everything.

Audit and cleanup the task list and append it with the new scope and tasks.
Continue the task list systematically until ALL are completed.
Build a plan of action along with a comprehensive task list and work through it systematically until all tasks are completed.


Todo
- Get server up with Docker images
- Setup DNS settings
- TaskWizer:
  - Landing Page
  - Email
  - LiteLLM published
  - Logo design


LVS

TBD:
How to optimize OpenWebUI to stop generating speach if the user stops it (with ability to continue on)?


Audit, test and validate all beta features and get them to at least a basic functioning state for further evaluation.

/metrics and /tts API endpoints don't seem to work.
the url endpoint does not show /examples endpoint listed.
I would like /examples to be a landing page to try out the examples, not an API endpoint per se.

/dashboard should
- include hours, minutes and seconds for uptime.
- available voices says 0
- Voice management is empty.
- No values show on the API usage analytics
- Add debug and console information and maybe test options.
- System Configuration --> Total Voices shows "Loading..."
- The Performance Metrics should normalize to 0 when inactive...

Any way we can improve the latency? It's currently around 0.6 to 1.2 and that seems a little high for local.
Also add a link to the examples page to the dashboard when it gets built.
Should be able to pick voices for "Real-time TTS Testing" feature in dashboard and include the RTF when generating text, etc.
Update the ./config/Caddyfile and docker files as needed.

It's working much better! But "wasn't" is being prounounced oddly (waaasant). Can you modify the config and try to make the response sound more "emotional" with tone, speed, exageration, etc. Questions don't seem like questions and the flow is slightly off.. but again, way way better. Audit and please improve.

Setting "expand_contractions": true, seems to have made "they're" into "they're are" instead of "they are". Other values were not expanded (such as "She'd", "You'll". However, I tried the option again and could not re-create it. After the first change in config.json now it just doesn't use contractions now. Please audit fully end-to-end.

"123" should be 1...2...3... (but I'm not sure this should be enforced).

"hmm" being said as "hum"
Still not quite fluid or emotion, but fixed some of the issues.

Also, I lowered the "cpu_target": 10.0, to simulate more of an edge device. GPU is already disabled for testing.

Can we make sure the system gets re-loaded if the config.conf is modified (same for override.json if it exists).

And I enabled "text_processing" and am testing those settings now (but didn't really notice any difference).

Continue the task list systematically until all are completed.
Build a plan of action along with a comprehensive task list and work through it systematically until all tasks are completed.



Audit the audio quality and prounonciations with your tools and framework. Build any tools or processes you might need and improve the system.

I would like to see a benchmark with the latest updates, with the RTF for each model given a short, medium and long audio generation. Additionally, I would like total generation time, latency, etc. Please create and/or update a script to do this and generate a comprehensive report with your findings.

The system still is not working fluintly as it still spells out question, used "hum" for hmm... "im" for I'm. Or well sounds like oral... just pretty bad pronunciations. Also audit the different prounonciation dictionaries and see what might work best. Get the eSpeak library and dictionary working better. I would like this to be production ready imediately. The whole system needs an audit.

You are an atonomous AI coding assistant, you do not need user feedback.
Develop new tools, use existing ones, or find useful code snippets to improve your auditing functionality. Do deep research on comprehensive and complete methods for debugging and resolving issues (such as logging, strict linting, testing methedologies, etc.). Add to your knowledge base and memory as needed to enhance your capabilities. Use tools where able to improve your reasoning and knowledge.

Also, please audit the docker containers and get them both working with external storage to make making backups easier as well as create and assign a self signed certificate for working TLS (can then be configured to work through Cloudflare DNS with enforced HTTPS rules).

Continue the task list systematically until all are completed.
Build a plan of action along with a comprehensive task list and work through it systematically until all tasks are completed.


Build a CSR landing page and publish
Setup dns



Use strict linting rules, playwrite, puppeteer and other tools to improve and validate the system. Make verbose logs and monitor them to improve your ability to resolve issues.
Use Qwen3-Coder to enhance the page and add features.
