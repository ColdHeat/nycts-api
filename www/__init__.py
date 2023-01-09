import os
import json

from flask import Blueprint, redirect, render_template, request, url_for, current_app
from sqlalchemy.orm.attributes import flag_modified

from models import Signs, db

www = Blueprint("www", __name__, template_folder="templates")

with open("data/stops.json") as f:
    STOPS = json.load(f)


@www.route("/")
def index():
    return render_template("index.html")


@www.route("/signs/nycts/<sign_id>", methods=["GET", "POST"])
def nycts(sign_id):
    sign = Signs.query.filter_by(sign_id=sign_id).first_or_404()
    if request.method == "POST":
        # Global Settings
        sign.config["settings"]["name"] = request.form["name"]
        sign.config["settings"]["transition_time"] = int(
            request.form["transition_time"]
        )
        sign.config["settings"]["brightness"] = int(request.form["brightness"])

        # Custom Text
        sign.config["customtext"]["enabled"] = (
            request.form["customtext_enabled"] == "true"
        )
        sign.config["customtext"]["line_1"] = request.form["customtext_line_1"]
        sign.config["customtext"]["line_2"] = request.form["customtext_line_2"]

        # Train
        sign.config["subway"]["enabled"] = request.form["subway_enabled"] == "true"
        sign.config["subway"]["line"] = request.form["subway_line"]
        sign.config["subway"]["train"] = request.form["subway_train"]

        # Weather
        sign.config["weather"]["enabled"] = request.form["weather_enabled"] == "true"
        sign.config["weather"]["zip_code"] = request.form["weather_zip_code"]

        # Logo
        sign.config["logo"]["enabled"] = request.form["logo_enabled"] == "true"
        logo = request.files.get("logo")
        if logo:
            sign.config["logo"]["updated"] = True
            logo.save(
                os.path.join(
                    current_app.root_path, "api", "static", "uploads", f"{sign_id}"
                )
            )

        flag_modified(sign, "config")
        db.session.commit()
        return render_template("wait.html", sign_id=sign_id)
    else:
        return render_template("nycts.html", sign=sign, STOPS=STOPS)


@www.route("/claim", methods=["GET", "POST"])
def claim():
    if request.method == "POST":
        code = request.form["claim_code"].upper()
        s = Signs.query.filter_by(claim_code=code).first_or_404()
        return redirect(url_for("www.nycts", sign_id=s.sign_id))
    else:
        return render_template("claim.html")
