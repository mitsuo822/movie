#!/usr/bin/env python3
"""URL の本文をキャッシュから返す（なければ取得してキャッシュする）。出力はキャッシュファイルのパス。
使い方: python3 -I cached.py <URL>   → パスを表示。中身は grep -n キーワード <パス> で読む。
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashlib
from check_sources import fetch, CACHE
url = sys.argv[1]
status, _ = fetch(url)
print(CACHE / (hashlib.sha1(url.encode()).hexdigest()[:16] + ".txt"), "status=" + status)
