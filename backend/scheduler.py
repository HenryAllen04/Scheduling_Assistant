from datetime import datetime, timedelta
from ortools.sat.python import cp_model
from airtable import (
    get_rota_record_ids_for_day,
    get_unavailabilty_data,
    delete_rota_records,
    write_to_rota_table
)

def gen_rota_for_date_range(start_date_str, end_date_str, employee_data, task_data, floors_data):
    # Convert string dates to datetime.date objects
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

    current_date = start_date
    while current_date <= end_date:
        print(f'---------Generating Rota for {current_date.strftime("%Y-%m-%d")}------------------')
        records = gen_rota_for_date(current_date.strftime("%Y-%m-%d"), employee_data, task_data, floors_data)
        print(f'---------Deleting existing Rota records if any for {current_date.strftime("%Y-%m-%d")}------------------')
        record_ids = get_rota_record_ids_for_day(current_date.strftime("%Y-%m-%d"))
        delete_rota_records(record_ids)
        print(f'---------Writing new Rota records for {current_date.strftime("%Y-%m-%d")}------------------')
        write_to_rota_table(records)
        print(f'---------Generating Rota for {current_date.strftime("%Y-%m-%d")} complete------------------')
        current_date += timedelta(days=1)

# ToDo: Handle failures
def gen_rota_for_date(date, employee_data, task_data, floors_data):
    records = []
    for floor in floors_data:
        print(f'*********Generating Rota for {floor}****************')
        floor_records = gen_rota_for_floor(date, employee_data, task_data, floors_data, floor)
        records.extend(floor_records)
    return records

# ToDo: Cleanup
def gen_rota_for_floor(date, employee_data, task_data, floors_data, floor):

    unavailability_data = get_unavailabilty_data(date)

    employees = {}
    for e in employee_data:
      if employee_data[e]['DefaultFloor'] == floor and e not in unavailability_data:
        employees[e] = employee_data[e]

    floor_data = floors_data[floor]

    # Create the model
    model = cp_model.CpModel()

    # Variables
    # Assignments: employee -> (time slot, task)
    assignments = {}
    for e in employees:
        for t in range(9, 17):
            for task in floor_data['Tasks List']:
                if task in employees[e]['Tasks']:
                    assignments[(e, t, task)] = model.NewBoolVar(f'assign_{e}_{t}_{floor}_{task}')

    # Breaks: employee -> time slot
    breaks = {}
    for e in employees:
        for t in range(11, 15):  # Breaks between 11am and 3pm
            breaks[(e, t)] = model.NewBoolVar(f'break_{e}_{t}')

    # Adding Constraints
    # 1. All tasks on a floor should have the required number of employees assigned throughout the day
    for task in floor_data['Tasks List']:
        for t in range(9, 17):
            model.Add(sum(assignments[(e, t, task)] for e in employees if task in employees[e]['Tasks']) ==
                      task_data[task]['Employees Required'])

    # 2. Each employee should not perform any given task for more than 2 back-to-back hours
    for e in employees:
      for task in floor_data['Tasks List']:
          if task in employees[e]['Tasks']:
              for start_time in range(9, 15):  # Check from 9 am to 2 pm (for 3-hour windows)
                  model.Add(sum(assignments[(e, t, task)]
                                for t in range(start_time, start_time + 3)) <= 2)

    # 3. Each employee should have an hour-long break every day
    for e in employees:
        model.Add(sum(breaks[(e, t)] for t in range(11, 15)) == 1)

    # 4. No task assignments during break time
    for e in employees:
        for t in range(11, 15):  # Breaks between 11am and 3pm
            for task in floor_data['Tasks List']:
                if task in employees[e]['Tasks']:
                    model.Add(assignments[(e, t, task)] == 0).OnlyEnforceIf(breaks[(e, t)])

    # 5.: Each employee is assigned at most one task per time slot
    for e in employees:
        for t in range(9, 17):
            model.Add(sum(assignments[(e, t, task)]
                          for task in floor_data['Tasks List'] if task in employees[e]['Tasks']) <= 1)

    # Run the solver
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Extracting and displaying the solution
    records = []
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for e in employees:
            for t in range(9, 17):
                is_on_break = False
                if t in range(11, 15):
                  is_on_break = solver.Value(breaks[(e, t)]) == 1
                assigned_tasks = []
                for task in floor_data['Tasks List']:
                    if task in employees[e]['Tasks']:
                      if solver.Value(assignments[(e, t, task)]) == 1:
                        assigned_tasks.append(task)

                if assigned_tasks and is_on_break:
                    print('********Error*************', 'Task during break')
                if not assigned_tasks and not is_on_break:
                    assigned_task = 'Roaming'
                elif len(assigned_tasks) > 1:
                    print('********Error*************', 'Multiple tasks')
                    print(assigned_tasks)
                elif len(assigned_tasks) == 1:
                    assigned_task = assigned_tasks[0]
                elif is_on_break:
                    assigned_task = 'Break'
                else:
                    print('********Error*************', 'Unhandled condition')

                records.append({
                    'fields': {
                        'Date': date,
                        'Employee ID': e,
                        'Employee Name': employees[e]['Name'],
                        'Start Time': f'{t}:00',
                        'End Time': f'{t+1}:00',
                        'Floor': floor,
                        'Task': assigned_task
                    }
                })
                # print(f'Employee {e} at {t}:00 - Floor: {floor} Task: {assigned_task}')
    elif status == cp_model.INFEASIBLE:
        print("No solution found: INFEASIBLE")
    elif status == cp_model.MODEL_INVALID:
        print("No solution found: MODEL_INVALID")
    else:
        print("No solution found: UNKNOWN")
    return records
