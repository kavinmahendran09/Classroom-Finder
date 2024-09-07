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
        building_name = request.form.get('building')
        day_order = pd.read_csv('batch 1/2024_Day_order.csv')
        time_table = pd.read_csv('batch 1/UNIFIED_TIME_TABLE.csv')
        result = process_data(day_order, time_table, building_name)  # pass building_name
        return render_template('result.html', result=result)
    return render_template('building.html')

@app.route('/process', methods=['POST'])
def process_post():
    if request.method == 'POST':
        day_order = pd.read_csv('batch 1/2024_Day_order.csv')
        time_table = pd.read_csv('batch 1/UNIFIED_TIME_TABLE.csv')
        result = process_data(day_order, time_table)
        return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
