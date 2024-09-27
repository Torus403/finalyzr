import yfinance as yf


def get_current_price(ticker: str) -> float:
    ticker_data = yf.Ticker(ticker)
    hist = ticker_data.history(period="1d")
    if hist.empty:
        raise ValueError(f"No data found for ticker {ticker}")
    current_price = hist["Close"].iloc[-1]
    return current_price
