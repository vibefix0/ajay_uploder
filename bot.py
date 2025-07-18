import os
import subprocess
from telegram import Update, Document
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.ext import Document  # ✅ Required for detecting .txt files

# 🔐 Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# ✅ /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello Ajay Babe! Send me a .txt file containing .m3u8 links, and I'll upload the videos for you 🎥.")

# ✅ Handle .txt file uploads
async def handle_txt_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 You're not authorized to use this bot.")
        return

    document: Document = update.message.document
    if document.mime_type != DocumentMimeType.TEXT_PLAIN:
        await update.message.reply_text("❗ Please send a valid .txt file.")
        return

    file = await context.bot.get_file(document)
    file_path = f"{document.file_name}"
    await file.download_to_drive(file_path)

    with open(file_path, 'r') as f:
        links = [line.strip() for line in f if line.strip().startswith("http")]

    await update.message.reply_text(f"✅ Found {len(links)} video links. Starting download and upload...")

    for i, link in enumerate(links, 1):
        file_name = f"video_{i}.mp4"
        await update.message.reply_text(f"🎬 Downloading Lecture {i}...")

        # ffmpeg command
        cmd = f'ffmpeg -i "{link}" -c copy -bsf:a aac_adtstoasc "{file_name}"'
        process = subprocess.run(cmd, shell=True)

        if os.path.exists(file_name):
            await update.message.reply_video(video=open(file_name, 'rb'), caption=f"📤 Uploaded Lecture {i}")
            os.remove(file_name)
        else:
            await update.message.reply_text(f"⚠️ Failed to download Lecture {i}")

    os.remove(file_path)
    await update.message.reply_text("🎉 All videos processed and uploaded successfully!")

# ✅ Run the bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.MimeType(DocumentMimeType.TEXT_PLAIN), handle_txt_file))
    print("🤖 Bot is running...")
    app.run_polling()
