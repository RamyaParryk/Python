AI Crypto Analyst Bot 📈🤖

仮想通貨の価格データと最新ニュースを収集し、Google Gemini AI (3.0/2.0 Flash) が相場を分析して X (旧Twitter) に自動投稿するPython製ボットです。

Windows (デスクトップ) と Linux (Umbrelサーバー等) の両方に対応しています。

✨ 特徴

AIによる相場分析: 単なるニュースの羅列ではなく、Gemini AIが「若い女性トレーダー」の人格で、その日の相場観を語ります。

マルチソース情報収集: 国内外の主要メディア（CoinPost, CoinTelegraph, Bloomberg, Yahoo Financeなど）計12サイトから情報を収集。

価格連動: CoinGeckoから BTC, ETH, XRP, SOL, BNB だけでなく、DOGE, FET, UNI, IMX, Gold(XAUT), XMR など計11銘柄の価格と変動率を取得し、分析に反映させます。

マンネリ防止: 「マクロ経済重視」「アルトコイン注目」「リスク警戒」「テクニカル分析」など、毎回異なる視点（8パターン）で分析を行います。

ハッシュタグ自動化: 記事の内容に合わせて適切なハッシュタグを自動選定します。

⚙️ 事前準備 (APIキーの取得)

このBotを動かすには、以下の2つのAPIキーが必要です。

X (Twitter) API Keys (Free TierでOK)

取得先: X Developer Portal

必要な権限: Read and Write (設定変更を忘れずに！)

Google Gemini API Key (無料枠でOK)

取得先: Google AI Studio

🚀 インストールと設定

1. リポジトリのクローン

git clone [https://github.com/あなたのユーザー名/リポジトリ名.git](https://github.com/あなたのユーザー名/リポジトリ名.git)
cd リポジトリ名


2. 設定ファイルの作成 (必須)

セキュリティのため、APIキーはコードに含まれていません。
フォルダ内に X-GoogleAPI.env という名前のファイルを作成し、以下の内容を記述してください。

ファイル名: X-GoogleAPI.env

# X (Twitter) Settings
X_API_KEY=あなたのAPI_KEY
X_API_SECRET=あなたのAPI_SECRET
X_ACCESS_TOKEN=あなたのACCESS_TOKEN
X_ACCESS_SECRET=あなたのACCESS_SECRET

# Google Gemini Settings
GEMINI_API_KEY=あなたのGEMINI_API_KEY


💻 Windowsでの実行方法

デスクトップ環境で簡単に動かす場合の手順です。

コマンドプロンプト(cmd) または PowerShell を開きます。

フォルダに移動して実行します。

python crypto_analyst.py


初回起動時に必要なライブラリ (google-generativeai, tweepy 等) が自動的にインストールされます。

黒い画面が開いている間、毎日 01:45, 07:45, 11:45, 17:45, 21:45 に自動投稿します。

🐧 Linux (Umbrel) での実行方法

Umbrelなどの常時稼働サーバーでバックグラウンド実行する場合の手順です。

1. 仮想環境の作成とライブラリインストール

Umbrel環境を汚さないよう、仮想環境(venv)を使用します。

# 仮想環境の作成
python3 -m venv venv

# 仮想環境の有効化
source venv/bin/activate

# ライブラリのインストール
pip install google-generativeai requests feedparser tweepy schedule python-dotenv


2. バックグラウンドでの起動

SSH接続を切っても動き続けるように nohup を使います。

# 実行 (ログは analyst_bot.log に保存されます)
nohup python3 crypto_analyst_linux.py > /dev/null 2>&1 &


UTC自動補正機能: サーバーが世界標準時(UTC)の場合、自動的に日本時間(JST)のスケジュール（01:45, 07:45, 11:45, 17:45, 21:45）に合わせて調整します。

3. 動作確認と停止

ログの確認:

tail -f analyst_bot.log


Botの停止:

pkill -f crypto_analyst_linux.py


📂 ファイル構成

crypto_analyst.py: Windows版 (文字化け対策・自動インストール機能付き)

crypto_analyst_linux.py: Linux版 (ログファイル出力・UTC時刻補正付き)

X-GoogleAPI.env: APIキー設定ファイル (※GitHubにはアップロードしません)

🕒 更新履歴 (Changelog)

v4.3: 投稿頻度を1日5回 (01:45, 07:45, 11:45, 17:45, 21:45) に変更。生存監視ログを削除。

v4.2: 分析の視点を8パターンに拡充（テクニカル、クジラ動向、セクター分析を追加）。

v4.1: 監視通貨を11銘柄に拡大 (BTC, ETH, XRP, SOL, BNB, DOGE, FET, UNI, IMX, GOLD, XMR)。

v3.x: マクロ経済ニュースの追加、Gemini 3.0系プレビュー版への対応、APIキーの外部ファイル化 (.env)。

v2.x: 日本語/英語ニュース対応、UTC時刻自動補正機能の実装。

⚠️ 免責事項

このBotによる投資助言や分析結果によって生じた損失について、開発者は一切の責任を負いません。

投資は自己責任で行ってください。