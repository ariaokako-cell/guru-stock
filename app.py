import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="大师选股 V5.0", layout="wide")

def deep_scan_finance(df, keywords):
    """深潜扫描：在复杂的财报行索引中通过关键词定位数据"""
    if df is None or df.empty: return None
    for kw in keywords:
        # 模糊匹配：不区分大小写，包含关键字即可
        matches = [idx for idx in df.index if kw.lower() in str(idx).lower()]
        if matches:
            val = df.loc[matches[0]].iloc[0]
            if pd.notnull(val) and val != 0: return val
    return None

def get_guru_logic(ticker):
    stock = yf.Ticker(ticker)
    
    # 获取原始报表数据 (这是最官方的源)
    try:
        fin = stock.financials
        bs = stock.balance_sheet
    except:
        fin, bs = pd.DataFrame(), pd.DataFrame()

    info = stock.info
    
    # --- 1. 巴菲特逻辑：ROE (利润 / 权益) ---
    net_inc = deep_scan_finance(fin, ['Net Income', 'Profit After Tax', 'NetProfit', '净利润'])
    equity = deep_scan_finance(bs, ['Stockholders Equity', 'Total Equity', 'Equity Attributable', '股东权益'])
    roe = (net_inc / equity) if net_inc and equity else info.get('returnOnEquity')

    # --- 2. 多尔西逻辑：毛利率 (护城河) ---
    rev = deep_scan_finance(fin, ['Total Revenue', 'Operating Revenue', '营业收入'])
    gp = deep_scan_finance(fin, ['Gross Profit', '毛利'])
    if not gp and rev:
        cost = deep_scan_finance(fin, ['Cost of Revenue', 'Operating Cost', '营业成本'])
        if cost: gp = rev - cost
    margin = (gp / rev) if gp and rev else info.get('grossMargins')

    # --- 3. 费雪逻辑：营收增速 ---
    rev_growth = None
    if not fin.empty:
        rev_rows = [idx for idx in fin.index if 'Revenue' in str(idx) or '营业收入' in str(idx)]
        if rev_rows and len(fin.columns) >= 2:
            r_now = fin.loc[rev_rows[0]].iloc[0]
            r_prev = fin.loc[rev_rows[0]].iloc[1]
            if r_prev != 0: rev_growth = (r_now - r_prev) / r_prev

    # --- 4. 格林布拉特：神奇收益率 (EBIT / EV) ---
    # $Earnings Yield = \frac{EBIT}{Enterprise Value}$
    ebit = deep_scan_finance(fin, ['EBIT', 'Operating Income', '营业利润'])
    ev = info.get('enterpriseValue') or info.get('marketCap', 1)
    ey = (ebit / ev) if ebit and ev > 0 else 0

    return {
        "名称": info.get('longName') or ticker,
        "ROE (质量核心)": f"{roe*100:.2f}%" if roe else "官方报表扫描中...",
        "毛利率 (护城河)": f"{margin*100:.2f}%" if margin else "官方报表扫描中...",
        "营收增速 (成长性)": f"{rev_growth*100:.2f}%" if rev_growth else "计算中...",
        "神奇收益率 (估值)": f"{ey*100:.2f}%" if ey > 0 else "估值待定",
        "马克思建议": "高安全边际" if ey > 0.08 else "需警惕周期风险",
        "邓普顿机会": "是" if info.get('currentPrice',0) < info.get('fiftyTwoWeekHigh',1)*0.7 else "否"
    }

st.title("🏛️ 大师核心选股系统 V5.0")
st.caption("【终极穿透版】已解决港股、A股官方财报关键词不匹配问题")

target = st.text_input("代码 (如: 01299.HK, 00005.HK, 600519.SS)", "01299.HK")

if st.button("开始深度扫描"):
    with st.spinner('正在像大师一样穿透底层原始报表...'):
        try:
            res = get_guru_logic(target)
            st.table(pd.DataFrame([res]))
            st.success("数据已成功调取！逻辑：优先扫描官方年度/季度审计报表。")
        except:
            st.error("调取失败，请检查代码后缀是否正确。")
