
# Employee Management System

This is a simple Employee Management System built with Django REST Framework and MongoDB. I created this as a clean, functional API for managing employee data.

## Quick Setup

**Requirements:**
- Python 3.8+
- MongoDB (local)

**Installation:**
1. Clone or download this project
2. Run the setup script:
    ```
    setup.bat
    ```
    This will create a virtual environment, install dependencies, and start the server.

3. Make sure MongoDB is running:
    ```
    mongod --dbpath "C:\data\db"
    ```

4. Open the frontend:
    - Double-click `frontend/index.html` OR use Live Server in VS Code

---

## API Endpoints

**Database:**
- MongoDB (local)
- Database: `employee_management`
- Collection: `employees`

**Employee Structure:**
```json
{
  "employee_id": "E123",
  "name": "John Doe",
  "department": "Engineering",
  "salary": 75000,
  "joining_date": "2023-01-15",
  "skills": ["Python", "MongoDB", "APIs"]
}
```

**Available Endpoints:**

| Method | Endpoint                        | Description                  |
|--------|----------------------------------|------------------------------|
| POST   | /employees                      | Create employee              |
| GET    | /employees/{employee_id}        | Get employee by ID           |
| PUT    | /employees/{employee_id}        | Update employee              |
| DELETE | /employees/{employee_id}        | Delete employee              |
| GET    | /employees?department=Dept      | Filter by department         |
| GET    | /employees/avg-salary           | Average salary by department |
| GET    | /employees/search?skill=Python  | Search by skill              |

## Frontend

Simple HTML/CSS/JS interface:
- All API calls use `fetch()` to Django endpoints
- You can add, edit, delete, search, and filter employees
- Frontend is fully connected to backend (CORS enabled)
- All features required by the assignment are covered

**How Frontend Connects to Backend:**
- Base URL is configured in `frontend/js/app.js`
- Uses fetch API to communicate with Django backend

## Testing

You can test the API using:
- The frontend interface
- Postman or curl commands
- Browser developer tools

## Project Structure

```
employee_management_system/
├── assessment/      # Django project settings
├── employees/       # Main app with API logic
├── frontend/        # Simple HTML/CSS/JS interface
├── requirements.txt # Python dependencies
└── setup.bat       # Quick setup script
```

## Key Features

- Full CRUD operations for employees
- Department-based filtering
- Skill-based search
- Salary aggregation
- MongoDB integration
- Clean REST API design
│   ├── css/styles.css
└── README.md
