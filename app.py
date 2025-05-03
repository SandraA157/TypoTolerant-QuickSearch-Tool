import json
import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from smartsearch import retrieve_relevant_entry

# Setup Flask
app = Flask(__name__, static_folder='static', static_url_path='/static', template_folder='templates')
app.secret_key = 'secretkey'
CORS(app)

# Static database paths
database_paths = {
    'data1': '/path/to/data1.json',  # Replace this with actual path
}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("query", "")
    result = retrieve_relevant_entry(query, database)
    return jsonify({"response": result})

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    return render_template('data.html')

@app.route('/load_data', methods=['POST'])
def load_data():
    selected_file = request.json.get('file')

    if selected_file in database_paths:
        file_path = database_paths[selected_file]

        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
            return jsonify(data)  # Return the JSON data (array of objects)
        else:
            return jsonify({"error": "File not found"}), 404
    else:
        return jsonify({"error": "Invalid file selected"}), 400

@app.route('/get_data', methods=['GET'])
def get_data():
    file = request.args.get('file')
    with open(database_paths[file], 'r') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/save_data', methods=['POST'])
def save_data():
    try:
        data = request.json.get('data')
        selected_file = request.json.get('selected_file')
        
        if selected_file not in database_paths:
            return jsonify({"error": "Invalid file selected"}), 400
        
        file_path = database_paths[selected_file]
        
        # Clean up data: Convert keys to lowercase and replace special characters
        for item in data:
            item['question'] = item['Question'].replace('\u2019', "'")  # Convert and clean
            item['answer'] = item['Answer'].replace('\u2019', "'")  # Convert and clean
            del item['Question']  # Remove the old key if it exists
            del item['Answer']  # Remove the old key if it exists

        # Save cleaned data to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        return jsonify({"success": True, "message": "Data saved successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update_data', methods=['POST'])
def update_data():
    try:
        # Get the data from the request
        index = request.json.get('index')
        question = request.json.get('question')
        answer = request.json.get('answer')
        file = request.json.get('file')

        # Make sure the file is valid
        if file not in database_paths:
            return jsonify({"error": "Invalid file selected"}), 400

        file_path = database_paths[file]

        # Load the current data from the file
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            return jsonify({"error": "File not found"}), 404

        # Update the data at the specified index
        if index >= len(data) or index < 0:
            return jsonify({"error": "Invalid index"}), 400

        # Convert and clean the data
        data[index]["question"] = question.replace('\u2019', "'")  # Convert and clean
        data[index]["answer"] = answer.replace('\u2019', "'")  # Convert and clean

        # Save the updated data back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return jsonify({"success": True, "message": "Data updated successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete_data', methods=['POST'])
def delete_data():
    try:
        # Get the index and file from the request
        index = request.json.get('index')
        file = request.json.get('file')

        # Make sure the file is valid
        if file not in database_paths:
            return jsonify({"error": "Invalid file selected"}), 400

        file_path = database_paths[file]

        # Load the current data from the file
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            return jsonify({"error": "File not found"}), 404

        # Ensure the index is valid
        if index < 0 or index >= len(data):
            return jsonify({"error": "Invalid index"}), 400

        # Delete the item at the specified index
        del data[index]

        # Save the updated data back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return jsonify({"success": True, "message": "Data deleted successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
