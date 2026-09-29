from rest_framework import serializers
from placements.models import Company, JobPosting


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'location',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class JobPostingSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = JobPosting
        fields = [
            'id',
            'company',
            'title',
            'description',
            'ctc_lpa',
            'bond_details',
            'eligible_departments',
            'eligibility_criteria',
            'application_deadline',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields
