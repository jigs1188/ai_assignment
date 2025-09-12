import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
import json

class EmployeeAPITestCase(APITestCase):
    
    def setUp(self):
        self.base_url = '/api/employees/'
        self.sample_employee = {
            "employee_id": "TEST001",
            "name": "Test Employee",
            "email": "test@example.com",
            "department": "Engineering",
            "position": "Software Developer",
            "salary": 70000,
            "skills": ["Python", "Django"],
            "joining_date": "2023-01-01",
            "is_active": True
        }
    
    def test_create_employee_success(self):
        """
        Test successful employee creation.
        """
        response = self.client.post(
            self.base_url,
            data=json.dumps(self.sample_employee),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('employee_id', response.data)
    
    def test_create_employee_duplicate_id(self):
        """
        Test creating employee with duplicate ID.
        """
        # Create first employee
        self.client.post(
            self.base_url,
            data=json.dumps(self.sample_employee),
            content_type='application/json'
        )
        
        # Try to create duplicate
        response = self.client.post(
            self.base_url,
            data=json.dumps(self.sample_employee),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)
    
    def test_get_employee_success(self):
        """
        Test retrieving an existing employee.
        """
        # Create employee first
        self.client.post(
            self.base_url,
            data=json.dumps(self.sample_employee),
            content_type='application/json'
        )
        
        # Get employee
        response = self.client.get(f"{self.base_url}TEST001/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['employee_id'], 'TEST001')
        self.assertEqual(response.data['name'], 'Test Employee')
    
    def test_get_employee_not_found(self):
        """
        Test retrieving a non-existent employee.
        """
        response = self.client.get(f"{self.base_url}NOTFOUND/")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('message', response.data)
    
    def test_update_employee_success(self):
        """
        Test successful employee update.
        """
        # Create employee first
        self.client.post(
            self.base_url,
            data=json.dumps(self.sample_employee),
            content_type='application/json'
        )
        
        # Update employee
        update_data = {
            "name": "Updated Name",
            "salary": 80000
        }
        
        response = self.client.put(
            f"{self.base_url}TEST001/",
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_delete_employee_success(self):
        """
        Test successful employee deletion.
        """
        # Create employee first
        self.client.post(
            self.base_url,
            data=json.dumps(self.sample_employee),
            content_type='application/json'
        )
        
        # Delete employee
        response = self.client.delete(f"{self.base_url}TEST001/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_list_employees(self):
        """
        Test listing employees.
        """
        response = self.client.get(self.base_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('employees', response.data)
        self.assertIn('pagination', response.data)
    
    def test_search_employees_by_skill(self):
        """
        Test searching employees by skill.
        """
        response = self.client.get(f"{self.base_url}search/?skill=Python")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('employees', response.data)
        self.assertIn('search_term', response.data)
    
    def test_department_statistics(self):
        """
        Test getting department statistics.
        """
        response = self.client.get(f"{self.base_url}department-stats/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('statistics', response.data)
    
    def test_health_check(self):
        """
        Test health check endpoint.
        """
        response = self.client.get(f"{self.base_url}health/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'healthy')

# You can run these tests with: python manage.py test employees
