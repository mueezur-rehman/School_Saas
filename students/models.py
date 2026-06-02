from django.db import models
from core.models import School, TimeStampedModel, AcademicSession # 👈 Import Update Kiya
from academics.models import ClassGrade, Section

class Student(TimeStampedModel):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('alumini', 'Alumini / Left'),
    )

    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    )

    RELIGION_CHOICES = (
        ('Islam', 'Islam'),
        ('Hinduism', 'Hinduism'),
        ('Christianity', 'Christianity'),
        ('Sikhism', 'Sikhism'),
        ('Jainism', 'Jainism'),
        ('Other', 'Other'),
    )

    CATEGORY_CHOICES = (
        ('General', 'General'),
        ('OBC', 'OBC'),
        ('SC', 'SC'),
        ('ST', 'ST'),
        ('Other', 'Other'),
    )

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students')
    
    # 👇 NEW FIELD: SESSION LINK
    session = models.ForeignKey(AcademicSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')

    admission_no = models.CharField(max_length=50)
    admission_date = models.DateField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    dob = models.DateField(null=True, blank=True)
    
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    religion = models.CharField(max_length=50, choices=RELIGION_CHOICES, blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True)
    
    aadhar_no = models.CharField(max_length=20, blank=True, null=True)
    samagra_id = models.CharField(max_length=9, blank=False)
    
    father_name = models.CharField(max_length=100)
    father_occupation = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True)
    father_mobile = models.CharField(max_length=15)
    
    previous_school = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField()
    
    current_class = models.ForeignKey(ClassGrade, on_delete=models.SET_NULL, null=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True)
    roll_number = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    
    class Meta:
        # Session ke saath unique hona chahiye (Same admission number agle saal use ho sakta hai)
        unique_together = [
            ('school', 'admission_no'), 
        ]
    ordering = ['school', 'current_class', 'section', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.admission_no})"