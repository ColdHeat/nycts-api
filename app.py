from flask import Flask
from flask_bootstrap import Bootstrap5

from api import api
from models import db
from www import www

app = Flask(__name__)

bootstrap = Bootstrap5(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///nycts.db"

app.config["SERVER_NAME"] = "trainsignapi.com"

db.init_app(app)
with app.app_context():
    db.create_all()

app.register_blueprint(api, subdomain="api")
app.register_blueprint(www, subdomain="www")

if __name__ == "__main__":
    app.run(debug=True, threaded=True, host="127.0.0.1", port=8000)
