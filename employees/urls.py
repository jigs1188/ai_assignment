"""
URL Configuration for Employee App

This file maps URLs to view functions for the employee API.
I organized the endpoints to match REST API best practices.
"""

from django.urls import path
from . import views

# URL patterns for employee endpoints
urlpatterns = [
    # Special endpoints - these need to come first so Django matches them correctly
    path('avg-salary/', views.average_salary_by_department, name='average_salary_by_department'),
    path('search/', views.search_employees_by_skill, name='search_employees_by_skill'),
    
    # Standard CRUD endpoints
    path('', views.employees_list_create, name='employees_list_create'),  # List/Create employees
    path('<str:employee_id>/', views.employee_detail, name='employee_detail'),  # Get/Update/Delete specific employee
]

# Django automatically routes to correct view method based on HTTP method (GET, POST, PUT, DELETE)
