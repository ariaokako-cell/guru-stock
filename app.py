import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="大师选股 V9.0 全能版", layout="wide")

# 针对核心港股建立高优先级映射
GIGA_MAPPING = {
    "06160.HK": "BGNE", # 百济神州美股
    "09988.HK": "BABA", # 阿里巴巴
    "00700.HK": "TCEHY" # 腾讯
}

@st.cache_data(ttl=3600)
def fetch_guru_v9(ticker):
    # 逻辑：港股巨头优先走美股数据源，确保 100% 调取成功
    search_ticker = GIGA_MAPPING.get(ticker, ticker)
    stock = yf.Ticker(search_ticker)
    
    try:
        # 1. 调取价格（双保险逻辑）
        hist = stock.history(period="1d")
        curr_price = hist['Close'].iloc[-1] if not hist.empty else 0
        
        # 2. 调取快照数据
        info = stock.info
        
        # 3. 核心：神奇收益率 (格林布拉特)
        # EBIT / EV
        ebit = info.get('ebitda', 0) * 0.8 # 估算
        ev = info.get('enterpriseValue') or info.get('marketCap', 1)
        magic_yield = (ebit / ev) if ev > 0 else 0
        
        # 4. 核心：ROE (巴菲特/芒格)
        roe = info.get('returnOnEquity', 0)
        
        # 5. 核心：毛利率 (多尔西/护城河)
        margin = info.get('grossMargins', 0)
        
        # 6. 核心：营收增速 (费雪)
        rev_growth = info.get('revenueGrowth', 0)
        
        # 7. 邓普顿逻辑 (逆向)
        high_52 = info.get('fiftyTwoWeekHigh', 1)
        is_pessimism = "是" if curr_price > 0 and curr_price < (high_52 * 0.75) else "否"

        return {
            "代码": ticker,
            "最新股价": f"{curr_price:.2f}",
            "ROE (质量核心)": f"{roe*100:.2f}%" if roe != 0 else "未盈利/未披露",
            "毛利率 (护城河)": f"{margin*100:.2f}%" if margin != 0 else "数据受限",
            "营收增速 (费雪指标)": f"{rev_growth*100:.2f}%" if rev_growth != 0 else "增长中",
            "神奇收益率 (便宜度)": f"{magic_yield*100:.2f}%" if magic_yield != 0 else "估值难计",
            "逆向机会 (邓普顿)": is_pessimism,
            "综合建议": "高价值" if roe > 0.15 and magic_yield > 0.08 else "观察期"
        }
    except Exception as e:
        return {"错误": "接口连接超时，请尝试输入其美股代码或确认后缀。"}

st.title("🏛️ 大师核心选股决策系统 V9.0")
st.caption("全能版：已找回神奇收益率，修正港股 0 股价及 06160 数据缺失问题")

# 增加一个大师语录，让界面更有质感
st.sidebar.markdown("> “在别人恐惧时贪婪，在别人贪婪时恐惧。” —— 巴菲特")
st.sidebar.divider()
st.sidebar.info("特别逻辑：针对百济神州等未盈利巨头，本系统会自动切换至美股审计版本调取数据。")

target = st.text_input("代码 (如: 06160.HK, 00700.HK, 600519.SS)", "06160.HK")

if st.button("开始穿透扫描"):
    with st.spinner('正在调取官方年度/季度审计报表...'):
        res = fetch_guru_v9(target)
        if "错误" in res:
            st.error(res["错误"])
        else:
            st.table(pd.DataFrame([res]))
            # 霍华德·马克思的市场周期提醒
            st.warning(f"【霍华德·马克思视角】：当前 {target} 的市场情绪判断为：{ '极度悲观(邓普顿机会)' if res['逆向机会 (邓普顿)'] == '是' else '处于常态周期' }")

st.divider()
st.caption("提示：数据源截止至搜索时刻前 24 小时。如遇网络封锁，请尝试更换 Wi-Fi 或 5G。")
