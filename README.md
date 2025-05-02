# Typo-Tolerant Quick Search App (Flask + Fuzzy Matching + Embeddings)

## Overview
This is a Python-based command-line tool for fast, typo-tolerant searching through a static JSON database of question-answer pairs.

It supports:
- Exact match retrieval
- Fuzzy matching for typo tolerance
- Semantic similarity using sentence embeddings

Ideal local documentation lookups.

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
        'data1': '/full/path/to/data1.json'
    }
3. Running the Tool
- Run the script:
    python search_tool.py
- You will be prompted to type your question:
- Type exit to quit the tool.

## Features
- Searches through static Q&A data
- Handles minor typos using fuzzy matching
- Requires no internet or external services-
- Lightweight and easy to modify
