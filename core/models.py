from django.db import models

# User model ki zaroorat nahi hai yahan agar hum CustomUser use nahi kar rahe foreign key me

class School(models.Model):
    # 👇 YEH FIELD JODI HAI (Universal Feature ke liye)
    INSTITUTE_TYPES = (
        ('school', 'School (Standard)'),
        ('coaching', 'Coaching Institute'),
        ('madrasa', 'Madrasa (Islamic)'),
    )
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    institute_type = models.CharField(max_length=20, choices=INSTITUTE_TYPES, default='school') # New Field
    address = models.TextField()
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)
    subscription_end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# ACADEMIC SESSION MODEL
class AcademicSession(TimeStampedModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='sessions')
    name = models.CharField(max_length=20) # e.g. "2025-26"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False) # Kya ye abhi chal raha hai?

    class Meta:
        unique_together = ('school', 'name')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Logic: Agar isse current banaya hai, toh baaki sabko non-current kar do
        if self.is_current:
            AcademicSession.objects.filter(school=self.school).exclude(id=self.id).update(is_current=False)
        super().save(*args, **kwargs)