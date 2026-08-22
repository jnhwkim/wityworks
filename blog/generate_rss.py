#!/usr/bin/env python3
"""Generate the static RSS 2.0 feed for the blog.

The browser uses marked.js from a CDN to render posts.  RSS generation must
also work offline during deployment, so this module deliberately renders the
portable Markdown subset used by the posts and strips active HTML.
"""
from __future__ import annotations

import argparse
import html
import os
import pathlib
import re
from datetime import date, datetime, timedelta, timezone
from email.utils import format_datetime
from html.parser import HTMLParser
from urllib.parse import urljoin
from xml.etree import ElementTree as ET


BLOG_DIR = pathlib.Path(__file__).parent
PROJECT_DIR = BLOG_DIR.parent
RSS_PATH = BLOG_DIR / "rss.xml"
RSS_LIMIT = 30
CONTENT_NS = "http://purl.org/rss/1.0/modules/content/"
MEDIA_NS = "http://search.yahoo.com/mrss/"
KST = timezone(timedelta(hours=9), name="KST")
FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
FENCE_RE = re.compile(r"^```([^`]*)$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
LIST_RE = re.compile(r"^\s*[-*+]\s+(.+)$")
ORDERED_LIST_RE = re.compile(r"^\s*\d+[.)]\s+(.+)$")
IMAGE_RE = re.compile(r"!\[([^]]*)\]\(([^ )]+)(?:\s+\"[^\"]*\")?\)")
LINK_RE = re.compile(r"(?<!!)\[([^]]+)\]\(([^ )]+)(?:\s+\"[^\"]*\")?\)")


def site_url() -> str:
    """Return the deployment URL, favoring explicit configuration."""
    configured = os.environ.get("SITE_URL", "").strip()
    if configured:
        return configured.rstrip("/")
    cname_path = PROJECT_DIR / "CNAME"
    if cname_path.is_file():
        domain = cname_path.read_text(encoding="utf-8").strip()
        if domain:
            return "https://" + domain.rstrip("/")
    raise ValueError("SITE_URL is not set and CNAME does not contain a site domain")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    data = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        data[key.strip()] = value.strip()
    return data, text[match.end():]


def absolute_url(value: str, base_url: str, post_url: str | None = None) -> str:
    """Resolve URLs exactly as the browser-rendered blog page does."""
    value = value.strip()
    if not value or value.startswith(("#", "mailto:", "tel:", "data:")):
        return (post_url + value) if value.startswith("#") and post_url else value
    return urljoin(base_url + "/blog/", value)


class PortableHtml(HTMLParser):
    """Keep safe, reader-portable HTML and make URLs absolute."""

    allowed_tags = {
        "a", "b", "blockquote", "br", "code", "del", "em", "figure",
        "figcaption", "h1", "h2", "h3", "h4", "h5", "h6", "hr", "i",
        "img", "li", "ol", "p", "pre", "strong", "table", "tbody", "td",
        "th", "thead", "tr", "ul",
    }
    void_tags = {"br", "hr", "img"}
    allowed_attrs = {"a": {"href", "title"}, "img": {"src", "alt", "title", "width", "height"}}

    def __init__(self, base_url: str, post_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.post_url = post_url
        self.parts: list[str] = []
        self.open_tags: list[str] = []
        self.suppressed_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in {"script", "iframe", "object", "embed", "style"}:
            self.suppressed_depth += 1
            return
        if self.suppressed_depth or tag not in self.allowed_tags:
            return
        rendered_attrs = []
        for name, value in attrs:
            name = name.lower()
            if name != "id" and name not in self.allowed_attrs.get(tag, set()) or value is None:
                continue
            if name in {"href", "src"}:
                value = absolute_url(value, self.base_url, self.post_url)
            rendered_attrs.append(f' {name}="{html.escape(value, quote=True)}"')
        self.parts.append("<" + tag + "".join(rendered_attrs) + ">")
        if tag not in self.void_tags:
            self.open_tags.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in {"script", "iframe", "object", "embed", "style"}:
            self.suppressed_depth = max(0, self.suppressed_depth - 1)
            return
        if self.suppressed_depth or tag not in self.allowed_tags or tag in self.void_tags:
            return
        if tag in self.open_tags:
            while self.open_tags:
                opened = self.open_tags.pop()
                self.parts.append(f"</{opened}>")
                if opened == tag:
                    break

    def handle_data(self, data):
        if not self.suppressed_depth:
            self.parts.append(html.escape(data))

    def output(self) -> str:
        while self.open_tags:
            self.parts.append(f"</{self.open_tags.pop()}>")
        return "".join(self.parts)


def sanitize_html(fragment: str, base_url: str, post_url: str) -> str:
    parser = PortableHtml(base_url, post_url)
    parser.feed(fragment)
    parser.close()
    return parser.output()


def render_inline(text: str, base_url: str, post_url: str) -> str:
    """Render inline Markdown while preserving sanitized embedded HTML."""
    tokens: list[str] = []

    def stash(value: str) -> str:
        tokens.append(value)
        return f"\x00RSS{len(tokens) - 1}\x00"

    def image(match):
        alt, src = match.groups()
        return stash(f'<img src="{html.escape(absolute_url(src, base_url, post_url), quote=True)}" alt="{html.escape(alt, quote=True)}">')

    def link(match):
        label, href = match.groups()
        return stash(f'<a href="{html.escape(absolute_url(href, base_url, post_url), quote=True)}">{render_inline(label, base_url, post_url)}</a>')

    # Math is rendered client-side by KaTeX on the site. Keep its source
    # untouched here; in particular, LaTeX underscores are not emphasis.
    text = re.sub(r"\$\$.*?\$\$|\$(?:\\.|[^$])*\$", lambda m: stash(html.escape(m.group(0))), text, flags=re.DOTALL)
    text = IMAGE_RE.sub(image, text)
    text = LINK_RE.sub(link, text)
    # Embedded HTML appears in several existing posts.  Stash it before
    # escaping the remaining Markdown text.
    text = re.sub(r"<[^>]+>", lambda m: stash(sanitize_html(m.group(0), base_url, post_url)), text)
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*|__([^_]+)__", lambda m: f"<strong>{m.group(1) or m.group(2)}</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)|(?<!_)_([^_]+)_(?!_)", lambda m: f"<em>{m.group(1) or m.group(2)}</em>", text)
    for index, token in enumerate(tokens):
        text = text.replace(html.escape(f"\x00RSS{index}\x00"), token)
    return text


def heading_id(text: str) -> str:
    """Match the small slugifier used by static/js/blog-page.js."""
    plain = re.sub(r"<[^>]*>", "", text).lower()
    plain = re.sub(r"[^A-Za-z0-9_\s-]", "", plain)
    plain = re.sub(r"[\s_]+", "-", plain)
    return plain.strip("-")


def markdown_to_html(markdown: str, base_url: str, post_url: str) -> str:
    """Render the portable block-level Markdown subset used by this static blog."""
    lines = markdown.replace("\r\n", "\n").split("\n")
    output: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    list_tag: str | None = None
    code_lines: list[str] = []
    code_language = ""
    in_code = False
    html_block: list[str] = []
    html_block_tag: str | None = None

    def flush_paragraph():
        if paragraph:
            output.append("<p>" + render_inline(" ".join(line.strip() for line in paragraph), base_url, post_url) + "</p>")
            paragraph.clear()

    def flush_list():
        nonlocal list_tag
        if list_items:
            output.append(f"<{list_tag}>" + "".join(f"<li>{render_inline(item, base_url, post_url)}</li>" for item in list_items) + f"</{list_tag}>")
            list_items.clear()
        list_tag = None

    for line in lines:
        if html_block_tag:
            html_block.append(line)
            if re.search(rf"</{html_block_tag}\s*>", line, re.IGNORECASE):
                output.append(sanitize_html("\n".join(html_block), base_url, post_url))
                html_block, html_block_tag = [], None
            continue
        fence = FENCE_RE.match(line)
        if fence:
            flush_paragraph(); flush_list()
            if not in_code:
                code_lines, code_language, in_code = [], fence.group(1).strip(), True
                continue
            klass = f' class="language-{html.escape(code_language, quote=True)}"' if code_language else ""
            output.append(f"<pre><code{klass}>{html.escape(chr(10).join(code_lines))}</code></pre>")
            code_lines, code_language, in_code = [], "", False
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line.strip():
            flush_paragraph(); flush_list()
            continue
        if line.strip() in {"---", "***", "___"}:
            flush_paragraph(); flush_list(); output.append("<hr>")
            continue
        heading = HEADING_RE.match(line)
        if heading:
            flush_paragraph(); flush_list()
            level, title = len(heading.group(1)), heading.group(2)
            output.append(f'<h{level} id="{heading_id(title)}">{render_inline(title, base_url, post_url)}</h{level}>')
            continue
        if line.startswith("> "):
            flush_paragraph(); flush_list()
            output.append("<blockquote><p>" + render_inline(line[2:], base_url, post_url) + "</p></blockquote>")
            continue
        unordered = LIST_RE.match(line)
        ordered = ORDERED_LIST_RE.match(line)
        if unordered or ordered:
            flush_paragraph()
            tag, item = ("ul", unordered.group(1)) if unordered else ("ol", ordered.group(1))
            if list_tag and list_tag != tag:
                flush_list()
            list_tag = tag
            list_items.append(item)
            continue
        if line.lstrip().startswith("<"):
            flush_paragraph(); flush_list()
            block = re.match(r"\s*<(figure|table|blockquote|div)\b", line, re.IGNORECASE)
            if block and not re.search(rf"</{block.group(1)}\s*>", line, re.IGNORECASE):
                html_block, html_block_tag = [line], block.group(1).lower()
                continue
            output.append(sanitize_html(line, base_url, post_url))
            continue
        flush_list()
        paragraph.append(line)
    if in_code:
        raise ValueError("unclosed fenced code block")
    if html_block_tag:
        raise ValueError(f"unclosed HTML <{html_block_tag}> block")
    flush_paragraph(); flush_list()
    return "\n".join(part for part in output if part)


def rfc822_date(iso_date: str) -> str:
    try:
        published = date.fromisoformat(iso_date)
    except ValueError as exc:
        raise ValueError(f"invalid date '{iso_date}' (expected YYYY-MM-DD)") from exc
    return format_datetime(datetime.combine(published, datetime.min.time(), tzinfo=KST))


def discover_posts() -> list[dict[str, str]]:
    posts = []
    for md_path in BLOG_DIR.glob("*/*.md"):
        data, body = parse_frontmatter(md_path.read_text(encoding="utf-8"))
        if data.get("visibility") != "public":
            continue
        missing = [key for key in ("title", "date", "summary") if not data.get(key)]
        if missing:
            raise ValueError(f"{md_path}: missing required frontmatter field(s): {', '.join(missing)}")
        data.update({"body": body, "path": str(md_path), "category": md_path.parent.name, "slug": md_path.stem})
        posts.append(data)
    return sorted(posts, key=lambda post: post["date"], reverse=True)


def generate_rss(output_path: pathlib.Path = RSS_PATH, limit: int = RSS_LIMIT) -> int:
    base_url = site_url()
    posts = discover_posts()[:limit]
    ET.register_namespace("content", CONTENT_NS)
    ET.register_namespace("media", MEDIA_NS)
    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Wityworks"
    ET.SubElement(channel, "link").text = base_url + "/blog/"
    ET.SubElement(channel, "description").text = "Research notes, paper reviews, and essays on AI, math, and life."
    ET.SubElement(channel, "language").text = "en"
    ET.SubElement(channel, "lastBuildDate").text = format_datetime(datetime.now(KST))
    cdata_values: list[str] = []
    for post in posts:
        post_url = f"{base_url}/blog/{post['category']}/{post['slug']}/"
        cover = post.get("cover") or post.get("coverImage")
        try:
            content_html = markdown_to_html(post["body"], base_url, post_url)
        except Exception as exc:
            raise ValueError(f"{post['path']}: could not render RSS content: {exc}") from exc
        if cover:
            cover_url = absolute_url(cover, base_url, post_url)
            cover_html = (
                '<figure><img src="'
                + html.escape(cover_url, quote=True)
                + '" alt="'
                + html.escape(post["title"], quote=True)
                + '"></figure>'
            )
            content_html = cover_html + content_html
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = post["title"]
        ET.SubElement(item, "link").text = post_url
        guid = ET.SubElement(item, "guid", {"isPermaLink": "true"})
        guid.text = post_url  # category + slug is the stable post identity.
        ET.SubElement(item, "pubDate").text = rfc822_date(post["date"])
        if post.get("author"):
            ET.SubElement(item, "author").text = post["author"]
        ET.SubElement(item, "category").text = post.get("categoryLabel", post["category"])
        ET.SubElement(item, "description").text = post["summary"]
        content = ET.SubElement(item, f"{{{CONTENT_NS}}}encoded")
        marker = f"__RSS_CDATA_{len(cdata_values)}__"
        cdata_values.append(content_html)
        content.text = marker
        if cover:
            ET.SubElement(item, f"{{{MEDIA_NS}}}content", {"url": cover_url, "medium": "image"})
    serialized = ET.tostring(rss, encoding="unicode", xml_declaration=True)
    for index, content_html in enumerate(cdata_values):
        serialized = serialized.replace(f"__RSS_CDATA_{index}__", "<![CDATA[" + content_html.replace("]]>", "]]><![CDATA[>") + "]]>")
    output_path.write_text(serialized + "\n", encoding="utf-8")
    return len(posts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate blog/rss.xml")
    parser.add_argument("--output", type=pathlib.Path, default=RSS_PATH)
    parser.add_argument("--limit", type=int, default=RSS_LIMIT)
    args = parser.parse_args()
    count = generate_rss(args.output, args.limit)
    print(f"wrote {args.output} — {count} public post(s)")


if __name__ == "__main__":
    main()
