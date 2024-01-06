import os
import requests
from dotenv import load_dotenv
import time

load_dotenv()
airtable_key = os.getenv('AIRTABLE_KEY')
employee_tbl_url = 'https://api.airtable.com/v0/appLwrU5u2KrHXkAd/Employee'
floors_tbl_url = 'https://api.airtable.com/v0/appLwrU5u2KrHXkAd/Floors'
tasks_tbl_url = 'https://api.airtable.com/v0/appLwrU5u2KrHXkAd/Tasks'
unavailability_tbl_url = 'https://api.airtable.com/v0/appLwrU5u2KrHXkAd/Unavailability'
rota_tbl_url = 'https://api.airtable.com/v0/appLwrU5u2KrHXkAd/Rota'

# Get Employee data
def get_employee_data():
    # Get all employee data from Airtable
    # ToDo: Add pagination
    headers = {
        'Authorization': f'Bearer {airtable_key}',
        'Content-Type': 'application/json'
    }
    response = requests.get(employee_tbl_url, headers=headers)
    response.raise_for_status()
    
    # Create a dict from the response with the employee id as the key
    employee_data = {}
    for employee in response.json()['records']:
        employee_data[employee['fields']['EmployeeId']] = {
            'Name': employee['fields']['Name'],
            'DefaultFloor': employee['fields']['DefaultFloor'],
            'Tasks': employee['fields']['Tasks']
        }
    return employee_data

# Get Floor data
def get_floor_data():
    # Get floor data from airtable
    headers = {
        'Authorization': f'Bearer {airtable_key}',
        'Content-Type': 'application/json'
    }
    response = requests.get(floors_tbl_url, headers=headers)
    response.raise_for_status()
    
    # Create a dict from the response with the floor name as the key
    floor_data = {}
    for floor in response.json()['records']:
        floor_data[floor['fields']['Floor']] = {
            'Tasks List': floor['fields']['Tasks List'],
            'Total Employees Required': floor['fields']['Total Employees Required']
        }
    return floor_data

# Get Task data
def get_task_data():
    # Get task data from airtable
    headers = {
        'Authorization': f'Bearer {airtable_key}',
        'Content-Type': 'application/json'
    }
    response = requests.get(tasks_tbl_url, headers=headers)
    response.raise_for_status()
    
    # Create a dict from the response with the task name as the key
    task_data = {}
    for task in response.json()['records']:
        task_data[task['fields']['Task']] = {
            'Employees Required': task['fields']['Employees Required']
        }
    return task_data

# Get Unavailability info for a specific data
def get_unavailabilty_data(date):
    # Get Unavailability data from airtable
    headers = {
        'Authorization': f'Bearer {airtable_key}',
        'Content-Type': 'application/json'
    }
    # Only return rows for which the date is on or between the start and end dates
    data = {
        'filterByFormula': f"OR(IS_SAME('{date}', {{Holiday Start Date}}, 'day'), AND(IS_AFTER('{date}', {{Holiday Start Date}}), IS_BEFORE('{date}', {{Holiday End Date}})), IS_SAME('{date}', {{Holiday End Date}}, 'day'))"
    }
    response = requests.post(unavailability_tbl_url + '/listRecords', headers=headers, json=data)
    response.raise_for_status()

    # Create a dict from the response with the floor name as the key
    unavailability_data = {}
    for unavailability in response.json()['records']:
        unavailability_data[unavailability['fields']['Employee ID']] = {
            'Start Date': unavailability['fields']['Holiday Start Date'],
            'End Date': unavailability['fields']['Holiday End Date']
        }
    return unavailability_data

# Add time off to Unavailability table
def add_time_off(employee_id, start_date, end_date):
    # Get Unavailability data from airtable
    headers = {
        'Authorization': f'Bearer {airtable_key}',
        'Content-Type': 'application/json'
    }
    data = {
        "records": [
            {
            "fields": {
                "Employee ID": employee_id,
                "Holiday Start Date": start_date,
                "Holiday End Date": end_date
            }
            }
        ]
    }
    response = requests.post(unavailability_tbl_url, headers=headers, json=data)
    response.raise_for_status()


def get_rota_for_day(date):
    # Get rota data from airtable
    headers = {
        'Authorization': f'Bearer {airtable_key}',
        'Content-Type': 'application/json'
    }
    # Only return rows for which the date is the same as the input date
    data = {
        'filterByFormula': f"IS_SAME('{date}', {{Date}}, 'day')"
    }

    # Get all records from the table making multiple calls to Airtable if required
    records = []
    run = True
    while run:
        response = requests.post(rota_tbl_url + '/listRecords', headers=headers, json=data)
        response.raise_for_status()
        records.extend(response.json().get('records', []))

        offset = response.json().get('offset')
        if offset:
            data['offset'] = offset
        else:
            run = False

    # Create a list of records for the day's rota
    rota = []
    for record in records:
        rota.append([
            record['fields']['Date'],
            record['fields']['Employee ID'],
            record['fields']['Employee Name'],
            record['fields']['Start Time'],
            record['fields']['End Time'],
            record['fields']['Floor'],
            record['fields']['Task']
        ])
    return rota

def get_rota_for_employee_and_day(date, employee_id):
    headers = {
        'Authorization': f'Bearer {airtable_key}',
        'Content-Type': 'application/json'
    }
    # Only return rows for which the date is the same as the input date and the
    # EmployeeID matches the input id
    data = {
        'filterByFormula': f"AND(IS_SAME('{date}', {{Date}}, 'day'), {employee_id}={{Employee ID}})"
    }
    response = requests.post(rota_tbl_url + '/listRecords', headers=headers, json=data)
    response.raise_for_status()

    # Create a list of records for the day's rota
    rota = []
    for record in response.json()['records']:
        rota.append([
            record['fields']['Date'],
            record['fields']['Employee ID'],
            record['fields']['Employee Name'],
            record['fields']['Start Time'],
            record['fields']['End Time'],
            record['fields']['Floor'],
            record['fields']['Task']
        ])
    return rota

def get_dates_w_rota_in_range(start_date, end_date):
    headers = {
        'Authorization': f'Bearer {airtable_key}',
        'Content-Type': 'application/json'
    }
    # Only return rows for which the date is on or between the start and end dates
    data = {
        'filterByFormula': f"OR(IS_SAME('{start_date}', {{Date}}, 'day'), AND(IS_AFTER({{Date}}, '{start_date}'), IS_BEFORE({{Date}}, '{end_date}')), IS_SAME('{end_date}', {{Date}}, 'day'))"
    }
    response = requests.post(rota_tbl_url + '/listRecords', headers=headers, json=data)
    response.raise_for_status()

    # Create a set with the unique dates in the response
    records = response.json().get('records', [])
    dates = {record['fields']['Date'] for record in records}
    return dates

def get_all_rota_record_ids():
    headers = {
        'Authorization': f'Bearer {airtable_key}',
        'Content-Type': 'application/json'
    }
    record_ids = []
    params = {}
    while True:
        response = requests.get(rota_tbl_url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        records = data.get('records', [])
        record_ids.extend([record['id'] for record in records])

        offset = data.get('offset')
        if not offset:
            break
        params['offset'] = offset
        time.sleep(0.25) # Handle rate limit of 5 requests per second + buffer
    return record_ids

def get_rota_record_ids_for_day(date):
    headers = {
        'Authorization': f'Bearer {airtable_key}',
        'Content-Type': 'application/json'
    }
    record_ids = []
    params = {
        'filterByFormula': f"IS_SAME('{date}', {{Date}}, 'day')"
    }
    while True:
        response = requests.post(rota_tbl_url + '/listRecords', headers=headers, json=params)
        response.raise_for_status()

        data = response.json()
        records = data.get('records', [])
        record_ids.extend([record['id'] for record in records])

        offset = data.get('offset')
        if not offset:
            break
        params['offset'] = offset
        time.sleep(0.25) # Handle rate limit of 5 requests per second + buffer
    return record_ids

def delete_rota_records(record_ids):
    headers = {
        'Authorization': f'Bearer {airtable_key}'
    }
    for i in range(0, len(record_ids), 10):
        batch = record_ids[i:i + 10]
        query = "&".join([f"records[]={record_id}" for record_id in batch])
        url = f"{rota_tbl_url}?{query}"
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        time.sleep(0.25) # Handle rate limit of 5 requests per second + buffer

def write_to_rota_table(records):
    # Write records to airtable
    headers = {
        'Authorization': f'Bearer {airtable_key}',
        'Content-Type': 'application/json'
    }

    for i in range(0, len(records), 10):
        batch = records[i:i + 10]
        data = {'records': batch}
        response = requests.post(rota_tbl_url, headers=headers, json=data)
        response.raise_for_status()
        time.sleep(0.25) # Handle rate limit of 5 requests per second + buffer
