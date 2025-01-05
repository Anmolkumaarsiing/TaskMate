# views.py
from django.shortcuts import render
from .models import Task  # Import the Task model

def task_list(request):
    tasks = Task.objects.all()  # Fetch all tasks from the database
    return render(request, 'tasks/task_list.html', {'tasks': tasks})  # Pass tasks to template

def home(request):
    return render(request, 'home.html') 