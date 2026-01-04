from django import forms
from .models import Assignment

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['subject', 'title', 'description', 'due_date', 'attachment']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }