---
title: Why Attention Is Normalized with Softmax
category: ml-concepts
categoryLabel: ML Concepts
date: 2026-08-10
readTime: 6 min read
summary: Revisiting softmax's role in turning query-key dot products into a probability distribution, alongside the temperature parameter.
visibility: public
---

Attention scores start life as raw dot products between a query vector $q$ and a set of key vectors $k_i$. On their own these numbers are unbounded and not comparable across positions, so we need something that turns them into a set of non-negative weights that sum to one — a probability distribution over the values we're about to mix.

## Inline math

The unnormalized score for position $i$ is $s_i = q \cdot k_i / \sqrt{d_k}$, where $d_k$ is the key dimension. Dividing by $\sqrt{d_k}$ keeps the variance of $s_i$ roughly constant as $d_k$ grows — without it, dot products in high dimensions blow up and push softmax into a near-one-hot regime with vanishing gradients.

## Display math

Softmax with temperature $\tau$ (here $\tau = \sqrt{d_k}$ folded in) is:

$$
\mathrm{softmax}(x_i) = \frac{\exp(x_i / \tau)}{\sum_{j} \exp(x_j / \tau)}
$$

As $\tau \to 0$ this sharpens toward a one-hot argmax; as $\tau \to \infty$ it flattens toward a uniform average over all positions. The $1/\sqrt{d_k}$ scaling in standard attention is exactly this temperature knob, chosen to keep the pre-softmax logits at a consistent scale regardless of head dimension.

## Why softmax specifically

A few properties make softmax the natural choice over, say, a plain normalized sum $s_i / \sum_j s_j$:

- Differentiable everywhere, unlike a hard argmax.
- Shift-invariant: $\mathrm{softmax}(x + c) = \mathrm{softmax}(x)$ for any constant $c$, which is what makes the usual "subtract the max before exponentiating" trick numerically safe.
- Monotonic in each $x_i$, so larger scores always get larger weight — no sign issues the way a raw normalized sum would have with negative dot products.

*(Sample post — used to work out this site's math-in-markdown conventions.)*
