from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .models import Task
import io
import matplotlib.pyplot as plt
from django.http import HttpResponse
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for non-interactive plotting (suitable for web environments)
from datetime import timedelta
from django.utils import timezone
from django.utils.timezone import datetime, now
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserUpdateForm, ProfileUpdateForm

# Home View
def home_view(request):
    if request.user.is_authenticated:
        return redirect('task_section')
    return render(request, 'tasks/home.html')

# Login View
def login_view(request):
    if request.user.is_authenticated:
        return redirect('task_section')
        
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
from django.db import IntegrityError

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('task_section')

    if request.method == 'POST':
        name = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')  # Redirect back to signup

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return redirect('signup')

        try:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.first_name = name
            user.save()

            # **Debugging Print Statements**
            print(f"User created: {user}")

            # Authenticate the user before logging in
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                print("User logged in successfully")  # Debugging
                return redirect('task_section')
            else:
                messages.error(request, "Account created, but login failed. Try logging in manually.")
                return redirect('login')

        except IntegrityError as e:
            print(f"IntegrityError: {e}")
            messages.error(request, 'Account has been created successfully, Please login now.')

    return render(request, 'tasks/signup.html')

# Dashboard View
@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)
    print(tasks)
    return render(request, 'tasks/tasks.html', {'tasks': tasks})

# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')

# Add Task View
@login_required
def add_task(request):
    errors = []  # Initialize an empty list for errors

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
            errors.append("Please fill in all fields.")  # Add error to the list
        else:
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
                return redirect('dashboard')  # Redirect to dashboard on success
            except Exception as e:
                print("Error saving task:", e)
                errors.append("Failed to add task. Please try again.")  # Add error to the list

    # Pass errors to the template
    return render(request, 'tasks/AddTask.html', {'errors': errors})

# Bubble Sort algorithm to sort tasks by priority
def bubble_sort_tasks(tasks):
    # Sorting Algorithm - Bubble Sort
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

#change status View
@login_required
def change_status(request, task_id):
    # Iterative Approach
    if request.method == "POST":
        status = request.POST.get("status")
        task = get_object_or_404(Task, id=task_id, user=request.user)
        if status == "Completed":
            task.is_completed = True
            task.in_progress = False
        elif status == "In Progress":
            task.is_completed = False
            task.in_progress = True
        else:  # Pending
            task.is_completed = False
            task.in_progress = False
        task.save()
    return redirect('dashboard')


@login_required
def edit_task(request, task_id):
    # Iterative Approach: The task is fetched using a loop, and if not found, it returns an error.
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        task_name = request.POST.get('task_name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        priority = request.POST.get('priority')
        task_type = request.POST.get('type')

        # Convert start_date and end_date from string to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        
        # Check if end_date is before start_date
        if end_date and start_date and end_date < start_date:
            # Add error message instead of throwing ValidationError
            messages.error(request, "End date cannot be earlier than start date.")
        else:
            # Update task fields if no error
            task.task_name = task_name
            task.start_date = start_date
            task.end_date = end_date
            task.priority = priority
            task.type = task_type
            task.save()
            
            return redirect('dashboard')  # Redirect back to dashboard after editing

    return render(request, 'tasks/edit_task.html', {'task': task})

@login_required
def delete_task(request, task_id):
    # Iterative Approach: The task is fetched and then deleted if found.
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()  # Delete the task
    return redirect('task_section')  # Redirect back to dashboard after deletion

# Define the priority order mapping
priority_order = {
    "High": 1,    # High priority gets a value of 1 (highest priority)
    "Medium": 2,  # Medium priority gets a value of 2
    "Low": 3      # Low priority gets a value of 3 (lowest priority)
}

@login_required
def dashboard(request):
    # List: Fetch tasks for the logged-in user
    tasks = Task.objects.filter(user=request.user)  
    
    # Sorting Algorithm - Bubble Sort: Sort the tasks by priority
    sorted_tasks = bubble_sort_tasks(list(tasks))

    # List: Add the current date to context for comparison in the template
    today = now().date()

    # Iterative Approach: Iterate through the sorted tasks to highlight tasks with an end date less than today
    for task in sorted_tasks:
        task.highlight = task.end_date < today

    # Pass the sorted tasks and today variable to the template
    return render(request, 'tasks/tasks.html', {'tasks': sorted_tasks, 'today': today})

@login_required
def task_status_graph(request):
    """
    This view generates a bar chart displaying the number of tasks categorized by 
    their priority (Low, Medium, High) for the logged-in user.
    """
    
    tasks = Task.objects.filter(user=request.user).order_by('start_date')[:20]

    # DSA Concept - Dictionary: Used to store task names categorized by their priority level.
    priority_counts = {
        'Low': [],     
        'Medium': [],  
        'High': []     
    }

    # DSA Concept - Iteration: Loop through each task and categorize them by priority.
    for task in tasks:
        priority = task.priority
        priority_counts[priority].append(task.task_name)

    # DSA Concept - Lists: Used to store the names of tasks for each priority category
    priorities = ['Low', 'Medium', 'High']
    
    # DSA Concept - List Length Calculation: Get the count of tasks for each priority
    low_counts = len(priority_counts['Low'])      
    medium_counts = len(priority_counts['Medium']) 
    high_counts = len(priority_counts['High'])    

    #Bar Chart Creation: Using Matplotlib to create a bar chart.
    plt.figure(figsize=(10, 6))

    bars = plt.bar(priorities, [low_counts, medium_counts, high_counts], color=['blue', 'yellow', 'red'])

    #Text Placement: We annotate the bars with task names.
    for i, bar in enumerate(bars):
        tasks_for_priority = priority_counts[priorities[i]]
        task_names = ', '.join(tasks_for_priority)
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, task_names,
                 ha='center', va='bottom', fontsize=8, rotation=0, fontweight='bold')

    plt.xlabel('Priority')
    plt.ylabel('Number of Tasks')
    plt.title('Task Distribution by Priority and Date')
    plt.xticks(rotation=45)

    #Using tight_layout() to optimize space around the chart
    plt.tight_layout()

    #Adjusting the y-axis limit to create space above the bars
    plt.ylim(0, max(low_counts, medium_counts, high_counts) + 0.7)

    #Saving the plot to a buffer instead of directly to a file
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    return HttpResponse(buffer, content_type='image/png')

@login_required
def task_alert(request):
    # Queue: Sorting tasks by deadline in the task_alert view
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

@login_required
def profile_view(request):
    if request.method == 'POST':
        # Update user form and profile form
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)

        # Handle password change if old password, new password and confirm new password are provided
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_password2')

        # Check if old password is correct and new passwords match
        if old_password and new_password and new_password2:
            user = authenticate(request, username=request.user.username, password=old_password)
            if user is not None:
                if new_password == new_password2:
                    password_form = PasswordChangeForm(user=request.user, data=request.POST)
                    if password_form.is_valid():
                        password_form.save()
                        update_session_auth_hash(request, password_form.user)  # Keeps the user logged in after changing password
                        messages.success(request, 'Your password has been updated!')
                        return redirect('profile')  # Redirect to the profile page
                    else:
                        messages.error(request, 'Password change failed. Please try again.')
                else:
                    # New passwords do not match
                    messages.error(request, 'Profile Error: New passwords do not match. Please re-enter them.')
            else:
                # Old password is incorrect
                messages.error(request, 'Profile Error: Incorrect old password. Please try again.')

        # Check if forms are valid for updating profile data
        elif user_form.is_valid() and profile_form.is_valid():
            user_form.save()  # Save first_name and last_name
            profile_form.save()  # Save profile information (phone number, etc.)
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        password_form = PasswordChangeForm(user=request.user)
    return render(request, 'tasks/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
    })
