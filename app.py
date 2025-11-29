import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------- تنظیمات صفحه ----------------
st.set_page_config(
    page_title="Executive Factory Dashboard",
    layout="wide"
)

# ---------------- استایل حرفه ای ----------------
st.markdown("""
<style>
body {background-color: #F4F6F8;}
.block-container {padding-top: 1rem;}
.kpi-card {
    background-color: white;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 6px 14px rgba(0,0,0,0.06);
    text-align: center;
}
.kpi-title {
    font-size: 14px;
    color: #666;
}
.kpi-value {
    font-size: 26px;
    font-weight: bold;
}
.section {
    background-color: white;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 6px 14px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# ---------------- ساخت دیتای نمونه ----------------
np.random.seed(10)

days = pd.date_range("2024-01-01", periods=240)
lines = ["Line A", "Line B", "Line C"]

df = pd.DataFrame({
    "Date": np.tile(days, 3),
    "Line": np.repeat(lines, len(days)),
    "Total Production": np.random.randint(10000, 18000, len(days)*3),
    "Defects": np.random.randint(150, 700, len(days)*3),
    "Energy (kWh)": np.random.randint(6000, 11000, len(days)*3),
    "Downtime (h)": np.random.uniform(0.2, 6, len(days)*3),
})

df["Good"] = df["Total Production"] - df["Defects"]
df["Quality %"] = (df["Good"] / df["Total Production"])*100
df["Availability %"] = 100 - (df["Downtime (h)"] / 24 * 100)
df["Performance %"] = np.random.uniform(85, 98, len(df))
df["OEE %"] = (df["Quality %"] * df["Availability %"] * df["Performance %"]) / 10000

# ---------------- فیلتر ----------------
st.sidebar.title("⚙ تنظیمات داشبورد")

line = st.sidebar.selectbox("انتخاب خط تولید", ["All"] + lines)
period = st.sidebar.selectbox("انتخاب بازه", ["ماهانه", "فصلی", "سالانه"])

if line != "All":
    data = df[df["Line"] == line]
else:
    data = df.copy()

# Resample
if period == "ماهانه":
    group = "M"
elif period == "فصلی":
    group = "Q"
else:
    group = "Y"

summary = data.set_index("Date").groupby("Line").resample(group).mean().reset_index()

# ---------------- عنوان ----------------
st.title("🏭 داشبورد اجرایی مدیریت کارخانه بطری شیشه‌ای")

# ---------------- KPI ها ----------------
k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("میانگین تولید", f"{int(data['Total Production'].mean()):,}")
k2.metric("کیفیت %", f"{data['Quality %'].mean():.2f}")
k3.metric("بهره‌وری کلی (OEE)", f"{data['OEE %'].mean():.2f}")
k4.metric("توقف روزانه (ساعت)", f"{data['Downtime (h)'].mean():.2f}")
k5.metric("مصرف انرژی", f"{int(data['Energy (kWh)'].mean()):,} kWh")

st.markdown("---")

# ---------------- نمودارهای مقایسه‌ای ----------------
col1, col2 = st.columns(2)

with col1:
    fig_prod = px.line(summary, x="Date", y="Total Production", color="Line", title="روند تولید خطوط")
    st.plotly_chart(fig_prod, use_container_width=True)

with col2:
    fig_oee = px.line(summary, x="Date", y="OEE %", color="Line", title="روند بهره‌وری (OEE)")
    st.plotly_chart(fig_oee, use_container_width=True)

# ---------------- انرژی و ضایعات ----------------
col3, col4 = st.columns(2)

with col3:
    fig_energy = px.bar(summary, x="Date", y="Energy (kWh)", color="Line", title="مصرف انرژی خطوط", barmode="group")
    st.plotly_chart(fig_energy, use_container_width=True)

with col4:
    fig_def = px.area(summary, x="Date", y="Defects", color="Line", title="روند ضایعات")
    st.plotly_chart(fig_def, use_container_width=True)

# ---------------- توقف تولید ----------------
st.subheader("📊 رابطه توقف و عملکرد")

fig_down = px.scatter(
    data,
    x="Downtime (h)",
    y="Total Production",
    color="Line",
    size="Energy (kWh)",
    title="تأثیر توقف روی تولید"
)
st.plotly_chart(fig_down, use_container_width=True)

# ---------------- جدول ----------------
with st.expander("مشاهده دیتای خلاصه"):
    st.dataframe(summary)

st.success("داشبورد اجرایی با موفقیت بارگذاری شد ✅")
