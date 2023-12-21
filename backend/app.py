from flask import Flask, request, jsonify, make_response
import datetime

from airtable import get_employee_data, get_floor_data, get_task_data, get_rota_for_day, get_rota_for_employee_and_day
from scheduler import gen_rota_for_date_range, gen_rota_for_date, gen_rota_for_floor

app = Flask(__name__)

# Home endpoint
@app.route('/')
def home():
    return "Welcome to the Scheduler App!"

# Generate Rota for time frame
@app.route('/rota/generate', methods=['POST'])
def generate_rota_for_dates():
    data = request.json

    # List of required fields
    required_keys = ['start_date', 'end_date']

    if not all(key in data for key in required_keys):
        missing_keys = [key for key in required_keys if key not in data]
        return make_response(jsonify({
            'error': 'Missing fields in request data.',
            'missing_fields': missing_keys
        }), 400)
    
    try:
        # Fetch required data
        # employee_data = get_employee_data()
        # floor_data = get_floor_data()
        # task_data = get_task_data()

        # Generate Rota
        # gen_rota_for_date_range(data['start_date'], data['end_date'], employee_data, task_data, floor_data)
        print('here')
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
    except:
        return make_response(jsonify({
            'error': 'Failed to generate rota for the date range.'
        }), 500)
    return rota

# Request timeoff
@app.route('/timeoff/create', methods=['POST'])
def request_time_off():
    data = request.json

    return "Added time-off.\n"

def is_valid_date(date_text):
    try:
        datetime.date.fromisoformat(date_text)
    except ValueError:
        print("Invalid date, please provide a valid date in YYYY-MM-DD format")
        return False
    return True

if __name__ == '__main__':

    # Run Flask app
    app.run(debug=True)

