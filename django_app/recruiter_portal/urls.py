from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('analysis/<str:candidate_name>/', views.candidate_analysis, name='candidate_analysis'),
    path('interview-assistant/', views.interview_assistant, name='interview_assistant'),
    path('home/',views.recruiter_home,name='recruiter_home'),
]
