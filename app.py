from flask import Flask, render_template, request
import pandas as pd
from main import process_data

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

<<<<<<< HEAD
@app.route('/process', methods=['POST'])
def process():
    if request.method == 'POST':
        day_order = pd.read_csv('batch 1/2024_Day_order.csv')
        time_table = pd.read_csv('batch 1/UNIFIED_TIME_TABLE.csv')
        result = process_data(day_order, time_table)
        return render_template('result.html', result=result)
=======
@app.route('/building', methods=['GET', 'POST'])
def building():
    if request.method == 'POST':
        # Handle the selection and redirect to results
        building_name = request.form.get('building')
        # Redirect to process with building information
        return render_template('result.html', result=process_data(building_name))
    return render_template('building.html')

@app.route('/process', methods=['POST'])
def process():
    # This route may not be necessary if you directly handle the building selection
    # through the `/building` route. But if you need to keep it, you can do the following:
    day_order = pd.read_csv('batch 1/2024_Day_order.csv')
    time_table = pd.read_csv('batch 1/UNIFIED_TIME_TABLE.csv')
    result = process_data(day_order, time_table)
    return render_template('result.html', result=result)
>>>>>>> 9ecb46e (buildingpage)

if __name__ == '__main__':
    app.run(debug=True)
