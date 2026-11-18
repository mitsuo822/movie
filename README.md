# movie

チャンネルを問わない**動画制作の基盤と知見**のリポジトリ。
制作台帳（`ledger.json`）を受け取り、AIナレーション・字幕・組立・検査を経て、長尺動画とショートを書き出し、YouTubeに投稿する。

最初の利用先: [mitsuo822/minecraft_physics](https://github.com/mitsuo822/minecraft_physics)（Minecraftで物理を検証するチャンネル）。

| パス | 中身 |
|---|---|
| `docs/全体設計.md` | 構成、工程、実装の段階 |
| `docs/制作台帳.md` | 台帳の書式（チャンネル側との境界） |
| `docs/ショート編集.md` | ショート（ドパガキ編集）の演出仕様 |
| `docs/YouTube運用.md` | 規約・APIの制約・表記ルール |
| `knowledge/` | 編集・音声・運用の知見の蓄積先 |

以前の汎用設計案（生成映像も扱う大きな構想）は commit `40f36c8` の `docs/設計提案.md` にある。この基盤はその一部（制作台帳・VOICEVOX・Remotion・検査）を先に実装する。
