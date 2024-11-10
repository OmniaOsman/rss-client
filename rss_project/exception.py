from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ImproperlyConfigured

def custom_exception_handler(exc, context):
    # Get the standard DRF exception response first
    response = exception_handler(exc, context)

    # Check if `exc.detail` has errors and format based on type
    if hasattr(exc, 'detail'):
        if isinstance(exc.detail, dict):
            # If detail is a dict, process each field's errors
            formatted_errors = {field: [str(error) for error in errors] for field, errors in exc.detail.items()}
            response.data = {
                'success': False,
                'message': formatted_errors
            }
        elif isinstance(exc.detail, list):
            # If detail is a list, process non-field errors
            response.data = {
                'success': False,
                'message': [str(error) for error in exc.detail]
            }

    # Handle ImproperlyConfigured exception
    elif isinstance(exc, ImproperlyConfigured):
        response.data = {
            'success': False,
            'message': str(exc)
        }
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return response
