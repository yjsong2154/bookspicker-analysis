#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# EPUB → Text (or JSON) Extractor
# --------------------------------
# Converts an .epub file to clean UTF-8 text (default) or a JSON structure
# (chapter-wise), preserving reading order using the EPUB spine.
#
# Requirements (install first):
#     pip install ebooklib beautifulsoup4 lxml tqdm
#
# Usage examples:
#     # Plain text
#     python epub_to_text.py input.epub -o output.txt
#
#     # JSON with chapter objects
#     python epub_to_text.py input.epub -o output.json --json
#
#     # Keep hyperlinks and footnotes (off by default)
#     python epub_to_text.py input.epub -o out.txt --keep-links --keep-footnotes
#
#     # Tweak paragraph joining and minimal length filters
#     python epub_to_text.py input.epub -o out.txt --join-lines --min-paragraph-len 20
#
import argparse
import json
import os
import re
import sys
from typing import List, Dict, Any
try:
    from ebooklib import epub, ITEM_DOCUMENT
except Exception as e:
    print("❗️ Missing dependency 'ebooklib'. Install with: pip install ebooklib", file=sys.stderr)
    raise
from bs4 import BeautifulSoup

def html_to_paragraphs(html: bytes,
                       keep_links: bool = False,
                       keep_footnotes: bool = False,
                       min_par_len: int = 8,
                       join_lines: bool = False) -> Dict[str, Any]:
    """Convert an HTML (bytes) chunk from an EPUB document to a dict:
       {title: str, paragraphs: List[str]}
    """
    soup = BeautifulSoup(html, "lxml")
    # Drop scripts/styles/navs
    for sel in ["script", "style", "nav"]:
        for t in soup.select(sel):
            t.decompose()
    # Remove footnotes if requested
    if not keep_footnotes:
        for t in soup.select("[role='doc-footnote'], [epub\\:type='footnote'], .footnote, sup.footnote"):
            t.decompose()
        for a in soup.select("a[href^='#fn'], a[href^='#footnote'], a[href^='#note']"):
            a.decompose()
    # Turn <br> runs into newlines to help paragraphization
    for br in soup.find_all("br"):
        br.replace_with("\n")
    # Extract a reasonable title: first h1/h2/h3 text
    title_tag = soup.find(["h1", "h2", "h3"])
    title = title_tag.get_text(strip=True) if title_tag else ""
    # Elements considered as block paragraphs
    blocks = soup.find_all(["h1","h2","h3","h4","h5","h6","p","li","blockquote","pre"])
    paras: List[str] = []
    def clean_text(txt: str) -> str:
        # Collapse internal whitespace, normalize unicode nbsp etc.
        txt = txt.replace("\xa0", " ")
        # If join_lines, collapse embedded newlines (from <br>) into spaces
        if join_lines:
            txt = re.sub(r"[ \t]*\n[ \t]*", " ", txt)
        # Collapse spaces
        txt = re.sub(r"[ \t]{2,}", " ", txt)
        # Trim
        return txt.strip()
    for blk in blocks:
        # Hyperlink handling
        if not keep_links:
            # Replace links with just their text
            for a in blk.find_all("a"):
                a.replace_with(a.get_text(" ", strip=True))
        # Code/pre blocks: keep as-is lines
        if blk.name == "pre":
            txt = blk.get_text("\n", strip=True)
        else:
            txt = blk.get_text("\n", strip=True)
        txt = clean_text(txt)
        if not txt:
            continue
        # Headings: add markdown-ish marker so downstream can detect structure
        if blk.name in {"h1","h2","h3","h4","h5","h6"}:
            lvl = int(blk.name[1])
            txt = "#" * min(lvl, 6) + " " + txt
        if len(txt) >= min_par_len:
            paras.append(txt)
    return {"title": title, "paragraphs": paras}

def extract_epub(input_path: str,
                 keep_links: bool = False,
                 keep_footnotes: bool = False,
                 min_par_len: int = 8,
                 join_lines: bool = False) -> List[Dict[str, Any]]:
    """Return list of chapters in reading order: [{title, paragraphs}]"""
    book = epub.read_epub(input_path)
    # Build map of id → item for documents
    id_to_item = {}
    for item in book.get_items():
        if item.get_type() == ITEM_DOCUMENT:
            id_to_item[item.get_id()] = item
    chapters: List[Dict[str, Any]] = []
    # Follow the spine order
    for idref, _ in book.spine:
        item = id_to_item.get(idref)
        if not item:
            # Sometimes spine entry refers to a file name; try filename fallback
            for candidate in id_to_item.values():
                if candidate.file_name.endswith(idref):
                    item = candidate
                    break
        if not item:
            continue
        html = item.get_content()
        ch = html_to_paragraphs(
            html,
            keep_links=keep_links,
            keep_footnotes=keep_footnotes,
            min_par_len=min_par_len,
            join_lines=join_lines,
        )
        # Skip empty pages
        if ch["paragraphs"]:
            chapters.append(ch)
    return chapters

def chapters_to_text(chapters: List[Dict[str, Any]]) -> str:
    """Serialize chapters to a single UTF-8 text with blank lines between paragraphs."""
    out_lines: List[str] = []
    for i, ch in enumerate(chapters, start=1):
        title = ch.get("title", "").strip()
        if title:
            out_lines.append(f"## {title}")
            out_lines.append("")
        for p in ch["paragraphs"]:
            out_lines.append(p)
            out_lines.append("")
    return "\n".join(out_lines).strip() + "\n"

def save_output(chapters: List[Dict[str, Any]], out_path: str, as_json: bool) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    if as_json:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(chapters, f, ensure_ascii=False, indent=2)
    else:
        text = chapters_to_text(chapters)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)

def main():
    import argparse
    ap = argparse.ArgumentParser(description="EPUB → Text/JSON extractor (UTF-8).")
    ap.add_argument("input", help="Input .epub path")
    ap.add_argument("-o", "--output", help="Output path (.txt or .json). If omitted, uses input name with .txt")
    ap.add_argument("--json", action="store_true", help="Export JSON (chapter-wise) instead of plain text")
    ap.add_argument("--keep-links", action="store_true", help="Preserve hyperlinks (default: strip)")
    ap.add_argument("--keep-footnotes", action="store_true", help="Preserve footnotes (default: remove)")
    ap.add_argument("--min-paragraph-len", type=int, default=8, help="Drop very short lines (<N chars)")
    ap.add_argument("--join-lines", action="store_true", help="Join soft line breaks inside paragraphs")
    args = ap.parse_args()
    in_path = args.input
    if not os.path.isfile(in_path):
        print(f"❗️ File not found: {in_path}", file=sys.stderr)
        sys.exit(1)
    out_path = args.output
    if not out_path:
        base, _ = os.path.splitext(in_path)
        out_path = base + (".json" if args.json else ".txt")
    chapters = extract_epub(
        in_path,
        keep_links=args.keep_links,
        keep_footnotes=args.keep_footnotes,
        min_par_len=args.min_paragraph_len,
        join_lines=args.join_lines,
    )
    save_output(chapters, out_path, as_json=args.json)
    print(f"✅ Done: {out_path} ({len(chapters)} chapters/sections)")

if __name__ == "__main__":
    main()
