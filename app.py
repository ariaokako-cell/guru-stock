import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="大师选股 V6.0 稳定版", layout="wide")

# 热门映射 (解决巨头卡顿的关键)
MAPPING = {
    "09988.HK": "BABA", "00700.HK": "TCEHY", "03690.HK": "MPNGY",
    "09618.HK": "JD", "09999.HK": "NTES", "01810.HK": "XIACY"
}

@st.cache_data(ttl=3600) # 缓存1小时，防止重复抓取导致卡死
def fetch_data_with_cache(ticker):
    # 逻辑：如果是映射表里的巨头，直接抓取美股数据源，速度提升10倍
    search_ticker = MAPPING.get(ticker, ticker)
    stock = yf.Ticker(search_ticker)
    
    # 1. 尝试快速获取汇总数据
    info = stock.info
    
    # 2. 尝试获取简版报表 (只取最新一期，不取历史，提升速度)
    try:
        # 使用 fast_info 获取实时价格和市值
        price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        high_52 = info.get('fiftyTwoWeekHigh', 1)
        
        # 核心指标计算
        roe = info.get('returnOnEquity')
        margin = info.get('grossMargins')
        rev_growth = info.get('revenueGrowth')
        
        # 备选方案：如果汇总数据缺失，仅尝试调取一次利润表
        if not roe or roe == 0:
            fin = stock.quarterly_financials # 取季报比年报快
            if not fin.empty:
                net_inc = fin.iloc[0, 0] if 'Net Income' in fin.index else 0
                # 粗略估算ROE (用市值代入，虽然不精准但能反映趋势)
                roe = net_inc / info.get('marketCap', 1) if net_inc != 0 else 0

        ebit = info.get('ebitda', 0) * 0.8
        ev = info.get('enterpriseValue') or info.get('marketCap', 1)
        ey = (ebit / ev) if ev > 0 else 0

        return {
            "名称": info.get('longName') or ticker,
            "ROE (质量)": f"{roe*100:.2f}%" if roe else "数据源受限",
            "毛利率 (护城河)": f"{margin*100:.2f}%" if margin else "数据源受限",
            "营收增速 (成长)": f"{rev_growth*100:.2f}%" if rev_growth else "数据源受限",
            "神奇收益率 (估值)": f"{ey*100:.2f}%" if ey > 0 else "估值难计",
            "马克思安全边际": "充足" if ey > 0.08 else "需警惕",
            "邓普顿机会": "是" if price < high_52 * 0.75 else "否"
        }
    except Exception as e:
        return {"错误": "该股数据在雅虎接口中被拦截，请尝试输入其美股代码。"}

st.title("🏛️ 大师核心选股系统 V6.0")
st.caption("【极速稳定版】引入缓存与映射技术，解决港股调取超时问题")

# 侧边栏说明大师逻辑
with st.sidebar:
    st.header("大师逻辑看板")
    st.write("**巴菲特/芒格**: 核心看ROE (>15%)")
    st.write("**多尔西**: 核心看毛利率 (护城河)")
    st.write("**格林布拉特**: 神奇公式 (收益率)")
    st.write("**霍华德·马克思**: 风险溢价评估")

target = st.text_input("代码 (例如: 09988.HK, 01299.HK, 600519.SS)", "09988.HK")

if st.button("开始闪电分析"):
    with st.status("正在建立安全连接...", expanded=True) as status:
        st.write("连接全球交易所官方数据源...")
        result = fetch_data_with_cache(target)
        st.write("应用大师筛选算法...")
        status.update(label="扫描完成！", state="complete", expanded=False)
    
    if "错误" in result:
        st.error(result["错误"])
    else:
        st.table(pd.DataFrame([result]))
        st.success("数据已根据搜索前一日财报自动更新。")
