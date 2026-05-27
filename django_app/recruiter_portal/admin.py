from django.contrib import admin
from .models import CandidateResume

@admin.register(CandidateResume)
class CandidateResumeAdmin(admin.ModelAdmin):

    list_display = (
        'candidate_name',
        'resume_file',
        'uploaded_by',
        'uploaded_at'
    )
    
    search_fields = (
        'candidate_name',
    )