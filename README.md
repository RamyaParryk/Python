<h1>AI Crypto Analyst Bot 📈🤖</h1>

仮想通貨の価格データと最新ニュースを収集し、Google Gemini AI (3.0 Pro/Flash Preview) が相場を分析して X (旧Twitter) に自動投稿するPython製ボットです。

Windows (デスクトップ) と Linux (Umbrelサーバー等) の両方に対応しています。

<h2>✨ 特徴</h2>

<ul>
<li><b>AIによる相場分析:</b> 単なるニュースの羅列ではなく、最新鋭の <b>Gemini 3.0 Pro</b> (または Flash) が「若い女性トレーダー」の人格で、その日の相場観を語ります。</li>
<li><b>マルチソース情報収集:</b> 国内外の主要メディア（CoinPost, CoinTelegraph, Bloomberg, Yahoo Financeなど）計12サイトから情報を収集。</li>
<li><b>価格連動:</b> CoinGeckoから BTC, ETH, XRP, SOL, BNB だけでなく、DOGE, FET, UNI, IMX, Gold(XAUT), XMR など計11銘柄の価格と変動率を取得し、分析に反映させます。</li>
<li><b>マンネリ防止:</b> 「マクロ経済重視」「アルトコイン注目」「リスク警戒」「テクニカル分析」など、毎回異なる視点（8パターン）で分析を行います。</li>
<li><b>ハッシュタグ自動化:</b> 記事の内容に合わせて適切なハッシュタグを自動選定します。</li>
</ul>

<h2>⚙️ 事前準備 (APIキーの取得)</h2>

このBotを動かすには、以下の2つのAPIキーが必要です。

<ol>
<li><b>X (Twitter) API Keys</b> (Free TierでOK)
<ul>
<li>取得先: <a href="https://developer.x.com/en/portal/dashboard">X Developer Portal</a></li>
<li>必要な権限: <b>Read and Write</b> (設定変更を忘れずに！)</li>
</ul>
</li>
<li><b>Google Gemini API Key</b> (無料枠でOK)
<ul>
<li>取得先: <a href="https://aistudio.google.com/app/apikey">Google AI Studio</a></li>
</ul>
</li>
</ol>

<h2>🚀 インストールと設定</h2>

<h3>1. リポジトリのクローン</h3>

<pre><code>git clone https://github.com/あなたのユーザー名/リポジトリ名.git
cd リポジトリ名</code></pre>

<h3>2. 設定ファイルの作成 (必須)</h3>

セキュリティのため、APIキーはコードに含まれていません。
フォルダ内に <code>X-GoogleAPI.env</code> という名前のファイルを作成し、以下の内容を記述してください。

<b>ファイル名:</b> <code>X-GoogleAPI.env</code>

<pre><code># X (Twitter) Settings
X_API_KEY=あなたのAPI_KEY
X_API_SECRET=あなたのAPI_SECRET
X_ACCESS_TOKEN=あなたのACCESS_TOKEN
X_ACCESS_SECRET=あなたのACCESS_SECRET

Google Gemini Settings

GEMINI_API_KEY=あなたのGEMINI_API_KEY</code></pre>

<hr>

<h2>💻 Windowsでの実行方法</h2>

デスクトップ環境で簡単に動かす場合の手順です。

コマンドプロンプト(cmd) または PowerShell を開きます。

フォルダに移動して実行します。

<pre><code>python crypto_analyst.py</code></pre>

<ul>
<li>初回起動時に必要なライブラリ (<code>google-generativeai</code>, <code>tweepy</code> 等) が自動的にインストールされます。</li>
<li>黒い画面が開いている間、毎日 <b>01:45, 07:45, 11:45, 17:45, 21:45</b> に自動投稿します。</li>
</ul>

<hr>

<h2>🐧 Linux (Umbrel) での実行方法</h2>

Umbrelなどの常時稼働サーバーでバックグラウンド実行する場合の手順です。

<h3>1. 仮想環境の作成とライブラリインストール</h3>

Umbrel環境を汚さないよう、仮想環境(venv)を使用します。

<pre><code># 仮想環境の作成
python3 -m venv venv

仮想環境の有効化

source venv/bin/activate

ライブラリのインストール

pip install google-generativeai requests feedparser tweepy schedule python-dotenv</code></pre>

<h3>2. バックグラウンドでの起動</h3>

SSH接続を切っても動き続けるように <code>nohup</code> を使います。

<pre><code># 実行 (ログは analyst_bot.log に保存されます)
nohup python3 crypto_analyst_linux.py > /dev/null 2>&1 &</code></pre>

<ul>
<li><b>UTC自動補正機能:</b> サーバーが世界標準時(UTC)の場合、自動的に日本時間(JST)のスケジュール（01:45, 07:45, 11:45, 17:45, 21:45）に合わせて調整します。</li>
</ul>

<h3>3. 動作確認と停止</h3>

<b>ログの確認:</b>

<pre><code>tail -f analyst_bot.log</code></pre>

<b>Botの停止:</b>

<pre><code>pkill -f crypto_analyst_linux.py</code></pre>

<h2>📂 ファイル構成</h2>

<ul>
<li><code>crypto_analyst.py</code>: <b>Windows版</b> (文字化け対策・自動インストール機能付き)</li>
<li><code>crypto_analyst_linux.py</code>: <b>Linux版</b> (ログファイル出力・UTC時刻補正付き)</li>
<li><code>X-GoogleAPI.env</code>: APIキー設定ファイル (※GitHubにはアップロードしません)</li>
</ul>

<h2>🕒 更新履歴 (Changelog)</h2>

<ul>
<li><b>v4.4</b>: 使用AIモデルを <b>Gemini 3.0 Pro/Flash Preview</b> に変更し、分析力と表現力を向上（2.0系を削除）。Windows版も同仕様に統一。</li>
<li><b>v4.3</b>: 投稿頻度を1日5回 (01:45, 07:45, 11:45, 17:45, 21:45) に変更。生存監視ログを削除。</li>
<li><b>v4.2</b>: 分析の視点を8パターンに拡充（テクニカル、クジラ動向、セクター分析を追加）。</li>
<li><b>v4.1</b>: 監視通貨を11銘柄に拡大 (BTC, ETH, XRP, SOL, BNB, DOGE, FET, UNI, IMX, GOLD, XMR)。</li>
<li><b>v3.x</b>: マクロ経済ニュースの追加、APIキーの外部ファイル化 (.env)。</li>
<li><b>v2.x</b>: 日本語/英語ニュース対応、UTC時刻自動補正機能の実装。</li>
</ul>

<h2>⚠️ 免責事項</h2>

このBotによる投資助言や分析結果によって生じた損失について、開発者は一切の責任を負いません。





投資は自己責任で行ってください。