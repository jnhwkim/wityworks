# wityworks — Jin-Hwa Kim personal homepage

Static site: `index.html` + `static/css/style.css`. No build step.

## Browser usage policy

Don't use Claude's built-in browser tool for this project (visual checks,
the crop tool, anything) unless the user explicitly asks for it. Default:
start a local server (`python3 -m http.server <port>` in the relevant dir)
and hand the user the `http://localhost:<port>/...` URL to open in their own
browser (Safari). `file://` downloads from the crop tool silently fail to
save — the server fixes that too, so prefer it even when the built-in
browser isn't the issue.

## Cropping a pub-thumb image

Crop tool: `tools/thumb-crop/crop-tool.html` (lives on the `tools` branch,
not `draft` — pull with
`git show origin/tools:tools/thumb-crop/crop-tool.html > tools/thumb-crop/crop-tool.html`
if missing). Standalone HTML/JS page, crops a source image/video frame to
16:9, pan/zoom + white-fill eraser. Extend this one, don't rewrite. Serve it
locally per the Browser usage policy above.

Each paper is one entry in the `PAPERS` array at the top of the script
(num, label, candidate image/video filenames). To add a paper: append an
entry, then drop the source image(s)/video(s) into `tools/thumb-crop/` next
to the script with matching filenames — these sources and any cropped
output PNGs stay out of git (heavy, per-run, not durable assets).

"Download 344px PNG" saves `final_NN_344x194.png`. Convert it to WebP and
place it at `static/img/pubs/<slug>.webp` — every thumbnail in that folder is
344x194. The single file covers both breakpoints:
`.pub-thumb img` is `object-fit: cover` at 160x90 on desktop and 344x194 on
mobile (style.css:475,493), so the browser just downscales the same image
for desktop.

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

- **Author markers**: `*` = co-first author, `<sup>†</sup>` = co-corresponding.
  Get these from the paper/venue page, not guessed — many multi-author NAVER
  AI Lab papers mark the last **two or three** authors as co-corresponding,
  don't assume "last author only". If a source (e.g. NAVER careers page)
  omits a mark the paper itself confirms, trust the more direct source. The
  legend above the list (`.pub-legend`) already explains the marks — don't
  repeat it per-entry.
- **Venue line (`pub-venue`)**: plain text, own `<p>`, no em dash, no italics.
  Always include the year (append `, YYYY` if the venue name lacks one, e.g.
  `arXiv preprint, 2026`). Wrap `Spotlight`/`Oral`/`Best Paper` in
  `<span class="pub-honor">...</span>` (gold) only when the paper's own
  project page or a direct author statement confirms the honor — not a
  scraped listing.
- **`pub-links` buttons**: one `<a class="pub-btn">` per resource:
  `arxiv.org` → `arXiv`; project/demo homepage → `Project` (`Demo` if
  explicitly a demo, e.g. HF Spaces); `.pdf` or ACL Anthology/CVF openaccess
  → `PDF`; HuggingFace papers/spaces → `HuggingFace`; code repo → `Code`
  (a second distinct repo, e.g. a `-threestudio` fork, gets its own name).
  Anything else → ask, don't guess.
- **`pub-topics` buttons**: `<button type="button" class="pub-topic" data-topic="SLUG">Label</button>`.
  Label must exactly match that slug's filter-bar label below, entities
  included (`&amp;` not `&`). These double as click-to-filter controls
  (event-delegated from `#pub-list`), so `data-topic` must be one of the six
  slugs, and `li[data-topics]` must list the same slugs.
- **Thumbnail**: leave `pub-thumb` an empty placeholder `<div>` unless a real
  image exists in `static/img/pubs/` (see cropping section above).
  `.pub-thumb img` auto-applies a theme-aware `filter: var(--thumb-filter)`
  — don't add a per-image override.
- **Featured**: add `data-featured="true"` to mark a paper Featured; a gold ★
  is prepended via CSS (`.pub-item[data-featured="true"] .pub-title::before`)
  — never type a literal star into the title. `featured` is just another
  `data-topic`/`currentTopic` value (first pill, star-only label, no count
  badge), handled by the same single-select `selectTopic()` via a special
  case in `matchesTopic()` — it's the default filter on load
  (`currentTopic = 'featured'`). Don't reintroduce a second "AND with topic"
  toggle here — tried before, ripped out for being overcomplicated. Under
  `featured`, "show more" reads "Click to see all publications" and just
  calls `selectTopic('all')`; it doesn't expand within the featured set.
- **Year / Venue (the "+" accordion)**: every `<li>` gets `data-year="YYYY"`
  and, only for top-tier *main-conference* venues, `data-venue="ACRONYM"`.
  These feed two `<select>`s behind `#filter-expand-toggle` /
  `#filter-accordion` (not pills); `change` calls `selectTopic('year:YYYY')`
  / `selectTopic('venue:ACRONYM')` — same single-select `matchesTopic()`
  special-cased for both prefixes, no separate filter logic.
  `#filter-accordion` starts `hidden`; `.filter-accordion` also sets
  `display: flex`, so there's an explicit
  `.filter-accordion[hidden] { display: none; }` override — without it
  `hidden` silently does nothing (broke once already).
  Top-tier venues tracked (add new ones here *and* to the Venue `<select>`):
  NeurIPS, ICLR, ICML, CVPR, ICCV, ECCV, ACL, EMNLP, IJCAI, WACV (`NIPS` is
  the NeurIPS alias). **Workshop papers don't count** even at a tracked venue
  (AAAI was dropped entirely on this basis — re-add if a main-track AAAI
  paper shows up). The `(N)` counts in the `<select>` option text are static,
  not live — recompute by hand after entries change:
  ```bash
  grep -oE 'data-venue="[^"]+"' index.html | sort | uniq -c
  grep -oE 'data-year="[^"]+"' index.html | sort | uniq -c
  ```
  Everything else (arXiv preprints, journals, CIKM, CHIL, NAACL, KIISE
  journals, Findings-track, etc.) intentionally gets no `data-venue`.
  If a venue string contains more than one plausible year (a journal year
  plus a later re-presentation, or a workshop name embedding a different
  year), use the paper's actual/original publication year — don't regex-guess.

## Topic taxonomy (fixed set — don't invent new slugs without asking)

| slug                     | label (used identically in filter bar AND per-paper tags) |
|--------------------------|-------------------------------------------------------------|
| `neural-3d`               | Neural 3D |
| `world-models`             | World Models |
| `multimodal-generation`     | Generation |
| `vision-language`           | Vision &amp; Language |
| `diffusion-safety`          | Safety |
| `ml-theory`                 | Theory |

Filter-bar label and every per-paper `pub-topic` button for a slug must read
identically (short labels won out over full names — don't flip back). If you
rename one, rename the other and grep for stragglers:
```bash
grep -oE 'data-topic="([\w-]+)">[^<]*</button>' index.html | sort -u
```

## Counts are automatic — don't hand-edit them

`.filter-count` badges and the "Show all publications — N in total" text are
computed live by the inline `<script>` at the bottom of `index.html` from
`data-topics` on page load. **Never hardcode a count.** After adding/removing
entries:

1. Check the new `<li>`'s `data-topics` slugs are spelled exactly per the
   table above (a typo silently drops it from that filter's count).
2. Sanity-check totals:
   ```bash
   grep -c 'class="pub-item"' index.html
   grep -oE 'data-topics="[^"]*"' index.html | sed -E 's/data-topics="//; s/"$//' | tr ' ' '\n' | sort | uniq -c
   ```
3. `COLLAPSE_LIMIT` (currently 7, how many "All"-filter items show before
   "Show all" appears) doesn't need to change when adding papers.

## Adding a News entry

Each item lives in `.news-list` (`index.html`) as one `<li>`, newest first.
Two shapes: a plain one-liner (copy an existing short entry) for most news,
or the long-form popover below for multi-paragraph announcements.

**Long-form with a scroll popover** — use when the source (e.g. a LinkedIn
post) is a multi-paragraph announcement. Summarize it to one visible
sentence and put the full original text behind a hover/focus popover:

```html
<li><span class="news-date">2026.08.03</span>📣 Welcoming <a href="https://jho-yonsei.github.io/" target="_blank">Dr. Jungho Lee</a> to Generation Research, NAVER AI Lab as a Research Scientist working on city-scale physical world models. <span class="news-popover" tabindex="0"><span class="news-popover-trigger" aria-hidden="true"><svg viewBox="0 0 12 14" width="13" height="15"><rect x="1.3" y="1.8" width="9.4" height="1.6" rx="0.8" fill="var(--gold)" fill-opacity="0.55" stroke="color-mix(in srgb, var(--gold) 55%, white)" stroke-width="0.5"/><rect x="1" y="3.4" width="10" height="10" fill="var(--gold)" fill-opacity="0.14" stroke="color-mix(in srgb, var(--gold) 55%, white)" stroke-width="0.5"/><line x1="2.6" y1="6" x2="9.4" y2="6" stroke="var(--gold)" stroke-width="0.6"/><line x1="2.6" y1="8.2" x2="9.4" y2="8.2" stroke="var(--gold)" stroke-width="0.6"/><line x1="2.6" y1="10.4" x2="7.4" y2="10.4" stroke="var(--gold)" stroke-width="0.6"/></svg></span><div class="news-popover-box" role="tooltip"><div class="popover-inner">
  <p class="popover-date">3 Aug 2026</p>
  <p class="popover-headline">📣 Welcoming Dr. Jungho Lee to Generation Research, NAVER AI Lab!</p>
  <p>...full original paragraphs, unedited...</p>
  <p class="popover-foot">J.H.</p>
</div></div></span></li>
```

Notes on this pattern:

- The rectangular-tablet SVG (flat box + a brighter rounded bar on top, echoing
  the popover box's own shape/gold accent) is the trigger icon — reuse this
  exact markup, don't swap in an emoji (💬 was tried and rejected as too
  chat-app-flavored; a parchment-scroll shape and a rounded-top tombstone were
  also tried and dropped — the scroll was too tall/fussy at inline text size,
  and the rounded top didn't read as clearly).
- `.news-popover-box`/`.popover-inner` are `<div>`s (they hold `<p>`s — a
  `<span>` wrapping `<p>` is invalid HTML); `.news-popover`/
  `.news-popover-trigger` stay `<span>` to sit inline in the sentence.
- `.news-popover-box` uses `padding-top: 10px`, not `margin-top` — this is
  the invisible bridge keeping `:hover` alive while the pointer moves from
  trigger to popover. A margin would create a dead zone and the popover
  would vanish early. Don't "simplify" this to a margin.
- `tabindex="0"` + `:focus-within` make it keyboard-accessible — keep both.
- Inside the popover: `.popover-date` (dateline, muted, above the quote),
  `.popover-headline` (bold, the post's own title/first line), plain `<p>`s
  for the rest verbatim, then `.popover-foot` (italic, right-aligned,
  initials only — no date, that's already in `.popover-date`).
- `.popover-inner`'s `border-top: 3px solid var(--gold)` is a deliberate nod
  to a Greek entablature line — a corner mark was tried in this spot and
  removed as too much decoration; don't re-add it.

## Layout/format gotchas (things that broke before, don't reintroduce)

- `pub-links` + `pub-topics` must be siblings inside one `.pub-footer` div
  (flex row, topics pushed right via `margin-left:auto`) — don't nest a
  second `.pub-footer` around just the topics div, and don't leave
  `pub-topics` outside any `.pub-footer` (both are real past bugs).
- Don't fix border-top via CSS `:first-child` alone — topic filtering hides
  items with `display:none` without reordering the DOM, so the visually
  first visible item often isn't the DOM's `:first-child`. JS already
  toggles `.pub-item--first-visible` on whichever item renders first after a
  filter change — leave that logic alone.
- Author name spelling/hyphenation should match the paper's own byline
  (e.g. "Yong-Hyun Park", not "Yong Hyun Park") — if two sources disagree,
  ask rather than pick one silently.
