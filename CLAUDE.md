# wityworks — Jin-Hwa Kim personal homepage

Static site: `index.html` + `static/css/style.css`. No build step.

## Adding a publication entry

Each entry lives in `#pub-list` (`index.html`) as one `<li class="pub-item">`.
Template (copy this shape exactly — don't reintroduce the old inline
"Authors — Venue" single-paragraph format, it was split into two `<p>`s
on purpose):

```html
<li class="pub-item" data-topics="neural-3d world-models">
  <div class="pub-thumb" aria-hidden="true"></div>
  <div>
    <p class="pub-title">Full Paper Title, No Hyperlink</p>
    <p class="pub-meta">Author One*, Author Two, <strong>Jin-Hwa Kim</strong><sup>†</sup>, Last Author<sup>†</sup></p>
    <p class="pub-venue">ECCV 2026 <span class="pub-honor">Spotlight</span></p>
    <div class="pub-footer">
      <div class="pub-links"><a class="pub-btn" href="https://arxiv.org/abs/..." target="_blank">arXiv</a></div>
      <div class="pub-topics"><button type="button" class="pub-topic" data-topic="neural-3d">Neural 3D</button></div>
    </div>
  </div>
</li>
```

Checklist when adding/editing an entry:

- **Author markers**: `*` = co-first author, `<sup>†</sup>` = co-corresponding
  author. Get these from the actual paper/venue page, not guessed — don't
  assume "last author = corresponding" for multi-author NAVER AI Lab papers,
  many mark the last **two** (sometimes three) authors as co-corresponding.
  If a source (e.g. the NAVER careers page) omits a `Jin-Hwa Kim` mark that
  the paper itself confirms, trust the more authoritative/direct source.
  A legend already exists above the list (`.pub-legend`) — don't duplicate it
  per-entry.
- **Venue line (`pub-venue`)**: plain text, own `<p>`, no em dash, no italics.
  Always include the year somewhere in this line (append `, YYYY` if the venue
  name doesn't already contain a year, e.g. `arXiv preprint, 2026`).
  Wrap `Spotlight` / `Oral` / `Best Paper` in `<span class="pub-honor">...</span>`
  (gold) when the venue confirms an honor — check the paper's own project page
  or the author's direct statement over any scraped listing if they conflict.
- **`pub-links` buttons**: one `<a class="pub-btn">` per resource. Label rules:
  - `arxiv.org` link → `arXiv`
  - project/demo homepage → `Project` (or `Demo` if it's explicitly a demo, e.g. HF Spaces)
  - `.pdf` or an ACL Anthology / CVF openaccess page → `PDF`
  - a `HuggingFace` papers/spaces link → `HuggingFace`
  - a code repo → `Code` (a second, distinct repo like a `-threestudio` fork → use its own name, e.g. `Threestudio`)
  - Anything that doesn't fit these → ask, don't guess a label.
- **`pub-topics` buttons**: `<button type="button" class="pub-topic" data-topic="SLUG">Label</button>` —
  the label text must exactly match that slug's filter-bar label (see
  taxonomy below), including entity encoding (`&amp;`, not a raw `&`).
  These are also click-to-filter controls (event-delegated from `#pub-list`),
  so `data-topic` must exactly match one of the six slugs. Keep
  `li[data-topics]` in sync with the same slugs.
- **Thumbnail**: leave `pub-thumb` as an empty placeholder `<div>` unless the
  user has supplied an actual image for that paper (`static/img/pubs/`).
  `.pub-thumb img` picks up a theme-aware `filter: var(--thumb-filter)`
  automatically (a faint warm desaturation in light mode, dimmed+desaturated
  in dark — set alongside the other theme variables at the top of
  style.css) — don't add a per-image inline filter or override this.
- **Featured**: add `data-featured="true"` on the `<li class="pub-item">` if
  the user asks a paper to be marked Featured. A gold ★ is prepended to the
  title automatically via CSS (`.pub-item[data-featured="true"] .pub-title::before`)
  — don't type a literal star into the title text. `featured` is just one more
  value of `data-topic`/`currentTopic` (first pill, star-only label, no
  count badge, no separate axis) — it's handled by the exact same
  single-select `selectTopic()` logic as every other topic, via a special
  case inside `matchesTopic()`. It is the **default** selected filter on
  page load (`currentTopic = 'featured'`). Don't reintroduce a second,
  independent "AND with topic" toggle for this — that was tried and
  deliberately ripped back out for being overcomplicated. When `featured`
  is selected, the "show more" button says "Click to see all publications"
  and clicking it just calls `selectTopic('all')` — it does not expand
  within the featured set.
- **Year / Venue (the "+" accordion)**: every `<li class="pub-item">` also
  gets `data-year="YYYY"` (single year, no honors/venue text) and, only if
  the venue is a top-tier *main-conference* venue (see exclusions below),
  `data-venue="ACRONYM"`. These power the accordion behind the "+" toggle
  next to the main filter row (`#filter-expand-toggle` / `#filter-accordion`)
  — two `<select>` dropdowns (`#filter-year-select`, `#filter-venue-select`),
  not pills; a `change` event on either calls `selectTopic('year:YYYY')` /
  `selectTopic('venue:ACRONYM')`. `matchesTopic()` has special cases for
  both prefixes, plugging into the exact same single-select `selectTopic()`
  — same rule as Featured: don't give this its own independent/combinable
  filter logic. `#filter-accordion` starts `hidden`; note that `.filter-accordion`
  also sets `display: flex`, so there's an explicit `.filter-accordion[hidden] { display: none; }`
  override — without it the `hidden` attribute silently does nothing (this
  broke once already).
  Top-tier venues currently tracked (add a new one here *and* to the
  `<select>` in the Venue accordion group if a new qualifying paper is
  added): NeurIPS, ICLR, ICML, CVPR, ICCV, ECCV, ACL, EMNLP, IJCAI, WACV.
  (`NIPS`, the pre-2018 name, is treated as an alias for NeurIPS.)
  **Workshop papers don't count**, even at an otherwise-tracked venue
  (AAAI was dropped from the `<select>` entirely on this basis — re-add it
  if a main-track AAAI paper shows up). The option text also carries a static
  `(N)` count baked into the label at edit time (there's no live badge for
  the selects) — recompute and update it by hand when entries change:
  ```bash
  grep -oE 'data-venue="[^"]+"' index.html | sort | uniq -c
  grep -oE 'data-year="[^"]+"' index.html | sort | uniq -c
  ```
  Everything else (arXiv preprints, journals, CIKM, CHIL, NAACL, KIISE
  journals, Findings-track papers, etc.) intentionally gets no `data-venue`
  — it just won't show up in that filter, which is correct.
  When a venue string contains more than one plausible year (e.g. a journal
  year plus a later conference re-presentation, or a workshop name that
  happens to embed a different year than the paper's actual year), don't
  regex-guess — use whichever year was the paper's original/actual
  publication year.

## Topic taxonomy (fixed set — don't invent new slugs without asking)

| slug                     | label (used identically in filter bar AND per-paper tags) |
|--------------------------|-------------------------------------------------------------|
| `neural-3d`               | Neural 3D |
| `world-models`             | World Models |
| `multimodal-generation`     | Generation |
| `vision-language`           | Vision &amp; Language |
| `diffusion-safety`          | Safety |
| `ml-theory`                 | Theory |

The filter-bar label and every per-paper `pub-topic` button for a given slug
must read identically (this was flip-flopped a few times — short labels won
out over the old "full name in the paper list" approach). If you rename one,
rename the other to match, and grep to confirm there's no stray copy left
with the old wording:
```bash
grep -oE 'data-topic="([\w-]+)">[^<]*</button>' index.html | sort -u
```

## Counts are automatic — don't hand-edit them

The `.filter-count` badge next to each top filter pill, and the "Show all
publications — N in total" button text, are both computed live by the inline
`<script>` at the bottom of `index.html` (it counts `data-topics` across all
`.pub-item`s on page load). **Never hardcode a count.** After adding/removing
entries, just double check:

1. The new `<li>`'s `data-topics` slugs are spelled exactly like the table
   above (a typo silently drops it from that filter's count).
2. Total `<li class="pub-item">` count and total `pub-topic` button count
   still make sense, e.g. via:
   ```bash
   grep -c 'class="pub-item"' index.html
   grep -oE 'data-topics="[^"]*"' index.html | sed -E 's/data-topics="//; s/"$//' | tr ' ' '\n' | sort | uniq -c
   ```
   and sanity-check the per-slug sum against what the filter badges show in
   the browser.
3. `COLLAPSE_LIMIT` (currently 7) is only about how many "All"-filter items
   show before the "Show all" button appears — it does not need to change
   when adding papers.

## Adding a News entry

Each item lives in `.news-list` (`index.html`) as one `<li>`, newest first.
Two shapes, pick based on length: a plain one-liner (copy an existing short
entry) for most news, or the long-form popover below for multi-paragraph
announcements.

**Long-form with a scroll popover** — use this when the source material
(e.g. a LinkedIn post) is a multi-paragraph announcement. Don't paste the
full text into the visible one-liner; summarize that to a single sentence,
and put the full original text behind a hover/focus popover instead:

```html
<li><span class="news-date">2026.08.03</span>📣 Welcoming <a href="https://jho-yonsei.github.io/" target="_blank">Dr. Jungho Lee</a> to Generation Research, NAVER AI Lab as a Research Scientist working on city-scale physical world models. <span class="news-popover" tabindex="0"><span class="news-popover-trigger" aria-hidden="true"><svg viewBox="0 0 20 14" width="18" height="13"><rect x="1" y="4.5" width="2.4" height="7.5" rx="1.2" fill="var(--gold)"/><rect x="16.6" y="4.5" width="2.4" height="7.5" rx="1.2" fill="var(--gold)"/><path d="M3.4,4.7 Q10,2.6 16.6,4.7 L16.6,11.8 Q10,13.9 3.4,11.8 Z" fill="var(--gold)" opacity="0.18" stroke="var(--gold)" stroke-width="0.8"/><line x1="6" y1="6.5" x2="14" y2="6.5" stroke="var(--gold)" stroke-width="0.7"/><line x1="6" y1="8.3" x2="14" y2="8.3" stroke="var(--gold)" stroke-width="0.7"/><line x1="6" y1="10.1" x2="11.5" y2="10.1" stroke="var(--gold)" stroke-width="0.7"/></svg></span><div class="news-popover-box" role="tooltip"><div class="popover-inner">
  <p class="popover-date">3 Aug 2026</p>
  <p class="popover-headline">📣 Welcoming Dr. Jungho Lee to Generation Research, NAVER AI Lab!</p>
  <p>...full original paragraphs, unedited...</p>
  <p class="popover-foot">J.H.</p>
</div></div></span></li>
```

Notes on this pattern:

- The parchment-scroll SVG (rolled ends + a few text-line strokes, all
  `var(--gold)`) is the trigger icon — reuse this exact markup, don't swap
  in an emoji (💬 was tried and rejected as too generic/chat-app-flavored).
- `<span class="news-popover-box">` and `<div class="popover-inner">` are
  intentionally `<div>`s (they hold `<p>` tags — a `<span>` wrapping `<p>` is
  invalid HTML), while `.news-popover` and `.news-popover-trigger` stay
  `<span>` so the trigger sits inline inside the running sentence.
- `.news-popover-box` has `padding-top: 10px` instead of `margin-top` on
  purpose — this is the "invisible bridge" that keeps the CSS `:hover` state
  alive while the mouse moves from the trigger down into the popover. Using
  `margin-top` instead would create a dead zone and the popover would
  vanish before the pointer reaches it. Don't "simplify" this to a margin.
- `tabindex="0"` + `:focus-within` on `.news-popover` make it keyboard-
  accessible (Tab to it, popover shows) — keep both when copying the pattern.
- Inside the popover: `.popover-date` (the dateline, plain weight, muted
  color, sits above the quote), `.popover-headline` (bold — the first
  line of the original post, e.g. its own title/exclamation), then plain
  `<p>`s for the rest of the original text verbatim, then `.popover-foot`
  (italic, right-aligned, initials only — signature-style, no date; the
  date already lives up top in `.popover-date`, don't repeat it here).
- The `border-top: 3px solid var(--gold)` on `.popover-inner` is deliberate
  (a small nod to a Greek entablature/architrave line) — a triangle/circle/
  square corner mark was tried in this same spot and removed for being too
  much decoration on a small utility popup; don't re-add it.

## Layout/format gotchas (things that broke before, don't reintroduce)

- `pub-links` + `pub-topics` must be siblings inside one `.pub-footer` div
  (flex row, topics pushed right via `margin-left:auto`) — don't nest a
  second `.pub-footer` around just the topics div, and don't leave an entry
  with `pub-topics` sitting outside any `.pub-footer` (both are real bugs
  that happened here before).
- Don't add a `border-top` fix via CSS `:first-child` alone — the topic
  filter hides items with `display:none` without reordering the DOM, so the
  *visually* first visible item is often not the DOM's `:first-child`. The
  JS already handles this by toggling `.pub-item--first-visible` on whichever
  item is actually first-rendered after a filter change — leave that logic
  alone.
- Author name spelling/hyphenation should match the paper's own byline
  (e.g. "Yong-Hyun Park", not "Yong Hyun Park") — when two sources disagree,
  ask rather than pick one silently.
