from django.urls import path
from students.views import MyStudentProfileView

urlpatterns = [
    path('me/', MyStudentProfileView.as_view(), name='student-profile-me'),
]
