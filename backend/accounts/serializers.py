from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.services import get_user_role
from students.models import StudentProfile


class StudentProfileSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = [
            'id',
            'full_name',
            'registration_number',
            'college_code',
            'roll_number',
            'department',
            'batch',
            'verification_status',
        ]
        read_only_fields = fields


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate_email(self, value):
        return value.strip().lower()

    def validate(self, attrs):
        email = attrs.get('email', '').strip().lower()
        password = attrs.get('password', '')

        # Query matching users case-insensitively with a bounded query (at most two matches)
        matching_users = list(User.objects.filter(email__iexact=email)[:2])

        # Reject the login unless exactly one match exists; never arbitrarily select an account
        # when duplicate emails exist.
        if len(matching_users) != 1:
            raise AuthenticationFailed("No active account found with the given credentials")

        user = matching_users[0]

        # Verify password before issuing tokens
        if not user.check_password(password):
            raise AuthenticationFailed("No active account found with the given credentials")

        # Safeguard 1: Explicitly reject inactive users before issuing JWT tokens
        if not user.is_active:
            raise AuthenticationFailed("User account is disabled.")

        # Issue JWT tokens
        refresh = RefreshToken.for_user(user)

        # Determine role using accounts.services.get_user_role
        role = get_user_role(user)

        # Build student profile summary safely
        student_profile_data = None
        if hasattr(user, 'student_profile'):
            try:
                if user.student_profile is not None:
                    student_profile_data = StudentProfileSummarySerializer(user.student_profile).data
            except StudentProfile.DoesNotExist:
                student_profile_data = None

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'role': role,
                'student_profile': student_profile_data,
            }
        }
