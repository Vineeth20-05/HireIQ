from django.urls import path
from .views import candidate_dashboard,candidate_home

urlpatterns=[
    path('dashboard/',candidate_dashboard,name='candidate_dashboard'),
    path('home/',candidate_home,name='candidate_home'),
]