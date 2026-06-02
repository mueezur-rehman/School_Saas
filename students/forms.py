from django import forms
from .models import Student
from academics.models import ClassGrade, Section

class StudentAdmissionForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'admission_no', 'roll_number',
            'first_name', 'last_name', 'dob', 'gender', 'blood_group', 
            'aadhar_no', 'samagra_id', 'father_name', 'mother_name', 
            'father_mobile', 'address', 'current_class', 'section', 'photo'
        ]
        widgets = {
            'admission_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reg / Adm No.'}),
            'roll_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Roll No.'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Student First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Surname (Optional)'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'aadhar_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12-digit Aadhar No.'}),
            'samagra_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SSSM ID'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Father's Full Name"}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Mother's Full Name"}),
            'father_mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'WhatsApp Mobile No.'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': '2'}),
            'current_class': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        
        # Sirf current school ki classes aur sections dikhayein
        if school:
            self.fields['current_class'].queryset = ClassGrade.objects.filter(school=school)
            self.fields['section'].queryset = Section.objects.filter(school=school)