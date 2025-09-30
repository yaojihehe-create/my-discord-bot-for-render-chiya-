import discord
import os
import random
from flask import Flask
from threading import Thread
import time

# Flaskのアプリケーションインスタンスを作成（gunicornが実行するWebサーバー）
app = Flask(__name__) 

# グローバルフラグ：Botが起動を試みたかを示す（ワーカー間で完全な同期はしないが、セーフティネットとして使用）
# gunicornの各ワーカープロセスで独立して初期化されます
bot_start_attempted = False

# -----------------
# Discord Bot本体の起動関数
# -----------------
def run_discord_bot():
    global bot_start_attempted

    # 応答メッセージリスト
    RANDOM_RESPONSES = [
    "「こんなところで諦めては、武士の恥ですわ！この命に代えても！」",
    "「ふふふ。和の心……」",
    "「風情（ふぜい）があるでしょう？」",
    "「いらっしゃいませ。甘兎庵へようこそ」",
    "「お仕置き（おしおき）が必要みたいね」",
    "「リゼちゃん、また私に甘えに来たのね」",
    "「和の心を感じるわね」",
    "「せっかくだから、みんなの心の中に隠していることを聞きたいわ」",
    "「物理部の精神、すてきだわね」"
    ]

    TOKEN = os.getenv("DISCORD_TOKEN") 
    intents = discord.Intents.default()
    intents.message_content = True 
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print('---------------------------------')
        print(f'Botがログインしました: {client.user.name}')
        print('---------------------------------')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        # Botへのメンションでの応答
        if client.user.mentioned_in(message):
            response = random.choice(RANDOM_RESPONSES)
            await message.channel.send(f'{message.author.mention} {response}')
            return 
    
    if TOKEN:
        # Botの起動を試行する
        try:
            client.run(TOKEN)
        except Exception as e:
            # トークンエラーなど、起動失敗時のログ
            print(f"Discord Bot 起動失敗: {e}")
    else:
        print("エラー: Botトークンが設定されていません。")

# -----------------
# Webサーバーのエンドポイント (gunicornがアクセスする場所)
# -----------------
@app.route('/')
def home():
    global bot_start_attempted
    
    # 致命的な二重起動を防ぐセーフティネットの強化
    if not bot_start_attempted:
        print("Webアクセスを検知。Discord Botの起動を試みます...")
        # フラグを立てて、このワーカーでは再起動しないようにする
        bot_start_attempted = True
        
        # Botを別スレッドで起動
        Thread(target=run_discord_bot).start()
        
        # 初回起動時は応答が遅れるため、Initializingを返す
        return "Discord Bot is initializing... (Please check Discord in 10 seconds)"
    
    # Bot起動試行済みの場合は、Renderのヘルスチェックに応答
    return "Bot is alive!"

# ----------------------------------------------------
# gunicornは 'app' インスタンスをWebサーバーとして起動します。
# ----------------------------------------------------
