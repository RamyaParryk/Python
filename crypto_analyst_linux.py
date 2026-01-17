#!/usr/bin/env python3
import os
import time
import datetime
import sys
import subprocess
import traceback
import random
import warnings

# ==========================================
# 警告メッセージの抑制
# ==========================================
warnings.simplefilter('ignore')
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'

# ==========================================
# 設定: パス設定 & ログ機能
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "analyst_bot.log")
# 読み込む設定ファイル名を指定
ENV_FILE = os.path.join(BASE_DIR, "X-GoogleAPI.env")

def log(message):
    """ログをコンソールとファイルに出力"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{timestamp}] {message}"
    # コンソールにも即時出力
    print(msg, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
            # ★ここを追加: バッファに溜めずに強制的にディスクに書き込む
            f.flush()
            os.fsync(f.fileno())
    except:
        pass

# ==========================================
# 自動インストール機能
# ==========================================
def install_libraries():
    # python-dotenvを追加
    required_libs = ["google-generativeai", "requests", "feedparser", "tweepy", "schedule", "python-dotenv"]
    for lib in required_libs:
        try:
            # パッケージ名の揺らぎ吸収
            if lib == "google-generativeai":
                module_name = "google.generativeai"
            elif lib == "python-dotenv":
                module_name = "dotenv"
            else:
                module_name = lib
            __import__(module_name)
        except ImportError:
            log(f"Installing {lib}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            except Exception as e:
                log(f"Failed to install {lib}: {e}")

# ライブラリ読み込み
try:
    import requests
    import feedparser
    import tweepy
    import schedule
    import google.generativeai as genai
    from dotenv import load_dotenv
except ImportError:
    log("必要なライブラリが見つかりません。自動インストールを試みます...")
    install_libraries()
    import requests
    import feedparser
    import tweepy
    import schedule
    import google.generativeai as genai
    from dotenv import load_dotenv

# .envファイルの読み込み
if os.path.exists(ENV_FILE):
    load_dotenv(ENV_FILE)
    log(f"設定ファイル {os.path.basename(ENV_FILE)} を読み込みました。")
else:
    log(f"⚠️ 設定ファイル {os.path.basename(ENV_FILE)} が見つかりません。環境変数から設定を読み込みます。")

# ==========================================
# 設定エリア (環境変数から読み込み)
# ==========================================

# 1. X (Twitter) API Keys
X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")

# 2. Google Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# キーチェック
if not all([X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET, GEMINI_API_KEY]):
    log("!!!! 設定エラー !!!!")
    log("APIキーが正しく読み込めませんでした。")
    log(f"同じフォルダに {os.path.basename(ENV_FILE)} ファイルがあるか確認してください。")

# 3. ニュースソース (カテゴリ別に整理・拡充)
RSS_URLS = [
    # ===========================
    # 仮想通貨メディア (国内)
    # ===========================
    "https://coinpost.jp/feed",               # CoinPost (国内最大手)
    "https://jp.cointelegraph.com/rss",       # CoinTelegraph Japan
    "https://www.coindeskjapan.com/feed/",    # CoinDesk Japan
    "https://jinacoin.ne.jp/feed/",           # JinaCoin
    "https://www.neweconomy.jp/feed",         # あたらしい経済
    "https://bittimes.net/feed",              # BITTIMES
    "https://crypto-times.jp/feed/",          # Crypto Times

    # ===========================
    # 仮想通貨メディア (海外 - 一次情報)
    # ===========================
    "https://cointelegraph.com/rss",                   # CoinTelegraph (Global)
    "https://www.coindesk.com/arc/outboundfeeds/rss/", # CoinDesk (Global - 老舗)
    "https://decrypt.co/feed",                         # Decrypt (Web3/Tech)
    "https://theblockcrypto.com/rss",                  # The Block (リサーチ重視)
    "https://cryptoslate.com/feed/",                   # CryptoSlate

    # ===========================
    # マクロ経済・金融 (米国株・金利・FOMC等)
    # ===========================
    "https://jp.investing.com/rss/news_14.rss",        # Investing.com JP (経済全般)
    "https://jp.wsj.com/xml/rss/0,25612,3_0088,00.xml", # WSJ日本版 (国際・経済)
    "https://finance.yahoo.com/news/rssindex",         # Yahoo Finance US
    "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664", # CNBC
    "http://feeds.marketwatch.com/marketwatch/topstories/", # MarketWatch

    # ===========================
    # 日本経済・ビジネス
    # ===========================
    "https://www3.nhk.or.jp/rss/news/cat5.xml",      # NHKニュース (経済)
    "https://news.yahoo.co.jp/rss/categories/business.xml", # Yahooニュース (経済)
    "https://kabutan.jp/rss/news/nkn.xml"             # 株探 (株式市場)
]

# ★ ニュース除外キーワード
IGNORE_KEYWORDS = [
    "パペット", "フィギュア", "Happy Bag", "子育て", "芸能", "映画", 
    "グルメ", "プレゼント", "発売", "ランキング", "アニメ", "診断", "占い"
]

# ==========================================
# 関数群
# ==========================================

def get_crypto_prices():
    """CoinGeckoから主要通貨の価格と変動率を取得"""
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum,ripple,solana,binancecoin,dogecoin,fetch-ai,uniswap,immutable-x,tether-gold,monero",
        "vs_currencies": "jpy",
        "include_24hr_change": "true"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        text = "【現在価格と24時間変動】\n"
        
        def add_coin_data(coin_id, symbol):
            if coin_id in data:
                d = data[coin_id]
                return f"{symbol}: {d['jpy']:,}円 ({d['jpy_24h_change']:.1f}%)\n"
            return ""

        text += add_coin_data("bitcoin", "BTC")
        text += add_coin_data("ethereum", "ETH")
        text += add_coin_data("ripple", "XRP")
        text += add_coin_data("solana", "SOL")
        text += add_coin_data("binancecoin", "BNB")
        text += add_coin_data("dogecoin", "DOGE")
        text += add_coin_data("fetch-ai", "FET")
        text += add_coin_data("uniswap", "UNI")
        text += add_coin_data("immutable-x", "IMX")
        text += add_coin_data("tether-gold", "Gold(XAUT)")
        text += add_coin_data("monero", "XMR")
        
        return text
    except Exception as e:
        log(f"価格取得エラー: {e}")
        return "価格データの取得に失敗しました。"

def get_latest_news_headlines():
    """RSSから直近のニュースタイトルを取得 (フィルタリング付き)"""
    headlines = []
    shuffled_urls = RSS_URLS.copy()
    random.shuffle(shuffled_urls)

    # 取得数を少し増やす
    target_count = 35

    for url in shuffled_urls:
        if len(headlines) >= target_count:
            break
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if response.status_code == 200:
                feed = feedparser.parse(response.text)
                count = 0
                for entry in feed.entries:
                    title = entry.title
                    # 除外キーワードが含まれていたらスキップ
                    if any(keyword in title for keyword in IGNORE_KEYWORDS):
                        continue
                    
                    headlines.append(f"- {title}")
                    count += 1
                    if count >= 2: break # 各サイト最大2件
        except Exception as e:
            pass
    
    if not headlines:
        return "ニュースの取得に失敗しました。"
    return "【直近のニュース】\n" + "\n".join(headlines)

def generate_analysis_tweet(prices, news):
    """Gemini APIを使って分析ツイートを生成"""
    # キーが読み込めていない場合は中止
    if not GEMINI_API_KEY:
        log("❌ エラー: GEMINI_API_KEY が設定されていません。")
        return None

    genai.configure(api_key=GEMINI_API_KEY)
    
    # モデル優先順: ユーザー発見のPreview版を最優先に追加
    # 3.0系がダメなら2.0にフォールバック
    models_to_try = ['gemini-3-pro-preview', 'gemini-3-flash-preview', 'gemini-2.0-flash']

    # 分析の切り口をランダム化
    analysis_angles = [
        "マクロ経済（FOMC、雇用統計、株価）と仮想通貨の連動性を鋭く分析",
        "アルトコインの個別材料やオンチェーンデータの動きに注目",
        "投資家の恐怖・強欲指数（センチメント）や市場の雰囲気を読み解く",
        "ダウンサイドリスク（下落の可能性）を警戒した慎重なシナリオ分析",
        "長期的なファンダメンタルズに基づいたポジティブな展望",
        "移動平均線やサポートラインなど、テクニカル分析に基づいたチャート視点",
        "ETFフローやクジラ（大口投資家）の資金動向に注目した分析",
        "今盛り上がっている特定のセクター（AI、ミーム等）やテーマ株にフォーカスした分析"
    ]
    current_angle = random.choice(analysis_angles)
    log(f"今回の分析テーマ: {current_angle}")

    for model_name in models_to_try:
        try:
            # log(f"AIモデル ({model_name}) で生成を試みます...") # ログ軽減のためコメントアウト
            model = genai.GenerativeModel(model_name)

            prompt = f"""
あなたは経験豊富で知的な若い女性トレーダーです。
以下の情報からX（Twitter）投稿を作成してください。

{prices}
{news}

【重要テーマ】
👉 {current_angle}

【条件】
- 120文字以内で簡潔に（ハッシュタグ込み140文字未満）。
- 一人称は「私」、語尾は「〜わ」「〜わね」「〜よ」「〜かしら」。
- 絵文字を文末だけでなく、文中の区切りなどにも適度に入れて（計3〜4個程度）、親しみやすさを出してください。
- **最重要:** ニュースが多岐にわたる場合、**最も市場への影響力が大きいトピックを1つだけ選び出し**、それと価格動向を絡めて分析してください。情報を詰め込みすぎないこと。
- 単調な表現を避け、金融用語（FOMC、利下げ、CPI、ETF等）や相場用語を自然に交えて、語彙の豊かさを見せてください。
- 自身のトレードポジション（「買う」「売る」）は宣言せず、**閲覧者にとって有益な気づき（リスク要因や注目点）**を提供するスタイルで。
- 関連するハッシュタグを最後に選んで付ける。
- 挨拶や前置きは不要。
"""
            response = model.generate_content(
                prompt, 
                generation_config={"temperature": 0.85}
            )
            text = response.text.strip()
            
            if len(text) > 140:
                 log("⚠️ 文字数調整を行います")
                 text = text[:137] + "..."
            
            log(f"✨ 使用モデル: {model_name}")
            return text
            
        except Exception as e:
            # log(f"⚠️ モデル {model_name} でエラー発生（スキップします）: {e}")
            time.sleep(2)
            continue

    log("❌ 全てのAIモデルで生成に失敗しました。")
    return None

def job():
    log("分析を開始します...")
    
    # APIキーの存在チェック
    if not all([X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET]):
        log(f"❌ エラー: X APIキーが設定されていません。{ENV_FILE} を確認してください。")
        return

    prices = get_crypto_prices()
    news = get_latest_news_headlines()
    
    # tweet_text に統一
    tweet_text = generate_analysis_tweet(prices, news)
    
    if tweet_text:
        log("--- 生成されたツイート ---")
        log(tweet_text)
        
        try:
            client = tweepy.Client(
                consumer_key=X_API_KEY,
                consumer_secret=X_API_SECRET,
                access_token=X_ACCESS_TOKEN,
                access_token_secret=X_ACCESS_SECRET
            )
            client.create_tweet(text=tweet_text)
            log("✅ 投稿成功！")
        except Exception as e:
            log(f"❌ 投稿エラー: {e}")
            if hasattr(e, 'response') and e.response is not None:
                log(f"詳細情報: {e.response.text}")
    else:
        log("ツイート生成に失敗したためスキップします。")

# ==========================================
# メイン処理 (タイムゾーン自動補正・スケジュール確認付き)
# ==========================================
def main():
    log("=== AI Crypto Analyst Bot (Linux Mode v4.6 Flush-Log) Started ===")
    
    # サーバーの現在時刻を確認
    now = datetime.datetime.now()
    utcnow = datetime.datetime.utcnow()
    # 差が1分未満ならサーバーはUTC設定とみなす
    is_utc = abs((now - utcnow).total_seconds()) < 60
    
    log(f"サーバー現在時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")

    if is_utc:
        log("🕒 サーバーはUTC(世界標準時)設定です。日本時間(JST)に合わせてスケジュールを自動調整します。")
        # UTCとJSTの時差は-9時間
        schedule.every().day.at("16:45").do(job) # JST 01:45
        schedule.every().day.at("22:45").do(job) # JST 07:45
        schedule.every().day.at("02:45").do(job) # JST 11:45
        schedule.every().day.at("08:45").do(job) # JST 17:45
        schedule.every().day.at("12:45").do(job) # JST 21:45
        log("設定時刻(UTC): 16:45, 22:45, 02:45, 08:45, 12:45")
    else:
        log("🕒 サーバーはJST(日本時間)設定と判定しました。そのままの時刻で設定します。")
        schedule.every().day.at("01:45").do(job)
        schedule.every().day.at("07:45").do(job)
        schedule.every().day.at("11:45").do(job)
        schedule.every().day.at("17:45").do(job)
        schedule.every().day.at("21:45").do(job)
    
    # 生存確認ログ(heartbeat)は削除

    # 次回実行予定を表示
    log("--- 次回実行スケジュール ---")
    for j in schedule.get_jobs():
        log(f"次回実行: {j.next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    log("----------------------------")

    log("スケジュール待機中...")
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except KeyboardInterrupt:
            log("Bot停止コマンドを受信しました。終了します。")
            break
        except Exception as e:
            log(f"メインループエラー: {e}")
            log(traceback.format_exc())
            time.sleep(60)

if __name__ == "__main__":
    main()