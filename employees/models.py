"""
Employee Data Models and Validation

This file handles data validation for employee records.
Since I'm using MongoDB instead of Django models, I created custom validation.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import re

class EmployeeValidator:
    """
    This class contains all the validation methods for employee data.
    I made sure to validate everything before saving to database.
    """
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Checks if email format is valid using regex.
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    @staticmethod
    def validate_employee_id(employee_id: str) -> bool:
        """
        Validates employee ID format - should be alphanumeric and reasonable length.
        """
        if not employee_id or len(employee_id) < 3 or len(employee_id) > 10:
            return False
        return employee_id.isalnum()
    
    @staticmethod
    def validate_salary(salary: Any) -> bool:
        """
        Checks if salary is a positive number.
        """
        try:
            salary_num = float(salary)
            return salary_num > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_date(date_str: str) -> bool:
        """
        Validate date format (YYYY-MM-DD).
        """
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_skills(skills: Any) -> bool:
        """
        Validate skills field.
        Should be a list of strings.
        """
        if not isinstance(skills, list):
            return False
        
        # Check if all items in the list are strings
        return all(isinstance(skill, str) and len(skill.strip()) > 0 for skill in skills)

class EmployeeModel:
    """
    Represents an employee with all necessary fields and validation.
    This is our custom model since we're not using Django's ORM.
    """
    
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize employee with provided data.
        """
        self.data = data
        self.errors = []
    
    def validate(self) -> bool:
        """
        Validate all employee data.
        Returns True if all data is valid, False otherwise.
        """
        self.errors = []
        
        # Required fields validation
        required_fields = ['employee_id', 'name', 'email', 'department', 'position', 'salary']
        for field in required_fields:
            if field not in self.data or not self.data[field]:
                self.errors.append(f"{field} is required")
        
        # If required fields are missing, don't proceed with other validations
        if self.errors:
            return False
        
        # Employee ID validation
        if not EmployeeValidator.validate_employee_id(self.data['employee_id']):
            self.errors.append("Employee ID must be alphanumeric and 3-10 characters long")
        
        # Email validation
        if not EmployeeValidator.validate_email(self.data['email']):
            self.errors.append("Invalid email format")
        
        # Salary validation
        if not EmployeeValidator.validate_salary(self.data['salary']):
            self.errors.append("Salary must be a positive number")
        
        # Skills validation (if provided)
        if 'skills' in self.data and self.data['skills']:
            if not EmployeeValidator.validate_skills(self.data['skills']):
                self.errors.append("Skills must be a list of non-empty strings")
        
        # Joining date validation (if provided)
        if 'joining_date' in self.data and self.data['joining_date']:
            if not EmployeeValidator.validate_date(self.data['joining_date']):
                self.errors.append("Joining date must be in YYYY-MM-DD format")
        
        return len(self.errors) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert employee data to dictionary format for MongoDB storage.
        Also adds default values and timestamps.
        """
        # Set default values
        employee_dict = {
            'employee_id': self.data['employee_id'],
            'name': self.data['name'].strip(),
            'email': self.data['email'].strip().lower(),
            'department': self.data['department'].strip(),
            'position': self.data['position'].strip(),
            'salary': float(self.data['salary']),
            'skills': self.data.get('skills', []),
            'joining_date': self.data.get('joining_date', datetime.now().strftime('%Y-%m-%d')),
            'is_active': self.data.get('is_active', True),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        return employee_dict
    
    def get_errors(self) -> List[str]:
        """
        Get list of validation errors.
        """
        return self.errors

def prepare_employee_for_update(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare employee data for update operation.
    Only includes fields that are being updated and adds timestamp.
    """
    update_data = {}
    
    # List of fields that can be updated
    updatable_fields = ['name', 'email', 'department', 'position', 'salary', 'skills', 'is_active']
    
    for field in updatable_fields:
        if field in data:
            if field == 'email':
                update_data[field] = data[field].strip().lower()
            elif field == 'name' or field == 'department' or field == 'position':
                update_data[field] = data[field].strip()
            elif field == 'salary':
                update_data[field] = float(data[field])
            else:
                update_data[field] = data[field]
    
    # Always update the timestamp
    update_data['updated_at'] = datetime.now().isoformat()
    
    return update_data

def validate_update_data(data: Dict[str, Any]) -> List[str]:
    """
    Validate data for update operations.
    Returns list of validation errors.
    """
    errors = []
    
    # Validate email if provided
    if 'email' in data and not EmployeeValidator.validate_email(data['email']):
        errors.append("Invalid email format")
    
    # Validate salary if provided
    if 'salary' in data and not EmployeeValidator.validate_salary(data['salary']):
        errors.append("Salary must be a positive number")
    
    # Validate skills if provided
    if 'skills' in data and not EmployeeValidator.validate_skills(data['skills']):
        errors.append("Skills must be a list of non-empty strings")
    
    return errors
