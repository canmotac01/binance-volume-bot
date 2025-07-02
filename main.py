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
        print("✅ Email sent")
    except Exception as e:
        print("❌ Email error:", e)

def scan_binance_futures():
    print("🔍 Scanning volume...")
    binance = ccxt.binance({'options': {'defaultType': 'future'}})
    markets = binance.load_markets()
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
            if last_vol > avg_vol * multiplier and last_vol > min_volume:
                spike_coins.append((symbol, last_vol, avg_vol))
        except:
            continue

    if spike_coins:
        content = ""
        for coin in spike_coins:
            content += f"{coin[0]} | Vol: {coin[1]:.2f} | Avg: {coin[2]:.2f}\n"
        send_email("🔥 Volume Spike", content)
    else:
        print("⛔ No spikes found.")

# Run every 30 minutes
schedule.every(15).minutes.do(scan_binance_futures)

keep_alive()

while True:
    schedule.run_pending()
    time.sleep(1)
