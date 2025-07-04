import requests
from datetime import datetime

def get_active_futures_symbols():
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    response = requests.get(url)
    data = response.json()

    # Lọc các symbol hợp đồng perpetual đang TRADING
    active_symbols = [
        symbol['symbol']
        for symbol in data['symbols']
        if symbol['contractType'] == 'PERPETUAL' and symbol['status'] == 'TRADING'
    ]
    return active_symbols

if __name__ == "__main__":
    symbols = get_active_futures_symbols()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print(f"[{now}] 🟢 Có {len(symbols)} đồng coin đang active trên Binance Futures:")
    print(', '.join(symbols))
