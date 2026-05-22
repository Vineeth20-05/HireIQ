from django.db import models
from accounts.models import CustomUser

class CandidateResume(models.Model):
    candidate_name = models.CharField(max_length=255)

    resume_file = models.FileField(upload_to="resumes/")
    uploaded_by = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate_name} - {self.uploaded_by.username}"
