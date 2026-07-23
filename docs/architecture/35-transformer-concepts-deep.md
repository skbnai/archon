---
title: 'Transformer Concepts: Deep Internals'
date_created: 2026-07-17
last_reviewed: 2026-07-17
status: current
source_type: converted-html
doc_type: reference-architecture
domain: architecture
topic_id: transformer-concepts-deep
maturity: expert
personas: [architect, research-engineer, ml-engineer]
tags: [transformers, llm, ai-foundations, deep-dive]
supersedes: [docs/ai-foundations/transformer_concepts_deep.md]
covers_version: "2026"
---

# Transformer Concepts: Deep Internals

Not model comparisons. Not benchmarks. The real mechanics — self-attention, Q/K/V, RoPE, MoE routing, and exactly what "total vs. active parameters" means — with interactive examples at every step.

## TOKENIZATION

Before a transformer sees a single letter, text is converted to integers. A **tokenizer** is a fixed lookup table (built before training) that maps subword pieces to IDs. The model never sees characters — only numbers.

### Example: BPE Tokenization

Input sentence: `"The cat sat on the mat"`

CHARACTERS → SUBWORDS (BPE)

The ▁cat ▁sat ▁on ▁the ▁mat

SUBWORDS → INTEGER IDs (LLaMA 3 vocab)

The → 791 cat → 8415 sat → 7731 on → 389 the → 279 mat → 14679

Why subwords, not words?

"Unbelievable" becomes ["un", "believ", "able"] — the model handles unseen words by composing seen pieces. A word-level vocab of 500K+ is impractical; BPE with 32K–128K tokens covers virtually all text with manageable embedding tables.

The output of tokenization is a sequence of integers: `[791, 8415, 7731, 389, 279, 14679]`. This integer sequence is the only input to the transformer. Everything else — meaning, grammar, world knowledge — must be learned from predicting what comes next.

## TOKEN EMBEDDINGS

An integer like `8415` carries no mathematical meaning — you can't do algebra on it. An **embedding layer** maps each integer to a high-dimensional vector of floats (typically 4096 or 8192 dimensions). This lookup table has one row per vocabulary token and is _learned during training_.

### Embedding as Lookup Table

E ∈ ℝ^(vocab_size × d_model)

token 0:

0.2

−.1

0.8

... 4093 more

token 791 →

0.7

0.3

−.4

... 4093 more

...

#### What Geometry Encodes

After training, semantically similar tokens occupy nearby regions in this space. The famous example:

E[king] − E[man] + E[woman]

≈ nearest neighbor to

E[queen]

This isn't magic — it emerges from predicting next tokens across billions of documents. The model that predicts "king wore a crown" must also predict "queen wore a crown", so their vectors necessarily capture the shared "royalty" dimension.

Critical Insight

Each token in the sequence gets its own vector from this table. A 6-token sentence produces a matrix of shape `[6 × 4096]`. This matrix is the raw input to the transformer stack — the transformer's job is to iteratively refine these vectors so that by the output layer, each vector encodes not just "what is this token" but "what does this token mean in this specific context."

## SELF-ATTENTION

Self-attention answers one question: **for each token, how much should it pay attention to every other token?** Unlike a CNN (fixed local window) or RNN (sequential, one step at a time), attention computes pairwise relationships between _all_ tokens simultaneously.

The key intuition: the meaning of "bank" in "river bank" vs. "bank account" is determined by surrounding words. Attention lets the model dynamically decide which surrounding words matter and how much.

↓ CLICK A WORD TO SEE WHAT IT ATTENDS TO ↓

What "attending" means computationally

When token A "attends to" token B with weight 0.6, the output representation of A is 60% influenced by B's value vector. The model learns which tokens are useful context for which other tokens — not through rules, but through gradient descent on next-token prediction.

## QUERIES, KEYS & VALUES

The brilliant insight of attention is splitting each token's representation into three distinct roles. Think of it like a **library database search** :

### Q — Query

### "What am I looking for?"

Each token produces a Query vector representing what information it needs from the context. "The word 'it' needs to find its antecedent noun."

Query = `x · W_Q` where W_Q is a learned weight matrix.

Shape: [seq_len × d_k] where d_k = d_model / num_heads

#### K — Key

### "What information do I have?"

Each token produces a Key vector describing what information it contains or offers. "The word 'cat' advertises: I am a concrete noun, an animal, a subject."

Key = `x · W_K` — a different learned projection.

Keys are matched against Queries via dot product to compute compatibility.

#### V — Value

### "What do I actually contribute?"

Each token produces a Value vector — the actual content that gets mixed into the output. "Once the model decides 'it' refers to 'cat', the cat's Value is what flows into 'it's' new representation."

Value = `x · W_V`

Attention output = weighted sum of all Values, where weights come from Q·K compatibility.

Scaled Dot-Product Attention

Attention(Q, K, V) = softmax( Q · Kᵀ / √d_k ) · V

Q ∈ ℝ^(n×dₖ)  |  K ∈ ℝ^(n×dₖ)  |  V ∈ ℝ^(n×dᵥ)  |  √dₖ = scaling factor 

EXAMPLE: "THE CAT SAT" → Q, K, V PROJECTIONS (simplified d_k=6)

TOKEN

Query (Q)

Key (K)

Value (V)

The

0.3

-0.1

0.7

0.2

-0.4

0.5

0.1

0.4

-0.2

0.6

0.1

-0.3

0.5

0.1

0.2

-0.1

0.4

0.3

cat

-0.2

0.8

0.1

-0.3

0.6

0.1

0.7

-0.1

0.4

0.2

-0.5

0.3

-0.1

0.7

0.4

0.2

-0.3

0.5

sat

0.6

0.2

-0.4

0.5

0.1

-0.2

-0.3

0.5

0.1

-0.4

0.6

0.2

0.2

-0.3

0.6

0.4

0.1

-0.2

ATTENTION SCORE: Q(sat) · K(cat)ᵀ / √6 — HOW MUCH "SAT" LOOKS AT "CAT"

= (0.6×0.7) + (0.2×−0.1) + (−0.4×0.4) + (0.5×0.2) + (0.1×−0.5) + (−0.2×0.3) 

= 0.42 − 0.02 − 0.16 + 0.10 − 0.05 − 0.06

= 0.23 → divide by √6 (2.449) → 0.094 → softmax → attention weight

Why scale by √d_k?

For large d_k (say 128), dot products grow large in magnitude, pushing softmax into regions with extremely small gradients. Dividing by √d_k keeps values in a stable range regardless of model dimension. Without this, training becomes unstable and the model learns poorly.

## MULTI-HEAD ATTENTION

One attention head can only learn one type of relationship pattern at a time. **Multi-head attention** runs H independent attention operations in parallel, each with its own W_Q, W_K, W_V matrices. The results are concatenated and projected back.

### Example: 4 Heads on "The cat that the dog chased finally ran away"

HEAD 1 — SUBJECT-VERB AGREEMENT

"ran" attends strongly to "cat" (the grammatical subject), skipping "dog" even though dog is syntactically closer. This head learned to track subject across intervening clauses.

HEAD 2 — COREFERENCE

"it" (if present) would strongly attend to "cat" as its antecedent. This head specializes in resolving pronoun-to-entity linkage across distances.

HEAD 3 — SYNTACTIC DEPENDENCY

"chased" strongly attends to "dog" (its subject) and "cat" (its object). This head encodes the chase-event's participant roles.

HEAD 4 — LOCAL CONTEXT

"finally" attends locally to neighboring words for adverbial modification. Some heads specialize in short-range positional patterns.

Multi-Head Attention Formula

MultiHead(Q,K,V) = Concat(head₁, ..., headₕ) · W^O

where headᵢ = Attention(Q·W^Q_i, K·W^K_i, V·W^V_i)

After concatenation, a final linear projection W^O mixes information across all heads. The output shape is identical to the input: `[seq_len × d_model]` — the heads work in parallel and their outputs are integrated seamlessly.

#### MHA — Full Multi-Head

H heads, each with independent W_Q, W_K, W_V. Dimension per head = d_model / H. For GPT-3 (d=12288, H=96): each head has d_k = 128.

**KV Cache size:** For each head, per token, store a K and V vector of size d_k. Total: `H × seq_len × d_k × 2`

#### GQA — Grouped Query Attention

Multiple Query heads share one K, V pair per group. If 32 Q heads share 8 KV groups, each group covers 4 Q heads. Same computation for Q, but 4× less KV cache memory.

**Why it matters:** KV cache is the bottleneck for long sequences. GQA makes 128K context practical on 80GB GPUs.

## FEED-FORWARD NETWORK

After attention mixes information across positions, a position-wise FFN processes each token independently. This is crucial: attention handles _communication between tokens_ ; FFN handles _per-token computation_. It's where the model stores factual associations.

### FFN as a Key-Value Memory Store

Research (Geva et al., 2021) showed FFN neurons behave like memory cells. The first weight matrix (W₁) acts as **keys** — detecting patterns like "this position contains a European capital city name". The second matrix (W₂) acts as **values** — contributing the associated knowledge like "→ is located in Europe, has a parliament, uses Euro...".

Standard FFN (ReLU)

FFN(x) = ReLU(x · W₁ + b₁) · W₂ + b₂

d_ff = 4 × d_model (typical). For d_model=4096: d_ff=16384. 2 matrices: [4096×16384] + [16384×4096] ≈ 134M params per layer

SwiGLU (LLaMA 3, Mistral)

FFN_SwiGLU(x) = (x·W₁ ⊗ SiLU(x·W₃)) · W₂

⊗ = elementwise multiply  |  SiLU(x) = x · σ(x) (smooth, differentiable gate)  |  Requires 3 matrices instead of 2

#### Why SwiGLU > ReLU

**ReLU** kills all negative activations (hard zero). **SiLU** allows small negative values through smoothly. The **gating** (multiplication by sigmoid) creates a soft information gate — neurons can learn "pass through only if the input matches pattern X AND pattern Y."

In practice, SwiGLU models achieve the same loss with fewer training steps, or lower loss at the same compute.

#### FFN Size vs. Attention Size

In a standard transformer, FFNs contain about **⅔ of total parameters**. A 7B model has roughly:

• Embedding: ~500M

• Attention (32 layers): ~1.5B

• FFN (32 layers): ~4.5B

• LayerNorm, biases: ~500M

## POSITIONAL ENCODING

Transformers are **permutation invariant** — without positional information, "cat bites dog" and "dog bites cat" would produce identical attention patterns. Positional encodings inject order into an architecture that otherwise has none.

1

### Original: Sinusoidal (2017)

Fixed, non-learned vectors added to embeddings: `PE(pos, 2i) = sin(pos / 10000^(2i/d))`. Works but can't extrapolate — the model struggles with sequences longer than those seen in training, because frequencies were fixed at training time.

2

### Learned Absolute (GPT-1, GPT-2)

Each position gets a trainable embedding vector. Simple, but hard limit at max training length (e.g., 2048 tokens). Position 2049 has no embedding — the model breaks completely.

3

### RoPE — Rotary Position Embedding (now standard)

Instead of adding positional vectors to embeddings, RoPE **rotates** the Q and K vectors by angles that depend on position. The dot product Q·K then naturally encodes relative distance between tokens.

RoPE Core Idea

Q_pos = R_θ(pos) · Q  |  K_pos = R_θ(pos) · K

R_θ(pos) = block-diagonal rotation matrix | dot product (Q_m · K_n) depends only on |m−n|, not absolute positions m or n

INTUITION: EACH TOKEN'S Q,K VECTOR IS ROTATED BY ITS POSITION ANGLE

↕ Relative angle between tokens = their positional distance

Token at pos 5 and pos 8 → angle difference = 3 steps  
This is the same whether they're at positions (5,8) or (105,108)  
→ Model sees relative distance, generalizes to unseen absolute positions

Base Frequency θ and Context Length

RoPE has a hyperparameter θ (base frequency). Standard: θ=10,000. LLaMA 3.1: θ=500,000. Higher θ means slower rotation — position vectors change more gradually, so the model can distinguish positions that are very far apart (128K tokens) without the embeddings wrapping around and becoming identical for different positions.

4

### ALiBi — Attention with Linear Biases

Instead of rotating embeddings, ALiBi adds a learned linear penalty to attention scores based on distance: `score(i,j) = Q_i · K_j − m · |i−j|` where m is a head-specific slope. Simpler and extrapolates well, but less expressive than RoPE.

## MIXTURE OF EXPERTS

Standard transformers are "dense" — every parameter is used for every token, every time. **Mixture of Experts (MoE)** breaks this: the FFN layer is replaced by E expert FFNs, and a learned **router** selects only K of them for each token. Most parameters are idle most of the time.

### The Router: How Experts Are Selected

The router is a small linear layer: `router_logits = x · W_r` where W_r ∈ ℝ^(d_model × E). Softmax gives probabilities over all E experts. The top-K probabilities are kept (K=2 in Mixtral, Gemini), rest set to zero. The output is a weighted sum of the selected expert outputs.

MoE FFN Output

MoE(x) = Σᵢ∈TopK(x) g_i(x) · Expert_i(x)

g_i(x) = softmax(router_logits)_i (renormalized over top-K)  |  Expert_i = standard FFN with its own W₁, W₂, W₃

Load Balancing Problem

If the router is naive, all tokens route to the same 2 experts, making the others useless. Training requires an **auxiliary load balancing loss** that penalizes uneven expert utilization: `L_aux = α · Σᵢ f_i · P_i` where f_i = fraction of tokens routed to expert i, P_i = mean routing probability. This pushes all experts to receive roughly equal traffic during training.

## TOTAL vs. ACTIVE PARAMS

This is the question that causes the most confusion when comparing models like "GPT-4 has 1.8T parameters" vs "LLaMA 3 has 405B parameters". These numbers mean fundamentally different things.

### Total Parameters

### All weights in the model file

The total count of all numbers stored on disk / in memory. For an MoE model, this includes _all expert weights_ — even the ones that won't be used for any given token.

This determines: **storage cost** , **GPU memory needed to load the model** , and **the model's total capacity for knowledge**.

Mixtral 8×7B: 8 experts × ~7B each = **46.7B total**

#### Active Parameters

### Params used per token, per forward pass

Only the experts actually selected by the router participate in computation. For a given token, K out of E experts run. The rest are ignored — no compute, no FLOPs.

This determines: **inference speed** , **FLOPs per token** , and **practical compute cost**.

Mixtral 8×7B: 2 of 8 experts active = **~12.9B active**

VISUAL: TOTAL (DARK) vs ACTIVE (BRIGHT) PARAMETERS PER TOKEN

LLaMA 3 405B (Dense) Active = Total = 405B (100%)

405B — Every param fires for every token 

Mixtral 8×7B (Sparse MoE) Active: 12.9B / 46.7B (28%)

12.9B active

34B idle (stored, not computed)

Mixtral 8×22B (Sparse MoE) Active: 39B / 141B (28%)

39B active

102B idle

GPT-4 (Estimated MoE) Active: ~220B / ~1.8T (12%)

220B

~1.58T parameters idle per token

Active/computed per token

Stored but idle per token

#### The Concrete Implications

### GPU Memory (Loading)

Loading a model requires enough VRAM for **all parameters** (total). Mixtral 8×7B at fp16 needs ~93GB of VRAM regardless of which experts will be used — because all experts must be available for routing decisions.

Memory ∝ Total Parameters

### Inference Speed (FLOPs)

Each forward pass only computes through **active parameters**. Mixtral 8×7B processes each token through ~12.9B parameters. This is why it runs at similar speed to a 13B dense model despite 46.7B total weights.

Speed ∝ Active Parameters

The MoE Trade-off in One Sentence

MoE buys you the **knowledge capacity of a large model** (total params determines what the model can know) at the **inference cost of a small model** (active params determines how fast it runs) — at the price of needing enough RAM/VRAM to store all the idle experts simultaneously.

| Metric | Dense Model (LLaMA 3 405B) | MoE Model (Mixtral 8×22B) | Winner  
---|---|---|---  
| VRAM to load | ~810GB (fp16) | ~282GB (fp16) | MoE ✓ (less total params)  
| FLOPs per token | ~810B FLOPs | ~78B FLOPs | MoE ✓ (only active experts)  
| Knowledge capacity | 405B params of knowledge | 141B params of knowledge | Dense ✓ (more total params)  
| Fine-tuning ease | Standard, well-understood | Complex (expert collapse risk) | Dense ✓  
| Quality at same FLOPs | Good | Better (larger total capacity) | MoE ✓  
| Serving complexity | Simple | Expert sharding across GPUs | Dense ✓  

## THE FULL FORWARD PASS

Now every piece connects. Here's what happens, step by step, for the sentence _"The capital of France is"_ — predicting the next token "Paris":

1

### Tokenization

### "The capital of France is" → [791, 6864, 315, 9822, 374]

5 integers. The model sees nothing else. No letters, no spaces — pure integers that index into the embedding table.

2

#### Embedding Lookup

### 5 integers → matrix [5 × 4096]

Each integer selects a row from the embedding table. We now have 5 vectors of 4096 floats each. At this point they encode _token identity_ only — no positional or contextual information yet. "France" in any position looks the same.

3

#### RoPE Position Injection

### Rotate Q, K vectors inside each attention layer

As Q and K matrices are computed in each attention head, they are rotated by position-specific angles. Now "France" at position 4 has Q/K vectors rotated differently from "France" at position 1 — the model knows order.

4

#### 32× Transformer Layers

### [Self-Attention → Add&Norm; → FFN → Add&Norm;] × 32

Each layer refines the representations. In early layers, attention captures local grammar. In middle layers, it builds syntactic structure. In late layers, it integrates semantic meaning. By layer 32, the vector for the last token "is" encodes the entire context: "this sentence is asking for a capital city, specifically France's."

#### Layer-by-layer intuition for "France is [?]"

| Layers | What's being computed  
---|---  
| 1–8 | Token-level patterns: "capital" is a noun, "of" is a preposition, "France" is a proper noun. Syntactic dependencies: "capital of France" forms a noun phrase.  
| 9–16 | Semantic grouping: "The capital of France" is recognized as a geographic entity reference. "is" is the copula linking subject to predicate.  
| 17–24 | World knowledge retrieval from FFN layers: "capital of France" activates the "Paris" memory cells in multiple FFN layers.  
| 25–32 | Final integration: Last token "is" accumulates evidence. High attention to "France" and "capital". Output vector now strongly points toward "Paris" in the vocabulary space.  

5

#### Language Model Head

### Final vector → probability over 128,256 tokens

The output vector for the last position is projected through the unembedding matrix (shape: [4096 × 128256]) and softmaxed to produce probabilities. "Paris" gets probability ~0.94, "Lyon" ~0.02, "Berlin" ~0.001, etc.

Unembedding + Temperature Sampling

P(next_token) = softmax(h_last · W_unembed / τ)

h_last ∈ ℝ^4096  |  W_unembed ∈ ℝ^(4096×128256)  |  τ = temperature (1.0 = no scaling)

6

#### Autoregressive Loop

### Append "Paris", repeat from step 1 for next token

The sampled token "Paris" is appended to the input: `[791, 6864, 315, 9822, 374, 12366]`. The entire forward pass runs again for the now-6-token sequence. This continues until an EOS (end-of-sequence) token is sampled or max length is reached.

This is why generation is slow: **one token per forward pass** , sequentially. KV caching saves the K, V computations from previous steps — only the new token's attention to all prior tokens needs fresh computation.

Summary

## THE BIG PICTURE

### Attention = Communication

Self-attention is how tokens talk to each other. Q asks questions. K advertises information. V delivers the content. The router (softmax) decides who listens to whom.

#### FFN = Memory

Feed-forward layers are the model's database. Each neuron in W₁ is a pattern detector; its corresponding row in W₂ is the associated fact or transformation to apply when that pattern fires.

#### MoE = Conditional Memory

MoE replaces one big FFN database with E specialized databases, and routes each token to the 2 most relevant ones. Total capacity scales with E, but per-token cost stays constant at 2 experts.

#### RoPE = Relative Compass

Without RoPE, the model is positionally blind. RoPE bakes relative distance into the Q·K dot product via rotation, letting the model know "this token is 50 steps behind that one" without hard position limits.

#### Total Params = Knowledge Tank

How much the model can store and know. Determined by architecture size. Requires this much GPU memory to load. Does NOT equal how fast it runs.

#### Active Params = Thinking Cost

How much compute per token. In dense models = total params. In MoE = (active experts / all experts) × total. This determines inference speed and API cost per token.

TRANSFORMER INTERNALS — CONCEPT-FIRST DEEP DIVE  ·  INTERACTIVE EXAMPLES  ·  2025  
All computations shown are simplified for illustrative clarity. Real vectors have thousands of dimensions.
