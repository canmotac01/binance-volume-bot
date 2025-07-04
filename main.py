import requests
import pandas as pd
import time
import schedule
import smtplib
from email.mime.text import MIMEText
from keep_alive import keep_alive
from datetime import datetime

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

def get_active_futures_symbols():
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    response = requests.get(url)
    data = response.json()

    active_symbols = [
        symbol['symbol']
        for symbol in data['symbols']
        if symbol['contractType'] == 'PERPETUAL' and symbol['status'] == 'TRADING' and symbol['quoteAsset'] == 'USDT'
    ]
    return active_symbols

def fetch_klines(symbol, interval='30m', limit=20):
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
    ])
    df['volume'] = df['volume'].astype(float)
    return df

def scan_and_report():
    print("🔍 Scanning volume...")
    symbols = get_active_futures_symbols()

    length = 20
    multiplier = 2
    min_volume = 100000
    spike_coins = []

    for symbol in symbols:
        try:
            df = fetch_klines(symbol, '30m', limit=length + 1)
            avg_vol = df['volume'][:-1].mean()
            last_vol = df['volume'].iloc[-1]
            if last_vol > avg_vol * multiplier and last_vol > min_volume:
                increase_pct = (last_vol / avg_vol - 1) * 100
                spike_coins.append((symbol, increase_pct))
        except Exception as e:
            print(f"⚠️ Error with {symbol}: {e}")
            continue

    if spike_coins:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = f"🕒 Thời gian: {now}\n\n🔥 Coin có volume tăng đột biến (30m):\n"
        for coin in spike_coins:
            content += f"{coin[0]} | Tăng {coin[1]:.0f}%\n"
        send_email("🔥 Volume Spike Alert (30m)", content)
    else:
        print("⛔ Không có coin nào spike. Không gửi email.")

# Chạy mỗi 10 phút
schedule.every(10).minutes.do(scan_and_report)

keep_alive()

while True:
    schedule.run_pending()
    time.sleep(1)
