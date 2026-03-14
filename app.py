import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="大师灵魂扫射雷达 V28.0", layout="wide")

# --- 定义：主板与港股通核心扫描宇宙 (选取各行业最具代表性的标的) ---
ELITE_UNIVERSE = [
    # A股主板 (消费/白马/资源/制造)
    "600519.SS", "601318.SS", "600036.SS", "600585.SS", "601888.SS", "000333.SZ", 
    "603288.SS", "600276.SS", "000651.SZ", "600887.SS", "600030.SS", "601012.SS",
    # 港股通 (互联网/医药/金融/消费)
    "00700.HK", "09988.HK", "03690.HK", "01211.HK", "02318.HK", "01810.HK", 
    "00941.HK", "00883.HK", "00005.HK", "02020.HK", "01801.HK", "09618.HK"
]

# --- 大师决策逻辑：核心算法 ---
def master_council_valuation(ticker, info):
    # 1. 抓取张新民关心的底层数据
    ocf = info.get('operatingCashflow', 0)
    net_p = info.get('netIncomeToCommon', 1)
    ocf_ni = ocf / net_p if net_p != 0 else 0
    
    # 2. 抓取巴菲特关心的ROE与毛利
    roe = info.get('returnOnEquity', 0)
    margin = info.get('grossMargins', 0)
    
    # 3. 抓取格林沃尔德的估值参数 (2026年3月基准)
    rf = 0.025
    ebit = info.get('ebitda', 0) * 0.8
    wacc = rf + (0.04 if roe > 0.18 else 0.07)
    epv = (ebit * 0.75) / wacc
    net_debt = info.get('totalDebt', 0) - info.get('totalCash', 0)
    shares = info.get('sharesOutstanding', 1)
    iv = (epv - net_debt) / shares if shares > 0 else 0
    price = info.get('currentPrice', 1)
    safety_margin = (iv - price) / iv if iv > 0 else -1.0
    
    # 4. 抓取费雪的增长动能
    rev_growth = info.get('revenueGrowth', 0)

    # --- 决策矩阵 ---
    council_vote = 0
    if ocf_ni > 1.0: council_vote += 2  # 张新民：现金流是灵魂
    if roe > 0.15: council_vote += 2    # 巴菲特：ROE是门槛
    if safety_margin > 0.2: council_vote += 2 # 格林沃尔德：便宜是硬道理
    if rev_growth > 0.1: council_vote += 1    # 费雪：增长是加分项
    if margin > 0.3: council_vote += 1        # 多尔西：护城河检测
    
    return {
        "council_vote": council_vote,
        "safety_margin": safety_margin,
        "ocf_ni": ocf_ni,
        "roe": roe,
        "name": info.get('shortName', ticker),
        "rev_growth": rev_growth,
        "iv": iv
    }

st.title("🏛️ 大师灵魂扫射系统 V28.0")
st.caption("【主板 + 港股通】巡航模式 | 排除科创与创业板 | 张新民财务防火墙前置")

if st.button("📡 启动主板全量扫射"):
    scan_results = []
    with st.status("正在扫射 A/H 核心主板资产...", expanded=True) as status:
        for i, ticker in enumerate(ELITE_UNIVERSE):
            try:
                stock = yf.Ticker(ticker)
                res = master_council_valuation(ticker, stock.info)
                if res['ocf_ni'] > 0.8: # 张新民防火墙：利润含金量不及格的一律不显示
                    scan_results.append({
                        "代码": ticker,
                        "名称": res['name'],
                        "大师共识分": res['council_vote'],
                        "ROE": f"{res['roe']*100:.1f}%",
                        "安全边际": f"{res['safety_margin']*100:.1f}%",
                        "含金量": f"{res['ocf_ni']:.2f}",
                        "IV": res['iv']
                    })
            except: continue
        status.update(label="扫射完成！正在按大师共识评分排列...", state="complete", expanded=False)
    
    # 排序并展示前 5
    top_picks = pd.DataFrame(scan_results).sort_values(by="大师共识分", ascending=False).head(5)
    
    st.subheader("🏆 大师委员会筛选：当前【最值得投资】的前 5 席")
    st.table(top_picks.drop(columns=['IV']))

    # --- 深度研报区 ---
    st.divider()
    st.subheader("🖋️ 精选标的深度剖析")
    for _, row in top_picks.iterrows():
        with st.expander(f"查看 {row['名称']} ({row['代码']}) 的大师辩论"):
            st.write(f"**🛡️ 张新民审计**：该股利润含金量为 {row['含金量']}，现金流表现稳健，无虚假利润嫌疑。")
            st.write(f"**📈 巴菲特评价**：{row['ROE']} 的 ROE 说明了其商业模式在主板中的卓越性。")
            st.write(f"**💰 格林沃尔德**：当前内在价值估算为 {row['IV']:.2f}。对比市价，安全边际达 {row['安全边际']}。")
            
            # 动态建议
            if "HK" in row['代码']:
                st.info("💡 港股提示：该股属于港股通，需关注汇率波动及南向资金流向。")
            else:
                st.info("💡 A股提示：主板蓝筹标的，适合作为核心资产配置。")

st.divider()
st.info("💡 逻辑：我们只在大树下寻找阴凉。本程序已自动过滤了不确定性较高的创业板和科创板，确保每一份建议都来自具备‘历史厚度’的企业。")
