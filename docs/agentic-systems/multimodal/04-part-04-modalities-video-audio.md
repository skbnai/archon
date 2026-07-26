---
title: "Part 04 — Video & Audio Intelligence"
doc_type: guide
domain: agentic-systems
status: current
topic_id: part-04-modalities-video-audio
date: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - docs/multimodal-ai/04-part-04-modalities-video-audio.md
---

# Part 04 — Video & Audio Intelligence

A comprehensive technical deep dive into video understanding and audio intelligence systems, covering architectures, ASR engines, enterprise use cases, and security-critical deployment patterns.

> **Audience:** Principal AI Architects, ML Engineers, Enterprise Solution Architects
> **Coverage:** Video Understanding · Audio Intelligence · ASR · Speaker Diarization · Surveillance · Predictive Maintenance
> **As of:** July 2026

---

## Video Understanding Capabilities

### Event Detection

Modern video understanding models support three core event detection tasks:

- *Action recognition*: classify human activities — sports gestures, assembly-line motions, security postures
- *Anomaly detection*: identify deviations from learned baseline behaviour — loitering, abandoned objects, unusual crowd flow
- *Pose estimation*: extract skeletal joint coordinates per frame using models such as MediaPipe, OpenPose, or ViTPose

Action recognition has moved from CNN-based two-stream networks (spatial + optical flow) to transformer architectures that model long-range temporal dependencies with self-attention over token sequences of frames.

### Temporal Reasoning

Long video understanding requires the model to maintain narrative coherence across minutes or hours of content. Key capabilities include:

- *Causal chain detection*: identifying the sequence of events that led to an outcome (e.g., equipment failure root cause)
- *Narrative understanding*: tracking objects, identities, and plot threads across scenes
- *Temporal grounding*: answering "what happened at timestamp T?" against a video index

### Surveillance Applications

Surveillance deployments demand low-latency inference on edge hardware:

- *Perimeter monitoring*: line-crossing detection, zone entry/exit alerts
- *Crowd analytics*: density estimation, flow direction, panic detection
- *Vehicle tracking*: license plate recognition, make/model classification, trajectory analysis

### Summarization

Summarization pipelines produce navigable artifacts from long recordings:

- *Key frame extraction*: select representative frames using scene-change detection or semantic clustering
- *Highlight detection*: identify peak-engagement or high-energy segments
- *Chapter generation*: segment video into titled sections for meeting recordings, lectures, or sports broadcasts

### Frame Sampling Strategies

| Strategy | Mechanism | Best For |
|----------|-----------|----------|
| Uniform | Fixed interval (1 fps, 2 fps) | Short clips, budget-constrained inference |
| Scene-change | Detect histogram or optical-flow shift | Narrative content, broadcast |
| Adaptive | Higher density around detected events | Surveillance, anomaly detection |
| Keyframe | I-frames only from video codec | Fast scrubbing, thumbnail generation |

### Clip Embeddings

- *CLIP-based*: frame-level CLIP embeddings averaged or max-pooled over a clip
- *VideoMAE*: masked autoencoder pre-trained on video — strong spatiotemporal features
- *InternVideo*: dual-encoder (video + text) trained on large-scale video-text pairs
- *S3D*: separable 3D convolutions for efficient clip-level embeddings

### Long Video Memory Strategies

Long video (&gt;30 minutes) exceeds the context window of any current VLM. Three approaches manage this:

- *Sliding window*: process overlapping chunks; maintain a summary buffer across windows
- *Hierarchical summarization*: chunk → clip summary → segment summary → video summary
- *StreamingLLM approach*: retain attention sinks (first few tokens) + recent window; evict middle tokens

### Action Recognition Architectures

- *Two-stream networks*: separate spatial (RGB) and temporal (optical flow) CNNs fused at late layers
- *Transformer-based*: Video Swin Transformer, TimeSformer — treat frames as token sequences
- *Video diffusion*: generative models that can interpolate and hallucinate missing frames for data augmentation

---

## Video Processing Architecture

### Ingestion Pipeline

```text
Source → Transcoding → Container Parsing → Frame Extraction → Embedding → Index
```

Key components:

- *Transcoding*: normalise to H.264/H.265 at target resolution and frame rate using FFmpeg
- *Container formats*: MP4 (broadest compatibility), MKV (multiple audio tracks, subtitles), WebM (browser-native)
- *Codec handling*: detect codec (H.264, H.265, AV1, VP9) before decoding; GPU-accelerated decode with NVDEC/VAAPI

### GPU Memory Management

Long video processing requires careful memory scheduling:

- Stream frames in batches; process batch → embed → release GPU memory before next batch
- Use mixed-precision inference (FP16) to double effective GPU memory capacity
- For distributed inference, partition video into segments and route each to a separate worker

### Chunking and Overlap

- Overlap adjacent chunks by 2–5 seconds to avoid boundary artefacts in event detection
- Store chunk metadata (start timestamp, end timestamp, scene ID) alongside embeddings for temporal retrieval

---

## Audio Intelligence Deep Dive

### Speech Categories

| Category | Characteristics | Key Challenges |
|----------|----------------|----------------|
| Conversational | Informal, overlapping speech, filler words | Diarization, spontaneous speech |
| Broadcast | Scripted, high SNR, single speaker | Minimal — well-solved domain |
| Medical | Jargon-heavy, abbreviations, dictation | Domain vocabulary, privacy (HIPAA) |
| Legal | Formal, multi-party, evidentiary | Verbatim accuracy, speaker attribution |
| Call center | Noisy channels, telephony codec artifacts | Telephony ASR, emotion detection |

### Environmental Sounds

- *Industrial machinery*: bearing degradation, imbalance, cavitation — distinctive spectral signatures
- *HVAC*: compressor cycling, refrigerant leaks, filter blockages
- *Vehicle diagnostics*: engine knock, exhaust anomalies, brake squeal

### Music Analysis

- *Genre classification*: CNN or transformer over mel-spectrogram
- *Tempo estimation*: beat tracking with librosa or madmom
- *Instrument separation*: source separation with Demucs or Spleeter

### Machine Sounds for Predictive Maintenance

Normal machine audio establishes a spectral baseline. Anomalies manifest as:

- New frequency components (bearing race defects appear at BPFO/BPFI frequencies)
- Amplitude modulation (imbalance causes once-per-revolution modulation)
- Broadband noise increase (cavitation, turbulence)

---

## ASR (Automatic Speech Recognition) Landscape

### Whisper Family

OpenAI Whisper is an encoder-decoder transformer trained on 680K hours of multilingual audio:

- *Whisper v2*: 1.5B parameters; strong multilingual performance
- *Whisper v3*: improved CER on low-resource languages; better long-form transcription
- *Whisper large-v3-turbo*: 4x inference speedup via pruning; 8-language optimisation
- *Enterprise trade-offs*: open-source flexibility vs. no SLA, no real-time streaming, compute cost at scale

### Cloud ASR Services

- *Azure Speech*: real-time and batch modes; custom acoustic and language models; integrated speaker diarization
- *AWS Transcribe*: call analytics, medical transcription specialty model, custom vocabulary
- *Google Speech-to-Text*: enhanced phone call model, automatic punctuation, word-level confidence

### Speaker Diarization

Diarization answers "who spoke when?" — a prerequisite for call analytics and meeting summarisation:

- *pyannote.audio*: SOTA open-source pipeline; speaker embedding + segmentation + clustering
- *AWS Transcribe*: built-in diarization; up to 10 speakers; returns speaker labels per word
- *Azure Speaker Recognition*: diarization integrated into batch transcription
- *Nvidia NeMo*: MarbleNet VAD + TitaNet speaker embeddings; strong on noisy call center audio

### Speaker Identification vs Verification

- *Identification*: 1:N match — "which enrolled speaker is this?"
- *Verification*: 1:1 match — "is this the claimed speaker?" Returns accept/reject at a threshold

### Language Identification

- Multilingual models (Whisper, MMS) produce a language probability vector before transcription
- Dedicated LangID models (CLD3, fastText) are faster for routing decisions before ASR

### Keyword Spotting

- *Always-on*: low-power embedded model running continuously on edge device (wake word detection)
- *Wake words*: "Hey Siri", "Alexa" — optimised for false-positive minimisation
- *Compliance monitoring*: detect prohibited phrases in call center recordings (price-fixing language, misleading claims)

### Emotion Detection

- *Valence/arousal model*: 2D circumplex model; predict positive/negative valence and high/low arousal from prosody
- *Clinical applications*: depression screening, pain assessment, cognitive decline indicators
- Input features: MFCCs, pitch contour, energy, speaking rate, jitter, shimmer

### Intent Detection from Audio

- *IVR routing*: classify caller intent from first utterance ("pay bill", "cancel service", "speak to agent")
- *Call center routing*: detect frustration → escalate; detect technical query → route to Tier 2
- Architecture: ASR → text → intent classifier; or end-to-end audio → intent (SpeechBrain, wav2vec2)

---

## ASR Engine Comparison Matrix

| Engine | WER (EN) | Real-Time | Languages | Diarization | Cost | Enterprise SLA |
|--------|----------|-----------|-----------|-------------|------|----------------|
| Whisper large-v3 | ~2.5% | No (batch) | 99 | External | Self-hosted | None |
| Whisper large-v3-turbo | ~3.1% | Near-RT | 8 optimised | External | Self-hosted | None |
| Azure Speech | ~3.5% | Yes | 100+ | Built-in | $1/hr audio | 99.9% |
| AWS Transcribe | ~4.0% | Yes | 100+ | Built-in | $0.024/min | 99.9% |
| Google STT | ~3.8% | Yes | 125+ | Built-in | $0.016/min | 99.9% |
| AssemblyAI | ~3.2% | Yes | 99 | Built-in | $0.012/min | 99.5% |
| Deepgram Nova-2 | ~2.8% | Yes | 35 | Built-in | $0.0043/min | 99.9% |

## Video Understanding Model Comparison

| Model | Context Length | Modalities | Cost | Diarization | Enterprise Ready |
|-------|---------------|------------|------|-------------|-----------------|
| Video-LLaMA 2 | ~256 frames | Video + Text | Open-source | No | Self-hosted |
| InternVideo 2 | ~8 min clips | Video + Text + Audio | Open-source | No | Self-hosted |
| VideoChat 2 | ~128 frames | Video + Text | Open-source | No | Self-hosted |
| GPT-4o Vision | ~50 frames/call | Image + Text | $0.01/img | No | Yes (Azure) |
| Gemini 1.5 Pro | 1 hour video | Video + Audio + Text | $3.5/1M tokens | No | Yes (GCP) |

---

**This is Part 1 of 2. [Continue with Part 2 →](pathname:///archon/agentic-systems/multimodal/parts/04-part-04-modalities-video-audio-part2) for Enterprise Pipelines, Use Cases, and Interview Examples.**

## Related

- [Part 3 — Image & Document Intelligence](03-part-03-modalities-image-document.md) — the previous section in this series.
- [Part 07 — Security & Threat Taxonomy for Multimodal AI](07-part-07-security-threats.md) — the next section in this series.
