---
title: Why KL Divergence Isn't a Distance
category: math-stats-notes
categoryLabel: Math & Stats Notes
date: 2026-07-28
readTime: 4 min read
summary: Working through asymmetry and the triangle-inequality violation by hand — and why it's still the tool of choice.
visibility: public
---

KL divergence between two distributions $P$ and $Q$ over the same support is defined as

$$
D_{\mathrm{KL}}(P \parallel Q) = \sum_{x} P(x) \log \frac{P(x)}{Q(x)}
$$

It's tempting to read this as "the distance between $P$ and $Q$," but it fails two of the three properties a real distance metric needs.

## Asymmetry

$D_{\mathrm{KL}}(P \parallel Q) \neq D_{\mathrm{KL}}(Q \parallel P)$ in general. A quick two-outcome example: let $P = (0.9, 0.1)$ and $Q = (0.5, 0.5)$. Then

$$
D_{\mathrm{KL}}(P \parallel Q) = 0.9 \log \frac{0.9}{0.5} + 0.1 \log \frac{0.1}{0.5}
$$

versus

$$
D_{\mathrm{KL}}(Q \parallel P) = 0.5 \log \frac{0.5}{0.9} + 0.5 \log \frac{0.5}{0.1}
$$

Plugging in numbers gives two different values — the divergence "from $P$ to $Q$" penalizes different mismatches than "from $Q$ to $P$," because the expectation is always taken under the first argument.

## Triangle inequality

Even ignoring asymmetry, there's no guarantee that $D_{\mathrm{KL}}(P \parallel R) \le D_{\mathrm{KL}}(P \parallel Q) + D_{\mathrm{KL}}(Q \parallel R)$ for an arbitrary intermediate $Q$. Counterexamples are straightforward to construct with three-outcome distributions where $Q$ places near-zero mass on an outcome that both $P$ and $R$ weight heavily — the $\log(1/Q(x))$ term spikes and breaks the inequality.

## Why we use it anyway

None of this makes $D_{\mathrm{KL}}$ the wrong tool — it's not trying to be a metric. It falls out directly as the expected extra number of bits needed to code samples from $P$ using a code optimized for $Q$ instead, i.e. $\mathbb{E}_{x \sim P}[-\log Q(x)] - \mathbb{E}_{x \sim P}[-\log P(x)]$. That asymmetry is the point: $D_{\mathrm{KL}}(P \parallel Q)$ answers "how surprised am I, on average, if reality is $P$ but I modeled it as $Q$" — a question that is inherently directional.

*(Sample post — used to work out this site's math-in-markdown conventions.)*
