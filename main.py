import ccxt
import smtplib
from email.mime.text import MIMEText

# Cấu hình email
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

def fetch_binance_futures_symbols():
    print("🔍 Fetching Futures USDT symbols from Binance...")
    binance = ccxt.binance({'options': {'defaultType': 'future'}})
    try:
        markets = binance.load_markets()
        symbols = [
            s for s in markets
            if s.endswith('/USDT')
            and markets[s].get('type') == 'future'
            and markets[s].get('active') == True
            and markets[s]['info'].get('contractType') == 'PERPETUAL'
        ]
        return symbols
    except Exception as e:
        print("❌ Lỗi load markets:", e)
        return []

# Chạy
symbols = fetch_binance_futures_symbols()

if symbols:
    content = "📄 Danh sách coin Futures USDT (PERPETUAL):\n"
    for i, symbol in enumerate(symbols, 1):
        content += f"{i}. {symbol}\n"
else:
    content = "⚠️ Không lấy được danh sách coin từ Binance."

send_email("📊 Test Binance Futures Coin List", content)
