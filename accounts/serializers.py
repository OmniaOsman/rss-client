from rest_framework import serializers
from accounts.models import User
from rss_project.utils import ResponseSerializer


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'password2']
        
    def validate(self, attrs):
        # password validation
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs
    
    
class RegisterSerializerResponse(ResponseSerializer):
    pass


class LoginResponse(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField()
    
    
class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()
    
    # check if user exists and password is correct
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = User.objects.filter(email=email).first()
            if user and user.check_password(password):
                attrs['user'] = user
            else:
                raise serializers.ValidationError("Invalid email or password")
        else:
            raise serializers.ValidationError("Email and password are required")

        return attrs
    

class LoginSerializerResponse(ResponseSerializer):
    payload = LoginResponse()


class UUIDSerializerResponse(ResponseSerializer):
    payload = serializers.UUIDField()


class LogoutSerializerResponse(ResponseSerializer):
    pass
