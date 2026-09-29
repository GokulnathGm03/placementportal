from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from students.models import StudentProfile


class StudentProfileAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='password123'
        )
        self.profile = StudentProfile.objects.create(
            user=self.user,
            full_name="John Doe",
            registration_number="REG12345",
            college_code="ENG01",
            roll_number="21CS001",
            department="Computer Science",
            batch="2021-2025",
            cgpa=Decimal("8.50"),
            history_of_arrears=0,
            standing_arrears=0,
            verification_status="VERIFIED",
        )

    def test_unauthenticated_returns_403(self):
        response = self.client.get('/api/students/me/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_student_retrieves_own_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/students/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['registration_number'], "REG12345")
        self.assertEqual(response.data['full_name'], "John Doe")

    def test_response_excludes_user_field(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/students/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('user', response.data)
        self.assertNotIn('user_id', response.data)

    def test_response_contains_expected_fields(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/students/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_fields = {
            'id',
            'full_name',
            'registration_number',
            'college_code',
            'roll_number',
            'department',
            'batch',
            'cgpa',
            'history_of_arrears',
            'standing_arrears',
            'verification_status',
            'created_at',
            'updated_at',
        }
        self.assertEqual(set(response.data.keys()), expected_fields)

    def test_user_without_profile_returns_404(self):
        user_no_profile = User.objects.create_user(
            username='user2',
            password='password123'
        )
        self.client.force_authenticate(user=user_no_profile)
        response = self.client.get('/api/students/me/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_id_url_resolves(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/students/{self.profile.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_list_url_resolves(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/students/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_write_methods_allowed(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/students/me/', {'full_name': 'Hacked Name'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
