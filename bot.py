import yfinance as yf
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import ta
import pandas as pd


TOKEN = 8067640949

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply("👋 ברוך הבא לבוט המניות!
שלח לי סימבול של מניה (למשל: NVDA, TSLA) ואני אתן לך מידע עליה!")

# פונקציה לחישוב אינדיקטורים טכניים
async def analyze_stock(stock_symbol):
    df = yf.download(stock_symbol, period="1mo", interval="1d")
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["EMA150"] = df["Close"].ewm(span=150, adjust=False).mean()
    df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()
    df["Volume_MA10"] = df["Volume"].rolling(window=10).mean()
    
    latest_price = df["Close"].iloc[-1]
    latest_ema50 = df["EMA50"].iloc[-1]
    latest_ema150 = df["EMA150"].iloc[-1]
    latest_ema200 = df["EMA200"].iloc[-1]
    latest_rsi = df["RSI"].iloc[-1]
    latest_volume = df["Volume"].iloc[-1]
    latest_volume_ma10 = df["Volume_MA10"].iloc[-1]
    price_change = (latest_price - df["Close"].iloc[-2]) / df["Close"].iloc[-2] * 100
    
    recommendation = "🔎 ניתוח טכני:\n"
    threshold = 1.5  # כמה אחוזים נחשבים קרובים ל-EMA
    
    if latest_price > latest_ema200:
        recommendation += "✅ המניה מעל ה-200EMA → מומלץ לשקול לונג\n"
    else:
        recommendation += "❌ המניה מתחת ל-200EMA → עדיף להמתין\n"
    
    if latest_price > latest_ema150:
        recommendation += "✅ המניה מעל ה-150EMA → סימן חיובי\n"
    else:
        recommendation += "❌ המניה מתחת ל-150EMA → סימן שלילי\n"
    
    if abs(latest_price - latest_ema200) / latest_ema200 * 100 < threshold:
        recommendation += "🚀 המחיר קרוב מאוד ל-200EMA → שים לב לפריצה פוטנציאלית!\n"
    if abs(latest_price - latest_ema150) / latest_ema150 * 100 < threshold:
        recommendation += "🔥 המחיר מתקרב ל-150EMA → מעקב נדרש!\n"
    
    if latest_rsi < 30:
        recommendation += "📉 RSI נמוך → המניה בקנייה חזקה (אולי oversold)\n"
    elif latest_rsi > 70:
        recommendation += "⚠️ RSI גבוה → המניה עשויה להיות במכירת יתר (overbought)\n"
    else:
        recommendation += "✅ RSI בטווח בריא → אין קיצוניות בשוק\n"
    
    if latest_volume > latest_volume_ma10 * 1.5:
        recommendation += "📊 נפח מסחר גבוה → פריצה אפשרית!\n"
    
    if price_change > 3:
        recommendation += "⚡ המניה עלתה ביותר מ-3% ביום האחרון → מומנטום חיובי!\n"
    
    return f"📊 {stock_symbol} מחיר נוכחי: {latest_price:.2f}$\n{recommendation}"

@dp.message_handler()
async def get_stock_analysis(message: types.Message):
    stock_symbol = message.text.upper()
    try:
        analysis = await analyze_stock(stock_symbol)
        await message.reply(analysis)
    except:
        await message.reply("❌ לא הצלחתי למצוא מידע, נסה שוב!")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
