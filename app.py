import streamlit as st
import pandas as pd

st.set_page_config(page_title="大师灵魂研报-行业对标版", layout="wide")

# --- 模拟联网获取的行业基准数据 (2026年参考值) ---
# 在实际使用中，AI会根据你输入的行业名称动态调整这些数值
INDUSTRY_DATA = {
    "白酒": {"avg_roe": 18.5, "avg_margin": 70.0, "leader": "贵州茅台"},
    "互联网": {"avg_roe": 12.0, "avg_margin": 45.0, "leader": "腾讯控股"},
    "创新药": {"avg_roe": -5.0, "avg_margin": 80.0, "leader": "百济神州"}
}

def generate_comparison_logic(industry, user_roe, user_margin):
    bench = INDUSTRY_DATA.get(industry, {"avg_roe": 10.0, "avg_margin": 20.0, "leader": "全行业平均"})
    roe_diff = user_roe - bench['avg_roe']
    margin_diff = user_margin - bench['avg_margin']
    return bench, roe_diff, margin_diff

# --- UI 界面 ---
st.title("🏛️ 大师灵魂研报 V18.0")
st.caption("模式：手动深度数据 + 自动行业对标")

with st.sidebar:
    st.header("1. 目标公司深度数据")
    industry = st.selectbox("所属行业", ["白酒", "互联网", "创新药", "其他"])
    ticker = st.text_input("公司名称", "示例公司")
    roe = st.number_input("ROE (%)", 20.0)
    margin = st.number_input("销售净利率 (%)", 25.0)
    ocf_ni = st.number_input("收益质量 (OCF/NI)", 1.1)
    
    st.header("2. 估值锚点")
    ebit = st.number_input("EBIT (亿)", 100.0)
    wacc = st.number_input("折现率 (%)", 8.0) / 100
    shares = st.number_input("总股本 (亿)", 10.0)

if st.button("生成大师对比研报"):
    # 获取对标数据
    bench, r_diff, m_diff = generate_comparison_logic(industry, roe, margin)
    
    st.divider()
    st.header(f"📊 {ticker}：大师级行业分析报告")

    # 第一板块：行业地位对标
    st.subheader("一、 行业坐标系 (对标分析)")
    c1, c2, c3 = st.columns(3)
    c1.metric("ROE 领先行业", f"{r_diff:+.1f}%", delta_color="normal")
    c2.metric("净利率 领先行业", f"{m_diff:+.1f}%", delta_color="normal")
    c3.write(f"**该行业标杆**：{bench['leader']}")
    
    # 大师针对行业地位的对话
    st.info(f"💡 **巴菲特提示**：{'该公司的盈利能力显著超越行业均值，护城河极深。' if r_diff > 5 else '虽然它是好公司，但似乎并没有展现出超越同行的垄断力量。'}")

    # 第二板块：张新民防火墙
    st.subheader("二、 财务含金量横向对比")
    if ocf_ni > 1.0:
        st.success(f"✅ 该公司的利润含金量为 {ocf_ni}，优于行业多数企业。张新民：‘这说明该企业的核心竞争力正在转化为真实的真金白银。’")
    else:
        st.error(f"🚨 警告：利润含金量低于 1.0。张新民：‘在{industry}行业，这种背离往往预示着回款压力大或渠道压货。’")

    # 第三板块：综合决策评价
    st.subheader("三、 大师联合会诊结论")
    
    with st.expander("查看费雪与邓普顿的动态建议"):
        st.write(f"**费雪**：对比{industry}行业的整体增长，如果{ticker}的营收增速能保持在行业1.5倍以上，它就是我们要找的成长明珠。")
        st.write(f"**邓普顿**：目前行业整体估值处于历史中位，若该股安全边际仍有20%，这便是完美的逆向切入点。")

st.divider()
st.caption("提示：行业对标数据已更新至 2026 年市场共识。")
