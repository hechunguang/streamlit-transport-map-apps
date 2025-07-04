import os
import subprocess
import json
import requests

def download_osm_and_run():

    
    # 加载边界
    try:
        with open("./osm_bbox.json", "r") as f:
            bbox = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        bbox = {"north": 43.8280, "south": 43.8220, "east": 87.6255, "west": 87.6180}
        
    
    # 构建参数
    params = f"{bbox['west']},{bbox['south']},{bbox['east']},{bbox['north']}"
    
    # 准备文件路径
    os.makedirs("./data", exist_ok=True)
    osm_file = os.path.abspath("./data/map.osm.xml")
    
    try:
        # 使用Python内置请求
        url = f"http://overpass-api.de/api/map?bbox={params}"
        print(f"下载OSM数据区域: {params}")
        response = requests.get(url, timeout=60, stream=True)
        
        if response.status_code != 200:
            raise ConnectionError(f"服务器返回错误: HTTP {response.status_code}")
            
        with open(osm_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"成功下载 {os.path.getsize(osm_file)/1024:.1f}KB 数据到 {osm_file}")
        # return True
        
    except Exception as e:
        print(f"下载失败: {str(e)}")
        # return False

    net_file = "./data/map.net.xml"
    result = subprocess.run(
        ["netconvert", "--osm-files", osm_file, "-o", net_file],
        capture_output=True,
        text=True
    )

    # 打印返回码和输出
    print("Return code:", result.returncode)
    print("Standard Output:", result.stdout)
    print("Standard Error:", result.stderr)

    route_file = "./data/route.rou.xml"
    subprocess.run([
        "./randomTrips.py",
        "-n", net_file,
        "-r", route_file,
        "--trip-attributes", 'departLane="best"',
        "-e", "200"
    ])

    cfg = """<configuration>
    <input>
        <net-file value="./map.net.xml"/>
        <route-files value="./route.rou.xml"/>
    </input>
    <time>
        <end value="200"/>
    </time>
    <output>
        <fcd-output value="./output_fcd.xml"/>
    </output>
    </configuration>
    """
    with open("./data/sim.sumocfg", "w") as f:
        f.write(cfg)

    subprocess.run([
        "sumo",
        "-c", "./data/sim.sumocfg"
    ])

if __name__ == "__main__":
    download_osm_and_run()