from airtable import get_employee_data, get_floor_data, get_task_data
from scheduler import gen_rota_for_date_range, gen_rota_for_date

if __name__ == '__main__':
    employee_data = get_employee_data()
    floor_data = get_floor_data()
    task_data = get_task_data()

    # gen_rota_for_date_range('2023-12-20', '2023-12-21', employee_data, task_data, floor_data)
    gen_rota_for_date('2023-12-20', employee_data, task_data, floor_data)
