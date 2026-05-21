from django.urls import path
from .views import recruiter_dashboard

urlpatterns=[
    path('dashboard/',recruiter_dashboard,name='recruiter_dashboard'),
]