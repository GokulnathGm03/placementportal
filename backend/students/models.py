from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class StudentProfile(models.Model):
    VERIFICATION_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    full_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=50)
    college_code = models.CharField(max_length=50, default='DEFAULT')
    roll_number = models.CharField(max_length=50)
    department = models.CharField(max_length=100)
    batch = models.CharField(max_length=20)
    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('10.00'))
        ]
    )
    history_of_arrears = models.PositiveIntegerField(default=0)
    standing_arrears = models.PositiveIntegerField(default=0)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['college_code', 'registration_number'],
                name='unique_college_student_reg'
            )
        ]

    def __str__(self):
        return f"{self.full_name} ({self.registration_number})"
