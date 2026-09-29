from decimal import Decimal
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from placements.models import Company, JobPosting


class CompanyAPITests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="Acme Corp",
            location="Bangalore",
            description="Innovative technology solutions",
        )

    def test_list_companies_returns_200_unauthenticated(self):
        response = self.client.get('/api/companies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_companies_empty(self):
        Company.objects.all().delete()
        response = self.client.get('/api/companies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_list_companies_returns_correct_fields(self):
        response = self.client.get('/api/companies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        first_item = response.data[0]
        self.assertIn('id', first_item)
        self.assertIn('name', first_item)
        self.assertIn('location', first_item)
        self.assertIn('description', first_item)
        self.assertIn('created_at', first_item)
        self.assertIn('updated_at', first_item)
        self.assertEqual(first_item['name'], "Acme Corp")
        self.assertEqual(first_item['location'], "Bangalore")

    def test_retrieve_company_returns_200_unauthenticated(self):
        response = self.client.get(f'/api/companies/{self.company.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.company.pk)
        self.assertEqual(response.data['name'], "Acme Corp")
        self.assertEqual(response.data['location'], "Bangalore")

    def test_retrieve_company_not_found_returns_404(self):
        response = self.client.get('/api/companies/999999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_company_list_no_write_methods(self):
        response = self.client.post('/api/companies/', {'name': 'New Corp'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_company_detail_no_write_methods(self):
        response = self.client.put(f'/api/companies/{self.company.pk}/', {'name': 'Updated Corp'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class JobPostingAPITests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="Tech Global",
            location="Chennai",
            description="Global tech firm",
        )
        self.active_job = JobPosting.objects.create(
            company=self.company,
            title="Software Engineer",
            description="Build scalable systems",
            ctc_lpa=Decimal("12.50"),
            bond_details="None",
            eligible_departments=["CSE", "IT"],
            eligibility_criteria="CGPA >= 7.5",
            application_deadline=timezone.now() + timezone.timedelta(days=10),
            is_active=True,
        )
        self.inactive_job = JobPosting.objects.create(
            company=self.company,
            title="Old Analyst",
            description="Closed position",
            ctc_lpa=Decimal("6.00"),
            bond_details="1 year",
            eligible_departments=["ECE"],
            eligibility_criteria="CGPA >= 6.0",
            application_deadline=timezone.now() - timezone.timedelta(days=5),
            is_active=False,
        )

    def test_list_jobs_returns_200_unauthenticated(self):
        response = self.client.get('/api/jobs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_jobs_only_returns_active(self):
        response = self.client.get('/api/jobs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = [job['id'] for job in response.data]
        self.assertIn(self.active_job.id, returned_ids)
        self.assertNotIn(self.inactive_job.id, returned_ids)

    def test_list_jobs_returns_correct_fields(self):
        response = self.client.get('/api/jobs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        first_item = response.data[0]
        self.assertIn('id', first_item)
        self.assertIn('title', first_item)
        self.assertIn('ctc_lpa', first_item)
        self.assertIn('company', first_item)
        self.assertIn('application_deadline', first_item)
        self.assertIn('eligible_departments', first_item)
        self.assertEqual(first_item['company']['name'], "Tech Global")

    def test_retrieve_active_job_returns_200_unauthenticated(self):
        response = self.client.get(f'/api/jobs/{self.active_job.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.active_job.id)
        self.assertEqual(response.data['title'], "Software Engineer")
        self.assertEqual(response.data['company']['name'], "Tech Global")

    def test_retrieve_inactive_job_returns_404(self):
        response = self.client.get(f'/api/jobs/{self.inactive_job.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_job_not_found_returns_404(self):
        response = self.client.get('/api/jobs/999999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_job_list_no_write_methods(self):
        response = self.client.post('/api/jobs/', {'title': 'New Job'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_job_detail_no_write_methods(self):
        response = self.client.put(f'/api/jobs/{self.active_job.id}/', {'title': 'Updated Job'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
