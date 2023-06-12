from flask import Flask, request, jsonify
from os import path
import requests

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

@app.route('/calculate', methods=['POST'])
def calculate():
    request_file = request.get_json()
    if request_file is None or 'file' not in request_file or 'product' not in request_file:
        return jsonify(
            file="null",
            error="Invalid JSON input."
        )
    
    file = request_file['file']
    if not path.exists("/home/" + file):
        return jsonify(
            file=file,
            error="File not found."
        )
    else:
        data = requests.post("http://apptwo:8000/sumUp", json=request_file)
        return data.json()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
