import streamlit as st
import pydeck as pdk
import json
import time
from parse_fcd import parse_fcd
import subprocess
import sys

st.set_page_config(layout="wide")
st.title("🚗 SUMO OSM 交通轨迹动画演示")

# Initialize session state
if "frame" not in st.session_state:
    st.session_state.frame = 0
if "is_playing" not in st.session_state:
    st.session_state.is_playing = False

# @st.cache_data
def readbbox():
    # 1. 从 osm_bbox.json 读取边界
# Area settings
    try:
        with open("./osm_bbox.json", "r") as f:
            default_bbox = json.load(f)
    except FileNotFoundError:
        # 如果文件不存在，使用默认值
        default_bbox = {
            "north": 43.8280,
            "south": 43.8220,
            "east":  87.6255,
            "west":  87.6180
        }
        print("警告：未找到 osm_bbox.json，已使用默认边界。")
    return default_bbox

default_bbox=readbbox()

# st.write(default_bbox)

# default_bbox = {"north": 43.8280, "south": 43.8220, "east": 87.6255, "west": 87.6180}
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
        # if process.stderr:
        #     st.error("脚本有错误输出：")
        #     st.code(process.stderr, language='text')

    except subprocess.CalledProcessError as e:
        st.error(f"独立脚本执行失败，返回码：{e.returncode}")
        st.code(e.stdout, language='text')
        st.code(e.stderr, language='text')
    except FileNotFoundError:
        st.error("错误：找不到 'run_simulation.py' 文件。请确保它在正确的路径下。")

# Cache trajectory data loading
# @st.cache_data
def get_fcd_data(fcd_path, net_path):
    return parse_fcd(fcd_path, net_path)

# Load trajectory data
traj = get_fcd_data("./data/output_fcd.xml", "./data/map.net.xml")
vehicle_ids = list(traj.keys())
timestamps = sorted(set(t for v in traj.values() for t, _, _ in v))
max_time = int(max(timestamps)) if timestamps else 200

# Multi-vehicle selection - placed before map and slider as it also determines what's displayed on the map
selected_vehicles = st.sidebar.multiselect("选择显示的车辆", vehicle_ids, default=vehicle_ids[:])

# Time slider - placed before map and buttons as it also determines what's displayed on the map
frame = st.sidebar.slider("当前时间", 0, max_time, st.session_state.frame, key="frame_slider")

# --- Create Pydeck map and add trajectories ---
# Data preparation for Pydeck layers
lines_data = []
points_data = []
colors = [[255, 0, 0], [0, 0, 255], [0, 128, 0], [128, 0, 128], [255, 165, 0], [139, 0, 0], [255, 192, 203], [95, 158, 160], [0, 100, 0], [144, 238, 144]]

for i, vid in enumerate(selected_vehicles):
    if vid in traj:
        history = [(lon, lat) for t, lat, lon in traj[vid] if t <= frame] # Pydeck expects [longitude, latitude]
        if history:
            color = colors[i % len(colors)]

            # For trajectory lines
            if len(history) > 1:
                for j in range(len(history) - 1):
                    lines_data.append({
                        "path": [history[j], history[j+1]],
                        "color": color,
                        "vehicle_id": vid
                    })

            # For current vehicle position (points)
            current_pos = history[-1]
            points_data.append({
                "position": current_pos,
                "color": color,
                "vehicle_id": vid,
                "time": frame
            })

# Define Pydeck layers
layers = []

if lines_data:
    line_layer = pdk.Layer(
        "PathLayer",
        data=lines_data,
        get_path="path",
        get_color="color",
        get_width=2,
        pickable=True,
        auto_highlight=True
    )
    layers.append(line_layer)

if points_data:
    point_layer = pdk.Layer(
        "ScatterplotLayer",
        data=points_data,
        get_position="position",
        get_color="color",
        get_radius=10,
        pickable=True,
        auto_highlight=True,
        tooltip={"text": "车辆ID: {vehicle_id}\n时间: {time}\n经纬度: {position}"} # Tooltip requires string formatting and @array for coordinates
    )
    layers.append(point_layer)

# Set the initial view state
view_state = pdk.ViewState(
    latitude=(north + south) / 2,
    longitude=(east + west) / 2,
    zoom=14, # Pydeck zoom levels might differ from Folium
    pitch=0,
)
# chart_col, map_col = st.columns([1, 1])
# map_area = map_col.empty()
map_area = st.empty()
# Render the Pydeck map
r = pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    tooltip={"html": "<b>车辆ID:</b> {vehicle_id}<br><b>时间:</b> {time}<br><b>经纬度:</b> {position}", "type": "html"}, # Global tooltip for interactivity
    # map_style="mapbox://styles/mapbox/light-v9" # You might need a Mapbox token for some styles
)
map_area.pydeck_chart(r)
# st.pydeck_chart(r)

st.sidebar.subheader("播放控制")
# Column layout within the sidebar
col_play, col_pause, col_replay = st.sidebar.columns(3)
with col_play:
    if st.button("▶️ 播放"):
        st.session_state.is_playing = True
with col_pause:
    if st.button("⏸️ 暂停"):
        st.session_state.is_playing = False
with col_replay:
    if st.button("⏪ 重新播放"):
        st.session_state.frame = 0
        st.session_state.is_playing = True
        st.rerun()

# Playback logic control
if st.session_state.is_playing:
    st.session_state.frame += 1
    # if st.session_state.frame > max_time:
        # st.session_state.frame = 0
        # st.session_state.is_playing = False
    time.sleep(1) # Adjusted sleep for smoother animation with pydeck. You might need to experiment.
    st.rerun()