# YouTube Data API v3 での投稿（videos.insert・クォータ・監査・OAuth・予約公開・サムネイル・字幕）

> 対象: YouTube Data API v3 で動画を上げるときの仕様。videos.insert のクォータ、未監査プロジェクトの非公開制限（2026-11-02 に撤回）、監査とクォータ拡張、OAuth、予約公開（publishAt）、サムネイル設定、字幕のアップロード、再開可能アップロード。
> 使う場面: movie リポジトリの投稿スクリプトを作る・直すとき。投稿前にメタデータの設定項目を確かめるとき。
> 調査日: 2026-11-19 ／ mc_version: 対象外（MCに関係しない）
> 関連: [多言語化と自動吹き替え.md](多言語化と自動吹き替え.md), [AI生成・改変コンテンツの開示.md](AI生成・改変コンテンツの開示.md), [ショートの仕様.md](ショートの仕様.md), [アナリティクス指標.md](アナリティクス指標.md)

## 要点
- **2026-11-02 に、未監査のAPIプロジェクトから上げた動画を非公開に制限する方針（2020-07-28 から）が撤回された。** 【一次】[S2][S1]
- そのため、status.privacyStatus を指定しないと、APIで上げた動画は既定で public（公開）になる。非公開で上げたいなら必ず private を指定する。 【一次】[S1][S2]
- videos.insert は 2026-06-01 から専用のクォータ枠（Video Uploads）に移った。既定は1日100回、1回1ユニット。 【一次】[S1][S2][S3]
- search.list も videos.insert と同じく専用の枠（既定1日100回）。この2つ以外のメソッドは合わせて1日10,000ユニット。毎日、太平洋時間の午前0時にリセットされる。無効なリクエスト（invalid requests）も最低1ユニットかかる。 【一次】[S3]
- 主なコスト: thumbnails.set 約50、captions.insert 400、videos.update 50、playlistItems.insert 50、videos.list 1。 【一次】[S3][S6][S7]
- 既定より多いクォータが欲しいときは、先に監査（API Compliance Audit）を通す必要がある。 【一次】[S4][S2]
- OAuth の同意画面のユーザーの種類が external（外部）で、公開ステータスが「Testing」のままだと、リフレッシュトークンは7日で失効する（名前・メール・プロフィールのスコープだけの場合を除く）。 【一次】[S10]
- 予約公開（status.publishAt）は、非公開でまだ一度も公開されていない動画にだけ設定できる。過去の日時を入れると即公開になる。 【一次】[S5]
- 字幕の captions.insert は youtube.force-ssl（または youtubepartner）スコープが必要で、youtube.upload スコープでは呼べない。2024-04-12 以降はタイミング情報のない字幕ファイルは失敗する。 【一次】[S7][S2]
- 再開可能アップロードでは、5xx（500/502/503/504）は指数バックオフで再開する。セッションURIには寿命があり、期限切れだと404になる。 【一次】[S8]
- 2026-11-16 から paidProductPlacementDetails.hasPaidProductPlacement は既定で false にならない。有料プロダクト プレースメントがないと申告するには、明示的に false を送る。 【一次】[S2]
- ショートのカスタムサムネイルも thumbnails.set で設定できるようになった（2026-11-03。動画の処理完了後に呼ぶ）。サムネイルの上限は 2026-09-14 に 2MB から 50MB に上がった。 【一次】[S2][S6]

## 詳細

### 1. 未監査プロジェクトからの投稿を非公開に制限する方針は撤回された（2026-11-02）

2020-07-28 の方針: 2020-07-28 より後に作られた未監査のAPIプロジェクトから videos.insert で上げた動画は、すべて非公開表示に制限され、解除には利用規約への準拠を確かめる監査が必要だった。 【一次】[S2]
> 「All videos uploaded using the videos.insert endpoint from unverified API projects created after 28 July 2020 will be restricted to private viewing mode.」[S2]

（訳）2020年7月28日より後に作られた未検証のAPIプロジェクトから videos.insert で上げた動画は、すべて非公開表示に制限される。

当時、未検証のクライアントで上げたクリエイターには、動画が非公開にロックされた旨のメールが届くとされていた。2020-07-28 より前に作られたプロジェクトは対象外だった。 【一次】[S2]
> 「API projects created prior to 28 July 2020 are not affected by this change.」[S2]

2026-11-02 の改訂履歴で、この制限がなくなったことが告知された。 【一次】[S2]
> 「Videos uploaded through the videos.insert method from unverified API projects are no longer restricted to private viewing mode.」[S2]
> 「This change reverses the policy announced on July 28, 2020」[S2]

（訳）未検証のAPIプロジェクトから videos.insert で上げた動画は、もう非公開表示に制限されない。この変更は2020年7月28日に告知した方針を覆すもの。

現在のリファレンス（videos.insert、2026-11-12 更新）にも同じ内容が書かれている。privacyStatus を指定しなければ既定は public で、アカウントの設定によっては既定が private になる場合がある、とヘルプセンターを参照している（そのヘルプは未読）。 【一次】[S1][S5]
> 「If you don't specify a value for this property, the uploaded video's privacy status defaults to public.」[S1]
> 「Videos uploaded from unverified API projects are not restricted to private viewing mode.」[S1]

日本語版のリファレンスにも「未確認の API プロジェクトからアップロードされた動画は、非公開視聴モードに制限されません」とある。ただし日本語版の最終更新日の表示は 2026-10-15 で、撤回の告知（11-02）より前の日付になっている。 【一次】[S11]

### 2. クォータ（2026-11-19 時点）

既定の割り当ては、search.list 100回、videos.insert 100回、その他のエンドポイント合計で1日10,000ユニット。 【一次】[S3][S4]
> 「100 search.list calls, 100 videos.insert calls, and 10,000 units per day combined for all other endpoints」[S3]
> 「Daily quotas reset at midnight Pacific Time (PT).」[S3]
> 「All API requests, including invalid requests, incur a quota cost of at least one point.」[S3]

videos.insert のリファレンスの記載: 【一次】[S1]
> 「Quota impact: 100 calls per day. A call to this method has a quota cost of 1 unit in the Video Uploads quota bucket.」[S1]

videos.insert のコストの変遷（改訂履歴より）:

| 時点 | videos.insert の扱い | 確度・出典 |
|---|---|---|
| 2025-12-04 の文書更新まで | 約1600ユニット（共通の10,000ユニット枠から消費していたことは、2026-06-01 の項目で専用枠に移したと書かれていることから読み取ったもの。本数は計算で1日6本程度） | 【一次】[S2]（共通枠は読み取り、本数は計算） |
| 2025-12-04 の文書更新 | 約100ユニットに変更 | 【一次】[S2] |
| 2026-06-01 から | 専用の枠に移行（search.list も同様）。他のメソッドは従来の枠 | 【一次】[S2] |
| 2026-11-19 時点 | 1回1ユニット、既定は1日100回 | 【一次】[S1][S3] |

> 「reflect a change in the quota cost of a video upload from approximately 1600 units to approximately 100 units.」[S2]
> 「API calls to the videos.insert and search.list methods will be charged to their own respective quota buckets.」[S2]

投稿まわりで使うメソッドのコスト（共通の10,000ユニット枠から消費）: 【一次】[S3]

| リソース | メソッド | コスト | 出典 |
|---|---|---|---|
| videos | insert | 専用枠。1日100回、1回1 | 【一次】[S3][S1] |
| videos | update / delete | 50 / 50 | 【一次】[S3] |
| videos | list | 1 | 【一次】[S3] |
| thumbnails | set | 50（メソッドの説明では約50） | 【一次】[S3][S6] |
| captions | insert / update / list / delete | 400 / 450 / 50 / 50 | 【一次】[S3][S7] |
| playlistItems | insert | 50 | 【一次】[S3] |
| channels | list | 1 | 【一次】[S3] |

複数ページの結果を返すメソッドは、追加のページを取るたびにコストがかかる。 【一次】[S3]
2026-06-03 に追加された videos.batchGetStats（動画の統計をまとめて取る）は、専用の枠で1回1ユニット、既定は1日10,000ユニット。 【一次】[S2]
クォータの使用量と上限は Google Cloud コンソールで見られる。 【一次】[S3][S2]

### 3. 監査とクォータの追加申請

既定を超えるクォータを申請するには、まずプロジェクトが利用規約に準拠していることを示す監査を受ける必要がある。 【一次】[S4]
> 「you must first complete an audit to show that your project is in compliance with the YouTube API Services Terms of Service.」[S4]
> 「All developers using YouTube's API Services must complete an API Compliance Audit in order to be granted more than the default quota allocation of 10,000 units.」[S2]（2021-07-01 の告知）

申請の窓口（2026-11-12 更新のガイド）: 【一次】[S4]

| 用途 | フォーム | 出典 |
|---|---|---|
| 監査を始める | YouTube API Services - Audit and Quota Extension Form。提出するとAPIサービスのチームから連絡が来る | 【一次】[S4] |
| 過去12か月以内に監査を通っていて、さらにクォータを増やす | Audit and Quota Extension Form | 【一次】[S4] |
| 監査に落ちた（[S4]）・増量を断られた（[S2] 2021-07-01 の告知） | Appeals Form | 【一次】[S4][S2] |
| YouTube側から定期監査の連絡が来た | Periodic Audit Form | 【一次】[S4] |
| 会社の買収などで支配権が変わった | Change of Control Form | 【一次】[S4][S2] |

> 「A member of YouTube's API Services team will contact you as soon as possible.」[S4]

2026-06-01 の改訂では、メソッドごとの枠にしたことで、YouTube がメソッドごとの使用状況に基づいて増量の申請を確認・承認できるようになり、増量までの道筋が簡単になると説明されている。増量の申請先は Quota Extension Form。 【一次】[S2]

### 4. OAuth（認可）

videos.insert は youtube.upload / youtube / youtubepartner / youtube.force-ssl のいずれかのスコープで呼べる。 【一次】[S1]
thumbnails.set も youtube.upload を含む4つのスコープで呼べる。 【一次】[S6]
captions.insert が受け付けるのは youtube.force-ssl と youtubepartner だけ。 【一次】[S7]
スコープの一覧での youtube.upload の説明は「Manage your YouTube videos.」[S9]。youtube.force-ssl は動画・評価・コメント・字幕の閲覧・編集・完全削除のスコープと説明されている。 【一次】[S9]
> 「Request the most narrow scope that supports your application's functionality.」[S9]

（訳）アプリの機能を満たす最も狭いスコープを要求すること。

デスクトップやコマンドラインのアプリは『OAuth 2.0 for Desktop Apps』のフローを使う。インストール型アプリは、認可コードを交換するときにリフレッシュトークンを自動で受け取る。 【一次】[S9]
> 「Installed applications and limited-input devices receive refresh tokens automatically」[S9]

OAuth トークンを付けないリクエストには API キーが要るが、API キーは公開データの取得だけに使う。 【一次】[S9]

リフレッシュトークンが使えなくなる条件（Google Identity の文書、2026-10-29 更新）: 【一次】[S10]
- ユーザーがアクセスを取り消した。
- 6か月使われていない。
> 「The refresh token has not been used for six months.」[S10]
- 同意画面が外部ユーザー向けで、公開ステータスが Testing のプロジェクトは、7日で失効するトークンが発行される（名前・メール・プロフィールのスコープだけの場合を除く）。
> 「publishing status of "Testing" is issued a refresh token expiring in 7 days」[S10]
- 1つの Google アカウント・1つの OAuth クライアントIDあたり100個までで、超えると最も古いものが警告なしに無効になる。
> 「creating a new refresh token automatically invalidates the oldest refresh token without warning.」[S10]

### 5. videos.insert のリクエストとメタデータ

送信先は `POST https://www.googleapis.com/upload/youtube/v3/videos`。ファイルの上限は 256GB、MIME タイプは video/* か application/octet-stream。 【一次】[S1]
insert で設定できる主な項目: snippet.title / description / tags[] / categoryId / defaultLanguage、localizations、status.embeddable / license / privacyStatus / publicStatsViewable / publishAt / selfDeclaredMadeForKids / containsSyntheticMedia、recordingDetails.recordingDate。 【一次】[S1]
タイトルは100文字まで、説明は5000バイトまで、タグは合計500文字まで。 【一次】[S5]
> 「The property value has a maximum length of 100 characters and may contain all valid UTF-8 characters except < and >.」[S5]
> 「The property value has a maximum length of 5000 bytes」[S5]

notifySubscribers（登録者に新着通知を送るか）の既定は True。大量に上げるチャンネルは False にしてもよいと説明されている。 【一次】[S1]
> 「The default value is True.」[S1]

主なエラー: 既定言語を指定せずに翻訳メタデータを付けると defaultLanguageNotSet、予約時刻が不正だと invalidPublishAt、アップロード数の上限を超えると uploadLimitExceeded、プライバシー設定が不正だと forbiddenPrivacySetting。 【一次】[S1]

status.selfDeclaredMadeForKids で子ども向けであることを、status.containsSyntheticMedia でリアルな改変・合成（A/S）コンテンツを含むことを申告できる。containsSyntheticMedia は 2024-10-30 に追加された。開示の基準は [AI生成・改変コンテンツの開示.md](AI生成・改変コンテンツの開示.md) を参照。 【一次】[S5][S2]

有料プロダクト プレースメントの申告は、2026-11-16 から既定値がなくなった。 【一次】[S2]
> 「The paidProductPlacementDetails.hasPaidProductPlacement property no longer defaults to false.」[S2]

（訳）paidProductPlacementDetails.hasPaidProductPlacement は、もう既定で false にならない。

改訂履歴によれば、値を送らないと、有料プロダクト プレースメントを含まないと申告したことにならない。含まないと申告するには、videos.insert か videos.update で明示的に false を送る。 【一次】[S2]

### 6. 予約公開（status.publishAt）

publishAt は非公開の動画にだけ設定できる。ISO 8601 形式。 【一次】[S5]
> 「It can be set only if the privacy status of the video is private.」[S5]
> 「This property can only be set if the video's privacy status is private and the video has never been published.」[S5]

videos.update で publishAt を設定するときは、すでに非公開でも privacyStatus に private を一緒に送る必要がある。 【一次】[S5]
> 「you must also set the status.privacyStatus property value to private even if the video is already private.」[S5]

過去の日時を指定すると、すぐに公開される（private→public に変えたのと同じ）。 【一次】[S5]
> 「the effect of setting the status.publishAt property to a past date and time is the same as of changing the video's privacyStatus from private to public.」[S5]

### 7. サムネイル（thumbnails.set）

上限 50MB、形式は image/jpeg・image/png・application/octet-stream。コストは約50ユニット。 【一次】[S6]
ショートにもカスタムサムネイルを設定できるが、動画の処理が終わってから呼ぶ必要がある。処理前に呼ぶと反映されないことがある。 【一次】[S6][S2]
> 「call this method only after the video has finished processing (when processingDetails.processingStatus is succeeded).」[S6]

カスタムサムネイルを設定する権限がないアカウントでは 403 forbidden になる（権限の条件はこのページには書かれていない）。 【一次】[S6]
> 「The authenticated user doesn't have permissions to upload and set custom video thumbnails.」[S6]

改訂履歴: 2026-09-14 に上限が 2MB→50MB、2026-09-11 に動画のサムネイル取得で fhd（1080p）・qhd（1440p）・uhd（4K）が一部の動画で返るようになった、2026-11-03 にショートのカスタムサムネイルに対応（thumbnails リソースに shortsAspectRatio を追加）。 【一次】[S2]

### 8. 字幕（captions.insert）

上限 100MB、MIME タイプは text/xml・application/octet-stream・*/*。コストは400ユニット。 【一次】[S7]
> 「A call to this method has a quota cost of 400 units.」[S7]

必須の項目は snippet.videoId・snippet.language・snippet.name。snippet.isDraft も設定できる。 【一次】[S7]
字幕トラック名（snippet.name）は150文字まで（2024-03-12 の告知。超えると nameTooLong）。 【一次】[S2]
以前は sync=true でタイムコードなしの書き起こしを自動同期できたが、2024-03-13 に廃止が告知され、2024-04-12 でサポートが終わった。 【一次】[S2][S7]
> 「developers must include timing information when inserting or updating caption tracks or the upload will fail.」[S2]

（訳）字幕トラックを追加・更新するときはタイミング情報を含めなければならず、含めないとアップロードは失敗する。

翻訳字幕や翻訳タイトルの運用は [多言語化と自動吹き替え.md](多言語化と自動吹き替え.md) を参照。

### 9. 再開可能アップロード（resumable upload）

大きいファイル、切断が起きやすい回線、モバイルなど不安定な回線で有効。Google API クライアントライブラリの一部は再開可能アップロードを内蔵している。 【一次】[S8]
手順: `uploadType=resumable` で POST してセッションを開始 → 応答の Location ヘッダーのセッションURIを保存 → そこへ PUT で本体を送る。 【一次】[S8]
接続が切れた場合と、500・502・503・504 が返った場合は再開できる。5xx のあとは指数バックオフで再開する。 【一次】[S8]
> 「each resumable session URI has a finite lifetime and eventually expires.」[S8]
> 「If you send a request with an expired session URI, the server returns a 404 HTTP response code (Not Found).」[S8]

進み具合を確かめるには、空の PUT に `Content-Range: bytes */<全体サイズ>` を付けて送る。途中なら 308 が返り、Range ヘッダーに送信済みのバイト範囲が入る（0始まり）。 【一次】[S8]
ファイルをチャンクに分けて送る方法は、追加のリクエストが性能に響くため推奨されない。使う場合、チャンクは最後を除き 256KB の倍数で、すべて同じ大きさにする。 【一次】[S8]
> 「This approach is rarely necessary and is actually discouraged because it requires additional requests, which have performance implications.」[S8]
> 「The chunk size must be a multiple of 256 KB.」[S8]

### 10. 2026年の主な改訂（投稿以外も含む）

| 日付 | 内容 | 出典 |
|---|---|---|
| 2026-11-16 | 公開の再生回数に共同視聴（テレビを複数人で見る）を含める。収益・YPP の条件・エンゲージビューには影響しない。有料プロダクト プレースメントの既定値の廃止 | 【一次】[S2] |
| 2026-11-03 | thumbnails.set がショートのカスタムサムネイルに対応 | 【一次】[S2] |
| 2026-11-02 | 未監査プロジェクトの非公開制限を撤回 | 【一次】[S2] |
| 2026-10-15 | videos.list メソッドの説明で、status.selfDeclaredMadeForKids / status.madeForKids は、リクエストで指定したときだけ更新され、省略しても上書きされないと明確化 | 【一次】[S2] |
| 2026-09-14 | サムネイル・再生リスト画像の上限を 2MB→50MB | 【一次】[S2] |
| 2026-08-27 | 公開の再生回数を、全形式で再生開始の時点で数える方式にそろえる（収益はエンゲージ指標のまま）。詳しくは [アナリティクス指標.md](アナリティクス指標.md) | 【一次】[S2] |
| 2026-06-03 | videos.batchGetStats を追加 | 【一次】[S2] |
| 2026-06-01 | メソッドごとのクォータ枠へ移行開始（videos.insert と search.list から） | 【一次】[S2] |

## このチャンネルでの使い方（提案）
> ※この節は上の事実から導いた提案で、事実ではない。
- **投稿スクリプトでは status.privacyStatus を必ず "private" と明示する。** 未監査でも非公開に固定されなくなったので、指定を忘れると即公開になる。人の確認を経てから公開する関門は、APIの制限ではなく自分たちの運用で守る。（根拠: [S1][S2]）
- `minecraft_physics/docs/全体設計.md` にある、監査を受けていないAPIプロジェクトからの投稿は非公開に固定されるという記述は、2026-11-02 以降は当てはまらない。非公開を明示して上げる、という書き方に直す。（根拠: [S2]）
- 公開の操作も API でやるなら、人が確認したあとに videos.update で privacyStatus=private と publishAt を一緒に送る。過去時刻を入れると即公開になるので、送る前に時刻を検査する。（根拠: [S5]）
- 1本あたりの共通枠の消費は、thumbnails.set 50 + 字幕1言語 400 + 再生リスト追加 50 = 500ユニット程度（計算）。既定の10,000ユニットで1日20本分なので、監査やクォータ増量は当面いらない。字幕を多言語で上げると1言語400ずつ増える。（根拠: [S3][S7]）
- OAuth のスコープは youtube.upload と、字幕を上げるなら youtube.force-ssl を要求する。同意画面が Testing のままだと7日ごとに再認可が要るので、投稿スクリプトはトークンの失効を検出して再認可を促す作りにする。（根拠: [S7][S9][S10]）
- アップロードはクライアントライブラリの再開可能アップロードを使い、5xx は指数バックオフで再試行、404 なら最初からやり直す。チャンク分割は使わない。（根拠: [S8]）
- 仕様の確認は英語版のリファレンス（`?hl=en`）で行う。日本語版は更新日が英語版より古いことがある（2026-11-19 時点で videos.insert の日本語版は 2026-10-15、英語版は 2026-11-12）。（根拠: [S1][S11]）
- 毎回、selfDeclaredMadeForKids・containsSyntheticMedia・paidProductPlacementDetails.hasPaidProductPlacement を明示して送る。とくに有料プロダクト プレースメントは既定値がなくなったので false を送る。（根拠: [S2][S5]）
- ショートのサムネイルは、processingDetails.processingStatus が succeeded になるまで待ってから thumbnails.set を呼ぶ。（根拠: [S6]）
- テスト投稿は notifySubscribers=False にして、登録者に通知が飛ばないようにする。（根拠: [S1]）

## わかっていないこと・要確認
- 2026-11-02 の撤回が、それ以前に非公開ロックされた既存動画にも及ぶのかは、改訂履歴に書かれていない。
- クリエイターのアカウントの設定によって既定が private になる場合（Certain uploads might default to private based on creator account settings）の具体的な条件（ヘルプセンターの該当ページは未読）。
- 日本語版リファレンスの最終更新日（2026-10-15）が撤回の告知日（2026-11-02）より前なのに撤回後の内容が書かれている理由。日本語版が英語版の改訂をどこまで反映しているかは確認していない。
- uploadLimitExceeded（アップロードできる本数を超えた）の具体的な本数は、リファレンスに書かれていない。
- カスタムサムネイルを設定できる権限の条件（電話番号の確認など）は thumbnails.set のページにない。チャンネル機能の条件は別ファイルの範囲。
- OAuth の同意画面を本番（In production）にするときの Google の審査要件は未調査。
- captions.insert で受け付ける字幕ファイルの形式の一覧（captions リソースのページは未読）。
- 多言語音声トラックや自動吹き替えを API で操作する項目は、読んだページ（videos リソース、改訂履歴）には見当たらなかった。
- 再開可能アップロードのセッションURIの寿命の具体的な長さは書かれていない。

## 参照先
- [S1] Videos: insert（英語版） — Google for Developers（YouTube Data API） — https://developers.google.com/youtube/v3/docs/videos/insert?hl=en — 最終更新 2026-11-12 — 取得: 2026-11-19 — 原文: 読んだ
- [S2] Revision History（YouTube Data API v3 の改訂履歴） — Google for Developers — https://developers.google.com/youtube/v3/revision_history?hl=en — 最終更新 2026-11-17（各項目に日付） — 取得: 2026-11-19 — 原文: 読んだ
- [S3] Quota Calculator — Google for Developers — https://developers.google.com/youtube/v3/determine_quota_cost?hl=en — 最終更新 2026-11-12 — 取得: 2026-11-19 — 原文: 読んだ
- [S4] Quota and Compliance Audits — Google for Developers — https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits?hl=en — 最終更新 2026-11-12 — 取得: 2026-11-19 — 原文: 読んだ
- [S5] Videos（リソースの定義） — Google for Developers — https://developers.google.com/youtube/v3/docs/videos?hl=en — 最終更新 2026-11-17 — 取得: 2026-11-19 — 原文: 読んだ
- [S6] Thumbnails: set — Google for Developers — https://developers.google.com/youtube/v3/docs/thumbnails/set?hl=en — 最終更新 2026-11-12 — 取得: 2026-11-19 — 原文: 読んだ
- [S7] Captions: insert — Google for Developers — https://developers.google.com/youtube/v3/docs/captions/insert?hl=en — 最終更新 2026-11-12 — 取得: 2026-11-19 — 原文: 読んだ
- [S8] Resumable Uploads — Google for Developers — https://developers.google.com/youtube/v3/guides/using_resumable_upload_protocol?hl=en — 最終更新 2026-11-12 — 取得: 2026-11-19 — 原文: 読んだ
- [S9] Implement authorization — Google for Developers（YouTube Data API） — https://developers.google.com/youtube/v3/guides/authentication?hl=en — 最終更新 2026-11-12 — 取得: 2026-11-19 — 原文: 読んだ
- [S10] Using OAuth 2.0 to Access Google APIs — Google for Developers（Google Identity） — https://developers.google.com/identity/protocols/oauth2?hl=en — 最終更新 2026-10-29 — 取得: 2026-11-19 — 原文: 読んだ
- [S11] Videos: insert（日本語版。言語指定なしのURLで日本語版が表示された） — Google for Developers — https://developers.google.com/youtube/v3/docs/videos/insert — 最終更新の表示 2026-10-15 — 取得: 2026-11-19 — 原文: 読んだ
