# Import necessary libraries
import json
import torch
import requests
import os
import openai #pip install openai
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
from transformers import DistilBertTokenizer, DistilBertForQuestionAnswering
from fuzzywuzzy import fuzz

# Set your OpenAI API key here
openai.api_key = 'your-openai-api-key'

# Setup Flask
app = Flask(__name__, static_folder='static', static_url_path='/static', template_folder='templates')
app.secret_key = 'samd21kkKNSA(SDi3jKSDOALSDALSD<'
CORS(app)

# Load models
qa_model_name = "distilbert-base-uncased-distilled-squad"
tokenizer = DistilBertTokenizer.from_pretrained(qa_model_name)
qa_model = DistilBertForQuestionAnswering.from_pretrained(qa_model_name)
retrieval_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Set up database paths
database_paths = {
    'checkin_checkout': '/home/user/03CHATBOT/data/checkin_checkout.json',
    'hotel_services': '/home/user/03CHATBOT/data/hotel_services.json',
    'local_area_info': '/home/user/03CHATBOT/data/local_area_info.json',
    'breakfast_dining': '/home/user/03CHATBOT/data/breakfast_dining.json',
    'transportation': '/home/user/03CHATBOT/data/transportation.json',
    'hotel_amenities': '/home/user/03CHATBOT/data/hotel_amenities.json',
}
dynamic_data_path = '/home/user/03CHATBOT/data/dynamic_data.json'

@app.route('/index')
def index():
    return render_template('index.html')

# Loads all database files and returns them as a dictionary.
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

# Loads dynamic data from a JSON file.
def load_dynamic_data():
    try:
        with open(dynamic_data_path, 'r', encoding='utf-8') as file:
            dynamic_data = json.load(file)
        return dynamic_data if isinstance(dynamic_data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"⚠️ Error loading dynamic data: {e}")
        return {}

# Uses fuzzy matching to find the closest match.
def find_best_match(query, database):
    best_match, best_score = None, 0
    for category, qa_pairs in database.items():
        for qa in qa_pairs:
            score = fuzz.ratio(query.lower(), qa["question"].lower())
            print ("Score : {score}")
            if score > best_score:
                best_score, best_match = score, qa["answer"]
    return best_match if best_score > 80 else None

# Uses DistilBERT to answer a question based on a given context.
def answer_question(query, context):
    try:
        inputs = tokenizer(query, context, return_tensors="pt")
        with torch.no_grad():
            outputs = qa_model(**inputs)
        answer_start, answer_end = torch.argmax(outputs.start_logits), torch.argmax(outputs.end_logits) + 1
        answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs['input_ids'][0][answer_start:answer_end]))
        return answer.strip() if answer else "I couldn't generate an answer."
    except Exception as e:
        print(f"⚠️ Error generating answer: {e}")
        return "I encountered an issue processing your question."

# Finds the best-matching answer in the database using exact match and embeddings."""
def retrieve_relevant_text(query, database):
    print(f"🔎 Searching for answer to: '{query}'")
    
    # Check exact match
    for category, qa_pairs in database.items():
        for qa in qa_pairs:
            if query.lower() == qa["question"].lower():
                return qa["answer"]

##    print("❌ No exact match found. Trying AI response...")

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

    return best_match if highest_score > 0.5 else None

# Function to call the ChatGPT API
def chatgpt_api(query):
    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",  # or "gpt-4" if available
            prompt=query,
            max_tokens=200,  # You can adjust this depending on the expected response length
            temperature=0.7  # You can adjust the creativity/variance of the response
        )
        return response.choices[0].text.strip()  # Return the response text
    except Exception as e:
        print(f"Error while getting response from ChatGPT: {e}")
        return "Sorry, I couldn't process your request."

# Updated chatbot_response function
def chatbot_response(query):
    print(f"Received query: {query}")

    # Try to retrieve an answer from the static database
    static_answer = retrieve_relevant_text(query, database)
    
    if static_answer:
        dynamic_data = load_dynamic_data()
        for key, value in dynamic_data.items():
            static_answer = static_answer.replace(f"{{{key}}}", str(value))
        return static_answer

    # Try answering dynamically
    dynamic_data = load_dynamic_data()
    context = " ".join(f"{key}: {value}" for key, value in dynamic_data.items())

    if "NODATA" in dynamic_data.values():
        # If "NODATA" is found in dynamic data, return the fallback message
        return "Sorry, I cannot answer your question at the moment. Please ask the front desk for more information."
    elif "SEARCH" in dynamic_data.values():
        # If "SEARCH" is found in dynamic data, trigger OpenAI search
        return chatgpt_api(query)
        
    if context.strip():
        dynamic_answer = answer_question(query, context)
        print(f"Answer: '{dynamic_answer}'")
        return dynamic_answer if dynamic_answer else chatgpt_api(query)

    # Final fallback: Query ChatGPT API if nothing else works
    return chatgpt_api(query)

def chat():
    while True:
        question = input("You: ").strip().lower()
        if question.lower() == 'exit':
            print("Goodbye!")
            break

        response = chatbot_response(message)
        print(f"Chatbot: {response}")

if __name__ == "__main__":
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)
