import ccxt
import pandas as pd
import time
import schedule
import smtplib
from email.mime.text import MIMEText
from keep_alive import keep_alive

# Email cấu hình
from_email = 'canmotac01@gmail.com'
to_email = 'hieutrading2025@gmail.com'
email_password = 'hmac clta hbjl yizr'

def send_email(subject, content):
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(from_email, email_password)
        server.send_message(msg)
        server.quit()
        print("✅ Email sent:", subject)
    except Exception as e:
        print("❌ Email error:", e)

def scan_binance_futures():
    print("🔍 Scanning volume...")
    binance = ccxt.binance({'options': {'defaultType': 'future'}})
    try:
        markets = binance.load_markets()
    except Exception as e:
        print("❌ Lỗi load markets:", e)
        return

    symbols = [s for s in markets if s.endswith('/USDT') and markets[s]['type'] == 'future']

    length = 20
    multiplier = 2
    min_volume = 100000
    limit = length + 1
    spike_coins = []

    for symbol in symbols:
        try:
            ohlcv = binance.fetch_ohlcv(symbol, timeframe='30m', limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            avg_vol = df['volume'][:-1].mean()
            last_vol = df['volume'].iloc[-1]
            print(f"🔎 {symbol}: Last Vol = {last_vol:.2f}, Avg Vol = {avg_vol:.2f}")
            if last_vol > avg_vol * multiplier and last_vol > min_volume:
                spike_coins.append((symbol, last_vol, avg_vol))
        except Exception as e:
            print(f"❌ Lỗi lấy dữ liệu {symbol}: {e}")
            continue

    if spike_coins:
        content = ""
        for coin in spike_coins:
            content += f"{coin[0]} | Vol: {coin[1]:.2f} | Avg: {coin[2]:.2f}\n"
        send_email("🔥 Volume Spike", content)
    else:
        print("⛔ No spikes found.")

# ⏰ Kiểm tra mỗi 30 phút
schedule.every(1).minutes.do(scan_binance_futures)

# 🌐 Giữ bot sống
keep_alive()

# 📧 Gửi email test khi khởi động
send_email("🔔 Bot Started", "Bot volume đang chạy và sẵn sàng kiểm tra volume.")

# ⏳ Vòng lặp chạy bot
while True:
    schedule.run_pending()
    time.sleep(1)
