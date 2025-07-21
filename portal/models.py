from django.db import models

# Create your models here.
class Teacher(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)  # Store hashed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    

    def __str__(self):
        return self.username

class Student(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    marks = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='students', null=True, blank=True)
    updated_by = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='updated', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('name', 'subject')

    def __str__(self):
        return f"{self.name} - {self.subject}"
