from flask import Flask
from flask import request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import database_manager as dbHandler

api = Flask(__name__)
cors = CORS(api)
api.config["CORS_HEADERS"] = "Content-Type"
limiter = Limiter(
      get_remote_address,
      app=api,
      default_limits=["200 per day", "50 per hour"],
      storage_uri="memory://",
)

@api.route("/", methods=["GET"])
@limiter.limit("3/second", override_defaults=False)
def get():
      if request.args.get("lang") and request.args.get("lang").isalpha():
            lang = request.args.get("lang")
            lang = lang.upper()
            content = dbHandler.extension_get(lang)
      else:
            content = dbHandler.extension_get("%")
      return (content), 200


@api.route("/add_extension", methods=["POST"])
@limiter.limit("1/second", override_defaults=False)
def post():
      data = request.get_json()
      return data, 201


if __name__ == "__main__":
      api.run(debug=True, host="0.0.0.0", port=3000)