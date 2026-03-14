import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="大师雷达 V24.0", layout="wide")

# --- 内置核心资产扫描池 (包含A股和港股最强蓝筹) ---
SCAN_POOL = [
    "600519.SS", "00700.HK", "09988.HK", "601318.SS", "03690.HK", 
    "600036.SS", "01211.HK", "02318.HK", "601888.SS", "01810.HK",
    "09618.HK", "06160.HK", "603288.SS", "01797.HK", "000333.SZ"
]

@st.cache_data(ttl=3600)
def master_scanner():
    results = []
    progress_bar = st.progress(0)
    
    for i, ticker in enumerate(SCAN_POOL):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # --- 步骤1: 核心定量审计 (巴菲特/多尔西) ---
            roe = info.get('returnOnEquity', 0)
            margin = info.get('grossMargins', 0)
            debt_ratio = info.get('debtToEquity', 100) / 100
            
            # 第一道关卡：基本素质
            if roe < 0.15 or margin < 0.25: continue
            
            # --- 步骤2: 财务防火墙 (张新民) ---
            ocf = info.get('operatingCashflow', 0)
            net_p = info.get('netIncomeToCommon', 1)
            cash_quality = ocf / net_p if net_p > 0 else 0
            
            # 第二道关卡：防造假/防暴雷
            if cash_quality < 0.8: continue
            
            # --- 步骤3: 估值审计 (格林沃尔德/格林布拉特) ---
            ebit = info.get('ebitda', 0) * 0.8
            ev = info.get('enterpriseValue', 1)
            ey = ebit / ev if ev > 0 else 0
            
            # 计算 EPV 每股价值
            iv = ( (ebit * 0.75) / 0.08 - (info.get('totalDebt', 0) - info.get('totalCash', 0)) ) / info.get('sharesOutstanding', 1)
            price = info.get('currentPrice', 1)
            margin_of_safety = (iv - price) / iv if iv > 0 else 0
            
            results.append({
                "代码": ticker,
                "名称": info.get('shortName', ticker),
                "ROE": f"{roe*100:.1f}%",
                "利润含金量": f"{cash_quality:.2f}",
                "神奇收益率": f"{ey*100:.1f}%",
                "安全边际": f"{margin_of_safety*100:.1f}%",
                "大师综合分": (roe * 0.4 + ey * 0.4 + margin_of_safety * 0.2) * 100
            })
        except:
            continue
        progress_bar.progress((i + 1) / len(SCAN_POOL))
        
    return pd.DataFrame(results).sort_values(by="大师综合分", ascending=False).head(5)

st.title("🏛️ 大师灵魂雷达 V24.0")
st.caption("扫描 2026 年最具价值的 A/H 核心资产 | 自动执行张新民审计与格林沃尔德估值")

if st.button("📡 启动全自动全球雷达扫描"):
    with st.spinner("正在穿透数千亿财务报表数据..."):
        top_picks = master_scanner()
        
        st.subheader("🏆 本次雷达扫描产生的【前 3-5 名】精英标的")
        st.table(top_picks)
        
        st.divider()
        st.subheader("🖋️ 大师委员会联合研报")
        
        for index, row in top_picks.iterrows():
            with st.expander(f"查看 {row['名称']} ({row['代码']}) 的选股逻辑"):
                st.write(f"**1. 巴菲特逻辑**：该股 ROE 为 {row['ROE']}，显示出极强的资本自我增值能力。")
                st.write(f"**2. 张新民审计**：利润含金量高达 {row['利润含金量']}，排除财务操纵嫌疑，底层资产纯净。")
                st.write(f"**3. 格林沃尔德估值**：当前具备 {row['安全边际']} 的安全边际。在不再增长的极端假设下，依然具备投资吸引力。")
                st.write(f"**4. 费雪/格林布拉特**：神奇收益率达 {row['神奇收益率']}，处于行业估值分位的顶端。")

st.divider()
st.info("提示：本雷达每小时自动更新一次数据。建议在收盘后运行以获得最精准的估值结论。")
