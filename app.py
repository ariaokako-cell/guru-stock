import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="大师选股系统 V3.0", layout="wide")

def find_value(df, keywords):
    """在财务报表中模糊搜索关键词并提取最新数值"""
    if df is None or df.empty:
        return None
    for key in keywords:
        # 在索引中寻找匹配的行
        match = [idx for idx in df.index if key.lower() in idx.lower()]
        if match:
            return df.loc[match[0]].iloc[0]
    return None

def get_ultra_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # 尝试调取不同版本的财务报表 (兼容新旧接口)
    try:
        fin = stock.get_income_stmt()
        bs = stock.get_balance_sheet()
    except:
        fin = stock.financials
        bs = stock.balance_sheet

    # --- 1. 巴菲特逻辑：ROE ---
    roe = info.get('returnOnEquity')
    if not roe or roe == 0:
        net_inc = find_value(fin, ['Net Income', 'NetProfit', 'Profit After Tax'])
        equity = find_value(bs, ['Stockholders Equity', 'Total Equity', 'Equity Attributable'])
        if net_inc and equity:
            roe = net_inc / equity

    # --- 2. 多尔西逻辑：毛利率 ---
    margin = info.get('grossMargins')
    if not margin or margin == 0:
        rev = find_value(fin, ['Total Revenue', 'Operating Revenue', 'Sales'])
        cost = find_value(fin, ['Cost Of Revenue', 'Cost of Goods Sold', 'Operating Expense'])
        if rev and cost:
            margin = (rev - cost) / rev
        elif rev: # 某些公司直接给出毛利
            gp = find_value(fin, ['Gross Profit'])
            if gp: margin = gp / rev

    # --- 3. 费雪逻辑：营收增速 ---
    rev_growth = info.get('revenueGrowth')
    if not rev_growth or rev_growth == 0:
        rev_list = fin.loc[[idx for idx in fin.index if 'Revenue' in idx or 'Sales' in idx][0]] if not fin.empty else []
        if len(rev_list) >= 2:
            rev_growth = (rev_list.iloc[0] - rev_list.iloc[1]) / rev_list.iloc[1]

    # --- 4. 格林布拉特：神奇公式 (EBIT/EV) ---
    ev = info.get('enterpriseValue') or info.get('marketCap', 1)
    ebit = find_value(fin, ['Ebit', 'Operating Income'])
    ey = (ebit / ev) if ebit and ev > 0 else 0

    # --- 5. 邓普顿/马克思：逆向机会 ---
    curr_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
    high_52 = info.get('fiftyTwoWeekHigh', 1)
    is_bottom = "是" if curr_price > 0 and curr_price < (high_52 * 0.75) else "否"

    return {
        "名称": info.get('longName') or info.get('shortName') or ticker,
        "ROE (巴菲特核心)": f"{roe*100:.2f}%" if roe else "官方未披露细节",
        "毛利率 (护城河)": f"{margin*100:.2f}%" if margin else "官方未披露细节",
        "营收增速 (费雪指标)": f"{rev_growth*100:.2f}%" if rev_growth else "官方未披露细节",
        "神奇收益率 (估值)": f"{ey*100:.2f}%" if ey else "估值难计算",
        "逆向机会 (邓普顿)": is_bottom,
        "马克思建议": "高安全边际" if ey and ey > 0.08 else "需关注宏观风险"
    }

st.title("🏛️ 大师核心选股决策系统 V3.0")
st.caption("全市场穿透版：兼容港股/A股官方报表差异")

target = st.text_input("输入代码 (A股: 600519.SS, 港股: 09988.HK)", "09988.HK")

if st.button("开始穿透分析"):
    with st.spinner('正在暴力破解官方财务报表关键词...'):
        try:
            res = get_ultra_data(target)
            st.table(pd.DataFrame([res]))
            st.info("数据逻辑：若官方汇总表缺失，系统已自动切换至底层年度/季度原始报表进行重构计算。")
        except Exception as e:
            st.error(f"分析失败，请检查网络或代码格式。")
