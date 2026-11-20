#!/usr/bin/env python3
"""knowledge/ の md を機械的に検査する。

使い方: python3 -I lint_knowledge.py <dir> [<dir> ...] [--mc <dir>]
  --mc を付けたディレクトリでは mc_version の記載も検査する。

検査:
  E1 必須の節（# 題名、## 要点、## 参照先）がない
  E2 本文で使った [S#] が参照先に定義されていない
  E3 要点の行に確度タグ（【一次】【二次】【未確認】【実測】）がない
  E4 参照先の行に URL がない
  E5 確度が【一次】【二次】なのに、引いている出典がすべて「検索要約のみ」
  W1 参照先に定義したが本文で使っていない [S#]
  W2 参照先の行に「取得」または「原文」の記載がない
  W3 （--mc）mc_version の記載がない
"""
import re
import sys
from pathlib import Path

TAG = re.compile(r"【(一次|二次|未確認|実測)】")
CITE = re.compile(r"\[S(\d+)\]")


def check(path: Path, mc: bool):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    errs, warns = [], []
    if not re.search(r"(?m)^# ", text):
        errs.append("E1 題名(#)がない")
    for sec in ("## 要点", "## 参照先"):
        if sec not in text:
            errs.append(f"E1 {sec} がない")
    # split body / refs
    ref_idx = None
    for i, l in enumerate(lines):
        if l.strip().startswith("## 参照先"):
            ref_idx = i
    body = lines[:ref_idx] if ref_idx is not None else lines
    refs = lines[ref_idx + 1:] if ref_idx is not None else []
    defined = {}
    for l in refs:
        m = re.match(r"\s*[-*]\s*\[S(\d+)\]", l)
        if m:
            n = m.group(1)
            defined[n] = l
            if "http" not in l:
                errs.append(f"E4 [S{n}] にURLがない")
            if "取得" not in l and "原文" not in l:
                warns.append(f"W2 [S{n}] に取得日/原文の記載がない")
    used = set()
    for i, l in enumerate(body):
        for n in CITE.findall(l):
            used.add(n)
            if n not in defined:
                errs.append(f"E2 L{i+1} [S{n}] が参照先にない")
    for n in defined:
        if n not in used:
            warns.append(f"W1 [S{n}] が本文で未使用")
    # 要点
    in_kp = False
    for i, l in enumerate(body):
        if l.startswith("## "):
            in_kp = l.strip().startswith("## 要点")
            continue
        if in_kp and re.match(r"\s*[-*] ", l) and not TAG.search(l):
            errs.append(f"E3 L{i+1} 要点に確度がない: {l.strip()[:60]}")
    # E5
    summ_only = {n for n, l in defined.items() if "検索要約のみ" in l and "読んだ" not in l}
    for i, l in enumerate(body):
        tags = TAG.findall(l)
        cites = CITE.findall(l)
        if cites and tags and all(c in summ_only for c in cites) and any(t in ("一次", "二次") for t in tags):
            errs.append(f"E5 L{i+1} 検索要約のみの出典で{tags}: {l.strip()[:60]}")
    if mc and "mc_version" not in text:
        warns.append("W3 mc_version の記載がない")
    stats = {t: len(re.findall(f"【{t}】", text)) for t in ("一次", "二次", "未確認", "実測")}
    return errs, warns, stats, len(defined)


def main():
    argv = sys.argv[1:]
    dirs = []
    mcdirs = set()
    i = 0
    while i < len(argv):
        if argv[i] == "--mc":
            mcdirs.add(argv[i + 1]); dirs.append(argv[i + 1]); i += 2
        else:
            dirs.append(argv[i]); i += 1
    total_e = 0
    for d in dirs:
        for p in sorted(Path(d).rglob("*.md")):
            if p.name == "README.md":
                continue
            e, w, s, nref = check(p, d in mcdirs)
            total_e += len(e)
            flag = "NG" if e else "ok"
            print(f"[{flag}] {p.relative_to(d)}  一次{s['一次']} 二次{s['二次']} 未確認{s['未確認']} 出典{nref}")
            for x in e[:15]:
                print("    " + x)
            if len(e) > 15:
                print(f"    ... 他 {len(e)-15} 件")
            for x in w[:5]:
                print("    " + x)
    print(f"errors: {total_e}")


if __name__ == "__main__":
    main()
