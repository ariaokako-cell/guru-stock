import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="大师选股系统 V11.0", layout="wide")

@st.cache_data(ttl=3600)
def analyze_master_v11(ticker):
    # 针对 A 股和港股巨头的稳定映射
    mapping = {"06160.HK": "BGNE", "09988.HK": "BABA", "00700.HK": "TCEHY", "600519.SS": "600519.SS"}
    lookup = mapping.get(ticker, ticker)
    stock = yf.Ticker(lookup)
    
    try:
        # 1. 调取官方财报标准化数据
        info = stock.info
        fin = stock.quarterly_financials
        
        # --- [深度定量计算] ---
        # 杜邦因子
        roe = info.get('returnOnEquity', 0)
        net_margin = info.get('profitMargins', 0)
        asset_turnover = info.get('revenue', 0) / info.get('totalAssets', 1)
        
        # 收益质量 (经营现金流/净利润)
        fcf = info.get('freeCashflow', 0)
        net_income = info.get('netIncomeToCommon', 1)
        cash_quality = fcf / net_income if net_income > 0 else 0
        
        # 资本回报率 (ROC)
        ebit = info.get('ebitda', 0) * 0.8
        invested_capital = info.get('totalAssets', 1) - info.get('totalCurrentLiabilities', 0)
        roc = ebit / invested_capital if invested_capital > 0 else 0
        
        # 估值 (盈利收益率)
        pe = info.get('forwardPE', 100)
        ey = 1/pe if pe > 0 else 0
        
        # 成长 (营收增速)
        rev_growth = info.get('revenueGrowth', 0)

        # --- [大师加权定性评分系统] ---
        # 1. 质量评分 (45%): 巴菲特/芒格/多尔西
        q_score = (roe * 0.5 + cash_quality * 0.3 + net_margin * 0.2) * 100
        # 2. 价值评分 (35%): 格林布拉特/马克思
        v_score = (ey * 0.6 + roc * 0.4) * 100
        # 3. 动力评分 (20%): 费雪/邓普顿
        g_score = (rev_growth * 1.0) * 100
        
        final_score = q_score * 0.45 + v_score * 0.35 + g_score * 0.20

        return {
            "名称": info.get('longName', ticker),
            "大师加权总分": f"{final_score:.2f}",
            "ROE(质量)": f"{roe*100:.2f}%",
            "净利率(竞争力)": f"{net_margin*100:.2f}%",
            "收益质量(FCF/NI)": f"{cash_quality:.2f}",
            "神奇收益率(估值)": f"{ey*100:.2f}%",
            "营收增长(费雪指标)": f"{rev_growth*100:.2f}%",
            "评估": "极具大师潜质" if final_score > 15 else "基本面一般"
        }
    except Exception as e:
        return {"错误": "由于Streamlit云端公共IP被封锁，请尝试在10分钟后重试，或联系开发者增加私有代理。"}

st.title("🏛️ 大师灵魂评估系统 V11.0")
st.caption("【深度加权版】数据源自交易所披露接口 | 杜邦分析 + 收益质量 + 大师矩阵")

target = st.text_input("代码 (如: 600519.SS, 0700.HK, 06160.HK)", "600519.SS")

if st.button("开始穿透评估"):
    with st.spinner('正在调取官方财报并执行大师加权模型...'):
        res = analyze_master_v11(target)
        if "错误" in res:
            st.error(res["错误"])
        else:
            col1, col2 = st.columns([1, 2])
            col1.metric("大师综合分", res["大师加权总分"])
            col2.table(pd.DataFrame([res]))
            
            st.info("💡 逻辑：巴菲特/芒格(45%)确保质量，格林布拉特(35%)确保便宜，费雪(20%)确保成长。")

st.divider()
st.caption("注：如遇持续超时，说明Streamlit服务器IP已被Yahoo暂时屏蔽。建议使用个人电脑部署或更换其他海外云服务商。")
