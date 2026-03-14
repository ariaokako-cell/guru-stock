import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="大师灵魂雷达 V25.1", layout="wide")

# --- 核心逻辑：大师决策与行业适配 ---
def master_board_logic(ticker, info):
    # 1. 宏观与基础参数
    rf = 0.025 # 2026年3月基准
    roe = info.get('returnOnEquity', 0)
    rev_growth = info.get('revenueGrowth', 0)
    margin = info.get('grossMargins', 0)
    ocf_ni = info.get('operatingCashflow', 0) / info.get('netIncomeToCommon', 1) if info.get('netIncomeToCommon', 0) != 0 else 0
    pb = info.get('priceToBook', 2)
    
    # 2. 行业识别与权重分配
    # 判定：信达生物(01801)、迈瑞(300760)等属于科技/生物
    is_growth = any(x in ticker for x in ["01801", "300760", "00700", "09988"])
    # 判定：海螺水泥(600585)等属于周期
    is_cycle = any(x in ticker for x in ["600585", "600019", "01171"])

    # 3. 大师投票逻辑
    votes = {}
    # 巴菲特 & 芒格：看重稳健，对困境公司谨慎
    if roe > 0.18 and not is_growth: votes["巴菲特"] = "👍 赞成 (确定性极高)"
    elif is_growth and rev_growth > 0.3: votes["巴菲特"] = "➖ 观察 (商业模式优秀但太贵)"
    else: votes["巴菲特"] = "👎 避坑 (回报率不足)"

    # 费雪：看重研发与未来
    votes["费雪"] = "👍 赞成 (高增长动能)" if rev_growth > 0.2 else "➖ 观察"

    # 格林沃尔德：看EPV安全边际
    wacc = rf + (0.04 if roe > 0.15 else 0.08)
    ebit = info.get('ebitda', 0) * 0.8
    epv = (ebit * 0.75) / wacc
    iv = (epv - (info.get('totalDebt', 0) - info.get('totalCash', 0))) / info.get('sharesOutstanding', 1)
    safety_margin = (iv - info.get('currentPrice', 1)) / iv if iv > 0 else 0
    votes["格林沃尔德"] = "👍 赞成 (具备安全边际)" if safety_margin > 0.2 else "👎 避坑 (估值过高)"

    # 张新民：一票否决权
    audit_ok = ocf_ni > 0.8
    votes["张新民"] = "✅ 通过" if audit_ok else "❌ 否决 (利润含金量低)"

    # 综合评分 (逻辑：根据行业特质动态调整)
    if is_growth:
        score = (rev_growth * 0.5 + margin * 0.3 + safety_margin * 0.2) * 100
    elif is_cycle:
        score = ( (1/pb) * 0.4 + ocf_ni * 0.3 + safety_margin * 0.3 ) * 100
    else:
        score = (roe * 0.4 + margin * 0.3 + safety_margin * 0.3) * 100

    return round(score, 2), votes, safety_margin, audit_ok

# --- 扫描池 (包含你关心的所有标的) ---
SCAN_POOL = ["600519.SS", "00700.HK", "000333.SZ", "01801.HK", "600585.SS", "300760.SZ", "603288.SS"]

st.title("🏛️ 大师灵魂雷达 V25.1")
st.caption("【Bug修复版】已自动适配信达生物、迈瑞医疗、海螺水泥等不同类型标的评价逻辑")

if st.button("📡 执行多维权重雷达扫描"):
    results = []
    progress = st.progress(0)
    
    for i, ticker in enumerate(SCAN_POOL):
        try:
            stock = yf.Ticker(ticker)
            score, votes, margin, audit = master_board_logic(ticker, stock.info)
            results.append({
                "代码": ticker,
                "名称": stock.info.get('shortName', ticker),
                "大师综合分": score,
                "安全边际": f"{margin*100:.1f}%",
                "张新民审计": "通过" if audit else "拒绝",
                "votes": votes
            })
        except Exception as e:
            continue
        progress.progress((i + 1) / len(SCAN_POOL))
    
    df = pd.DataFrame(results).sort_values(by="大师综合分", ascending=False)
    
    st.subheader("🏆 2026年3月大师推荐排位")
    st.table(df.drop(columns=['votes']))
    
    st.divider()
    st.subheader("🖋️ 针对性大师灵魂评述")
    for item in results:
        with st.expander(f"查看 {item['名称']} ({item['代码']}) 的投票详情"):
            v = item['votes']
            st.write(f"**巴菲特/芒格**: {v['巴菲特']}")
            st.write(f"**费雪**: {v['费雪']}")
            st.write(f"**格林沃尔德**: {v['格林沃尔德']}")
            st.write(f"**张新民审计**: {v['张新民']}")
            
            # 针对性逻辑解释
            if "01801" in item['code']:
                st.info("💡 特别提示：信达生物目前处于‘费雪模式’。虽然ROE和利润含金量可能受研发投入拖累，但其营收增速和护城河是核心观察点。")
            elif "600585" in item['code']:
                st.info("💡 特别提示：海螺水泥处于‘周期底部分析’。重点关注PB和资产重置成本，而非当前的净利润。")
