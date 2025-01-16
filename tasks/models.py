from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Task(models.Model):
    TASK_TYPES = [
        ('Work', 'Work'),
        ('Personal', 'Personal'),
        ('Urgent', 'Urgent'),
        ('Study', 'Study'),
        ('Projects', 'Projects'),
        ('Others', 'Others'),
    ]

    PRIORITY_LEVELS = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # Default user for migrations
    task_name = models.CharField(max_length=255, default='Default Task Name')
    start_date = models.DateField(default=date.today)  # Default to today's date
    end_date = models.DateField(default=date.today)  # Default to today's date
    type = models.CharField(max_length=50, choices=TASK_TYPES, default='General')
    priority = models.CharField(max_length=50, choices=PRIORITY_LEVELS, default='Medium')
    is_completed = models.BooleanField(default=False)
    in_progress = models.BooleanField(default=False)
    dependent_task = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)  # Dependency field
    
    def __str__(self):
        return f"{self.task_name} ({self.user.username})"
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    qualifications = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.username
