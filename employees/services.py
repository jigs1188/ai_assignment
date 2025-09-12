"""
Employee Service Layer

This file contains the business logic for all employee operations.
I separated this from the views to keep the code organized and reusable.
"""

from typing import Dict, List, Optional, Any
from pymongo.errors import DuplicateKeyError
from .database import employees_collection
from .models import EmployeeModel, prepare_employee_for_update, validate_update_data
import logging

logger = logging.getLogger(__name__)

# Sample data for testing when MongoDB is not connected
DEMO_EMPLOYEES = {
    "E123": {
        "employee_id": "E123",
        "name": "John Doe",
        "position": "Software Engineer",
        "department": "Engineering",
        "salary": 75000,
        "skills": ["Python", "Django", "MongoDB"],
        "hire_date": "2023-01-15",
        "email": "john.doe@company.com",
        "status": "active"
    },
    "E124": {
        "employee_id": "E124", 
        "name": "Jane Smith",
        "position": "Frontend Developer",
        "department": "Engineering",
        "salary": 70000,
        "skills": ["JavaScript", "React", "CSS"],
        "hire_date": "2023-02-01",
        "email": "jane.smith@company.com",
        "status": "active"
    },
    "E125": {
        "employee_id": "E125",
        "name": "Bob Wilson",
        "position": "Product Manager", 
        "department": "Product",
        "salary": 85000,
        "skills": ["Strategy", "Analytics", "Communication"],
        "hire_date": "2022-12-01",
        "email": "bob.wilson@company.com",
        "status": "active"
    }
}

class EmployeeService:
    """
    This class handles all the employee business logic.
    I kept it separate from views to make the code more organized.
    """
    
    @staticmethod
    def create_employee(employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new employee after validating all the data.
        Returns success/error status with appropriate messages.
        """
        try:
            # First, validate all the input data
            employee = EmployeeModel(employee_data)
            
            if not employee.validate():
                return {
                    'success': False,
                    'message': 'Validation failed',
                    'errors': employee.get_errors()
                }
            
            # Check if MongoDB is available
            if employees_collection is None:
                # Use fallback storage for demo
                employee_id = employee_data['employee_id']
                
                # Check if employee already exists in demo data
                if employee_id in DEMO_EMPLOYEES:
                    return {
                        'success': False,
                        'message': 'Employee with this ID already exists',
                        'errors': ['Duplicate employee ID']
                    }
                
                # Add to demo storage
                DEMO_EMPLOYEES[employee_id] = employee.to_dict()
                logger.info(f"Employee created in demo mode: {employee_id}")
                return {
                    'success': True,
                    'message': 'Employee created successfully (demo mode)',
                    'employee_id': employee_id
                }
            
            # MongoDB is available - use real database
            # Check if employee with same ID already exists
            existing_employee = employees_collection.find_one(
                {"employee_id": employee_data['employee_id']}
            )
            
            if existing_employee:
                return {
                    'success': False,
                    'message': 'Employee with this ID already exists',
                    'errors': ['Duplicate employee ID']
                }
            
            # Check if employee with same email already exists
            existing_email = employees_collection.find_one(
                {"email": employee_data['email'].lower()}
            )
            
            if existing_email:
                return {
                    'success': False,
                    'message': 'Employee with this email already exists',
                    'errors': ['Duplicate email address']
                }
            
            # Insert the employee into database
            employee_dict = employee.to_dict()
            result = employees_collection.insert_one(employee_dict)
            
            if result.inserted_id:
                logger.info(f"Employee created successfully: {employee_data['employee_id']}")
            if result.inserted_id:
                logger.info(f"Employee created successfully: {employee_data['employee_id']}")
                return {
                    'success': True,
                    'message': 'Employee created successfully',
                    'employee_id': employee_data['employee_id']
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to create employee',
                    'errors': ['Database insertion failed']
                }
                
        except DuplicateKeyError:
            return {
                'success': False,
                'message': 'Employee with this ID or email already exists',
                'errors': ['Duplicate key error']
            }
        except Exception as e:
            logger.error(f"Error creating employee: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error',
                'errors': [str(e)]
            }
    
    @staticmethod
    def get_employee_by_id(employee_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an employee by their ID.
        
        Args:
            employee_id: The unique employee identifier
            
        Returns:
            Employee data dictionary or None if not found
        """
        try:
            # Check if database is available
            if employees_collection is None:
                # Use fallback demo data
                employee = DEMO_EMPLOYEES.get(employee_id)
                if employee:
                    logger.info(f"Employee retrieved from demo data: {employee_id}")
                return employee
            
            # Find employee and exclude MongoDB's internal _id field
            employee = employees_collection.find_one(
                {"employee_id": employee_id},
                {"_id": 0}  # Exclude the MongoDB ObjectId from response
            )
            
            if employee:
                logger.info(f"Employee retrieved: {employee_id}")
            
            return employee
            
        except Exception as e:
            logger.error(f"Error retrieving employee {employee_id}: {str(e)}")
            return None
    
    @staticmethod
    def update_employee(employee_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing employee's information.
        
        Args:
            employee_id: The unique employee identifier
            update_data: Dictionary containing fields to update
            
        Returns:
            Dictionary with success/error status and message
        """
        try:
            # Validate the update data
            validation_errors = validate_update_data(update_data)
            if validation_errors:
                return {
                    'success': False,
                    'message': 'Validation failed',
                    'errors': validation_errors
                }
            
            # Prepare the data for update (clean and format)
            prepared_data = prepare_employee_for_update(update_data)
            
            # Check if trying to update email to an existing one
            if 'email' in prepared_data:
                existing_email = employees_collection.find_one({
                    "email": prepared_data['email'],
                    "employee_id": {"$ne": employee_id}  # Exclude current employee
                })
                
                if existing_email:
                    return {
                        'success': False,
                        'message': 'Email already exists for another employee',
                        'errors': ['Duplicate email address']
                    }
            
            # Update the employee
            result = employees_collection.update_one(
                {"employee_id": employee_id},
                {"$set": prepared_data}
            )
            
            if result.matched_count == 0:
                return {
                    'success': False,
                    'message': 'Employee not found',
                    'errors': ['Employee does not exist']
                }
            
            if result.modified_count > 0:
                logger.info(f"Employee updated successfully: {employee_id}")
                return {
                    'success': True,
                    'message': 'Employee updated successfully'
                }
            else:
                return {
                    'success': True,
                    'message': 'No changes made (data was identical)'
                }
                
        except Exception as e:
            logger.error(f"Error updating employee {employee_id}: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error',
                'errors': [str(e)]
            }
    
    @staticmethod
    def delete_employee(employee_id: str) -> Dict[str, Any]:
        """
        Delete an employee from the database.
        
        Args:
            employee_id: The unique employee identifier
            
        Returns:
            Dictionary with success/error status and message
        """
        try:
            # Delete the employee
            result = employees_collection.delete_one({"employee_id": employee_id})
            
            if result.deleted_count == 0:
                return {
                    'success': False,
                    'message': 'Employee not found',
                    'errors': ['Employee does not exist']
                }
            
            logger.info(f"Employee deleted successfully: {employee_id}")
            return {
                'success': True,
                'message': 'Employee deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"Error deleting employee {employee_id}: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error',
                'errors': [str(e)]
            }
    
    @staticmethod
    def list_employees(department: Optional[str] = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Get a list of employees with optional filtering and pagination.
        
        Args:
            department: Optional department filter
            limit: Maximum number of employees to return
            offset: Number of employees to skip (for pagination)
            
        Returns:
            Dictionary containing employee list and pagination info
        """
        try:
            # Check if database is available
            if employees_collection is None:
                return {
                    'success': True,
                    'employees': [],
                    'pagination': {
                        'total': 0,
                        'limit': limit,
                        'offset': offset,
                        'has_next': False,
                        'has_previous': False
                    },
                    'message': 'Database not available. Please start MongoDB to see employee data.'
                }
            
            # Build query filter
            query = {}
            if department:
                # Case-insensitive department search
                query["department"] = {"$regex": f"^{department}$", "$options": "i"}
            
            # Get total count for pagination
            total_count = employees_collection.count_documents(query)
            
            # Get employees with pagination and sorting
            employees = list(employees_collection.find(
                query,
                {"_id": 0}  # Exclude MongoDB ObjectId
            ).sort("joining_date", -1).skip(offset).limit(limit))
            
            logger.info(f"Listed {len(employees)} employees (department: {department})")
            
            return {
                'success': True,
                'employees': employees,
                'pagination': {
                    'total': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_next': (offset + limit) < total_count,
                    'has_previous': offset > 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error listing employees: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to retrieve employees',
                'errors': [str(e)]
            }
    
    @staticmethod
    def search_employees_by_skill(skill: str) -> Dict[str, Any]:
        """
        Search for employees who have a specific skill.
        
        Args:
            skill: The skill to search for
            
        Returns:
            Dictionary containing matching employees
        """
        try:
            # Check if database is available
            if employees_collection is None:
                return {
                    'success': True,
                    'employees': [],
                    'search_term': skill,
                    'count': 0,
                    'message': 'Database not available. Please start MongoDB to search employees.'
                }
            
            # Case-insensitive skill search
            employees = list(employees_collection.find(
                {"skills": {"$regex": f"^{skill}$", "$options": "i"}},
                {"_id": 0}
            ).sort("name", 1))
            
            logger.info(f"Found {len(employees)} employees with skill: {skill}")
            
            return {
                'success': True,
                'employees': employees,
                'search_term': skill,
                'count': len(employees)
            }
            
        except Exception as e:
            logger.error(f"Error searching employees by skill {skill}: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error',
                'errors': [str(e)]
            }
    
    @staticmethod
    def get_department_statistics() -> Dict[str, Any]:
        """
        Get statistics about employees grouped by department.
        This includes average salary, employee count, etc.
        
        Returns:
            Dictionary containing department statistics
        """
        try:
            # Check if database is available
            if employees_collection is None:
                return {
                    'success': True,
                    'statistics': [],
                    'total_departments': 0,
                    'message': 'Database not available. Please start MongoDB to see department statistics.'
                }
            
            # MongoDB aggregation pipeline to calculate department stats
            pipeline = [
                # Group by department and calculate statistics
                {
                    "$group": {
                        "_id": "$department",
                        "average_salary": {"$avg": "$salary"},
                        "employee_count": {"$sum": 1},
                        "total_salary": {"$sum": "$salary"},
                        "min_salary": {"$min": "$salary"},
                        "max_salary": {"$max": "$salary"}
                    }
                },
                # Format the output
                {
                    "$project": {
                        "_id": 0,
                        "department": "$_id",
                        "average_salary": {"$round": ["$average_salary", 2]},
                        "employee_count": 1,
                        "total_salary": 1,
                        "min_salary": 1,
                        "max_salary": 1
                    }
                },
                # Sort by department name
                {
                    "$sort": {"department": 1}
                }
            ]
            
            statistics = list(employees_collection.aggregate(pipeline))
            
            logger.info(f"Generated statistics for {len(statistics)} departments")
            
            return {
                'success': True,
                'statistics': statistics,
                'total_departments': len(statistics)
            }
            
        except Exception as e:
            logger.error(f"Error getting department statistics: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error',
                'errors': [str(e)]
            }
    
    @staticmethod
    def get_average_salary_by_department() -> Dict[str, Any]:
        """
        Get average salary by department using MongoDB aggregation.
        Returns data in the exact format required by assignment:
        [
            {"department": "Engineering", "avg_salary": 80000},
            {"department": "HR", "avg_salary": 60000}
        ]
        """
        try:
            # Check if database is available
            if employees_collection is None:
                return {
                    'success': True,
                    'data': [],
                    'message': 'Database not available. Please start MongoDB to see salary statistics.'
                }
            
            # MongoDB aggregation pipeline for average salary by department
            pipeline = [
                {
                    "$group": {
                        "_id": "$department",
                        "avg_salary": {"$avg": "$salary"}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "department": "$_id",
                        "avg_salary": {"$round": ["$avg_salary", 0]}
                    }
                },
                {
                    "$sort": {"department": 1}
                }
            ]
            
            result = list(employees_collection.aggregate(pipeline))
            
            logger.info(f"Generated average salary statistics for {len(result)} departments")
            
            return {
                'success': True,
                'data': result
            }
            
        except Exception as e:
            logger.error(f"Error calculating average salary by department: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to calculate average salary',
                'errors': [str(e)]
            }
