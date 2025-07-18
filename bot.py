import os
import subprocess
from telegram import Update, Document
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Send me a `.txt` file containing .m3u8 links.")

async def handle_txt_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 You are not authorized to use this bot.")
        return

    document: Document = update.message.document
    if not document.file_name.endswith('.txt'):
        await update.message.reply_text("❗ Please send a valid .txt file.")
        return

    file = await context.bot.get_file(document)
    file_path = f"{document.file_name}"
    await file.download_to_drive(file_path)

    with open(file_path, 'r') as f:
        links = [line.strip() for line in f if line.strip().startswith("http")]

    await update.message.reply_text(f"✅ Found {len(links)} links. Starting download...")

    for i, link in enumerate(links, 1):
        file_name = f"video_{i}.mp4"
        await update.message.reply_text(f"⬇️ Downloading lecture {i}...")

        # ffmpeg command
        cmd = f'ffmpeg -i "{link}" -c copy -bsf:a aac_adtstoasc "{file_name}"'
        process = subprocess.run(cmd, shell=True)

        if os.path.exists(file_name):
            await update.message.reply_video(video=open(file_name, 'rb'), caption=f"📤 Lecture {i}")
            os.remove(file_name)
        else:
            await update.message.reply_text(f"⚠️ Failed to download lecture {i}")

    os.remove(file_path)
    await update.message.reply_text("✅ All done!")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.FILE_EXTENSION("txt"), handle_txt_file))
    print("🤖 Bot running...")
    app.run_polling()
