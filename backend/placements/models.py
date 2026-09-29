from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.name


class JobPosting(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='job_postings'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    ctc_lpa = models.DecimalField(max_digits=6, decimal_places=2)
    bond_details = models.TextField(blank=True)
    eligible_departments = models.JSONField(default=list, blank=True)
    eligibility_criteria = models.TextField(blank=True)
    application_deadline = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.company.name}"
