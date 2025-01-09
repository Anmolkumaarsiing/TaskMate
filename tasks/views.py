from django.shortcuts import render, redirect, get_object_or_404
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
from django.http import JsonResponse
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for non-interactive plotting (suitable for web environments)
from datetime import timedelta
from django.utils import timezone


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
            return redirect('task_section')
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
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect('task_section')
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

# Bubble Sort algorithm to sort tasks by priority
def bubble_sort_tasks(tasks):
    """
    Sort the tasks by priority using the Bubble Sort algorithm.

    Args:
        tasks (list): List of task objects to be sorted.

    Returns:
        list: Sorted list of tasks by priority.
    """
    # Priority mapping for sorting
    priority_order = {
        "High": 1,    # High priority gets a value of 1 (highest priority)
        "Medium": 2,  # Medium priority gets a value of 2
        "Low": 3      # Low priority gets a value of 3 (lowest priority)
    }
    
    n = len(tasks)
    
    # Bubble Sort Algorithm: Repeatedly swap elements to sort the list
    for i in range(n):
        swapped = False  # To track if any swaps were made
        
        # Perform a pass and compare each task with the next one
        for j in range(0, n - i - 1):
            # Compare the tasks based on their priority values
            if priority_order[tasks[j].priority] > priority_order[tasks[j + 1].priority]:
                # Swap if the priority of the current task is lower than the next one
                tasks[j], tasks[j + 1] = tasks[j + 1], tasks[j]
                swapped = True
        
        # If no elements were swapped in the inner loop, the list is already sorted
        if not swapped:
            break
    
    return tasks

@login_required
def task_section_view(request):
    tasks = Task.objects.filter(user=request.user)  # Fetch tasks for the logged-in user

    # Sort tasks based on priority using the bubble_sort_tasks function
    sorted_tasks = bubble_sort_tasks(list(tasks))

    return render(request, 'tasks/dashboard.html', {'tasks': sorted_tasks})

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

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        task.task_name = request.POST.get('task_name')
        task.start_date = request.POST.get('start_date')
        task.end_date = request.POST.get('end_date')
        task.priority = request.POST.get('priority')
        task.type = request.POST.get('type')
        task.save()
        return redirect('dashboard')  # Redirect back to dashboard after editing
    return render(request, 'tasks/edit_task.html', {'task': task})

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()  # Delete the task
    return redirect('task_section')  # Redirect back to dashboard after deletion

# Define the priority order mapping
priority_order = {
    "High": 1,    # High priority gets a value of 1 (highest priority)
    "Medium": 2,  # Medium priority gets a value of 2
    "Low": 3      # Low priority gets a value of 3 (lowest priority)
}

from django.utils import timezone

@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)  # Fetch tasks for the logged-in user
    
    # Apply the bubble_sort_tasks function to sort the tasks by priority
    sorted_tasks = bubble_sort_tasks(list(tasks))

    # Add the current date to context for comparison in the template
    today = timezone.now().date()

    # Pass the sorted tasks and today variable to the template
    return render(request, 'tasks/tasks.html', {'tasks': sorted_tasks, 'today': today})


@login_required
def task_status_graph(request):
    """
    This view generates a bar chart displaying the number of tasks categorized by 
    their priority (Low, Medium, High) for the logged-in user.
    """
    
    # Fetch the first 20 tasks for the logged-in user, ordered by start_date
    # This retrieves a subset of tasks to keep the graph manageable and focused on the most recent ones.
    tasks = Task.objects.filter(user=request.user).order_by('start_date')[:20]
    
    # DSA Concept - Dictionary: Used to store task names categorized by their priority level.
    # We are using a dictionary because it allows for fast access and efficient grouping of tasks.
    priority_counts = {
        'Low': [],     # List for storing tasks with Low priority
        'Medium': [],  # List for storing tasks with Medium priority
        'High': []     # List for storing tasks with High priority
    }

    # DSA Concept - Iteration: Loop through each task and categorize them by priority.
    # We are iterating over the tasks and grouping them based on priority, 
    # which helps in segregating tasks for visual representation in the chart.
    for task in tasks:
        priority = task.priority  # Get the priority of the task
        priority_counts[priority].append(task.task_name)  # Add task name to the corresponding priority list

    # DSA Concept - Lists: Used to store the names of tasks for each priority category
    # The task names are added to the lists under their corresponding priority category 
    # (Low, Medium, High). We are using lists here because we need to maintain the order 
    # in which tasks were categorized.
    
    # Data for the bar chart
    priorities = ['Low', 'Medium', 'High']  # The priority categories (Low, Medium, High)
    
    # DSA Concept - List Length Calculation: Get the count of tasks for each priority
    low_counts = len(priority_counts['Low'])      # Number of tasks with Low priority
    medium_counts = len(priority_counts['Medium']) # Number of tasks with Medium priority
    high_counts = len(priority_counts['High'])    # Number of tasks with High priority

    # DSA Concept - Bar Chart Creation: Using Matplotlib to create a bar chart.
    # This visualizes the number of tasks for each priority level.
    plt.figure(figsize=(10, 6))  # Set the figure size to make it look visually appealing.

    # Create bars for each priority level and assign colors
    bars = plt.bar(priorities, [low_counts, medium_counts, high_counts], color=['blue', 'yellow', 'red'])

    # DSA Concept - Text Placement: We annotate the bars with task names.
    # Each task name is separated by a comma for better readability.
    for i, bar in enumerate(bars):
        tasks_for_priority = priority_counts[priorities[i]]  # Get the list of tasks for the current priority
        task_names = ', '.join(tasks_for_priority)  # Combine task names with commas
        # Add some spacing from the top of the bars for the task names
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, task_names,
                 ha='center', va='bottom', fontsize=8, rotation=0, fontweight='bold')

    # DSA Concept - Customization: Setting axis labels, title, and rotating x-axis labels
    plt.xlabel('Priority')  # Label the x-axis as "Priority"
    plt.ylabel('Number of Tasks')  # Label the y-axis as "Number of Tasks"
    plt.title('Task Distribution by Priority and Date')  # Title for the graph
    plt.xticks(rotation=45)  # Rotate the x-axis labels for better readability

    # DSA Concept - Graph Layout: Using tight_layout() to optimize space around the chart
    plt.tight_layout()  # This ensures that all elements fit within the figure area without overlapping

    # DSA Concept - Y-axis Limits: Adjusting the y-axis limit to create space above the bars
    # We are setting the top limit of the y-axis to prevent the task names from overlapping with the top edge.
    plt.ylim(0, max(low_counts, medium_counts, high_counts) + 0.7)

    # DSA Concept - Buffer: Saving the plot to a buffer instead of directly to a file
    # This allows the graph to be served as an image in the HTTP response, without needing to store it permanently.
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')  # Save the figure as PNG in the buffer
    buffer.seek(0)  # Rewind the buffer to the start
    plt.close()  # Close the plot to free up resources

    # Return the image as HTTP response with PNG content type
    return HttpResponse(buffer, content_type='image/png')



@login_required
def task_alert(request):
    # Get tasks for the logged-in user, sorted by their deadline (Earliest Deadline First)
    tasks = Task.objects.filter(user=request.user).order_by('end_date')

    # Get the current time and calculate the 24-hour notification window
    current_time = timezone.now().date()
    notification_time = current_time + timedelta(days=1)

    # Filter tasks that have deadlines within the next 24 hours
    upcoming_tasks = [task for task in tasks if task.end_date == notification_time]

    # Notify the user if there are tasks that need attention
    if upcoming_tasks:
        notification_message = "You have tasks due in 24 hours! Please check them below."
    else:
        notification_message = "No tasks are due within the next 24 hours."

    # Return the HTML page with the tasks
    return render(request, 'tasks/task_alert.html', {
        'tasks': tasks,
        'notification_message': notification_message,
        'upcoming_tasks': upcoming_tasks
    })
