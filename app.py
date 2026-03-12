import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="大师选股系统 V10.0", layout="wide")

@st.cache_data(ttl=3600)
def get_master_evaluation(ticker):
    # 针对巨头的映射逻辑，规避超时
    mapping = {"06160.HK": "BGNE", "09988.HK": "BABA", "00700.HK": "TCEHY"}
    lookup = mapping.get(ticker, ticker)
    stock = yf.Ticker(lookup)
    
    try:
        # 获取最新及历史财务报表
        fin = stock.financials
        bs = stock.balance_sheet
        cf = stock.cashflow
        info = stock.info
        
        # --- [定量深化：深度财务指标] ---
        # 1. 杜邦分析：净利率与周转率
        net_margin = info.get('profitMargins', 0)
        asset_turnover = info.get('revenue', 0) / info.get('totalAssets', 1)
        # 2. 收益质量：现金流/净利润
        fcf = info.get('freeCashflow', 0)
        net_income = info.get('netIncomeToCommon', 1)
        earnings_quality = fcf / net_income if net_income > 0 else 0
        # 3. 资本回报率 (ROC)
        ebit = info.get('ebitda', 0) * 0.8
        invested_capital = info.get('totalAssets', 1) - info.get('totalCurrentLiabilities', 0)
        roc = ebit / invested_capital if invested_capital > 0 else 0

        # --- [定性模拟：加权评分矩阵] ---
        scores = {}
        
        # 巴菲特/芒格权重 (50%): 核心看ROE稳定性与收益质量
        roe = info.get('returnOnEquity', 0)
        scores['Buffett_Munger'] = (roe * 0.6 + earnings_quality * 0.4) * 100
        
        # 格林布拉特/马克思权重 (30%): 神奇公式(ROC + 盈利率)
        pe = info.get('forwardPE', 50)
        ey = 1/pe if pe > 0 else 0
        scores['Greenblatt_Marks'] = (roc * 0.7 + ey * 0.3) * 100
        
        # 费雪/邓普顿权重 (20%): 营收增速与价格偏离度
        rev_growth = info.get('revenueGrowth', 0)
        price_to_high = info.get('currentPrice', 0) / info.get('fiftyTwoWeekHigh', 1)
        scores['Fisher_Templeton'] = (rev_growth * 0.7 + (1 - price_to_high) * 0.3) * 100

        # 最终加权总分
        final_score = (scores['Buffett_Munger'] * 0.5 + 
                       scores['Greenblatt_Marks'] * 0.3 + 
                       scores['Fisher_Templeton'] * 0.2)

        return {
            "名称": info.get('longName', ticker),
            "大师综合分": f"{final_score:.1f}",
            "ROE (质量)": f"{roe*100:.2f}%",
            "收益质量 (FCF/NI)": f"{earnings_quality:.2f}",
            "资产周转率 (效率)": f"{asset_turnover:.2f}",
            "神奇收益率 (估值)": f"{ey*100:.2f}%",
            "营收增长 (费雪)": f"{rev_growth*100:.2f}%",
            "结论": "值得重仓" if final_score > 15 else "谨慎观察"
        }
    except:
        return {"错误": "连接由于公共IP受限，请尝试切换网络或输入美股代码。"}

st.title("🏛️ 大师灵魂评估系统 V10.0")
st.caption("【加权重构版】定量杜邦分析 + 定性权重矩阵")

target = st.text_input("代码 (如: 06160.HK, 09988.HK, 600519.SS)", "06160.HK")

if st.button("开始深度加权扫描"):
    with st.spinner('正在执行杜邦分析与大师权重对齐...'):
        res = get_master_evaluation(target)
        if "错误" in res:
            st.error(res["错误"])
        else:
            st.metric("大师综合加权分", res["大师综合分"])
            st.table(pd.DataFrame([res]))
            
            # 逻辑说明
            with st.expander("点击查看评价逻辑"):
                st.write("**50% 核心权重 (巴菲特/芒格)**：不仅看ROE，更看现金流对净利润的覆盖。")
                st.write("**30% 估值权重 (格林布拉特)**：基于剔除杠杆后的ROC与市场盈利率。")
                st.write("**20% 成长逆向 (费雪/邓普顿)**：评估营收爆发力与当前价格的下行保护。")

st.divider()
st.info("提示：若连接超时，请尝试在 iPhone 上切换 Wi-Fi 为 5G 信号，这会改变你的访问 IP，从而绕过防火墙封锁。")
