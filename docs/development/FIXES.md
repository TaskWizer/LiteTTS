Please complete the following comprehensive TTS system maintenance and analysis tasks:

## 1. OpenWebUI Integration Fix
- Investigate and fix the TTS voice dropdown functionality in OpenWebUI that is currently not working with this API
- Ensure proper voice selection and API communication between OpenWebUI and the TTS service
- Test the integration end-to-end to confirm voice selection works correctly

## 2. Project Structure Cleanup and Organization
Reorganize the project structure to follow proper conventions:

### File and Folder Cleanup:
- **Remove all temporary/test files from root directory** including:
  - Random audio files (*.wav, *.mp3) generated during testing
  - Any temporary folders created during development
  - Test output files that should be in designated test directories
- **Consolidate test directories**: Move all test-related content to either `docs/tests/` or `kokoro/tests/`
- **Organize logs**: Move all log files to `docs/logs/` directory
- **Merge script directories**: Move contents of `./scripts/` into `./kokoro/scripts/` and remove the redundant `./scripts/` folder
- **Relocate infrastructure folders**: Move the following folders from root into the `kokoro/` directory:
  - `./monitoring/` → `./kokoro/monitoring/`
  - `./certs/` → `./kokoro/certs/`
  - `./nginx/` → `./kokoro/nginx/`
  - Any other infrastructure-related folders currently in root

### Technical Requirements:
- **Avoid symbolic links** - use direct file organization instead
- **Clean up temporary folders** and remove unnecessary files
- **Audit the entire system** for orphaned files and unused directories

## 3. CLI Configuration Enhancement
Add command-line configuration loading capability:
- Implement `--config /path/to/json_file.json` parameter support
- Allow users to specify custom configuration files at runtime
- Ensure this works alongside existing config.json loading with proper precedence

## 4. Comprehensive Model Benchmark Analysis
Create a complete performance benchmark comparing ALL available model variants with detailed statistics:

### Required Model Variants to Test:
```
"available_variants": [
  "model.onnx",
  "model_f16.onnx",
  "model_q4.onnx",
  "model_q4f16.onnx",
  "model_q8f16.onnx",
  "model_quantized.onnx",
  "model_uint8.onnx",
  "model_uint8f16.onnx"
]
```

### Benchmark Metrics Required:
For each model variant, measure and report:
- **RTF (Real-Time Factor)** - ratio of synthesis time to audio duration
- **Latency** - time from request to first audio output
- **Total Generation Time** - complete processing time for standard test phrases
- **Memory Usage** - RAM consumption during inference
- **CPU Utilization** - processor usage during synthesis
- **Model File Size** - disk space requirements
- **Audio Quality Metrics** - if measurable (MOS scores, etc.)
- **Throughput** - requests per second capability

### Output Format:
- Provide results in **markdown format only**
- Include comparison tables with all metrics
- Add recommendations for different use cases (real-time vs quality vs resource-constrained)
- Include test methodology and hardware specifications used
- Provide clear performance rankings and trade-off analysis

## 5. System Audit
Perform a final system audit to ensure:
- All cleanup tasks are completed
- No orphaned files remain
- Project structure follows best practices
- All functionality works correctly after reorganization
- Documentation reflects the new structure

Enable/disable "" seems to work, but disabling the entire feature seems to do nothing:
  "text_processing": {
    "enabled": false, but "expand_contractions": true, still expands contractions.
And for "expand_contractions" I have to start and re-run the service because hot loading seems to detect but not reflect the updates made to the config.json.

Being that these issues exist for this setting, there are likely similiar issues. Please do a system wide end-to-end audit of everything and enhance this in general. Lets try to reduce and even eliminate all the bugs and edge cases please.
