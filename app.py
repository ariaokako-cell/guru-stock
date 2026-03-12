import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="大师灵魂评估 V22.0-自动审计版", layout="wide")

# --- 核心逻辑：大师自动护城河审计 ---
def master_moat_audit(df, avg_roe_10y):
    # 逻辑：巴菲特看毛利率稳定性
    margin_std = df['margin'].std() if 'margin' in df.columns else 5.0
    # 逻辑：多尔西看超额收益 (假设WACC为8%)
    excess_return = avg_roe_10y - 8.0
    
    # 综合判定护城河分数 (1-10)
    # 基础分来自长期ROE，修正分来自波动率
    base_moat = (avg_roe_10y / 3) 
    stability_penalty = max(0, margin_std * 0.5)
    final_moat = min(10, max(1, base_moat - stability_penalty))
    
    # 大师评述生成
    if final_moat > 7.5:
        verdict = "💎 钻石级护城河：长期极高且稳健的资本回报，显示出极强的定价权。"
    elif final_moat > 5:
        verdict = "🧱 宽阔护城河：具备明显的行业竞争优势，但需关注边际竞争。"
    else:
        verdict = "⌛ 窄护城河/无护城河：盈利能力不稳定，可能正处于剧烈的同质化竞争中。"
    
    return final_moat, verdict

# --- UI 界面 ---
st.title("🏛️ 大师灵魂评估系统 V22.0")
st.caption("逻辑：大师自动审计 | 财务揭示模型 | 避开主观偏见")

# 主界面数据录入
st.subheader("第一步：录入财务底蕴与最新环境")
c1, c2, c3 = st.columns(3)
with c1:
    ticker = st.text_input("公司简称", "示例白马")
    curr_p = st.number_input("当前股价", value=100.0)
with c2:
    avg_roe_10y = st.number_input("10年平均 ROE (%)", value=20.0)
    ebit = st.number_input("最新 EBIT (亿)", value=10.0)
with c3:
    shares = st.number_input("总股本 (亿股)", value=10.0)
    net_debt = st.number_input("净债务 (亿)", value=5.0)

st.subheader("第二步：录入近三年核心数据 (2025-2023)")
years = ["2025(新)", "2024", "2023"]
data_3y = []
cols = st.columns(3)
for i, yr in enumerate(years):
    with cols[i]:
        data_3y.append({
            "roe": st.number_input(f"ROE (%) - {yr}", value=15.0, key=f"r_{i}"),
            "margin": st.number_input(f"销售净利率 (%) - {yr}", value=12.0, key=f"m_{i}"),
            "ocf": st.number_input(f"经营现金流 (亿) - {yr}", value=11.0, key=f"o_{i}"),
            "net_p": st.number_input(f"净利润 (亿) - {yr}", value=10.0, key=f"p_{i}"),
            "equity": st.number_input(f"净资产 (亿) - {yr}", value=50.0, key=f"e_{i}"),
            "debt_r": st.number_input(f"负债率 (%) - {yr}", value=40.0, key=f"d_{i}")
        })

if st.button("🚀 启动大师自动审计与决策"):
    df_3y = pd.DataFrame(data_3y)
    
    # 1. 自动审计护城河
    moat_score, moat_verdict = master_moat_audit(df_3y, avg_roe_10y)
    
    # 2. 张新民防火墙
    latest = data_3y[0]
    red_flags = []
    if latest['ocf'] < latest['net_p'] * 0.8: red_flags.append("利润含金量严重不足")
    if latest['debt_r'] > 65: red_flags.append("负债率跨越安全红线")
    
    # 3. 格林沃尔德估值 (EPV)
    wacc = 0.08
    adj_ebit = max(ebit, (avg_roe_10y/100 * latest['equity'])) if moat_score > 6 else ebit
    iv = ( (adj_ebit * 0.75) / wacc - net_debt ) / shares

    # --- 结果展示 ---
    st.divider()
    st.header(f"📈 {ticker}：大师灵魂审计简报")
    
    c_m1, c_m2, c_m3 = st.columns(3)
    c_m1.metric("护城河成色 (系统算法)", f"{moat_score:.1f}/10")
    c_m2.metric("内在价值 (EPV)", f"{iv:.2f}")
    c_m3.metric("安全边际", f"{((iv-curr_p)/iv*100):.1f}%")
    
    st.info(f"🖋️ **大师委员会审计意见**：{moat_verdict}")
    
    if red_flags:
        st.error(f"🚫 **张新民说“不”**：{', '.join(red_flags)}。倒过来想，数据虽好，但底色存疑。")
    
    with st.expander("🔍 查看详细逻辑拆解"):
        st.write(f"**巴菲特/多尔西逻辑**：通过分析您录入的10年ROE({avg_roe_10y}%)及近3年净利率波动，我们反向推导出该公司的竞争优势。")
        st.write(f"**估值修正逻辑**：{'由于护城河评分较高，我们采用了标准收益能力进行估值。' if moat_score > 6 else '由于护城河较窄，我们仅按现状盈利能力保守估值。'}")

st.divider()
st.caption("注：V22.0 已移除主观滑块，所有评分均由大师根据财务数据间的勾稽关系自动计算。")
