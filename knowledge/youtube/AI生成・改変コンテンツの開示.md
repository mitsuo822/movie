# AI生成・改変コンテンツの開示（YouTube）

> 対象: YouTube の改変または合成されたコンテンツ（altered or synthetic content）＝生成 AI コンテンツの開示義務（2024年3月〜）、開示が必要な場合・不要な場合、AI 音声ナレーション・台本生成・字幕生成・ゲーム映像の扱い、ラベルの表示（2026年5月の変更）、自動検出、API での開示、開示しない場合のリスク、肖像（顔・声）の保護、その他2025〜2026年の AI 関連の変更。収益化ポリシー側の AI の扱いは別ファイル。
> 使う場面: 動画をアップロードするとき（Studio の「AI の使用」、API の `status.containsSyntheticMedia`）／生成 AI の素材（映像・音楽・音声）を使うか決めるとき／AI のラベルが自動で付いたとき。
> 調査日: 2026-11-19 ／ mc_version: 該当なし（YouTube の制度。ゲーム映像一般についての記述）
> 関連: [量産型・再利用コンテンツのポリシー.md](量産型・再利用コンテンツのポリシー.md), [収益化の条件.md](収益化の条件.md), [API投稿.md](API投稿.md), [../audio/VOICEVOX利用規約.md](../audio/VOICEVOX利用規約.md), [../audio/BGMと効果音.md](../audio/BGMと効果音.md), [../channel/AI音声チャンネルの事例とリスク.md](../channel/AI音声チャンネルの事例とリスク.md)

## 要点

- YouTube は2024年3月18日から、視聴者が実在の人物・場所・場面・出来事と誤認しうる「リアルな」コンテンツを、生成 AI を含む改変・合成メディアで作った場合の開示を求めている（予告は2023年11月14日）。【一次】[S3][S15]
- 開示が必要なのは、実在の人物が言っていない・していないことを言った・したように見せる／実際の出来事や場所の映像を改変する／現実に起きていない場面をリアルに生成する／動画の中心となる音楽を生成する、の場合。【一次】[S1][S2]
- 開示が不要なものとして、ヘルプは非現実的な内容（アニメーション等）、美顔・色・照明・特殊効果、生成 AI による台本・アウトライン・サムネイル・タイトル・インフォグラフィックの作成や改善、字幕の作成、アイデア生成、**自分の声のクローンによるナレーションや吹き替え**、**ビデオゲームのゲームプレイ映像**などを挙げている。【一次】[S1][S2]
- **第三者の声の合成ナレーション**: 2024年3月の公式ブログは「synthetically generating a person’s voice to narrate a video」（訳: ある人物の声を合成して動画のナレーションにする）を、開示が必要な「Using the likeness of a realistic person」の例に挙げた。2026-11-19 時点のヘルプには、架空キャラクターの音声合成ナレーションを名指しした記述はない。【一次】[S3][S1]
- 開示は YouTube Studio の［属性］→［AI の使用］で「はい／いいえ」を選ぶ。YouTube Data API では2024年10月30日から `status.containsSyntheticMedia` を `videos.insert`・`videos.update` で設定できる。【一次】[S1][S2][S6]
- 2026年5月からラベルの位置が変わり、写真のようにリアルな・大幅に改変された AI コンテンツは、長尺ではプレーヤーの直下（説明欄の上）、ショートでは動画に重ねて表示される。非現実的・アニメ・軽微なものは説明欄を開いた中に出る。【一次】[S4][S5]
- 2026年5月から、申告がなくても、システムが写真のようにリアルな AI の大きな使用を検出すると自動でラベルを付ける。誤りは「いいえ」に直せるが、YouTube の AI ツール（Veo、Dream Screen）で作ったもの、C2PA メタデータで AI 生成とわかるもの、手動審査でラベルを付けたものは外せない。【一次】[S1][S4][S5]
- YouTube は、開示（ラベル）だけでは推薦のされ方や収益化の資格は変わらないと繰り返し書いている。【一次】[S1][S4][S5]
- 開示を繰り返し意図的に怠ると、ラベルの手動適用、コンテンツの削除、YPP の参加停止などのペナルティがありうる。【一次】[S1][S2]
- 肖像検出（likeness detection）は2025年に YPP のクリエイター向けに始まり、2026年5月19日に18歳以上の全クリエイターへ拡大。2026-11-19 時点のヘルプでは検出は顔のみで、声は導入を進めている段階。【一次】[S7][S8][S10][S11]
- 日本語版のヘルプには「AI 技術を使用して翻訳されたコンテンツが含まれている場合があります」と書かれている。細かい解釈は英語版で確かめる。【一次】[S2]
- 収益化ポリシー側では、汎用テンプレートで量産した印象の AI 生成コンテンツ、デリケートな話題で人間の専門家を装う AI ペルソナが収益化できない（開示とは別の基準。[量産型・再利用コンテンツのポリシー.md](量産型・再利用コンテンツのポリシー.md)）。【一次】[S16]

## 詳細

### 1. 経緯

| 日付 | 出来事 | 確度 | 出典 |
|---|---|---|---|
| 2023-11-14 | 公式ブログで、リアルな改変・合成コンテンツの開示義務とラベル、AI で特定の個人の顔や声を模したコンテンツの削除をプライバシー申し立てで求められる仕組みを予告 | 【一次】 | [S15] |
| 2024-03-18 | Creator Studio に開示ツールを導入。多くの動画は説明欄にラベル、健康・ニュース・選挙・金融などのデリケートな話題はプレーヤー上にも表示 | 【一次】 | [S3] |
| 2024-10-30 | YouTube Data API に `status.containsSyntheticMedia` を追加 | 【一次】 | [S6] |
| 2025-02-10 | ハラスメントのポリシーで、亡くなった人が自分の死や受けた暴力を語る様子をリアルに再現するコンテンツを削除の対象に | 【一次】 | [S14] |
| 2025（月不明） | 肖像検出を YPP のクリエイター向けに開始 | 【一次】 | [S8] |
| 2026-01-21 | CEO の書簡で「AI slop」への対策と、クリエイターがリアルな改変・合成コンテンツを開示する義務に言及 | 【一次】 | [S12] |
| 2026-03-10 | 肖像検出を政府関係者・ジャーナリスト・候補者の試験グループへ拡大 | 【一次】 | [S8] |
| 2026-04-21 | 肖像検出をタレント事務所・マネジメント会社とその所属タレントへ拡大 | 【一次】 | [S9] |
| 2026-05-19 | 肖像検出を18歳以上の全クリエイターへ拡大すると発表 | 【一次】 | [S10] |
| 2026-05-27 | ラベルの表示位置の変更と、AI の自動検出の導入を発表 | 【一次】 | [S4][S5] |
| 2026-06 | クリエイターの責任のポリシーを更新し、YouTube の機能・ツールで他人を害するコンテンツを作ることを重大な違反として、機能の利用制限の対象に | 【一次】 | [S14] |
| 2026-08 ごろ | 自動で付いたラベルを Studio の「コンテンツ」一覧でまとめて確認できるようにしたと追記 | 【一次】 | [S5] |
| 2026-09-23 | Made on YouTube で、肖像検出のスマホ対応と、話し声の検出を顔の検出と組み合わせる方針を発表 | 【一次】 | [S11] |
| 2026-11 | YouTube Music で、アーティストとレーベルにコンテンツでの AI 使用の開示を求めるとした | 【一次】 | [S14] |

> 「That’s why today, we're introducing a new tool in Creator Studio requiring creators to disclose to viewers when realistic content – content a viewer could easily mistake for a real person, place, scene, or event – is made with altered or synthetic media, including generative AI.」[S3]
> （訳）視聴者が実在の人物・場所・場面・出来事と簡単に見間違えうるリアルなコンテンツを、生成 AI を含む改変・合成メディアで作った場合に、視聴者への開示を求めるツールを導入する。

### 2. 開示が必要なもの・不要なもの（2026-11-19 時点のヘルプ）

> 「AI 生成コンテンツまたは改変コンテンツが本物のように見える場合、クリエイターによる開示が必要になります。」[S2]

| 分類 | 例（ヘルプの日本語版の表現） | 開示 | 確度 | 出典 |
|---|---|---|---|---|
| 実在の人物 | 「実在する人物が実際には発言または行動していないことを、発言または行動しているように見せている。」 | 必要 | 【一次】 | [S2] |
| 実際の出来事・場所 | 「実際の出来事や場所の映像を改変している。」 | 必要 | 【一次】 | [S2] |
| リアルな架空の場面 | 「現実には起こっていないシーンをリアルに生成している。」（例: 実在の都市に向かう竜巻をリアルに描く） | 必要 | 【一次】 | [S2] |
| 音楽 | 「動画の中心となる音楽を作成する。」／例の一覧では「AI 生成の音楽」 | 必要 | 【一次】 | [S2] |
| 非現実的 | 「ユニコーンに乗って幻想的な世界を旅する人物」「AI で生成または改変したミサイルのアニメーションが使われているフル アニメーション動画」 | 不要 | 【一次】 | [S2] |
| 見た目の軽微な編集 | 美顔フィルタ、色調整・照明、背景ぼかし等の特殊効果 | 不要 | 【一次】 | [S2] |
| 制作支援 | 「生成 AI ツールを使用した軽微な制作支援（動画案のアウトライン、スクリプト、サムネイル、タイトル、インフォグラフィックの作成や改善など）」 | 不要 | 【一次】 | [S2] |
| 字幕・アイデア | 「字幕の作成」「アイデア生成」 | 不要 | 【一次】 | [S2] |
| 画質・音質の補正 | 「動画のシャープネス調整、アップスケーリング、修復、または音声の修復」 | 不要 | 【一次】 | [S2] |
| 自分の声 | 「自分の声をクローニングしたナレーションや吹き替え」 | 不要 | 【一次】 | [S2] |
| ゲーム映像 | 「ビデオゲームのゲームプレイ映像」 | 不要 | 【一次】 | [S2] |

- ヘルプは、軽微な編集を「主に見た目を良くすることが目的で、実際に何が起きたかについて視聴者に誤解を与えるようなコンテンツ改変を含まない編集」と定義している。【一次】[S2]
- 冒頭の一覧は「動画の中心となる音楽」、例の一覧は「AI 生成の音楽」と書いていて、BGM 程度の AI 音楽が必要かどうかは表現が揃っていない。【一次】[S1][S2]
- 2026年5月の TeamYouTube の投稿は、開示が必要なのは「meaningfully altered or generated and appears photorealistic」な AI コンテンツだけだと書いている。【一次】[S5]
  > 「Disclosure is required only for AI content that is meaningfully altered or generated and appears photorealistic.」[S5]

### 3. AI 音声ナレーションの扱い（公式の記述の比較）

| 資料 | 記述 | 確度 | 出典 |
|---|---|---|---|
| 公式ブログ 2024-03-18 | 開示が必要な例の「Using the likeness of a realistic person」に「synthetically generating a person’s voice to narrate a video」 | 【一次】 | [S3] |
| ヘルプ 2026-11-19 | 開示不要の例に「自分の声をクローニングしたナレーションや吹き替え」。第三者・架空キャラクターの合成音声ナレーションを名指しした記述はない | 【一次】 | [S1][S2] |
| ヘルプ 2026-11-19（ラベルの節） | 「音楽以外の AI 生成音声」は、説明欄を開いたときにラベルが表示されることがある | 【一次】 | [S2] |
| TeamYouTube の FAQ（再利用されたコンテンツ） | AI でナレーションを作っても必ずしも停止にはならない。改変・合成コンテンツは視聴者に知らせることを期待する | 【一次】 | [S17] |

> 「Using the likeness of a realistic person: Digitally altering content to replace the face of one individual with another's or synthetically generating a person’s voice to narrate a video.」[S3]

> 「音楽以外の AI 生成音声、または写真のようにリアルではない AI コンテンツやアニメーションの AI コンテンツについては、説明欄を開いたときにラベルが表示されることがあります。」[S2]

- 2024年の公式ブログは、台本・アイデア・自動字幕の生成のような生産性のための生成 AI の利用は開示不要とした。【一次】[S3]
  > 「We won’t require creators to disclose if generative AI was used for productivity, like generating scripts, content ideas, or automatic captions.」[S3]

### 4. 開示の方法

- YouTube Studio でアップロードの手順に沿って進み、［属性］セクションの［AI の使用］で、要件に当たれば［はい］、当たらなければ［いいえ］を選ぶ。パソコンでもモバイルでも設定できる。【一次】[S1][S2]
- 公開済みの動画も、多くの場合は Studio の「コンテンツ」で動画を選び、［属性］の「AI の使用」アンケートで変更できる。【一次】[S5]
- YouTube Data API: 2024年10月30日の改訂で、リアルな改変・合成（A/S）コンテンツを含むかを `status.containsSyntheticMedia` で示せるようになった。`videos.insert` か `videos.update` で設定でき、設定すると video リソースで返される。【一次】[S6]
  > 「To indicate whether a video contains A/S content, set the status.containsSyntheticMedia property. This property can be set when calling the videos.insert or videos.update methods. If set, the property is returned in the video resource.」[S6]
- 音楽アーティスト向けには別の開示の記事がある。【一次】[S1]

### 5. ラベルの表示

- 2024年3月の導入時: 多くの動画は説明欄を開いた中にラベル、健康・ニュース・選挙・金融などのデリケートな話題はプレーヤー上にも目立つラベル。【一次】[S3]
- 2026年5月からの表示: 写真のようにリアルな・大幅に AI で改変または生成されたコンテンツは、長尺ではプレーヤーの直下・説明欄の上、ショートでは動画に重ねて表示。これが写真のようにリアルな AI コンテンツの唯一のラベル形式になった。非現実的・アニメ・わずかな改変は説明欄を開いた中。【一次】[S4][S5]
  > 「For Long-form Videos: The label will now appear directly below the video player, above the description.」「For Shorts: The label will appear as an overlay on the video itself.」[S4]
- ヘルプ（2026-11-19）は、AI 生成の音楽と写真のようにリアルなコンテンツでは動画プレーヤーにラベルが出ることがあり、音楽以外の AI 生成音声・非写実的・アニメの AI コンテンツは説明欄に出ることがある、と書く。【一次】[S1][S2]
- ラベルの影響: 「開示を行うだけで、動画の視聴者に制限が設けられたり、収益化の資格に影響が及んだりすることはありません」（ヘルプ）、「a disclosure label alone does not change how a video is recommended or whether it’s eligible to earn money」（公式ブログ 2026-05-27）。【一次】[S2][S4]

### 6. 自動検出と変えられないラベル

- YouTube は、YouTube の生成 AI ツールで作ったコンテンツ、C2PA メタデータを含むコンテンツ、内部システムが AI で生成・改変されたと検出したコンテンツに、自動でラベルを付けることがある。自動で付いた場合は Studio に通知が届く。【一次】[S1][S2]
- 2026年5月から新しい内部シグナルを導入し、クリエイターが AI の使用を申告せず、システムが写真のようにリアルな AI の大きな使用を検出した場合は自動でラベルを付ける。【一次】[S4]
  > 「If a creator doesn’t specify whether or not they used AI, but our systems detect significant photorealistic AI use, we will now automatically apply a label.」[S4]
- 誤検出は多くの場合、［属性］の AI 使用アンケートで［いいえ］にすると外せる。自動ラベルの付いた動画は、コンテンツ一覧の「Other notices」の列でまとめて確認できる（2026年8月ごろの追記。日本語 UI での列名は未確認）。【一次】[S1][S5]
- 外せないもの: YouTube の AI ツール（Veo、Dream Screen など）で作ったもの、AI で生成されたことを示す C2PA メタデータを含むもの、手動審査でラベルを付けたもの。【一次】[S1][S2][S4][S5]
- Gemini Omni でリミックスしたショートには、電子透かしと識別用メタデータが付き、元の動画へのリンクが付く（2026-05-19 の発表）。【一次】[S10]

### 7. 開示しない場合のリスク

> 「クリエイターがこの情報開示を繰り返し意図的に怠る場合は、YouTube によるラベルの手動適用やペナルティ（コンテンツの削除や YouTube パートナー プログラムへの参加停止など）が発生する可能性があります。」[S2]

- AI で生成・改変したかどうかに関係なく、すべてのコンテンツにコミュニティガイドラインが適用される。2023年の公式ブログは、ラベルを付けても、衝撃を与えることを目的としたリアルな暴力の合成映像などは削除されうると書いた。【一次】[S2][S15]

### 8. 肖像（顔・声）の保護

- **肖像検出（likeness detection）**: 登録したクリエイターの顔が AI で改変・生成されたように見える動画を探し、プライバシーの申し立てで削除を求められる。18歳以上で、チャンネルのオーナーまたは管理者が、政府発行の身分証明書と顔の短い動画（自撮り）で本人確認して設定する。新しくアップロードされた動画を1回検索する仕組みで、Content ID に似た仕組みと説明されている（「This works similarly to Content ID」）。【一次】[S7]
  > 「Currently, the feature is only used to detect matches of an enrolled creators’ face. We aim to extend likeness detection to audio in the near future.」[S7]
- 一部のユーザーは設定時に話し声のサンプルを録音できるようになっている、とヘルプに注記がある。【一次】[S7]
- 検出は削除を保証せず、パロディや風刺は考慮される。【一次】[S7][S8]
- **プライバシーの申し立て**: AI などで自分の声や姿を許可なく改変・生成されたコンテンツは、削除を求められる。対象になるには、本人の肖像のリアルな改変・合成版である必要がある。【一次】[S13]
  > 「To qualify for removal, the content should show a realistic altered or synthetic version of your likeness.」[S13]

### 9. 二次情報との食い違い

- ゆっくり解説の制作ツールを販売する事業者の note 記事は、収益化の通過条件として「AIラベルを必ずチェックする」を挙げている。公式の基準では、開示が必要なのは本物のように見える（写真のようにリアルな）AI コンテンツで、ゲーム映像や台本の生成は不要とされている。【二次】[S18]（公式: [S1][S2][S5]）

## このチャンネルでの使い方（提案）

> ※この節は上の事実から導いた提案で、事実ではない。

- **Minecraft の録画そのもの（Replay Mod・Flashback・シェーダー）は「ゲームプレイ映像」として開示不要と扱う。** AI を使わない Remotion の図やグラフは、そもそもヘルプが対象とする AI ツールで生成・改変したものに当たらないと読める。（根拠: [S1][S2]）
- **台本の下書きや構成、字幕、タイトル案に生成 AI を使っても開示は不要。** ただし数値は実測値だけを使う（CLAUDE.md の確度の決まり）。（根拠: [S1][S2][S3]）
- **VOICEVOX のキャラクター音声のナレーションは、判断を決めて記録しておく。** 現行ヘルプの開示が必要な一覧には当たらないと読め、ゲーム映像の上で架空のキャラクターが話す形は、実在の人物に言っていないことを言わせるものでもない。一方、2024年のブログは「synthetically generating a person’s voice to narrate a video」を例に挙げ、ヘルプのラベルの節は「音楽以外の AI 生成音声」に触れている。ラベルだけでは推薦・収益化に影響しないと公式が書いているので、迷う回は［はい］にしても損は小さい。どちらにしたかを動画ごとの記録に残す。（根拠: [S1][S2][S3][S4]）
- **API で投稿するときは `status.containsSyntheticMedia` を毎回明示的に設定する（省略しない）。** 申告がない場合に自動検出でラベルが付く仕組みがあるため。（根拠: [S4][S6]。投稿の手順は [API投稿.md](API投稿.md)）
- **次の場合は［はい］にする。** (1) 現実の実験・歴史上の実験（系統B）を生成 AI でリアルな映像として再現したとき、(2) 実在の場所の映像を AI で作り足したとき、(3) AI 生成の音楽を使ったとき、(4) 実在の人物（物理学者を含む）が言っていないことを言うリアルな映像・音声を作ったとき。(4) はできれば作らない。（根拠: [S1][S2]）
- **YouTube の AI ツール（Veo、Dream Screen 等）や C2PA の「AI 生成」メタデータを付ける外部ツールの素材は、外せないラベルが付く前提で使う。** 書き出した素材のメタデータを確認する。（根拠: [S1][S4]）
- **キャラクターの見た目に AI 生成画像を使うかは、開示とは別に、キャラクターの規約で決める。**（[../audio/キャラクター立ち絵の規約.md](../audio/キャラクター立ち絵の規約.md)）

## わかっていないこと・要確認

- 架空キャラクターの音声合成（VOICEVOX など）によるナレーションに開示が必要か、YouTube の明示的な説明（見つからなかった）。
- API の `status.containsSyntheticMedia` を `false` に設定した場合に、2026年5月からの自動検出によるラベルが付くかどうか（記載なし）。
- Studio の日本語 UI での「AI の使用」の質問文の現在の表現（画面を見ていない）。
- 「動画の中心となる音楽」と「AI 生成の音楽」の表現の違い（BGM 程度の AI 音楽が必要か）。[S1][S2]
- 肖像検出の声の検出が日本のクリエイターにいつ提供されるか（Made on YouTube 2026 では「We’ll also start integrating speaking voice detection with facial detection to improve overall match accuracy」とあるだけで、時期と国の記載はない）。[S11]

## 参照先

- [S1] Disclosing use of GenAI content — YouTube ヘルプ — https://support.google.com/youtube/answer/14328491?hl=en — 更新日: 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S2] 生成 AI コンテンツの使用に関する開示 — YouTube ヘルプ — https://support.google.com/youtube/answer/14328491?hl=ja — 更新日: 不明（「AI 技術を使用して翻訳されたコンテンツが含まれている場合があります」と注記） — 取得: 2026-11-19 — 原文: 読んだ
- [S3] How we're helping creators disclose altered or synthetic content — The YouTube Team（YouTube 公式ブログ） — https://blog.youtube/news-and-events/disclosing-ai-generated-content/ — 2024-03-18 — 取得: 2026-11-19 — 原文: 読んだ
- [S4] Improving AI labels for viewers and creators — The YouTube Team（YouTube 公式ブログ） — https://blog.youtube/news-and-events/improving-ai-labels-viewers-creators/ — 2026-05-27 — 取得: 2026-11-19 — 原文: 読んだ
- [S5] Updates to AI content disclosure and labels — Dave（TeamYouTube）、YouTube ヘルプ コミュニティ — https://support.google.com/youtube/blog/424874071/updates-to-ai-content-disclosure-and-labels?hl=en — ページ内データの時刻から 2026-05-27 投稿、2026-08-03 ごろ追記（表示上の日付は未確認） — 取得: 2026-11-19 — 原文: 読んだ（本文はページに埋め込まれたデータから抽出）
- [S6] YouTube Data API 改訂履歴（Revision History）— 2024-10-30 の項 — Google for Developers — https://developers.google.com/youtube/v3/revision_history?hl=en — 2024-10-30（該当の項） — 取得: 2026-11-19 — 原文: 読んだ
- [S7] Likeness detection on YouTube — YouTube ヘルプ — https://support.google.com/youtube/answer/16440338?hl=en — 更新日: 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S8] Expanding likeness detection to civic leaders and journalists — Amjad Hanif、Leslie Miller（YouTube 公式ブログ） — https://blog.youtube/news-and-events/expanding-likeness-detection-civic-leaders-journalists/ — 2026-03-10 — 取得: 2026-11-19 — 原文: 読んだ
- [S9] Expanding likeness detection to the entertainment industry — The YouTube Team（YouTube 公式ブログ） — https://blog.youtube/news-and-events/youtube-likeness-detection-ai-protection/ — 2026-04-21 — 取得: 2026-11-19 — 原文: 読んだ
- [S10] All the YouTube news from Google I/O 2026 — The YouTube Team（YouTube 公式ブログ） — https://blog.youtube/news-and-events/youtube-news-google-io-2026/ — 2026-05-19 — 取得: 2026-11-19 — 原文: 読んだ
- [S11] Innovation for the YouTube Era: What’s new for viewers and creators（Made On YouTube 2026） — Neal Mohan（YouTube 公式ブログ） — https://blog.youtube/news-and-events/innovation-youtube-era-made-on-viewers-creators/ — 2026-09-23 — 取得: 2026-11-19 — 原文: 読んだ
- [S12] From the CEO: What’s coming to YouTube in 2026 — Neal Mohan（YouTube 公式ブログ） — https://blog.youtube/inside-youtube/the-future-of-youtube-2026/ — 2026-01-21 — 取得: 2026-11-19 — 原文: 読んだ
- [S13] YouTube Privacy Guidelines — YouTube ヘルプ — https://support.google.com/youtube/answer/7671399?hl=en — 更新日: 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S14] YouTube policy updates（ポリシー更新の一覧） — YouTube ヘルプ — https://support.google.com/youtube/answer/10008196?hl=en — 最新の記載は2026年11月 — 取得: 2026-11-19 — 原文: 読んだ
- [S15] Our approach to responsible AI innovation — Jennifer Flannery O'Connor、Emily Moxley（YouTube 公式ブログ） — https://blog.youtube/inside-youtube/our-approach-to-responsible-ai-innovation/ — 2023-11-14 — 取得: 2026-11-19 — 原文: 読んだ
- [S16] YouTube channel monetization policies — YouTube ヘルプ — https://support.google.com/youtube/answer/1311392?hl=en — 更新日: 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S17] 🔎 FAQ: Reused Content & YouTube’s Partner Program — Rob（TeamYouTube）、YouTube ヘルプ コミュニティ — https://support.google.com/youtube/community-guide/271248162/?hl=en — 公開日: ページ上で未確認 — 取得: 2026-11-19 — 原文: 読んだ
- [S18] 【基礎から学ぶゆっくり解説】「ゆっくり動画、収益化できない」はもう古い！…（2026年最新版） — SS@ゆっくり編集効率化（note、制作ツールの販売者） — https://note.com/yukkuri_auto/n/n6da3c97b7b4f — 2025-06-11（記事の表示日） — 取得: 2026-11-19 — 原文: 読んだ
