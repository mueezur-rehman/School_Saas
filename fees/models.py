from django.db import models
from core.models import School, TimeStampedModel, AcademicSession # 👈 Import Update Kiya
from students.models import Student
from academics.models import ClassGrade

class FeeCategory(TimeStampedModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='fee_categories')
    name = models.CharField(max_length=100) # e.g. "Tuition Fee", "Bus Fee"
    
    class Meta:
        unique_together = ('school', 'name')
        verbose_name_plural = "Fee Categories"

    def __str__(self):
        return f"{self.name}"

class FeeStructure(TimeStampedModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='fee_structures')
    class_grade = models.ForeignKey(ClassGrade, on_delete=models.CASCADE, related_name='fee_structures')
    category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2) # e.g. 1200.00
    
    # Optional: Hum structure ko bhi session se jod sakte hain future me
    
    class Meta:
        unique_together = ('school', 'class_grade', 'category')

    def __str__(self):
        return f"{self.class_grade.name} - {self.category.name}: {self.amount}"

class FeePayment(TimeStampedModel):
    PAYMENT_MODES = (
        ('cash', 'Cash'),
        ('online', 'Online / UPI'),
        ('cheque', 'Cheque'),
    )

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='fee_payments')
    
    # 👇 NEW FIELD: SESSION LINK
    session = models.ForeignKey(AcademicSession, on_delete=models.SET_NULL, null=True, blank=True)
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    mode = models.CharField(max_length=20, choices=PAYMENT_MODES, default='cash')
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.first_name} - ₹{self.amount_paid}"