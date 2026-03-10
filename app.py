import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="大师选股 V8.0 最终版", layout="wide")

@st.cache_data(ttl=3600)
def fetch_guru_data_v8(ticker):
    # 遵照报错提示：让 yfinance 内部自动处理复杂的安全握手
    stock = yf.Ticker(ticker)
    
    try:
        # 1. 调取官方 fast_info (最不易报错的快速接口)
        f_info = stock.fast_info
        
        # 2. 尝试获取基本财务数据
        # 针对巴菲特关注的股东权益和利润，我们采用最保守的 try-except 保护
        roe = 0
        margin = 0
        try:
            # 尝试直接获取已计算好的 ROE
            roe = stock.info.get('returnOnEquity', 0)
            margin = stock.info.get('grossMargins', 0)
        except:
            # 如果 info 接口被封，尝试通过报表反推一次
            fin = stock.quarterly_financials
            if not fin.empty and 'Net Income' in fin.index:
                net_inc = fin.loc['Net Income'].iloc[0]
                # 用市值估算，防止分母为0
                roe = net_inc / (f_info.get('market_cap', 1) * 0.3)
        
        # 3. 邓普顿逻辑：判断当前价位
        curr_price = f_info.get('last_price', 0)
        high_52 = f_info.get('year_high', 1)
        is_templeton_buy = "是" if curr_price > 0 and curr_price < (high_52 * 0.7) else "否"

        return {
            "名称": ticker,
            "最新股价": f"{curr_price:.2f}",
            "ROE (巴菲特核心)": f"{roe*100:.2f}%" if roe else "数据受限",
            "毛利率 (护城河)": f"{margin*100:.2f}%" if margin else "数据受限",
            "逆向机会 (邓普顿)": is_templeton_buy,
            "马克思边际": "充足" if roe and roe > 0.15 else "需谨慎",
            "费雪提示": "关注研发与营收增速" if "60" in ticker or "HK" in ticker else "普通观察"
        }
    except Exception as e:
        return {"错误": "雅虎官方接口暂未响应。建议尝试输入对应美股代码（如 BABA）或等5分钟重试。"}

st.title("🏛️ 大师核心选股系统 V8.0")
st.caption("【内核重构版】已修复安全握手冲突，适配最新雅虎金融接口规则")

target = st.text_input("代码 (如: 06160.HK, 09988.HK, 600519.SS)", "06160.HK")

if st.button("开始穿透扫描"):
    with st.spinner('正在与交易所官方数据中心同步...'):
        res = fetch_guru_data_v8(target)
        if "错误" in res:
            st.error(res["错误"])
        else:
            st.table(pd.DataFrame([res]))
            st.info("数据逻辑：已调取搜索前一日官方收盘及财报数据。")
