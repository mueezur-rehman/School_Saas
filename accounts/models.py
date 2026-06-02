from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import School, TimeStampedModel

class CustomUser(AbstractUser, TimeStampedModel):
    # Roles define karte hain
    SUPER_ADMIN = 'super_admin'
    SCHOOL_ADMIN = 'school_admin'
    TEACHER = 'teacher'
    ACCOUNTANT = 'accountant'
    PARENT = 'parent'
    STUDENT = 'student'

    ROLE_CHOICES = (
        (SUPER_ADMIN, 'Super Admin'),
        (SCHOOL_ADMIN, 'School Admin'),
        (TEACHER, 'Teacher'),
        (ACCOUNTANT, 'Accountant'),
        (PARENT, 'Parent'),
        (STUDENT, 'Student'),
    )

    # School link karna zaroori hai (Tenant Isolation)
    # Super Admin ke liye school null ho sakta hai
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STUDENT)
    phone = models.CharField(max_length=15, blank=True, null=True)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    # Profile pic for user
    profile_picture = models.ImageField(upload_to='user_profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()}) - {self.school.name if self.school else 'System'}"

    # Helper methods check karne ke liye
    @property
    def is_school_admin(self):
        return self.role == self.SCHOOL_ADMIN
    
    @property
    def is_teacher(self):
        return self.role == self.TEACHER