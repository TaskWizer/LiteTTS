# LiteTTS Voice Cloning Studio

A web-based interface for creating custom voice profiles using the LiteTTS API.

## Features

- **Audio Upload**: Support for WAV, MP3, and M4A files up to 50MB
- **Voice Analysis**: Extract voice characteristics from uploaded audio samples
- **Voice Testing**: Generate test audio using the cloned voice
- **Interactive Workflow**: Step-by-step guided process
- **Real-time Progress**: Visual feedback during processing
- **Responsive Design**: Works on desktop and mobile devices

## Usage

1. **Upload Audio Sample**
   - Click the upload area or drag and drop an audio file
   - Supported formats: WAV, MP3, M4A
   - Recommended: 10-30 seconds of clear speech
   - Maximum file size: 50MB

2. **Voice Analysis**
   - Enter a name for your custom voice
   - Optionally add a description
   - Click "Analyze Voice" to extract voice characteristics

3. **Test Generated Voice**
   - Enter test text to generate with your cloned voice
   - Click "Generate Test Audio" to create a sample
   - Listen to the result and adjust if needed

4. **Save Voice Profile**
   - Review your voice profile information
   - Save the voice for future use
   - Start over with a new audio sample if desired

## Technical Implementation

### Frontend
- Pure HTML5, CSS3, and JavaScript
- Responsive design with CSS Grid and Flexbox
- Drag-and-drop file upload
- Audio playback controls
- Progress indicators and status messages

### Backend Integration
- Uses the existing LiteTTS `/v1/audio/speech` API endpoint
- File upload handling for voice samples
- Voice analysis and profile creation
- Audio generation with custom voices

### File Structure
```
static/examples/voice-cloning/
├── index.html          # Main application interface
├── README.md          # This documentation
└── assets/            # Additional assets (if needed)
```

## API Endpoints Used

- `POST /v1/audio/speech` - Generate speech with selected voice
- `POST /v1/voices/analyze` - Analyze uploaded voice sample (planned)
- `POST /v1/voices/create` - Create custom voice profile (planned)
- `GET /v1/voices/custom` - List custom voice profiles (planned)

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Security Considerations

- File type validation on upload
- File size limits (50MB max)
- Audio format verification
- Secure file handling

## Future Enhancements

- **Real Voice Cloning**: Integration with actual voice cloning models
- **Voice Training**: Multi-sample training for better quality
- **Voice Editing**: Fine-tune voice characteristics
- **Voice Library**: Manage multiple custom voices
- **Export Options**: Download voice profiles
- **Batch Processing**: Process multiple samples at once

## Development Notes

This is currently a demonstration interface that shows the workflow for voice cloning. The actual voice cloning functionality requires:

1. **Voice Analysis Backend**: Extract voice embeddings from audio samples
2. **Voice Model Training**: Train or fine-tune TTS models with custom voices
3. **Voice Storage**: Persistent storage for custom voice profiles
4. **Voice Synthesis**: Generate speech using custom voice embeddings

## Getting Started

1. Ensure LiteTTS server is running
2. Navigate to `/static/examples/voice-cloning/` in your browser
3. Follow the step-by-step workflow to create custom voices

## Support

For issues or questions about the Voice Cloning Studio:
- Check the LiteTTS documentation
- Review the browser console for error messages
- Ensure audio files meet the format and size requirements
