from django import forms
from .models import AcademicSession

class AcademicSessionForm(forms.ModelForm):
    class Meta:
        model = AcademicSession
        fields = ['name', 'start_date', 'end_date', 'is_current']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2026-2027'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type':'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type':'date'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
        }
        