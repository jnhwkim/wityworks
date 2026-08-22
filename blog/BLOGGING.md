# Blogging Guidelines & Publishing Workflow

A guide for authoring blog posts using web-based AI tools (e.g., Gemini AI Plus) without relying on local IDE automation tools.

---

## 1. LaTeX Formatting Pitfalls (KaTeX Engine)

When writing math blocks or inline math for this site:

* **Avoid LaTeX Spacing Primitives:** Do NOT use commands like `\!`, `\,`, `\;`, or `\:` inside inline `$...$` or display `$$...$$` math blocks.
* **Root Cause:** The renderer passes certain LaTeX spacing commands through as literal characters rather than interpreting them properly.
* **Best Practice:** Stick to standard plain spaces inside math expressions to avoid rendering issues.

---

## 2. Step-by-Step Article Publishing Walkthrough

### Step 1: Create the Article File
Create a standalone Markdown file inside its corresponding category folder:
`root/blog/<category-slug>/<article-slug>.md`

Include the required frontmatter metadata block at the top:

---
title: Your Article Title
category: ml-concepts
categoryLabel: ML Concepts
date: YYYY-MM-DD
readTime: 5 min read
summary: A short description of the article.
visibility: public
---

### Optional X discussion

To place an X conversation at the bottom of a public article, publish a post
linking to that article, then add its canonical post URL to the frontmatter:

```text
xPostUrl: https://x.com/your-handle/status/1234567890123456789
```

The site renders a compact **Join the conversation** button that opens X's
reply composer for the same post. Omit `xPostUrl` until the post has been
published; no empty discussion panel is rendered.

### Step 2: Write Content
* Use standard Markdown headers (`##`, `###`).
* Keep inline math inside single `$ ... $` and display math inside double `$$ ... $$`.
* Follow the LaTeX formatting rule (avoid spacing primitives like `\!` or `\,`).

### Step 3: Update Blog Features, Post Counts, and RSS (`manifest.js`, `rss.xml`)
Since this site uses static file hosting without dynamic directory indexing, post listing counts and metadata rely on `root/blog/manifest.js`.

**Option A — Automated (via Terminal):**
Run the sync script to auto-generate `manifest.js` from all `.md` frontmatter and
the full-content RSS feed at `root/blog/rss.xml`:
python3 blog/sync_manifest.py

The feed uses `https://wityworks.com` from `CNAME` for canonical URLs. Set
`SITE_URL` when building for another canonical domain (for example,
`SITE_URL=https://example.com python3 blog/sync_manifest.py`). Post GUIDs are
their canonical category-and-slug URLs, so edits to the title or body do not
change feed identity. Optional `author`, `cover`, or `coverImage` frontmatter
is included in RSS when present.

**Option B — Manual (Web/AI Update):**
If working solely in a browser/web-AI interface:
1. Open `root/blog/manifest.js`.
2. Add or update the corresponding entry in the `BLOG_POSTS` array:
   {
     category: 'ml-concepts',
     categoryLabel: 'ML Concepts',
     slug: 'your-article-slug',
     title: 'Your Article Title',
     summary: 'A short description of the article.',
     date: 'YYYY-MM-DD',
     readTime: '5 min read',
     visibility: 'public',
   }
3. Keep `BLOG_POSTS` sorted by `date` in descending order so counting and sorting work seamlessly on `index.html` and `root/blog/index.html`.

## 3. Illustration Guidelines (Vintage Line Art)

When generating vector/line art illustrations for scientific blog posts, use the following standardized prompt template and rules to maintain consistent aesthetics across all articles.

### Prompt Template
```text
A minimal vintage fountain pen line art illustration of [TARGET_SUBJECT]. 
Fine line drawing style, micro-hatched straight lines and cross-hatching for shading and depth. 
No solid fills, clean background, vintage scientific sketchbook illustration style. 
All line strokes in monochrome brownish-gray color (#55503f). 
High precision, elegant vector line art, isolated on pure white background.
