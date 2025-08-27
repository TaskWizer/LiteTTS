# chunk_processor.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Chunk processor for handling long text inputs


## Class: TextChunk

Represents a chunk of text for processing

## Class: ChunkProcessor

Processes long text by splitting into manageable chunks

### __init__()

### chunk_text()

Split text into processable chunks

### _split_by_paragraphs()

Split text by paragraph boundaries

### _chunk_paragraph()

Chunk a single paragraph

### _find_best_split_point()

Find the best point to split text

### _ends_with_sentence_boundary()

Check if text ends with a sentence boundary

### _calculate_pause_duration()

Calculate pause duration after chunk

### process_chunks_to_audio()

Process text chunks and combine into single audio

### estimate_processing_time()

Estimate total processing time for chunks

### get_chunk_statistics()

Get statistics about the chunks

### _estimate_audio_duration()

Estimate total audio duration

### optimize_chunks()

Optimize chunks for better synthesis

### _optimize_chunk_text()

Optimize individual chunk text

### validate_chunks()

Validate chunks and return list of issues

### merge_small_chunks()

Merge chunks that are too small

