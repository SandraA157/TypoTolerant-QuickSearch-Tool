import json
import torch
from sentence_transformers import SentenceTransformer, util
from transformers import DistilBertTokenizer, DistilBertForQuestionAnswering
from fuzzywuzzy import fuzz

retrieval_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased-distilled-squad")
qa_model = DistilBertForQuestionAnswering.from_pretrained("distilbert-base-uncased-distilled-squad")

database_paths = {
    'reference': '/home/user/Downloads/TypoTolerant-QuickSearch-Tool-main/data1.json'
}

def load_database():
    database = {}
    for name, path in database_paths.items():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    database[name] = data
                else:
                    print(f"Warning: {name} is not a list. Skipping...")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading {path}: {e}")
            database[name] = []
    return database

database = load_database()

def lookup(query, database):
    query = query.strip().lower()
    best_match = None
    highest_score = 0

    # Exact match
    for _, entries in database.items():
        for item in entries:
            if query == item["keyword"].lower():
                return item["entry"]

    # Fuzzy match
    for _, entries in database.items():
        for item in entries:
            score = fuzz.ratio(query, item["keyword"].lower())
            if score > highest_score:
                highest_score = score
                best_match = item["entry"]
    if highest_score >= 85:
        return best_match

    # Semantic similarity
    query_embedding = retrieval_model.encode(query, convert_to_tensor=True)
    best_match, similarity_score = None, -1

    for _, entries in database.items():
        for item in entries:
            combined_text = item["keyword"] + " " + item["entry"]
            entry_embedding = retrieval_model.encode(combined_text, convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(query_embedding, entry_embedding).item()
            if similarity > similarity_score:
                similarity_score = similarity
                best_match = item["entry"]

    return best_match if similarity_score > 0.5 else "No matching entry found."

def run_lookup():
    print("Keyword Lookup Tool (type 'exit' to quit)")
    while True:
        query = input("> ").strip()
        if query.lower() == "exit":
            print("Goodbye!")
            break
        result = lookup(query, database)
        print(result)

if __name__ == "__main__":
    run_lookup()
