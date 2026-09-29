from django.urls import path
from placements.views import (
    CompanyListView,
    CompanyDetailView,
    JobPostingListView,
    JobPostingDetailView,
)

urlpatterns = [
    path('companies/', CompanyListView.as_view(), name='company-list'),
    path('companies/<int:pk>/', CompanyDetailView.as_view(), name='company-detail'),
    path('jobs/', JobPostingListView.as_view(), name='jobposting-list'),
    path('jobs/<int:pk>/', JobPostingDetailView.as_view(), name='jobposting-detail'),
]
