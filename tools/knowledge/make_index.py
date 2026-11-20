#!/usr/bin/env python3
"""knowledge/README.md の一覧表を、各ファイル冒頭の「> 対象:」から作り直す。

使い方: python3 -I make_index.py <knowledgeディレクトリ>

README.md の `<!-- BEGIN:index -->` と `<!-- END:index -->` の間を置き換える
（目印がなければ何もしない）。ディレクトリごとに「ファイル | 対象」の表を出す。
"""
import re
import sys
from pathlib import Path


def first_sentence(s: str, limit: int = 90) -> str:
    s = s.strip()
    m = re.match(r"(.+?。)", s)
    if m:
        s = m.group(1)
    return s if len(s) <= limit else s[:limit].rstrip("、・ ") + "…"


def build(root: Path) -> str:
    out = []
    dirs = sorted({p.parent for p in root.rglob("*.md") if p.name != "README.md"})
    for d in dirs:
        rel = d.relative_to(root).as_posix()
        files = sorted(p for p in d.glob("*.md") if p.name != "README.md")
        out.append(f"\n### `{rel}/`（{len(files)}）\n")
        out.append("| ファイル | 対象 |")
        out.append("|---|---|")
        for p in files:
            t = p.read_text(encoding="utf-8")
            m = re.search(r"(?m)^> 対象[:：]\s*(.+)", t)
            desc = first_sentence(m.group(1)) if m else ""
            desc = desc.replace("|", "／")
            out.append(f"| [{p.stem}]({p.relative_to(root).as_posix()}) | {desc} |")
    return "\n".join(out) + "\n"


def main():
    root = Path(sys.argv[1]).resolve()
    readme = root / "README.md"
    text = readme.read_text(encoding="utf-8")
    pat = re.compile(r"(<!-- BEGIN:index -->\n).*?(<!-- END:index -->)", re.S)
    if not pat.search(text):
        print("目印がない:", readme)
        return
    n = sum(1 for p in root.rglob("*.md") if p.name != "README.md")
    new = pat.sub(lambda m: m.group(1) + build(root) + m.group(2), text)
    readme.write_text(new, encoding="utf-8")
    print(f"{readme}: {n} ファイルの一覧を更新")


if __name__ == "__main__":
    main()
