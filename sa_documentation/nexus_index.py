#!/usr/bin/env python3
"""Nexus indexer (Phase 2 CLI-мост): ingests AI-PROCESSES nodes into ruflo memory.

Каждый Узел Нексуса → ruflo memory (ns=ai-kortex) как векторная запись для семантического RAG.
ВАЖНО: ruflo memory store ломается на сыром контенте с `---`/YAML (`boolean (true)` error),
поэтому храним САНИТИРОВАННЫЙ однострочный summary: title + ключевые поля + body без markdown.
Idempotent: store по key=node_id (upsert). Переиндексировать после изменения узлов.

Usage: python3 sa_documentation/nexus_index.py [--root AI-PROCESSES] [--ns ai-kortex]
"""
import pathlib, re, subprocess, sys

ROOT = pathlib.Path(sys.argv[sys.argv.index("--root")+1] if "--root" in sys.argv else "AI-PROCESSES")
NS = sys.argv[sys.argv.index("--ns")+1] if "--ns" in sys.argv else "ai-kortex"
MAXBODY = 1500

def strip_fm(text):
    m = re.match(r'^---\n.*?\n---\n?', text, re.S)
    return text[m.end():] if m else text

def parse_fm(text):
    m = re.match(r'^---\n(.*?)\n---', text, re.S)
    d = {}
    if m:
        for line in m.group(1).splitlines():
            if ':' in line:
                k, v = line.split(':', 1); d[k.strip()] = v.strip()
    return d

def sanitize(body):
    # убрать markdown-синтаксис, оставить прозу
    s = re.sub(r'```.*?```', ' ', body, flags=re.S)      # code blocks
    s = re.sub(r'`[^`]*`', ' ', s)                         # inline code
    s = re.sub(r'\[\[([^\]|]+)(\|[^\]]*)?\]\]', r'\1', s)  # [[wikilink|alias]] -> wikilink
    s = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', s)         # [text](url) -> text
    s = re.sub(r'^[#>\-\*\|].*$', ' ', s, flags=re.M)      # headings/quotes/list/table lines
    s = re.sub(r'[*_`#\[\]()]', ' ', s)                    # residual markup
    s = re.sub(r'\s+', ' ', s).strip()                      # collapse whitespace
    return s[:MAXBODY]

def title_of(body):
    m = re.search(r'^#\s+(.+)$', body, re.M)
    return m.group(1).strip() if m else ""

stored = failed = skipped = 0
for p in sorted(ROOT.rglob("*.md")):
    text = p.read_text(encoding="utf-8")
    fm = parse_fm(text)
    nid = fm.get("node_id")
    if not nid:
        skipped += 1; continue
    body = strip_fm(text)
    meta = f"[nexus={fm.get('nexus','')} step={fm.get('paf_step','')} phase={fm.get('sprint_phase','')}]"
    value = f"{title_of(body)} {meta} {sanitize(body)}".strip()
    r = subprocess.run(["ruflo","memory","store","--key",nid,"--value",value,"--namespace",NS],
                       capture_output=True, text=True)
    # ruflo возвращает exit 0 даже при внутренней ошибке — проверяем stdout на [ERROR]/[OK]
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode == 0 and "[ERROR]" not in out:
        stored += 1
    else:
        print(f"FAIL {nid}: {out[:160]}", file=sys.stderr); failed += 1

print(f"indexed {stored} | failed {failed} | skipped {skipped} | ns={NS}")
