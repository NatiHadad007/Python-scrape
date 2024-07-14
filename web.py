from flask import Flask, redirect, url_for
from PYtesting import run_script
import os

app = Flask(__name__, static_folder='static')

@app.route("/")
def home():
    return redirect(url_for('run'))

@app.route("/data.json")
def data_json():
    return app.send_static_file('data.json')

@app.route("/run")
def run():
    run_script()
    return "<p>Script run!</p>"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
