from rest_framework import generics
from rest_framework.permissions import AllowAny
from placements.models import Company, JobPosting
from placements.serializers import CompanySerializer, JobPostingSerializer


class CompanyListView(generics.ListAPIView):
    queryset = Company.objects.all().order_by('name')
    serializer_class = CompanySerializer
    permission_classes = [AllowAny]


class CompanyDetailView(generics.RetrieveAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [AllowAny]


class JobPostingListView(generics.ListAPIView):
    queryset = (
        JobPosting.objects.filter(is_active=True)
        .select_related('company')
        .order_by('-created_at')
    )
    serializer_class = JobPostingSerializer
    permission_classes = [AllowAny]


class JobPostingDetailView(generics.RetrieveAPIView):
    queryset = JobPosting.objects.filter(is_active=True).select_related('company')
    serializer_class = JobPostingSerializer
    permission_classes = [AllowAny]
