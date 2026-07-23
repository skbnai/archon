---
title: "Transformer Concepts: Deep Internals"
doc_type: guide
domain: architecture
status: current
canonical: true
topic_id: transformer-concepts-deep
maturity: expert
personas: [ml-engineer, research-engineer, architect]
last_reviewed: 2026-07-19
covers_version: "2026"
supersedes: [docs/ai-foundations/transformer_concepts_deep.md]
tags: [transformers, llm, deep-dive, internals, concepts]
sources: []
---

# Transformer Concepts: Deep Internals

Transformer mechanics—self-attention, Q/K/V, RoPE, MoE routing, total vs. active parameters—with intuition at every step.

## Why This Matters

Production agent systems require understanding what's happening under the hood. Why does context length matter? What limits inference speed? How do Mixture-of-Experts actually work? These questions have concrete answers that drive architecture decisions.

---

## 1. TOKENIZATION

Before a transformer sees a single letter, text is converted to integers. A **tokenizer** is a fixed lookup table mapping subword pieces to IDs. The model never sees characters—only numbers.

### Example: Byte-Pair Encoding (BPE)

Input: `"The cat sat on the mat"`

**CHARACTERS → SUBWORDS (BPE)**
- The, cat, sat, on, the, mat

**SUBWORDS → INTEGER IDs (LLaMA 3 vocab)**
- The→791, cat→8415, sat→7731, on→389, the→279, mat→14679

**Why subwords, not words?**

"Unbelievable" becomes ["un", "believ", "able"]. The model handles unseen words by composing seen pieces. A word-level vocab of 500K+ is impractical; BPE with 32K–128K tokens covers virtually all text with manageable embedding tables.

**Key Insight:** The output of tokenization is a sequence of integers: `[791, 8415, 7731, 389, 279, 14679]`. This integer sequence is the only input to the transformer. Everything else—meaning, grammar, world knowledge—must be learned from predicting what comes next.

---

## 2. TOKEN EMBEDDINGS

An integer like `8415` carries no mathematical meaning—you can't do algebra on it. An **embedding layer** maps each integer to a high-dimensional vector of floats (typically 4096 or 8192 dimensions). This lookup table has one row per vocabulary token.

### Embedding as Lookup Table

Each token gets its own row in embedding matrix `E ∈ ℝ^(vocab_size × d_model)`. Token 791 ("The") maps to a vector of 4096 floats.

### What Geometry Encodes

After training, semantically similar tokens occupy nearby regions in this space.

**Famous example:**
```
E[king] − E[man] + E[woman] ≈ nearest neighbor to E[queen]
```

This isn't magic—it emerges from predicting next tokens across billions of documents. The model that predicts "king wore a crown" must also predict "queen wore a crown", so their vectors necessarily capture shared "royalty" dimension.

### Critical Insight

Each token in the sequence gets its own vector. A 6-token sentence produces a matrix of shape `[6 × 4096]`. This matrix is the raw input to the transformer stack. The transformer's job is to iteratively refine these vectors so that by the output layer, each vector encodes not just "what is this token" but "what does this token mean in this specific context."

---

## 3. SELF-ATTENTION

Self-attention answers: **for each token, how much should it pay attention to every other token?** Unlike CNNs (fixed local window) or RNNs (sequential), attention computes pairwise relationships between *all* tokens simultaneously.

**Key intuition:** The meaning of "bank" in "river bank" vs. "bank account" is determined by surrounding words. Attention lets the model dynamically decide which surrounding words matter and how much.

### What "Attending" Means Computationally

When token A "attends to" token B with weight 0.6, the output representation of A is 60% influenced by B's value vector. The model learns which tokens are useful context for which other tokens—through gradient descent on next-token prediction.

### Scaled Dot-Product Attention

**Formula:** `Attention(Q, K, V) = softmax(Q · K^T / √d_k) · V`

The scaling by √d_k (typically √128=11.3) prevents extremely small gradients. Without it, training becomes unstable.

---

## 4. QUERIES, KEYS & VALUES

The brilliant insight of attention is splitting each token's representation into three roles. Think of a **library database search**:

**Q — Query:** "What am I looking for?" Each token produces a Query vector representing what information it needs from context. Query = `x · W_Q` where W_Q is a learned weight matrix.

**K — Key:** "What information do I have?" Each token produces a Key vector describing what information it contains. Keys are matched against Queries via dot product to compute compatibility.

**V — Value:** "What do I actually contribute?" Each token produces a Value vector—the actual content that gets mixed into the output. Once the model decides which tokens matter, the Value is what flows into the output.

**Formula:** `Attention output = weighted sum of all Values, where weights come from Q·K compatibility`

### Intuitive Example: "The cat sat"

Token "sat" produces a Query that asks: "Which tokens help me understand what happened?" The Key of "cat" advertises: "I'm a noun, a concrete entity." The softmax similarity between sat's Query and cat's Key is high. The Value of "cat" then influences sat's refined representation.

---

## 5. MULTI-HEAD ATTENTION

One attention head can only learn one type of relationship pattern. **Multi-head attention** runs H independent attention operations in parallel, each with its own W_Q, W_K, W_V matrices. Results concatenated and projected back.

### Example: 4 Heads on "The cat that the dog chased finally ran away"

**HEAD 1 — SUBJECT-VERB AGREEMENT**
- "ran" attends strongly to "cat" (grammatical subject), skipping "dog" even though syntactically closer. This head learned subject tracking across clauses.

**HEAD 2 — COREFERENCE**
- "it" (if present) would attend to "cat" as antecedent. This head specializes in pronoun-entity linkage.

**HEAD 3 — SYNTACTIC DEPENDENCY**
- "chased" attends to "dog" (subject) and "cat" (object). Encodes event participants.

**HEAD 4 — LOCAL CONTEXT**
- "finally" attends locally to neighboring words for adverbial modification.

**Formula:** `MultiHead(Q,K,V) = Concat(head_1, ..., head_h) · W^O`

---

## 6. FEED-FORWARD NETWORK

After attention mixes information across positions, a position-wise FFN processes each token independently.

**Key insight:** Attention handles *communication between tokens*. FFN handles *per-token computation*. This is where the model stores factual associations.

### FFN as Key-Value Memory Store

Research (Geva et al., 2021) showed FFN neurons behave like memory cells. The first weight matrix (W_1) acts as **keys**—detecting patterns like "this position contains a European capital city name". The second matrix (W_2) acts as **values**—contributing associated knowledge like "→ is located in Europe, has a parliament, uses Euro".

**Standard FFN (ReLU):**
```
FFN(x) = ReLU(x · W_1 + b_1) · W_2 + b_2
d_ff = 4 × d_model (typical)
```

**SwiGLU (LLaMA 3, Mistral):**
```
FFN_SwiGLU(x) = (x·W_1 ⊗ SiLU(x·W_3)) · W_2
⊗ = elementwise multiply
SiLU(x) = x · σ(x) (smooth, differentiable gate)
Requires 3 matrices instead of 2
```

### Why SwiGLU &gt; ReLU

**ReLU** kills all negative activations (hard zero). **SiLU** allows small negatives through smoothly. The **gating** (multiplication by sigmoid) creates a soft information gate—neurons learn "pass through only if input matches pattern X AND pattern Y."

In practice, SwiGLU models achieve the same loss with fewer training steps.

---

## 7. POSITIONAL ENCODING

Transformers are **permutation invariant**—without positional information, "cat bites dog" and "dog bites cat" produce identical attention patterns. Positional encodings inject order into an architecture that otherwise has none.

### Three Approaches

**1. Sinusoidal (2017):** Fixed, non-learned vectors added to embeddings: `PE(pos, 2i) = sin(pos / 10000^(2i/d))`
- Works but can't extrapolate—model struggles with sequences longer than training.

**2. Learned Absolute (GPT-1, GPT-2):** Each position gets a trainable embedding vector.
- Simple, but hard limit at max training length (e.g., 2048 tokens). Position 2049 has no embedding—model breaks completely.

**3. RoPE — Rotary Position Embedding (now standard):** Instead of adding positional vectors to embeddings, RoPE **rotates** Q and K vectors by angles that depend on position.

**RoPE Core Idea:**
```
Q_pos = R_θ(pos) · Q
K_pos = R_θ(pos) · K

R_θ(pos) = block-diagonal rotation matrix
The dot product (Q_m · K_n) depends only on |m−n|, not absolute positions m or n
```

**Intuition:** Each token's Q,K vector is rotated by its position angle. The relative angle between two tokens equals their positional distance—this is the same whether they're at positions (5,8) or (105,108). The model sees relative distance and generalizes to unseen absolute positions.

### Base Frequency θ and Context Length

**RoPE hyperparameter θ** determines rotation rate. Standard θ=10,000. LLaMA 3.1 uses θ=500,000.

**Higher θ** means slower rotation—position vectors change more gradually. Model can distinguish positions very far apart (128K tokens) without embeddings wrapping around and becoming identical for different positions.

---

## 8. MIXTURE OF EXPERTS

Standard transformers are "dense"—every parameter used for every token, every time. **Mixture of Experts (MoE)** breaks this: the FFN layer is replaced by E expert FFNs, and a learned **router** selects only K of them per token. Most parameters idle most of the time.

### The Router: How Experts Are Selected

Router is a small linear layer: `router_logits = x · W_r` where W_r ∈ ℝ^(d_model × E).

Softmax gives probabilities over all E experts. Top-K probabilities kept (K=2 in Mixtral, Gemini), rest set to zero.

**Formula:** `MoE(x) = Σ_i∈TopK(x) g_i(x) · Expert_i(x)`

### Load Balancing Problem

If router is naive, all tokens route to same 2 experts, making others useless. Training requires an **auxiliary load balancing loss** that penalizes uneven expert utilization: `L_aux = α · Σ_i f_i · P_i`

This pushes all experts to receive roughly equal traffic during training.

---

## 9. TOTAL vs. ACTIVE PARAMETERS

This distinction causes the most confusion when comparing models like "GPT-4 has 1.8T parameters" vs "LLaMA 3 has 405B parameters". These numbers mean fundamentally different things.

### Total Parameters

All weights stored on disk / in memory. For MoE, includes *all expert weights*—even ones not used for any given token.

**Determines:** Storage cost, GPU memory needed to load, total capacity for knowledge.

**Example:** Mixtral 8×7B = 8 experts × ~7B each = **46.7B total**

### Active Parameters

Only experts actually selected by router participate in computation. For a given token, K out of E experts run. Rest ignored—no compute, no FLOPs.

**Determines:** Inference speed, FLOPs per token, practical compute cost.

**Example:** Mixtral 8×7B = 2 of 8 active = **~12.9B active**

### The MoE Trade-off in One Sentence

**MoE buys you the knowledge capacity of a large model (total params) at the inference cost of a small model (active params)—at the price of needing enough RAM/VRAM to store all idle experts simultaneously.**

### Concrete Implications

| Metric | Dense Model (LLaMA 405B) | MoE Model (Mixtral 8×22B) | Winner |
|---|---|---|---|
| VRAM to load | ~810GB | ~282GB | MoE ✓ |
| FLOPs per token | ~810B | ~78B | MoE ✓ |
| Knowledge capacity | 405B params | 141B params | Dense ✓ |
| Fine-tuning ease | Simple | Complex (expert collapse risk) | Dense ✓ |
| Quality at same FLOPs | Good | Better (larger total capacity) | MoE ✓ |

---

## 10. THE FULL FORWARD PASS

Here's what happens, step by step, for "The capital of France is" → predict "Paris":

**Step 1: Tokenization**
`"The capital of France is" → [791, 6864, 315, 9822, 374]` (5 integers)

**Step 2: Embedding Lookup**
5 integers → matrix `[5 × 4096]`. Each integer selects a row from embedding table. At this point they encode *token identity* only—no positional or contextual information.

**Step 3: RoPE Position Injection**
As Q and K matrices computed in each attention layer, they are rotated by position-specific angles. Now "France" at position 4 has Q/K vectors rotated differently from position 1.

**Step 4: 32× Transformer Layers**
Each layer refines representations via `[Self-Attention → Add&Norm → FFN → Add&Norm]`.

- **Layers 1–8:** Token-level patterns. "capital" is noun, "of" is preposition, "France" is proper noun. Syntactic dependencies form noun phrase.
- **Layers 9–16:** Semantic grouping. "The capital of France" recognized as geographic entity. "is" is copula.
- **Layers 17–24:** World knowledge retrieval. "capital of France" activates "Paris" memory cells in multiple FFN layers.
- **Layers 25–32:** Final integration. Last token "is" accumulates evidence. High attention to "France" and "capital". Output vector now strongly points toward "Paris" in vocabulary space.

**Step 5: Language Model Head**
Output vector for last position projected through unembedding matrix `[4096 × 128,256]` and softmaxed to produce probabilities. "Paris" gets ~0.94, "Lyon" ~0.02, etc.

**Step 6: Autoregressive Loop**
Sampled token "Paris" appended to input: `[791, 6864, 315, 9822, 374, 12366]`. Entire forward pass runs again for now-6-token sequence.

**Why generation is slow:** One token per forward pass, sequentially. KV caching saves K, V computations from previous steps—only new token's attention to all prior tokens needs fresh computation.

---

## The Big Picture

| Component | Role |
|---|---|
| **Attention** | Communication between tokens. Q asks questions. K advertises. V delivers. Router decides who listens. |
| **FFN** | Memory. Each neuron in W_1 detects patterns; corresponding row in W_2 is associated fact. |
| **MoE** | Conditional memory. E specialized databases routed per token. Total capacity scales; per-token cost constant. |
| **RoPE** | Relative compass. Bakes relative distance into Q·K dot product via rotation. Enables position generalization. |
| **Total Params** | Knowledge tank. How much the model can know. Determines GPU memory to load. |
| **Active Params** | Thinking cost. How much compute per token. Determines inference speed and cost. |

---

## Related

- [Transformer Architecture: Frontier Models Deep Dive](34-transformer-architectures.md)
- [Agentic AI Landing Zone: Visual Guide](32-agentic-ai-landing-zone-visual-guide.md)

---

**Document Status:** Current (July 2026)  
**Owner:** ML Research & Architecture  
**Audience:** Research engineers, ML architects, advanced platform teams
