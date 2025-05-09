import json
import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from smartsearch import retrieve_relevant_entry

# Setup Flask
app = Flask(__name__, static_folder='static', static_url_path='/static', template_folder='templates')
app.secret_key = 'secretkey'
CORS(app)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("message", "")
    result = retrieve_relevant_entry(query)
    return jsonify({"response": result})

@app.route('/index')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
