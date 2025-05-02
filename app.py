# Import necessary libraries
import torch
import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
from transformers import DistilBertTokenizer, DistilBertForQuestionAnswering
from fuzzywuzzy import fuzz

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
    'data1': '/path/to/data1.json',
}

@app.route('/index')
def index():
    return render_template('index.html')

# Load database from JSON
def load_database():
    database = {}
    for category, path in database_paths.items():
        try:
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if isinstance(data, list):
                    database[category] = data
                else:
                    print(f"⚠️ Warning: {category} data is not a list. Skipping...")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️ Error loading {path}: {e}")
            database[category] = []
    return database

database = load_database()

# Retrieve best answer from static data
def retrieve_relevant_text(query, database):
    print(f"🔎 Searching for answer to: '{query}'")

    # Check for exact match
    for category, qa_pairs in database.items():
        for qa in qa_pairs:
            if query.lower() == qa["question"].lower():
                return qa["answer"]

    # Use embeddings for similarity search
    query_embedding = retrieval_model.encode(query, convert_to_tensor=True)
    best_match, highest_score = "", -1

    for category, qa_pairs in database.items():
        for qa in qa_pairs:
            text = qa["question"] + " " + qa["answer"]
            embedding = retrieval_model.encode(text, convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(query_embedding, embedding).item()
            if similarity > highest_score:
                highest_score, best_match = similarity, qa["answer"]

    return best_match if highest_score > 0.5 else "Sorry, I couldn't find a good answer."

@app.route("/chat", methods=["POST"])
def chat_route():
    data = request.get_json()
    query = data.get("query", "")
    response = retrieve_relevant_text(query, database)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
