import streamlit as st
from streamlit_folium import st_folium
import folium
import json
import time
from parse_fcd import parse_fcd
import subprocess
import sys

st.set_page_config(layout="wide")
st.title("🚗 SUMO OSM 交通轨迹动画演示")

# 初始化会话状态
if "frame" not in st.session_state:
    st.session_state.frame = 0
if "is_playing" not in st.session_state:
    st.session_state.is_playing = False

# 区域设置
# st.sidebar.header("🗺️ OSM 区域选择")
default_bbox = {"north": 43.8280, "south": 43.8220, "east": 87.6255, "west": 87.6180}
north = st.sidebar.number_input("北纬", value=default_bbox["north"])
south = st.sidebar.number_input("南纬", value=default_bbox["south"])
east = st.sidebar.number_input("东经", value=default_bbox["east"])
west = st.sidebar.number_input("西经", value=default_bbox["west"])
if st.sidebar.button("更新边界"):
    with open("./osm_bbox.json", "w") as f:
        json.dump({"north": north, "south": south, "east": east, "west": west}, f)
    st.sidebar.success("区域已更新，请重新运行仿真")

st.sidebar.title("使用 subprocess 执行 Python 文件的 Streamlit 应用")

if st.sidebar.button("重新运行仿真"):
    st.sidebar.write("正在启动重新仿真脚本...")

    try:
        command = [sys.executable, "./run_simulation.py"]
        process = subprocess.run(command, capture_output=True, text=True, check=True)

        st.sidebar.success("仿真执行完成！")
        st.sidebar.code(process.stdout, language='text')
        if process.stderr:
            st.error("脚本有错误输出：")
            st.code(process.stderr, language='text')

    except subprocess.CalledProcessError as e:
        st.error(f"独立脚本执行失败，返回码：{e.returncode}")
        st.code(e.stdout, language='text')
        st.code(e.stderr, language='text')
    except FileNotFoundError:
        st.error("错误：找不到 'my_independent_script.py' 文件。请确保它在正确的路径下。")

# 缓存轨迹数据加载
@st.cache_data
def get_fcd_data(fcd_path, net_path):
    return parse_fcd(fcd_path, net_path)

# 加载轨迹数据
traj = get_fcd_data("./data/output_fcd.xml", "./data/map.net.xml")
vehicle_ids = list(traj.keys())
timestamps = sorted(set(t for v in traj.values() for t, _, _ in v))
max_time = int(max(timestamps)) if timestamps else 600

# 多车选择 - 放在地图和滑块之前，因为它也决定了地图上显示的内容
selected_vehicles = st.sidebar.multiselect("选择显示的车辆", vehicle_ids, default=vehicle_ids[:])

# 时间滑块 - 放在地图和按钮之前，因为它也决定了地图上显示的内容
frame = st.sidebar.slider("当前时间", 0, max_time, st.session_state.frame, key="frame_slider")

# --- 创建 Folium 地图并添加轨迹 ---
# 显示地图
m = folium.Map(location=[(north + south) / 2, (east + west) / 2], zoom_start=16)

# 绘制轨迹回放与当前位置
colors = ["red", "blue", "green", "purple", "orange", "darkred", "lightred", "cadetblue", "darkgreen", "lightgreen"] # 为不同车辆分配颜色

for i, vid in enumerate(selected_vehicles):
    if vid in traj:
        history = [(lat, lon) for t, lat, lon in traj[vid] if t <= frame]
        if history:
            color = colors[i % len(colors)] # 为每辆车分配颜色
            folium.PolyLine(history, color=color, weight=2, tooltip=f"{vid} - 轨迹").add_to(m)
            # folium.CircleMarker(location=history[-1], radius=6, color=color, fill=True, tooltip=f"{vid} - 当前位置").add_to(m)
            # 车辆当前位置的标记，tooltip 显示车辆ID
            folium.CircleMarker(
                location=history[-1],
                radius=6,
                color=color,
                fill=True,
                tooltip=f"车辆ID: {vid}",  # 明确显示车辆ID
                popup=f"<b>车辆ID:</b> {vid}<br><b>时间:</b> {frame}<br><b>经纬度:</b> {history[-1][0]:.4f}, {history[-1][1]:.4f}"
            ).add_to(m)

# 将地图放在按钮上方
st_folium(m, width=1000, height=600)

st.sidebar.subheader("播放控制")
# 侧边栏内的列布局
col_play, col_pause, col_replay = st.sidebar.columns(3)
with col_play:
    if st.button("▶️ 播放"): # st.button 不需要 st.sidebar.button，它会自动根据父容器决定位置
        st.session_state.is_playing = True
with col_pause:
    if st.button("⏸️ 暂停"):
        st.session_state.is_playing = False
with col_replay:
    if st.button("⏪ 重播"):
        st.session_state.frame = 0  # 重置时间帧到开始
        st.session_state.is_playing = True # 开始播放
        st.rerun() # 强制重新运行，更新滑块并开始播放

# # # --- 播放控制按钮 ---
# col1, col2, col3 = st.columns([1, 1, 4]) # 增加一列给新按钮

# with col1:
#     if st.sidebar.button("▶️ 播放"):
#         st.session_state.is_playing = True
# with col2:
#     if st.sidebar.button("⏸️ 暂停"):
#         st.session_state.is_playing = False
# with col3: # 新增的重新播放按钮
#     if st.sidebar.button("⏪ 重新播放"):
#         st.session_state.frame = 0  # 将帧数重置为起始
#         st.session_state.is_playing = True # 重新开始播放
#         st.rerun() # 强制重新运行以更新滑块和播放状态


# 播放逻辑控制
if st.session_state.is_playing:
    st.session_state.frame += 1
    # if st.session_state.frame > max_time: # 使用 > 而不是 >= 确保最后一帧也能显示
        # st.session_state.frame = 0 # 达到最大时间后，循环回0
        # st.session_state.is_playing = False # 如果不希望循环播放，则取消注释此行
    time.sleep(5) # 调整动画速度，可以考虑通过滑块让用户控制
    st.rerun()