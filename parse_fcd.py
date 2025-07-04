# import xml.etree.ElementTree as ET
# from sumolib.net import readNet

# def parse_fcd(fcd_file, net_file):
#     net = readNet(net_file)
#     tree = ET.parse(fcd_file)
#     root = tree.getroot()

#     traj = {}
#     for timestep in root.findall("timestep"):
#         for v in timestep.findall("vehicle"):
#             vid = v.attrib["id"]
#             x, y = float(v.attrib["x"]), float(v.attrib["y"])
#             lon, lat = net.convertXY2LonLat(x, y)
#             if vid not in traj:
#                 traj[vid] = []
#             traj[vid].append((lat, lon))
#     return traj


import xml.etree.ElementTree as ET
from sumolib.net import readNet

def parse_fcd(fcd_file, net_file):
    net = readNet(net_file)
    tree = ET.parse(fcd_file)
    root = tree.getroot()

    traj = {}
    for timestep in root.findall("timestep"):
        t = float(timestep.attrib["time"])
        for v in timestep.findall("vehicle"):
            vid = v.attrib["id"]
            x, y = float(v.attrib["x"]), float(v.attrib["y"])
            lon, lat = net.convertXY2LonLat(x, y)
            if vid not in traj:
                traj[vid] = []
            traj[vid].append((t, lat, lon))
    return traj
