
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
from extract_speed_data import parse_fcd_xml

st.set_page_config(page_title="速度热力图", page_icon="🔥")

st.header("🚗 SUMO 仿真 - 车辆速度热力图")

# 自动读取仿真数据
fcd_file = "data/output_fcd.xml"
df = parse_fcd_xml(fcd_file)

# 选择时间步
time_steps = sorted(df['time'].unique())
selected_time = st.slider("选择仿真时间", float(min(time_steps)), float(max(time_steps)), step=1.0)
filtered_df = df[df['time'] == selected_time]

if filtered_df.empty:
    st.warning("当前时间步没有车辆数据。")
    st.stop()

# 地图可视化
m = folium.Map(location=[filtered_df.latitude.mean(), filtered_df.longitude.mean()], zoom_start=13)
heat_data = filtered_df[["latitude", "longitude", "speed"]].values.tolist()
HeatMap(heat_data, radius=10, blur=8).add_to(m)
st_folium(m, height=500)

# 显示表格（可选）
with st.expander("查看原始数据"):
    st.dataframe(filtered_df)
