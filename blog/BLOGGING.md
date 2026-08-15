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

### Step 2: Write Content
* Use standard Markdown headers (`##`, `###`).
* Keep inline math inside single `$ ... $` and display math inside double `$$ ... $$`.
* Follow the LaTeX formatting rule (avoid spacing primitives like `\!` or `\,`).

### Step 3: Update Blog Features & Post Counts (`manifest.js`)
Since this site uses static file hosting without dynamic directory indexing, post listing counts and metadata rely on `root/blog/manifest.js`.

**Option A — Automated (via Terminal):**
Run the sync script to auto-generate `manifest.js` from all `.md` frontmatter:
python3 blog/sync_manifest.py

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
3. Keep `BLOG_POSTS` sorted by `date` in descending order so counting and sorting work seamlessly on `blog.html`.