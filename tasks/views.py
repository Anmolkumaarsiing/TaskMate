from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Task
from collections import defaultdict
import heapq
import io
import matplotlib.pyplot as plt
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for non-interactive plotting (suitable for web environments)


# Login View
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return render(request, 'tasks/login.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password')
    return render(request, 'tasks/login.html')

# Signup View
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect('dashboard')
    return render(request, 'tasks/signup.html')

# Home View
def home_view(request):
    return render(request, 'tasks/home.html')

# Dashboard View
@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)  # Fetch tasks for the logged-in user
    print(tasks)  # Print to console for debugging purposes
    return render(request, 'tasks/tasks.html', {'tasks': tasks})



# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def add_task(request):
    if request.method == 'POST':
        task_name = request.POST.get('task_name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        task_type = request.POST.get('type')
        priority = request.POST.get('priority')

        print("Received Data:", {
            "task_name": task_name,
            "start_date": start_date,
            "end_date": end_date,
            "type": task_type,
            "priority": priority,
        })

        # Validate input fields
        if not all([task_name, start_date, end_date, task_type, priority]):
            print("Error: Missing required fields.")
            messages.error(request, "Please fill in all fields.")
            return render(request, 'tasks/AddTask.html')

        # Save task to database
        try:
            task = Task.objects.create(
                user=request.user,
                task_name=task_name,
                start_date=start_date,
                end_date=end_date,
                type=task_type,
                priority=priority,
            )
            print("Task successfully saved:", task)
            messages.success(request, "Task added successfully!")
            return redirect('dashboard')
        except Exception as e:
            print("Error saving task:", e)
            messages.error(request, "Failed to add task. Please try again.")
    return render(request, 'tasks/AddTask.html')

@login_required
def task_section_view(request):
    tasks = Task.objects.filter(user=request.user)  # Fetch tasks for the logged-in user
    return render(request, 'tasks/dashboard.html', {'tasks': tasks})

# Task Completion Graph View
@login_required
def task_completion_graph(request):
    tasks = Task.objects.filter(is_completed=True)

    category_data = defaultdict(lambda: {'low': 0, 'medium': 0, 'high': 0})
    for task in tasks:
        priority = task.priority.lower()
        category_data[task.category][priority] += 1

    categories = list(category_data.keys())
    low_counts = [category_data[cat]['low'] for cat in categories]
    medium_counts = [category_data[cat]['medium'] for cat in categories]
    high_counts = [category_data[cat]['high'] for cat in categories]

    fig, ax = plt.subplots(figsize=(8, 6))
    x = range(len(categories))
    ax.bar(x, low_counts, label="Low", color='blue', width=0.6)
    ax.bar(x, medium_counts, bottom=low_counts, label="Medium", color='yellow', width=0.6)
    ax.bar(x, high_counts, bottom=[low + medium for low, medium in zip(low_counts, medium_counts)],
           label="High", color='red', width=0.6)

    ax.set_xlabel('Categories')
    ax.set_ylabel('Number of Tasks')
    ax.set_title('Task Completion by Category and Priority')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.legend()

    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)

    return HttpResponse(buffer, content_type='image/png')

@login_required
def dashboard_view(request):
    return render(request, 'tasks/tasks.html')


def AddTask_view(request):
    return render(request, 'tasks/AddTask.html')


@login_required
def mark_completed(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.is_completed = True
    task.save()
    return redirect('dashboard')  # Redirect back to dashboard

@login_required
def change_status(request, task_id):
    if request.method == "POST":
        status = request.POST.get("status")
        task = get_object_or_404(Task, id=task_id, user=request.user)
        if status == "Completed":
            task.is_completed = True
            task.in_progress = False  # Add `in_progress` field in the model if needed
        elif status == "In Progress":
            task.is_completed = False
            task.in_progress = True  # Add `in_progress` field
        else:  # Pending
            task.is_completed = False
            task.in_progress = False
        task.save()
    return redirect('dashboard')  # Redirect back to dashboard

# views.py

# Define the priority order mapping
priority_order = {
    "High": 1,    # High priority gets a value of 1 (highest priority)
    "Medium": 2,  # Medium priority gets a value of 2
    "Low": 3      # Low priority gets a value of 3 (lowest priority)
}

# Bubble Sort Algorithm to sort tasks based on priority
def bubble_sort_tasks(tasks):
    """
    Sort the tasks by priority using the Bubble Sort algorithm.

    Args:
        tasks (list): List of task objects to be sorted.

    Returns:
        list: Sorted list of tasks by priority.
    """
    n = len(tasks)
    
    # Bubble Sort Algorithm: Repeatedly swap elements to sort the list
    for i in range(n):
        # Flag to check if any swapping happens during the current pass
        swapped = False
        
        # Perform a pass and compare each task with the next one
        for j in range(0, n - i - 1):
            # Compare the tasks based on their priority values
            if priority_order[tasks[j].priority] > priority_order[tasks[j + 1].priority]:
                # Swap if the priority of the current task is lower than the next one
                tasks[j], tasks[j + 1] = tasks[j + 1], tasks[j]
                swapped = True
        
        # If no elements were swapped in the inner loop, then the list is already sorted
        if not swapped:
            break
    
    return tasks

# Dashboard View with Sorting
@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)  # Fetch tasks for the logged-in user
    
    # Apply the bubble_sort_tasks function to sort the tasks by priority
    sorted_tasks = bubble_sort_tasks(list(tasks))

    # Pass the sorted tasks to the template
    return render(request, 'tasks/tasks.html', {'tasks': sorted_tasks})

import matplotlib.pyplot as plt
from django.http import HttpResponse
from collections import defaultdict
from django.shortcuts import render
from .models import Task
import io

@login_required
def task_status_graph(request):
    # Fetch tasks
    tasks = Task.objects.filter(user=request.user)

    # Count tasks by status and priority, and store task names
    status_priority_counts = {
        'Completed': {'Low': [], 'Medium': [], 'High': []},
        'In Progress': {'Low': [], 'Medium': [], 'High': []},
        'Pending': {'Low': [], 'Medium': [], 'High': []},
    }

    # Calculate the count of tasks in each status and priority
    for task in tasks:
        status = task_status(task)
        priority = task.priority

        # Add task to the respective status and priority category
        status_priority_counts[status][priority].append(task.task_name)

    # Data for the bar chart
    statuses = ['Completed', 'In Progress', 'Pending']
    priorities = ['Low', 'Medium', 'High']

    # Prepare data for plotting
    low_counts = [len(status_priority_counts[status]['Low']) for status in statuses]
    medium_counts = [len(status_priority_counts[status]['Medium']) for status in statuses]
    high_counts = [len(status_priority_counts[status]['High']) for status in statuses]

    # Define colors for the bars
    colors = ['blue', 'yellow', 'red']

    # Create a bar chart
    width = 0.25  # Width of each bar
    x = range(len(statuses))  # X positions for each group of bars

    plt.figure(figsize=(10, 6))
    
    # Plot bars for each priority level
    bars_low = plt.bar(x, low_counts, width, label='Low', color='blue')
    bars_medium = plt.bar([i + width for i in x], medium_counts, width, label='Medium', color='yellow')
    bars_high = plt.bar([i + 2 * width for i in x], high_counts, width, label='High', color='red')

    # Annotate task names on top of the bars
    for i, bar in enumerate(bars_low):
        # Add task names for Low priority
        tasks_for_status = status_priority_counts[statuses[i]]['Low']
        for idx, task_name in enumerate(tasks_for_status):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05, task_name, 
                     ha='center', va='bottom', fontsize=8, rotation=0, fontweight='bold')

    for i, bar in enumerate(bars_medium):
        # Add task names for Medium priority
        tasks_for_status = status_priority_counts[statuses[i]]['Medium']
        for idx, task_name in enumerate(tasks_for_status):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05, task_name, 
                     ha='center', va='bottom', fontsize=8, rotation=0, fontweight='bold')

    for i, bar in enumerate(bars_high):
        # Add task names for High priority
        tasks_for_status = status_priority_counts[statuses[i]]['High']
        for idx, task_name in enumerate(tasks_for_status):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05, task_name, 
                     ha='center', va='bottom', fontsize=8, rotation=0, fontweight='bold')

    # Customize the graph
    plt.xlabel('Task Status')
    plt.ylabel('Number of Tasks')
    plt.title('Task Status Distribution by Priority')
    plt.xticks([i + width for i in x], statuses)  # Position the x-axis labels in the middle of the grouped bars
    plt.legend()

    # Render the graph image
    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    return HttpResponse(buffer, content_type='image/png')


def task_status(task):
    """
    Determine the task status based on the fields.
    """
    if task.is_completed:
        return 'Completed'
    elif task.in_progress:
        return 'In Progress'
    else:
        return 'Pending'
