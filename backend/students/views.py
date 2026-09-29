from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from students.models import StudentProfile
from students.serializers import StudentProfileSerializer


class MyStudentProfileView(generics.RetrieveAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(StudentProfile, user=self.request.user)
