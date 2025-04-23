import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is working!")

async def signal1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📈 Signal for 1-minute (placeholder)")

async def signal2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Signal for 5-minute (placeholder)")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if update and hasattr(update, "message"):
        await update.message.reply_text("⚠️ An error occurred. Please try again later.")

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("🚫 Bot TOKEN is not set. Add it in Render Environment Variables.")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal1", signal1))
    app.add_handler(CommandHandler("signal2", signal2))

    app.add_error_handler(error_handler)

    app.run_polling()
