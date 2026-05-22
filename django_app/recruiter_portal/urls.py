from django.urls import path
from .views import recruiter_dashboard, candidate_analysis,interview_assistant

urlpatterns = [
    path("dashboard/", recruiter_dashboard, name="recruiter_dashboard"),
    path("analysis/<str:candidate_name>/", candidate_analysis, name="candidate_analysis"),
    path('interview-assistant/',interview_assistant,name='interview_assistant'),
]
