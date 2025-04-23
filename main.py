import logging
import yfinance as yf
import pandas as pd
import numpy as np
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio
import os

# Use Render environment variable
TOKEN = os.getenv("TOKEN")

# Forex pairs list (no OTC)
pairs = [
    "AUDCHF=X", "AUDJPY=X", "AUDUSD=X", "AUDCAD=X",
    "CADCHF=X", "CADJPY=X", "CHFJPY=X",
    "EURAUD=X", "EURCAD=X", "EURCHF=X", "EURJPY=X", "EURUSD=X",
    "USDCAD=X", "USDCHF=X"
]

# Nicknames for display
pair_nicknames = {
    "AUDCHF=X": "AUD/CHF", "AUDJPY=X": "AUD/JPY", "AUDUSD=X": "AUD/USD", "AUDCAD=X": "AUD/CAD",
    "CADCHF=X": "CAD/CHF", "CADJPY=X": "CAD/JPY", "CHFJPY=X": "CHF/JPY",
    "EURAUD=X": "EUR/AUD", "EURCAD=X": "EUR/CAD", "EURCHF=X": "EUR/CHF",
    "EURJPY=X": "EUR/JPY", "EURUSD=X": "EUR/USD",
    "USDCAD=X": "USD/CAD", "USDCHF=X": "USD/CHF"
}

logging.basicConfig(level=logging.INFO)

# Indicators
def calculate_indicators(df):
    df['RSI'] = df['Close'].diff().apply(lambda x: max(x, 0)).rolling(14).mean() / df['Close'].diff().abs().rolling(14).mean() * 100
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['Volatility'] = df['Close'].rolling(window=20).std()
    return df

# Support and resistance
def detect_snr(df):
    levels = []
    for i in range(2, len(df) - 2):
        if df['Low'][i] < df['Low'][i-1] and df['Low'][i] < df['Low'][i+1]:
            levels.append((i, df['Low'][i]))
        if df['High'][i] > df['High'][i-1] and df['High'][i] > df['High'][i+1]:
            levels.append((i, df['High'][i]))
    return levels[-5:]

# Analysis function
def analyze(pair, interval):
    df = yf.download(tickers=pair, period="1d", interval=interval)
    if df.empty:
        return "No data available."
    df = calculate_indicators(df)
    levels = detect_snr(df)
    msg = f"RSI: {df['RSI'].iloc[-1]:.2f}\nMA20: {df['MA20'].iloc[-1]:.4f}\nMA50: {df['MA50'].iloc[-1]:.4f}\nVolatility: {df['Volatility'].iloc[-1]:.4f}\n"
    msg += "Support/Resistance:\n" + "\n".join([f"{round(l[1], 4)}" for l in levels])
    return msg

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use /signal1 for 1-minute or /signal2 for 5-minute signals.")

# /signal1
async def signal1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pair = np.random.choice(pairs)
    nickname = pair_nicknames.get(pair, pair)
    result = analyze(pair, "1m")
    await update.message.reply_text(f"{nickname}:\n{result}")

# /signal2
async def signal2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pair = np.random.choice(pairs)
    nickname = pair_nicknames.get(pair, pair)
    result = analyze(pair, "5m")
    await update.message.reply_text(f"{nickname}:\n{result}")

# Run bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal1", signal1))
    app.add_handler(CommandHandler("signal2", signal2))
    app.run_polling()
