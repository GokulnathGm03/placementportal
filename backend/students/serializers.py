from rest_framework import serializers
from students.models import StudentProfile


class StudentProfileSerializer(serializers.ModelSerializer):
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
            'cgpa',
            'history_of_arrears',
            'standing_arrears',
            'verification_status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields
