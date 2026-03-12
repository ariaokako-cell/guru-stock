import streamlit as st
import pandas as pd

st.set_page_config(page_title="大师选股 V19.0-决策团版", layout="wide")

# --- 核心逻辑：大师投票算法 ---
def master_voting_panel(data, master_score, red_flags):
    # 投票结果初始化
    votes = {}
    
    # 0. 张新民 (首席审计官) - 拥有一票否决权
    if red_flags:
        return {m: "❌ 否决 (财务存疑)" for m in ["巴菲特", "芒格", "费雪", "邓普顿", "格林布拉特", "马克思", "多尔西"]}
    
    # 1. 巴菲特 & 芒格 (质量派)
    if data['roe'] >= 20 and data['ocf_ni'] >= 1.2: votes["巴菲特"] = "👍 赞成"
    elif data['roe'] < 12: votes["巴菲特"] = "👎 避坑"
    else: votes["巴菲特"] = "➖ 持有"
    
    votes["芒格"] = "👍 赞成" if data['roe'] > 18 and data['debt_ratio'] < 30 else "➖ 持有"
    
    # 2. 费雪 (成长派)
    votes["费雪"] = "👍 赞成" if data['growth'] > 20 else "➖ 持有"
    
    # 3. 邓普顿 (逆向派)
    votes["邓普顿"] = "👍 赞成" if data['ey'] > 12 else "➖ 持有"
    
    # 4. 格林布拉特 (神奇公式)
    votes["格林布拉特"] = "👍 赞成" if data['ey'] > 15 else "👎 避坑"
    
    # 5. 霍华德·马克思 (风险派)
    votes["马克思"] = "👍 赞成" if data['ey'] > 10 else "👎 避坑"
    
    # 6. 帕特·多尔西 (护城河)
    votes["多尔西"] = "👍 赞成" if data['margin'] > 25 else "➖ 持有"
    
    return votes

# --- UI 界面：直接在主页显示输入 ---
st.title("🏛️ 大师灵魂决策委员会 V19.0")
st.markdown("### 第一步：请在下方直接录入财务数据")

# 主页面输入区 (不再隐藏在边栏)
c1, c2, c3 = st.columns(3)
with c1:
    ticker = st.text_input("公司简称", "示例公司")
    roe = st.number_input("ROE (%)", 15.0)
    margin = st.number_input("销售净利率 (%)", 20.0)
with c2:
    net_p = st.number_input("净利润 (亿)", 10.0)
    ocf = st.number_input("经营现金流 (亿)", 12.0)
    growth = st.number_input("营收增长率 (%)", 10.0)
with c3:
    ey = st.number_input("神奇收益率 (EBIT/EV %)", 8.0)
    debt_ratio = st.number_input("资产负债率 (%)", 40.0)
    cash_equity = st.number_input("现金/净资产 (倍)", 0.2)

# 执行分析
if st.button("🚀 启动大师委员会联合表决"):
    # 封存数据
    data_pkg = {
        'roe': roe, 'margin': margin, 'net_profit': net_p, 'ocf': ocf,
        'ocf_ni': ocf/net_p, 'growth': growth, 'ey': ey, 'debt_ratio': debt_ratio,
        'equity': 1, 'cash': cash_equity # 简化处理
    }
    
    # 张新民防火墙
    red_flags = []
    if ocf < net_p * 0.8: red_flags.append("利润含金量低")
    if cash_equity > 0.3 and debt_ratio > 50: red_flags.append("存贷双高风险")
    
    # 投票演算
    vote_results = master_voting_panel(data_pkg, 0, red_flags)
    
    st.divider()
    
    # 第二步：显示投票表
    st.subheader("🗳️ 大师委员会表决结果")
    vote_df = pd.DataFrame(list(vote_results.items()), columns=["投资大师", "最终表决意见"])
    st.table(vote_df)
    
    # 第三步：深度研报摘要
    st.subheader("🖋️ 联合会诊报告摘要")
    if red_flags:
        st.error(f"张新民首席审计官已行使‘一票否决权’。原因：{', '.join(red_flags)}。在真实性无法保障前，所有投资建议无效。")
    else:
        赞成票 = list(vote_results.values()).count("👍 赞成")
        st.write(f"在委员会的 7 位大师中，有 **{赞成票}** 位投出了赞成票。")
        if 赞成票 >= 4:
            st.success("结论：共识已达成。该股具备极强的‘确定性+安全边际’，建议列入核心观察池。")
        else:
            st.warning("结论：共识尚未达成。建议针对分歧点（如估值或成长性）进行二轮定性调研。")
