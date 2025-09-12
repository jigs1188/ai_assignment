"""
Employee API Views

This file contains the main API endpoints for managing employees.
I've implemented REST endpoints using Django REST Framework decorators.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .services import EmployeeService
import logging

logger = logging.getLogger(__name__)

@api_view(['GET', 'POST'])
def employees_list_create(request):
    """
    This handles both getting all employees and creating new ones.
    GET request returns a list of employees with optional filtering.
    POST request creates a new employee.
    """
    if request.method == 'GET':
        # Check if user wants to filter by department
        department = request.GET.get('department')
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        
        # Make sure pagination values are reasonable
        if limit < 1 or limit > 100:
            limit = 20
        if offset < 0:
            offset = 0
        
        # Get the employees from service layer
        result = EmployeeService.list_employees(department, limit, offset)
        
        if result['success']:
            return Response({
                'employees': result['employees'],
                'pagination': result['pagination']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': result['message'],
                'errors': result.get('errors', [])
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    elif request.method == 'POST':
        return create_employee(request)


@api_view(['GET', 'PUT', 'DELETE'])
def employee_detail(request, employee_id):
    """
    Handles operations on individual employees.
    This endpoint supports getting, updating, and deleting specific employees.
    """
    if request.method == 'GET':
        return get_employee(request, employee_id)
    elif request.method == 'PUT':
        return update_employee(request, employee_id)
    elif request.method == 'DELETE':
        return delete_employee(request, employee_id)

def create_employee(request):
    """
    Creates a new employee record.
    I validate all the required fields before saving to database.
    """
    try:
        # Get data from request body
        employee_data = request.data
        
        # Use service layer to create employee
        result = EmployeeService.create_employee(employee_data)
        
        if result['success']:
            return Response({
                'message': result['message'],
                'employee_id': result['employee_id']
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': result['message'],
                'errors': result.get('errors', [])
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Unexpected error in create_employee: {str(e)}")
        return Response({
            'message': 'Internal server error',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_employee(request, employee_id):
    """
    Retrieves a specific employee by their ID.
    Returns 404 if employee doesn't exist.
    """
    try:
        # Call service to get employee data
        employee = EmployeeService.get_employee_by_id(employee_id)
        
        if employee:
            return Response(employee, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'Employee not found',
                'employee_id': employee_id
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        logger.error(f"Error getting employee {employee_id}: {str(e)}")
        return Response({
            'message': 'Internal server error',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def update_employee(request, employee_id):
    """
    Update an existing employee's information.
    
    PUT /api/employees/{employee_id}/
    
    Expected JSON body (all fields are optional):
    {
        "name": "John Smith",
        "email": "john.smith@company.com",
        "department": "Engineering",
        "position": "Senior Software Engineer",
        "salary": 85000,
        "skills": ["Python", "Django", "MongoDB", "React"],
        "is_active": false
    }
    """
    try:
        # Get data from request body
        update_data = request.data
        
        # Use service layer to update employee
        result = EmployeeService.update_employee(employee_id, update_data)
        
        if result['success']:
            return Response({
                'message': result['message']
            }, status=status.HTTP_200_OK)
        else:
            # Check if it's a "not found" error
            if 'not found' in result['message'].lower():
                return Response({
                    'message': result['message'],
                    'employee_id': employee_id
                }, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    'message': result['message'],
                    'errors': result.get('errors', [])
                }, status=status.HTTP_400_BAD_REQUEST)
                
    except Exception as e:
        logger.error(f"Unexpected error in update_employee: {str(e)}")
        return Response({
            'message': 'Internal server error',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def delete_employee(request, employee_id):
    """
    Delete an employee.
    
    DELETE /api/employees/{employee_id}/
    """
    try:
        # Use service layer to delete employee
        result = EmployeeService.delete_employee(employee_id)
        
        if result['success']:
            return Response({
                'message': result['message']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': result['message'],
                'employee_id': employee_id
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        logger.error(f"Unexpected error in delete_employee: {str(e)}")
        return Response({
            'message': 'Internal server error',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def list_employees(request):
    """
    List all employees with optional filtering and pagination.
    
    GET /api/employees/
    
    Query parameters:
    - department: Filter by department (optional)
    - limit: Number of employees per page (default: 20)
    - offset: Number of employees to skip (default: 0)
    
    Examples:
    - GET /api/employees/ (all employees)
    - GET /api/employees/?department=Engineering (filter by department)
    - GET /api/employees/?limit=10&offset=20 (pagination)
    """
    try:
        # Get query parameters
        department = request.GET.get('department')
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        
        # Validate pagination parameters
        if limit < 1 or limit > 100:
            limit = 20  # Default limit
        if offset < 0:
            offset = 0  # Default offset
        
        # Use service layer to get employees
        result = EmployeeService.list_employees(department, limit, offset)
        
        if result['success']:
            return Response({
                'employees': result['employees'],
                'pagination': result['pagination']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': result['message'],
                'errors': result.get('errors', [])
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except ValueError:
        return Response({
            'message': 'Invalid pagination parameters',
            'error': 'limit and offset must be valid integers'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Unexpected error in list_employees: {str(e)}")
        return Response({
            'message': 'Internal server error',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def search_employees(request):
    """
    Search for employees by skill.
    
    GET /api/employees/search/
    
    Query parameters:
    - skill: The skill to search for (required)
    
    Example:
    - GET /api/employees/search/?skill=Python
    """
    try:
        # Get skill parameter
        skill = request.GET.get('skill')
        
        if not skill:
            return Response({
                'message': 'Skill parameter is required',
                'example': '/api/employees/search/?skill=Python'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Use service layer to search employees
        result = EmployeeService.search_employees_by_skill(skill.strip())
        
        if result['success']:
            return Response({
                'employees': result['employees'],
                'search_term': result['search_term'],
                'count': result['count']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': result['message'],
                'errors': result.get('errors', [])
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Unexpected error in search_employees: {str(e)}")
        return Response({
            'message': 'Internal server error',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def average_salary_by_department(request):
    """
    Get average salary by department using MongoDB aggregation.
    
    GET /employees/avg-salary
    
    Returns:
    [
        {"department": "Engineering", "avg_salary": 80000},
        {"department": "HR", "avg_salary": 60000}
    ]
    """
    try:
        # Use service layer to get statistics
        result = EmployeeService.get_average_salary_by_department()
        
        if result['success']:
            return Response(result['data'], status=status.HTTP_200_OK)
        else:
            return Response({
                'message': result['message'],
                'errors': result.get('errors', [])
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Unexpected error in average_salary_by_department: {str(e)}")
        return Response({
            'message': 'Internal server error',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def search_employees_by_skill(request):
    """
    Search for employees who have a specific skill.
    
    GET /employees/search?skill=Python
    """
    try:
        # Get skill parameter
        skill = request.GET.get('skill')
        
        if not skill:
            return Response({
                'message': 'Skill parameter is required',
                'example': '/employees/search?skill=Python'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Use service layer to search employees
        result = EmployeeService.search_employees_by_skill(skill.strip())
        
        if result['success']:
            return Response(result['employees'], status=status.HTTP_200_OK)
        else:
            return Response({
                'message': result['message'],
                'errors': result.get('errors', [])
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Unexpected error in search_employees_by_skill: {str(e)}")
        return Response({
            'message': 'Internal server error',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    """
    Get statistics about employees grouped by department.
    
    GET /api/employees/department-stats/
    
    Returns information like:
    - Average salary per department
    - Number of employees per department
    - Min/max salaries per department
    """
    try:
        # Use service layer to get statistics
        result = EmployeeService.get_department_statistics()
        
        if result['success']:
            return Response({
                'statistics': result['statistics'],
                'total_departments': result['total_departments']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': result['message'],
                'errors': result.get('errors', [])
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Unexpected error in department_statistics: {str(e)}")
        return Response({
            'message': 'Internal server error',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def health_check(request):
    """
    Simple health check endpoint to verify the API is working.
    
    GET /api/employees/health/
    """
    try:
        # You could add database connectivity check here
        return Response({
            'status': 'healthy',
            'message': 'Employee Management API is running',
            'timestamp': '2023-12-01T10:00:00Z'  # In real app, use actual timestamp
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return Response({
            'status': 'unhealthy',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
