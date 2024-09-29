from flask import Flask, render_template, request
import pandas as pd
from main import process_data

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/building', methods=['GET', 'POST'])
def building():
    if request.method == 'POST':
        building_name = request.form.get('building')  # Get the selected building name
        # Call process_data directly without needing to pass the day_order
        result = process_data(None, building_name)  # Pass building_name to process_data
        return render_template('result.html', result=result)
    return render_template('building.html')

@app.route('/process', methods=['POST'])
def process_post():
    if request.method == 'POST':
        # You can keep this if you want to handle another case, or remove it if redundant
        result = process_data(None, None)  # Call process_data without specific parameters
        return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
