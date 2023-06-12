from flask import Flask, request,jsonify
from os import path
import csv

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


@app.route('/sumUp', methods=['POST'])
def calculate_sum():
    data = request.get_json()
    file = data['file']
    product = data['product']

    if not is_csv_file(file):
        return jsonify(file = file, error='Input file not in CSV format.' )

    sum_result = calculate(file, product)
    return jsonify(file = file, sum = sum_result)

def is_csv_file(file):
    file_path = "/home/" + file
    try:
        with open(file_path, 'r') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            return dialect.delimiter == ','
    except (csv.Error, IOError):
        return False

def calculate(file, product):
    file_path = "/home/" + file

    if path.exists(file_path):
        total_sum = 0

        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['product'].lower() == product.lower():
                    amount = int(row['amount'])
                    total_sum += amount

        return total_sum

    else:
        return 'File not found'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
