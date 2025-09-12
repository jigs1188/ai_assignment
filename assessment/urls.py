"""
URL configuration for Employee Management System.

This file contains the main URL routing for my application.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    """
    Root endpoint that shows available API endpoints.
    """
    return JsonResponse({
        'message': 'Welcome to Employee Management System API',
        'version': '1.0',
        'endpoints': {
            'employees': '/api/employees/',
            'admin': '/admin/',
            'docs': 'See README.md for API documentation'
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),
    path('employees/', include('employees.urls')),
]
