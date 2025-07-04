
import xml.etree.ElementTree as ET
import pandas as pd

def parse_fcd_xml(filepath: str) -> pd.DataFrame:
    tree = ET.parse(filepath)
    root = tree.getroot()

    rows = []

    for timestep in root.findall('timestep'):
        time = float(timestep.get('time'))
        for vehicle in timestep.findall('vehicle'):
            veh_id = vehicle.get('id')
            lon = float(vehicle.get('x'))
            lat = float(vehicle.get('y'))
            speed = float(vehicle.get('speed'))
            rows.append({
                "time": time,
                "vehicle_id": veh_id,
                "longitude": lon,
                "latitude": lat,
                "speed": speed
            })

    df = pd.DataFrame(rows)
    return df
