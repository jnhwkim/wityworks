---
title: Why Attention Is Normalized with Softmax
category: ml-concepts
categoryLabel: ML Concepts
date: 2026-08-15
readTime: 6 min read
summary: Revisiting softmax's role in turning query-key dot products into a probability distribution, alongside the temperature parameter.
visibility: public
---

Attention scores start life as raw dot products between query and key vectors. The goal is to produce a weighted mixture of value vectors — formally,

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V$$

where $Q$, $K$, $V$ are matrices whose rows are queries, keys, and values respectively. The softmax output is itself a matrix of the same shape as $QK^\top$, so the product with $V$ is ordinary matrix multiplication. For those weights to define a valid mixture at each position, each row must be non-negative and sum to one: a probability distribution over positions.

The unnormalized score for position $i$ is $s_i = q^\top k_i / \sqrt{d_k}$, where $d_k$ is the key dimension. The scaling is not cosmetic: if $q_j, k_{ij} \sim \mathcal{N}(0,1)$, then $q^\top k_i = \sum_{j=1}^{d_k} q_j k_{ij}$ has variance $d_k$, so its standard deviation grows as $\sqrt{d_k}$. Dividing by $\sqrt{d_k}$ restores unit variance regardless of head size — without it, dot products in high dimensions blow up and push softmax into a near-one-hot regime.

Softmax with temperature $\tau$ (here $\tau = \sqrt{d_k}$ folded in) is:

$$
\mathrm{softmax}(x_i) = \frac{\exp(x_i / \tau)}{\sum_{j} \exp(x_j / \tau)}
$$

As $\tau \to 0$ this sharpens toward a one-hot argmax; as $\tau \to \infty$ it flattens toward a uniform average over all positions. The $1/\sqrt{d_k}$ scaling in standard attention is exactly this temperature knob, chosen to keep the pre-softmax logits at a consistent scale regardless of head dimension. When one logit dominates, softmax output approaches 1 there and 0 everywhere else; the Jacobian of softmax becomes near-zero, so gradients through the attention weights effectively vanish during backprop.

## Why softmax specifically

Alternatives like sparsemax or per-element sigmoid attention exist, but softmax remains the default. A few properties explain why, compared to a plain normalized sum $s_i / \sum_j s_j$:

- Differentiable everywhere, unlike a hard argmax.
- Shift-invariant: $\mathrm{softmax}(x + c) = \mathrm{softmax}(x)$ for any constant $c$, which is what makes the usual "subtract the max before exponentiating" trick numerically safe.
- Monotonic in each $x_i$, so larger scores always get larger weight — no sign issues the way a raw normalized sum would have with negative dot products.