#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BTC 技术分析脚本
- 数据: 多源自动降级 (xfinance 优先, OKX/Binance/CoinGecko 直连兜底)
- 输出: 关键指标 + 支撑/压力位(自动去重聚类) + 走势图(带标注)
依赖: pip install xfinance pandas matplotlib requests
"""

import os

# ========== 代理配置 ==========
# 不启用代理: PROXY = None
# 启用代理:   PROXY = "http://127.0.0.1:7890"  (端口按实际代理软件填写)
PROXY = None
# =============================

_PROXY_ENV_KEYS = ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"]
if PROXY:
    for _k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        os.environ[_k] = PROXY
else:
    for _k in _PROXY_ENV_KEYS:
        os.environ.pop(_k, None)

import xfinance as xf
import pandas as pd
import matplotlib.pyplot as plt

# ========== 参数区(按需修改) ==========
TICKER   = "BTC-USD"
PERIOD   = "5d"
INTERVAL = "1h"
MA_FAST  = 10
MA_SLOW  = 99
N_LEVELS = 3
CLUSTER_PCT = 0.004
OUT_IMG  = "btc_analysis.png"
# =====================================

OKX_BAR = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "1H", "4h": "4H", "1d": "1D"}
BINANCE_BAR = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "1h", "4h": "4h", "1d": "1d"}


def _norm(df):
    df = df.dropna(subset=["Close"]).sort_values("Date").reset_index(drop=True)
    if df.empty:
        raise ValueError("空数据")
    return df


def _from_xfinance(ticker, period, interval):
    """xfinance 优先数据源, 内置 Yahoo -> Binance -> CoinGecko 自动降级"""
    symbol = ticker.replace("-USD", "/USDT")   # xfinance 加密符号格式
    t = xf.Ticker(symbol)
    df = t.history(period=period, interval=interval)

    if df is None or df.empty:
        raise ValueError("xfinance 返回空数据")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()
    for cand in ("Datetime", "Date", "index"):
        if cand in df.columns:
            df = df.rename(columns={cand: "Date"})
            break

    required = ["Date", "Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"xfinance 数据列缺失: {missing}, 实际列: {list(df.columns)}")

    return df[required]


def _from_okx(ticker, interval, limit):
    import requests
    inst_id = ticker.replace("-USD", "-USDT")
    bar = OKX_BAR.get(interval, "1H")
    url = ("https://www.okx.com/api/v5/market/candles"
           f"?instId={inst_id}&bar={bar}&limit={min(limit, 300)}")
    data = requests.get(url, timeout=10, proxies=PROXY).json().get("data", [])
    if not data:
        raise ValueError("OKX 无数据")
    cols = ["ts", "Open", "High", "Low", "Close", "Volume", "volCcy", "confirm"]
    df = pd.DataFrame(data, columns=cols)
    df = df[df["confirm"] == "1"]
    for c in ["Open", "High", "Low", "Close", "Volume"]:
        df[c] = df[c].astype(float)
    df["Date"] = pd.to_datetime(df["ts"].astype("int64"), unit="ms", utc=True)
    return df[["Date", "Open", "High", "Low", "Close", "Volume"]]


def _from_binance(ticker, interval, limit):
    import requests
    symbol = ticker.replace("-USD", "USDT")
    bar = BINANCE_BAR.get(interval, "1h")
    url = ("https://api.binance.com/api/v3/klines"
           f"?symbol={symbol}&interval={bar}&limit={min(limit, 1000)}")
    data = requests.get(url, timeout=10, proxies=PROXY).json()
    if not isinstance(data, list) or not data:
        raise ValueError("Binance 无数据")
    df = pd.DataFrame(data, columns=[
        "ts", "Open", "High", "Low", "Close", "Volume",
        "ct", "qv", "trades", "tbb", "tbq", "ig"])
    for c in ["Open", "High", "Low", "Close", "Volume"]:
        df[c] = df[c].astype(float)
    df["Date"] = pd.to_datetime(df["ts"].astype("int64"), unit="ms", utc=True)
    return df[["Date", "Open", "High", "Low", "Close", "Volume"]]


def _from_coingecko(ticker, period):
    import requests
    days = {"1d": 1, "5d": 5, "1mo": 30}.get(period, 5)
    url = ("https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
           f"?vs_currency=usd&days={days}")
    j = requests.get(url, timeout=15, proxies=PROXY).json()
    prices = j.get("prices", [])
    vols = j.get("total_volumes", [])
    if not prices:
        raise ValueError("CoinGecko 无数据")
    df = pd.DataFrame(prices, columns=["ts", "Close"])
    v = pd.DataFrame(vols, columns=["ts", "Volume"])
    df = df.merge(v, on="ts")
    df["Date"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    df = df.set_index("Date").resample("1h").last().dropna(subset=["Close"])
    df["Open"] = df["High"] = df["Low"] = df["Close"]
    return df.reset_index()[["Date", "Open", "High", "Low", "Close", "Volume"]]


SOURCES = [
    ("xfinance",  lambda t, p, i, n: _from_xfinance(t, p, i)),
    ("OKX",       lambda t, p, i, n: _from_okx(t, i, n)),
    ("Binance",   lambda t, p, i, n: _from_binance(t, i, n)),
    ("CoinGecko", lambda t, p, i, n: _from_coingecko(t, p)),
]


def fetch_data(ticker=TICKER, period=PERIOD, interval=INTERVAL):
    limit = {"1d": 24, "5d": 120, "1mo": 720}.get(period, 120)
    errors = []
    for name, fn in SOURCES:
        try:
            df = _norm(fn(ticker, period, interval, limit))
            print(f"数据源: {name}")
            return df
        except Exception as e:
            errors.append(f"{name}: {type(e).__name__}: {e}")
            print(f"[跳过] {name} -> {type(e).__name__}: {e}")
    raise ValueError("所有数据源均失败: " + " | ".join(errors))


def add_indicators(df):
    df["MA_fast"] = df["Close"].rolling(MA_FAST).mean()
    df["MA_slow"] = df["Close"].rolling(MA_SLOW).mean()
    df["pct_chg"] = df["Close"].pct_change() * 100
    return df


def cluster_levels(levels, tol_pct=CLUSTER_PCT):
    levels = sorted(levels)
    clusters = []
    for p in levels:
        if clusters and abs(p - clusters[-1][-1]) / clusters[-1][-1] < tol_pct:
            clusters[-1].append(p)
        else:
            clusters.append([p])
    return [round(sum(c) / len(c)) for c in clusters]


def find_levels(df, n=N_LEVELS):
    recent = df.tail(48)
    last = df["Close"].iloc[-1]
    hi, lo = df["High"].max(), df["Low"].min()

    q25, q75 = recent["Close"].quantile(0.25), recent["Close"].quantile(0.75)
    local_highs = recent["High"].tolist() + [q75]
    local_lows  = recent["Low"].tolist() + [q25]

    resistance = cluster_levels([p for p in local_highs if p > last])[:n]
    support    = cluster_levels([p for p in local_lows  if p < last])[:n]
    return support, resistance, round(hi), round(lo)


def print_report(df, support, resistance, hi, lo):
    last = df.iloc[-1]
    peak = df["High"].max()
    chg = (last["Close"] / peak - 1) * 100
    vol_last, vol_avg = last["Volume"], df["Volume"].tail(20).mean()

    print("=" * 50)
    print(f"品种: {TICKER}   周期: {INTERVAL}   范围: {PERIOD}")
    print(f"最新价: {last['Close']:.0f}   当根涨跌: {last['pct_chg']:+.2f}%")
    print(f"区间高/低: {hi} / {lo}   距高点: {chg:+.2f}%")
    print(f"MA{MA_FAST}: {last['MA_fast']:.0f}   MA{MA_SLOW}: {last['MA_slow']:.0f}")

    px, f, sl = last['Close'], last['MA_fast'], last['MA_slow']
    if px > f > sl:   trend = "多头排列(强势)"
    elif px < f < sl: trend = "空头排列(弱势)"
    elif f > sl:      trend = "均线多头但价格跌破短均线(转弱信号)"
    else:             trend = "均线空头但价格站上短均线(转强信号)"
    print(f"趋势状态: {trend}")

    def _fmt(v):
        return f"{v/1e8:.1f}亿" if v >= 1e8 else (f"{v/1e4:.1f}万" if v >= 1e4 else f"{v:.0f}")

    print(f"最新量: {_fmt(vol_last)}   20根均量: {_fmt(vol_avg)}   量比: {vol_last/vol_avg:.1f}")
    print("-" * 50)
    print("支撑位:", " / ".join(map(str, support)) or "无(创阶段新低)")
    print("压力位:", " / ".join(map(str, resistance)))
    print("=" * 50)


def plot(df, support, resistance):
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(df.index, df["Close"], label="Close", lw=1.2, color="#2b6cb0")
    ax.plot(df.index, df["MA_fast"], label=f"MA{MA_FAST}", lw=1, color="#e53e3e")
    ax.plot(df.index, df["MA_slow"], label=f"MA{MA_SLOW}", lw=1, color="#b7791f")

    ymin, ymax = df["Close"].min(), df["Close"].max()
    pad = (ymax - ymin) * 0.15
    ax.set_ylim(ymin - pad, ymax + pad)

    all_levels = [(s, "green", "S") for s in support] + [(r, "red", "R") for r in resistance]
    for i, (p, color, tag) in enumerate(all_levels):
        if not (ymin - pad <= p <= ymax + pad):
            continue
        ax.axhline(p, color=color, ls="--", alpha=0.5)
        offset = (i % 3) * (pad * 0.18)
        ax.text(df.index[2], p + offset, f"{tag} {p}", color=color, fontsize=10)

    ax.set_title(f"{TICKER} {INTERVAL}  latest={df['Close'].iloc[-1]:.0f}")
    ax.legend(loc="best")
    ax.grid(alpha=0.2)
    plt.tight_layout()
    plt.savefig(OUT_IMG, dpi=120)
    print(f"图已保存: {OUT_IMG}")


if __name__ == "__main__":
    df = add_indicators(fetch_data())
    support, resistance, hi, lo = find_levels(df)
    print_report(df, support, resistance, hi, lo)
    plot(df, support, resistance)