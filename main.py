from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
import requests
from flask_wtf import CSRFProtect
from flask_csp.csp import csp_header
import logging

app = Flask(__name__)
csrf = CSRFProtect(app)
app.secret_key = b"6HlQfWhu03PttohW;apl"

app_header = {"Authorisation": "4L50v92nOgcDCYUM"}

@app.route("/index.html", methods=["GET"])
def root():
      return redirect("/", 302)

@app.route("/privacy.html", methods=["GET"])
def privacy():
      return render_template("/privacy.html")

@app.route("/", methods=["GET"])
@csp_header(
      {
            "base-uri": "self",
            "default-src": "'self'",
            "style-src": "'self'",
            "script-src": "'self'",
            "img-src": "*",
            "media-src": "'self'",
            "font-src": "self",
            "object-src": "'self'",
            "child-src": "'self'",
            "connect-src": "'self'",
            "worker-src": "'self'",
            "report-uri": "/csp_report",
            "frame-ancestors": "'none'",
            "form-action": "'self'",
            "frame-src": "'none'",
      }
)
def index():
      url = "http://127.0.0.1:3000"
      try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
      except requests.exceptions.RequestException as e:
            data = {"error": "Failed to retrieve data from API"}
      return render_template("/index.html", data=data)


@app.route("/csp_report", methods=["POST"])
@csrf.exempt
def csp_report():
      app.logger.critical(request.data.decode())
      return "done"

if __name__ == "__main__":
      app.run(debug=True, host="0.0.0.0", port=5000)