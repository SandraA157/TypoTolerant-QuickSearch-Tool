# TypoTolerant-QuickSearch/Predefined-Chatbot Tool (Flask + Fuzzy Matching + Embeddings)

## Overview
This is a Python-based command-line tool for fast, typo-tolerant searching through a static JSON database. 

It can also function as a chatbot with predetermined responses if the fuzzy match score threshold set lowers (as originally intended).

It supports:
- Exact match retrieval
- Fuzzy matching for typo tolerance
- Semantic similarity using sentence embeddings

## Requirements
- Python 3.7 or higher

Install dependencies with:
  pip install -r requirements.txt

## Setup
1. Prepare your keyword-entry database in a JSON file with this format:
    [
      {
        "keyword": "pip",
        "entry": "Python package installer."
      },
      {
        "keyword": "flask",
        "entry": "A lightweight web framework for Python."
      }
    ]

2. Update the file path in your script:
    database_paths = {
        'data': '/full/path/to/data.json'
    }
3. Running the Tool
- Run the script:
    python search_tool.py
- Run the flask script:
    python app.py
## Features
- Searches through static data
- Handles minor typos using fuzzy matching
- Requires no internet or external services-
- Lightweight and easy to modify
