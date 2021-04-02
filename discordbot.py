'''
import youtube_dl
import asyncio

#音声についての関数
youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}
ffmpeg_options = {
    'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):

       
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
        
#音楽を再生/停止する
    if message.content.startswith("start"):
        await message.author.voice.channel.connect()#vc接続
        message.content=message.content.replace("start","")
        async with message.channel.typing():
            player = await YTDLSource.from_url(message.content, loop=asyncio.get_event_loop())#多分再生用の素材を作ってるとこ
            message.author.guild.voice_client.play(player, after=lambda e: print(
                'Player error: %s' % e) if e else None)#再生してるとこ
            await message.channel.send('Now playing: {}'.format(player.title))  #再生中のタイトルをsend
    if message.content.startswith("stop"):
        await message.author.guild.voice_client.disconnect()  #VC切断
'''
import discord
from discord.ext import commands
import random
import pdb
import os
import pickle


TOKEN=os.environ['DISCORD_BOT_TOKEN']

#ここにidが入る 環境変数で設定したい
#ボット専用のチャンネルのid
CHANNEL_ID=os.environ['CHANNEL_ID']

#独り言チャンネルのカテゴリid
CATEGORY_ID=os.environ['CATEGORY_ID']

#dloppのサーバーid
SERVER_ID=os.environ['SERVER_ID']

#botの作成
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='.', intents=intents)

#チャンネルリスト
clist=[]

#絡んでほしくない人のチャンネルリスト
noclist=[]
noxlist=[]

#絡む言葉のリスト
tlist=["お元気ですか?","進捗どうですか？","こんにちは","開発してみたいものはありますか？"]

#チャンネルのリストを取り出す関数
def get_data(message):
    command = '/text_channels'
    data_table = {
        '/members': message.guild.members, # メンバーのリスト
        '/roles': message.guild.roles, # 役職のリスト
        '/text_channels': message.guild.text_channels, # テキストチャンネルのリスト
        '/voice_channels': message.guild.voice_channels, # ボイスチャンネルのリスト
        '/category_channels': message.guild.categories, # カテゴリチャンネルのリスト
    }
    return data_table.get(command, '無効なコマンドです')

#bot起動時の処理
@client.event
async def on_ready():
    print("bot is ready ")

#入室したときのイベント
@client.event
async def on_member_join(member):
    #チャンネル作成処理
    guild=client.get_guild(SERVER_ID)
    category_id=CATEGORY_ID
    category =guild.get_channel(category_id)
    name=str(member)
    new_channel = await category.create_text_channel(name=name)
    text = f'{new_channel.mention} を作成しました'
    channel = client.get_channel(CHANNEL_ID)
    await channel.send(text)
    await new_channel.send("これからよろしくお願いします!\nまずはScrapbox https://scrapbox.io/dlopp/member で自己紹介ページを作ってみましょう")

#コマンド入力によるイベント
@client.event
async def on_message(message):
    l=message.content
    if message.author.bot:
        return
    else:
        if l=='/help':
            #ヘルプ機能
            embed=discord.Embed(title="ヘルプ", description="botの使い方", color=0x59adee)
            embed.add_field(name="コマンド一覧", value="メッセージとして打ち込んでください", inline=False)
            embed.add_field(name="/set", value="botがメンバーリストを取得します", inline=True)
            embed.add_field(name="/talk", value="ある独り言チャンネルに話しかけます", inline=True)
            embed.add_field(name="/cancel", value="そのチャンネルに話しかけなくなります", inline=True)
            embed.add_field(name="start'url'", value="urlにある動画を音楽にして流します", inline=True)
            embed.add_field(name="stop",value="音楽を停止します",inline=True)
            embed.add_field(name="/help", value="ヘルプを表示します", inline=True)
            embed.set_footer(text="動かなければScrapboxに連絡ください")
            await message.channel.send(embed=embed)
        elif l=='/talk':
            guild = message.guild
            user_count = sum(1 for member in guild.members if not member.bot)
            if len(clist)==0:
                await message.channel.send("先に/setコマンドを入力してください")
            else:
                if os.path.exists("list.binaryfile"):
                    with open('list.binaryfile','rb') as lists:
                        noxlist=pickle.load(lists)
                    if user_count==len(noxlist):
                        await message.channel.send("話しかける相手がいません...")
                    while True:
                        judge=False
                        maxc=len(clist)-1
                        n=random.randint(0,maxc)
                        for i in range(len(noxlist)):
                            if noxlist[i]==clist[n]:
                                judge=True
                            
                        if judge==False:
                            break
                else:
                    maxc=len(clist)-1
                    n=random.randint(0,maxc)
                channel = client.get_channel(clist[n])
                maxt=len(tlist)-1
                s=random.randint(0,maxt)
                text=tlist[s]
                await channel.send(text)
        elif l=='/set':
            clist.clear()
            data=get_data(message)
            #print(data)
            for i in range(len(data)):
                if data[i].category_id==CATEGORY_ID:
                    c_id=data[i].id
                    clist.append(c_id)
                    
        elif l=='/cancel':
            global noclist
            no_c_id=message.channel.id
            if os.path.exists("list.binaryfile"):
                with open('list.binaryfile','rb') as lists:
                    noclist=pickle.load(lists)
                    noclist.append(no_c_id)
            else:
                noclist.append(no_c_id)
            with open('list.binaryfile','wb') as lists:
                pickle.dump(noclist,lists)
            await message.channel.send("ありがとうございました。")
#botの起動
client.run(TOKEN)