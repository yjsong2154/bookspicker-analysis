import os
import re
import sys
from typing import List, Dict, Any
from bs4 import BeautifulSoup

try:
    from ebooklib import epub, ITEM_DOCUMENT
except ImportError:
    print("❗️ Missing dependency 'ebooklib'. Install with: pip install ebooklib", file=sys.stderr)
    # raise # 의존성 에러는 실행 시점에 잡히도록

def html_to_paragraphs(html: bytes,
                       keep_links: bool = False,
                       keep_footnotes: bool = False,
                       min_par_len: int = 8,
                       join_lines: bool = False) -> Dict[str, Any]:
    """Convert an HTML (bytes) chunk from an EPUB document to a dict."""
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
    # Turn <br> runs into newlines
    for br in soup.find_all("br"):
        br.replace_with("\n")
    # Extract title
    title_tag = soup.find(["h1", "h2", "h3"])
    title = title_tag.get_text(strip=True) if title_tag else ""
    # Elements considered as block paragraphs
    blocks = soup.find_all(["h1","h2","h3","h4","h5","h6","p","li","blockquote","pre"])
    paras: List[str] = []
    
    def clean_text(txt: str) -> str:
        txt = txt.replace("\xa0", " ")
        if join_lines:
            txt = re.sub(r"[ \t]*\n[ \t]*", " ", txt)
        txt = re.sub(r"[ \t]{2,}", " ", txt)
        return txt.strip()

    for blk in blocks:
        if not keep_links:
            for a in blk.find_all("a"):
                a.replace_with(a.get_text(" ", strip=True))
        if blk.name == "pre":
            txt = blk.get_text("\n", strip=True)
        else:
            txt = blk.get_text("\n", strip=True)
        txt = clean_text(txt)
        if not txt:
            continue
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
    """Return list of chapters in reading order."""
    book = epub.read_epub(input_path)
    id_to_item = {}
    for item in book.get_items():
        if item.get_type() == ITEM_DOCUMENT:
            id_to_item[item.get_id()] = item
    chapters: List[Dict[str, Any]] = []
    for idref, _ in book.spine:
        item = id_to_item.get(idref)
        if not item:
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
        if ch["paragraphs"]:
            chapters.append(ch)
    return chapters

def chapters_to_text(chapters: List[Dict[str, Any]]) -> str:
    """Serialize chapters to a single UTF-8 text."""
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

def convert_epub_to_txt(epub_path: str, output_path: str):
    """Convenience function to convert epub to txt file."""
    chapters = extract_epub(epub_path)
    text = chapters_to_text(chapters)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
