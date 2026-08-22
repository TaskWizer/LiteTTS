# SSML Reference Guide

**Date:** 2026-08-22

---

## Overview

LiteTTS supports Speech Synthesis Markup Language (SSML) for fine-grained control over speech synthesis. This document describes supported SSML tags, their attributes, and known limitations.

---

## Supported SSML Tags

### Core Tags

| Tag | Status | Description |
|-----|--------|-------------|
| `<speak>` | ✅ Full | Root element for SSML content |
| `<prosody>` | ⚠️ Limited | Pitch, rate, and volume control |
| `<emphasis>` | ✅ Full | Word/phrase emphasis |
| `<break>` | ✅ Full | Pause insertion |
| `<say-as>` | ✅ Full | Interpretation of special content |
| `<sub>` | ✅ Full | Substitution |
| `<phoneme>` | ✅ Full | Phonetic pronunciation |
| `<voice>` | ✅ Full | Voice selection |
| `<lang>` | ✅ Full | Language specification |

### Custom Tags

| Tag | Status | Description |
|-----|--------|-------------|
| `<background>` | ✅ Full | Ambient background noise |
| `<audio>` | 🔜 Planned | Audio file insertion |

---

## Tag Reference

### `<emphasis>`

Adds emphasis to words or phrases.

```xml
<emphasis level="strong">This is important</emphasis>
<emphasis level="moderate">This is slightly emphasized</emphasis>
<emphasis level="none">No emphasis</emphasis>
```

**Attributes:**

| Attribute | Values | Default | Notes |
|-----------|--------|---------|-------|
| `level` | strong, moderate, none | moderate | Emphasis intensity |

**Example:**
```xml
<emphasis level="strong">Warning</emphasis>: System failure imminent!
```

---

### `<prosody>`

Controls pitch, rate, and volume. **Note:** Uses minimal marking to avoid SSML corruption with Kokoro engine.

```xml
<prosody rate="fast">Speak quickly</prosody>
<prosody pitch="high">Higher pitch</prosody>
<prosody volume="loud">Louder</prosody>
```

**Attributes:**

| Attribute | Values | Default | Notes |
|-----------|--------|---------|-------|
| `rate` | slow, fast, medium, or percentage | medium | Speaking rate |
| `pitch` | number±st, low, medium, high | medium | Pitch adjustment |
| `volume` | soft, medium, loud, or number | medium | Volume level |

**Limitations:**
- Full prosody implementation is intentionally limited for safety
- Kokoro's native prosody handling may conflict with aggressive SSML prosody

---

### `<break>`

Inserts pauses in speech.

```xml
Normal speech <break time="0.5s"/> Pause...
Short pause <break time="200ms"/> Continue
```

**Attributes:**

| Attribute | Values | Default | Notes |
|-----------|--------|---------|-------|
| `time` | seconds (s) or milliseconds (ms) | - | Duration of pause |
| `strength` | none, x-weak, weak, medium, strong, x-strong | medium | Relative strength |

**Example:**
```xml
Before the answer <break time="0.3s"/> The answer is 42.
```

---

### `<say-as>`

Interprets special content types.

```xml
<say-as interpret="date">2024-01-15</say-as>
<say-as interpret="time">14:30</say-as>
<say-as interpret="cardinal">42</say-as>
<say-as interpret="ordinal">1st</say-as>
```

**Interpret Values:**

| Value | Description | Example Output |
|-------|-------------|----------------|
| `date` | Date interpretation | "January 15, 2024" |
| `time` | Time interpretation | "2:30 PM" |
| `cardinal` | Number as cardinal | "forty-two" |
| `ordinal` | Number as ordinal | "first" |
| `telephone` | Telephone number | Phone digits |
| `currency` | Currency amount | Dollar amount |
| `spell-out` | Letter-by-letter | "A B C" |

---

### `<phoneme>`

Provides phonetic pronunciation using IPA or RIME notation.

```xml
<phoneme alphabet="ipa" ph="tɪˈleɪfɒn">telephone</phoneme>
<phoneme alphabet="x-misaki" ph="tɛlɪfɛn">telephone</phoneme>
```

**Attributes:**

| Attribute | Values | Default | Notes |
|-----------|--------|---------|-------|
| `alphabet` | ipa, x-misaki | - | Phonetic alphabet |
| `ph` | phonetic string | - | Phoneme sequence |

---

### `<voice>`

Switches to a different voice.

```xml
Default voice. <voice name="af_bella">Using a different voice.</voice>
```

**Attributes:**

| Attribute | Values | Default | Notes |
|-----------|--------|---------|-------|
| `name` | Voice ID | - | Voice to use |

**Available Voices:**
- `af_*` - American English female voices
- `bf_*` - American English male voices
- `af_*_scot` - Scottish female voices
- And many more regional variants

---

### `<background>` (Custom)

Adds ambient background noise to speech.

```xml
<background type="coffee_shop" volume="0.3">
  Welcome to the cafe. <break time="2s"/> Your order is ready.
</background>
```

**Attributes:**

| Attribute | Values | Default | Notes |
|-----------|--------|---------|-------|
| `type` | coffee_shop, office, nature, rain, wind, white_noise, pink_noise, brown_noise | - | Background type |
| `volume` | 0.0 - 1.0 | 0.3 | Background volume |
| `fade_in` | seconds | 0.5 | Fade in duration |
| `fade_out` | seconds | 0.5 | Fade out duration |

---

## Limitations & Known Issues

### Kokoro Engine Integration

1. **Prosody Conflicts:** Kokoro has native prosody handling that may conflict with aggressive SSML prosody. We limit prosody marking to avoid SSML corruption.

2. **Break Tag Safety:** Break tags are handled carefully to prevent timing issues with Kokoro's internal timing.

3. **Nested Tags:** Deeply nested SSML tags may cause unexpected behavior. Keep nesting shallow.

### Text Processing

1. **SSML in Text Normalization:** The text processing pipeline may modify SSML tags if not properly escaped. Use `<sub>` for special characters.

2. **Unicode Normalization:** Some Unicode characters may be normalized, affecting phoneme accuracy.

3. **Empty Tags:** Empty `<emphasis>` or `<prosody>` tags may be removed during processing.

---

## Best Practices

### ✅ Recommended

```xml
<!-- Use word-level emphasis for clarity -->
<emphasis level="strong">Important</emphasis>

<!-- Use breaks sparingly -->
<break time="0.2s"/>

<!-- Use say-as for numbers and dates -->
<say-as interpret="date">2024-01-15</say-as>
```

### ⚠️ Use Caution

```xml
<!-- Avoid deep nesting -->
<voice name="af_heart">
  <emphasis level="moderate">
    <!-- Keep nesting to 2-3 levels max -->
  </emphasis>
</voice>

<!-- Avoid conflicting prosody -->
<prosody rate="fast">
  <prosody rate="slow">
    <!-- Conflicting rates - use only one -->
  </prosody>
</prosody>
```

### ❌ Not Recommended

```xml
<!-- Avoid complex nesting -->
<nested><tags><are><dangerous></dangerous></are></tags></nested>

<!-- Avoid empty tags -->
<emphasis level="strong"></emphasis>

<!-- Avoid overlapping tags -->
<voice name="a">Text <emphasis>b</voice> more text</emphasis>
```

---

## Examples

### Formal Announcement

```xml
<speak>
  <emphasis level="strong">Attention passengers.</emphasis>
  <break time="0.5s"/>
  Flight <say-as interpret="cardinal">2347</say-as> to New York
  is now boarding at gate <say-as interpret="ordinal">12</say-as>.
</speak>
```

### Conversational

```xml
<speak>
  <prosody rate="medium">
    Hey there! <break time="0.3s"/>
    How are you doing <emphasis level="moderate">today</emphasis>?
  </prosody>
</speak>
```

### Background Ambiance

```xml
<speak>
  <voice name="af_heart">
    <background type="rain" volume="0.2">
      It's raining outside. <break time="1s"/>
      Stay dry and warm.
    </background>
  </voice>
</speak>
```

---

## API Usage

### REST API

```bash
curl -X POST http://localhost:8354/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "<speak><emphasis level=\"strong\">Hello</emphasis> world!</speak>",
    "voice": "af_heart",
    "ssml": true
  }'
```

### Python SDK

```python
from litetts import LiteTTS

client = LiteTTS()
audio = client.speech(
    input="<speak><emphasis level='strong'>Hello</emphasis> world!</speak>",
    voice="af_heart",
    ssml=True
)
```

---

## See Also

- [Text Processing](TEXT_PROCESSING.md) - How text is normalized before synthesis
- [Voice System](VOICES.md) - Available voices and voice blending
- [API Reference](../api/API_REFERENCE.md) - Full API documentation
