from importlib import import_module
from decimal import Decimal
from django.contrib.auth.models import AnonymousUser, Group, User
from django.db import migrations
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.services import (
    PLACEMENT_INCHARGE_GROUP_NAME,
    ROLE_ANONYMOUS,
    ROLE_PLACEMENT_INCHARGE,
    ROLE_STAFF,
    ROLE_STUDENT,
    ROLE_USER,
    get_user_role,
    is_placement_incharge,
)
from students.models import StudentProfile


class PlacementInchargeRoleTests(TestCase):
    def setUp(self):
        self.incharge_group = Group.objects.get(name=PLACEMENT_INCHARGE_GROUP_NAME)

    def test_placement_incharge_group_seeded_by_migration(self):
        """Verify the 'Placement Incharge' group was created by the initial migration."""
        self.assertTrue(
            Group.objects.filter(name=PLACEMENT_INCHARGE_GROUP_NAME).exists()
        )

    def test_migration_reverse_operation_is_noop(self):
        """Verify the migration's reverse_code is non-destructive (noop)."""
        migration_module = import_module('accounts.migrations.0001_initial')
        migration = migration_module.Migration('0001_initial', 'accounts')
        self.assertEqual(len(migration.operations), 1)
        operation = migration.operations[0]
        self.assertIsInstance(operation, migrations.RunPython)
        self.assertIs(operation.reverse_code, migrations.RunPython.noop)

    def test_group_member_gets_placement_incharge_role(self):
        """A user in 'Placement Incharge' group has incharge status and role."""
        user = User.objects.create_user(
            username='incharge_user',
            email='incharge@example.com',
            password='password123'
        )
        user.groups.add(self.incharge_group)

        self.assertTrue(is_placement_incharge(user))
        self.assertEqual(get_user_role(user), ROLE_PLACEMENT_INCHARGE)

    def test_superuser_gets_placement_incharge_role(self):
        """A superuser has incharge status and role even without explicit group membership."""
        superuser = User.objects.create_superuser(
            username='admin_user',
            email='admin@example.com',
            password='password123'
        )

        self.assertTrue(is_placement_incharge(superuser))
        self.assertEqual(get_user_role(superuser), ROLE_PLACEMENT_INCHARGE)

    def test_staff_user_without_group_is_not_placement_incharge(self):
        """A staff user without group membership must NOT get PLACEMENT_INCHARGE."""
        staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@example.com',
            password='password123',
            is_staff=True
        )

        self.assertFalse(is_placement_incharge(staff_user))
        self.assertEqual(get_user_role(staff_user), ROLE_STAFF)
        self.assertNotEqual(get_user_role(staff_user), ROLE_PLACEMENT_INCHARGE)

    def test_student_gets_student_role(self):
        """A user with an associated StudentProfile gets STUDENT role."""
        student_user = User.objects.create_user(
            username='student_user',
            email='student@example.com',
            password='password123'
        )
        StudentProfile.objects.create(
            user=student_user,
            full_name="Jane Doe",
            registration_number="REG99999",
            college_code="ENG01",
            roll_number="21CS099",
            department="Computer Science",
            batch="2021-2025",
            cgpa=Decimal("8.50"),
            history_of_arrears=0,
            standing_arrears=0,
            verification_status="PENDING"
        )

        self.assertFalse(is_placement_incharge(student_user))
        self.assertEqual(get_user_role(student_user), ROLE_STUDENT)

    def test_ordinary_authenticated_user_gets_user_role(self):
        """An ordinary authenticated user gets USER role."""
        user = User.objects.create_user(
            username='regular_user',
            email='regular@example.com',
            password='password123'
        )

        self.assertFalse(is_placement_incharge(user))
        self.assertEqual(get_user_role(user), ROLE_USER)

    def test_anonymous_user_returns_anonymous_role(self):
        """AnonymousUser instance returns False for incharge and ANONYMOUS role."""
        anon = AnonymousUser()

        self.assertFalse(is_placement_incharge(anon))
        self.assertEqual(get_user_role(anon), ROLE_ANONYMOUS)

    def test_none_user_returns_anonymous_role(self):
        """Passing None safely returns False for incharge and ANONYMOUS role."""
        self.assertFalse(is_placement_incharge(None))
        self.assertEqual(get_user_role(None), ROLE_ANONYMOUS)

    def test_role_precedence_incharge_over_student(self):
        """Incharge role takes precedence over student profile if user has both."""
        dual_user = User.objects.create_user(
            username='dual_user',
            email='dual@example.com',
            password='password123'
        )
        dual_user.groups.add(self.incharge_group)
        StudentProfile.objects.create(
            user=dual_user,
            full_name="Dual User",
            registration_number="REG88888",
            college_code="ENG01",
            roll_number="21CS088",
            department="Computer Science",
            batch="2021-2025",
            verification_status="PENDING"
        )

        self.assertTrue(is_placement_incharge(dual_user))
        self.assertEqual(get_user_role(dual_user), ROLE_PLACEMENT_INCHARGE)


class LoginAPITests(APITestCase):
    def setUp(self):
        self.incharge_group = Group.objects.get(name=PLACEMENT_INCHARGE_GROUP_NAME)
        self.password = "StrongPassword123!"

        # Create student user
        self.student_user = User.objects.create_user(
            username='student_user',
            email='student@example.com',
            password=self.password
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            full_name="Jane Doe",
            registration_number="REG12345",
            college_code="ENG01",
            roll_number="21CS001",
            department="Computer Science",
            batch="2021-2025",
            cgpa=Decimal("8.50"),
            history_of_arrears=0,
            standing_arrears=0,
            verification_status="PENDING"
        )

        # Create Placement Incharge user
        self.incharge_user = User.objects.create_user(
            username='incharge_user',
            email='incharge@college.edu',
            password=self.password
        )
        self.incharge_user.groups.add(self.incharge_group)

        # Create Superuser
        self.admin_user = User.objects.create_superuser(
            username='admin_user',
            email='admin@college.edu',
            password=self.password
        )

        # Create Staff user (no incharge group)
        self.staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@college.edu',
            password=self.password,
            is_staff=True
        )

        # Create Ordinary user
        self.ordinary_user = User.objects.create_user(
            username='ordinary_user',
            email='ordinary@example.com',
            password=self.password
        )

    def test_student_login_success(self):
        """Student login returns 200, JWT tokens, STUDENT role, and safe profile summary."""
        response = self.client.post('/api/auth/login/', {
            'email': 'student@example.com',
            'password': self.password,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

        user_data = response.data['user']
        self.assertEqual(user_data['id'], self.student_user.id)
        self.assertEqual(user_data['email'], 'student@example.com')
        self.assertEqual(user_data['role'], 'STUDENT')

        profile_data = user_data['student_profile']
        self.assertIsNotNone(profile_data)
        self.assertEqual(profile_data['registration_number'], 'REG12345')
        self.assertEqual(profile_data['full_name'], 'Jane Doe')
        self.assertEqual(profile_data['college_code'], 'ENG01')
        self.assertEqual(profile_data['verification_status'], 'PENDING')

        # Ensure sensitive fields are not exposed
        self.assertNotIn('password', response.data)
        self.assertNotIn('password', user_data)

    def test_real_integration_bearer_token_calls_students_me(self):
        """Real integration test: log in, take access token, call GET /api/students/me/ with Bearer header."""
        login_response = self.client.post('/api/auth/login/', {
            'email': 'student@example.com',
            'password': self.password,
        }, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access_token = login_response.data['access']

        # Set Bearer token and call protected student profile endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_response = self.client.get('/api/students/me/')
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['registration_number'], 'REG12345')
        self.assertEqual(profile_response.data['full_name'], 'Jane Doe')

    def test_placement_incharge_login_success(self):
        """Placement incharge login returns 200, tokens, PLACEMENT_INCHARGE role, and student_profile=None."""
        response = self.client.post('/api/auth/login/', {
            'email': 'incharge@college.edu',
            'password': self.password,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['role'], 'PLACEMENT_INCHARGE')
        self.assertIsNone(response.data['user']['student_profile'])

    def test_superuser_login_success(self):
        """Superuser login returns 200, tokens, PLACEMENT_INCHARGE role, and student_profile=None."""
        response = self.client.post('/api/auth/login/', {
            'email': 'admin@college.edu',
            'password': self.password,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['role'], 'PLACEMENT_INCHARGE')
        self.assertIsNone(response.data['user']['student_profile'])

    def test_staff_without_group_login_success(self):
        """Staff user without incharge group receives STAFF role, never PLACEMENT_INCHARGE."""
        response = self.client.post('/api/auth/login/', {
            'email': 'staff@college.edu',
            'password': self.password,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['role'], 'STAFF')
        self.assertNotEqual(response.data['user']['role'], 'PLACEMENT_INCHARGE')
        self.assertIsNone(response.data['user']['student_profile'])

    def test_ordinary_user_login_success(self):
        """Ordinary user receives USER role and student_profile=None."""
        response = self.client.post('/api/auth/login/', {
            'email': 'ordinary@example.com',
            'password': self.password,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['role'], 'USER')
        self.assertIsNone(response.data['user']['student_profile'])

    def test_email_normalization_login(self):
        """Email with leading/trailing spaces and mixed casing authenticates properly."""
        response = self.client.post('/api/auth/login/', {
            'email': '  STUDENT@EXAMPLE.COM  ',
            'password': self.password,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], 'student@example.com')

    def test_invalid_password_returns_401(self):
        """Correct email but wrong password returns 401 with generic error."""
        response = self.client.post('/api/auth/login/', {
            'email': 'student@example.com',
            'password': 'WrongPassword123!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data['detail'],
            "No active account found with the given credentials"
        )

    def test_nonexistent_email_returns_401(self):
        """Nonexistent email returns 401 with identical generic error."""
        response = self.client.post('/api/auth/login/', {
            'email': 'nobody@example.com',
            'password': self.password,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data['detail'],
            "No active account found with the given credentials"
        )

    def test_inactive_user_returns_401(self):
        """Inactive user account explicitly returns 401 without issuing tokens."""
        self.student_user.is_active = False
        self.student_user.save()

        response = self.client.post('/api/auth/login/', {
            'email': 'student@example.com',
            'password': self.password,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "User account is disabled.")

    def test_duplicate_email_rejected_with_401(self):
        """Multiple users sharing identical email returns 401; neither receives tokens."""
        User.objects.create_user(
            username='dup_user_1',
            email='duplicate@example.com',
            password=self.password
        )
        User.objects.create_user(
            username='dup_user_2',
            email='duplicate@example.com',
            password=self.password
        )

        response = self.client.post('/api/auth/login/', {
            'email': 'duplicate@example.com',
            'password': self.password,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data['detail'],
            "No active account found with the given credentials"
        )

    def test_missing_email_returns_400(self):
        """Missing email returns 400 Bad Request."""
        response = self.client.post('/api/auth/login/', {
            'password': self.password,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_missing_password_returns_400(self):
        """Missing password returns 400 Bad Request."""
        response = self.client.post('/api/auth/login/', {
            'email': 'student@example.com',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_login_succeeds_even_with_stale_bearer_token(self):
        """Stale or invalid Bearer token in header does not block public login."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer stale_invalid_token_12345')
        response = self.client.post('/api/auth/login/', {
            'email': 'student@example.com',
            'password': self.password,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class TokenRefreshAndLogoutAPITests(APITestCase):
    def setUp(self):
        self.password = "StrongPassword123!"
        self.user = User.objects.create_user(
            username='refresh_user',
            email='refresh@example.com',
            password=self.password
        )
        self.profile = StudentProfile.objects.create(
            user=self.user,
            full_name="Refresh Tester",
            registration_number="REG55555",
            college_code="ENG01",
            roll_number="21CS055",
            department="Computer Science",
            batch="2021-2025",
            verification_status="PENDING"
        )
        # Login to obtain initial tokens
        login_response = self.client.post('/api/auth/login/', {
            'email': 'refresh@example.com',
            'password': self.password,
        }, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.initial_access = login_response.data['access']
        self.initial_refresh = login_response.data['refresh']

    def test_token_refresh_success(self):
        """Valid refresh token returns 200, a new access token, and a new rotated refresh token."""
        response = self.client.post('/api/auth/token/refresh/', {
            'refresh': self.initial_refresh,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertNotEqual(response.data['refresh'], self.initial_refresh)

    def test_token_rotation_blacklists_previous_refresh_token(self):
        """After rotation, submitting the previous refresh token is rejected as blacklisted."""
        refresh_response = self.client.post('/api/auth/token/refresh/', {
            'refresh': self.initial_refresh,
        }, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)

        # Attempt to use the original (now previous) refresh token again
        reuse_response = self.client.post('/api/auth/token/refresh/', {
            'refresh': self.initial_refresh,
        }, format='json')
        self.assertEqual(reuse_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(reuse_response.data['detail'], 'Token is blacklisted')

    def test_newly_rotated_refresh_token_can_be_used(self):
        """The newly rotated refresh token can be used in subsequent refresh calls."""
        first_refresh = self.client.post('/api/auth/token/refresh/', {
            'refresh': self.initial_refresh,
        }, format='json')
        self.assertEqual(first_refresh.status_code, status.HTTP_200_OK)
        second_refresh_token = first_refresh.data['refresh']

        second_refresh = self.client.post('/api/auth/token/refresh/', {
            'refresh': second_refresh_token,
        }, format='json')
        self.assertEqual(second_refresh.status_code, status.HTTP_200_OK)
        self.assertIn('access', second_refresh.data)
        self.assertIn('refresh', second_refresh.data)
        self.assertNotEqual(second_refresh.data['refresh'], second_refresh_token)

    def test_refreshed_access_token_authenticates_protected_view(self):
        """A newly issued access token from refresh successfully authenticates against /api/students/me/."""
        refresh_response = self.client.post('/api/auth/token/refresh/', {
            'refresh': self.initial_refresh,
        }, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        new_access_token = refresh_response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        profile_response = self.client.get('/api/students/me/')
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['registration_number'], 'REG55555')
        self.assertEqual(profile_response.data['full_name'], 'Refresh Tester')

    def test_refresh_rejects_invalid_token(self):
        """Invalid refresh token returns 401 Unauthorized."""
        response = self.client.post('/api/auth/token/refresh/', {
            'refresh': 'invalid_garbage_token_value',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], 'token_not_valid')

    def test_refresh_missing_field_returns_400(self):
        """Omitting 'refresh' field returns 400 Bad Request."""
        response = self.client.post('/api/auth/token/refresh/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('refresh', response.data)

    def test_refresh_succeeds_even_with_stale_bearer_header(self):
        """Stale or invalid Bearer token in header does not block token refresh."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer stale_or_expired_bearer_token')
        response = self.client.post('/api/auth/token/refresh/', {
            'refresh': self.initial_refresh,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_logout_success(self):
        """Valid refresh token blacklists token and returns 200 with confirmation detail."""
        response = self.client.post('/api/auth/logout/', {
            'refresh': self.initial_refresh,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'detail': 'Successfully logged out.'})

    def test_blacklisted_token_cannot_be_used_for_refresh(self):
        """After logout, the blacklisted refresh token cannot be used to refresh tokens."""
        logout_response = self.client.post('/api/auth/logout/', {
            'refresh': self.initial_refresh,
        }, format='json')
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

        refresh_response = self.client.post('/api/auth/token/refresh/', {
            'refresh': self.initial_refresh,
        }, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(refresh_response.data['detail'], 'Token is blacklisted')

    def test_repeated_logout_fails(self):
        """Submitting an already-blacklisted refresh token to logout returns 401."""
        first_logout = self.client.post('/api/auth/logout/', {
            'refresh': self.initial_refresh,
        }, format='json')
        self.assertEqual(first_logout.status_code, status.HTTP_200_OK)

        second_logout = self.client.post('/api/auth/logout/', {
            'refresh': self.initial_refresh,
        }, format='json')
        self.assertEqual(second_logout.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(second_logout.data['detail'], 'Token is blacklisted')

    def test_logout_rejects_invalid_token(self):
        """Invalid refresh token to logout returns 401 Unauthorized."""
        response = self.client.post('/api/auth/logout/', {
            'refresh': 'invalid_garbage_token_value',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], 'token_not_valid')

    def test_logout_missing_field_returns_400(self):
        """Omitting 'refresh' field to logout returns 400 Bad Request."""
        response = self.client.post('/api/auth/logout/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('refresh', response.data)

    def test_logout_succeeds_even_with_stale_bearer_header(self):
        """Stale or invalid Bearer token in header does not block logout."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer stale_or_expired_bearer_token')
        response = self.client.post('/api/auth/logout/', {
            'refresh': self.initial_refresh,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'detail': 'Successfully logged out.'})
