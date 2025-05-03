import json
import torch
import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
from transformers import DistilBertTokenizer, DistilBertForQuestionAnswering
from fuzzywuzzy import fuzz
from smartsearch import retrieve_relevant_entry

# Setup Flask
app = Flask(__name__, static_folder='static', static_url_path='/static', template_folder='templates')
app.secret_key = 'secretkey'
CORS(app)

# Load models
qa_model_name = "distilbert-base-uncased-distilled-squad"
tokenizer = DistilBertTokenizer.from_pretrained(qa_model_name)
qa_model = DistilBertForQuestionAnswering.from_pretrained(qa_model_name)
retrieval_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Static database paths
database_paths = {
    'data1': '/path/to/data1.json',  # Replace this with actual path
}

@app.route('/index')
def index():
    return render_template('index.html')

# Load database from JSON file
def load_database():
    database = {}
    for name, path in database_paths.items():
        try:
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if isinstance(data, list):
                    database[name] = data
                else:
                    print(f"Warning: {name} data is not a list. Skipping...")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading {path}: {e}")
            database[name] = []
    return database

database = load_database()

# Retrieve the most relevant entry from the static data
def retrieve_relevant_entry(query, database):
    query = query.strip().lower()

    # Exact match
    for _, entries in database.items():
        for item in entries:
            if query == item.get("keyword", "").lower():
                return item.get("entry", "")

    # Fuzzy match
    best_match = None
    highest_score = 0
    for _, entries in database.items():
        for item in entries:
            keyword = item.get("keyword", "")
            score = fuzz.ratio(query, keyword.lower())
            if score > highest_score:
                highest_score = score
                best_match = item.get("entry", "")
    if highest_score >= 85:
        return best_match

    # Semantic similarity
    query_embedding = retrieval_model.encode(query, convert_to_tensor=True)
    best_match, best_score = "", -1
    for _, entries in database.items():
        for item in entries:
            combined_text = item.get("keyword", "") + " " + item.get("entry", "")
            entry_embedding = retrieval_model.encode(combined_text, convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(query_embedding, entry_embedding).item()
            if similarity > best_score:
                best_score = similarity
                best_match = item.get("entry", "")
    return best_match if best_score > 0.5 else "No relevant entry found."

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("query", "")
    result = retrieve_relevant_entry(query, database)
    return jsonify({"response": result})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
