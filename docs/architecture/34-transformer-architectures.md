---
title: 'Transformer Architecture: Frontier Models Deep Dive'
date_created: 2026-07-17
last_reviewed: 2026-07-17
status: current
source_type: converted-html
doc_type: reference-architecture
domain: architecture
topic_id: transformer-architectures
maturity: expert
personas: [architect, research-engineer, ml-engineer]
tags: [transformers, llm, ai-foundations, architecture]
supersedes: [docs/ai-foundations/transformer_architectures.md]
covers_version: "2026"
---

# Transformer Architecture: Frontier Models Deep Dive

A rigorous technical comparison of how GPT-4, Claude, Gemini, LLaMA, Mistral, Grok, and others build upon — and diverge from — the original Transformer paradigm.

## The Original Transformer: Core Concepts

The "Attention Is All You Need" paper (Vaswani et al., 2017) introduced the Transformer — a sequence-to-sequence model that dispensed with recurrence entirely. Every frontier model today is a descendant of this architecture, but each has made crucial design choices that differentiate them dramatically.

### Self-Attention

Every token attends to every other token simultaneously. Three learnable projections — Queries (Q), Keys (K), Values (V) — determine which tokens are relevant to which. The formula: `Attention(Q,K,V) = softmax(QKᵀ/√dₖ)·V`

The scaling by √dₖ prevents extremely small gradients in the softmax from large dot products. This is the core insight — not the architecture itself, but the ability to learn _arbitrary_ relationships between any positions.

### Multi-Head Attention

Instead of one attention pass, the model runs h attention heads in parallel, each learning different relationship types. Syntactic, semantic, positional, and co-reference relationships can all be captured simultaneously. Outputs are concatenated and projected: `MultiHead = Concat(head₁...headₕ)·W°`

### Feed-Forward Network

After attention, each position independently passes through a two-layer MLP: `FFN(x) = max(0, xW₁ + b₁)W₂ + b₂`. This is where most of the model's "knowledge storage" lives — each FFN neuron acts like a memory slot. Modern variants replace ReLU with SwiGLU or GeLU.

### Residual Connections & LayerNorm

Each sub-layer is wrapped with a residual connection: `output = LayerNorm(x + SubLayer(x))`. Frontier models diverge here: some use Pre-Norm (normalize before attention), others Post-Norm. Pre-Norm dramatically stabilizes training of very deep networks — it's now standard.

### Positional Encoding

Transformers are inherently permutation-invariant — they don't know token order. Original: fixed sinusoidal encodings. Modern: **Rotary Position Embedding (RoPE)** encodes relative positions directly into Q/K matrices via rotation, enabling extrapolation to longer sequences. **ALiBi** adds a learned bias. This choice massively impacts context length capability.

### Causal (Decoder-Only) Masking

All modern LLMs use decoder-only architectures with causal masking — each token can only attend to tokens that came before it. This allows efficient autoregressive generation: generate one token, append it to context, generate the next. The masking is implemented as a lower-triangular attention mask.

**Key Insight** The shift from Encoder-Decoder to Decoder-Only was the architectural decision that enabled scale. Decoder-only models are simpler, train faster, and generalize better to generation tasks — but at the cost of bidirectional understanding. Every frontier model from GPT-2 onward uses decoder-only.

## Attention Mechanism Evolution

The attention mechanism has evolved significantly since 2017. The core compute bottleneck is that full self-attention scales as `O(n²)` in sequence length — 100k tokens means 10 billion attention computations per layer. Modern models address this differently.

### MHA → MQA → GQA

**Multi-Head Attention (MHA):** h independent Q, K, V heads. Maximum expressiveness, maximum memory.

**Multi-Query Attention (MQA):** One shared K, V pair across all Q heads. 8× less KV cache memory, faster inference, slight quality drop.

**Grouped-Query Attention (GQA):** G groups of K, V pairs shared across multiple Q heads. Best balance — used by LLaMA-3, Mistral, Gemini.

### Flash Attention

Not a different formula — same math, different implementation. FlashAttention tiles the computation to fit in SRAM, avoiding slow HBM reads. Result: 3–4× faster attention, 5–20× less memory, enables much longer contexts without approximation.

FlashAttention-2 and -3 add further optimizations for modern GPU architectures (A100, H100).

### Sparse & Linear Attention

**Sliding Window:** Each token attends to only W neighboring tokens — O(n·W) complexity. Mistral uses this.

**Ring Attention:** Distributes long-context attention across devices — used for million-token contexts.

**Linear Attention:** Approximates attention in O(n) via kernel tricks — used in state-space hybrid models.

## GPT-4 / GPT-4o — OpenAI

GPT-4 / GPT-4o: OpenAI · Closed Source · Mixture-of-Experts (Rumored)

| Parameter | Value | Notes |
|---|---|---|
| Total Parameters | ~1.8T (rumored MoE) | 8 experts, ~220B active per token |
| Architecture | Decoder-Only Transformer | Likely sparse MoE layers |
| Context Window | 128K tokens | GPT-4 Turbo; o-series up to 200K |
| Attention | MHA + FlashAttention | Exact details not disclosed |
| Positional Encoding | RoPE (ALiBi-influenced) | Modified for 128K extension |
| Training Data | >13T tokens | Web + proprietary datasets |

### Architecture Deep Dive

GPT-4's architecture is not officially confirmed, but extensive analysis suggests a **Mixture-of-Experts (MoE)** design with approximately 8 expert FFN sub-networks per layer, with a router selecting 2 active experts per token. This means despite ~1.8T total parameters, only ~220B are "active" per forward pass — making inference cost closer to a dense 220B model.

**MoE Architecture Detail** In MoE layers, the FFN is replaced by E expert networks and a learned router: `output = Σᵢ Router(x)ᵢ · Expertᵢ(x)`. The router learns to specialize experts — some handle code, others handle reasoning, etc. The training challenge is load balancing: preventing all tokens from routing to the same experts via auxiliary loss terms.

**GPT-4o** introduces native multimodality — vision, audio, and text processed within a single model rather than via adapters. This required significant architectural changes to handle different modalities' tokenization (Vision Transformer patch embeddings + audio spectrograms + text BPE).

OpenAI also pioneered **RLHF (Reinforcement Learning from Human Feedback)** — training a reward model on human preferences, then using PPO to align the policy model. GPT-4 extends this with RLAIF and constitutional methods.

#### Strengths

* MoE enables massive capacity at manageable inference cost
* Best-in-class tool use and function calling ecosystem
* Native multimodality (GPT-4o) across text/vision/audio
* Strongest code generation and complex reasoning benchmarks
* Mature API with extensive fine-tuning options
* 128K context with strong retrieval at long ranges

#### Weaknesses

* Completely closed — no architecture transparency
* MoE adds inference serving complexity and latency variance
* Expensive per-token pricing vs. open alternatives
* Occasional refusals inconsistently applied
* Cannot be self-hosted or fine-tuned without API
* Context degradation at very long ranges (needle-in-haystack issues)

## Claude 3.5 / Claude 4 — Anthropic

Claude 3.5 / Claude 4: Anthropic · Closed Source · Constitutional AI

| Parameter | Value | Notes |
|---|---|---|
| Context Window | 200K tokens | Largest among major proprietary models |
| Architecture | Decoder-Only Transformer | Exact topology undisclosed |
| Alignment Method | Constitutional AI (CAI) | Principle-based self-critique loop |
| Positional Encoding | Likely RoPE with interpolation | For 200K context extension |
| Training Approach | SL-CAI → RL-CAI → RLHF | Multi-stage alignment pipeline |
| Modalities | Text + Vision | Via vision encoder adapter |

### Architecture Deep Dive

Claude's most distinctive architectural contribution is not the transformer topology itself but its **Constitutional AI (CAI)** training methodology. CAI replaces pure human preference labeling with a set of principles — a "constitution" — from which the model learns to critique and revise its own outputs.

The training pipeline: (1) Supervised learning on principle-following (SL-CAI), (2) Generating red-team prompts and critiques using the constitution (RLAIF), (3) Training a preference model on principle-ranked outputs, (4) Fine-tuning with RLHF. This creates more consistent alignment than pure RLHF because the reward signal is more principled and less dependent on annotator biases.

**200K Context: How It Works** Achieving 200K tokens requires context length extension techniques applied to RoPE: **Position Interpolation** (scaling down position indices to fit pre-trained range), **YaRN** (Yet Another RoPE extensioN — different scaling for different frequency components), and careful fine-tuning on long-document data. The model also uses FlashAttention-2 for memory efficiency.

Claude 3.5 Sonnet showed that the **scaling laws** for smaller, more carefully trained models can outperform larger, sloppier models. Anthropic invests heavily in training data quality, filtering, and deduplication — matching or beating GPT-4 class performance with a presumably smaller dense model.

Claude's vision capability uses a separate vision encoder (likely a ViT variant) whose outputs are projected into the language model's embedding space — a cross-attention or projection adapter approach rather than native multimodality.

#### Strengths

* 200K context window — best long-document handling
* Constitutional AI gives more principled, consistent alignment
* Exceptional writing quality and nuanced instruction following
* Strong safety properties without excessive refusals
* Excellent for agentic tasks (tool use, multi-step reasoning)
* Best-in-class on many coding benchmarks (SWE-bench)

#### Weaknesses

* Closed source — no fine-tuning or self-hosting
* Vision less integrated than GPT-4o's native multimodality
* No audio modality (vs. GPT-4o)
* Can be overly cautious on ambiguous edge cases
* API availability occasionally constrained by demand

## Gemini 1.5 / 2.0 — Google DeepMind

Gemini 1.5 Pro / 2.0: Google DeepMind · Closed Source · MoE + Native Multimodal

| Parameter | Value | Notes |
|---|---|---|
| Context Window | 1M tokens (1.5 Pro), 2M (1.5 Ultra) | Largest context of any frontier model |
| Architecture | MoE Transformer | Confirmed sparse MoE |
| Attention | Multi-Query + GQA | Critical for 1M context efficiency |
| Positional Encoding | RoPE with specialized extension | Custom scaling for million-token context |
| Modalities | Text, Image, Video, Audio, Code | Trained natively on all modalities |
| Training Infrastructure | TPU v5p clusters | Google's proprietary hardware advantage |

### Architecture Deep Dive

Gemini 1.5 Pro's most dramatic architectural achievement is the **1-million-token context window**. This required solving a genuinely hard engineering problem: attention over 1M tokens at O(n²) complexity is computationally infeasible. Google's solution is a combination of:

#### Ring Attention

Distributes attention computation across TPU cores in a ring topology, each processing a chunk of the sequence and passing KV caches to neighbors. Enables linear scaling in context length across devices.

#### MQA / GQA

Grouped-Query Attention dramatically reduces KV cache memory — critical when a 1M token context would otherwise require hundreds of GB per inference pass.

#### Needle-in-Haystack

Gemini 1.5 Pro achieves near-perfect recall across its full 1M context — a capability that GPT-4 cannot match at these lengths, verified by independent benchmarks.

Gemini's most unique strength is **native multimodality** — unlike models that bolt on vision adapters, Gemini was trained from scratch on interleaved text, images, video, and audio. This means its video understanding is qualitatively different: it can reason about temporal dynamics across long video sequences, not just single frames.

The MoE architecture gives Gemini Ultra/Pro enormous capacity while maintaining reasonable inference costs. Google's TPU hardware also gives it training efficiency advantages — Gemini Ultra was trained on TPU v4 Pods with custom inter-chip networking that reduces communication overhead in distributed training.

#### Strengths

* 1M+ token context — unmatched for ultra-long documents
* Best native video and audio understanding of any frontier model
* Strong multilingual capability (trained on 100+ languages)
* TPU efficiency enables faster iteration cycles
* Deep Google Search and workspace ecosystem integration
* Gemini 2.0 Flash: fastest inference at frontier quality level

#### Weaknesses

* Closed source; API pricing not competitive with open models
* Historical issues with factual accuracy (hallucination rate)
* Alignment behavior inconsistent across model sizes
* 1M context practical use requires careful prompting
* Less developed tool-use ecosystem vs. OpenAI

## LLaMA 3 / 3.1 — Meta AI

LLaMA 3 / 3.1 / 3.3: Meta AI · Open Weights · Dense Decoder-Only

| Parameter | Value | Notes |
|---|---|---|
| Model Sizes | 8B, 70B, 405B | LLaMA 3.1; all open weights |
| Architecture | Dense Decoder-Only Transformer | No MoE — every parameter active |
| Attention | Grouped-Query Attention (GQA) | 8 KV heads for 8B, 8 for 70B |
| Positional Encoding | RoPE (θ=500,000) | High base frequency for long context |
| FFN Activation | SwiGLU | Swish-gated linear unit |
| Context Window | 128K tokens | LLaMA 3.1 extended from 8K |
| Vocabulary | 128,256 tokens | 4× larger than LLaMA 2; better multilingual |
| Training Tokens | 15T+ tokens | High-quality filtered web data |

### Architecture Deep Dive

LLaMA 3's architecture is publicly documented — a major advantage. It's a clean, well-optimized dense Transformer with specific innovations that make it exceptionally trainable and deployable:

**SwiGLU Activation:** Replaces the standard ReLU FFN with `FFN(x) = (xW₁ ⊙ σ(xW₃)) · W₂` where σ is Swish. This gating mechanism adds a multiplicative interaction that empirically outperforms vanilla ReLU at the same parameter count. SwiGLU requires 3 weight matrices instead of 2, but the hidden dimension is reduced proportionally.

**RoPE with high base frequency (θ=500,000):** Standard RoPE uses θ=10,000. LLaMA 3.1 uses θ=500,000, which means position embeddings vary much more slowly — allowing robust generalization to longer sequences (128K) without severe degradation beyond training length.

**Pre-RMSNorm:** Uses Root Mean Square Layer Normalization instead of standard LayerNorm — eliminates the mean subtraction operation, reducing compute by ~40% while achieving equivalent training stability. Applied before each sub-layer (Pre-Norm arrangement).

**Why GQA Matters at Scale** For LLaMA 3.1 405B with 128K context, full MHA would require: 128 heads × 128K tokens × 128 dim × 2 (K+V) × 4 bytes ≈ 168GB of KV cache per inference pass. With GQA (8 KV heads), this drops to ~10.5GB — the difference between needing 4 A100s and 1.

LLaMA 3.3 70B demonstrates that careful data curation and extended training can push a 70B dense model to near-405B performance on many benchmarks — a crucial insight that challenges the assumption that bigger always wins.

#### Strengths

* Open weights — fully inspectable, self-hostable, fine-tunable
* Best performance per parameter in the open-source ecosystem
* Well-documented architecture enables community innovation
* Massive ecosystem of fine-tunes, quantizations, and tools
* 405B model approaches GPT-4 class on many benchmarks
* Quantization-friendly (GGUF, AWQ, GPTQ readily available)

#### Weaknesses

* Dense architecture — higher inference cost vs. MoE at same quality
* 405B requires substantial hardware (8× H100 minimum)
* Base model requires fine-tuning for instruction following
* Safety alignment weaker than proprietary models out-of-box
* No native multimodality in core model (LLaMA 3.2 Vision added)

## Mistral / Mixtral — Mistral AI

Mistral 7B / Mixtral 8×7B / 8×22B: Mistral AI · Open Weights · Sparse MoE + Sliding Window

| Parameter | Value | Notes |
|---|---|---|
| Mistral 7B Params | 7.3B | Dense; outperforms LLaMA 2 13B |
| Mixtral 8×7B Total | 46.7B total, ~12.9B active | 8 experts, 2 active per token |
| Mixtral 8×22B Total | 141B total, ~39B active | Strongest open MoE model |
| Attention (7B) | Sliding Window (W=4096) | Full attention in alternating layers |
| Attention (Mixtral) | Full attention + GQA | No sliding window in Mixtral |
| Context Window | 32K tokens | Via positional interpolation |
| FFN Activation | SwiGLU | Same as LLaMA 3 |

### Architecture Deep Dive

Mistral AI's key contribution is demonstrating that **architectural efficiency** can beat brute-force scale. Mistral 7B outperforms LLaMA 2 13B on most benchmarks — with half the parameters — through a combination of Sliding Window Attention and careful architecture choices.

**Sliding Window Attention (SWA):** Each token attends to only W=4096 preceding tokens rather than the full context. For a sequence of length L, this reduces memory from O(L) to O(W) in the KV cache. The key insight is that for many tasks, local context is sufficient — global context is handled implicitly through the recurrent structure of token generation. However, Mistral alternates between SWA layers and full-attention layers to ensure global information can propagate.

Mixtral's MoE is the first widely-deployed open MoE model. Its router learns task specialization without explicit supervision — experts self-organize to handle different domains, languages, and reasoning patterns. Analysis shows individual experts develop distinct specializations (e.g., one expert handles Python, another handles mathematical proofs).

**Codestral and Mistral Large** extend the architecture with longer context (128K), larger vocabulary, and better multilingual tokenization. Mistral's approach of releasing strong base models with permissive licenses has made it the foundation of dozens of fine-tuned variants.

#### Strengths

* Efficiency leader — best quality-per-active-parameter ratio
* Mixtral 8×22B matches GPT-3.5 at lower inference cost
* Open weights with Apache 2.0 license (commercial use OK)
* SWA enables efficient inference on consumer hardware
* Strong code generation (Codestral specialization)
* Excellent for fine-tuning on domain-specific data

#### Weaknesses

* MoE expert routing adds inference complexity/latency
* Smaller context than Claude or Gemini 1.5
* Base alignment weaker than proprietary RLHF-trained models
* SWA layers can miss information beyond window in 7B model
* Smaller research team than OpenAI/Google/Meta

## Grok-1 / Grok-1.5 / Grok-2 — xAI

Grok-1 / Grok-2: xAI · Grok-1 Open Weights · MoE Architecture

| Parameter | Value | Notes |
|---|---|---|
| Grok-1 Total Params | 314B | 8 experts, 2 active (25% of params) |
| Architecture | Sparse MoE Transformer | Confirmed in open-source release |
| Attention | Multi-Head Attention | Standard MHA, no GQA in Grok-1 |
| Positional Encoding | RoPE | Standard implementation |
| FFN Activation | GeLU | Not SwiGLU unlike LLaMA/Mistral |
| Context Window | 8K (Grok-1), 128K (Grok-1.5) | Major improvement in 1.5 |
| Data Advantage | Real-time X (Twitter) data | Unique access to live social data |

### Architecture Deep Dive

Grok-1 is the largest open-weight MoE model, with 314B total parameters across 8 expert networks. Its architecture code was released on GitHub in March 2024, revealing a relatively standard MoE Transformer with notable differences from LLaMA/Mistral:

**GeLU vs. SwiGLU:** Grok-1 uses Gaussian Error Linear Unit activations rather than SwiGLU. GeLU is smoother than ReLU but lacks SwiGLU's gating mechanism. This is a less common choice for 2024-era models, suggesting Grok-1's architecture predates widespread SwiGLU adoption.

**No GQA:** Grok-1 uses standard Multi-Head Attention, meaning full KV cache per head. This is computationally more expensive than GQA but was the standard at training time. Grok-1.5 and Grok-2 presumably address this.

**The Real-Time Data Advantage** Grok's most differentiating feature is not architectural — it's data. As an xAI product, Grok has real-time access to X's firehose of social media data. This allows it to answer questions about current events, trending topics, and breaking news without web search, which is fundamentally different from frozen-training-data models. The challenge is that social media data is noisy and requires careful quality filtering.

Grok-2 significantly extended context length (128K) and improved multimodal capability with vision understanding. xAI's access to massive GPU clusters (reportedly 100K+ H100s, later upgraded to H200s) suggests Grok-3 and beyond will see significant scale improvements.

#### Strengths

* Grok-1 is the largest open-weight MoE available
* Real-time X data integration unique to any frontier model
* Less restrictive response policy for certain topics
* xAI's GPU scale enables rapid future improvements
* Strong math and science reasoning (Grok-2)

#### Weaknesses

* Grok-1 architecture dated (no GQA, GeLU over SwiGLU)
* Smaller research team / less ML publishing transparency
* Limited API ecosystem vs. OpenAI/Anthropic
* Quality inconsistency across domains
* Grok-2+ not open weight

## Comprehensive Comparison Matrix

| Dimension | GPT-4o | Claude 3.5 | Gemini 1.5 | LLaMA 3.1 | Mixtral 8×22B | Grok-2 |
|---|---|---|---|---|---|---|
| Architecture Type | MoE (rumored) | Dense | MoE (confirmed) | Dense | Sparse MoE | Sparse MoE |
| Open Weights | ✗ Closed | ✗ Closed | ✗ Closed | ✓ Open | ✓ Open | Grok-1 only |
| Context Window | 128K | 200K | 1M–2M | 128K | 64K | 128K |
| Attention Mechanism | MHA + Flash | MHA (likely) | GQA + Ring | GQA | Full + GQA | MHA |
| Positional Encoding | RoPE | RoPE (ext.) | RoPE (custom) | RoPE θ=500K | RoPE | RoPE |
| FFN Activation | SwiGLU (likely) | Unknown | GeGLU / SwiGLU | SwiGLU | SwiGLU | GeLU |
| Alignment Method | RLHF + RLAIF | Constitutional AI | RLHF + SFT | RLHF + DPO | SFT + DPO | RLHF |
| Native Multimodal | ✓ Text+Vision+Audio | Text+Vision | ✓ All modalities | 3.2: Text+Vision | Text only | Text+Vision |
| Coding Strength | ★★★★★ | ★★★★★ | ★★★★½ | ★★★★☆ | ★★★★☆ | ★★★★☆ |
| Reasoning Depth | ★★★★★ | ★★★★★ | ★★★★½ | ★★★★☆ | ★★★★☆ | ★★★★☆ |
| Deployment Flexibility | API only | API only | API / Vertex | Full self-host | Full self-host | Grok-1 self-host |
| Inference Cost Efficiency | Medium (MoE) | Medium | High (MoE + Flash) | Variable by size | Best open-source | Medium |

### Key Architectural Differentiators: What Actually Sets Them Apart

#### Context Length King

Gemini 1.5 Pro is the only model with truly verified 1M+ token context with high recall. Achieved through Ring Attention across TPU slices, MQA/GQA, and a specialized RoPE extension. No other frontier model comes close — Claude's 200K and GPT-4's 128K are significant but an order of magnitude smaller.

#### Efficiency Leader

Mixtral 8×22B achieves near-GPT-4-level quality with only 39B active parameters per token. This is the most compute-efficient frontier model available open-source. For deployment at scale where cost per token matters, nothing beats the MoE efficiency at this quality tier.

#### Alignment Innovation

Constitutional AI is the most principled approach to alignment. Rather than human labelers rating outputs, a set of principles guides self-critique. This produces more consistent behavior across adversarial inputs and avoids the "label distribution shift" problem that RLHF suffers from at scale.

#### Native Multimodality

Both Gemini and GPT-4o handle multiple modalities natively (video, audio for Gemini; audio for GPT-4o). Other models use adapters. Native training means cross-modal reasoning — asking "what sound would this image make" or reasoning about video motion — is fundamentally more capable.

#### Open Ecosystem

LLaMA 3 is the only model in this tier with fully open weights at the 405B scale. This enables: fine-tuning for proprietary domains, inference on-premise (no data leaving your infrastructure), and community innovation (100s of fine-tuned variants). The ecosystem value is impossible to quantify.

#### Recency Advantage

Grok is the only frontier model with real-time access to live data without explicit web search. X's firehose provides breaking news, trending topics, and social sentiment — genuinely different from models trained on static datasets. Critical for time-sensitive tasks.

## The Big Picture

There is no single best architecture. MoE wins on capacity-at-cost. Dense wins on consistency and fine-tuning. GQA/MQA wins on inference efficiency. Constitutional AI wins on alignment. The frontier is moving toward: (1) MoE becoming standard, (2) Context windows expanding toward 10M+, (3) Native multimodality across all modalities, (4) Hybrid architectures mixing attention with state-space models (Mamba, RWKV) for sub-quadratic scaling. The next 2 years will see these ideas converge into a new generation of architectures that look meaningfully different from today's pure Transformer descendants.

Specifications reflect publicly available information; proprietary model details are best estimates based on published research, model card data, and independent analysis.
