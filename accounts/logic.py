from .models import User
from rest_framework.authtoken.models import Token


def register_user(data, request):
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data['email']
    password = data['password']
    
    # Register user
    User.objects.create_user(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
    )
    
    return {
        'success': True,
        'message': 'User registered successfully',
    }


def login_user(data, request):
    email = data['email']
    
    # Login user
    user = User.objects.filter(email=email).first()
    token, created = Token.objects.get_or_create(user=user)
    response = {
        'email': user.email,
        'token': token.key
    }
    
    return {
        'success': True,
        'message': 'User logged in successfully',
        'payload': response
    }
