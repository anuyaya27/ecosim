# app.py

from flask import Flask, render_template, request, jsonify
from main.engine.simulation_engine import simulate
import os

app = Flask(__name__, static_folder='frontend', template_folder='frontend')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/simulate", methods=["POST"])
def run_simulation():
    data = request.form

    try:
        policy_params = {
            'ubi': float(data.get('ubi', 0)),
            'minimum_wage': float(data.get('minimum_wage', 0)),
        'tax_brackets': [
            (0, float(data.get('tax1_rate', 0.1)) / 100),
            (20000, float(data.get('tax2_rate', 0.2)) / 100),
            (60000, float(data.get('tax3_rate', 0.3)) / 100)
        ]
        }

        result = simulate(policy_params, os.path.join("data", "agents_sample.csv"))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
