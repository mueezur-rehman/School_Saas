# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from core.models import School
import random

class SignUpForm(UserCreationForm):
    # Extra fields jo signup par mangni hain
    school_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Institute Name'}))
    
    INSTITUTE_CHOICES = (
        ('school', 'School (Standard)'),
        ('coaching', 'Coaching Center'),
        ('madrasa', 'Madrasa (Islamic)'),
    )
    institute_type = forms.ChoiceField(choices=INSTITUTE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # UserCreationForm ke default password fields ko Bootstrap style aur placeholder de rahe hain
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Create Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # 1. Pehle School/Madrasa create karo
        school_name = self.cleaned_data['school_name']
        itype = self.cleaned_data['institute_type']
        
        # Slug (URL name) auto-generate karo
        slug_name = f"{school_name.lower().replace(' ', '-')}-{random.randint(1000, 9999)}"
        
        school = School.objects.create(
            name=school_name,
            institute_type=itype,
            phone=self.cleaned_data['phone'],
            email=self.cleaned_data['email'],
            slug=slug_name,
            address="Address not set"
        )
        
        # 2. Ab User ko School se link karo aur Admin banao
        user.school = school
        user.role = 'school_admin'  # Signup karne wala boss hai
        
        if commit:
            user.save()
        return user
    
    
class StaffCreationForm(forms.ModelForm):
    # Password field hum manually bana rahe hain taaki usko hash (secure) kar sakein
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create Password'})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Username'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        # 🚀 SECURITY: Password ko hamesha hash karke save karna chahiye
        user.set_password(self.cleaned_data['password'])
        
        # Naya staff by default active rahega taaki wo turant login kar sake
        user.is_active = True 
        
        if commit:
            user.save()
        return user