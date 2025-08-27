# 🎛️ SSML Guide - Advanced Speech Synthesis Markup Language

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../FEATURES.md) | [Configuration](../CONFIGURATION.md) | [Performance](../PERFORMANCE.md) | [Monitoring](../MONITORING.md) | [Testing](../TESTING.md) | [Troubleshooting](../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../DEPENDENCIES.md) | [Quick Start](QUICK_START_COMMANDS.md) | [Docker Deployment](DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../api/API_REFERENCE.md) | [Development](../development/README.md) | [Voice System](../voices/README.md) | [Watermarking](../WATERMARKING.md)

**Project:** [Changelog](../CHANGELOG.md) | [Roadmap](../ROADMAP.md) | [Contributing](../CONTRIBUTIONS.md) | [Beta Features](../BETA_FEATURES.md)

---

**Master advanced speech synthesis with SSML for natural, expressive text-to-speech**

## 🎯 Overview

Speech Synthesis Markup Language (SSML) allows you to control various aspects of speech synthesis including pronunciation, volume, pitch, rate, and background audio. The Kokoro ONNX TTS API supports a rich set of SSML features for creating engaging audio experiences.

## 🚀 Quick Start

### **Basic SSML Structure**
```xml
<speak>
  Your text content goes here
</speak>
```

### **Simple Example**
```bash
curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "<speak>Hello, <break time=\"1s\"/> world!</speak>", "voice": "af_heart"}' \
  --output ssml_example.mp3
```

## 🎵 Background Audio

### **Available Background Types**
- `rain` - Gentle rain sounds
- `ocean` - Ocean waves
- `forest` - Forest ambience
- `cafe` - Coffee shop atmosphere
- `library` - Quiet library sounds
- `fireplace` - Crackling fireplace
- `wind` - Gentle wind sounds
- `thunder` - Distant thunder
- `birds` - Bird songs
- `city` - Urban ambience

### **Background Audio Examples**
```xml
<!-- Rain background -->
<speak>
  <background type="rain" volume="20">
    It's a rainy day outside. Perfect weather for staying indoors.
  </background>
</speak>

<!-- Ocean background -->
<speak>
  <background type="ocean" volume="15">
    The waves crash gently against the shore.
  </background>
</speak>

<!-- Multiple backgrounds -->
<speak>
  <background type="forest" volume="10">
    Walking through the peaceful forest,
  </background>
  <break time="1s"/>
  <background type="birds" volume="25">
    you can hear the birds singing in the trees.
  </background>
</speak>
```

## ⏸️ Pauses and Breaks

### **Break Elements**
```xml
<!-- Time-based breaks -->
<speak>
  First sentence.
  <break time="500ms"/>
  After a half-second pause.
  <break time="2s"/>
  After a two-second pause.
</speak>

<!-- Strength-based breaks -->
<speak>
  Sentence one.
  <break strength="weak"/>
  Sentence two.
  <break strength="medium"/>
  Sentence three.
  <break strength="strong"/>
  Final sentence.
</speak>
```

### **Break Strength Values**
- `none` - No pause
- `x-weak` - Very brief pause
- `weak` - Brief pause
- `medium` - Medium pause (default)
- `strong` - Long pause
- `x-strong` - Very long pause

## 🎭 Voice Modulation

### **Parenthetical Content**
```xml
<speak>
  This is normal speech.
  <parenthetical>This is whispered aside content.</parenthetical>
  Back to normal speech.
</speak>
```

### **Emphasis**
```xml
<speak>
  This is <emphasis level="strong">very important</emphasis> information.
  <emphasis level="moderate">Moderately important</emphasis> details.
  <emphasis level="reduced">Less important</emphasis> notes.
</speak>
```

### **Prosody Control**
```xml
<speak>
  <prosody rate="slow" pitch="low" volume="soft">
    This is spoken slowly, in a low pitch, and softly.
  </prosody>
  
  <prosody rate="fast" pitch="high" volume="loud">
    This is spoken quickly, in a high pitch, and loudly!
  </prosody>
</speak>
```

## 🔊 Volume Control

### **Volume Levels**
- `silent` - No sound
- `x-soft` - Very quiet
- `soft` - Quiet
- `medium` - Normal volume (default)
- `loud` - Loud
- `x-loud` - Very loud

### **Volume Examples**
```xml
<speak>
  <prosody volume="soft">This is whispered</prosody>
  <prosody volume="medium">This is normal</prosody>
  <prosody volume="loud">This is emphasized!</prosody>
</speak>
```

## 🎼 Pitch and Rate Control

### **Pitch Control**
```xml
<speak>
  <prosody pitch="x-low">Very low pitch</prosody>
  <prosody pitch="low">Low pitch</prosody>
  <prosody pitch="medium">Normal pitch</prosody>
  <prosody pitch="high">High pitch</prosody>
  <prosody pitch="x-high">Very high pitch</prosody>
  
  <!-- Relative pitch changes -->
  <prosody pitch="+20%">20% higher than normal</prosody>
  <prosody pitch="-15%">15% lower than normal</prosody>
</speak>
```

### **Rate Control**
```xml
<speak>
  <prosody rate="x-slow">Very slow speech</prosody>
  <prosody rate="slow">Slow speech</prosody>
  <prosody rate="medium">Normal speed</prosody>
  <prosody rate="fast">Fast speech</prosody>
  <prosody rate="x-fast">Very fast speech</prosody>
  
  <!-- Relative rate changes -->
  <prosody rate="150%">50% faster than normal</prosody>
  <prosody rate="75%">25% slower than normal</prosody>
</speak>
```

## 📚 Practical Examples

### **Weather Report**
```xml
<speak>
  <background type="wind" volume="15">
    Today's weather forecast:
    <break time="500ms"/>
    <prosody rate="slow">
      Morning temperatures will be around 
      <emphasis level="moderate">65 degrees</emphasis>,
    </prosody>
    <break time="300ms"/>
    with <background type="rain" volume="20">
      light rain expected in the afternoon.
    </background>
  </background>
</speak>
```

### **Storytelling**
```xml
<speak>
  <background type="forest" volume="10">
    Once upon a time, in a deep, dark forest,
    <break time="1s"/>
    <prosody pitch="low" rate="slow">
      there lived a mysterious creature.
    </prosody>
    <break time="500ms"/>
    <background type="birds" volume="20">
      Every morning, the birds would sing,
    </background>
    <parenthetical>though none dared to venture too close.</parenthetical>
  </background>
</speak>
```

### **Presentation**
```xml
<speak>
  Welcome to our quarterly review.
  <break time="1s"/>
  
  <emphasis level="strong">First</emphasis>, let's look at our sales figures.
  <break time="500ms"/>
  
  <prosody rate="slow">
    Revenue increased by <emphasis level="moderate">twenty-five percent</emphasis>
    compared to last quarter.
  </prosody>
  
  <break time="1s"/>
  
  <prosody volume="loud">
    This is our best performance yet!
  </prosody>
</speak>
```

### **Meditation Guide**
```xml
<speak>
  <background type="ocean" volume="15">
    <prosody rate="x-slow" volume="soft">
      Take a deep breath in
      <break time="3s"/>
      and slowly breathe out.
      <break time="3s"/>
      
      Feel the tension leaving your body
      <break time="2s"/>
      as you relax completely.
    </prosody>
  </background>
</speak>
```

### **News Broadcast**
```xml
<speak>
  <background type="city" volume="10">
    Good evening, I'm your news anchor.
    <break time="500ms"/>
    
    <emphasis level="strong">Breaking news:</emphasis>
    <prosody rate="fast">
      Local technology company announces major breakthrough
      in artificial intelligence.
    </prosody>
    
    <break time="1s"/>
    
    <prosody rate="slow" pitch="low">
      We'll have more details after this short break.
    </prosody>
  </background>
</speak>
```

## 🎯 Best Practices

### **1. Natural Flow**
```xml
<!-- Good: Natural pauses -->
<speak>
  Hello there! <break time="300ms"/> How are you doing today?
</speak>

<!-- Avoid: Too many artificial pauses -->
<speak>
  Hello <break time="1s"/> there <break time="1s"/> how <break time="1s"/> are <break time="1s"/> you?
</speak>
```

### **2. Appropriate Volume Levels**
```xml
<!-- Good: Subtle background audio -->
<speak>
  <background type="cafe" volume="15">
    Let's discuss the project over coffee.
  </background>
</speak>

<!-- Avoid: Overwhelming background -->
<speak>
  <background type="thunder" volume="80">
    This is hard to hear over the thunder.
  </background>
</speak>
```

### **3. Consistent Voice Characteristics**
```xml
<!-- Good: Consistent character voice -->
<speak>
  <prosody pitch="high" rate="fast">
    "I'm so excited!" she exclaimed.
    <break time="500ms"/>
    "This is the best day ever!"
  </prosody>
</speak>
```

### **4. Meaningful Emphasis**
```xml
<!-- Good: Emphasis on important words -->
<speak>
  The <emphasis level="strong">deadline</emphasis> is 
  <emphasis level="moderate">tomorrow</emphasis> at noon.
</speak>

<!-- Avoid: Over-emphasis -->
<speak>
  <emphasis level="strong">The</emphasis> 
  <emphasis level="strong">deadline</emphasis> 
  <emphasis level="strong">is</emphasis> 
  <emphasis level="strong">tomorrow</emphasis>
</speak>
```

## 🧪 Testing SSML

### **Test Different Elements**
```bash
# Test background audio
curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "<speak><background type=\"rain\" volume=\"20\">Testing rain background</background></speak>", "voice": "af_heart"}' \
  --output test_background.mp3

# Test prosody
curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "<speak><prosody rate=\"slow\" pitch=\"low\">Testing slow, low speech</prosody></speak>", "voice": "af_heart"}' \
  --output test_prosody.mp3

# Test breaks
curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "<speak>Before break <break time=\"2s\"/> after break</speak>", "voice": "af_heart"}' \
  --output test_breaks.mp3
```

### **Validation**
```bash
# Validate SSML syntax (basic check)
echo '<speak><background type="rain" volume="20">Test</background></speak>' | xmllint --format -
```

## 🎨 Creative Applications

### **Interactive Stories**
- Use different voices for characters
- Add environmental sounds
- Create dramatic pauses
- Vary speech patterns for emotion

### **Educational Content**
- Emphasize key concepts
- Use pauses for comprehension
- Add relevant background sounds
- Vary pace for different sections

### **Meditation and Relaxation**
- Slow, soft speech
- Calming background sounds
- Long pauses for reflection
- Gentle volume levels

### **Podcasts and Audio Content**
- Professional pacing
- Clear emphasis on important points
- Appropriate background ambience
- Natural conversation flow

## 🔗 Related Resources

- [Voice Showcase](../voices/README.md) - Choose the right voice for your SSML
- [Quick Start Guide](../QUICK_START_COMMANDS.md) - Basic API usage
- [OpenWebUI Integration](OPENWEBUI-INTEGRATION.md) - Use SSML in chat interfaces
- [API Reference](../FEATURES.md) - Complete API documentation

## 📝 SSML Reference

### **Supported Elements**
- `<speak>` - Root element
- `<break>` - Pauses and breaks
- `<emphasis>` - Text emphasis
- `<prosody>` - Voice characteristics
- `<background>` - Background audio
- `<parenthetical>` - Whispered asides

### **Attributes**
- `time` - Duration (ms, s)
- `strength` - Break strength
- `level` - Emphasis level
- `rate` - Speech rate
- `pitch` - Voice pitch
- `volume` - Audio volume
- `type` - Background audio type

---

**🎭 Master SSML** to create engaging, natural-sounding audio experiences with the Kokoro ONNX TTS API! 🎵✨
