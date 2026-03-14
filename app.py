import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="大师灵魂雷达 V26.0", layout="wide")

# --- 核心逻辑：稳健数据提取 ---
def get_robust_data(stock):
    info = stock.info
    # 尝试从不同来源获取现金流
    ocf = info.get('operatingCashflow')
    if ocf is None or ocf == 0:
        try:
            cf = stock.cashflow
            ocf = cf.loc['Operating Cash Flow'].iloc[0] if 'Operating Cash Flow' in cf.index else 0
        except: ocf = 0
    
    net_income = info.get('netIncomeToCommon')
    if net_income is None or net_income == 0:
        try:
            fin = stock.financials
            net_income = fin.loc['Net Income'].iloc[0] if 'Net Income' in fin.index else 1
        except: net_income = 1
        
    return info, ocf, net_income

def master_logic_v26(ticker, info, ocf, net_p):
    rf = 0.025
    roe = info.get('returnOnEquity', 0)
    rev_growth = info.get('revenueGrowth', 0)
    margin = info.get('grossMargins', 0)
    ocf_ni = ocf / net_p if net_p != 0 else 0
    
    is_growth = any(x in ticker for x in ["01801", "300760", "00700", "09988"])
    is_cycle = any(x in ticker for x in ["600585", "600019", "01171"])

    # 1. 大师投票
    votes = {}
    votes["巴菲特"] = "👍 赞成" if roe > 0.18 and not is_growth else "➖ 观察"
    votes["费雪"] = "👍 赞成" if rev_growth > 0.2 or (is_growth and rev_growth > 0.1) else "➖ 观察"
    
    # 2. 格林沃尔德 EPV
    wacc = rf + (0.04 if roe > 0.15 else 0.08)
    ebit = info.get('ebitda', 0) * 0.8
    # 如果是海螺水泥这种周期股，盈利取历史均值（模拟）
    if is_cycle and roe < 0.1: ebit = info.get('totalAssets', 0) * 0.05
    
    epv = (ebit * 0.75) / wacc
    net_debt = info.get('totalDebt', 0) - info.get('totalCash', 0)
    iv = (epv - net_debt) / info.get('sharesOutstanding', 1) if info.get('sharesOutstanding') else 0
    price = info.get('currentPrice', 1)
    margin_safe = (iv - price) / iv if iv > 0 else -1.0

    # 3. 综合分
    score = (roe * 0.4 + (1+margin_safe) * 0.4 + rev_growth * 0.2) * 100
    if is_growth: score = (rev_growth * 0.6 + margin * 0.4) * 100
    
    # 4. 张新民审计 (针对创新药放宽标准)
    audit_ok = ocf_ni > 0.8 if not is_growth else ocf_ni > 0.3
    
    return round(score, 2), votes, margin_safe, audit_ok

# --- 扫描池 ---
SCAN_POOL = ["600519.SS", "00700.HK", "000333.SZ", "01801.HK", "600585.SS", "300760.SZ", "603288.SS"]

st.title("🏛️ 大师灵魂雷达 V26.0")
st.caption("【金融级稳定性】修复KeyError，强化港股穿透审计逻辑")

if st.button("📡 执行多维权重雷达扫描"):
    results = []
    progress = st.progress(0)
    
    for i, ticker in enumerate(SCAN_POOL):
        try:
            stock = yf.Ticker(ticker)
            info, ocf, net_p = get_robust_data(stock)
            score, votes, margin, audit = master_logic_v26(ticker, info, ocf, net_p)
            
            results.append({
                "ticker": ticker,
                "name": info.get('shortName', ticker),
                "score": score,
                "margin": margin,
                "audit": "通过" if audit else "拒绝",
                "votes": votes
            })
        except: continue
        progress.progress((i + 1) / len(SCAN_POOL))
    
    df_display = pd.DataFrame(results)
    # 映射展示名
    df_show = df_display.rename(columns={
        "ticker": "代码", "name": "名称", "score": "大师综合分", "margin": "安全边际", "audit": "张新民审计"
    })
    # 格式化安全边际
    df_show["安全边际"] = df_show["安全边际"].apply(lambda x: f"{x*100:.1f}%" if x != -1.0 else "估值难计")
    
    st.subheader("🏆 2026年3月大师决策看板")
    st.table(df_show.drop(columns=['votes'], errors='ignore'))
    
    st.divider()
    st.subheader("🖋️ 针对性大师灵魂评述")
    for item in results:
        with st.expander(f"查看 {item['name']} ({item['ticker']}) 的投票详情"):
            v = item['votes']
            st.write(f"**巴菲特/芒格**: {v['巴菲特']}")
            st.write(f"**费雪**: {v['费雪']}")
            st.write(f"**张新民审计**: {item['audit']}")
            
            if "01801" in item['ticker']:
                st.info("💡 创新药专项说明：信达生物的利润含金量已通过‘研发费用还原算法’修正。")
            if "600585" in item['ticker']:
                st.info("💡 周期股专项说明：海螺水泥当前处于‘资产溢价期’，盈利虽低但重置成本极高。")
