# 脚本 1：基础统计（第一次分析）
import pandas as pd

df = pd.read_csv('/mnt/agents/output/btc_5d_1h.csv', parse_dates=['Date'])

# 看最近12根小时线
print(df.tail(12)[['Date','Open','High','Low','Close','Volume']].to_string(index=False))

last = df.iloc[-1]
peak = df['High'].max()
peak_t = df.loc[df['High'].idxmax(), 'Date']

print(f"\n5日高点: {peak:.0f} @ {peak_t}")
print(f"最新: {last['Close']:.0f} @ {last['Date']}")
print(f"自高点回落: {(last['Close']/peak-1)*100:.2f}%")
print(f"5日最低: {df['Low'].min():.0f}")

# 脚本 2：趋势结构分析（第二次，更新数据后）
import pandas as pd

df = pd.read_csv('/mnt/agents/output/btc_5d_1h_v2.csv', parse_dates=['Date'])

print(df.tail(10)[['Date','Open','High','Low','Close','Volume']].to_string(index=False))

last = df.iloc[-1]
peak = df['High'].max()
print(f"\n5日高点: {peak:.0f}")
print(f"最新: {last['Close']:.0f} @ {last['Date']}  (自高点 {(last['Close']/peak-1)*100:.2f}%)")
print(f"5日最低: {df['Low'].min():.0f} @ {df.loc[df['Low'].idxmin(),'Date']}")

# 找近期成交密集区（25%~75%分位），判断支撑/压力
recent = df[df['Date'] >= '2026-10-21']
print(f"\n10/21以来成交密集区: {recent['Close'].quantile(0.25):.0f} ~ {recent['Close'].quantile(0.75):.0f}")

# 把整个流程换成纯 Python 也可以，用 yfinance 库一行就能拉数据
# import yfinance as yf
# df = yf.download("BTC-USD", period="5d", interval="1h")