from airtable import get_employee_data, get_floor_data, get_task_data
from scheduler import gen_rota_for_floor

if __name__ == '__main__':
    employee_data = get_employee_data()
    floor_data = get_floor_data()
    task_data = get_task_data()

    records, records2 = gen_rota_for_floor('2023-12-20', employee_data, task_data, floor_data, 'Basement')
