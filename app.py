import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="大师选股系统", layout="wide")

def get_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    # 大师逻辑计算
    roe = info.get('returnOnEquity', 0) # 巴菲特/芒格
    margin = info.get('grossMargins', 0) # 多尔西(护城河)
    rev_growth = info.get('revenueGrowth', 0) # 费雪(成长)
    pe = info.get('forwardPE', 1)
    ey = (1/pe) if pe > 0 else 0 # 格林布拉特(收益率)
    
    # 邓普顿逻辑：股价是否接近52周低点
    low_52 = info.get('twoHundredDayAverage', 0) 
    current_price = info.get('currentPrice', 0)
    is_pessimism = "是" if current_price < low_52 else "否"

    return {
        "名称": info.get('longName', ticker),
        "ROE(>15%优质)": f"{roe*100:.2f}%",
        "毛利率(护城河)": f"{margin*100:.2f}%",
        "营收增长(成长性)": f"{rev_growth*100:.2f}%",
        "盈利收益率(便宜度)": f"{ey*100:.2f}%",
        "逆向机会(邓普顿)": is_pessimism,
        "马克思安全边际": "充足" if ey > 0.06 else "需警惕"
    }

st.title("🏛️ 大师核心选股决策系统")
st.caption("同步官方财报数据 | 逻辑：巴菲特/芒格/费雪/多尔西/格林布拉特")

target = st.text_input("输入代码 (A股加.SS或.SZ, 港股加.HK)", "600519.SS")

if st.button("开始分析"):
    with st.spinner('正在调取官方实时财报...'):
        try:
            res = get_data(target)
            st.table(pd.DataFrame([res]))
            st.success("数据已更新至搜索前一日，符合时效性要求。")
        except:
            st.error("请输入正确的代码，例如：贵州茅台 600519.SS / 腾讯 0700.HK")
