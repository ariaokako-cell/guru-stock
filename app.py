import streamlit as st
import pandas as pd

st.set_page_config(page_title="大师灵魂决策系统 V12.0", layout="wide")

# --- UI 头部 ---
st.title("🏛️ 大师核心决策演算系统 V12.0")
st.markdown("### 模式：数据驱动版 (避开封锁，直达决策核心)")
st.info("💡 请从巨潮、港交所或雪球财报摘要中，输入以下核心指标：")

# --- 数据输入区 ---
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        roe = st.number_input("1. 净资产收益率 ROE (%)", value=15.0)
        net_margin = st.number_input("2. 销售净利率 (%)", value=10.0)
    with col2:
        asset_turnover = st.number_input("3. 资产周转率 (次)", value=1.0)
        fcf_ni_ratio = st.number_input("4. 收益质量 (经营现金流/净利润)", value=1.0)
    with col3:
        rev_growth = st.number_input("5. 营收年增长率 (%)", value=12.0)
        ey_magic = st.number_input("6. 神奇收益率 (EBIT/EV %)", value=8.0)

# --- 核心演算逻辑 ---
def calculate_master_verdict(roe, margin, turnover, cash_q, growth, magic):
    # 1. 质量评分 (45%) - 巴菲特/芒格/多尔西
    # 核心：高ROE + 高现金流质量
    q_score = (roe * 0.6 + (cash_q * 10) * 0.4) 
    
    # 2. 价值评分 (35%) - 格林布拉特/马克思
    # 核心：神奇收益率
    v_score = (magic * 1.0) 
    
    # 3. 动力评分 (20%) - 费雪/邓普顿
    # 核心：成长性
    g_score = (growth * 1.0)
    
    # 综合加权 (归一化处理)
    final = (q_score * 0.45 + v_score * 3.5 * 0.35 + g_score * 0.20)
    return final, q_score, v_score, g_score

if st.button("开始大师灵魂演算"):
    final_score, q, v, g = calculate_master_verdict(roe, net_margin, asset_turnover, fcf_ni_ratio, rev_growth, ey_magic)
    
    st.divider()
    st.metric("大师综合价值分 (Master Score)", f"{final_score:.1f}")

    # --- 大师点评区 (定性衡量的数字化体现) ---
    st.subheader("🖋️ 大师灵魂评述")
    
    # 巴菲特/芒格 视角
    with st.expander("巴菲特 & 查理·芒格 的评价", expanded=True):
        if roe > 20 and fcf_ni_ratio > 1.1:
            st.success("巴菲特：‘这是一家拥有深厚护城河的公司，它的利润不仅仅是会计数字，更是实实在在的现金。就像喜诗糖果一样，它值得我们长期坚守。’")
        elif roe < 10:
            st.error("芒格：‘这种回报率还不如去存银行。如果一个生意需要持续投入大量资产却只能产生微薄利润，那简直是在自掘坟墓。’")
        else:
            st.warning("巴菲特：‘生意不错，但还没到让人兴奋的地步。我们要寻找的是那种无需增加资本投入就能持续增长的特种生意。’")

    # 格林布拉特 视角
    with st.expander("乔尔·格林布拉特 的评价"):
        if ey_magic > 15:
            st.success("格林布拉特：‘神奇公式在这里闪闪发光！它不仅好，而且非常便宜。这正是我们寻找的被市场错杀的珍珠。’")
        else:
            st.info("格林布拉特：‘价格只能算合理，尚未进入我们的‘击球区’。记住，好公司如果不便宜，就不是一笔好投资。’")

    # 费雪 & 邓普顿 视角
    with st.expander("菲利普·费雪 & 约翰·邓普顿 的评价"):
        if rev_growth > 25:
            st.success("费雪：‘我在它身上看到了未来的影子！管理层极具远见，这种增长势头正是超级大牛股的雏形。’")
        else:
            st.info("邓普顿：‘即便增长缓慢，只要现在的悲观情绪足够重，反转的机会就一定存在。’")

    # 杜邦分析结论
    st.info(f"📊 杜邦深度分析：当前ROE为{roe}%。其中，净利率对盈利的贡献权重较高，说明产品具备{ '强定价权' if net_margin > 20 else '平均竞争水平' }。")
