import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
from get_fcd_data_with_speed import get_fcd_data
import pandas as pd

st.set_page_config(page_title="速度热力图", page_icon="🔥")
st.set_page_config(layout="wide")
st.header("🚗 SUMO 仿真 - 车辆速度热力图（含路网背景）")

# ==== 加载轨迹数据 ====
fcd_path = "data/output_fcd.xml"
net_path = "data/map.net.xml"

try:
    traj = get_fcd_data(fcd_path, net_path)
except Exception as e:
    st.error(f"轨迹加载失败：{e}")
    st.stop()

vehicle_ids = list(traj.keys())
timestamps = sorted(set(t for v in traj.values() for t, _, _, _ in v))
max_time = int(max(timestamps)) if timestamps else 600

# ==== 时间选择 ====
selected_time = st.slider("选择仿真时间（秒）", 0, max_time, step=1)

# ==== 提取该时间的轨迹点 ====
heat_points = []
for veh_id, traj_list in traj.items():
    for t, lon, lat, speed in traj_list:
        if int(t) == selected_time:
            heat_points.append([lat, lon, speed])

if not heat_points:
    st.warning("当前时间无车辆活动")
    st.stop()

# ==== 创建地图 ====
m = folium.Map(location=[heat_points[0][0], heat_points[0][1]], zoom_start=15)
HeatMap(heat_points, radius=10, blur=8).add_to(m)

# ==== 展示地图 ====
st_folium(m, width=1000, height=600)

# ==== 数据表格（可选）====
with st.expander("查看当前时间轨迹数据"):
    df = pd.DataFrame(heat_points, columns=["lat", "lon", "speed"])
    st.dataframe(df)
