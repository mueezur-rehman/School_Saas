from django import forms
from .models import ClassGrade, Section, Subject

class ClassGradeForm(forms.ModelForm):
    class Meta:
        model = ClassGrade
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Class 10 / Hifz Batch'})}

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['class_grade', 'name']
        widgets = {
            'class_grade': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. A / Morning'})
        }
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['class_grade'].queryset = ClassGrade.objects.filter(school=user.school)

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['class_grade', 'name', 'total_marks']
        widgets = {
            'class_grade': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Mathematics'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control'})
        }
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['class_grade'].queryset = ClassGrade.objects.filter(school=user.school)