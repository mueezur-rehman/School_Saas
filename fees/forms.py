from django import forms
from .models import FeeStructure, FeeCategory
from academics.models import ClassGrade

class FeeStructureForm(forms.ModelForm):
    # Yeh field database me nahi hai, bas form me dikhegi
    fee_head_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Tuition Fee / Exam Fee'}),
        label="Fee Category Name"
    )

    class Meta:
        model = FeeStructure
        # due_date hata diya, category handle hum view me karenge
        fields = ['class_grade', 'amount'] 
        widgets = {
            'class_grade': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount (₹)'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['class_grade'].queryset = ClassGrade.objects.filter(school=user.school)