import logging
import yfinance as yf
import pandas as pd
import numpy as np
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio

TOKEN = "7752254695:AAFdkqZG4m6a6V-qBQ4fIWXy622nbsmw1Rc"  # replace this with your real token

pairs = [
    "AUDCHF=X", "AUDJPY=X", "AUDUSD=X", "AUDCAD=X",
    "CADCHF=X", "CADJPY=X", "CHFJPY=X",
    "EURAUD=X", "EURCAD=X", "EURCHF=X", "EURJPY=X", "EURUSD=X",
    "USDCAD=X", "USDCHF=X"
]

pair_nicknames = {
    "AUDCHF=X": "AUD/CHF", "AUDJPY=X": "AUD/JPY", "AUDUSD=X": "AUD/USD", "AUDCAD=X": "AUD/CAD",
    "CADCHF=X": "CAD/CHF", "CADJPY=X": "CAD/JPY", "CHFJPY=X": "CHF/JPY",
    "EURAUD=X": "EUR/AUD", "EURCAD=X": "EUR/CAD", "EURCHF=X": "EUR/CHF",
    "EURJPY=X": "EUR/JPY", "EURUSD=X": "EUR/USD",
    "USDCAD=X": "USD/CAD", "USDCHF=X": "USD/CHF"
}

logging.basicConfig(level=logging.INFO)

def calculate_indicators(df):
    df['RSI'] = df['Close'].diff().apply(lambda x: max(x, 0)).rolling(14).mean() / df['Close'].diff().abs().rolling(14).mean() * 100
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['Volatility'] = df['Close'].rolling(window=20).std()
    return df

def detect_snr(df):
    levels = []
    for i in range(2, len(df) - 2):
        if df['Low'][i] < df['Low'][i-1] and df['Low'][i] < df['Low'][i+1]:
            levels.append((i, df['Low'][i]))
        if df['High'][i] > df['High'][i-1] and df['High'][i] > df['High'][i+1]:
            levels.append((i, df['High'][i]))
    return levels[-5:]  # last 5 zones

def analyze(pair, timeframe):
    interval = "1m" if timeframe == "1" else "5m"
    df = yf.download(tickers=pair, period="1d", interval=interval)
    if df.empty:
        return "No data"
    df = calculate_indicators(df)
    levels = detect_snr(df)
    msg = f"RSI: {df['RSI'].iloc[-1]:.2f}\nMA20: {df['MA20'].iloc[-1]:.4f}\nMA50: {df['MA50'].iloc[-1]:.4f}\nVolatility: {df['Volatility'].iloc[-1]:.4f}\n"
    msg += "Support/Resistance:\n" + "\n".join([f"{round(l[1], 4)}" for l in levels])
    return msg

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send /signal 1 (for 1m) or /signal 2 (for 5m)")

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tf = context.args[0]
        pair = np.random.choice(pairs)
        nickname = pair_nicknames.get(pair, pair)
        result = analyze(pair, tf)
        await update.message.reply_text(f"{nickname}:\n{result}")
    except:
        await update.message.reply_text("Usage: /signal 1 or /signal 2")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))
    app.run_polling()
