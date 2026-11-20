#!/usr/bin/env python3
"""知見ファイルの出典を機械的に照合する。

使い方: python3 -I check_sources.py <md> [<md> ...] [--json out.json]

- 各ファイルの「## 参照先」から [S#] と URL を取り出し、URL を取得する（キャッシュあり）。
- 本文の 「…」 の引用のうち、[S#] が付いているものについて、引用文が出典の本文に
  そのまま含まれるかを調べる（空白・引用符・全角半角の違いは無視。「…」「...」で区切られた
  断片はそれぞれ調べる。「（訳）」付きと8文字未満は対象外）。
- 結果: URL の状態（ok / dead / unreachable / skipped）と、見つからない引用の一覧。
"""
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import os
HELPER = Path(__file__).resolve().parent / "fetch_text.py"
# 取得したページのキャッシュ先。環境変数 KNOWLEDGE_CACHE で変えられる。
CACHE = Path(os.environ.get("KNOWLEDGE_CACHE", Path.home() / ".cache" / "knowledge_check")) / "src"
CACHE.mkdir(parents=True, exist_ok=True)

URL_RE = re.compile(r"https?://[^\s>\]」、，,（`]+")
QUOTE_RE = re.compile(r"「([^「」]{8,}?)」")
CITE_RE = re.compile(r"\[S(\d+)\]")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"')
    s = re.sub(r"[\s\"'`*_|]+", "", s)
    return s.lower()


def fetch(url: str):
    key = hashlib.sha1(url.encode()).hexdigest()[:16]
    f = CACHE / f"{key}.txt"
    if f.exists():
        t = f.read_text(encoding="utf-8", errors="replace")
    else:
        try:
            p = subprocess.run(["python3", "-I", str(HELPER), url, "--max", "3000000"],
                               capture_output=True, timeout=90)
            t = p.stdout.decode("utf-8", errors="replace")
        except subprocess.TimeoutExpired:
            t = "[fetch] status=timeout"
        f.write_text(t, encoding="utf-8")
    m = re.search(r"\[fetch\] status=(\S+)", t)
    status = m.group(1) if m else "?"
    return status, t


def classify(status: str, text: str) -> str:
    if status.startswith("2"):
        body = text.split("\n", 2)[-1] if text else ""
        return "ok" if len(body.strip()) > 200 else "thin"
    if status in ("000", "timeout", "?") or "not enabled for this session" in text:
        return "unreachable"
    if status in ("403", "429", "401"):
        return "unreachable"
    return "dead"


def parse(md: Path):
    lines = md.read_text(encoding="utf-8").splitlines()
    ref_i = max((i for i, l in enumerate(lines) if l.strip().startswith("## 参照先")), default=None)
    refs = {}
    if ref_i is not None:
        for l in lines[ref_i + 1:]:
            m = re.match(r"\s*[-*]\s*\[S(\d+)\]", l)
            if m:
                urls = []
                for u in URL_RE.findall(l):
                    while u.endswith(")") and u.count("(") < u.count(")"):
                        u = u[:-1]
                    urls.append(u.rstrip(".;:"))
                refs[m.group(1)] = {"urls": urls, "summary_only": ("検索要約のみ" in l and "読んだ" not in l)}
    body = lines[:ref_i] if ref_i is not None else lines
    quotes = []
    for i, l in enumerate(body):
        if "（訳）" in l or "(訳)" in l:
            # 訳の引用はその行の「」の最初の1つだけ除外せず、行ごと対象外にする
            continue
        cites = CITE_RE.findall(l)
        if not cites:
            continue
        for q in QUOTE_RE.findall(l):
            quotes.append({"line": i + 1, "quote": q, "cites": cites})
    return refs, quotes


def main():
    args = sys.argv[1:]
    out = None
    if "--json" in args:
        out = args[args.index("--json") + 1]
        args = [a for a in args if a not in ("--json", out)]
    files = [Path(a) for a in args]
    parsed = {f: parse(f) for f in files}
    urls = sorted({u for refs, _ in parsed.values() for r in refs.values() for u in r["urls"]
                   if "youtube.com/watch" not in u and "youtu.be/" not in u})
    with ThreadPoolExecutor(max_workers=6) as ex:
        results = dict(zip(urls, ex.map(fetch, urls)))
    report = []
    for f, (refs, quotes) in parsed.items():
        state = {}
        for n, r in refs.items():
            sts = []
            for u in r["urls"]:
                if "youtube.com/watch" in u or "youtu.be/" in u:
                    sts.append("skipped")
                else:
                    s, t = results[u]
                    sts.append(classify(s, t))
            state[n] = "ok" if "ok" in sts else (sts[0] if sts else "nourl")
        missing, found, unverifiable = [], 0, 0
        for q in quotes:
            texts = []
            for c in q["cites"]:
                for u in refs.get(c, {}).get("urls", []):
                    if u in results and classify(*results[u]) in ("ok", "thin"):
                        texts.append(norm(results[u][1]))
            if not texts:
                unverifiable += 1
                continue
            parts = [p for p in re.split(r"…+|\.\.\.+|（中略）|\(中略\)", q["quote"]) if len(norm(p)) >= 6]
            if parts and all(any(norm(p) in t for t in texts) for p in parts):
                found += 1
            else:
                missing.append(q)
        rep = {
            "file": str(f),
            "sources": len(refs),
            "dead": [n for n, s in state.items() if s == "dead"],
            "unreachable": [n for n, s in state.items() if s == "unreachable"],
            "youtube_skipped": [n for n, s in state.items() if s == "skipped"],
            "quotes_checked": found + len(missing),
            "quotes_found": found,
            "quotes_unverifiable": unverifiable,
            "quotes_missing": missing,
        }
        report.append(rep)
        print(f"{f.name}: 出典{rep['sources']} dead{len(rep['dead'])} 到達不可{len(rep['unreachable'])} "
              f"YT{len(rep['youtube_skipped'])} | 引用 照合{rep['quotes_checked']} 一致{found} "
              f"不一致{len(missing)} 照合不能{unverifiable}")
        for m in missing[:8]:
            print(f"   L{m['line']} [S{','.join(m['cites'])}] 「{m['quote'][:70]}」")
        if rep["dead"]:
            print(f"   dead: {rep['dead']}")
    if out:
        Path(out).write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
