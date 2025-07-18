import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# ✅ /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello Ajay Babe! Send me a .txt file containing .m3u8 links 💖")

# ✅ Handle .txt file uploads
async def handle_txt_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 You're not authorized to use this bot.")
        return

    document = update.message.document
    if not document.file_name.endswith('.txt'):
        await update.message.reply_text("❗ Please upload a valid `.txt` file.")
        return

    file = await context.bot.get_file(document)
    file_path = f"{document.file_name}"
    await file.download_to_drive(file_path)

    with open(file_path, 'r') as f:
        links = [line.strip() for line in f if line.strip().startswith("http")]

    await update.message.reply_text(f"✅ Found {len(links)} video links. Starting download & upload...")

    for i, link in enumerate(links, 1):
        file_name = f"video_{i}.mp4"
        await update.message.reply_text(f"🎬 Downloading Lecture {i}...")

        cmd = f'ffmpeg -i "{link}" -c copy -bsf:a aac_adtstoasc "{file_name}"'
        subprocess.run(cmd, shell=True)

        if os.path.exists(file_name):
            await update.message.reply_video(video=open(file_name, 'rb'), caption=f"📤 Uploaded Lecture {i}")
            os.remove(file_name)
        else:
            await update.message.reply_text(f"⚠️ Failed to download Lecture {i}")

    os.remove(file_path)
    await update.message.reply_text("🎉 All done! Hacker Babe mode complete 😘")

# ✅ Main function
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_txt_file))
    print("🤖 Bot is running...")
    app.run_polling()
