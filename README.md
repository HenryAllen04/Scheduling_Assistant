# Scheduling_Assistant

## Database Config
Database can be found in Airtable
### Tables Include: 
- Employee
  - EmployeeId (integer)
  - Name (string)
  - Floor (string)
  - Tasks (array)
  - Monday (string)
  - Tuesday (string)
  - Wednesday (string)
  - Thursday (string)
  - Friday (string)
  - Saturday (string)
  - Sunday (string)
- Tasks
  - name of Task (string) PK
  - employees required (integer)
- Floors
  - Name of Floor (string)
  - Tasks list (array)
  - total employees required (integer)
- Unavailability
  - EmployeeId (integer) FK
  - Start date (date)
  -End date (date)
- Rota
  - Date (date)
  - Time (string)
  - EmployeeId (Integer)
  - Name (string)
  - Floor (string)
  - Task (string)
