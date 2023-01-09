import csv
import json

import requests

header = ["id", "name", "stop", "line"]


routes = requests.get("https://api.wheresthefuckingtrain.com/routes", timeout=5).json()[
    "data"
]

stops_json = []

with open("stops.csv", "w") as output_file, open(
    "stops.json", "w"
) as output_stops_json:
    fc = csv.DictWriter(output_file, fieldnames=header)
    fc.writeheader()

    for route in routes:
        print(f"Building {route}")
        stations = requests.get(
            f"https://api.wheresthefuckingtrain.com/by-route/{route}", timeout=5
        ).json()["data"]
        for station in stations:
            stops = station["stops"].keys()
            for stop in stops:
                line = {
                    "id": station["id"],
                    "name": station["name"],
                    "stop": stop,
                    "line": route,
                }
                fc.writerow(line)
                stops_json.append(line)
                print(line)
                # input()
    json.dump(stops_json, output_stops_json)
