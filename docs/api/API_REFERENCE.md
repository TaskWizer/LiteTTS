# 🔌 API Reference

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../FEATURES.md) | [Configuration](../CONFIGURATION.md) | [Performance](../PERFORMANCE.md) | [Monitoring](../MONITORING.md) | [Testing](../TESTING.md) | [Troubleshooting](../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../DEPENDENCIES.md) | [Quick Start](../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](API_REFERENCE.md) | [Development](../development/README.md) | [Voice System](../voices/README.md) | [Watermarking](../WATERMARKING.md)

**Project:** [Changelog](../CHANGELOG.md) | [Roadmap](../ROADMAP.md) | [Contributing](../CONTRIBUTIONS.md) | [Beta Features](../BETA_FEATURES.md)

---

## ⚠️ Ethical Use Disclaimer

**By using this API, you agree to uphold relevant legal standards and ethical responsibilities. This service is not responsible for any misuse:**

- **🚫 Identity Misuse**: Do not produce audio resembling real individuals without explicit permission
- **🚫 Deceptive Content**: Do not use this API to generate misleading content (e.g., fake news, impersonation)
- **🚫 Illegal or Malicious Use**: Do not use this API for activities that are illegal or intended to cause harm

**We strongly encourage responsible AI practices and respect for individual privacy and consent.**

## Base URL

```
http://localhost:8000
```

## Authentication

No authentication required for local deployment.

## Endpoints

### POST /v1/audio/speech

Generate speech from text input.

#### Request Body

```json
{
  "input": "string",           // Text or SSML to synthesize
  "voice": "string",           // Voice ID (e.g., "af_heart")
  "response_format": "string", // Audio format: "mp3" or "wav"
  "speed": "number"            // Optional: Speech speed (0.5-2.0)
}
```

#### Response

- **Content-Type**: `audio/mpeg` (for mp3) or `audio/wav` (for wav)
- **Body**: Binary audio data

#### Example

```bash
curl -X POST 'http://localhost:8000/v1/audio/speech' \
  -H 'Content-Type: application/json' \
  -d '{
    "input": "Hello world!",
    "voice": "af_heart",
    "response_format": "mp3"
  }' \
  --output speech.mp3
```

### GET /v1/voices

List all available voices.

#### Response

```json
{
  "voices": [
    {
      "id": "af_heart",
      "name": "Heart",
      "gender": "female",
      "language": "en-US",
      "description": "Warm, natural voice"
    }
  ]
}
```

### GET /dashboard

View real-time analytics and performance metrics.

#### Response

HTML dashboard with:
- Performance metrics (RTF, response times)
- Usage statistics (requests, voice popularity)
- System health (memory, cache hit rates)
- Error rates and status codes

## Voice IDs

### American English
- **Female**: `af_heart`, `af_bella`, `af_alloy`, `af_nova`, `af_sky`
- **Male**: `am_onyx`, `am_liam`, `am_echo`, `am_adam`

### British English
- **Female**: `bf_alice`, `bf_emma`, `bf_lily`
- **Male**: `bm_daniel`, `bm_george`

### Japanese
- **Female**: `jf_alpha`, `jf_nezumi`
- **Male**: `jm_kumo`

### Chinese
- **Female**: `zf_xiaobei`, `zf_xiaoni`
- **Male**: `zm_yunxi`, `zm_yunyang`

*See [Voice Showcase](voices/README.md) for complete list with audio samples.*

## SSML Support

Enhanced SSML with background noise synthesis:

```xml
<speak>
  <background type="rain" volume="20">
    Your text with ambient rain sounds
  </background>
</speak>
```

**Background Types**: `nature`, `rain`, `coffee_shop`, `office`, `wind`
**Volume Range**: 1-100

## Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 400 | Bad Request | Check request format and parameters |
| 404 | Voice Not Found | Use valid voice ID from `/v1/voices` |
| 422 | Validation Error | Verify input text and parameters |
| 500 | Server Error | Check server logs, retry request |

## Rate Limits

- **Default**: No rate limiting for local deployment
- **Recommended**: 10-20 concurrent requests for optimal performance
- **Monitor**: Use `/dashboard` to track performance

## Performance

### Real-Time Factor (RTF)
- **Excellent**: < 0.3 (3x faster than real-time)
- **Good**: 0.3-0.7
- **Fair**: 0.7-1.0
- **Poor**: > 1.0

### Response Times
- **Cached**: ~29ms (typical)
- **Uncached**: ~200-1000ms (depending on text length)
- **SSML Background**: +100-200ms additional

### Optimization Tips
1. Use caching for repeated phrases
2. Keep text length reasonable (< 500 chars per request)
3. Monitor RTF via dashboard
4. Use appropriate voice for content type

## SDKs and Libraries

### Python

```python
import requests

def text_to_speech(text, voice="af_heart", format="mp3"):
    response = requests.post(
        'http://localhost:8000/v1/audio/speech',
        json={
            'input': text,
            'voice': voice,
            'response_format': format
        }
    )
    return response.content

# Usage
audio_data = text_to_speech("Hello world!")
with open('output.mp3', 'wb') as f:
    f.write(audio_data)
```

### JavaScript

```javascript
async function textToSpeech(text, voice = 'af_heart', format = 'mp3') {
    const response = await fetch('http://localhost:8000/v1/audio/speech', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            input: text,
            voice: voice,
            response_format: format
        })
    });
    
    return await response.blob();
}

// Usage
textToSpeech('Hello world!').then(blob => {
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    audio.play();
});
```

## OpenAI Compatibility

This API is compatible with OpenAI's TTS API format, allowing drop-in replacement:

```python
# OpenAI format (compatible)
import openai

client = openai.OpenAI(
    api_key="dummy",
    base_url="http://localhost:8000/v1"
)

response = client.audio.speech.create(
    model="kokoro",
    voice="af_heart",
    input="Hello world!"
)
```

---

*For more examples and guides, see [SSML Guide](ssml_guide.md) and [Performance Guide](performance_guide.md).*
