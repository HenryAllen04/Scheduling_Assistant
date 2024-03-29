from flask import Flask, request, jsonify, make_response
import datetime

from airtable import (
    add_time_off,
    get_employee_data,
    get_floor_data,
    get_task_data,
    get_rota_for_day,
    get_rota_for_employee_and_day,
    get_dates_w_rota_in_range,
    get_rota_record_ids_for_day,
    delete_rota_records,
    write_to_rota_table
)
from scheduler import (
    gen_rota_for_date_range,
    gen_rota_for_date
)

app = Flask(__name__)

# Home endpoint
@app.route('/')
def home():
    return "Welcome to the Scheduler App!\n"

# Generate Rota for time frame
@app.route('/rota/generate', methods=['POST'])
def generate_rota_for_dates():
    data = request.json

    # List of required fields
    required_keys = ['StartDate', 'EndDate']

    if not all(key in data for key in required_keys):
        missing_keys = [key for key in required_keys if key not in data]
        return make_response(jsonify({
            'error': 'Missing fields in request data.',
            'missing_fields': missing_keys
        }), 400)
    
    try:
        # Fetch required data
        employee_data = get_employee_data()
        floor_data = get_floor_data()
        task_data = get_task_data()

        # Generate Rota
        gen_rota_for_date_range(data['StartDate'], data['EndDate'], employee_data, task_data, floor_data)
    except:
        return make_response(jsonify({
            'error': 'Failed to generate rota for the date range.'
        }), 500)
    return "Successfully generated rota for the date range.\n"

# Fetch rota
@app.route('/rota/fetch/<string:date>')
def fetch_rota_for_day(date):
    # Check if date is valid
    if not is_valid_date(date):
        return make_response(jsonify({
            'error': 'Invalid date, please provide a valid date in YYYY-MM-DD format.'
        }), 400)
    try:
        employee_id = request.args.get('EmployeeID')
        if not employee_id:
            rota = get_rota_for_day(date)
            
        else:
            rota = get_rota_for_employee_and_day(date, employee_id)
            #adding ascending sort for schedule formatting, based on End time "[4]"
            rota = sorted(rota, key=lambda x: x[4])
    except:
        return make_response(jsonify({
            'error': 'Failed to fetch the rota for the day.'
        }), 500)
    return rota

# Request timeoff
@app.route('/timeoff/add', methods=['POST'])
def request_time_off():
    data = request.json

    # List of required fields
    required_keys = ['EmployeeID', 'StartDate', 'EndDate']

    if not all(key in data for key in required_keys):
        missing_keys = [key for key in required_keys if key not in data]
        return make_response(jsonify({
            'error': 'Missing fields in request data.',
            'missing_fields': missing_keys
        }), 400)

    if not (is_valid_date(data['StartDate']) and is_valid_date(data['EndDate'])):
        return make_response(jsonify({
            'error': 'Invalid date, please provide valid dates in YYYY-MM-DD format.'
        }), 400)
    try:
        print(f"---------Adding time-off for EmployeeID: {data['EmployeeID']} from {data['StartDate']} to {data['EndDate']}------------------")
        add_time_off(data['EmployeeID'], data['StartDate'], data['EndDate'])
        dates = get_dates_w_rota_in_range(data['StartDate'], data['EndDate'])
    except:
        return make_response(jsonify({
            'error': 'Failed to add time-off.'
        }), 500)
    try:
        employee_data = get_employee_data()
        floor_data = get_floor_data()
        task_data = get_task_data()
        for date in dates:
            print(f'---------Generating Rota for {date}------------------')
            records = gen_rota_for_date(date, employee_data, task_data, floor_data)
            print(f'---------Deleting existing Rota records if any for {date}------------------')
            record_ids = get_rota_record_ids_for_day(date)
            delete_rota_records(record_ids)
            print(f'---------Writing new Rota records for {date}------------------')
            write_to_rota_table(records)
            print(f'---------Generating Rota for {date} complete------------------')
    except:
        return make_response(jsonify({
            'error': f'Failed to generate rota with time-off for {date}.'
        }), 500)

    return "Added time-off.\n"

# Check if the date string refers to a valid date
def is_valid_date(date_str):
    try:
        datetime.date.fromisoformat(date_str)
    except ValueError:
        print("Invalid date, please provide a valid date in YYYY-MM-DD format")
        return False
    return True

# Run the app
if __name__ == '__main__':

    # Run Flask app
    app.run(debug=True)

