from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from .serializers import RegisterSerializer
from django.contrib.auth.models import User
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    """
    queryset = User.objects.all()
    # Anyone can access this view (permission to register)
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for viewing and updating the authenticated user's profile.
    Handles GET (retrieve) and PUT/PATCH (update) requests.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # This is the key part: only authenticated users can access this view
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Overrides the default get_object to return the current user.
        This ensures users can only ever see or edit their own profile.
        """
        return self.request.user

class LogoutView(generics.GenericAPIView):
    """
    API endpoint for logging out a user by blacklisting their refresh token.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            # The user must send their refresh token to be blacklisted
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": "An error occurred during logout."}, status=status.HTTP_400_BAD_REQUEST)

