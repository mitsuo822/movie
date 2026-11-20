# Remotion（利用ライセンスと書き出し・タイムライン・字幕・レンダリング）

> 対象: 動画をコード（React）で組み立てる Remotion の利用条件（無料ライセンスの範囲、会社ライセンス）と、技術の知見（書き出しのコーデック・音声・並列化、音声の長さからタイムラインを組む方法、テロップと字幕の同期、レンダリング時間とGPU）。
> 使う場面: 編集の自動化を設計するとき、Remotion のバージョンを上げるとき、書き出し設定を決めるとき、チームの人数や体制が変わるとき（ライセンスの見直し）。
> 調査日: 2026-11-20 ／ mc_version: 対象外 ／ Remotion: GitHub main ブランチで 4.0.545（2026-11-20 取得）。記載の多くは公式ドキュメントの 2026-11-20 時点の内容で、Remotion 4.0 系が前提。5.0 で既定値が変わる項目は明記した。
> 関連: [アップロード仕様と書き出し設定.md](../youtube/アップロード仕様と書き出し設定.md), [テロップ・字幕.md](テロップ・字幕.md), [ショート編集.md](ショート編集.md), [図解・グラフの見せ方.md](図解・グラフの見せ方.md), [音量とラウドネス.md](../audio/音量とラウドネス.md), [フォントのライセンス.md](../legal/フォントのライセンス.md), [VOICEVOX利用規約.md](../audio/VOICEVOX利用規約.md)

## 要点
- Remotion はソースは公開されているが、OSI の定義でいうオープンソースではなく、独自の Remotion License で使う。個人、3人までの営利組織、非営利組織は無料で、商用利用もできる。それより大きい営利組織は会社ライセンスが要る。【一次】[S1][S3]
- 無料ライセンスと会社ライセンスで機能の差はない。無料ライセンスなら連絡もアカウント作成も不要で、自動化（render コマンドを呼ぶパイプライン）も組んでよい。【一次】[S3]
- 人数の判定は会社全体の人数で行う。20人の会社で1人だけが使う場合も、無料ライセンスの免除に当たらなければ会社ライセンスが要る。【一次】[S3]
- 会社ライセンスの料金（2026-11-20 取得）: 手作業の制作は1人あたり月25ドル、自動化は1レンダー0.01ドルで月100ドルから、エンタープライズは月500ドルから。【一次】[S2][S3]
- Remotion 5.0 でライセンスが少し変わると LICENSE.md に書かれている。FAQ によると Automators の利用者のテレメトリの必須化を含むが、変更の全体（PR #3750）は未読。5.0 では GL の既定（angle）や色空間の既定（bt709）も変わる。【一次】[S1][S5][S8]
- 既定のコーデックは H.264。CRF の既定値と範囲はコーデックごとに違い、H.264 は 1〜51 で既定 18。【一次】[S4]
- NVIDIA GPU による NVENC のハードウェアエンコードは Windows でも v4.0.484 から使える。ただし既定は無効で、CRF と併用できず、ファイルが大きくなりやすいので --video-bitrate で調整する。【一次】[S6]
- ヘッドレスのレンダリングでは多くの場合 GPU が無効なので、影・グラデーション・ぼかし・WebGL などは遅くなる。4.0 では、デスクトップで WebGL を使うなら --gl=angle が推奨。angle には長いレンダーでのメモリリークの問題がある。【一次】[S7][S8][S9]
- 音声の長さに合わせて動画の長さを決めるには、Composition の calculateMetadata() で durationInFrames を返す。長さの取得には、公式資料が示す getMediaMetadata()（Mediabunny を使う関数のコード例で、自分のプロジェクトに置いて使う）を使うよう案内されており、@remotion/media-utils の getAudioDurationInSeconds() は非推奨になった。【一次】[S11][S12][S13]
- セリフを順番に並べるには <Series> を使う。各 Series.Sequence の長さ（フレーム数）は、最後の1つ（Infinity にできる）を除いて正の整数でなければならない。【一次】[S14]
- 字幕は @remotion/captions で、同じ Caption データから焼き込み（テロップ）と .srt ファイルの両方を出せる。.srt は <Artifact> と serializeSrt() で書き出す。【一次】[S15][S16][S17]
- 第三者の計測（Windows 11 Pro、Remotion v4.0.398、1920x1080・30fps、約115秒、口パクのキュー781個を含む動画、2026-01-28 検証）では、レンダリングに平均約2分53秒（動画1秒あたり約1.5秒）かかった。著者は、その約92%がフレームのレンダリングだったと推定している（工程別の時間は推定値）。【二次】[S19]

## 詳細

### 1. 利用ライセンス

#### 無料ライセンスの対象
LICENSE.md の無料ライセンスの対象は、個人、従業員3人までの営利組織、非営利組織、商用利用の前の評価の4つ。【一次】[S1]
> 「a for-profit organization with up to 3 employees」[S1]

ライセンスの FAQ では、2つ目を組織または個人のチームで3人までと書いている。LICENSE.md は employees（従業員）、FAQ は people（人）と書き方が違う。【一次】[S1][S3]
> 「an organization or team of individuals with up to 3 people」[S3]

FAQ は、Remotion はソースが公開されている（source-available）が、OSI のオープンソースの定義には当たらず、独自の Remotion License で使用が決まると書いている。【一次】[S3]
> 「Remotion is source-available software, but it is not open source software according to the Open Source Initiative's Open Source Definition.」[S3]

（訳）個人と小さな会社は、動画を作るために無料で（商用でも）Remotion を使える。原文「Individuals and small companies are allowed to use Remotion to create videos for free (even commercial)」【一次】[S1]

料金ページの冒頭にも、個人と小さな会社は完全に無料だと書かれている。【一次】[S2]
> 「Remotion is completely free to use for any individual or small company - no catch.」[S2]

法人化した1人会社でも、総人数が3人以下なら無料ライセンスで使える。【一次】[S3]

無料ライセンスで収益を得てよいかという問いに、FAQ は「はい」と答え、商用の制限は全員共通の小さなものだけだとしている。【一次】[S3]
> 「Yes. There are only a couple of small commercial restrictions which are in place for everybody.」[S3]

無料ライセンスで自動化を動かしてもよい。後述の Remotion for Automators は会社ライセンスにだけ関係する。【一次】[S3]
> 「If you are eligible for the Free License, you can also run an automation.」[S3]

無料ライセンスを使うのに Remotion への連絡もアカウントも不要。【一次】[S3]
> 「You don't have to contact us to use Remotion under the Free License.」[S3]

無料ライセンスと会社ライセンスで機能の差はない。【一次】[S3]

#### 禁止されていること（全員共通）
Remotion のコードをコピー・改変して、自分の派生物として販売・貸与・ライセンスすることは禁止。【一次】[S1]
> 「It is not allowed to copy or modify Remotion code for the purpose of selling, renting, licensing, relicensing, or sublicensing your own derivate of Remotion.」[S1]

FAQ では、Remotion そのものを製品として売ることと、他人がライセンスを買うべき場面を回避させることが禁止の範囲とされる。利用者が自分の Remotion プロジェクトを持ち込んでレンダリングさせるサービスは認められない例として挙げられている。【一次】[S3]

#### 会社ライセンスが要る場合と料金（2026-11-20 取得）
人数の判定は会社全体の人数で行う。20人の会社で1人だけが Remotion を使う場合も、免除がなければ会社ライセンスが要る。【一次】[S3]
> 「Eligibility depends on your company's total headcount.」[S3]

| プラン | 対象 | 料金（2026-11-20 取得） | 確度 | 出典 |
|---|---|---|---|---|
| Remotion for Creators | 自動化をせず手作業で動画を作る組織。Remotion のプロジェクトを手元に持って動画を作る人（コードを書く人、AIエージェントに指示する人、Studio で編集する人）ごとに1席 | 1席あたり月25ドル | 【一次】 | [S2][S3] |
| Remotion for Automators | 自動化を作る組織（renderMedia() や npx remotion render などをプログラムから呼ぶコードを持つ） | 1レンダー0.01ドル、最低月100ドル | 【一次】 | [S2][S3] |
| Enterprise | 規約・価格の個別調整、書類対応、専用サポートなど | 月500ドルから | 【一次】 | [S2][S3] |

Creators の席が要らないのは、AIエージェント、完成した動画を確認・受け取るだけの人、自動化を作る開発者。【一次】[S3]

Studio と Player でのプレビューはレンダー数に数えない。【一次】[S3]
> 「Previews in the Remotion Studio or Remotion Player do not count as Renders.」[S3]

代理で動画を作る場合、相手に完成した動画ファイルだけを渡すなら、相手の人数は数えず、作る側の人数だけで判定する。相手が Remotion のプロジェクトを持つ・動かす場合や、同じプロジェクトで外部の制作会社やフリーランスと共同作業する場合は、人数を合算する。【一次】[S3]

返金はない。商用利用の前に評価できるから、という理由。【一次】[S3]
> 「There are no refunds because you can already evaluate Remotion before using it commercially.」[S3]

Creators の契約をやめても、作った動画を使う権利は残る。【一次】[S3]

#### コーデックの特許
Remotion のライセンスは Remotion の利用だけを対象とし、H.264/AVC、HEVC、AAC などのコーデックに関する第三者の特許のライセンスは含まない。用途と法域によっては別のライセンスや使用料が要る場合があり、当てはまるかを判断するのは利用者の責任だと FAQ は書いている。【一次】[S3]
> 「No. A Remotion license covers your use of Remotion only.」[S3]

#### テレメトリ
サーバー側（自分のPCでの CLI や Node.js の）レンダリングには自動のテレメトリはない。ブラウザ内でのレンダリング（クライアント側）は既定でテレメトリが有効で、無効にできない。【一次】[S3]
> 「For server-side rendering, there is no automatic telemetry.」[S3]

5.0 では Automators の利用者にはテレメトリが必須になる。無料ライセンスと Creators では任意のまま。【一次】[S3]
> 「Telemetry in server-side rendering remains voluntary for Free License users」[S3]

CLI には v4.0.539 から --license-key がある。無料ライセンスの対象なら、鍵の代わりに free-license という値を渡す。【一次】[S5]

#### 5.0 での変更
LICENSE.md の冒頭に、5.0 でライセンスが少し変わるとある。変更の中身は GitHub の PR #3750 にあるが、今回は読めていない。【一次】[S1]
> 「In Remotion 5.0, the license will slightly change.」[S1]

FAQ には、5.0 でライセンスと規約を変えて Automators の利用者のテレメトリを必須にすると書かれている（上記「テレメトリ」）。PR #3750 の変更がこれだけかは確認できていない。【一次】[S3]
> 「we are making a change to our license and terms in Remotion 5.0」[S3]

2026-11-20 時点で GitHub の main ブランチの package.json の version は 4.0.545（npm の公開版と同じかは未確認）。【一次】[S18]

### 2. 書き出しの設定

#### コーデックと品質
主な映像コーデックは h264（既定）、h265、vp8、vp9、av1、prores。--codec を指定しなければ H.264 になる。【一次】[S4][S5]
> 「The main video codecs are h264 (default), h265, vp8, vp9, av1 and prores.」[S4]

出力ファイルの拡張子でも既定のコーデックが決まる。.mp4 は h264、.mov は prores、.mkv は h264-mkv、.webm は vp8。【一次】[S4]

CRF（小さいほど高画質、大きいほど小さいファイル）は、コーデックごとに範囲と既定値が違う。【一次】[S4]
> 「Every codec has it's own range of acceptable values and a different default.」[S4]

| コーデック | 最小（最高画質） | 最大（最高圧縮） | 既定 | 確度 | 出典 |
|---|---|---|---|---|---|
| H.264 | 1 | 51 | 18 | 【一次】 | [S4] |
| H.265 | 0 | 51 | 23 | 【一次】 | [S4] |
| VP8 | 4 | 63 | 9 | 【一次】 | [S4] |
| VP9 | 0 | 63 | 28 | 【一次】 | [S4] |
| AV1 | 0 | 63 | 30 | 【一次】 | [S4] |

ビットレートで品質を決める --video-bitrate と CRF は併用できない。【一次】[S4]
> 「The videoBitrate option cannot be combined with crf.」[S4]

H.264 の x264 プリセットは --x264-preset で変えられ（v4.0.22〜）、既定は medium。【一次】[S5]

色空間は --color-space で指定する（v4.0.28〜）。4.0 系の既定 default は bt601 と同じ（v4.0.424〜）で、5.0 から既定が bt709 になる。正確な色のためには画像形式を png にすることも勧められている。YouTube 側の推奨は [アップロード仕様と書き出し設定.md](../youtube/アップロード仕様と書き出し設定.md) を参照。【一次】[S5]

#### 音声
H.264 の動画に入る音声の既定は aac。pcm-16 や mp3 も選べるが、組み合わせによって拡張子（コンテナ）が決まる。【一次】[S4]

mp3、wav、aac をコーデックに指定すると音声だけを書き出せる。【一次】[S4]

音声ビットレートの既定はサーバー側のレンダーで320k。【一次】[S5]
> 「Default for server-side renders: 320k.」[S5]

出力のサンプルレートの既定は 48000 Hz（--sample-rate、v4.0.448〜）。元の音声に合わせるよう勧められている。【一次】[S5]
> 「The default is 48000 Hz. Match this to your source audio to avoid resampling artifacts.」[S5]

--separate-audio-to（v4.0.123〜）を使うと、音声を本体に入れずに別ファイルとして書き出せる。【一次】[S5]

#### 並列化
ローカルのレンダリングでの並列数（concurrency）は、同時に開くブラウザのタブの数。各タブがページを描いてスクリーンショットを撮る。【一次】[S10]
> 「In local rendering, concurrency refers to how many browser tabs are opened in parallel during a render.」[S10]

--concurrency の最小は1、最大はCPUのスレッド数。50% のような割合でも指定できる。最適な値は npx remotion benchmark で探す。【一次】[S5][S9]
> 「The maximum is the amount of CPU threads you have」[S5]

並列数を上げすぎると効果が頭打ちになり、マシンが過負荷になってレンダーが落ちることがある。【一次】[S10]
> 「too high concurrency will lead to diminishing returns and to overload of the machines, which might crash a render.」[S10]

フレームのレンダリングと並行してエンコードもできる（並列エンコード）。v4.0.533 からは空きメモリに応じて自動で無効にはならないので、メモリ不足になったら --disallow-parallel-encoding を付ける。【一次】[S4][S5]
> 「This makes the rendering process more memory-efficient, but possibly slower.」[S5]

#### Windows での注意
--props にJSON文字列を直接書く方法は Windows のシェルでは使えない（" が消えるため）。JSONファイルのパスを渡す。【一次】[S5]
> 「Inline JSON string isn't supported on Windows shells」[S5]

### 3. レンダリング時間とGPU

#### 公式の説明
動画のレンダリングは、コンピュータにとって最も重い処理の1つだと公式は書いている。【一次】[S9]
> 「Video rendering is one of the most heavy workloads a computer can take on.」[S9]

ヘッドレスモードでは多くの場合 GPU が無効で、レンダリングがかなり遅くなることがある。Studio と Player では GPU があれば既定で使われる。【一次】[S7]
> 「By default in many cases, the GPU is disabled in headless mode, which can lead to a significant slowdown in rendering time.」[S7]

GPU で速くなる要素は、WebGL（Three.js、Skia など）、動画のデコード、box-shadow、text-shadow、linear-gradient / radial-gradient の背景、filter の blur と drop-shadow、transform、多くの2D Canvas の処理。【一次】[S7]

これらの効果は、前もって画像にしておくと最も速いとされる。【一次】[S9]
> 「Consider replacing those effects with a precomputed image for the best performance.」[S9]

GL のバックエンドは --gl で選ぶ。4.0 の既定は null（Chrome に任せる）で、5.0 の既定は angle。4.0 で WebGL・WebGPU・Three.js を使うなら、デスクトップでは angle が推奨。使わないなら既定が最良とされる。【一次】[S8][S5]
> 「On a desktop, angle is recommended」[S8]

angle にはメモリリークの問題があり、長い動画は複数に分けてレンダリングするよう勧められている。【一次】[S8]
> 「Memory leaks are a known problem with angle. We recommend to split up long renders into multiple parts when rendering large videos」[S8]

#### ハードウェアエンコード（NVENC）
ハードウェアエンコードは v4.0.228 から。Linux と Windows の NVENC（NVIDIA GPU が必要）は v4.0.484 から。【一次】[S6]
> 「Linux and Windows: Acceleration using NVENC (requires an NVIDIA GPU) (from v4.0.484)」[S6]

既定は無効（disable）。if-possible にすると使えるときだけ使い、required にすると使えないときにレンダーが失敗する。Studio では書き出し画面の Advanced タブで設定する。【一次】[S6][S5]

NVENC の条件は NVIDIA GPU、ドライバ（525以上を推奨）、h264_nvenc / hevc_nvenc を含む FFmpeg。Remotion に同梱の Windows x64 用 FFmpeg にはこの2つが入っている。対象は H.264 と H.265 だけ。【一次】[S6]

CRF は NVENC と併用できない。if-possible で CRF を指定するとソフトウェアエンコードに戻る。【一次】[S4][S6]

ハードウェアエンコードは既定ではファイルがかなり大きくなる。公式は --video-bitrate での調整を勧め、Full HD の H.264 では 8M でソフトウェアエンコードと同じくらいのサイズになったとしている。【一次】[S6]
> 「We find that --video-bitrate=8M achieves a similar file size than software encoding when exporting a H.264 Full HD video.」[S6]

ハードウェアエンコードが効いているかは、--log=verbose のログで確かめる（例: h264_nvenc, hardware accelerated: true）。ただし公式は、ログの文言そのものに頼らないよう注意している。【一次】[S6]
> 「Don't rely on the exact wording of the log message to determine if hardware acceleration is being used.」[S6]

#### その他の速度の要因
画像形式は png より jpeg が速い（既定は jpeg）。透過の動画には png が必要。vp8 / vp9 は圧縮が強いぶんエンコードがとても遅い。解像度が高いほど遅い。【一次】[S9][S5]

動画素材を埋め込むなら @remotion/media の <Video> が最も速い。従来の <Html5Video> と <OffthreadVideo> は最適化されていない。【一次】[S9]

--log=verbose で遅いフレームが一覧に出る。各スレッドの最初のフレームは初期化のぶん遅いことがある。【一次】[S9]
> 「Consider that the first frames rendered in a thread might be slow due to initialization.」[S9]

1フレームの delayRender() の待ちは既定で30000ミリ秒でタイムアウトする（--timeout）。【一次】[S5]

--frames で一部のフレームだけを書き出せる。v4.0.502 からは複数の範囲をつないで1本にできる。【一次】[S5]

#### 第三者の計測例
Zenn の記事（2026-01-28 検証）では、Windows 11 Pro、Remotion v4.0.398、Node.js 18.x で、約115秒・5シーン・3,471フレーム（30fps）・1920x1080、口パク（リップシンク）のキュー781個を含む動画を3回レンダリングし、平均2分52.83秒（標準偏差0.80秒）、動画1秒あたり約1.5秒だった。CPU の型番は書かれていない。【二次】[S19]
> 「2分の動画が約3分で完成する。」[S19]

同じ記事は、全体の時間の約91.7%がフレームのレンダリングだったと推定している（工程別の時間は推定値）。【二次】[S19]
> 「91.7%がフレームレンダリング。ここが圧倒的なボトルネックだ。」[S19]

同じ記事は、並列数6と x264 の fast プリセットなどを組み合わせると180秒が100秒になると見込んでいるが、これは実測ではなく推定。【二次】[S19]
> 「組み合わせによる効果を推定した。」[S19]

同じ記事は Remotion の既定の並列数を3としている。公式資料ではこの既定値を確認できていない。【二次】[S19]
> 「Remotionはデフォルトで3並行でフレームをレンダリングする。」[S19]

同じ記事では、日本語フォント（Noto Sans JP）の2ウェイトを読み込むとフォントのために248回のネットワークリクエストが出たので、ウェイトを1つに減らしている。【二次】[S19]
> 「Noto Sans JP（日本語フォント）は漢字をカバーするためにサブセットが多い。」[S19]

同じ記事では、フォントの読み込みを設定しないと日本語の字幕が豆腐（□）になり、エラーも出ないとしている。【二次】[S19]
> 「エラーメッセージが出ないので気づきにくい。」[S19]

別の Zenn 記事（SNS-tool.online）では、ConoHa VPS（4コア / 4GB RAM）上の Docker コンテナで renderMedia() を concurrency 4 で動かし（H.264・24fps・1080p と図にある）、10分の動画のレンダリングに5〜20分かかるとしている。Remotion のバージョンと計測の方法は書かれていない。【二次】[S20]
> 「Remotionのレンダリングは CPU集約型 で、10分の動画に5〜20分かかります。」[S20]

同じ記事は、10分を超える動画のレンダリングで 4GB の VPS のメモリが逼迫したので、concurrency を CPU のコア数に合わせ、同時に動かすレンダーを1つに制限したとしている。【二次】[S20]
> 「10分超の動画をレンダリングすると、4GBのVPSでもメモリが逼迫します。」[S20]

### 4. 音声の長さからタイムラインを組む

Composition に calculateMetadata()（v4.0.0〜）を渡すと、非同期に求めた値で動画の長さ（durationInFrames）、fps、幅・高さを決められる。props も同時に変換して返せる。【一次】[S11]

公式の例では、素材の秒数に fps を掛けて Math.ceil() で切り上げ、フレーム数にしている。【一次】[S11]

useEffect() と delayRender() で長さを取る方法は、v4.0 から推奨されない。並列のレンダーで worker を立てるたびにも実行され、無駄な API 呼び出しやレート制限につながるため。【一次】[S11]
> 「This technique is not recommended anymore since v4.0」[S11]
> 「Since a render process might be highly concurrent, this might lead to unnecessary API calls and rate limitations.」[S11]

--width などの上書きは calculateMetadata() より優先され、--scale は最後に適用される。【一次】[S11]

音声の長さを取る getAudioDurationInSeconds() は非推奨になり、getMediaMetadata() を使うよう案内されている。【一次】[S12]
> 「This function has been deprecated. Use getMediaMetadata() instead, which is faster and supports more formats.」[S12]

getMediaMetadata() は Remotion のパッケージの関数ではなく、公式資料にある get-media-metadata.ts のコード例で、自分のプロジェクトに置いて使う。Mediabunny（依存のないライブラリ。ブラウザ、Node.js、Bun で動く）を使い、長さ（秒）・寸法・fps を返す。音声ファイルなら寸法と fps は null になる。【一次】[S11][S13]
> 「See Getting metadata using Mediabunny for the snippet for get-media-metadata.ts.」[S11]
> 「If the media file is an audio file, return null for the dimensions and frame rate.」[S13]

Mediabunny は fetch() で素材を読むので、CORS で止められない場所に素材を置く必要がある。止められる場合は @remotion/media-utils の getVideoMetadata() を使う。【一次】[S13]
> 「The assets are loaded using fetch(), so they must be accessible for the current website and not be blocked by CORS.」[S13]

<Series> を使うと、場面を順番につないで再生できる。各 Series.Sequence の durationInFrames は、最後の1つだけ Infinity にでき、それ以外は正の整数でなければならない。【一次】[S14]
> 「Only the last <Series.Sequence /> instance is allowed to have Infinity as a duration, all previous one must have a positive integer.」[S14]

offset に正の数を渡すとその分だけ間が空き、負の数を渡すと前の場面に重ねて早く始まる。offset はそれ以降の場面もずらす。【一次】[S14]
> 「Pass a negative number to start the sequence earlier, and to overlay the sequence with the one that comes before.」[S14]

v4.0.443 から <Series> は内部的に <Sequence> になり、<Sequence> の props をすべて受け付ける。【一次】[S14]

場面を前もって読み込んでおく premountFor の既定は、Studio では v4.0.535 から2秒。Player などの一般の既定は v4 で0秒、v5 で2秒。【一次】[S14]

### 5. テロップと字幕の同期

公式の Captions のガイドは、.srt / .vtt の読み込み、音声からの文字起こし、動画内への表示、字幕の書き出し（焼き込み / .srt）の4項目からなる。字幕のユーティリティの API は @remotion/captions。【一次】[S15]

表示の手順: 字幕の JSON を読み込む間は useDelayRender() でレンダーを待たせ、createTikTokStyleCaptions() で字幕をページにまとめ、各ページを <Sequence> で表示する。【一次】[S16]

combineTokensWithinMilliseconds で一度に表示する語の量を決める。pageBreakAfter: true の字幕のあとでページが切り替わる。【一次】[S16]
> 「The combineTokensWithinMilliseconds option controls how many words appear at once」[S16]
> 「If a caption has pageBreakAfter: true, the current page ends after that caption and the next caption starts a new page.」[S16]

ページの中の各トークンは fromMs / toMs を持ち、現在のフレームの時刻と比べて、話している語だけ色を変える例が公式にある。【一次】[S16]

焼き込み字幕は、表示の手順どおりに作って普通にレンダーすればよい。別の .srt ファイルとして出すときは <Artifact> と serializeSrt() を使う。【一次】[S17]
> 「To export subtitles as a separate .srt file, use the <Artifact> component together with serializeSrt().」[S17]

書き出した .srt は out/[composition-id]/subtitles.srt に保存される。【一次】[S17]
> 「The artifact will be saved to out/[composition-id]/subtitles.srt when rendering.」[S17]

1語ずつの字幕は、createTikTokStyleCaptions() でページにしてから serializeSrt() に渡すと、複数の語を1行にまとめられる。【一次】[S17]

VOICEVOX と Remotion で解説動画を作るテンプレート（nyanko3141592 さんの remotion-voicevox-template）を試した Zenn のスクラップでは、台本データ（src/data/script.ts）の各セリフに durationInFrames と pauseAfter があり、npm run voices で VOICEVOX から音声を作ると public/voices/durations.json に各セリフの秒数とフレーム数が出る。この値を台本データに反映し直す必要があるとしている。試した VOICEVOX は 0.25.1。テンプレートでは話しているキャラごとに字幕の色が変わる。【二次】[S21]
> 「これを最初のJSONに再反映する必要がある。」[S21]

## このチャンネルでの使い方（提案）
> ※この節は上の事実から導いた提案で、事実ではない。
- 運営が個人または3人以下のチームなら無料ライセンスで足りる。ただし、運営者が4人以上の会社の業務として作る場合や、外部の編集者と同じ Remotion プロジェクトで作業して合計が4人以上になる場合は、会社ライセンス（Creators なら1席月25ドル）が要る。体制が変わったら FAQ を読み直す。（根拠: [S1][S3]）
- 5.0 へ上げるときは、LICENSE.md の変更点、GL の既定（angle）、色空間の既定（bt709）、premountFor の既定の変化を確認してから上げる。package.json で Remotion のバージョンを固定しておく。（根拠: [S1][S5][S8][S14]）
- 4.0 系のうちは --color-space=bt709 を明示しておく（既定は bt601 と同じ）。YouTube 側の色の推奨は [アップロード仕様と書き出し設定.md](../youtube/アップロード仕様と書き出し設定.md) と照らし合わせる。（根拠: [S5]）
- 制作PC（RTX 4070 Ti SUPER）では、v4.0.484 以降で --hardware-acceleration if-possible と --video-bitrate を使い、--log=verbose で h264_nvenc が使われたか確かめる。CRF を併用するとソフトウェアエンコードに戻るので外す。画質とファイルサイズはソフトウェアエンコード（CRF 18）と1本比べてから決める。（根拠: [S4][S6]）
- 並列数は固定値を書かず、制作PCで npx remotion benchmark を1回走らせて決める。長尺（8〜12分）で落ちたら、並列数を下げる、--disallow-parallel-encoding を付ける、angle なら分割レンダーにする、の順で試す。（根拠: [S5][S8][S9][S10]）
- 影・グラデーション・ぼかしを多用したテロップは GPU がないと遅いので、固定の装飾は画像にしておく。（根拠: [S7][S9]）
- 台本の各セリフを VOICEVOX で1ファイルずつ書き出し、calculateMetadata() の中で getMediaMetadata() で秒数を取り、Math.ceil(秒数 × fps) を各 Series.Sequence の長さにし、合計を durationInFrames にする。間を空けたいときは offset を使う。（根拠: [S11][S13][S14]）
- 字幕は、セリフの文字列と上で求めた開始・終了時刻から Caption の配列を作り、同じデータから焼き込みテロップと YouTube に上げる .srt の両方を出す。こうすると画面のテロップと字幕トラックの時刻がずれない。字幕の見た目の方針は [テロップ・字幕.md](テロップ・字幕.md) に従う。（根拠: [S15][S16][S17]）
- props は JSON ファイルで渡す（Windows のシェルでは JSON 文字列を直接書けない）。日本語フォントは必要なウェイトだけを読み込み、最初の1本で豆腐になっていないか目で確かめる。フォントの権利は [フォントのライセンス.md](../legal/フォントのライセンス.md) で確認する。（根拠: [S5][S19]）
- Minecraft の録画（Flashback / Replay Mod の書き出し）を埋め込むときは @remotion/media の <Video> を使う。（根拠: [S9]）
- 確認用には --frames で問題の区間だけを書き出し、全体のレンダーを待たない。（根拠: [S5]）

## わかっていないこと・要確認
- 5.0 でライセンスがどう変わるか（PR #3750 の中身）と、5.0 の公開時期。GitHub の Web ページは読めないので、公開後に LICENSE.md を読み直す。[S1]
- Terms and Conditions の正式な定義（従業員に業務委託やアルバイトを含むか）。今回は Terms のページを読んでいない。LICENSE.md は employees、FAQ は people と書き方が違う。[S1][S3]
- ローカルの CLI での --concurrency の既定値。公式資料では確認できず、Zenn の記事は3としている。[S5][S19]
- このチャンネルの制作PC（RTX 4070 Ti SUPER）で、8〜12分・1920x1080 の動画のレンダリングに何分かかるか。NVENC と --gl=angle でどれだけ縮むか。第三者の数値は環境が違い、CPU も不明。[S19]
- ハードウェアエンコードの画質（同じビットレートでのソフトウェアエンコードとの差）。公式はファイルサイズの話だけ。[S6]
- npm で公開されている最新版と main ブランチの 4.0.545 が同じか。[S18]
- 音声からの文字起こし（Transcribing audio）の方法と日本語への対応。今回は読んでいない。[S15]
- コーデックの特許（H.264/AVC、AAC など）について、このチャンネルの使い方（自分のPCで書き出して YouTube に上げる）で別のライセンスが要るか。Remotion の FAQ は利用者の責任としか書いておらず、今回は調べていない。[S3]
- remotion-voicevox-template の GitHub の README・ライセンス。github.com のページは読めず、今回は raw も読んでいない。[S21]
- <Audio> の音量調整・ダッキングの方法は今回読んでいない。音量の基準は [音量とラウドネス.md](../audio/音量とラウドネス.md) を参照。

## 参照先
- [S1] Remotion License（LICENSE.md） — Remotion — https://raw.githubusercontent.com/remotion-dev/remotion/main/LICENSE.md — 更新日不明（本文に Copyright © 2026） — 取得: 2026-11-20 — 原文: 読んだ
- [S2] License & Pricing — Remotion — https://www.remotion.dev/docs/license/pricing — 更新日不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S3] License FAQ — Remotion — https://www.remotion.dev/docs/license/faq — 更新日不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S4] Encoding Guide — Remotion — https://www.remotion.dev/docs/encoding — 更新日不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S5] npx remotion render — Remotion — https://www.remotion.dev/docs/cli/render — 更新日不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S6] Hardware accelerated encoding — Remotion — https://www.remotion.dev/docs/hardware-acceleration — 更新日不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S7] Using the GPU — Remotion — https://www.remotion.dev/docs/gpu — 更新日不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S8] --gl flag — Remotion — https://www.remotion.dev/docs/gl-options — 更新日不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S9] Performance Tips — Remotion — https://www.remotion.dev/docs/performance — 更新日不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S10] Concurrency — Remotion — https://www.remotion.dev/docs/terminology/concurrency — 更新日不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S11] Variable duration and dimensions — Remotion — https://www.remotion.dev/docs/dynamic-metadata — 更新日不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S12] getAudioDurationInSeconds() — Remotion — https://www.remotion.dev/docs/get-audio-duration-in-seconds — 更新日不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S13] Getting metadata from a video in JavaScript — Remotion — https://www.remotion.dev/docs/mediabunny/metadata — 更新日不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S14] Series component — Remotion — https://www.remotion.dev/docs/series — 更新日不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S15] Captions — Remotion — https://www.remotion.dev/docs/captions/ — 更新日不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S16] Displaying captions — Remotion — https://www.remotion.dev/docs/captions/displaying — 更新日不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S17] Exporting subtitles — Remotion — https://www.remotion.dev/docs/captions/exporting — 更新日不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S18] packages/core/package.json — Remotion（GitHub main ブランチ） — https://raw.githubusercontent.com/remotion-dev/remotion/main/packages/core/package.json — 取得時点の main — 取得: 2026-11-20 — 原文: 読んだ
- [S19] 『AIで作る業務動画 Day 28｜2分の動画が3分でレンダリングできる理由と最適化の実践』 — Akira（Zenn） — https://zenn.dev/akira_cloudjob/articles/20260128-performance-optimization — 検証日 2026-01-28 — 取得: 2026-11-20 — 原文: 読んだ
- [S20] 『テーマを入力するだけでYouTube動画が完成する全自動システムを作った』 — SNS-tool.online（Zenn） — https://zenn.dev/sns_tool/articles/28f993528bf3a7 — 公開日不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S21] 『コードでゆっくり/ずんだもん解説動画を作れるremotionのvoicevox-templateを試す』 — kurehajime（Zenn スクラップ） — https://zenn.dev/kurehajime/scraps/02272b238a876b — 公開日不明 — 取得: 2026-11-20 — 原文: 読んだ
