import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="大师灵魂评估 V21.0", layout="wide")

# --- 核心逻辑：情景分析与大师投票 ---
def master_board_v21(data_3y, avg_roe_10y, red_flags, moat_score):
    votes = {}
    latest = data_3y[0]
    is_turnaround = latest['roe'] < 10 and avg_roe_10y > 15
    
    # 张新民一票否决
    if red_flags:
        return {m: "❌ 否决 (财务地雷)" for m in ["巴菲特", "芒格", "邓普顿", "马克思", "费雪"]}, "🚨 财务质量危机"

    # 1. 巴菲特/芒格 (侧重：确定性与底蕴)
    if is_turnaround:
        votes["巴菲特"] = "➖ 持有 (观察护城河是否受损)"
        votes["芒格"] = "👎 避坑 (不喜欢泥潭里的生意)"
    elif latest['roe'] > 18:
        votes["巴菲特"] = "👍 赞成 (高质量持续)"
        votes["芒格"] = "👍 赞成 (简单、可理解)"
    
    # 2. 邓普顿/霍华德·马克思 (侧重：逆向与周期)
    if is_turnaround:
        votes["邓普顿"] = "👍 赞成 (极度悲观即是买点)"
        votes["马克思"] = "👍 赞成 (正在进入周期底部)"
    else:
        votes["马克思"] = "➖ 持有 (谨防自满情绪)"

    # 3. 费雪 (侧重：研发与未来)
    votes["费雪"] = "👍 赞成" if moat_score > 8 else "➖ 持有"

    mode_desc = "🦇 困境反转模式" if is_turnaround else "🦁 稳健价值模式"
    return votes, mode_desc

# --- UI 界面 ---
st.title("🏛️ 大师灵魂评估系统 V21.0")
st.caption("逻辑：长短期时空穿透 | 张新民财务防火墙 | 格林沃尔德 EPV 估值")

# 主界面数据录入
st.subheader("第一步：录入财务‘快照’与‘底蕴’")
col_a, col_b = st.columns(2)
with col_a:
    ticker = st.text_input("公司简称", "某白马股")
    curr_p = st.number_input("当前股价", value=100.0)
    avg_roe_10y = st.number_input("10年平均 ROE (%)", value=20.0, help="这是该公司的‘历史底蕴’")
with col_b:
    moat_score = st.slider("护城河/定性优势评分 (1-10)", 1, 10, 7)
    shares = st.number_input("总股本 (亿股)", value=10.0)
    ebit = st.number_input("最新 EBIT (亿)", value=10.0)

st.subheader("第二步：录入近三年动态数据 (2025-2023)")
years = ["2025(新)", "2024", "2023"]
data_3y = []
cols = st.columns(3)
for i, yr in enumerate(years):
    with cols[i]:
        data_3y.append({
            "roe": st.number_input(f"ROE (%) - {yr}", value=15.0, key=f"r_{i}"),
            "net_p": st.number_input(f"净利润 (亿) - {yr}", value=10.0, key=f"p_{i}"),
            "ocf": st.number_input(f"经营现金流 (亿) - {yr}", value=11.0, key=f"o_{i}"),
            "total_a": st.number_input(f"总资产 (亿) - {yr}", value=100.0, key=f"a_{i}"),
            "debt_r": st.number_input(f"负债率 (%) - {yr}", value=40.0, key=f"d_{i}"),
            "cash": st.number_input(f"货币资金 (亿) - {yr}", value=20.0, key=f"c_{i}"),
            "equity": st.number_input(f"净资产 (亿) - {yr}", value=50.0, key=f"e_{i}")
        })

if st.button("🚀 执行全周期灵魂评估"):
    # 1. 张新民审计 (防火墙)
    latest = data_3y[0]
    red_flags = []
    if latest['ocf'] < latest['net_p'] * 0.7: red_flags.append("最新利润含金量极差")
    if latest['cash'] > latest['equity'] * 0.4 and latest['debt_r'] > 60: red_flags.append("疑似存贷双高舞弊")
    
    # 2. 场景判定与大师投票
    votes, mode = master_board_v21(data_3y, avg_roe_10y, red_flags, moat_score)
    
    # 3. 格林沃尔德估值 (EPV)
    # WACC 设定为机会成本底线 8%
    wacc = 0.08
    adj_ebit = max(ebit, (avg_roe_10y/100 * latest['equity'])) # 如果在爬坡，取均值盈利能力
    epv = (adj_ebit * 0.75) / wacc
    iv = (epv - (latest['total_a'] * latest['debt_r']/100 - latest['cash'])) / shares
    
    st.divider()
    
    # 结果展示
    st.subheader(f"分析结论：{mode}")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("大师综合判定", "买入" if "👍" in str(votes) and not red_flags else "观察/回避")
    c2.metric("内在价值 (EPV)", f"{iv:.2f}")
    c3.metric("安全边际", f"{((iv-curr_p)/iv*100):.1f}%")

    st.subheader("🗳️ 大师委员会投票记录")
    st.table(pd.DataFrame(list(votes.items()), columns=["分析流派", "针对当前场景的表决"]))
    
    if red_flags:
        st.error(f"张新民防火墙警报：{', '.join(red_flags)}")
    
    with st.expander("📄 查看大师灵魂评述"):
        if "困境反转" in mode:
            st.write("**约翰·邓普顿**：‘目前的财务报表是一场灾难，但这正是廉价买入卓越底蕴的机会。’")
            st.write("**张新民**：‘虽然利润难看，但只要经营现金流没有断裂，企业就有反击的本钱。’")
        else:
            st.write("**巴菲特**：‘稳定的数字说明了一切。我们不需要聪明的反转，我们只需要平庸的持续。’")
