import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="大师灵魂雷达 V25.0", layout="wide")

# 扩展扫描池：加入用户提到的潜力股
SCAN_POOL = [
    "600519.SS", "00700.HK", "09988.HK", "600036.SS", "000333.SZ", 
    "600585.SS", "300760.SZ", "01801.HK", "02020.HK", "603288.SS"
]

@st.cache_data(ttl=3600)
def adaptive_master_scanner():
    rf = 0.025 # 2026年3月国债基准
    results = []
    
    for ticker in SCAN_POOL:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # --- [参数提取] ---
            roe = info.get('returnOnEquity', 0)
            rev_growth = info.get('revenueGrowth', 0)
            rd_ratio = info.get('payoutRatio', 0) # 模拟研发强度
            margin = info.get('grossMargins', 0)
            ocf_ni = info.get('operatingCashflow', 0) / info.get('netIncomeToCommon', 1)
            
            # --- [逻辑修正：针对不同行业调整权重] ---
            # 逻辑：如果是生物医药/科技，降低ROE权重，提高增长和研发权重
            is_tech_bio = "01801" in ticker or "300760" in ticker
            w_quality = 0.3 if is_tech_bio else 0.5
            w_growth = 0.4 if is_tech_bio else 0.2
            w_valuation = 0.3
            
            # --- [估值演算：格林沃尔德 EPV] ---
            ebit = info.get('ebitda', 0) * 0.8
            # 动态WACC：高质量公司给更低折现率
            wacc = rf + (0.04 if roe > 0.15 else 0.07)
            epv = (ebit * 0.75) / wacc
            iv = (epv - (info.get('totalDebt', 0) - info.get('totalCash', 0))) / info.get('sharesOutstanding', 1)
            price = info.get('currentPrice', 1)
            safety_margin = (iv - price) / iv if iv > 0 else 0

            # --- [大师评分综合体] ---
            quality_score = (roe * 0.7 + margin * 0.3) * 100
            growth_score = rev_growth * 100
            val_score = safety_margin * 100
            
            final_score = (quality_score * w_quality + growth_score * w_growth + val_score * w_valuation)

            results.append({
                "代码": ticker,
                "名称": info.get('shortName', ticker),
                "综合评分": round(final_score, 2),
                "安全边际": f"{safety_margin*100:.1f}%",
                "利润含金量": round(ocf_ni, 2),
                "ROE": f"{roe*100:.1f}%",
                "建议": "重仓" if safety_margin > 0.2 and ocf_ni > 1 else "观察"
            })
        except: continue
        
    return pd.DataFrame(results).sort_values(by="综合评分", ascending=False)

st.title("🏛️ 大师灵魂雷达 V25.0")
st.caption("当前阶段策略：动态权重分配 | 2026年3月宏观对齐 | 行业特质修正")

[attachment_0](attachment)

if st.button("📡 执行多维权重扫描"):
    with st.spinner("正在对标 2026 年行业生命周期..."):
        df = adaptive_master_scanner()
        st.table(df)
        
        # 针对用户提到的股票进行逻辑诊断
        st.divider()
        st.subheader("🖋️ 针对性逻辑会诊")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**关于信达生物 (01801.HK)**")
            st.write("费雪视角：研发费用不应被视为损失，而是未来的‘护城河期权’。若营收增速 > 30%，即便 ROE 为负，也具备进攻价值。")
        with col2:
            st.write("**关于海螺水泥 (600585.SS)**")
            st.write("格林沃尔德视角：周期股不看利润看资产。当股价跌破‘有形重置成本’且行业供给收缩时，便是安全边际最大的时刻。")
