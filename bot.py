import os,asyncio,threading
from flask import Flask
from PIL import Image,ExifTags
from telegram import InlineKeyboardButton,InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import Application,CommandHandler,MessageHandler,CallbackQueryHandler,ContextTypes,filters

TOKEN=os.getenv("BOT_TOKEN")
PORT=int(os.getenv("PORT","8080"))
FORCE_CHANNEL="@bytesly"
FORCE_URL="https://t.me/bytesly"
BACKUP_URL="https://t.me/+Mi0qvOEKsPViYTA1"

if not TOKEN:raise RuntimeError("BOT_TOKEN environment variable is missing.")

app=Flask(__name__)
processing=asyncio.Semaphore(5)

@app.get("/")
def home():return "Metadata Extractor Bot is running.",200

@app.get("/health")
def health():return "OK",200

def fraction(v):
    try:return float(v)
    except:
        try:return v.numerator/v.denominator
        except:return None

def gps_decimal(c,r):
    try:
        v=[fraction(x) for x in c]
        if any(x is None for x in v):return None
        d=v[0]+v[1]/60+v[2]/3600
        return -d if r in("S","W") else d
    except:return None

def extract(path):
    with Image.open(path) as im:
        ex=im.getexif()
        d={"format":im.format or"Unknown","width":im.width,"height":im.height,"mode":im.mode,"exif":[],"gps":None}
        if not ex:return d
        for i,v in ex.items():
            t=ExifTags.TAGS.get(i,str(i))
            if t=="GPSInfo":continue
            v=str(v)
            if len(v)>500:v=v[:500]+"..."
            d["exif"].append((t,v))
        try:
            g=ex.get_ifd(ExifTags.IFD.GPSInfo)
            la,lr,lo,orr=g.get(2),g.get(1),g.get(4),g.get(3)
            if la and lo and lr and orr:
                la,lo=gps_decimal(la,lr),gps_decimal(lo,orr)
                if la is not None and lo is not None:d["gps"]=(la,lo)
        except:pass
        return d

def escape(s):
    s=str(s)
    for c in r"\_*[]()~`>#+-=|{}.!":s=s.replace(c,"\\"+c)
    return s

def format_data(d):
    x=[
        "FORMAT: "+escape(d["format"]),
        f"DIMENSIONS: {d['width']} x {d['height']}",
        "MODE: "+escape(d["mode"])
    ]
    if d["exif"]:
        x+=["","EXIF DATA"]
        for t,v in d["exif"]:x.append(f"{escape(t)}: {escape(v)}")
    else:x+=["","NO EXIF METADATA FOUND"]
    if d["gps"]:
        la,lo=d["gps"]
        x+=["","GPS LOCATION",f"Latitude: {la:.6f}",f"Longitude: {lo:.6f}",f"Google Maps: https://maps.google.com/?q={la},{lo}"]
    return"\n".join(x)

def code(text):
    return "```\n"+text.replace("\\","\\\\").replace("`","\\`")+"\n```"

async def joined(uid,ctx):
    try:
        m=await ctx.bot.get_chat_member(FORCE_CHANNEL,uid)
        return m.status in("member","administrator","creator")
    except:return False

def join_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 Channel",url=FORCE_URL),
            InlineKeyboardButton("📢 Backup",url=BACKUP_URL)
        ],
        [
            InlineKeyboardButton("🔄 Check Membership",callback_data="check_join")
        ]
    ])

async def force(update,ctx):
    text=f"""
*To continue, join these 2 channels*

> 📢 *Channel* — @bytesly
> 📢 *Backup* — Please join

Join both channels and then tap *🔄 Check Membership* below\\.
"""
    await update.message.reply_text(text,parse_mode="MarkdownV2",reply_markup=join_keyboard())

async def start(update,ctx):
    if not await joined(update.effective_user.id,ctx):
        return await force(update,ctx)

    text=f"""
*👋 Welcome to Metadata Extractor\\!*

> 🔍 Send me an image and I'll extract its available metadata and EXIF information\\.

*📤 Send an image to get started\\.*

> 💡 For maximum metadata preservation, send the original image as a document/file\\.
"""
    kb=InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👨‍💻 Developer",url="https://t.me/outwiles")
        ]
    ])
    await update.message.reply_text(text,parse_mode="MarkdownV2",reply_markup=kb)

async def callback(update,ctx):
    q=update.callback_query
    await q.answer()

    if await joined(q.from_user.id,ctx):
        text=f"""
*✅ Membership verified\\!*

> 🎉 You're all set\\.

*📤 Send me an image to extract its metadata\\.*
"""
        kb=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👨‍💻 Developer",url="https://t.me/outwiles"),
                InlineKeyboardButton("📧 Mail",url="mailto:outwiles@proton.me")
            ]
        ])
        await q.edit_message_text(text,parse_mode="MarkdownV2",reply_markup=kb)
    else:
        text=f"""
*🔒 Join Required*

> ❌ Please join both channels to continue\\.

After joining, tap *🔄 Check Membership* again\\.
"""
        await q.edit_message_text(text,parse_mode="MarkdownV2",reply_markup=join_keyboard())

async def process(update,ctx,fid,path):
    async with processing:
        try:
            await update.message.chat.send_action(ChatAction.TYPING)
            f=await ctx.bot.get_file(fid)
            await f.download_to_drive(path)
            d=await asyncio.to_thread(extract,path)
            text=code(format_data(d))
            if len(text)>4000:text=text[:3990]+"```"
            await update.message.reply_text(text,parse_mode="MarkdownV2",disable_web_page_preview=True)
        except Exception as e:
            text=f"""
*❌ Unable to extract metadata\\.*

> `{escape(str(e)[:1000])}`
"""
            await update.message.reply_text(text,parse_mode="MarkdownV2")
        finally:
            try:os.remove(path)
            except:pass

async def image(update,ctx):
    if not await joined(update.effective_user.id,ctx):
        return await force(update,ctx)

    m=update.message

    if m.photo:
        f=m.photo[-1].file_id
        p=f"/tmp/{f}.jpg"
    elif m.document and(m.document.mime_type or"").startswith("image/"):
        f=m.document.file_id
        p=f"/tmp/{f}"
    else:return

    await process(update,ctx,f,p)

def flask():
    app.run(host="0.0.0.0",port=PORT,threaded=True,use_reloader=False)

async def main():
    a=Application.builder().token(TOKEN).concurrent_updates(True).build()
    private=filters.ChatType.PRIVATE
    a.add_handler(CommandHandler("start",start,filters=private))
    a.add_handler(CallbackQueryHandler(callback,pattern="^check_join$"))
    a.add_handler(MessageHandler(private&(filters.PHOTO|filters.Document.IMAGE),image))
    await a.initialize()
    await a.start()
    await a.updater.start_polling(drop_pending_updates=True)
    try:await asyncio.Event().wait()
    finally:
        await a.updater.stop()
        await a.stop()
        await a.shutdown()

if __name__=="__main__":
    threading.Thread(target=flask,daemon=True).start()
    asyncio.run(main())
