import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="大师选股系统 V2.0", layout="wide")

def get_robust_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    fin = stock.financials
    bs = stock.balance_sheet
    
    # --- 1. 巴菲特/芒格：ROE (净资产收益率) ---
    roe = info.get('returnOnEquity')
    if (not roe or roe == 0) and not fin.empty and not bs.empty:
        try:
            # 取最新一期净利润和股东权益手动计算
            net_income = fin.loc['Net Income'].iloc[0]
            equity = bs.loc['Stockholders Equity'].iloc[0]
            roe = net_income / equity
        except: roe = 0
    
    # --- 2. 帕特·多尔西：毛利率 (护城河) ---
    margin = info.get('grossMargins')
    if (not margin or margin == 0) and not fin.empty:
        try:
            rev = fin.loc['Total Revenue'].iloc[0]
            cost = fin.loc['Cost Of Revenue'].iloc[0]
            margin = (rev - cost) / rev
        except: margin = 0

    # --- 3. 费雪：营收增长率 ---
    rev_growth = info.get('revenueGrowth')
    if (not rev_growth or rev_growth == 0) and not fin.empty:
        try:
            rev_now = fin.loc['Total Revenue'].iloc[0]
            rev_prev = fin.loc['Total Revenue'].iloc[1]
            rev_growth = (rev_now - rev_prev) / rev_prev
        except: rev_growth = 0

    # --- 4. 格林布拉特：神奇公式 (EBIT/EV) ---
    # 如果没取到 EV，用市值代替
    ev = info.get('enterpriseValue') or info.get('marketCap', 1)
    ebit = info.get('ebitda', 0) * 0.8 # 粗略估算 EBIT
    if not fin.empty and 'Ebit' in fin.index:
        ebit = fin.loc['Ebit'].iloc[0]
    
    ey = (ebit / ev) if ev > 0 else 0

    # --- 5. 邓普顿/马克思：逆向与边际 ---
    curr_price = info.get('currentPrice', 0)
    high_52 = info.get('fiftyTwoWeekHigh', 1)
    is_bottom = "是" if curr_price < (high_52 * 0.7) else "否" # 距高点跌30%视为逆向机会

    return {
        "名称": info.get('longName', ticker),
        "ROE (巴菲特核心)": f"{roe*100:.2f}%" if roe else "数据缺失",
        "毛利率 (护城河)": f"{margin*100:.2f}%" if margin else "数据缺失",
        "营收增速 (费雪指标)": f"{rev_growth*100:.2f}%" if rev_growth else "数据缺失",
        "神奇收益率 (估值)": f"{ey*100:.2f}%" if ey else "数据缺失",
        "逆向机会 (邓普顿)": is_bottom,
        "马克思建议": "高安全边际" if ey > 0.08 else "估值偏高"
    }

st.title("🏛️ 大师核心选股决策系统 V2.0")
st.caption("强化版：自动抓取底层财务报表进行逻辑计算")

target = st.text_input("输入代码 (如 09988.HK, 600519.SS)", "09988.HK")

if st.button("开始深度分析"):
    with st.spinner('正在穿透底层报表，调取官方原始数据...'):
        try:
            res = get_robust_data(target)
            st.table(pd.DataFrame([res]))
            st.success("分析完成。若显示'数据缺失'，可能由于该企业未在当前接口披露最新财报细节。")
        except Exception as e:
            st.error(f"分析出错：请确保代码格式正确（如 09988.HK）。")
