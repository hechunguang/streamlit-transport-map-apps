import xml.etree.ElementTree as ET
import pyproj
from sumolib.net import readNet

def get_fcd_data(fcd_file, net_file):
    """
    从 SUMO fcd.xml 和 net.xml 文件中提取车辆轨迹数据（包含速度）并转为经纬度。

    返回:
        traj: dict, vehicle_id -> List of (time, lon, lat, speed)
    """
    # 读取坐标系投影信息
    # net = ET.parse(net_file).getroot()
    # conv = net.find("location")
    # if conv is None:
    #     raise ValueError("location 标签到 net.xml 中未找到")
    # x_orig = float(conv.attrib["convBoundary"].split(",")[0])
    # y_orig = float(conv.attrib["convBoundary"].split(",")[1])
    # proj_str = conv.attrib.get("projParameter", "+proj=utm +zone=45 +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
    # proj = pyproj.Proj(proj_str)

    # 解析 FCD 文件
    tree = ET.parse(fcd_file)
    root = tree.getroot()
    net = readNet(net_file)
    traj = {}

    for timestep in root.findall("timestep"):
        time = float(timestep.attrib["time"])
        for vehicle in timestep.findall("vehicle"):
            veh_id = vehicle.attrib["id"]
            x = float(vehicle.attrib["x"])
            y = float(vehicle.attrib["y"])
            speed = float(vehicle.attrib["speed"])

            # lon, lat = proj(x + x_orig, y + y_orig, inverse=True)
            lon, lat = net.convertXY2LonLat(x, y)
            traj.setdefault(veh_id, []).append((time, lon, lat, speed))

    return traj

