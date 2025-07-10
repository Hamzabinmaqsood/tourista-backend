# In users/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile

class RegisterSerializer(serializers.ModelSerializer):
    # We add a password2 field to confirm the password
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        # List the fields we want for registration
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True} # Ensures password is not sent back in response
        }

    def validate(self, attrs):
        """
        Check that the two password entries match.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # You can also add Django's built-in password validation here if you want
        # validate_password(attrs['password'])
        
        return attrs

    def create(self, validated_data):
        """
        Create and return a new user.
        """
        # We use create_user to handle password hashing automatically
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        # We don't need the password2 field anymore, so we remove it
        # validated_data.pop('password2') # Not needed since we don't pass it to create_user

        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        # List all the fields from your UserProfile model that you want to be viewable/editable
        fields = ['travel_style', 'budget', 'preferred_languages', 'avatar']

class UserSerializer(serializers.ModelSerializer):
    # Nest the profile serializer
    profile = UserProfileSerializer()

    class Meta:
        model = User
        # We only want to show these fields. We don't want to show the password hash!
        fields = ['id', 'username', 'email', 'profile']

    def update(self, instance, validated_data):
        # This custom update method allows us to update the nested profile
        profile_data = validated_data.pop('profile', {})
        profile = instance.profile

        # Update the User instance
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        # Update the UserProfile instance
        profile.travel_style = profile_data.get('travel_style', profile.travel_style)
        profile.budget = profile_data.get('budget', profile.budget)
        profile.preferred_languages = profile_data.get('preferred_languages', profile.preferred_languages)
        profile.avatar = profile_data.get('avatar', profile.avatar)
        profile.save()

        return instance