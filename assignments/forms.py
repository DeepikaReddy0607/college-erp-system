from django import forms
from .models import Assignment


class AssignmentForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"})
    )
    class Meta:
        model = Assignment
        fields = [
            "offering",
            "title",
            "description",
            "max_marks",
            "due_date",
            "attachment",
        ]
