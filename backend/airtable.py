import os
import requests
from dotenv import load_dotenv

load_dotenv()
airtable_key = os.getenv('AIRTABLE_KEY')

# Get Employee data
def get_employee_data():
    # Get all employee data from Airtable
    # ToDo: Add pagination
    global airtable_key
    employee_tbl_url = 'https://api.airtable.com/v0/appLwrU5u2KrHXkAd/Employee'
    headers = {
        'Authorization': f'Bearer {airtable_key}',
        'Content-Type': 'application/json'
    }
    response = requests.get(employee_tbl_url, headers=headers)
    
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
    global airtable_key
    floors_tbl_url = 'https://api.airtable.com/v0/appLwrU5u2KrHXkAd/Floors'
    headers = {
        'Authorization': f'Bearer {airtable_key}',
        'Content-Type': 'application/json'
    }
    response = requests.get(floors_tbl_url, headers=headers)
    
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
    global airtable_key
    tasks_tbl_url = 'https://api.airtable.com/v0/appLwrU5u2KrHXkAd/Tasks'
    headers = {
        'Authorization': f'Bearer {airtable_key}',
        'Content-Type': 'application/json'
    }
    response = requests.get(tasks_tbl_url, headers=headers)
    
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
    global airtable_key
    unavailability_tbl_url = 'https://api.airtable.com/v0/appLwrU5u2KrHXkAd/Unavailability'
    headers = {
        'Authorization': f'Bearer {airtable_key}',
        'Content-Type': 'application/json'
    }
    # Only return rows for which the date is on or between the start and end dates
    data = {
        'filterByFormula': "OR(IS_SAME('" + date + "', {Holiday Start Date}, 'day'), AND(IS_AFTER('" + date + "', {Holiday Start Date}), IS_BEFORE('" + date + "', {Holiday End Date})), IS_SAME('" + date + "', {Holiday End Date}, 'day'))"
    }
    response = requests.post(unavailability_tbl_url + '/listRecords', headers=headers, json=data)

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
    global airtable_key
    unavailability_tbl_url = 'https://api.airtable.com/v0/appLwrU5u2KrHXkAd/Unavailability'
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


def get_rota_for_day(date):
    # Get rota data from airtable
    global airtable_key
    rota_tbl_url = 'https://api.airtable.com/v0/appLwrU5u2KrHXkAd/Rota'
    headers = {
        'Authorization': f'Bearer {airtable_key}',
        'Content-Type': 'application/json'
    }
    # Only return rows for which the date is the same as the input date
    data = {
        'filterByFormula': "IS_SAME('" + date + "', {Date}, 'day')"
    }
    response = requests.post(rota_tbl_url + '/listRecords', headers=headers, json=data)

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

def get_rota_for_employee_and_day(date, employee_id):
    global airtable_key
    rota_tbl_url = 'https://api.airtable.com/v0/appLwrU5u2KrHXkAd/Rota'
    headers = {
        'Authorization': f'Bearer {airtable_key}',
        'Content-Type': 'application/json'
    }
    # Only return rows for which the date is the same as the input date and the
    # EmployeeID matches the input id
    data = {
        'filterByFormula': "AND(IS_SAME('" + date + "', {Date}, 'day'), " + employee_id + " = {Employee ID})"
    }
    response = requests.post(rota_tbl_url + '/listRecords', headers=headers, json=data)

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

def write_to_rota_table(records):
    # Write records to airtable
    global airtable_key
    rota_tbl_url = 'https://api.airtable.com/v0/appLwrU5u2KrHXkAd/Rota'

    print("Todo: Write to airtable")
