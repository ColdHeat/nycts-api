import json
import requests
import os
claim_code = None
idx = None
with open("/home/pi/nycts-unit/api/config.json", "r+") as f:
    config = json.load(f)
    sign_id = config["settings"]["sign_id"]
    claim_code = config["customtext"]["line_2"]
    try:
        idx = sign_id.index(";")
    except ValueError:
        pass
if idx:
    with open("/home/pi/nycts-unit/api/config.json", "w+") as f:
        config["settings"]["sign_id"] = sign_id[:idx]
        json.dump(config, f)
os.system("echo 'pi:raspberry' | chpasswd")
requests.post("https://api.trainsignapi.com/claim", json={"claim_code": claim_code}, timeout=5)