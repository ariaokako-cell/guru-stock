import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="大师灵魂评估 V22.1", layout="wide")

# --- 核心逻辑不变，优化 UI 提示 ---
def master_moat_audit(df, avg_roe_10y):
    margin_std = df['margin'].std() if 'margin' in df.columns else 5.0
    base_moat = (avg_roe_10y / 3) 
    stability_penalty = max(0, margin_std * 0.5)
    final_moat = min(10, max(1, base_moat - stability_penalty))
    
    if final_moat > 7.5:
        verdict = "💎 钻石级护城河：高毛利且极度稳定，具备定价权。"
    elif final_moat > 5:
        verdict = "🧱 宽阔护城河：行业领先，具备竞争优势。"
    else:
        verdict = "⌛ 窄护城河/无护城河：盈利波动大，竞争惨烈。"
    return final_moat, verdict

st.title("🏛️ 大师灵魂评估系统 V22.1")
st.caption("注：点击输入框旁的 '?' 查看官方财务公式，确保数据选取准确。")

# --- 第一步：主页录入 ---
st.subheader("第一步：底蕴与估值核心")
c1, c2, c3 = st.columns(3)
with c1:
    ticker = st.text_input("公司简称", "示例企业")
    curr_p = st.number_input("当前股价", value=100.0)
with c2:
    avg_roe_10y = st.number_input("10年平均 ROE (%)", value=20.0, 
                                  help="公式：最近10年归母ROE的算术平均值")
    ebit = st.number_input("最新 EBIT (亿)", value=10.0, 
                           help="公式：净利润 + 所得税 + 利息支出")
with c3:
    shares = st.number_input("总股本 (亿股)", value=10.0)
    net_debt = st.number_input("净债务 (亿)", value=5.0, 
                               help="公式：(短借+长借+应付债券) - (货币资金+理财)")

# --- 第二步：三年数据 ---
st.subheader("第二步：近三年趋势 (2025-2023)")
years = ["2025(新)", "2024", "2023"]
data_3y = []
cols = st.columns(3)
for i, yr in enumerate(years):
    with cols[i]:
        st.write(f"**{yr} 年度**")
        data_3y.append({
            "roe": st.number_input(f"ROE (%) - {yr}", value=15.0, key=f"r_{i}", 
                                   help="公式：净利润 / 归母净资产"),
            "margin": st.number_input(f"销售净利率 (%) - {yr}", value=12.0, key=f"m_{i}", 
                                      help="公式：净利润 / 营业总收入"),
            "ocf": st.number_input(f"经营现金流 (亿) - {yr}", value=11.0, key=f"o_{i}", 
                                   help="来源：现金流量表-经营活动产生的现金流量净额"),
            "net_p": st.number_input(f"净利润 (亿) - {yr}", value=10.0, key=f"p_{i}"),
            "equity": st.number_input(f"净资产 (亿) - {yr}", value=50.0, key=f"e_{i}"),
            "debt_r": st.number_input(f"资产负债率 (%) - {yr}", value=40.0, key=f"d_{i}", 
                                      help="公式：总负债 / 总资产")
        })

if st.button("🚀 启动大师审计"):
    df_3y = pd.DataFrame(data_3y)
    moat_score, moat_verdict = master_moat_audit(df_3y, avg_roe_10y)
    latest = data_3y[0]
    
    # 张新民红旗检测
    red_flags = []
    if latest['ocf'] < latest['net_p'] * 0.8: red_flags.append("利润含金量低 (OCF/NI < 0.8)")
    
    # 格林沃尔德估值
    wacc = 0.08
    adj_ebit = max(ebit, (avg_roe_10y/100 * latest['equity'])) if moat_score > 6 else ebit
    iv = ( (adj_ebit * 0.75) / wacc - net_debt ) / shares

    st.divider()
    st.subheader(f"📊 {ticker} 深度审计结论")
    
    c_m1, c_m2, c_m3 = st.columns(3)
    c_m1.metric("护城河评分", f"{moat_score:.1f}/10")
    c_m2.metric("每股内在价值", f"{iv:.2f}")
    c_m3.metric("安全边际", f"{((iv-curr_p)/iv*100):.1f}%")
    
    st.info(f"🖋️ **委员会意见**：{moat_verdict}")
    if red_flags:
        st.error(f"🚫 **张新民否决原因**：{', '.join(red_flags)}")
